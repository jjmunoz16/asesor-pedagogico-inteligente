# Guía de Operación Local y Despliegue Gratuito — Asesor Pedagógico Inteligente

**Fase:** Fases 8 y 9 — Verificación y Despliegue (`ADR-006`)  
**Fecha:** 2026-11-16

---

## 1. Ejecución Local

### Backend (FastAPI + Python 3.12)
Desde `backend/`:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)
Desde `frontend/`:
```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
npm.cmd run dev
```
Abrir `http://127.0.0.1:5173/`.

### Pruebas automatizadas (`tests/`)
Desde la raíz del proyecto:
```powershell
.\backend\.venv\Scripts\python.exe -m pytest tests -v
```

---

## 2. Despliegue Web 100 % Gratis Sin Tarjeta (Neon + GitHub + Render)

*(Actualizado 2026-11-16: Hugging Face Spaces exige plan PRO de pago para Docker SDK; **Render Free Tier** ofrece Web Services Docker gratuitos sin tarjeta de crédito).*

Arquitectura Todo-en-Uno (1 sola URL pública HTTPS):
1. **Neon** (`neon.tech`) → Base de datos PostgreSQL gratuita (1 GB).
2. **GitHub** (`github.com`) → Repositorio público para evaluación (`jjmunoz16/asesor-pedagogico-inteligente`), excluyendo estrictamente `source-material/`, `.env` y bases `.db` vía `.gitignore`.
3. **Render** (`render.com`) → Web Service gratuito con nuestro `Dockerfile` Todo-en-Uno (sirve React + FastAPI juntos).

---

### Paso 1: Crear la Base de Datos en Neon y sincronizar tus 6 actividades
1. Entra a **https://neon.tech** e inicia sesión (con Google o GitHub).
2. Crea un proyecto gratuito (`asesor-pedagogico`) y copia el **Connection String** (`postgresql://...`).
3. Ejecuta en PowerShell desde `backend/` (o pásame la URL para ejecutarlo por ti):
```powershell
cd C:\Users\jvall\Downloads\ProyectoFInalProf1IA\backend
$env:DATABASE_URL="PEGA_AQUI_TU_CADENA_DE_NEON"
.\.venv\Scripts\python.exe sync_to_remote_db.py
```

---

### Paso 2: Subir el código a GitHub
1. Crea un repositorio en **https://github.com/new** (`asesor-pedagogico-inteligente`, público para evaluación docente o privado según necesidad).
2. Sube el proyecto verificando que `.gitignore` excluya estrictamente `source-material/`, `.env`, `.venv/`, `node_modules/` y `*.db`.

---

### Paso 3: Desplegar en Render (Web Service Free — sin tarjeta)
1. Entra a **https://render.com** e inicia sesión con **GitHub** (no pide tarjeta).
2. Haz clic en **New +** → **Web Service** → conecta tu repositorio privado `asesor-pedagogico-inteligente`.
   *(Alternativa: **New +** → **Blueprint**, y Render leerá automáticamente `render.yaml`).*
3. Verifica la configuración:
   - **Language / Runtime:** `Docker`
   - **Instance Type:** **Free (\$0/month)**
4. En **Environment Variables**, agrega:
   - `DATABASE_URL` = tu cadena de Neon (`postgresql://...`)
   - `JWT_SECRET_KEY` = una cadena aleatoria larga (ej. 32+ caracteres)
   - `AI_PROVIDER` = `gemini` *(o `deterministic` si no pondrás API key)*
   - `GEMINI_API_KEY` = tu clave gratuita de Google AI Studio *(opcional)*
   - `SANDBOX_MODE` = `static_only`
   - `PUBLIC_DEMO_MODE` = `false` *(exige inicio de sesión JWT + RBAC en producción)*
5. Haz clic en **Deploy Web Service**.
6. Cuando el estado pase a **Live**, Render te dará tu URL pública `https://asesor-pedagogico-inteligente.onrender.com`.

> **Nota sobre suspensión en Render Free:** tras 15 minutos sin visitas, Render suspende el contenedor y tarda ~30–50 segundos en despertar en la primera carga. Para la sustentación, basta abrir el enlace 2 minutos antes de presentar (o usar un monitor gratuito como UptimeRobot cada 10 min apuntando a `/api/v1/health`).
