from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
<<<<<<< HEAD
from .models import CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo, Reserva, Empleado, Rol,  ConfiguracionSistema
=======
from .models import CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo, Reserva, Empleado, Rol, Area
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
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
<<<<<<< HEAD
    RolSerializer,
    Area,
    ConfiguracionSistemaSerializer
=======
    RolSerializer
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
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
        Verifica que el mesero pertenezca al área de la mesa.
        """
        if Consumo.objects.filter(idmesa=idmesa, estado=1).exists():
<<<<<<< HEAD
            return Response({"error": "La mesa ya tiene un consumo abierto."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear el cliente
=======
            raise ValidationError({"error": "La mesa ya tiene un consumo abierto."})
            
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
        ciCliente = request.data.get("ciCliente")
        nombre = request.data.get("nombre")

        if ciCliente:
            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})
        else:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

<<<<<<< HEAD
        # Obtener el empleado (mesero) que se asignará
        id_empleado = request.data.get("empleado")
        try:
            empleado = Empleado.objects.get(idempleado=id_empleado, rol__nombre="Mesero")
        except Empleado.DoesNotExist:
            return Response({"error": "El empleado no existe o no tiene el rol de 'Mesero'."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si la mesa existe
        try:
            mesa = Mesa.objects.get(idmesa=idmesa)
=======
        try:
            mesa = Mesa.objects.get(idmesa=idmesa) 
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Validar que el mesero trabaja en el mismo área que la mesa
        if mesa.area != empleado.area:
            return Response({"error": f"El mesero no trabaja en el área de la mesa {mesa.area.nombre}."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el consumo para la mesa con el cliente y el mesero asignado
        consumo = Consumo.objects.create(
            idmesa=mesa,
            idcliente=cliente,
            empleado=empleado,
        )

        mesa.estado = "Ocupada"
        mesa.save()

        # Retornar la respuesta con los datos del consumo
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

            # Verificar si hay suficiente stock
            if producto.stock < cantidad:
                return Response({"error": "No hay suficiente stock."}, status=status.HTTP_400_BAD_REQUEST)

            # Crear detalle de consumo
            detalle = DetalleConsumo.objects.create(idproducto=producto, idConsumo=consumo, cantidad=cantidad)

<<<<<<< HEAD
            # Actualizar el stock
            producto.stock -= cantidad
            producto.save()

            # Actualizar el total del consumo
=======
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
            consumo.total += producto.precio * cantidad
            consumo.save()

            # Verificar si el stock ha alcanzado el nivel mínimo
            mensaje_alerta = ""
            if producto.stock <= producto.stock_minimo:
                mensaje_alerta = f"Alerta: El stock del producto ha alcanzado o es menor al mínimo ({producto.stock_minimo})."

            # Serializar el detalle de consumo
            detalle_serializer = DetalleConsumoSerializer(detalle)

            # Responder con los datos del detalle y la alerta de stock mínimo, si aplica
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

            consumo.estado = 2
            consumo.fecha_cierre = timezone.now()
            consumo.save()
<<<<<<< HEAD

            mesa.estado = "Libre"
            mesa.save()

            # Generar el ticket PDF
=======
            
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
            pdf_path = self.generar_ticket(consumo)

            return Response({
                "message": "Consumo cerrado exitosamente.",
                "ticket_pdf": pdf_path
            }, status=status.HTTP_200_OK)
        except Consumo.DoesNotExist:
            return Response({"error": "Consumo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def generar_ticket(self, consumo):
  
        pdf_dir = "tickets"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filename = f"ticket_consumo_{consumo.idConsumo}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)

    
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setTitle(f"Ticket Consumo {consumo.idConsumo}")

   
        c.drawString(100, 750, f"Ticket de Consumo - ID: {consumo.idConsumo}")
        c.drawString(100, 730, f"Fecha: {consumo.fecha_cierre.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 710, f"Cliente: {consumo.idcliente.nombre}")

     
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

      
        y_position -= 20
        c.drawString(100, y_position, f"Total: {total}")


        c.showPage()
        c.save()

        return pdf_path

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

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

        # Verificar si se ha proporcionado un CI de cliente
        if not ciCliente:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear el cliente
        try:
            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})

            # Si el cliente no existía y no se proporcionó nombre, debe devolverse un error
            if created and not nombre:
                return Response({"error": "El nombre del cliente es obligatorio cuando el cliente no está registrado."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # Si el cliente fue encontrado o creado con éxito, obtenemos la mesa
            mesa = Mesa.objects.get(idmesa=idmesa)

            # Verificar si la mesa está ocupada
            if mesa.estado == 'Ocupada':
                return Response({"error": "La mesa ya está ocupada."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si la mesa está reservada
            if mesa.estado == 'Reservada':
                return Response({"error": "La mesa está reservada."}, status=status.HTTP_400_BAD_REQUEST)

            # Cambiar el estado de la mesa a ocupada
            mesa.estado = 'Ocupada'
            mesa.save()

            # Crear un consumo para la mesa y el cliente
            consumo = Consumo.objects.create(idmesa=mesa, idcliente=cliente)

            # Retornar el consumo creado
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
        # Obtener datos de la reserva desde el request
        idmesa = request.data.get("idmesa")
        fecha = request.data.get("fecha")
        hora = request.data.get("hora")
        cantidad_personas = request.data.get("cantidad_personas")
        contacto = request.data.get("contacto")
        ciCliente = request.data.get("ciCliente")
        nombre_cliente = request.data.get("nombre")

        # Validar que el campo ciCliente está presente
        if not ciCliente:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la mesa está disponible para la fecha y hora solicitadas
        if Reserva.objects.filter(mesa=idmesa, fecha=fecha, hora=hora).exists():
            return Response({"error": "La mesa ya está reservada en este horario."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar o crear el cliente basado en el ciCliente
        cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre_cliente})

        # Verificar si la mesa existe
        try:
            mesa = Mesa.objects.get(idmesa=idmesa)
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Validar si la cantidad de personas excede la capacidad de la mesa
        if cantidad_personas > mesa.capacidad:
            return Response({"error": f"La cantidad de personas excede la capacidad de la mesa ({mesa.capacidad})."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Cambiar el estado de la mesa a 'Reservada'
        mesa.estado = 'Reservada'
        mesa.save()

        # Crear la reserva
        reserva = Reserva.objects.create(
            cliente=cliente,
            mesa=mesa,
            fecha=fecha,
            hora=hora,
            cantidad_personas=cantidad_personas,
            contacto=contacto
        )

        # Retornar respuesta con los datos de la reserva
        reserva_serializer = ReservaSerializer(reserva)
        return Response(reserva_serializer.data, status=status.HTTP_201_CREATED)



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

        # Verificar que el nombre está presente
        if not nombre:
            return Response({"error": "El campo 'nombre' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        errores = {}
        area = None
        rol = None

        # Validar área
        try:
            area = Area.objects.get(nombre=area_nombre)
        except Area.DoesNotExist:
            errores["area"] = list(Area.objects.values_list("nombre", flat=True))

        # Validar rol
        try:
            rol = Rol.objects.get(nombre=rol_nombre)
        except Rol.DoesNotExist:
            errores["rol"] = list(Rol.objects.values_list("nombre", flat=True))

        # Si hay errores, retornar respuesta
        if errores:
            return Response(
                {
                    "error": "No existe el rol o área proporcionados.",
                    "posibles_opciones": errores
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear empleado
        empleado = Empleado.objects.create(nombre=nombre, area=area, rol=rol)

        # Serializar y retornar el empleado creado
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
<<<<<<< HEAD

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
    
=======
>>>>>>> f15cb2a5528b7202102cb788d8c236d045a2991b
