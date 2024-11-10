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

    def __str__(self):
        return self.nombreProducto


class Mesa(models.Model):
    idmesa = models.AutoField(primary_key=True)

    def __str__(self):
        return f'Mesa {self.idmesa}'


class Cliente(models.Model):
    idcliente = models.AutoField(primary_key=True)
    ciCliente = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=100) 

    def __str__(self):
        return self.nombre

class Consumo(models.Model):
    ESTADO_CHOICES = [
        (1, 'Abierto'),
        (2, 'Cerrado'),
    ]
    idConsumo = models.AutoField(primary_key=True)
    idmesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='consumos')
    idcliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='consumos')
    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES, default=1)
    total = models.PositiveIntegerField(default=0)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Consumo {self.idConsumo} - Mesa {self.idmesa.idmesa}'


class DetalleConsumo(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_consumo')
    idConsumo = models.ForeignKey(Consumo, on_delete=models.CASCADE, related_name='detalles')
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.cantidad} x {self.idproducto.nombreProducto} (Consumo {self.idConsumo.idConsumo})'