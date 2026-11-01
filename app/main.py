from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

app = FastAPI(
    title="Finance Tracker API",
    description="API de seguimiento financiero con arquitectura en capas (FastAPI + PostgreSQL)",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Verifica que el servidor y la conexión a PostgreSQL estén activos."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}

