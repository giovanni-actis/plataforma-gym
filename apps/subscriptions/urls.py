from django.urls import path
from .views import PlanListView, AdminDashboardView, PlanCreateView, PlanDeleteView, PlanUpdateView, AdminPlanListView, SelectPlanView,AdminPlanRequestDashboardView, ProcessPlanRequestView

app_name = "subscriptions"

urlpatterns = [
    path('planes/', PlanListView.as_view(), name='plan_list'),
    path('plans/select/<int:plan_id>/', SelectPlanView.as_view(), name='select_plan'),
    path('admin-planes/', AdminPlanListView.as_view(), name='admin_plan_list'),
    path('admin/dashboard/requests/', AdminPlanRequestDashboardView.as_view(), name='admin_plan_request_dashboard'),
    path('admin/requests/<int:pk>/<str:action>/', ProcessPlanRequestView.as_view(), name='process_request'),
    path('planes/nuevo/', PlanCreateView.as_view(), name='plan_create'),
    path('planes/editar/<int:pk>/', PlanUpdateView.as_view(), name='plan_edit'),
    path('planes/eliminar/<int:pk>/', PlanDeleteView.as_view(), name='plan_delete'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
]