from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_trainer = models.BooleanField(default=False, verbose_name="¿Es entrenador?")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username

class PhysicalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    weight = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    height = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="Altura (m)")
    notes = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Perfil Físico"
        verbose_name_plural = "Perfiles Físicos"

    def __str__(self):
        return f"Profile of {self.user.username}"