# PLAN DE EJECUCIÓN: CHESS COACH AGENTIC → PRODUCCIÓN

**Rol:** Tech Lead & Arquitecto  
**Fecha de inicio:** 12 de febrero de 2026  
**Duración estimada:** 8 semanas (2 meses)  
**Objetivo:** Transformar MVP en producto production-ready completamente funcional

---

## ÍNDICE

1. [Visión y Objetivos](#1-visión-y-objetivos)
2. [Estructura del Equipo](#2-estructura-del-equipo)
3. [Arquitectura Objetivo](#3-arquitectura-objetivo)
4. [Sprints Detallados](#4-sprints-detallados)
5. [Backlog Priorizado](#5-backlog-priorizado)
6. [Especificaciones Técnicas](#6-especificaciones-técnicas)
7. [Plan de Testing](#7-plan-de-testing)
8. [Plan de Deploy](#8-plan-de-deploy)
9. [Gestión de Riesgos](#9-gestión-de-riesgos)
10. [KPIs y Métricas](#10-kpis-y-métricas)

---

## 1. VISIÓN Y OBJETIVOS

### 1.1 Definición de "Completamente Funcional"

Un sistema que cumple:

✅ **Funcional**
- Todas las features críticas operativas
- UX fluida sin bloqueos
- Performance aceptable (<3s tiempo respuesta)

✅ **Confiable**
- 99% uptime
- Tests automatizados (>80% coverage)
- Error handling robusto

✅ **Seguro**
- Autenticación obligatoria
- Datos encriptados
- Rate limiting

✅ **Escalable**
- Soporta 100+ usuarios concurrentes
- Procesamiento asíncrono
- Caché distribuida

✅ **Mantenible**
- Código refactorizado (SRP, DRY)
- CI/CD automatizado
- Documentación completa

✅ **Deployable**
- Containerizado (Docker)
- Monitoreo en tiempo real
- Backup automático

### 1.2 Objetivos SMART

| Objetivo | Métrica | Target | Deadline |
|----------|---------|--------|----------|
| **Lanzamiento Beta** | Sistema en staging | 100% features core | Semana 6 |
| **Test Coverage** | % código testeado | >80% backend, >60% frontend | Semana 5 |
| **Performance** | Tiempo bootstrap | <5 min (async) | Semana 3 |
| **Uptime** | Disponibilidad | >99% | Desde semana 6 |
| **Usuarios Beta** | Testers activos | 50 usuarios | Semana 8 |

### 1.3 Criterios de Éxito

**Must Have (P0 - Bloqueantes):**
- [x] Autenticación funcional
- [x] Bootstrap asíncrono
- [x] Tests automatizados
- [x] Deploy en staging
- [x] Monitoreo básico

**Should Have (P1 - Importantes):**
- [x] Repaso espaciado
- [x] Progreso histórico
- [x] Chat con LLM mejorado
- [x] Notificaciones

**Nice to Have (P2 - Deseables):**
- [ ] Mobile app
- [ ] Social features
- [ ] Marketplace coaches

---

## 2. ESTRUCTURA DEL EQUIPO

### 2.1 Roles y Responsabilidades

**Tech Lead (1)** - Tú
- Arquitectura y decisiones técnicas
- Code reviews críticos
- Coordinación sprints
- Mentoring equipo

**Backend Developer Senior (1)**
- Refactoring repositorio
- Implementación autenticación
- Optimización Stockfish
- Tests backend

**Backend Developer Mid (1)**
- Async processing (Celery)
- Endpoints nuevos
- Migraciones DB
- Integración LLM

**Frontend Developer Senior (1)**
- Refactoring componentes
- State management (Zustand/Redux)
- UI/UX improvements
- Tests frontend (Playwright)

**DevOps Engineer (1)**
- Docker setup
- CI/CD pipelines
- Monitoring (Prometheus + Grafana)
- Deploy automation

**QA Engineer (1)**
- Test planning
- Manual testing
- Bug tracking
- User acceptance testing

### 2.2 Ceremonias Ágiles

**Daily Standup:** 9:00 AM (15 min)
- ¿Qué hice ayer?
- ¿Qué haré hoy?
- ¿Bloqueos?

**Sprint Planning:** Lunes inicio sprint (2h)
- Review backlog
- Estimaciones (planning poker)
- Asignación tareas

**Sprint Review:** Viernes final sprint (1h)
- Demo features
- Feedback stakeholders
- Update roadmap

**Retrospective:** Viernes final sprint (1h)
- Start/Stop/Continue
- Action items

**Tech Sync:** Miércoles (1h)
- Decisiones arquitectónicas
- POCs review
- Pair programming sessions

### 2.3 Herramientas

| Categoría | Tool | Uso |
|-----------|------|-----|
| **Project Management** | Linear / Jira | Tracking tareas |
| **Code Repository** | GitHub | Source control |
| **CI/CD** | GitHub Actions | Pipelines |
| **Communication** | Slack | Chat equipo |
| **Docs** | Notion | Documentación |
| **Monitoring** | Grafana + Sentry | Observability |

---

## 3. ARQUITECTURA OBJETIVO

### 3.1 Diagrama de Arquitectura Final

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (Web/Mobile)                      │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 NGINX (Reverse Proxy + SSL)                  │
│                    Rate Limiting + CORS                      │
└────────┬────────────────────────────────┬───────────────────┘
         │                                │
         ▼                                ▼
┌─────────────────────┐        ┌─────────────────────┐
│   Next.js Frontend  │        │  FastAPI Backend    │
│   (Static + SSR)    │        │  (API + WebSockets) │
│                     │        │                     │
│  - Auth (JWT)       │        │  - Auth Middleware  │
│  - State Mgmt       │        │  - Async Tasks      │
│  - Real-time UI     │        │  - REST + WS        │
└─────────────────────┘        └──────────┬──────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │  PostgreSQL DB   │  │  Redis Cache     │  │  Celery Workers  │
         │                  │  │                  │  │                  │
         │  - Users         │  │  - Sessions      │  │  - Bootstrap     │
         │  - Games         │  │  - Evals cache   │  │  - Stockfish     │
         │  - Puzzles       │  │  - Task queue    │  │  - LLM calls     │
         │  - Stats         │  │                  │  │                  │
         └──────────────────┘  └──────────────────┘  └────────┬─────────┘
                                                               │
                                                               ▼
                                                    ┌──────────────────┐
                                                    │  Stockfish Pool  │
                                                    │  (3 processes)   │
                                                    └──────────────────┘

         ┌──────────────────────────────────────────────────────────┐
         │              MONITORING & OBSERVABILITY                  │
         │                                                          │
         │  Prometheus (metrics) → Grafana (dashboards)            │
         │  Sentry (errors) → Alerts (email/Slack)                 │
         │  Logs (JSON) → Loki → Query interface                   │
         └──────────────────────────────────────────────────────────┘
```

### 3.2 Cambios Arquitectónicos Principales

#### 3.2.1 Base de Datos: SQLite → PostgreSQL

**Razón:** Multi-tenant, concurrencia, backups automáticos

**Plan de migración:**
```python
# Paso 1: Crear schema Postgres
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE games (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    platform VARCHAR(20) NOT NULL,
    game_id VARCHAR(100) NOT NULL,
    played_at TIMESTAMP NOT NULL,
    pgn TEXT NOT NULL,
    -- ... resto campos
    UNIQUE(user_id, platform, game_id)
);

CREATE TABLE puzzles (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    game_id BIGINT REFERENCES games(id),
    fen_before TEXT NOT NULL,
    pv_uci TEXT[],  -- Array nativo Postgres
    tags TEXT[],
    swing_cp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_games_user_played ON games(user_id, played_at DESC);
CREATE INDEX idx_puzzles_user_created ON puzzles(user_id, created_at DESC);
CREATE INDEX idx_puzzles_tags ON puzzles USING GIN(tags);  -- Full-text search
```

**Script de migración:**
```python
# scripts/migrate_sqlite_to_postgres.py
import sqlite3
import asyncpg
from tqdm import tqdm

async def migrate():
    sqlite_conn = sqlite3.connect('chess_coach.db')
    pg_conn = await asyncpg.connect('postgresql://user:pass@localhost/chess_coach')
    
    # Migrar juegos
    games = sqlite_conn.execute("SELECT * FROM games").fetchall()
    for game in tqdm(games, desc="Migrando games"):
        await pg_conn.execute(
            "INSERT INTO games (...) VALUES (...)",
            *game
        )
    
    # Similar para puzzles, stats, etc.
    await pg_conn.close()
```

#### 3.2.2 Procesamiento Asíncrono: Celery + Redis

**Arquitectura:**
```python
# chess_coach/workers/tasks.py
from celery import Celery
import os

celery_app = Celery(
    'chess_coach',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True)
def bootstrap_user(self, user_id: str, platform: str, games_limit: int):
    """Bootstrap asíncrono con progreso reportado."""
    from chess_coach.infrastructure.lichess_client import LichessClient
    from chess_coach.infrastructure.stockfish_engine import StockfishEngine
    from chess_coach.application.blunder_mining import find_blunders
    
    # Update progress
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Importando partidas...'})
    
    # Import games
    client = LichessClient()
    games = client.fetch_games(username, limit=games_limit)
    save_games_to_db(user_id, games)
    
    self.update_state(state='PROGRESS', meta={'current': 30, 'total': 100, 'status': 'Analizando con Stockfish...'})
    
    # Analyze blunders
    engine = get_stockfish_from_pool()
    blunders = find_blunders(games, engine, max_blunders=50)
    save_puzzles_to_db(user_id, blunders)
    
    self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Etiquetando puzzles...'})
    
    # Tag puzzles
    tag_puzzles(user_id)
    
    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completado'})
    
    return {'games': len(games), 'puzzles': len(blunders)}

@celery_app.task
def analyze_game_deep(user_id: str, game_id: int):
    """Análisis profundo de una partida específica."""
    # Depth 20, más lento pero más preciso
    pass

@celery_app.task
def generate_daily_plan(user_id: str):
    """Genera plan diario (puede ejecutarse como cron)."""
    pass
```

**Endpoint API con progreso:**
```python
# chess_coach/api/routers/coach.py
from chess_coach.workers.tasks import bootstrap_user

@router.post("/coach/bootstrap-async")
async def bootstrap_async(req: BootstrapRequest, current_user: User = Depends(get_current_user)):
    """Inicia bootstrap asíncrono y retorna task_id."""
    task = bootstrap_user.delay(
        user_id=str(current_user.id),
        platform=req.platform,
        games_limit=req.import_games
    )
    
    return {
        "task_id": task.id,
        "status": "PENDING",
        "message": "Bootstrap iniciado. Usa /bootstrap-status para ver progreso."
    }

@router.get("/coach/bootstrap-status/{task_id}")
async def bootstrap_status(task_id: str):
    """Consulta estado de tarea asíncrona."""
    from chess_coach.workers.tasks import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {'state': task.state, 'current': 0, 'total': 100, 'status': 'En cola...'}
    elif task.state == 'PROGRESS':
        response = {'state': task.state, **task.info}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'current': 100, 'total': 100, 'result': task.result}
    else:  # FAILURE
        response = {'state': task.state, 'error': str(task.info)}
    
    return response
```

**Frontend con polling:**
```typescript
// app/session/page.tsx
async function bootstrapAsync() {
    const res = await apiPost<{task_id: string}>("/coach/bootstrap-async", {...})
    const taskId = res.task_id
    
    // Poll status cada 2 segundos
    const interval = setInterval(async () => {
        const status = await apiGet<{state: string, current: number, total: number}>(`/coach/bootstrap-status/${taskId}`)
        
        setProgress(status.current / status.total * 100)
        setStatusMessage(status.status)
        
        if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
            clearInterval(interval)
            if (status.state === 'SUCCESS') {
                loadPuzzles()
            }
        }
    }, 2000)
}
```

#### 3.2.3 Autenticación: OAuth2 + JWT

**Stack:**
- `python-jose` para JWT
- `passlib[bcrypt]` para password hashing
- `python-multipart` para form data

**Implementación:**
```python
# chess_coach/infrastructure/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@router.post("/auth/register")
async def register(username: str, email: str, password: str):
    # Validar email único
    if await user_exists(email):
        raise HTTPException(400, "Email already registered")
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password)
    )
    await save_user(user)
    
    return {"message": "User created successfully"}

@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email
    }
```

**Frontend (Next.js):**
```typescript
// src/lib/auth/client.ts
export async function login(username: string, password: string) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const res = await fetch(`${BASE}/auth/login`, {
        method: 'POST',
        body: formData
    })
    
    if (!res.ok) throw new Error('Login failed')
    
    const data = await res.json()
    localStorage.setItem('access_token', data.access_token)
    return data
}

export function getToken(): string | null {
    return localStorage.getItem('access_token')
}

export async function apiAuthGet<T>(path: string): Promise<T> {
    const token = getToken()
    if (!token) throw new Error('Not authenticated')
    
    const res = await fetch(`${BASE}${path}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    
    if (res.status === 401) {
        localStorage.removeItem('access_token')
        window.location.href = '/login'
        throw new Error('Unauthorized')
    }
    
    return res.json()
}
```

#### 3.2.4 Caché Distribuida: Redis

**Casos de uso:**
1. **Session storage** (JWT blacklist, rate limiting)
2. **Evaluaciones Stockfish** (caché por FEN)
3. **Planes generados** (caché 1 hora)
4. **Task queue** (Celery broker)

**Implementación:**
```python
# chess_coach/infrastructure/cache.py
import redis
import json
from typing import Optional, Any

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self.client = redis.from_url(url, decode_responses=True)
    
    def get_eval(self, fen: str, depth: int) -> Optional[dict]:
        key = f"eval:{fen}:{depth}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def set_eval(self, fen: str, depth: int, eval_data: dict, ttl: int = 86400):
        """TTL = 24 horas"""
        key = f"eval:{fen}:{depth}"
        self.client.setex(key, ttl, json.dumps(eval_data))
    
    def get_plan(self, user_id: str, date: str) -> Optional[dict]:
        key = f"plan:{user_id}:{date}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def set_plan(self, user_id: str, date: str, plan: dict, ttl: int = 3600):
        """TTL = 1 hora"""
        key = f"plan:{user_id}:{date}"
        self.client.setex(key, ttl, json.dumps(plan))

# Uso en StockfishEngine
class CachedStockfishEngine(StockfishEngine):
    def __init__(self, *args, cache: RedisCache = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = cache
    
    def analyze(self, board: chess.Board) -> Eval:
        fen = board.fen()
        
        # Check cache
        if self.cache:
            cached = self.cache.get_eval(fen, self.depth)
            if cached:
                return Eval(**cached)
        
        # Compute
        result = super().analyze(board)
        
        # Save to cache
        if self.cache:
            self.cache.set_eval(fen, self.depth, asdict(result))
        
        return result
```

#### 3.2.5 Monitoreo: Prometheus + Grafana + Sentry

**Métricas a trackear:**
```python
# chess_coach/infrastructure/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Counters
bootstrap_requests = Counter('bootstrap_requests_total', 'Total bootstrap requests')
puzzle_attempts = Counter('puzzle_attempts_total', 'Total puzzle attempts', ['correct'])
api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])

# Histograms
stockfish_duration = Histogram('stockfish_analyze_duration_seconds', 'Time to analyze position')
bootstrap_duration = Histogram('bootstrap_duration_seconds', 'Time to complete bootstrap')

# Gauges
active_users = Gauge('active_users', 'Number of active users in last 5 minutes')
stockfish_pool_size = Gauge('stockfish_pool_size', 'Number of available Stockfish processes')

# Middleware FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        
        api_requests.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        return response

# En app.py
from prometheus_client import make_asgi_app

app.add_middleware(MetricsMiddleware)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Sentry para errores:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% de traces
    environment=os.getenv("ENV", "production")
)
```

---

## 4. SPRINTS DETALLADOS

### Sprint 0: Setup e Infraestructura (Semana 1)

**Objetivos:**
- Configurar entorno de desarrollo
- Definir estándares de código
- Setup CI/CD básico

**Tareas:**

#### Backend
- [ ] **BE-001:** Configurar pre-commit hooks (black, ruff, mypy)
  - Tiempo: 2h
  - Responsable: Backend Senior
  - Output: `.pre-commit-config.yaml`

- [ ] **BE-002:** Setup pytest + fixtures base
  - Tiempo: 4h
  - Responsable: Backend Senior
  - Output: `tests/conftest.py`, primeros 5 tests

- [ ] **BE-003:** Configurar GitHub Actions (lint + tests)
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: `.github/workflows/backend.yml`

- [ ] **BE-004:** Dockerizar backend (dev)
  - Tiempo: 4h
  - Responsable: DevOps
  - Output: `Dockerfile`, `docker-compose.dev.yml`

#### Frontend
- [ ] **FE-001:** Setup ESLint + Prettier
  - Tiempo: 2h
  - Responsable: Frontend Senior
  - Output: `.eslintrc.json`, `.prettierrc`

- [ ] **FE-002:** Configurar Playwright tests
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: `playwright.config.ts`, primeros 3 E2E tests

- [ ] **FE-003:** GitHub Actions (lint + build + tests)
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: `.github/workflows/frontend.yml`

#### Infraestructura
- [ ] **INFRA-001:** Setup PostgreSQL (local Docker)
  - Tiempo: 2h
  - Responsable: DevOps
  - Output: `docker-compose.yml` con Postgres + pgAdmin

- [ ] **INFRA-002:** Setup Redis (local Docker)
  - Tiempo: 1h
  - Responsable: DevOps
  - Output: Redis en docker-compose

- [ ] **INFRA-003:** Migración SQLite → Postgres (script)
  - Tiempo: 6h
  - Responsable: Backend Mid
  - Output: `scripts/migrate_db.py`

**Definition of Done:**
- CI/CD ejecutándose en cada PR
- Tests pasando (aunque coverage bajo)
- Entorno local replicable con docker-compose
- Migración DB validada con datos de prueba

---

### Sprint 1: Autenticación y Seguridad (Semana 2)

**Objetivos:**
- Implementar autenticación completa
- Proteger todos los endpoints
- Frontend con login/register

**Tareas:**

#### Backend
- [ ] **BE-101:** Crear modelo User (Postgres)
  - Tiempo: 3h
  - Responsable: Backend Senior
  - Output: `domain/user.py`, migration SQL
  - Criterio: Username, email, password_hash, created_at

- [ ] **BE-102:** Implementar password hashing (bcrypt)
  - Tiempo: 2h
  - Responsable: Backend Senior
  - Output: `infrastructure/auth.py` con hash/verify

- [ ] **BE-103:** JWT token generation/validation
  - Tiempo: 4h
  - Responsable: Backend Senior
  - Output: `create_access_token()`, `get_current_user()` middleware

- [ ] **BE-104:** Endpoints /auth/register, /auth/login, /auth/me
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `api/routers/auth.py`

- [ ] **BE-105:** Middleware autenticación global
  - Tiempo: 3h
  - Responsable: Backend Senior
  - Output: Dependency `current_user` en todos los endpoints

- [ ] **BE-106:** Tests autenticación (10+ tests)
  - Tiempo: 4h
  - Responsable: Backend Senior
  - Output: `tests/test_auth.py`

#### Frontend
- [ ] **FE-101:** Crear páginas login/register
  - Tiempo: 6h
  - Responsable: Frontend Senior
  - Output: `app/login/page.tsx`, `app/register/page.tsx`

- [ ] **FE-102:** Auth context (React Context API)
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: `src/contexts/AuthContext.tsx`

- [ ] **FE-103:** Protected routes (middleware Next.js)
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: `middleware.ts` redirige a /login si no autenticado

- [ ] **FE-104:** Actualizar API client con token
  - Tiempo: 2h
  - Responsable: Frontend Senior
  - Output: `apiAuthGet()`, `apiAuthPost()` incluyen Bearer token

- [ ] **FE-105:** UI componente User menu (avatar, logout)
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: `src/components/UserMenu.tsx`

#### Seguridad
- [ ] **SEC-101:** Rate limiting (Redis)
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: Middleware 100 req/min por IP

- [ ] **SEC-102:** CORS configuración estricta
  - Tiempo: 1h
  - Responsable: Backend Senior
  - Output: Whitelist dominios en producción

- [ ] **SEC-103:** Validación input (Pydantic)
  - Tiempo: 3h
  - Responsable: Backend Mid
  - Output: Field constraints en todos los schemas

**Definition of Done:**
- Usuario puede registrarse y logearse
- Token JWT funciona en todas las requests
- Endpoints protegidos retornan 401 sin token
- Tests cubren casos happy path + errores
- Frontend redirige a login si 401

---

### Sprint 2: Procesamiento Asíncrono (Semana 3)

**Objetivos:**
- Bootstrap no bloquea request
- UI muestra progreso en tiempo real
- Stockfish pool para concurrencia

**Tareas:**

#### Backend
- [ ] **BE-201:** Setup Celery + Redis
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `workers/tasks.py`, `workers/__init__.py`

- [ ] **BE-202:** Task bootstrap_user asíncrono
  - Tiempo: 6h
  - Responsable: Backend Senior
  - Output: `bootstrap_user.delay()` con progreso

- [ ] **BE-203:** Endpoint /bootstrap-async
  - Tiempo: 3h
  - Responsable: Backend Mid
  - Output: Retorna task_id

- [ ] **BE-204:** Endpoint /bootstrap-status/{task_id}
  - Tiempo: 2h
  - Responsable: Backend Mid
  - Output: Retorna {state, current, total, status}

- [ ] **BE-205:** Stockfish process pool (3 workers)
  - Tiempo: 5h
  - Responsable: Backend Senior
  - Output: `infrastructure/stockfish_pool.py` con queue

- [ ] **BE-206:** Refactor blunder_mining para usar pool
  - Tiempo: 4h
  - Responsable: Backend Senior
  - Output: Parallelización análisis (3x más rápido)

- [ ] **BE-207:** Tests tareas Celery
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `tests/test_tasks.py` con mocks

#### Frontend
- [ ] **FE-201:** UI progress bar component
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: `src/components/ProgressBar.tsx`

- [ ] **FE-202:** Implementar polling /bootstrap-status
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: Hook `useTaskProgress(taskId)`

- [ ] **FE-203:** Refactor session page con async bootstrap
  - Tiempo: 5h
  - Responsable: Frontend Senior
  - Output: UX fluida sin bloqueos

- [ ] **FE-204:** Loading states (Suspense)
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: Skeletons en todas las páginas

#### Infraestructura
- [ ] **INFRA-201:** Docker Celery worker
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: `docker-compose.yml` con worker service

- [ ] **INFRA-202:** Configurar Redis persistence
  - Tiempo: 2h
  - Responsable: DevOps
  - Output: RDB snapshots cada 5 min

**Definition of Done:**
- Bootstrap tarda <5 min (antes 1-2h)
- Usuario ve progreso en tiempo real
- Sin timeouts ni bloqueos
- Stockfish pool maneja 3 análisis en paralelo
- Tests confirman task completa exitosamente

---

### Sprint 3: Refactoring y Calidad (Semana 4)

**Objetivos:**
- Separar mega-repositorio
- Aumentar test coverage a 80%
- Mejorar performance queries

**Tareas:**

#### Backend
- [ ] **BE-301:** Separar SqliteGameRepository
  - Tiempo: 8h
  - Responsable: Backend Senior
  - Output: `GameRepository`, `PuzzleRepository`, `StatsRepository`, `TraceRepository`

- [ ] **BE-302:** Implementar patrón Repository genérico
  - Tiempo: 4h
  - Responsable: Backend Senior
  - Output: `BaseRepository` con CRUD común

- [ ] **BE-303:** Optimizar queries N+1
  - Tiempo: 6h
  - Responsable: Backend Senior
  - Output: JOINs en lugar de loops, queries batch

- [ ] **BE-304:** Agregar índices faltantes (Postgres)
  - Tiempo: 2h
  - Responsable: Backend Mid
  - Output: Índices GIN para arrays, BRIN para timestamps

- [ ] **BE-305:** Tests unitarios dominio (30+ tests)
  - Tiempo: 8h
  - Responsable: Backend Senior + Mid
  - Output: `tests/domain/`, coverage >80% domain layer

- [ ] **BE-306:** Tests integración endpoints (40+ tests)
  - Tiempo: 10h
  - Responsable: Backend Senior + Mid
  - Output: `tests/api/`, todos los endpoints testeados

- [ ] **BE-307:** Mocks para Stockfish/LLM
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `tests/mocks.py` con fixtures

#### Frontend
- [ ] **FE-301:** Separar session page en componentes
  - Tiempo: 6h
  - Responsable: Frontend Senior
  - Output: `<PuzzleBoard>`, `<PuzzleList>`, `<ChatPanel>`

- [ ] **FE-302:** Implementar state management (Zustand)
  - Tiempo: 5h
  - Responsable: Frontend Senior
  - Output: `src/stores/sessionStore.ts`

- [ ] **FE-303:** Tests E2E Playwright (15+ scenarios)
  - Tiempo: 8h
  - Responsable: Frontend Senior
  - Output: `tests/e2e/` con flujos críticos

- [ ] **FE-304:** Tests unitarios componentes (Vitest)
  - Tiempo: 6h
  - Responsable: Frontend Senior
  - Output: `src/components/*.test.tsx`

#### Code Quality
- [ ] **QA-301:** Configurar SonarQube
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: Análisis estático en CI

- [ ] **QA-302:** Eliminar code smells (10+ issues)
  - Tiempo: 6h
  - Responsable: Backend Senior
  - Output: SonarQube score >8/10

- [ ] **QA-303:** Documentar APIs (OpenAPI/Swagger)
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `/docs` con specs completas

**Definition of Done:**
- Coverage backend >80%, frontend >60%
- Todos los tests CI pasando
- Queries optimizadas (medibles con EXPLAIN ANALYZE)
- Code base refactorizado (SRP, DRY)
- Documentación API actualizada

---

### Sprint 4: Features Críticas (Semana 5)

**Objetivos:**
- Repaso espaciado funcional
- Progreso histórico visible
- Chat LLM mejorado

**Tareas:**

#### Backend
- [ ] **BE-401:** Implementar algoritmo SM-2 (spaced repetition)
  - Tiempo: 6h
  - Responsable: Backend Mid
  - Output: `application/spaced_repetition.py`

- [ ] **BE-402:** Endpoint /review/due (puzzles por repasar)
  - Tiempo: 3h
  - Responsable: Backend Mid
  - Output: Lista puzzles con due_date <= today

- [ ] **BE-403:** Endpoint /review/{puzzle_id}/complete
  - Tiempo: 2h
  - Responsable: Backend Mid
  - Output: Actualiza next_review según performance

- [ ] **BE-404:** Endpoint /stats/history (gráfica progreso)
  - Tiempo: 4h
  - Responsable: Backend Senior
  - Output: Retorna solve_rate por día últimos 30 días

- [ ] **BE-405:** Chat LLM con contexto usuario
  - Tiempo: 6h
  - Responsable: Backend Mid
  - Output: System prompt incluye stats/debilidades

- [ ] **BE-406:** Chat con tool calling (generar plan, buscar puzzles)
  - Tiempo: 8h
  - Responsable: Backend Senior
  - Output: LLM puede llamar funciones

- [ ] **BE-407:** Notificaciones (tabla + endpoints)
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `/notifications` con unread count

#### Frontend
- [ ] **FE-401:** Página /review con queue
  - Tiempo: 6h
  - Responsable: Frontend Senior
  - Output: Lista puzzles due + interfaz resolución

- [ ] **FE-402:** Página /progress con gráficas
  - Tiempo: 8h
  - Responsable: Frontend Senior
  - Output: Chart.js con solve rate, heatmap debilidades

- [ ] **FE-403:** Mejorar chat UI (streaming)
  - Tiempo: 5h
  - Responsable: Frontend Senior
  - Output: Respuestas LLM aparecen en tiempo real

- [ ] **FE-404:** Notificaciones badge
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: Ícono campana con contador

- [ ] **FE-405:** Persistir estado sesión (localStorage)
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: No pierde progreso al recargar

#### UX/UI
- [ ] **UI-401:** Diseñar componentes coherentes (Design System básico)
  - Tiempo: 6h
  - Responsable: Frontend Senior
  - Output: `Button`, `Input`, `Card` estandarizados

- [ ] **UI-402:** Feedback visual (toasts, alerts)
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: Librería react-hot-toast integrada

**Definition of Done:**
- Repaso espaciado funciona (puzzles aparecen en fechas correctas)
- Gráfica progreso muestra datos reales
- Chat LLM usa contexto del usuario
- UX fluida sin pérdida de estado

---

### Sprint 5: Performance y Caché (Semana 6)

**Objetivos:**
- Caché Redis funcional
- Performance <3s todos los endpoints
- Optimización bundle frontend

**Tareas:**

#### Backend
- [ ] **BE-501:** Implementar RedisCache wrapper
  - Tiempo: 4h
  - Responsable: Backend Mid
  - Output: `infrastructure/cache.py`

- [ ] **BE-502:** Caché evaluaciones Stockfish
  - Tiempo: 3h
  - Responsable: Backend Senior
  - Output: Cache hit rate >50% tras warm-up

- [ ] **BE-503:** Caché planes generados
  - Tiempo: 2h
  - Responsable: Backend Mid
  - Output: TTL 1 hora, invalidación manual

- [ ] **BE-504:** Caché diagnósticos
  - Tiempo: 2h
  - Responsable: Backend Mid
  - Output: TTL 6 horas

- [ ] **BE-505:** Optimizar serialización (orjson)
  - Tiempo: 3h
  - Responsable: Backend Senior
  - Output: Reemplazar json.dumps con orjson

- [ ] **BE-506:** Database connection pooling
  - Tiempo: 3h
  - Responsable: Backend Senior
  - Output: asyncpg pool 10-50 connections

- [ ] **BE-507:** Benchmark y profiling (locust)
  - Tiempo: 5h
  - Responsable: Backend Senior + DevOps
  - Output: Report 100 usuarios concurrentes

#### Frontend
- [ ] **FE-501:** Code splitting (dynamic imports)
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: Bundle main <200KB

- [ ] **FE-502:** Image optimization (next/image)
  - Tiempo: 2h
  - Responsable: Frontend Senior
  - Output: Imágenes piezas ajedrez optimizadas

- [ ] **FE-503:** Lazy loading componentes pesados
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: ChessBoard carga bajo demanda

- [ ] **FE-504:** Implementar SWR (stale-while-revalidate)
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: Caché client-side con revalidación

- [ ] **FE-505:** Lighthouse audit >90 score
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: Performance, Accessibility, SEO >90

#### Infraestructura
- [ ] **INFRA-501:** Setup Nginx (reverse proxy)
  - Tiempo: 4h
  - Responsable: DevOps
  - Output: nginx.conf con gzip, cache headers

- [ ] **INFRA-502:** CDN para assets estáticos (Cloudflare)
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: JS/CSS servidos desde CDN

**Definition of Done:**
- Todos los endpoints <3s (p95)
- Cache hit rate >60% tras 1 hora uso
- Bundle frontend <300KB gzipped
- Lighthouse score >90

---

### Sprint 6: Deploy y Monitoreo (Semana 7)

**Objetivos:**
- Deploy staging funcional
- Monitoreo en tiempo real
- Backups automáticos

**Tareas:**

#### Infraestructura
- [ ] **INFRA-601:** Crear Dockerfile producción (multi-stage)
  - Tiempo: 4h
  - Responsable: DevOps
  - Output: `Dockerfile.prod` optimizado

- [ ] **INFRA-602:** docker-compose producción
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: `docker-compose.prod.yml` con healthchecks

- [ ] **INFRA-603:** Setup servidor staging (DigitalOcean/AWS)
  - Tiempo: 6h
  - Responsable: DevOps
  - Output: VPS con Docker instalado

- [ ] **INFRA-604:** CI/CD deploy automático (GitHub Actions)
  - Tiempo: 5h
  - Responsable: DevOps
  - Output: Push a `main` → deploy staging

- [ ] **INFRA-605:** SSL certificado (Let's Encrypt)
  - Tiempo: 2h
  - Responsable: DevOps
  - Output: HTTPS funcionando

- [ ] **INFRA-606:** Backup PostgreSQL automático (diario)
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: Cron job pg_dump → S3

#### Monitoreo
- [ ] **MON-601:** Setup Prometheus
  - Tiempo: 4h
  - Responsable: DevOps
  - Output: Scraping métricas cada 15s

- [ ] **MON-602:** Setup Grafana + dashboards
  - Tiempo: 5h
  - Responsable: DevOps
  - Output: 3 dashboards (API, DB, Workers)

- [ ] **MON-603:** Configurar Sentry
  - Tiempo: 2h
  - Responsable: DevOps
  - Output: Errores enviados a Sentry

- [ ] **MON-604:** Alertas (email/Slack)
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: Alerta si error rate >5% o uptime <99%

- [ ] **MON-605:** Logs centralizados (Loki)
  - Tiempo: 4h
  - Responsable: DevOps
  - Output: Logs queryables en Grafana

#### Seguridad
- [ ] **SEC-601:** Secrets en vault (no hardcoded)
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: Secrets en GitHub Secrets / HashiCorp Vault

- [ ] **SEC-602:** Firewall + fail2ban
  - Tiempo: 2h
  - Responsable: DevOps
  - Output: Solo puertos 80, 443 abiertos

- [ ] **SEC-603:** Audit logs
  - Tiempo: 3h
  - Responsable: Backend Senior
  - Output: Tabla audit con cambios críticos

#### Testing
- [ ] **QA-601:** Smoke tests staging
  - Tiempo: 4h
  - Responsable: QA
  - Output: Suite 20 tests críticos

- [ ] **QA-602:** Load testing (1000 req/min)
  - Tiempo: 4h
  - Responsable: QA + DevOps
  - Output: Sistema soporta carga sin degradación

**Definition of Done:**
- Staging accesible vía HTTPS
- Deploy automático funcionando
- Dashboards Grafana con datos reales
- Alertas configuradas y testeadas
- Backups ejecutándose

---

### Sprint 7: Beta Testing y Fixes (Semana 8)

**Objetivos:**
- Onboarding 50 usuarios beta
- Corregir bugs críticos
- Documentación usuario final

**Tareas:**

#### Producto
- [ ] **PROD-701:** Crear landing page
  - Tiempo: 8h
  - Responsable: Frontend Senior
  - Output: `/` con CTA "Join Beta"

- [ ] **PROD-702:** Onboarding wizard (3 pasos)
  - Tiempo: 6h
  - Responsable: Frontend Senior
  - Output: 1) Conectar Lichess, 2) Bootstrap, 3) Primer puzzle

- [ ] **PROD-703:** Tutorial interactivo
  - Tiempo: 5h
  - Responsable: Frontend Senior
  - Output: Tooltips guiados (react-joyride)

- [ ] **PROD-704:** Documentación usuario (FAQ)
  - Tiempo: 4h
  - Responsable: QA + Frontend
  - Output: `/help` con 20+ preguntas frecuentes

#### Beta Testing
- [ ] **TEST-701:** Reclutar 50 beta testers
  - Tiempo: 8h
  - Responsable: Product Owner
  - Output: Lista emails + invitaciones enviadas

- [ ] **TEST-702:** Formulario feedback
  - Tiempo: 3h
  - Responsable: Frontend Senior
  - Output: `/feedback` con TypeForm embebido

- [ ] **TEST-703:** Analytics (PostHog/Mixpanel)
  - Tiempo: 4h
  - Responsable: Frontend Senior
  - Output: Tracking eventos críticos

- [ ] **TEST-704:** Session recording (LogRocket)
  - Tiempo: 2h
  - Responsable: Frontend Senior
  - Output: Primeras 100 sesiones grabadas

#### Bug Fixes
- [ ] **FIX-701:** Corregir bugs P0 (reportados por beta)
  - Tiempo: 16h
  - Responsable: Todo el equipo
  - Output: 0 bugs críticos abiertos

- [ ] **FIX-702:** Optimizaciones UX (basado en feedback)
  - Tiempo: 12h
  - Responsable: Frontend Senior
  - Output: 5+ mejoras implementadas

#### DevOps
- [ ] **INFRA-701:** Runbook operacional
  - Tiempo: 4h
  - Responsable: DevOps
  - Output: Guía troubleshooting, rollback, escalado

- [ ] **INFRA-702:** Disaster recovery plan
  - Tiempo: 3h
  - Responsable: DevOps
  - Output: Procedimiento restaurar desde backup

**Definition of Done:**
- 50 usuarios registrados y activos
- Bugs críticos resueltos
- Feedback positivo >80%
- Documentación completa
- Sistema estable en staging

---

## 5. BACKLOG PRIORIZADO

### Épicas y User Stories

#### ÉPICA 1: Autenticación y Usuarios [P0]
- **US-001:** Como usuario, quiero registrarme con email/password para tener cuenta personal
  - Acceptance: Form validación, email único, password ≥8 chars
  - Story points: 5
  
- **US-002:** Como usuario, quiero loggearme para acceder a mis datos
  - Acceptance: JWT generado, token válido 7 días, logout limpia sesión
  - Story points: 3

- **US-003:** Como usuario, quiero recuperar contraseña olvidada
  - Acceptance: Email con link temporal (1h), cambio password funciona
  - Story points: 8

#### ÉPICA 2: Importación y Análisis [P0]
- **US-010:** Como usuario, quiero importar partidas sin esperar bloqueado
  - Acceptance: Request retorna inmediato, progreso visible, completa en <5min
  - Story points: 13

- **US-011:** Como usuario, quiero ver progreso de análisis en tiempo real
  - Acceptance: Barra progreso actualiza cada 2s, mensaje descriptivo
  - Story points: 5

- **US-012:** Como usuario, quiero cancelar análisis en curso
  - Acceptance: Botón "Cancelar", task revocada, datos parciales guardados
  - Story points: 8

#### ÉPICA 3: Entrenamiento con Puzzles [P0]
- **US-020:** Como usuario, quiero resolver puzzles de mis blunders
  - Acceptance: Tablero interactivo, validación multi-step, feedback inmediato
  - Story points: 8

- **US-021:** Como usuario, quiero ver estadísticas de resolución
  - Acceptance: % acierto por tag, progreso histórico, racha actual
  - Story points: 5

- **US-022:** Como usuario, quiero puzzles adaptados a mi fatiga
  - Acceptance: Fatiga alta → puzzles fáciles, fatiga baja → desafiantes
  - Story points: 8

#### ÉPICA 4: Repaso Espaciado [P1]
- **US-030:** Como usuario, quiero repasar puzzles en intervalos óptimos
  - Acceptance: Algoritmo SM-2, notificación cuando hay puzzles due
  - Story points: 13

- **US-031:** Como usuario, quiero marcar puzzle como "muy fácil" o "difícil"
  - Acceptance: Botones rating, ajusta intervalo siguiente
  - Story points: 5

#### ÉPICA 5: Planes Personalizados [P1]
- **US-040:** Como usuario, quiero plan diario adaptado a tiempo disponible
  - Acceptance: Input minutos, genera bloques, suma exacta
  - Story points: 8

- **US-041:** Como usuario, quiero timer para cada bloque de entrenamiento
  - Acceptance: Countdown visual, alerta cuando termina, pausa/resume
  - Story points: 5

#### ÉPICA 6: Diagnóstico y Cursos [P1]
- **US-050:** Como usuario, quiero ver mis debilidades principales
  - Acceptance: Top 5 tags con peor rate, evidencia estadística
  - Story points: 5

- **US-051:** Como usuario, quiero cursos recomendados según debilidades
  - Acceptance: 3-5 cursos priorizados, duración estimada
  - Story points: 8

- **US-052:** Como usuario, quiero completar curso estructurado
  - Acceptance: 10 puzzles ordenados, progreso guardado, certificado
  - Story points: 13

### Backlog Sprint 1-2 (Semanas 2-3)

| ID | Tarea | Tipo | Prioridad | SP | Asignado |
|----|-------|------|-----------|----|----|
| BE-101 | Modelo User | Dev | P0 | 3 | Backend Senior |
| BE-102 | Password hashing | Dev | P0 | 2 | Backend Senior |
| BE-103 | JWT tokens | Dev | P0 | 5 | Backend Senior |
| BE-104 | Endpoints auth | Dev | P0 | 5 | Backend Mid |
| FE-101 | Páginas login/register | Dev | P0 | 8 | Frontend Senior |
| FE-102 | Auth context | Dev | P0 | 5 | Frontend Senior |
| BE-201 | Setup Celery | Infra | P0 | 5 | Backend Mid |
| BE-202 | Task bootstrap async | Dev | P0 | 8 | Backend Senior |
| FE-201 | Progress bar UI | Dev | P0 | 3 | Frontend Senior |

**Total SP Sprint 1-2:** 44 points  
**Velocidad estimada:** 40 points/sprint  
**Duración:** 2 sprints (2 semanas)

---

## 6. ESPECIFICACIONES TÉCNICAS

### 6.1 API Specifications

#### Endpoint: POST /auth/register

**Request:**
```json
{
  "username": "string (3-20 chars, alphanumeric)",
  "email": "string (valid email)",
  "password": "string (min 8 chars, 1 uppercase, 1 number)"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "created_at": "ISO8601"
}
```

**Errors:**
- 400: Email already registered
- 400: Username taken
- 422: Validation error

#### Endpoint: POST /coach/bootstrap-async

**Request:**
```json
{
  "platform": "lichess | chesscom",
  "import_games": "int (1-500)",
  "daily_limit": "int (1-50)",
  "fatigue": "int? (0-10)"
}
```

**Response 202:**
```json
{
  "task_id": "uuid",
  "status": "PENDING",
  "message": "Bootstrap iniciado"
}
```

#### Endpoint: GET /coach/bootstrap-status/{task_id}

**Response (PROGRESS):**
```json
{
  "state": "PROGRESS",
  "current": 45,
  "total": 100,
  "status": "Analizando con Stockfish...",
  "eta_seconds": 180
}
```

**Response (SUCCESS):**
```json
{
  "state": "SUCCESS",
  "current": 100,
  "total": 100,
  "result": {
    "games": 50,
    "puzzles": 38,
    "duration_seconds": 287
  }
}
```

### 6.2 Database Schema (PostgreSQL)

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    lichess_username VARCHAR(50),
    chesscom_username VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    settings JSONB DEFAULT '{}'::jsonb
);

-- Games
CREATE TABLE games (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    game_id VARCHAR(100) NOT NULL,
    played_at TIMESTAMP NOT NULL,
    white VARCHAR(100) NOT NULL,
    black VARCHAR(100) NOT NULL,
    result VARCHAR(10),
    opening_name VARCHAR(200),
    time_control VARCHAR(50),
    pgn TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform, game_id)
);

-- Puzzles
CREATE TABLE puzzles (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    game_id BIGINT REFERENCES games(id) ON DELETE CASCADE,
    ply INTEGER NOT NULL,
    fen_before TEXT NOT NULL,
    played_uci VARCHAR(10) NOT NULL,
    best_uci VARCHAR(10) NOT NULL,
    pv_uci TEXT[] NOT NULL,  -- Array de strings
    tags TEXT[] NOT NULL,
    swing_cp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Puzzle Stats
CREATE TABLE puzzle_stats (
    puzzle_id BIGINT PRIMARY KEY REFERENCES puzzles(id) ON DELETE CASCADE,
    attempts INTEGER DEFAULT 0,
    solved INTEGER DEFAULT 0,
    first_attempt_at TIMESTAMP,
    last_attempt_at TIMESTAMP,
    average_time_seconds INTEGER
);

-- Spaced Review
CREATE TABLE spaced_reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    puzzle_id BIGINT NOT NULL REFERENCES puzzles(id) ON DELETE CASCADE,
    due_date DATE NOT NULL,
    interval_days INTEGER NOT NULL,
    easiness_factor FLOAT DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    UNIQUE(user_id, puzzle_id, due_date)
);

-- Coach Traces
CREATE TABLE coach_traces (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    intent VARCHAR(50) NOT NULL,
    fatigue INTEGER NOT NULL,
    decision JSONB NOT NULL
);

-- Notifications
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    link VARCHAR(500),
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_games_user_played ON games(user_id, played_at DESC);
CREATE INDEX idx_puzzles_user_created ON puzzles(user_id, created_at DESC);
CREATE INDEX idx_puzzles_tags ON puzzles USING GIN(tags);
CREATE INDEX idx_reviews_user_due ON spaced_reviews(user_id, due_date) WHERE NOT completed;
CREATE INDEX idx_traces_user_created ON coach_traces(user_id, created_at DESC);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id) WHERE NOT read;
```

### 6.3 Environment Variables

```bash
# Backend (.env.backend)
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chess_coach
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET_KEY=<generate-strong-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080  # 1 semana

# Stockfish
STOCKFISH_PATH=/usr/bin/stockfish
STOCKFISH_DEPTH=8
STOCKFISH_THREADS=2
STOCKFISH_HASH_MB=128
STOCKFISH_POOL_SIZE=3

# LLM (optional)
LLM_PROVIDER=openai  # ollama | openai | none
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Monitoring
SENTRY_DSN=https://...
ENVIRONMENT=staging  # development | staging | production

# Email (para notificaciones)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@chesscoach.com
SMTP_PASSWORD=...

# Frontend (.env.local)
NEXT_PUBLIC_API_BASE_URL=https://api.chesscoach.com/v1
NEXT_PUBLIC_WS_URL=wss://api.chesscoach.com/ws
NEXT_PUBLIC_SENTRY_DSN=https://...
```

---

## 7. PLAN DE TESTING

### 7.1 Estrategia de Testing

**Pirámide de testing:**
```
         /\
        /UI\       10% - E2E (Playwright)
       /────\
      /Integr\     30% - Integration (API tests)
     /────────\
    /  Unit    \   60% - Unit (pytest, vitest)
   /────────────\
```

### 7.2 Backend Testing

#### 7.2.1 Tests Unitarios (pytest)

**Estructura:**
```
tests/
├── conftest.py              # Fixtures globales
├── unit/
│   ├── domain/
│   │   ├── test_models.py
│   │   └── test_training_taxonomy.py
│   ├── application/
│   │   ├── test_blunder_mining.py
│   │   ├── test_pattern_tagger.py
│   │   ├── test_coach_planner.py
│   │   └── test_diagnostics_engine.py
│   └── infrastructure/
│       ├── test_repositories.py
│       └── test_stockfish_engine.py
├── integration/
│   ├── test_api_auth.py
│   ├── test_api_coach.py
│   ├── test_api_puzzles.py
│   └── test_database.py
└── e2e/
    └── test_bootstrap_flow.py
```

**Ejemplo test unitario:**
```python
# tests/unit/application/test_pattern_tagger.py
import pytest
from chess_coach.application.pattern_tagger import tag_from_position_and_pv
from chess_coach.domain.training_taxonomy import PatternTag

def test_detect_mate_pattern():
    # Scholar's mate threat
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 1"
    pv = ["d8h4", "e1f1"]
    
    tags = tag_from_position_and_pv(fen, pv)
    
    assert PatternTag.CHECK in tags
    assert PatternTag.MATE in tags

def test_detect_fork():
    # Knight fork king and rook
    fen = "r3k2r/8/8/4N3/8/8/8/4K3 b kq - 0 1"
    pv = ["e5c6"]  # Fork king on e8 and rook on a8
    
    tags = tag_from_position_and_pv(fen, pv)
    
    assert PatternTag.FORK in tags

@pytest.mark.parametrize("fen,pv,expected_tag", [
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", ["e2e4"], PatternTag.HANGING_PIECE),
    # ... más casos
])
def test_tag_various_patterns(fen, pv, expected_tag):
    tags = tag_from_position_and_pv(fen, pv)
    assert expected_tag in tags
```

**Ejemplo test integración:**
```python
# tests/integration/test_api_coach.py
import pytest
from fastapi.testclient import TestClient
from chess_coach.api.app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Register and login
    client.post("/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test1234"
    })
    response = client.post("/v1/auth/login", data={
        "username": "testuser",
        "password": "Test1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_bootstrap_async_requires_auth(client):
    response = client.post("/v1/coach/bootstrap-async", json={
        "platform": "lichess",
        "import_games": 10
    })
    assert response.status_code == 401

def test_bootstrap_async_returns_task_id(client, auth_headers):
    response = client.post("/v1/coach/bootstrap-async", json={
        "platform": "lichess",
        "import_games": 10
    }, headers=auth_headers)
    
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"

def test_bootstrap_status_returns_progress(client, auth_headers):
    # Inicia task
    task_response = client.post("/v1/coach/bootstrap-async", json={
        "platform": "lichess",
        "import_games": 5
    }, headers=auth_headers)
    task_id = task_response.json()["task_id"]
    
    # Consulta status
    status_response = client.get(f"/v1/coach/bootstrap-status/{task_id}", headers=auth_headers)
    
    assert status_response.status_code == 200
    data = status_response.json()
    assert "state" in data
    assert "current" in data
    assert "total" in data
```

**Coverage target:**
- Domain: >90%
- Application: >80%
- Infrastructure: >70%
- API: >80%

**Comandos:**
```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=chess_coach --cov-report=html

# Solo unitarios (rápidos)
pytest tests/unit/ -v

# Solo un módulo
pytest tests/unit/application/test_blunder_mining.py -v

# Con markers
pytest -m "not slow" -v  # Excluye tests lentos
```

### 7.3 Frontend Testing

#### 7.3.1 Tests Unitarios (Vitest)

**Estructura:**
```
src/
├── components/
│   ├── ChessBoard.tsx
│   ├── ChessBoard.test.tsx
│   ├── ProgressBar.tsx
│   └── ProgressBar.test.tsx
├── lib/
│   ├── auth/
│   │   ├── client.ts
│   │   └── client.test.ts
└── stores/
    ├── sessionStore.ts
    └── sessionStore.test.ts
```

**Ejemplo:**
```typescript
// src/components/ProgressBar.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ProgressBar } from './ProgressBar'

describe('ProgressBar', () => {
  it('muestra porcentaje correcto', () => {
    render(<ProgressBar current={50} total={100} />)
    expect(screen.getByText('50%')).toBeInTheDocument()
  })

  it('aplica clase completed cuando 100%', () => {
    const { container } = render(<ProgressBar current={100} total={100} />)
    expect(container.firstChild).toHaveClass('completed')
  })

  it('maneja valores edge case', () => {
    render(<ProgressBar current={0} total={0} />)
    expect(screen.getByText('0%')).toBeInTheDocument()
  })
})
```

#### 7.3.2 Tests E2E (Playwright)

**Estructura:**
```
tests/e2e/
├── auth.spec.ts
├── bootstrap.spec.ts
├── puzzles.spec.ts
└── review.spec.ts
```

**Ejemplo:**
```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('usuario puede registrarse y logearse', async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // Registro
    await page.click('text=Register')
    await page.fill('input[name="username"]', 'e2euser')
    await page.fill('input[name="email"]', 'e2e@test.com')
    await page.fill('input[name="password"]', 'Test1234')
    await page.click('button[type="submit"]')
    
    // Debe redirigir a login
    await expect(page).toHaveURL(/\/login/)
    
    // Login
    await page.fill('input[name="username"]', 'e2euser')
    await page.fill('input[name="password"]', 'Test1234')
    await page.click('button[type="submit"]')
    
    // Debe redirigir a dashboard
    await expect(page).toHaveURL(/\/session/)
    await expect(page.locator('text=e2euser')).toBeVisible()
  })

  test('muestra error con credenciales incorrectas', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', 'wronguser')
    await page.fill('input[name="password"]', 'wrongpass')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('text=Incorrect username or password')).toBeVisible()
  })
})

// tests/e2e/puzzles.spec.ts
test.describe('Puzzle Solving', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', 'testuser')
    await page.fill('input[name="password"]', 'Test1234')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/session/)
  })

  test('resolver puzzle correctamente incrementa stats', async ({ page }) => {
    // Seleccionar primer puzzle
    await page.click('text=Puzzle #1')
    
    // Mover pieza (simulado - necesita interacción con ChessBoard)
    const board = page.locator('.chessboard')
    await expect(board).toBeVisible()
    
    // Hacer movimiento correcto
    // (Esto requiere drag & drop, complejo en Playwright)
    // Por ahora validamos que UI cambia
    await page.click('button:has-text("Submit Move")')
    
    await expect(page.locator('text=✅ Correcto')).toBeVisible()
  })
})
```

**Comandos:**
```bash
# Ejecutar tests E2E
npx playwright test

# Con UI
npx playwright test --ui

# Solo un spec
npx playwright test tests/e2e/auth.spec.ts

# Generar report
npx playwright show-report
```

### 7.4 CI/CD Testing

**GitHub Actions workflow:**
```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: chess_coach_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Install Stockfish
        run: sudo apt-get install -y stockfish
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/chess_coach_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest tests/ -v --cov=chess_coach --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: web/chess-coach-web/package-lock.json
      
      - name: Install dependencies
        working-directory: web/chess-coach-web
        run: npm ci
      
      - name: Run unit tests
        working-directory: web/chess-coach-web
        run: npm run test:unit
      
      - name: Build
        working-directory: web/chess-coach-web
        run: npm run build
      
      - name: Install Playwright
        working-directory: web/chess-coach-web
        run: npx playwright install --with-deps
      
      - name: Run E2E tests
        working-directory: web/chess-coach-web
        run: npm run test:e2e
      
      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: web/chess-coach-web/playwright-report/
```

---

## 8. PLAN DE DEPLOY

### 8.1 Arquitectura de Deploy

```
┌──────────────────────────────────────────────────────────┐
│               CLOUDFLARE (DNS + CDN + WAF)               │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌──────────────────────────────────────────────────────────┐
│         VPS (DigitalOcean Droplet / AWS EC2)            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         NGINX (Reverse Proxy + SSL)                │ │
│  └───────┬─────────────────────────┬──────────────────┘ │
│          │                         │                     │
│          ▼                         ▼                     │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Frontend   │         │   Backend    │             │
│  │ (Next.js)    │         │  (FastAPI)   │             │
│  │ Port 3000    │         │  Port 8000   │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                     │
│          ┌────────────────────────┼────────────┐        │
│          ▼                        ▼            ▼        │
│  ┌─────────────┐       ┌─────────────┐  ┌──────────┐  │
│  │  PostgreSQL │       │    Redis    │  │  Celery  │  │
│  │  Port 5432  │       │  Port 6379  │  │  Workers │  │
│  └─────────────┘       └─────────────┘  └──────────┘  │
│                                                          │
│  Volumes:                                               │
│  - /data/postgres                                       │
│  - /data/redis                                          │
│  - /data/backups                                        │
└──────────────────────────────────────────────────────────┘
```

### 8.2 Docker Setup

#### 8.2.1 Dockerfile Backend (Producción)

```dockerfile
# Dockerfile.backend
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    stockfish \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Production stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/games/stockfish /usr/games/stockfish

# Copy application
COPY chess_coach/ ./chess_coach/

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

CMD ["uvicorn", "chess_coach.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 8.2.2 Dockerfile Frontend

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY web/chess-coach-web/package*.json ./
RUN npm ci

# Copy source
COPY web/chess-coach-web/ ./

# Build
ENV NEXT_PUBLIC_API_BASE_URL=https://api.chesscoach.com/v1
RUN npm run build

# --- Production stage ---
FROM node:18-alpine

WORKDIR /app

# Copy built app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

#### 8.2.3 Docker Compose Producción

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: chess_coach_db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: chess_coach_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: chess_coach_api
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      STOCKFISH_PATH: /usr/games/stockfish
      STOCKFISH_DEPTH: 8
      SENTRY_DSN: ${SENTRY_DSN}
      ENVIRONMENT: production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "127.0.0.1:8000:8000"
    restart: unless-stopped

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: chess_coach_worker
    command: celery -A chess_coach.workers.tasks worker --loglevel=info --concurrency=2
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      STOCKFISH_PATH: /usr/games/stockfish
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: chess_coach_web
    ports:
      - "127.0.0.1:3000:3000"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: chess_coach_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - /var/log/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: chess_coach_prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "127.0.0.1:9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: chess_coach_grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    ports:
      - "127.0.0.1:3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 8.3 Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;

    # Upstream backends
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name chesscoach.com www.chesscoach.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name chesscoach.com www.chesscoach.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API
        location /v1/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Auth endpoints (más restrictivos)
        location /v1/auth/ {
            limit_req zone=auth_limit burst=5 nodelay;
            
            proxy_pass http://backend;
            # ... same headers
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Static assets (cache aggressive)
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 8.4 GitHub Actions Deploy

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      
      - name: Deploy to server
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USER: ${{ secrets.SERVER_USER }}
        run: |
          ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'EOF'
            cd /opt/chess_coach
            git pull origin main
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d --build
            docker-compose -f docker-compose.prod.yml exec -T backend python scripts/migrate_db.py
            docker system prune -af
          EOF
      
      - name: Health check
        run: |
          sleep 30
          curl --fail https://api.chesscoach.com/health || exit 1
      
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deploy to production: ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 8.5 Backup Strategy

```bash
# scripts/backup_db.sh
#!/bin/bash

BACKUP_DIR=/data/backups
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"

# Backup PostgreSQL
docker exec chess_coach_db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} | gzip > ${BACKUP_FILE}

# Upload to S3
aws s3 cp ${BACKUP_FILE} s3://chesscoach-backups/postgres/

# Keep only last 7 days locally
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +7 -delete

# Keep last 30 backups in S3
aws s3 ls s3://chesscoach-backups/postgres/ | sort -r | tail -n +31 | awk '{print $4}' | xargs -I {} aws s3 rm s3://chesscoach-backups/postgres/{}
```

**Cron job:**
```bash
# crontab -e
0 2 * * * /opt/chess_coach/scripts/backup_db.sh
```

---

## 9. GESTIÓN DE RIESGOS

### 9.1 Matriz de Riesgos

| ID | Riesgo | Probabilidad | Impacto | Severidad | Mitigación |
|----|--------|--------------|---------|-----------|------------|
| R1 | Stockfish timeout bloquea workers | Alta | Alto | 🔴 Crítico | Timeout configurable, retry logic, pool de procesos |
| R2 | Migración DB pierde datos | Media | Alto | 🔴 Crítico | Backup antes de migrar, migración idempotente, tests |
| R3 | LLM API rate limit excedido | Media | Medio | 🟠 Alto | Caché respuestas, fallback determinista, retry exponential |
| R4 | Usuarios beta reportan bugs críticos | Alta | Medio | 🟠 Alto | Testing exhaustivo pre-beta, feature flags, rollback rápido |
| R5 | Performance degradación con 100+ users | Media | Alto | 🟠 Alto | Load testing, auto-scaling, monitoreo proactivo |
| R6 | Dependencias breaking changes | Baja | Medio | 🟡 Medio | Pin versions, Dependabot alerts, staging tests |
| R7 | Equipo bloqueado por decisión arquitectónica | Media | Medio | 🟡 Medio | ADRs documentados, sync semanal, pair programming |
| R8 | SSL certificado expira | Baja | Alto | 🟠 Alto | Auto-renewal (certbot), alertas 30 días antes |

### 9.2 Plan de Contingencia

#### R1: Stockfish Timeout

**Síntomas:**
- Celery tasks fallan con timeout
- Workers bloqueados

**Acciones:**
1. **Inmediato:** Reducir `STOCKFISH_DEPTH` de 8 a 6
2. **Short-term:** Implementar timeout por análisis (30s max)
3. **Long-term:** Distribuir análisis en múltiples workers

**Código:**
```python
# workers/tasks.py
@celery_app.task(bind=True, time_limit=300, soft_time_limit=270)
def bootstrap_user(self, ...):
    # Si tarda >270s, lanza SoftTimeLimitExceeded
    # Si tarda >300s, hard kill
    pass

# infrastructure/stockfish_pool.py
def analyze_with_timeout(board, depth, timeout=30):
    import signal
    
    def handler(signum, frame):
        raise TimeoutError("Stockfish analysis timeout")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    
    try:
        result = engine.analyze(board, depth)
    finally:
        signal.alarm(0)
    
    return result
```

#### R2: Migración DB Pierde Datos

**Prevención:**
1. Backup manual antes de migrar
2. Migración en staging primero
3. Script rollback preparado

**Checklist pre-migración:**
```bash
# 1. Backup
./scripts/backup_db.sh

# 2. Verificar backup
gunzip -c /data/backups/backup_TIMESTAMP.sql.gz | head -n 100

# 3. Migrar staging
python scripts/migrate_sqlite_to_postgres.py --env=staging

# 4. Validar staging (queries manuales)
psql -h localhost -U postgres -d chess_coach_staging -c "SELECT COUNT(*) FROM games;"

# 5. Si OK, migrar producción
python scripts/migrate_sqlite_to_postgres.py --env=production

# 6. Validar producción
psql -h localhost -U postgres -d chess_coach -c "SELECT COUNT(*) FROM games;"

# 7. Si falló, rollback
psql -h localhost -U postgres -d chess_coach < /data/backups/backup_TIMESTAMP.sql
```

#### R5: Performance Degradación

**Monitoreo:**
- Alertas si p95 latency > 5s
- Alertas si CPU > 80% por 5 min
- Alertas si memoria > 90%

**Acciones escalado:**
```bash
# Horizontal scaling (más workers)
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=5

# Vertical scaling (más recursos)
# Editar docker-compose.prod.yml:
# celery_worker:
#   deploy:
#     resources:
#       limits:
#         cpus: '2.0'
#         memory: 4G

# Database connection pool
# En .env:
DATABASE_POOL_SIZE=50  # aumentar de 20
```

---

## 10. KPIS Y MÉTRICAS

### 10.1 Métricas de Desarrollo

| Métrica | Target | Medición | Frecuencia |
|---------|--------|----------|------------|
| **Velocity** | 40 SP/sprint | Jira/Linear | Por sprint |
| **Test Coverage** | Backend >80%, Frontend >60% | CodeCov | Cada commit |
| **Build Time** | <5 min | GitHub Actions | Cada commit |
| **Code Review Time** | <4 horas | GitHub | Semanal |
| **Bug Escape Rate** | <5% a producción | Sentry | Semanal |
| **Technical Debt** | <10% tiempo | SonarQube | Mensual |

### 10.2 Métricas de Producto

| Métrica | Target | Herramienta | Frecuencia |
|---------|--------|-------------|------------|
| **Usuarios Activos (WAU)** | 50 en beta | PostHog | Diaria |
| **Tasa Retención (D7)** | >40% | PostHog | Semanal |
| **Time to First Puzzle** | <10 min | PostHog | Semanal |
| **Puzzles Resolved** | Promedio 5/sesión | Base datos | Diaria |
| **NPS** | >40 | Typeform | Mensual |
| **Churn Rate** | <10% | Base datos | Mensual |

### 10.3 Métricas de Infraestructura

| Métrica | Target | Herramienta | Alerta |
|---------|--------|-------------|--------|
| **Uptime** | >99% | Prometheus | <99% |
| **Latencia API (p95)** | <3s | Prometheus | >5s |
| **Error Rate** | <1% | Sentry | >5% |
| **DB Query Time (p95)** | <500ms | Prometheus | >1s |
| **Cache Hit Rate** | >60% | Redis | <40% |
| **Celery Queue Length** | <100 | Prometheus | >500 |
| **Disk Usage** | <80% | Node exporter | >90% |

### 10.4 Dashboards Grafana

#### Dashboard 1: API Health
- Requests/min (por endpoint)
- Latency p50/p95/p99
- Error rate 5xx, 4xx
- Active connections

#### Dashboard 2: Database
- Connection pool usage
- Query duration (top 10 slow)
- Transaction rate
- Cache hit rate

#### Dashboard 3: Workers
- Celery tasks (pending/running/failed)
- Worker CPU/Memory
- Task duration por tipo
- Stockfish pool usage

#### Dashboard 4: Business Metrics
- New users (daily)
- Puzzles solved (daily)
- Bootstrap completions
- Active sessions

### 10.5 Alertas Críticas

**Configuración Alertmanager:**
```yaml
# alertmanager.yml
global:
  smtp_from: alerts@chesscoach.com
  smtp_smarthost: smtp.gmail.com:587
  smtp_auth_username: alerts@chesscoach.com
  smtp_auth_password: ${SMTP_PASSWORD}

route:
  receiver: 'team-slack'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10m
  repeat_interval: 12h
  routes:
    - match:
        severity: critical
      receiver: 'team-pagerduty'
      continue: true

receivers:
  - name: 'team-slack'
    slack_configs:
      - api_url: ${SLACK_WEBHOOK_URL}
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  - name: 'team-pagerduty'
    pagerduty_configs:
      - service_key: ${PAGERDUTY_KEY}
```

**Reglas de alerta:**
```yaml
# prometheus/alerts.yml
groups:
  - name: critical
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      - alert: ServiceDown
        expr: up{job="backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          description: "Backend service is down"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          description: "95th percentile latency is {{ $value }}s"
```

---

## RESUMEN EJECUTIVO

### Cronograma Consolidado

| Semana | Sprint | Objetivo Principal | Entregables | Riesgo |
|--------|--------|-------------------|-------------|--------|
| **1** | Sprint 0 | Setup infraestructura | CI/CD, Docker, Migraciones | 🟡 Bajo |
| **2** | Sprint 1 | Autenticación | Login/Register funcional | 🟠 Medio |
| **3** | Sprint 2 | Async processing | Bootstrap <5min, progreso UI | 🔴 Alto |
| **4** | Sprint 3 | Refactoring + Tests | Coverage >80%, repos separados | 🟡 Bajo |
| **5** | Sprint 4 | Features críticas | Repaso espaciado, progreso | 🟠 Medio |
| **6** | Sprint 5 | Performance | Caché Redis, optimización | 🟡 Bajo |
| **7** | Sprint 6 | Deploy staging | HTTPS, monitoreo, backups | 🟠 Medio |
| **8** | Sprint 7 | Beta testing | 50 usuarios, bugs resueltos | 🔴 Alto |

### Inversión Total Estimada

**Equipo (8 semanas):**
- Tech Lead: 320h × $100/h = $32,000
- Backend Senior: 320h × $80/h = $25,600
- Backend Mid: 320h × $60/h = $19,200
- Frontend Senior: 320h × $80/h = $25,600
- DevOps: 320h × $70/h = $22,400
- QA: 320h × $50/h = $16,000
- **Total Salarios:** $140,800

**Infraestructura:**
- VPS (DigitalOcean): $200/mes × 2 = $400
- Database backups (S3): $50/mes × 2 = $100
- CDN (Cloudflare): $20/mes × 2 = $40
- Monitoring (Grafana Cloud): $50/mes × 2 = $100
- Error tracking (Sentry): $26/mes × 2 = $52
- **Total Infra:** $692

**Servicios externos:**
- OpenAI API: $200 (testing)
- Domain + SSL: $50
- **Total Servicios:** $250

**TOTAL INVERSIÓN:** ~$141,742

### ROI Esperado

**Supuestos:**
- 50 usuarios beta → 20% conversión a paid ($9.99/mes)
- 10 usuarios Pro × $9.99 × 12 meses = $1,199/año
- Tiempo para recup inversión: ~10 años (no viable)

**Conclusión:** Proyecto requiere más usuarios o mayor pricing para viabilidad comercial. Alternativas:
1. Buscar funding (pre-seed $500K)
2. Freemium agresivo (1000+ usuarios gratuitos → 5% conversión)
3. B2B (licenciar a clubes/academias: $500/mes cada uno)

### Hitos Críticos

✅ **Semana 3:** Bootstrap async funcional (bloqueante para UX)  
✅ **Semana 4:** Tests >80% coverage (bloqueante para refactoring)  
✅ **Semana 6:** Deploy staging exitoso (bloqueante para beta)  
✅ **Semana 8:** 50 usuarios beta activos (validación product-market fit)

---

## ANEXOS

### A. ADRs (Architecture Decision Records)

#### ADR-001: PostgreSQL vs SQLite
**Decisión:** Migrar a PostgreSQL  
**Contexto:** SQLite no soporta concurrencia de writes necesaria para multi-tenant  
**Consecuencias:** +Complejidad setup, +Costo hosting, +Performance, +Confiabilidad

#### ADR-002: Celery vs FastAPI BackgroundTasks
**Decisión:** Usar Celery con Redis  
**Contexto:** BackgroundTasks no persiste estado, no soporta retry  
**Consecuencias:** +Complejidad, +Infraestructura (Redis), +Robustez, +Observabilidad

#### ADR-003: Next.js App Router vs Pages Router
**Decisión:** Mantener App Router  
**Contexto:** Ya implementado, mejor para SSR, futuro de Next.js  
**Consecuencias:** API más nueva (menos recursos), mejor performance

### B. Glossario

- **SP:** Story Points (unidad estimación)
- **P0/P1/P2:** Prioridad (0=crítico, 1=importante, 2=deseable)
- **WAU:** Weekly Active Users
- **NPS:** Net Promoter Score
- **ADR:** Architecture Decision Record
- **SRP:** Single Responsibility Principle
- **DRY:** Don't Repeat Yourself

### C. Comandos Útiles

```bash
# Development
make venv              # Setup virtual env
make api               # Run backend
make web               # Run frontend
docker-compose up -d   # Start services

# Testing
pytest tests/ -v                    # Backend tests
npm run test                        # Frontend tests
npx playwright test                 # E2E tests

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build
./scripts/backup_db.sh
ssh user@server "cd /opt/chess_coach && git pull"

# Monitoring
docker logs chess_coach_api -f
docker stats
curl http://localhost:9090/metrics
```

---

**FIN DEL PLAN DE EJECUCIÓN**

**Preparado por:** Tech Lead  
**Fecha:** 12 de febrero de 2026  
**Próxima revisión:** Fin de cada sprint  
**Aprobación requerida:** Product Owner, CTO
