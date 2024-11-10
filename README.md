# Restaurante API

Este proyecto es una API para gestionar consumos en un restaurante, permitiendo registrar productos, cambiar clientes, agregar detalles de consumo y cerrar un consumo generando un ticket en formato PDF.

## Requisitos

- Python
- Django
- Django REST Framework
- ReportLab (para generar PDFs)

## Instalación

1. **Clona el repositorio**:
    ```bash
    git clone https://github.com/patyrudi/restauranteAPI
    cd restauranteAPI
    ```

2. **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Migrations**:
    Asegúrate de tener las migraciones aplicadas para que la base de datos esté lista:
    ```bash
    python manage.py migrate
    ```

4. **Inicia el servidor**:
    ```bash
    python manage.py runserver
    ```

La API estará disponible en `http://127.0.0.1:8000/restaurante/api/v1/`

## Endpoints

### 1. **Abrir un Consumo para una Mesa**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/crear`
   
   **Método**: `POST`
   
   **Descripción**: Este endpoint abre un consumo en una mesa específica. Si ya hay un consumo abierto en la mesa (estado 1), la solicitud será rechazada.
   
   **Cuerpo de la solicitud (JSON)**:
   ```json
   {
       "ciCliente": "12345678",  # CI del cliente (obligatorio)
       "nombre": "Juan Perez"    # Nombre del cliente (opcional, se usa si el cliente no está registrado)
   }
   ```

   **Respuestas**:
   - `201 Created`: Si el consumo fue creado exitosamente.
   - `400 Bad Request`: Si el campo `ciCliente` no es proporcionado o hay un error en la creación del cliente.
   - `404 Not Found`: Si la mesa no existe.

---

### 2. **Obtener el Consumo Actual de una Mesa**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}`
   
   **Método**: `GET`
   
   **Descripción**: Este endpoint recupera el consumo actual para una mesa específica que tenga un consumo abierto (estado 1).

   **Respuestas**:
   - `200 OK`: Si el consumo abierto es encontrado, se devuelve los detalles.
   - `404 Not Found`: Si no hay un consumo abierto para la mesa o si la mesa no existe.
   - `400 Bad Request`: Si el consumo ya está cerrado.

---