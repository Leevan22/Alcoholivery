from django.contrib import admin
from .models import PerfilUsuario, Producto, Pedido

admin.site.register(PerfilUsuario)
admin.site.register(Producto)
admin.site.register(Pedido)