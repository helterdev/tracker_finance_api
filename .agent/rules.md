# Directrices de Ingeniería: Finance Tracker API (FastAPI + PostgreSQL)

## 1. Filosofía Arquitectónica y Separación de Capas
- **Arquitectura en capas estricta:**
  - `app/api/v1/`: Rutas, deserialización y serialización HTTP. Cero lógica de negocio o queries complejas aquí.
  - `app/services/`: Lógica de dominio, cálculos de balances, orquestación de transacciones y reglas de negocio.
  - `app/models/`: Entidades declarativas de SQLAlchemy 2.0 (representación de tablas en BD).
  - `app/schemas/`: Esquemas de validación y DTOs con Pydantic v2.
  - `app/core/`: Configuración (`pydantic-settings`), conexión de base de datos, seguridad criptográfica y middleware.
- **Inyección de dependencias:** Utilizar `Depends()` de FastAPI para inyectar sesiones de base de datos (`Session` / `AsyncSession`) y autenticación de usuario (`current_user`).

## 2. Modelado de Datos y Reglas de Base de Datos
- **Manejo monetario:**
  - NUNCA usar `Float` ni `Real` para saldos o importes de dinero.
  - Usar siempre `Numeric(precision=12, scale=2)` en SQLAlchemy o almacenar en centavos enteros (`BigInteger`).
- **Identificadores y Tiempos:**
  - Claves primarias: `UUIDv4` para prevenir ataques de enumeración (IDOR) desde el frontend.
  - Timestamps: Todos los campos temporales (`created_at`, `updated_at`, `transaction_date`) deben ser `DateTime(timezone=True)` almacenados en UTC.
- **Integridad y ACID:**
  - Toda transferencia o movimiento entre cuentas debe envolverse en un bloque `db.begin()` / transacción atómica explícita.
  - Índices obligatorios en campos de filtrado recurrente: `user_id`, `created_at`, `category_id`.
  - Aislamiento multi-inquilino obligatorio: Cada consulta debe validar explícitamente `WHERE model.user_id == current_user.id`.

## 3. Estándares de Código y Tipado (Python / FastAPI)
- **Tipado estricto:** Usar type hints completos en todos los parámetros y retornos (`typing` nativo de Python 3.10+: `list[T]`, `T | None`).
- **SQLAlchemy 2.0:** Usar exclusivamente sintaxis declarativa moderna `mapped_column` y `Mapped[T]`. No utilizar sintaxis legada de SQLAlchemy 1.4 (`Column(...)`).
- **Pydantic v2:**
  - Separar esquemas por operación: `[Entity]Base`, `[Entity]Create`, `[Entity]Update`, `[Entity]Response`.
  - Usar `model_config = ConfigDict(from_attributes=True)` para serializar modelos ORM.
- **Manejo de Excepciones:** No devolver códigos de estado genéricos (500) para errores de cliente. Lanzar `HTTPException` con códigos semánticos (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`).

## 4. Gestión de Dependencias
- Usar únicamente `uv` para instalar o remover dependencias (`uv add`, `uv remove`).
- Mantener `pyproject.toml` y `uv.lock` sincronizados y versionados.

## 5. Infraestructura y Entorno Local (Docker)
- **Base de datos en contenedor:** PostgreSQL debe ejecutarse exclusivamente mediante Docker (`docker compose`) para aislar los datos y evitar instalaciones o escrituras directas en el sistema operativo anfitrión.
- **Persistencia controlada:** Utilizar volúmenes nombrados de Docker (`postgres_data`) gestionados por `docker-compose.yml` y variables de entorno desde `.env`.