from fastapi import FastAPI

app = FastAPI(
    title="Finance Tracker API",
    description="API de seguimiento financiero con arquitectura en capas (FastAPI + PostgreSQL)",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Verifica que el servidor esté activo y respondiendo correctamente."""
    return {"status": "ok"}
