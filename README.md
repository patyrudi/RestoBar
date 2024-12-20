
# Restaurante API

Este proyecto es una API para gestionar consumos en un restaurante, permitiendo registrar productos, cambiar clientes, agregar detalles de consumo, gestionar mesas y reservas, controlar stock, gestionar empleados y cerrar un consumo generando un ticket en formato PDF.

## Requisitos

- Python
- Django
- Django REST Framework
- ReportLab (para generar PDFs)

## Instalación

1. **Clona el repositorio**:
    ```bash
    git clone https://github.com/patyrudi/RestoBar
    cd RestoBar
    ```

2. **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Aplica las migraciones**:
    ```bash
    python manage.py migrate
    ```

4. **Inicia el servidor**:
    ```bash
    python manage.py runserver
    ```

La API estará disponible en `http://127.0.0.1:8000/restaurante/api/v1/`.

## Endpoints

### Gestión de Consumos

#### 1. Abrir un Consumo para una Mesa
**URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/crear/`  
**Método**: `POST`  
**Descripción**: Abre un consumo en una mesa específica. Si ya hay un consumo abierto en la mesa (estado 1), la solicitud será rechazada.  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "ciCliente": "1234567",
    "nombre": "Juan Perez"
}
```

#### 2. Obtener el Consumo Actual de una Mesa
**URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/`  
**Método**: `GET`  
**Descripción**: Recupera el consumo actual para una mesa específica.

#### 3. Cambiar el Cliente Asociado a un Consumo Abierto
**URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/cambiar-cliente/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "ciCliente": "8765432",
    "nombre": "Ana Gomez"
}
```

#### 4. Agregar un Detalle al Consumo Actual
**URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/agregar-detalle/`  
**Método**: `POST`  
**Descripción**: Al seleccionar un producto y especificar su cantidad durante la creación del consumo, el sistema verifica automáticamente los niveles de stock disponibles. Si algún producto tiene un nivel de stock por debajo del mínimo establecido, se genera una alerta.  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "idproducto": 8,
    "cantidad": 5
}
```
**Ejemplo de Respuesta**:
```json
{
  "id": 5,
  "cantidad": 5,
  "idproducto": 8,
  "idConsumo": 6,
  "alerta_stock_minimo": "Alerta: El stock del producto ha alcanzado o es menor al mínimo (5)."
}
```

#### 5. Cerrar el Consumo Actual y Generar Ticket PDF
**URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/cerrar/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "monto_propina": 20000,
    "id_medio_pago":1
}
```
**Ejemplo de Respuesta**:
```json
{
  "message": "Consumo cerrado exitosamente.",
  "ticket_pdf": "pdf_path"
}
```

### Gestión de Mesas

#### a. Detalle de Mesa
**URL**: `/restaurante/api/v1/mesas/{idmesa}/`  
**Método**: `GET`  
**Ejemplo de Respuesta**:
```json
{
    "idmesa": 1,
    "capacidad": 5,
    "estado": "Libre",
    "area": 1
}
```

#### b. Estado de Mesas por Área
**URL**: `/restaurante/api/v1/areas/estado-mesas/`  
**Método**: `GET`  
**Ejemplo de Respuesta**:
```json
[
    {
        "area": "Terraza",
        "mesas": [
            {
                "idmesa": 1,
                "estado": "Libre",
                "capacidad": 5
            }
        ]
    },
    {
        "area": "Primer Piso",
        "mesas": [
            {
                "idmesa": 2,
                "estado": "Libre",
                "capacidad": 2
            }
        ]
    }
]
```

#### c. Asignar Cliente a una Mesa
**URL**: `/restaurante/api/v1/mesas/asignar-cliente/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "idmesa": 4,
    "ciCliente": "7535234",
    "nombre": "Rosa Franco"
}
```

---

### Gestión de Reservas

**URL**: `/restaurante/api/v1/reservas/reservar/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "fecha": "2024-12-10",
    "hora": "19:00",
    "cantidad_personas": 2,
    "contacto": "juan@correo.com",
    "ciCliente": "1234567",
    "nombre": "Juan Perez",
    "idmesa": 1
}
```
### Abrir consumo en el día de la reserva

**URL**: `/restaurante/api/v1/reservas/abrir_consumo_reserva/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
  "idreserva":3,
  "idempleado":2
}
```
---

### Gestión de Empleados

#### a. Registrar Empleado
**URL**: `/restaurante/api/v1/empleados/crear-empleado/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "nombre": "Juana Lopez",
    "area": "Terraza",
    "rol": "Mesero"
}
```

#### b. Asignar Empleado a un Consumo
**URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/crear/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "ciCliente": "12345678",
    "nombre": "Juan Pérez",
    "empleado": 2
}
```

#### c. Registro de Ventas por Empleado
**URL**: `/restaurante/api/v1/empleados/{idempleado}/registro-ventas/`  
**Método**: `GET`  

---

### Configuración del Sistema

**Obtener Configuración**:  
**URL**: `/restaurante/api/v1/configuracion-sistema/`  
**Método**: `GET`  

**Modificar Configuración**:  
**URL**: `/restaurante/api/v1/configuracion-sistema/1/`  
**Método**: `PUT`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "impuestos": 18.5,
    "moneda": "USD",
    "idioma": "en",
    "formato_impresion": "PDF"
}
```

---

### Medios de pagos

#### a. Registrar medio de pago
**URL**: `/restaurante/api/v1/medio-pago/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "descripcion":"Tarjeta credito DINELCO"
}
```

#### b. Reporte de Ventas por medio de pago
**URL**: `/restaurante/api/v1/medio-pago/{idmediopago}/reporte-ventas/`  
**Método**: `GET` 



### Pedidos
**Observacion**: Antes de realizar la prueba, se cuenta con una tabla donde se podra registrar todos los tipos de estados
manejados por el negocio. Al marcar el pedido con el estado ENRGA, el sistema simula la peticion contra pedidos ya, para
luego cambiar al nuevo estado
Pendiente	PNTE
En proceso	PROC
Para entrega	ENRGA
Entregando	ENNDO
Finalizado	FNZDO 
#### a. Registrar pedido
**URL**: `/restaurante/api/v1/pedido/`  
**Método**: `POST`  
**Cuerpo de la solicitud (JSON)**:
```json
{
    "idcliente":1,
    "productos":[
        {
            "idproducto":1,
            "cantidad":2
        }
    ],
    "idmediopago":1
}
```

#### b. Actualizar el estado del pedido
**URL**: `/restaurante/api/v1/pedido/{idpedido}/`  
**Método**: `PUT` 
**Cuerpo de la solicitud (JSON)**:
```json
{
    "codigoEstado":"ENRGA" // actualiza a disponible para entrega
}
```
