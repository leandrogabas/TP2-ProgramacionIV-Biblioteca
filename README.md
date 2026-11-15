# TP2: Sistema de Biblioteca (FastAPI + SQLModel)

API RESTful construida con **FastAPI** y **SQLModel** para la gestión del catálogo de una biblioteca, sus socios y el circuito transaccional de préstamos y devoluciones. Desarrollado para **Programación IV (TUP - UTN)**.

## Arquitectura del Proyecto

El proyecto implementa una arquitectura en capas con separación estricta de responsabilidades e Inyección de Dependencias (`Depends`):

- **`database.py`**: Configuración del `engine` SQLite, creación de tablas y generador de sesión (`get_session`).
- **`main.py`**: Punto de entrada de la aplicación FastAPI, ciclo de vida (`lifespan`) y registro de routers.
- **`models/`**: Modelos de datos SQLModel (entidades ORM de base de datos y esquemas DTO de entrada/salida).
  - `models/__init__.py`
  - `models/autor.py`: Modelo `Autor` y tabla intermedia `LibroAutor` (relación N-N).
  - `models/libro.py`: Modelo `Libro` y esquema `LibroRead` con autores anidados.
  - `models/socio.py`: Modelo `Socio` con validación de email único.
  - `models/prestamo.py`: Modelo `Prestamo` con control de fechas de vencimiento, devolución y multas.
- **`routers/`**: Capa de presentación y controladores HTTP (sin lógica de negocio).
  - `routers/__init__.py`
  - `routers/autores.py`: Endpoints CRUD para `/autores`.
  - `routers/libros.py`: Endpoints CRUD para `/libros`, asociación N-N (`/libros/{id}/autores/{autor_id}`) y filtro `?disponibles=true`.
  - `routers/socios.py`: Endpoints CRUD para `/socios` y consulta de préstamos por socio (`/socios/{id}/prestamos?activos=true`).
  - `routers/prestamos.py`: Endpoints transaccionales para registrar préstamos (`/prestamos`) y devoluciones (`/prestamos/{id}/devolucion`).
- **`services/`**: Capa de lógica de negocio, validaciones de dominio y transacciones atómicas.
  - `services/__init__.py`
  - `services/autores.py`: Servicio `AutorService`.
  - `services/libros.py`: Servicio `LibroService` (unicidad de ISBN, filtro de stock y asociación de autores).
  - `services/socios.py`: Servicio `SocioService` (unicidad de email y gestión de socios).
  - `services/prestamos.py`: Servicio `PrestamoService` (reglas de préstamos activos, control de stock, plazos de 14 días y cálculo de multas).
- **`tests/`**: Suite de pruebas de integración con Pytest y SQLite en memoria (`StaticPool`).
  - `tests/__init__.py`
  - `tests/conftest.py`: Fixtures de base de datos aislada en memoria (`session`) y cliente de pruebas (`client`).
  - `tests/test_biblioteca.py`: Casos de prueba de éxito y error para todas las reglas de negocio.
- **`pyproject.toml`** y **`requirements.txt`**: Configuración de herramientas y dependencias del proyecto.

## Requisitos e Instalación

1. Clonar el repositorio y ubicarse en el directorio del proyecto:

```bash
git clone https://github.com/ffumaneri/utn-tup-2026-python.git
cd TP2-Prog-IV-biblioteca
```

2. Crear y activar un entorno virtual:

```bash
python -m venv .venv
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución de la API

Para iniciar el servidor de desarrollo con recarga automática:

```bash
uvicorn main:app --reload
```

- **Documentación interactiva (Swagger UI):** `http://127.0.0.1:8000/docs`
- **Documentación alternativa (ReDoc):** `http://127.0.0.1:8000/redoc`

## Ejecución de Pruebas y Cobertura (Testing)

La suite de pruebas utiliza una base de datos SQLite en memoria aislada por cada función de test (`sqlite://` + `StaticPool`), sin afectar el archivo `biblioteca.db` local.

Para correr los tests:

```bash
pytest -v
```

Para ejecutar los tests midiendo el porcentaje de cobertura de código (requisito >= 80%):

```bash
pytest --cov=. --cov-report=term-missing
```

## Endpoints Principales y Reglas de Negocio

| Método | Ruta | Descripción | Códigos HTTP |
|---|---|---|---|
| `CRUD` | `/autores`, `/libros`, `/socios` | Alta, baja, modificación (`PUT`/`PATCH`) y consulta | `200`, `201`, `404`, `409` |
| `POST` | `/libros/{id}/autores/{autor_id}` | Asocia un autor existente a un libro (relación N-N) | `200`, `404`, `409` |
| `GET` | `/libros?disponibles=true` | Lista únicamente los libros con `stock > 0` | `200` |
| `POST` | `/prestamos` | Registra un préstamo (descuenta 1 stock, vence en 14 días) | `201`, `403`, `404`, `409` |
| `POST` | `/prestamos/{id}/devolucion` | Registra devolución, repone stock y calcula multa (100 por día de atraso) | `200`, `404`, `409` |
| `GET` | `/socios/{id}/prestamos?activos=true` | Lista los préstamos activos (`fecha_devolucion == null`) del socio | `200`, `404` |
