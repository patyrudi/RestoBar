from django.contrib import admin
from .models import CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo

# Lista de todos los modelos
models = [CategoriaProducto, Producto, Mesa, Cliente, Consumo, DetalleConsumo]

# Registrar cada modelo en el admin
for model in models:
    admin.site.register(model)
