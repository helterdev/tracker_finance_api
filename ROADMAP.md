# Hoja de Ruta (Roadmap) — Finance Tracker API

Este documento detalla el estado actual del proyecto y la lista paso a paso de lo que se ha creado (`[x]`) y lo que falta por implementar (`[ ]`), siguiendo las directrices arquitectónicas de `.agent/rules.md`.

---

## Fase 0: Cimientos, Infraestructura y Modelos de Datos (Completado)

- [x] **Gestión de dependencias y entorno**: Configuración inicial con `uv` (`pyproject.toml`, `uv.lock`).
- [x] **Base de datos en contenedor**: Configuración de PostgreSQL 17 en `docker-compose.yml` con volumen persistente `postgres_data`.
- [x] **Configuración centralizada**: Validación de variables de entorno con `pydantic-settings` en `app/core/config.py`.
- [x] **Conexión a Base de Datos**: Motor SQLAlchemy 2.0 (`psycopg` v3), `DeclarativeBase` y dependencia `get_db` en `app/core/database.py`.
- [x] **Modelos ORM Declarativos (SQLAlchemy 2.0)**:
  - [x] `UUIDTimestampMixin` (`id` UUIDv4, `created_at` y `updated_at` en UTC) en `app/models/base.py`.
  - [x] Modelo `User` en `app/models/user.py`.
  - [x] Modelo `Account` con `Numeric(12, 2)` en `app/models/account.py`.
  - [x] Modelo `Category` y `CategoryType` (`INCOME`, `EXPENSE`) en `app/models/category.py`.
  - [x] Modelo `Transaction` y `TransactionType` (`INCOME`, `EXPENSE`, `TRANSFER`) en `app/models/transaction.py`.
- [x] **Migración inicial de base de datos**: Configuración de Alembic y versión inicial `d60f18e87aaa_create_initial_tables.py`.
- [x] **Servidor base y Healthcheck**: Instancia de FastAPI y endpoint `GET /health` en `app/main.py`.

---

## Paso 1: Seguridad, Hashing y Autenticación JWT

Garantizar que cada petición esté autenticada y preparada para el aislamiento multi-inquilino (`WHERE model.user_id == current_user.id`).

- [x] **1.1. Instalar dependencias de seguridad con `uv`**:
  - [x] Añadir `pyjwt`, `pwdlib[argon2]` (o `bcrypt`), `python-multipart` y `pydantic[email]`.
- [x] **1.2. Utilidades criptográficas y JWT (`app/core/security.py`)**:
  - [x] Implementar `get_password_hash(password: str) -> str`.
  - [x] Implementar `verify_password(plain_password: str, hashed_password: str) -> bool`.
  - [x] Implementar `create_access_token(subject: str | UUID) -> str` y decodificación de token.
- [x] **1.3. Esquemas Pydantic v2 de Autenticación y Usuario**:
  - [x] Crear `app/schemas/token.py` (`Token`, `TokenPayload`).
  - [x] Crear `app/schemas/user.py` (`UserBase`, `UserCreate`, `UserUpdate`, `UserResponse` con `from_attributes=True`).
- [ ] **1.4. Servicio de Autenticación y Usuarios (`app/services/auth_service.py`)**:
  - [ ] Lógica de registro de usuario (verificar email único, hashear contraseña).
  - [ ] Lógica de autenticación (validar credenciales y estado `is_active`).
- [ ] **1.5. Dependencia de Usuario Actual (`app/api/deps.py`)**:
  - [ ] Implementar `get_current_user` con `OAuth2PasswordBearer` que valide el JWT y retorne la entidad `User`.
- [ ] **1.6. Endpoints de Autenticación (`app/api/v1/auth.py`)**:
  - [ ] `POST /api/v1/auth/register` — Registro de nuevos usuarios.
  - [ ] `POST /api/v1/auth/login` — Inicio de sesión y entrega de Access Token JWT.
  - [ ] `GET /api/v1/auth/me` — Obtener datos del usuario autenticado.

---

## Paso 2: Módulo de Cuentas Financieras (`Accounts`)

Gestión de cuentas del usuario (Banco, Efectivo, Ahorros, etc.) asegurando aislamiento por `user_id`.

- [ ] **2.1. Esquemas de Cuenta (`app/schemas/account.py`)**:
  - [ ] `AccountBase`, `AccountCreate` (con saldo inicial `Decimal`), `AccountUpdate` (nombre y moneda), `AccountResponse`.
- [ ] **2.2. Servicio de Cuentas (`app/services/account_service.py`)**:
  - [ ] Crear cuenta asociada a `current_user.id`.
  - [ ] Listar todas las cuentas del usuario autenticado.
  - [ ] Obtener detalle de una cuenta validando pertenencia (`404 Not Found` si no existe o no pertenece al usuario).
  - [ ] Actualizar nombre/moneda de la cuenta.
  - [ ] Eliminar cuenta del usuario.
- [ ] **2.3. Endpoints de Cuentas (`app/api/v1/accounts.py`)**:
  - [ ] `POST /api/v1/accounts`
  - [ ] `GET /api/v1/accounts`
  - [ ] `GET /api/v1/accounts/{account_id}`
  - [ ] `PATCH /api/v1/accounts/{account_id}`
  - [ ] `DELETE /api/v1/accounts/{account_id}`

---

## Paso 3: Módulo de Categorías (`Categories`)

Clasificación personalizada de ingresos (`INCOME`) y gastos (`EXPENSE`) por usuario.

- [ ] **3.1. Esquemas de Categoría (`app/schemas/category.py`)**:
  - [ ] `CategoryBase`, `CategoryCreate`, `CategoryUpdate`, `CategoryResponse`.
- [ ] **3.2. Servicio de Categorías (`app/services/category_service.py`)**:
  - [ ] Crear categoría validando que no exista duplicada (mismo nombre y tipo para el mismo usuario).
  - [ ] Listar categorías del usuario (con filtro opcional por `type: CategoryType`).
  - [ ] Obtener, actualizar y eliminar categoría validando `user_id`.
- [ ] **3.3. Endpoints de Categorías (`app/api/v1/categories.py`)**:
  - [ ] `POST /api/v1/categories`
  - [ ] `GET /api/v1/categories`
  - [ ] `GET /api/v1/categories/{category_id}`
  - [ ] `PATCH /api/v1/categories/{category_id}`
  - [ ] `DELETE /api/v1/categories/{category_id}`

---

## Paso 4: Motor de Transacciones y Consistencia ACID (`Transactions`)

Núcleo financiero donde cada movimiento impacta de forma atómica el `balance` de las cuentas involucradas.

- [ ] **4.1. Soporte de Transferencias entre Cuentas (Modelo + Migración)**:
  - [ ] Añadir `destination_account_id` (nullable `UUID`, FK a `accounts.id`) en `app/models/transaction.py` (o definir estrategia de doble asiento) y generar migración con Alembic.
- [ ] **4.2. Esquemas de Transacción (`app/schemas/transaction.py`)**:
  - [ ] `TransactionBase`, `TransactionCreate` (validando `amount > 0`), `TransactionUpdate`, `TransactionResponse`.
  - [ ] Esquema/parámetros de filtrado (`account_id`, `category_id`, `type`, `date_from`, `date_to`, `limit`, `offset`).
- [ ] **4.3. Servicio de Transacciones con Atomicidad (`app/services/transaction_service.py`)**:
  - [ ] Bloqueo pesimista (`with_for_update()`) de las cuentas afectadas dentro de una transacción atómica.
  - [ ] **Ingreso (`INCOME`)**: Sumar `amount` al `balance` de la cuenta y validar que la categoría (si se envía) sea `INCOME`.
  - [ ] **Gasto (`EXPENSE`)**: Restar `amount` al `balance` de la cuenta y validar que la categoría (si se envía) sea `EXPENSE`.
  - [ ] **Transferencia (`TRANSFER`)**: Descontar `amount` de la cuenta origen y acreditar `amount` en la cuenta destino dentro del mismo bloque atómico.
  - [ ] **Actualización y Eliminación**: Revertir el impacto previo en el `balance` de la cuenta y aplicar el nuevo monto/tipo de forma atómica.
- [ ] **4.4. Endpoints de Transacciones (`app/api/v1/transactions.py`)**:
  - [ ] `POST /api/v1/transactions`
  - [ ] `GET /api/v1/transactions`
  - [ ] `GET /api/v1/transactions/{transaction_id}`
  - [ ] `PATCH /api/v1/transactions/{transaction_id}`
  - [ ] `DELETE /api/v1/transactions/{transaction_id}`

---

## Paso 5: Reportes, Balances y Analítica (`Reports`)

Consultas agregadas para alimentar dashboards y resúmenes financieros.

- [ ] **5.1. Esquemas de Reportes (`app/schemas/report.py`)**:
  - [ ] `FinancialSummaryResponse` (`total_balance`, `total_income`, `total_expense`, `net_cashflow`).
  - [ ] `CategoryBreakdownItem` (`category_id`, `category_name`, `type`, `total_amount`, `percentage`).
- [ ] **5.2. Servicio de Reportes (`app/services/report_service.py`)**:
  - [ ] Agregaciones SQL (`func.sum`, `GROUP BY`) filtradas por `user_id` y rango de fechas (`date_from`, `date_to`).
- [ ] **5.3. Endpoints de Reportes (`app/api/v1/reports.py`)**:
  - [ ] `GET /api/v1/reports/summary`
  - [ ] `GET /api/v1/reports/by-category`

---

## Paso 6: Integración de Rutas, Middleware y Documentación (`app/main.py`)

- [ ] **6.1. Enrutador central v1 (`app/api/v1/router.py`)**:
  - [ ] Agrupar `auth`, `accounts`, `categories`, `transactions` y `reports` bajo `/api/v1`.
- [ ] **6.2. Configurar `app/main.py`**:
  - [ ] Incluir el router `/api/v1`.
  - [ ] Configurar `CORSMiddleware`.
- [ ] **6.3. Documentar `README.md`**:
  - [ ] Instrucciones de levantamiento con Docker, migraciones con Alembic y ejecución con `uv run uvicorn`.

---

## Paso 7: Suite de Pruebas Automatizadas (`tests/`)

- [ ] **7.1. Configuración de `pytest` (`tests/conftest.py`)**:
  - [ ] Añadir `httpx` para `TestClient` y configurar base de datos/transacciones de prueba aisladas.
- [ ] **7.2. Tests de Autenticación (`tests/test_auth.py`)**:
  - [ ] Registro exitoso, email duplicado (`400`), login válido y rutas protegidas (`401`).
- [ ] **7.3. Tests de Aislamiento Multi-inquilino (`tests/test_isolation.py`)**:
  - [ ] Verificar que el Usuario A nunca pueda leer, editar ni borrar cuentas, categorías o transacciones del Usuario B.
- [ ] **7.4. Tests de Integridad Financiera ACID (`tests/test_transactions.py`)**:
  - [ ] Verificar exactitud decimal (`Decimal`) del `balance` tras crear, editar y eliminar ingresos, gastos y transferencias.
