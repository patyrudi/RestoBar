from django.db import models

class CategoriaProducto(models.Model):
    idcategoriaProducto = models.AutoField(primary_key=True)
    nombreCategoria = models.CharField(max_length=45)

    def __str__(self):
        return self.nombreCategoria

class Producto(models.Model):
    idproducto = models.AutoField(primary_key=True)
    idcategoriaProducto = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, related_name='productos')
    nombreProducto = models.CharField(max_length=100)
    precio = models.PositiveIntegerField() 
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombreProducto

class Cliente(models.Model):
    idcliente = models.AutoField(primary_key=True)
    ciCliente = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=100) 

    def __str__(self):
        return self.nombre
    
class Rol(models.Model):
    idrol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
    
class Area(models.Model):
    idarea = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    idempleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='empleados' )
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, related_name='empleados')

    def __str__(self):
        return self.nombre
    


class Mesa(models.Model):
    idmesa = models.AutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, related_name='mesas')
    capacidad = models.PositiveIntegerField(default=2)
    estado = models.CharField(max_length=10, choices=[('Libre', 'Libre'), ('Ocupada', 'Ocupada'), ('Reservada', 'Reservada')], default='Libre')

    def __str__(self):
        return f'Mesa {self.idmesa} - {self.area.nombre if self.area else "Sin área"}'

class Reserva(models.Model):
    idreserva = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, related_name='reservas')
    fecha = models.DateField()
    hora = models.TimeField()
    cantidad_personas = models.PositiveIntegerField()
    contacto = models.CharField(max_length=50)

    def __str__(self):
        return f'Reserva {self.idreserva} - Mesa {self.mesa.idmesa if self.mesa else "No asignada"}'

class Consumo(models.Model):
    ESTADO_CHOICES = [
        (1, 'Abierto'),
        (2, 'Cerrado'),
    ]
    idConsumo = models.AutoField(primary_key=True)
    idmesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='consumos')
    idcliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='consumos')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, default=1, related_name='consumos')
    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES, default=1)
    total = models.PositiveIntegerField(default=0)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_propina = models.PositiveIntegerField(default=0)
    idmediopago = models.ForeignKey('MedioPago', on_delete=models.CASCADE, null=True, related_name='consumos')

    def __str__(self):
        return f'Consumo {self.idConsumo} - Mesa {self.idmesa.idmesa}'


class DetalleConsumo(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_consumo')
    idConsumo = models.ForeignKey(Consumo, on_delete=models.CASCADE, related_name='detalles')
    cantidad = models.PositiveIntegerField()
    
    def __str__(self):
        return f'{self.cantidad} x {self.idproducto.nombreProducto} (Consumo {self.idConsumo.idConsumo})'
    
#Patron singleton para evitar crear muchas configuraciones y solo mantener una
class ConfiguracionSistema(models.Model):
    impuestos = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Porcentaje de impuestos aplicables.")
    moneda = models.CharField(max_length=3, default='PYG', help_text="Código de la moneda utilizada, e.g., 'USD', 'EUR'.")
    idioma = models.CharField(max_length=10, default='es', help_text="Código del idioma, e.g., 'es' para español.")
    formato_impresion = models.CharField(max_length=100, default='PDF', help_text="Formato de impresión preferido.")

    def save(self, *args, **kwargs):
        # Verificar si ya existe una instancia
        if not self.pk and ConfiguracionSistema.objects.exists():
            raise ValueError("Solo puede existir una configuración del sistema.")
        super(ConfiguracionSistema, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Retornar la instancia existente o crearla si no existe
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración del sistema"


class MedioPago(models.Model):
    idmediopago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Pedido(models.Model):
    idpedido = models.AutoField(primary_key=True)
    fechapedido = models.DateTimeField(auto_now_add=True)
    idcliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='pedidos')
    idempleado = models.ForeignKey('Empleado', null=True, on_delete=models.CASCADE, related_name='pedidos')
    totalpedido = models.DecimalField(max_digits=10, decimal_places=2)
    idestadopedido = models.ForeignKey('TipoEstadoPedido', on_delete=models.CASCADE, null=True, related_name='pedidos')
    idmediopago = models.ForeignKey('MedioPago', on_delete=models.CASCADE, null=True, related_name='pedidos')
    direccion_entrega = models.CharField(max_length=100)

    def __str__(self):
        return f"Pedido #{self.idpedido} - Cliente: {self.idcliente.nombre}"

class DetallePedido(models.Model):
    iddetalle = models.AutoField(primary_key=True)
    idpedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    idproducto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='detalles')
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"Detalle #{self.iddetalle} - Pedido: {self.idpedido.idpedido}"

class TipoEstadoPedido(models.Model):
    idtipoestado = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class EstadoPedido(models.Model):
    idtipoestado = models.ForeignKey(TipoEstadoPedido, on_delete=models.CASCADE, related_name='estados')
    idpedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='estados')
    fechacreacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Estado: {self.idtipoestado.descripcion} - Pedido: {self.idpedido.idpedido}"
