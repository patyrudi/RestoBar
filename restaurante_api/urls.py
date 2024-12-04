from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaProductoViewSet, 
    ProductoViewSet, 
    MesaViewSet, 
    ClienteViewSet, 
    ConsumoViewSet, 
    DetalleConsumoViewSet,
    ReservaViewSet, 
    EmpleadoViewSet,
    RolViewSet,
    AreaViewSet,
    ConfiguracionSistemaViewSet
)

# Crear el router
router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'mesas', MesaViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'consumos', ConsumoViewSet)
router.register(r'detalles-consumo', DetalleConsumoViewSet)
router.register(r'reservas', ReservaViewSet)  
router.register(r'empleados', EmpleadoViewSet)  
router.register(r'roles', RolViewSet)  
router.register(r'areas', AreaViewSet)
router.register(r'configuracion-sistema',ConfiguracionSistemaViewSet)

# Incluir las rutas generadas por el router
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
