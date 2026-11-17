"""
Sincroniza localmente las 6 actividades reales de source-material/ y sus evaluaciones
base hacia la base de datos remota (ej. Neon PostgreSQL) sin subir archivos privados a Git.

Uso:
  $env:DATABASE_URL="postgresql://usuario:clave@host.neon.tech/neondb?sslmode=require"
  .\.venv\Scripts\python.exe sync_to_remote_db.py
"""

import asyncio
import os
import sys
from pathlib import Path

from sqlmodel import Session, select

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.models import Evaluation, Submission, User, UserRole  # noqa: E402
from app.db.seed import run_seed  # noqa: E402
from app.db.session import build_engine, init_db  # noqa: E402
from app.services.evaluation_service import run_submission_evaluation  # noqa: E402


async def sync() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "Define primero la variable de entorno DATABASE_URL con tu cadena de conexión de Neon."
        )

    remote_engine = build_engine(db_url)
    init_db(remote_engine)

    with Session(remote_engine) as session:
        run_seed(session)
        teacher = session.exec(select(User).where(User.role == UserRole.TEACHER)).first()
        subs = session.exec(select(Submission).order_by(Submission.id)).all()
        created = 0
        for sub in subs:
            existing = session.exec(
                select(Evaluation).where(Evaluation.submission_id == sub.id)
            ).first()
            if not existing and teacher:
                ev = await run_submission_evaluation(
                    session, sub.id, teacher, provider_override="deterministic"
                )
                created += 1
                print(
                    f"[OK] Actividad sub={sub.id} evaluada -> eval={ev.id} (nota={ev.calculated_score_ai})"
                )
        print(f"Sincronización finalizada. Entregas={len(subs)}, nuevas evaluaciones={created}.")


if __name__ == "__main__":
    asyncio.run(sync())
