from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaProductoViewSet, 
    ProductoViewSet, 
    MesaViewSet, 
    ClienteViewSet, 
    ConsumoViewSet, 
    DetalleConsumoViewSet
)

# Crear el router
router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'mesas', MesaViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'consumos', ConsumoViewSet)
router.register(r'detalles-consumo', DetalleConsumoViewSet)

# Incluir las rutas generadas por el router
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
