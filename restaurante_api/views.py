from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import datetime 
from .models import CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo, Reserva, Empleado, Rol,  ConfiguracionSistema, Pedido, DetallePedido, TipoEstadoPedido, EstadoPedido, MedioPago
from .serializer import (
    CategoriaProductoSerializer, 
    ProductoSerializer, 
    MesaSerializer, 
    ClienteSerializer, 
    ConsumoSerializer, 
    DetalleConsumoSerializer,
    AreaSerializer,
    ReservaSerializer, 
    EmpleadoSerializer,
    RolSerializer,
    Area,
    ConfiguracionSistemaSerializer,
    PedidoSerializer,
    DetalleProductoSerializer
)

class ConsumoViewSet(viewsets.ModelViewSet):
    queryset = Consumo.objects.all()
    serializer_class = ConsumoSerializer

    def create(self, request, *args, **kwargs):
        idmesa = request.data.get("idmesa")

        if Consumo.objects.filter(idmesa=idmesa, estado=1).exists():
            raise ValidationError({"error": "La mesa ya tiene un consumo abierto."})

        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], url_path=r'mesa/(?P<idmesa>\d+)/crear')
    def abrir_consumo(self, request, idmesa=None):
        """
        Abre un consumo en la mesa especificada.
        Valida que no haya un consumo abierto, recibe los datos del cliente y asigna un mesero.
        Verifica que el mesero pertenezca al área de la mesa y considera las reservas.
        """
        if Consumo.objects.filter(idmesa=idmesa, estado=1).exists():
            return Response({"error": "La mesa ya tiene un consumo abierto."}, status=status.HTTP_400_BAD_REQUEST)

        ciCliente = request.data.get("ciCliente")
        nombre = request.data.get("nombre")

        if ciCliente:
            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})
        else:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        id_empleado = request.data.get("empleado")
        try:
            empleado = Empleado.objects.get(idempleado=id_empleado, rol__nombre="Mesero")
        except Empleado.DoesNotExist:
            return Response({"error": "El empleado no existe o no tiene el rol de 'Mesero'."}, status=status.HTTP_404_NOT_FOUND)

        try:
            mesa = Mesa.objects.get(idmesa=idmesa)
            if mesa.estado == 'Ocupada':
                return Response({"error": "La mesa ya está ocupada."}, status=status.HTTP_400_BAD_REQUEST)

            if mesa.estado == 'Reservada':
                reservas_hoy = Reserva.objects.filter(
                    mesa=mesa,
                    fecha=datetime.date.today()
                )
                if reservas_hoy.exists():
                    return Response({"error": "La mesa tiene una reserva para hoy y no se puede abrir un consumo."}, status=status.HTTP_400_BAD_REQUEST)
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        if mesa.area != empleado.area:
            return Response({"error": f"El mesero no trabaja en el área de la mesa {mesa.area.nombre}."}, status=status.HTTP_400_BAD_REQUEST)
        consumo = Consumo.objects.create(
            idmesa=mesa,
            idcliente=cliente,
            empleado=empleado,
        )

        mesa.estado = "Ocupada"
        mesa.save()

        serializer = ConsumoSerializer(consumo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path=r'mesa/(?P<idmesa>\d+)')
    def consumo_actual(self, request, idmesa=None):
        """
        Recupera el consumo actual para una mesa con consumo abierto específica.
        """
        try:
            consumo = Consumo.objects.filter(idmesa=idmesa, estado=1).first()
            if not consumo:
                return Response({"error": "La mesa no tiene consumos abiertos."}, status=status.HTTP_404_NOT_FOUND)
            
            if consumo.estado != 1:
                return Response({"error": "El consumo ya está cerrado."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = ConsumoSerializer(consumo)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no existe."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path=r'mesa/(?P<idmesa>\d+)/cambiar-cliente')
    def cambiar_cliente(self, request, idmesa=None):
        """
        Permite cambiar el cliente asociado a un consumo abierto para una mesa específica.
        """
        try:
            consumo = Consumo.objects.filter(idmesa=idmesa, estado=1).first()
            if not consumo:
                return Response({"error": "La mesa no tiene consumos abiertos."}, status=status.HTTP_404_NOT_FOUND)

            ciCliente = request.data.get("ciCliente")
            nombre = request.data.get("nombre")

            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})
            consumo.idcliente = cliente
            consumo.save()

            return Response({"message": "Cliente actualizado exitosamente."}, status=status.HTTP_200_OK)
        except Consumo.DoesNotExist:
            return Response({"error": "Consumo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path=r'mesa/(?P<idmesa>\d+)/agregar-detalle')
    def agregar_detalle(self, request, idmesa=None):
        """
        Agrega un nuevo detalle de consumo al consumo actual para una mesa específica.
        Actualiza el stock de los productos y verifica si el stock mínimo ha sido alcanzado.
        """
        try:
            consumo = Consumo.objects.filter(idmesa=idmesa, estado=1).first()
            if not consumo:
                return Response({"error": "La mesa no tiene consumos abiertos."}, status=status.HTTP_404_NOT_FOUND)

            idproducto = request.data.get("idproducto")
            cantidad = request.data.get("cantidad")

            producto = Producto.objects.get(idproducto=idproducto)

            if producto.stock < cantidad:
                return Response({"error": "No hay suficiente stock."}, status=status.HTTP_400_BAD_REQUEST)

            detalle = DetalleConsumo.objects.create(idproducto=producto, idConsumo=consumo, cantidad=cantidad)

            producto.stock -= cantidad
            producto.save()

            consumo.total += producto.precio * cantidad
            consumo.save()

            mensaje_alerta = ""
            if producto.stock <= producto.stock_minimo:
                mensaje_alerta = f"Alerta: El stock del producto ha alcanzado o es menor al mínimo ({producto.stock_minimo})."

            detalle_serializer = DetalleConsumoSerializer(detalle)

            response_data = detalle_serializer.data
            if mensaje_alerta:
                response_data["alerta_stock_minimo"] = mensaje_alerta

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path=r'mesa/(?P<idmesa>\d+)/cerrar')
    def cerrar_consumo(self, request, idmesa=None):
        """
        Cierra el consumo actual y genera el ticket en PDF para una mesa específica.
        """
        try:
            consumo = Consumo.objects.filter(idmesa=idmesa, estado=1).first()
            mesa = Mesa.objects.filter(idmesa=idmesa, estado="Ocupada").first()
            if not consumo:
                return Response({"error": "La mesa no tiene consumos abiertos."}, status=status.HTTP_404_NOT_FOUND)

            # Cambiar estado a cerrado y guardar la fecha de cierre
            consumo.estado = 2
            consumo.fecha_cierre = timezone.now()
            consumo.save()

            mesa.estado = "Libre"
            mesa.save()

            # Generar el ticket PDF
            pdf_path = self.generar_ticket(consumo)

            return Response({
                "message": "Consumo cerrado exitosamente.",
                "ticket_pdf": pdf_path
            }, status=status.HTTP_200_OK)
        except Consumo.DoesNotExist:
            return Response({"error": "Consumo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def generar_ticket(self, consumo):
        # Ruta para guardar el PDF
        pdf_dir = "tickets"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filename = f"ticket_consumo_{consumo.idConsumo}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        # Crear el canvas para el PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setTitle(f"Ticket Consumo {consumo.idConsumo}")

        # Encabezado
        c.drawString(100, 750, f"Ticket de Consumo - ID: {consumo.idConsumo}")
        c.drawString(100, 730, f"Fecha: {consumo.fecha_cierre.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 710, f"Cliente: {consumo.idcliente.nombre}")

        # Detalles del consumo
        y_position = 680
        c.drawString(100, y_position, "Detalles del Consumo:")
        y_position -= 20
        total = 0

        for detalle in DetalleConsumo.objects.filter(idConsumo=consumo):
            producto = detalle.idproducto.nombreProducto
            cantidad = detalle.cantidad
            precio = detalle.idproducto.precio
            subtotal = cantidad * precio
            total += subtotal

            c.drawString(100, y_position, f"{producto} - Cantidad: {cantidad} - Precio: {precio} - Subtotal: {subtotal}")
            y_position -= 20

        # Total del consumo
        y_position -= 20
        c.drawString(100, y_position, f"Total: {total}")

        # Finalizar y guardar el PDF
        c.showPage()
        c.save()

        return pdf_path
    

class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer

    @action(detail=False, methods=['post'], url_path='asignar-cliente')
    def asignar_cliente(self, request):
        """
        Asigna manualmente un cliente a una mesa. Si el cliente no existe, se crea con el nombre proporcionado.
        """
        idmesa = request.data.get("idmesa")
        ciCliente = request.data.get("ciCliente")
        nombre = request.data.get("nombre")

        if not ciCliente:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})

            if created and not nombre:
                return Response({"error": "El nombre del cliente es obligatorio cuando el cliente no está registrado."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            mesa = Mesa.objects.get(idmesa=idmesa)

            if mesa.estado == 'Ocupada':
                return Response({"error": "La mesa ya está ocupada."}, status=status.HTTP_400_BAD_REQUEST)
            
            if mesa.estado == 'Reservada':
                return Response({"error": "La mesa está reservada."}, status=status.HTTP_400_BAD_REQUEST)

            mesa.estado = 'Ocupada'
            mesa.save()

            consumo = Consumo.objects.create(idmesa=mesa, idcliente=cliente)

            serializer = ConsumoSerializer(consumo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

    @action(detail=False, methods=['get'], url_path='estado-mesas')
    def estado_mesas(self, request):
        """
        Devuelve el estado de las mesas en formato JSON (libre, ocupada) junto con su área.
        """
        mesas_estado = []

        for area in self.queryset:
            mesas = Mesa.objects.filter(area=area)
            mesas_info = [{
                "idmesa": mesa.idmesa,
                "estado": mesa.estado,
                "area": area.nombre,
                "capacidad": mesa.capacidad
            } for mesa in mesas]
            
            mesas_estado.append({
                "area": area.nombre,
                "mesas": mesas_info
            })

        return Response(mesas_estado)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    @action(detail=False, methods=['post'], url_path='reservar')
    def realizar_reserva(self, request):
        """
        Realiza una reserva para una mesa específica.
        Verifica la disponibilidad de la mesa, la capacidad y asocia un cliente.
        """
        idmesa = request.data.get("idmesa")
        fecha = request.data.get("fecha")
        hora = request.data.get("hora")
        cantidad_personas = request.data.get("cantidad_personas")
        contacto = request.data.get("contacto")
        ciCliente = request.data.get("ciCliente")
        nombre_cliente = request.data.get("nombre")

        if not ciCliente:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        if Reserva.objects.filter(mesa=idmesa, fecha=fecha, hora=hora).exists():
            return Response({"error": "La mesa ya está reservada en este horario."}, status=status.HTTP_400_BAD_REQUEST)

        cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre_cliente})

        try:
            mesa = Mesa.objects.get(idmesa=idmesa)
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if cantidad_personas > mesa.capacidad:
            return Response({"error": f"La cantidad de personas excede la capacidad de la mesa ({mesa.capacidad})."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        mesa.estado = 'Reservada'
        mesa.save()

        reserva = Reserva.objects.create(
            cliente=cliente,
            mesa=mesa,
            fecha=fecha,
            hora=hora,
            cantidad_personas=cantidad_personas,
            contacto=contacto
        )
        reserva_serializer = ReservaSerializer(reserva)
        return Response(reserva_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='abrir_consumo_reserva')
    def abrir_consumo_reserva(self, request):
        """
        Abre un consumo basado en una reserva existente.
        Utiliza los datos de la reserva y valida al mesero asignado.
        """
        idreserva = request.data.get("idreserva")
        idempleado = request.data.get("idempleado")

        if not idreserva:
            return Response({"error": "El campo idreserva es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
        if not idempleado:
            return Response({"error": "El campo idempleado es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reserva = Reserva.objects.get(idreserva=idreserva)
        except Reserva.DoesNotExist:
            return Response({"error": "Reserva no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if Consumo.objects.filter(idmesa=reserva.mesa, estado=1).exists():
            return Response({"error": "La mesa ya tiene un consumo abierto."}, status=status.HTTP_400_BAD_REQUEST)

        if reserva.fecha != datetime.date.today():
            return Response({"error": "La reserva no es para hoy."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            empleado = Empleado.objects.get(idempleado=idempleado, rol__nombre="Mesero")
        except Empleado.DoesNotExist:
            return Response({"error": "El empleado no existe o no tiene el rol de 'Mesero'."}, status=status.HTTP_404_NOT_FOUND)

        if empleado.area != reserva.mesa.area:
            return Response({"error": f"El mesero no trabaja en el área de la mesa {reserva.mesa.area.nombre}."},
                            status=status.HTTP_400_BAD_REQUEST)

        consumo = Consumo.objects.create(
            idmesa=reserva.mesa,
            idcliente=reserva.cliente,
            empleado=empleado,
        )

        reserva.mesa.estado = "Ocupada"
        reserva.mesa.save()

        serializer = ConsumoSerializer(consumo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer

    @action(detail=False, methods=['post'], url_path='crear-empleado')
    def crear_empleado(self, request):
        """
        Crea un empleado validando que el rol y el área existan.
        Si no existen, devuelve un error con las posibles opciones.
        """
        nombre = request.data.get("nombre")
        area_nombre = request.data.get("area")
        rol_nombre = request.data.get("rol")

        if not nombre:
            return Response({"error": "El campo 'nombre' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        errores = {}
        area = None
        rol = None

        try:
            area = Area.objects.get(nombre=area_nombre)
        except Area.DoesNotExist:
            errores["area"] = list(Area.objects.values_list("nombre", flat=True))

        try:
            rol = Rol.objects.get(nombre=rol_nombre)
        except Rol.DoesNotExist:
            errores["rol"] = list(Rol.objects.values_list("nombre", flat=True))

        if errores:
            return Response(
                {
                    "error": "No existe el rol o área proporcionados.",
                    "posibles_opciones": errores
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        empleado = Empleado.objects.create(nombre=nombre, area=area, rol=rol)

        serializer = self.get_serializer(empleado)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='registro-ventas')
    def reporte_ventas(self, request, pk=None):
        empleado = self.get_object()

        consumos = Consumo.objects.filter(empleado=empleado)

        total_ventas = consumos.aggregate(total=Sum('total')).get('total', 0) or 0

        data = {
            "empleado": empleado.nombre,
            "rol": empleado.rol.nombre,
            "total_ingresos": total_ventas,
            "consumos": [
                {
                    "idConsumo": c.idConsumo,
                    "mesa": c.idmesa.idmesa,
                    "total": c.total,
                    "fecha": c.fecha_inicio,
                }
                for c in consumos
            ],
        }

        return Response(data)

class DetalleConsumoViewSet(viewsets.ModelViewSet):
    queryset = DetalleConsumo.objects.all()
    serializer_class = DetalleConsumoSerializer

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class ConfiguracionSistemaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionSistema.objects.all()
    serializer_class = ConfiguracionSistemaSerializer

    def create(self, request, *args, **kwargs):
        if ConfiguracionSistema.objects.exists():
            return Response(
                {"error": "Ya existe una configuración del sistema. No se pueden crear más configuraciones."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def create(self, request):
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            # Crear el pedido
            idcliente = serializer.validated_data['idcliente']
            idmediopago = serializer.validated_data['idmediopago']
            productos = serializer.validated_data['productos']
            direccion_entrega = serializer.validated_data['direccionEntrega']

            if not productos:
                return Response({"message": "No se proporcionaron productos para el pedido."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                cliente = Cliente.objects.get(idcliente=idcliente)
            except Cliente.DoesNotExist:
                return Response(
                    {"message": f"Cliente con ID {idcliente} no encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                mediopago = MedioPago.objects.get(idmediopago=idmediopago)
            except MedioPago.DoesNotExist:
                return Response(
                    {"message": f"Medio de pago con ID {idcliente} no encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )

            estado_pedido = TipoEstadoPedido.objects.get(codigo = 'PNTE');
            
            pedido = Pedido.objects.create(
                idcliente_id=idcliente,
                idmediopago_id=idmediopago,
                idestadopedido_id= estado_pedido.idtipoestado,
                totalpedido=0,
                direccion_entrega= direccion_entrega
            )

            total = 0
            for producto_data in productos:
                idproducto = producto_data['idproducto']
                cantidad = producto_data['cantidad']

                producto = Producto.objects.get(idproducto=idproducto)

                try:
                    # verificacion si existe el producto
                    producto = Producto.objects.get(idproducto=idproducto)
                except Producto.DoesNotExist:
                    return Response(
                        {"message": f"Producto con ID {idproducto} no encontrado."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                if producto.stock < cantidad:
                    return Response({"message": f"No se cuenta con stock suficiente para el producto {producto.nombreProducto} ."}, status=status.HTTP_400_BAD_REQUEST)

                total += producto.precio * cantidad

                # Crear detalle del pedido
                DetallePedido.objects.create(
                    idpedido=pedido,
                    idproducto=producto,
                    cantidad=cantidad,
                )

                # Actualizar stock
                producto.stock -= cantidad
                producto.save()

            # Actualizar total del pedido
            pedido.totalpedido = total
            pedido.save()

            EstadoPedido.objects.create(
                idtipoestado_id = estado_pedido.idtipoestado,
                idpedido_id= pedido.idpedido
            )

            return Response({"idpedido": pedido.idpedido, 
                            "message": "Pedido creado con éxito.",
                            "totalPagar": total
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self, request, pk=None):
        data = request.data
        codigo_estado = data.get('codigoEstado')

        if codigo_estado is None:
            return Response({"message": "Debe proporcionar el nuevo estado del pedido."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = Pedido.objects.get(pk=pk) 
        except Pedido.DoesNotExist: 
            return Response({"message": "Pedido no encontrado."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        try:
            tipoestado = TipoEstadoPedido.objects.get(codigo=codigo_estado) 
        except Pedido.DoesNotExist: 
            return Response({"message": f"No existe el estado {codigo_estado}."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        EstadoPedido.objects.create(
            idtipoestado_id = tipoestado.idtipoestado,
            idpedido_id= pedido.idpedido
        )

        if codigo_estado == 'ENRGA':
            # aqui se simula la peticion a la API de pedidos ya 
            self.enviar_a_pedidos_ya(pedido)
            
        
        pedido.idestadopedido_id = tipoestado.idtipoestado
        pedido.save()

        return Response({
                        "message": f"Se actualizo con éxito el estado del pedido.",
                        "estado": tipoestado.descripcion
        }, status=status.HTTP_200_OK)
    
    def enviar_a_pedidos_ya(self, pedido):
        # Obtener detalles del pedido
        cliente = pedido.idcliente
        detalles = DetallePedido.objects.filter(idpedido=pedido.idpedido)
        
        # Construir la lista de productos
        productos = []
        for detalle in detalles:
            producto = Producto.objects.get(idproducto=detalle.idproducto_id)
            productos.append({
                "nombre": producto.nombreProducto,
                "cantidad": detalle.cantidad,
                "precio_unitario": producto.precio
            })

        # Construir el payload
        payload = {
            "cliente": {
                "nombre": cliente.nombre,
                "direccion": pedido.direccion_entrega,
            },
            "pedido": {
                "monto_total": pedido.totalpedido,
                "productos": productos
            },
            "medio_pago": {
                "descripcion": pedido.idmediopago.descripcion
            },
            "entrega": {
                "tipo": "delivery",
                "instrucciones": "Tocar el timbre y dejar en la puerta si no hay respuesta."
            }
        }

        # Aquí podrías realizar la solicitud a la API de PedidosYa
        # Por ejemplo:
        # response = requests.post("https://api.pedidosya.com/delivery", json=payload)
        # print(response.json())

        # Simulación
        print("Payload enviado a PedidosYa:", payload)