from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.subscriptions.models import Subscription

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        subscription = Subscription.objects.filter(user=user).select_related('plan').first()
        
        context['subscription'] = subscription
        context['is_admin'] = user.is_staff
        
        context['show_plans_button'] = not subscription or not subscription.is_active or subscription.is_expired
        return context