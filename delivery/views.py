from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, CheckoutForm
from .models import PerfilUsuario, Producto, Pedido, CarroCompras, ItemCarro, DetallePedido

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            PerfilUsuario.objects.create(
                user=user,
                rut=form.cleaned_data['rut'],
                fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                direccion=form.cleaned_data['direccion']
            )

            CarroCompras.objects.create(cliente=user)
            messages.success(request, "Cuenta creada exitosamente. Ya puedes iniciar sesión.")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'delivery/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            CarroCompras.objects.get_or_create(cliente=user)
            return redirect('catalogo')
    else:
        form = AuthenticationForm()
    return render(request, 'delivery/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def catalogo_view(request):
    perfil = request.user.perfil
    if not perfil.es_mayor_de_edad():
        messages.error(request, "Acceso restringido solo para mayores de 18 años.")
        return redirect('logout')

    productos = Producto.objects.filter(disponible=True)
    return render(request, 'delivery/catalogo.html', {'productos': productos, 'perfil': perfil})

@login_required
def agregar_al_carro(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carro, _ = CarroCompras.objects.get_or_create(cliente=request.user)

    if producto.stock_actual > 0:
        item, created = ItemCarro.objects.get_or_create(carro=carro, producto=producto)
        if not created:
            if item.cantidad < producto.stock_actual:
                item.cantidad += 1
                item.save()
                messages.success(request, f"Se agregó otra unidad de {producto.nombre} al carro.")
            else:
                messages.warning(request, f"No hay más stock disponible de {producto.nombre}.")
        else:
            messages.success(request, f"{producto.nombre} añadido al carro de compras.")
    else:
        messages.error(request, "Producto sin stock disponible.")

    return redirect('catalogo')

@login_required
def ver_carro(request):
    carro, _ = CarroCompras.objects.get_or_create(cliente=request.user)
    items = carro.items.select_related('producto').all()
    subtotal = carro.obtener_subtotal()
    costo_envio = 2000 if items.exists() else 0
    total = subtotal + costo_envio

    return render(request, 'delivery/carrito.html', {
        'carro': carro,
        'items': items,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total
    })

@login_required
def eliminar_del_carro(request, item_id):
    item = get_object_or_404(ItemCarro, id=item_id, carro__cliente=request.user)
    item.delete()
    messages.info(request, "Producto eliminado del carro.")
    return redirect('ver_carro')

@login_required
def checkout_view(request):
    carro, _ = CarroCompras.objects.get_or_create(cliente=request.user)
    items = carro.items.select_related('producto').all()

    if not items.exists():
        messages.warning(request, "Tu carro de compras está vacío.")
        return redirect('catalogo')

    subtotal = carro.obtener_subtotal()
    costo_envio = 2000
    total = subtotal + costo_envio

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            direccion = form.cleaned_data['direccion_entrega']
            metodo = form.cleaned_data['metodo_pago']

            # Crear el pedido principal
            pedido = Pedido.objects.create(
                cliente=request.user,
                direccion_entrega=direccion,
                metodo_pago=metodo,
                subtotal=subtotal,
                costo_envio=costo_envio,
                total_pagar=total,
                estado_despacho='PENDIENTE'
            )

            # Transferir items del carro al detalle del pedido y descontar stock
            for item in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                    subtotal=item.obtener_subtotal()
                )
                item.producto.stock_actual -= item.cantidad
                item.producto.save()

            # Vaciar el carro de compras
            carro.items.all().delete()

            messages.success(request, f"¡Pedido #{pedido.id} realizado exitosamente! En breve será despachado.")
            return redirect('mis_pedidos')
    else:
        # Pre-llenar la dirección con la guardada en el perfil del cliente
        direccion_inicial = request.user.perfil.direccion
        form = CheckoutForm(initial={'direccion_entrega': direccion_inicial})

    return render(request, 'delivery/checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total
    })

@login_required
def mis_pedidos_view(request):
    pedidos = Pedido.objects.filter(cliente=request.user).prefetch_related('detalles__producto').order_by('-fecha_hora')
    return render(request, 'delivery/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def cancelar_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    # Si el pedido aún está PENDIENTE, devolvemos las unidades al stock
    if pedido.estado_despacho == 'PENDIENTE':
        for detalle in pedido.detalles.all():
            producto = detalle.producto
            producto.stock_actual += detalle.cantidad
            producto.save()
        messages.success(request, f"Pedido #{pedido.id} cancelado con éxito. Se ha reabastecido el stock.")
    else:
        messages.info(request, f"Pedido #{pedido.id} eliminado de tu historial.")

    # Eliminar el registro del pedido de la base de datos
    pedido.delete()
    return redirect('mis_pedidos')