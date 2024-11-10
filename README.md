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