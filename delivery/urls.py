from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('carro/agregar/<int:producto_id>/', views.agregar_al_carro, name='agregar_al_carro'),
    path('carro/', views.ver_carro, name='ver_carro'),
    path('carro/eliminar/<int:item_id>/', views.eliminar_del_carro, name='eliminar_del_carro'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
    path('mis-pedidos/cancelar/<int:pedido_id>/', views.cancelar_pedido_view, name='cancelar_pedido'),
      path('gestion-productos/', views.admin_productos_view, name='admin_productos'),  # <--- NUEVA RUTA
]