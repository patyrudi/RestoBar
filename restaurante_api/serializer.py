from rest_framework import serializers
from .models import CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo, Reserva, Empleado, Area, Rol

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class DetalleConsumoSerializer(serializers.ModelSerializer):
    # Puedes agregar más campos si es necesario, como el subtotal calculado si no está en el modelo.
    class Meta:
        model = DetalleConsumo
        fields = '__all__'


class ConsumoSerializer(serializers.ModelSerializer):
    detalles_consumo = DetalleConsumoSerializer(source='detalles', many=True, read_only=True)

    class Meta:
        model = Consumo
        fields = ['idConsumo', 'estado', 'total', 'fecha_inicio', 'fecha_cierre', 'idmesa', 'idcliente', 'detalles_consumo']

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'