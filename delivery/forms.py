from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Pedido, Producto
from datetime import date

class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        label="Usuario", 
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. nicolas123'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    rut = forms.CharField(
        label="RUT", 
        max_length=12,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'})
    )
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    direccion = forms.CharField(
        label="Dirección de Entrega predeterminada", 
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Av. Pajaritos 1234, Maipú'})
    )
    
    acepto_declaracion = forms.BooleanField(
        required=True,
        label="Declaración Jurada de Mayoría de Edad",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input me-2',
            'id': 'id_acepto_declaracion'
        }),
        error_messages={
            'required': 'Debes aceptar obligatoriamente la declaración jurada para poder crear tu cuenta.'
        },
        help_text="Declaro bajo juramento que toda la información ingresada es real y que tengo 18 años o más. Comprendo que la plataforma y las imágenes del Carnet de Identidad (en caso de subirse) serán utilizadas strictly para verificar mi edad y cumplir con las leyes de venta de alcohol (Ley N° 19.925 y Ley N° 19.628)."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_fecha_nacimiento(self):
        fecha_nac = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nac:
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad < 18:
                raise forms.ValidationError("🚫 Acceso denegado: No cumples con los requisitos de edad. Debes tener 18 años o más para crear una cuenta en Alcoholivery.")
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
    metodo_verificacion = forms.ChoiceField(
        label="Verificación de Edad en Venta de Alcohol",
        choices=Pedido.METODOS_VERIFICACION,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    imagen_carnet = forms.ImageField(
        label="Foto del Carnet de Identidad (Opcional si eligió subida digital)",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get("metodo_verificacion")
        imagen = cleaned_data.get("imagen_carnet")

        if metodo == 'DIGITAL' and not imagen:
            raise forms.ValidationError("Debes adjuntar una foto de tu Carnet de Identidad si seleccionas la verificación digital.")
        return cleaned_data


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'stock_actual', 'imagen', 'requiere_mayor_edad', 'disponible']
        labels = {
            'nombre': 'Nombre del Producto',
            'categoria': 'Categoría',
            'precio': 'Precio ($)',
            'stock_actual': 'Stock Inicial',
            'imagen': 'Imagen del Producto',
            'requiere_mayor_edad': '¿Requiere verificación +18?',
            'disponible': '¿Disponible para venta?'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Pisco Alto del Carmen 35° 1L'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '7990'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '24'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'requiere_mayor_edad': forms.CheckboxInput(attrs={'class': 'form-check-input me-2'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input me-2'}),
        }