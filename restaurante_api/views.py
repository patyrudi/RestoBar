from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from .models import CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo
from .serializer import (
    CategoriaProductoSerializer, 
    ProductoSerializer, 
    MesaSerializer, 
    ClienteSerializer, 
    ConsumoSerializer, 
    DetalleConsumoSerializer
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
        Valida que no haya un consumo abierto y recibe los datos del cliente.
        """
        if Consumo.objects.filter(idmesa=idmesa, estado=1).exists():
            raise ValidationError({"error": "La mesa ya tiene un consumo abierto."})
            
        ciCliente = request.data.get("ciCliente")
        nombre = request.data.get("nombre")

        if ciCliente:
            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})
        else:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mesa = Mesa.objects.get(idmesa=idmesa) 
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        consumo = Consumo.objects.create(
            idmesa=mesa,
            idcliente=cliente,
        )

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
        """
        try:
            consumo = Consumo.objects.filter(idmesa=idmesa, estado=1).first()
            if not consumo:
                return Response({"error": "La mesa no tiene consumos abiertos."}, status=status.HTTP_404_NOT_FOUND)

            idproducto = request.data.get("idproducto")
            cantidad = request.data.get("cantidad")

            producto = Producto.objects.get(idproducto=idproducto)
            detalle = DetalleConsumo.objects.create(idproducto=producto, idConsumo=consumo, cantidad=cantidad)

            consumo.total += producto.precio * cantidad
            consumo.save()

            detalle_serializer = DetalleConsumoSerializer(detalle)
            return Response(detalle_serializer.data, status=status.HTTP_201_CREATED)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    
    @action(detail=False, methods=['post'], url_path=r'mesa/(?P<idmesa>\d+)/cerrar')
    def cerrar_consumo(self, request, idmesa=None):
        """
        Cierra el consumo actual y genera el ticket en PDF para una mesa específica.
        """
        try:
            consumo = Consumo.objects.filter(idmesa=idmesa, estado=1).first()
            if not consumo:
                return Response({"error": "La mesa no tiene consumos abiertos."}, status=status.HTTP_404_NOT_FOUND)

            consumo.estado = 2
            consumo.fecha_cierre = timezone.now()
            consumo.save()
            
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
    

class DetalleConsumoViewSet(viewsets.ModelViewSet):
    queryset = DetalleConsumo.objects.all()
    serializer_class = DetalleConsumoSerializer

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer



