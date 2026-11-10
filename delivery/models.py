from django.db import models
from django.contrib.auth.models import User
from datetime import date

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=12, unique=True)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=200)

    def es_mayor_de_edad(self):
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return edad >= 18

    def __str__(self):
        return f"{self.user.username} ({'Mayor de edad' if self.es_mayor_de_edad() else 'Menor de edad'})"


class Producto(models.Model):
    CATEGORIAS = [
        ('ALCOHOL', 'Bebidas Alcohólicas'),
        ('BEBIDA', 'Refrescos y Bebidas'),
        ('CIGARRO', 'Cigarrillos y Tabaco'),
    ]

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='ALCOHOL')
    precio = models.IntegerField()
    stock_actual = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    requiere_mayor_edad = models.BooleanField(default=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio} (Stock: {self.stock_actual})"


class CarroCompras(models.Model):
    cliente = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carro')

    def obtener_subtotal(self):
        return sum(item.obtener_subtotal() for item in self.items.all())

    def obtener_total_items(self):
        return sum(item.cantidad for item in self.items.all())


class ItemCarro(models.Model):
    carro = models.ForeignKey(CarroCompras, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def obtener_subtotal(self):
        return self.producto.precio * self.cantidad


class Pedido(models.Model):
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo contra entrega'),
        ('DEBITO', 'Tarjeta de Débito (Redcompra)'),
        ('CREDITO', 'Tarjeta de Crédito'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
    ]
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_CAMINO', 'En camino'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    direccion_entrega = models.CharField(max_length=200)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='DEBITO')
    subtotal = models.IntegerField(default=0)
    costo_envio = models.IntegerField(default=2000)
    total_pagar = models.IntegerField(default=0)
    estado_despacho = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username} [{self.estado_despacho}]"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.IntegerField()
    subtotal = models.IntegerField()