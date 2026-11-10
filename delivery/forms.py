from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Pedido
from datetime import date

class RegistroForm(forms.ModelForm):
    username = forms.CharField(label="Usuario", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    email = forms.EmailField(label="Correo Electrónico")
    rut = forms.CharField(label="RUT", max_length=12)
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    direccion = forms.CharField(label="Dirección de Entrega predeterminada", max_length=200)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_fecha_nacimiento(self):
        fecha_nac = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nac:
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad < 18:
                raise forms.ValidationError("Acceso denegado: Debes ser mayor de 18 años para registrarte en Alcoholivery.")
        return fecha_nac


class CheckoutForm(forms.Form):
    direccion_entrega = forms.CharField(
        label="Dirección de Envío",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Av. Pajaritos 1234, Maipú'})
    )
    metodo_pago = forms.ChoiceField(
        label="Método de Pago",
        choices=Pedido.METODOS_PAGO,
        widget=forms.Select(attrs={'class': 'form-select'})
    )