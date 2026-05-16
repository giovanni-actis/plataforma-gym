from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, View, CreateView, UpdateView, DeleteView
from django.db import transaction
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Max
from apps.subscriptions.models import Subscription 
from .models import Plan, PlanRequest

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class PlanListView(LoginRequiredMixin, ListView):
    model = Plan
    template_name = 'subscriptions/plan_list.html'
    context_object_name = 'plans'

class SelectPlanView(LoginRequiredMixin, View):
    """
    Logic for selecting a plan, canceling previous ones, 
    and sending professional HTML notifications.
    """
    def get(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        
        try:
            with transaction.atomic():
                # Cancel previous pending requests
                PlanRequest.objects.filter(
                    user=request.user, 
                    status='pending'
                ).update(status='canceled_by_new')

                # Create the new record
                PlanRequest.objects.create(
                    user=request.user,
                    plan=plan,
                    status='pending'
                )

            # Send professional HTML Email
            self.send_html_notification(request.user, plan)
            
            # Client-facing message in Spanish
            messages.success(
                request, 
                f"¡Solicitud enviada! Has seleccionado el plan '{plan.name}'. "
                f"Cualquier pedido anterior ha sido cancelado. Nos contactaremos pronto."
            )
            
        except Exception as e:
            print(e)
            messages.error(request, "Hubo un error al procesar tu solicitud. Por favor, intenta de nuevo.")
            
        return redirect('subscriptions:plan_list')

    def send_html_notification(self, user, plan):
        """Renders and sends a professional Nord-themed email."""
        subject = f"Nueva Solicitud de Plan: {plan.name} - {user.username}"
        admin_url = "http://127.0.0.1:8000/subscriptions/admin-dashboard/"
        
        # Context for the template
        context = {
            'user': user,
            'plan': plan,
            'admin_url': admin_url,
        }
        
        # Render HTML and plain text version for compatibility
        html_content = render_to_string('emails/plan_request_notification.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email='giovagameplay151@gmail.com',
            to=['giovagameplay151@gmail.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=True)

class AdminPlanListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Plan
    template_name = 'subscriptions/admin_plan_dashboard.html'
    context_object_name = 'plans'

class PlanCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Plan
    fields = ['name', 'price', 'duration_days']
    template_name = 'subscriptions/admin_plan_form.html'
    success_url = reverse_lazy('subscriptions:admin_plan_list')

class PlanUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Plan
    fields = ['name', 'price', 'duration_days']
    template_name = 'subscriptions/admin_plan_form.html'
    success_url = reverse_lazy('subscriptions:admin_plan_list')

class PlanDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Plan
    template_name = 'subscriptions/plan_confirm_delete.html'
    success_url = reverse_lazy('subscriptions:admin_plan_list')


class AdminDashboardView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/admin_panel.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        # 1. Empezamos con el queryset básico
        queryset = super().get_queryset().select_related('user', 'plan')
        
        # 2. Obtenemos parámetros de búsqueda
        self.query = self.request.GET.get('q', '')
        self.status_filter = self.request.GET.get('status', '')
        today = timezone.now().date()

        # 3. Filtro por nombre o email
        if self.query:
            queryset = queryset.filter(
                Q(user__username__icontains=self.query) |
                Q(user__email__icontains=self.query)
            )

        # 4. Filtro por estado
        if self.status_filter == 'activa':
            queryset = queryset.filter(is_active=True, end_date__gte=today)
        elif self.status_filter == 'inactiva':
            queryset = queryset.filter(Q(is_active=False) | Q(end_date__lt=today))
        elif self.status_filter == 'pendiente':
            queryset = queryset.filter(
                is_active=True, 
                end_date__lt=today + timezone.timedelta(days=3)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        # Pasamos los filtros de vuelta al template para que se mantengan en los inputs
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['status_filter'] = self.status_filter
        return context


class UpdateSubscriptionStatusView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        sub_id = self.kwargs.get('sub_id')
        action = self.kwargs.get('action')
        subscription = get_object_or_404(Subscription, id=sub_id)
        
        if action == 'reactivar':
            subscription.is_active = True
            subscription.end_date = timezone.now().date() + timezone.timedelta(days=30)
        elif action == 'pendiente':
            subscription.is_active = True
            subscription.end_date = timezone.now().date()
            
        subscription.save()
        return redirect('admin_panel')

class AdminPlanRequestDashboardView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = PlanRequest
    template_name = 'subscriptions/admin_plan_request_dashboard.html'
    context_object_name = 'requests'

    def get_queryset(self):
        # Obtenemos el ID de la última solicitud pendiente por cada usuario
        latest_requests_ids = PlanRequest.objects.filter(
            status='pending'
        ).values('user').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)

        # Retornamos los objetos completos ordenados por fecha
        return PlanRequest.objects.filter(
            id__in=latest_requests_ids
        ).select_related('user', 'plan').order_by('-request_date')

from django.utils import timezone
from .models import Subscription, PlanRequest # Asegúrate de importar tu modelo Subscription

class ProcessPlanRequestView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk, action):
        plan_request = get_object_or_404(PlanRequest, pk=pk)
        
        actions_map = {
            'approve': {'status': 'approved', 'msg': 'aprobada', 'level': messages.SUCCESS},
            'reject': {'status': 'rejected', 'msg': 'rechazada', 'level': messages.ERROR},
            'hold': {'status': 'pending', 'msg': 'puesta en espera', 'level': messages.WARNING},
        }

        if action in actions_map:
            config = actions_map[action]
            plan_request.status = config['status']
            plan_request.save()

            # --- Lógica de Registro de Suscripción ---
            if action == 'approve':
                # Buscamos una suscripción existente o creamos una nueva
                subscription, created = Subscription.objects.update_or_create(
                    user=plan_request.user,
                    defaults={
                        'plan': plan_request.plan,
                        'start_date': timezone.now(),
                        'is_active': True
                    }
                )
                # Opcional: Si quieres que el mensaje sea más específico
                action_msg = f"aprobada y suscripción activa al plan {plan_request.plan.name}"
            else:
                action_msg = config['msg']
            # ----------------------------------------
            
            messages.add_message(
                request, 
                config['level'], 
                f"La solicitud de {plan_request.user.username} ha sido {action_msg}."
            )
        else:
            messages.error(request, "Acción no válida.")

        return redirect('subscriptions:admin_request_dashboard')