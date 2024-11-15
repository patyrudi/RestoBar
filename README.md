# RestoBar
Este proyecto es una API para gestionar consumos en un restaurante, permitiendo registrar productos, cambiar clientes, agregar detalles de consumo y cerrar un consumo generando un ticket en formato PDF.

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
3.  **MakeMigrations**:
    ```bash
    python manage.py makemigrations
    ```
    
4. **Migrations**:
    Asegúrate de tener las migraciones aplicadas para que la base de datos esté lista:
    ```bash
    python manage.py migrate
    ```

5. **Inicia el servidor**:
    ```bash
    python manage.py runserver
    ```

La API estará disponible en `http://127.0.0.1:8000/restaurante/api/v1/`

## Endpoints

### 1. **Abrir un Consumo para una Mesa**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/crear/`
   
   **Método**: `POST`
   
   **Descripción**: Este endpoint abre un consumo en una mesa específica. Si ya hay un consumo abierto en la mesa (estado 1), la solicitud será rechazada.
   
   **Cuerpo de la solicitud (JSON)**:
   ```json
   {
       "ciCliente": "1234567", 
       "nombre": "Juan Perez"    
   }
   ```

   **Respuestas**:
   - `201 Created`: Si el consumo fue creado exitosamente.
   - `400 Bad Request`: Si el campo `ciCliente` no es proporcionado o hay un error en la creación del cliente.
   - `404 Not Found`: Si la mesa no existe.

---

### 2. **Obtener el Consumo Actual de una Mesa**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/`
   
   **Método**: `GET`
   
   **Descripción**: Este endpoint recupera el consumo actual para una mesa específica que tenga un consumo abierto (estado 1).

   **Respuestas**:
   - `200 OK`: Si el consumo abierto es encontrado, se devuelve los detalles.
   - `404 Not Found`: Si no hay un consumo abierto para la mesa o si la mesa no existe.
   - `400 Bad Request`: Si el consumo ya está cerrado.

---
### 3. **Cambiar el Cliente Asociado a un Consumo Abierto**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/cambiar-cliente/`
   
   **Método**: `POST`
   
   **Descripción**: Este endpoint permite cambiar el cliente asociado a un consumo abierto para una mesa específica.
   
   **Cuerpo de la solicitud (JSON)**:
   ```json
   {
       "ciCliente": "8765432",  
       "nombre": "Ana Gomez"     
   }
   ```

   **Respuestas**:
   - `200 OK`: Si el cliente se actualizó exitosamente.
   - `404 Not Found`: Si no hay consumo abierto o si la mesa no existe.
   - `400 Bad Request`: Si el campo `ciCliente` no es proporcionado o si ocurre un error con el cliente.

---

### 4. **Agregar un Detalle al Consumo Actual**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/agregar-detalle/`
   
   **Método**: `POST`
   
   **Descripción**: Este endpoint agrega un nuevo detalle de consumo a un consumo abierto para una mesa específica.

   **Cuerpo de la solicitud (JSON)**:
   ```json
   {
       "idproducto": 1,  
       "cantidad": 2     
   }
   ```

   **Respuestas**:
   - `201 Created`: Si el detalle fue agregado exitosamente.
   - `404 Not Found`: Si el producto no existe o si no hay un consumo abierto en la mesa.
   - `400 Bad Request`: Si la cantidad no es válida.

---

### 5. **Cerrar el Consumo Actual y Generar Ticket PDF**
   
   **URL**: `/restaurante/api/v1/consumos/mesa/{idmesa}/cerrar/`
   
   **Método**: `POST`
   
   **Descripción**: Este endpoint cierra el consumo actual para una mesa específica y genera un ticket en formato PDF con los detalles del consumo.

   **Cuerpo de la solicitud (JSON)**: No es necesario enviar un cuerpo JSON para cerrar el ticker.

   **Respuestas**:
   - `200 OK`: Si el consumo fue cerrado correctamente y se generó el ticket PDF.
   - `404 Not Found`: Si no hay consumo abierto para la mesa.
   - `400 Bad Request`: Si el consumo ya está cerrado.

---
