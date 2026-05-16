from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class PlanRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('canceled_by_new', 'Canceled by New Request'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    debit = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def days_left(self):
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(0, delta.days)
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'Sin Plan'}"