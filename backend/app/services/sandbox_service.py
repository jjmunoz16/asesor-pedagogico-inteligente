"""Sandbox dual para verificación técnica objetiva de código sin riesgo para el host."""

import ast
import json
import os
import subprocess
import sys
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


RISKY_CALLS = {"eval", "exec", "compile", "__import__"}
RISKY_MODULES = {"subprocess", "os", "socket", "ctypes", "shutil"}


class _HTMLCheckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag.lower())


def analyze_python_ast(filename: str, source: str) -> dict[str, Any]:
    """Analiza sintaxis y estructura Python usando ast.parse sin ejecutar código."""
    findings: list[str] = []
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return {
            "file": filename,
            "language": "python",
            "syntax_valid": False,
            "error": f"SyntaxError línea {exc.lineno}: {exc.msg}",
            "functions": 0,
            "classes": 0,
            "has_unittest": False,
            "findings": [f"Error de sintaxis en línea {exc.lineno}: {exc.msg}"],
        }

    functions = 0
    classes = 0
    has_unittest = False

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1
        elif isinstance(node, ast.ClassDef):
            classes += 1
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root == "unittest":
                    has_unittest = True
                if root in RISKY_MODULES:
                    findings.append(f"Importación sensible detectada: '{alias.name}'")
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root == "unittest":
                has_unittest = True
            if root in RISKY_MODULES:
                findings.append(f"Importación sensible detectada: 'from {node.module}'")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in RISKY_CALLS:
                findings.append(f"Llamada dinámica riesgosa detectada: '{node.func.id}()'")
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"}:
                findings.append(f"Llamada a sistema detectada: '.{node.func.attr}()'")

    return {
        "file": filename,
        "language": "python",
        "syntax_valid": True,
        "functions": functions,
        "classes": classes,
        "has_unittest": has_unittest,
        "findings": findings,
    }


def analyze_json_file(filename: str, source: str) -> dict[str, Any]:
    try:
        json.loads(source)
        return {"file": filename, "language": "json", "syntax_valid": True, "findings": []}
    except json.JSONDecodeError as exc:
        return {
            "file": filename,
            "language": "json",
            "syntax_valid": False,
            "findings": [f"JSON inválido en línea {exc.lineno}: {exc.msg}"],
        }


def analyze_html_file(filename: str, source: str) -> dict[str, Any]:
    parser = _HTMLCheckParser()
    try:
        parser.feed(source)
        return {
            "file": filename,
            "language": "html",
            "syntax_valid": len(parser.tags) > 0,
            "tags_count": len(parser.tags),
            "findings": [] if parser.tags else ["Archivo HTML sin etiquetas reconocibles."],
        }
    except Exception as exc:
        return {
            "file": filename,
            "language": "html",
            "syntax_valid": False,
            "findings": [f"Error parseando HTML: {exc}"],
        }


def run_sandbox_checks(
    files: list[tuple[str, str]],
    mode: str = "static_only",
    timeout_seconds: int = 5,
) -> dict[str, Any]:
    """
    Ejecuta verificación técnica objetiva sobre archivos de código.

    Args:
        files: lista de (nombre_archivo, contenido_texto).
        mode: 'static_only' (sin ejecución) o 'isolated_subprocess' (pruebas aisladas sin secretos).
    """
    started = time.perf_counter()
    checked: list[dict[str, Any]] = []
    findings: list[str] = []
    syntax_all_valid = True

    py_files: list[tuple[str, str]] = []
    for name, content in files:
        ext = Path(name).suffix.lower()
        if ext == ".py":
            res = analyze_python_ast(name, content)
            checked.append(res)
            py_files.append((name, content))
            if not res["syntax_valid"]:
                syntax_all_valid = False
            findings.extend(f"[{name}] {f}" for f in res["findings"])
        elif ext == ".json":
            res = analyze_json_file(name, content)
            checked.append(res)
            if not res["syntax_valid"]:
                syntax_all_valid = False
            findings.extend(f"[{name}] {f}" for f in res["findings"])
        elif ext in {".html", ".htm"}:
            res = analyze_html_file(name, content)
            checked.append(res)
            if not res["syntax_valid"]:
                syntax_all_valid = False
            findings.extend(f"[{name}] {f}" for f in res["findings"])

    tests_passed: int | None = None
    tests_total: int | None = None

    if mode == "isolated_subprocess" and py_files and syntax_all_valid:
        test_candidates = [name for name, _ in py_files if Path(name).name.startswith("test_")]
        if test_candidates:
            tests_passed, tests_total, exec_note = _run_isolated_unittest(
                py_files, timeout_seconds=timeout_seconds
            )
            if exec_note:
                findings.append(exec_note)

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {
        "sandbox_mode": mode,
        "syntax_valid": syntax_all_valid,
        "files_checked": checked,
        "static_findings": findings,
        "unit_tests_passed": tests_passed,
        "unit_tests_total": tests_total,
        "execution_time_ms": elapsed_ms,
    }


def _run_isolated_unittest(
    py_files: list[tuple[str, str]], timeout_seconds: int
) -> tuple[int | None, int | None, str]:
    """Ejecuta unittest en un directorio temporal desechable sin variables sensibles."""
    with tempfile.TemporaryDirectory(prefix="sandbox_eval_") as tmpdir:
        tmp_path = Path(tmpdir)
        for rel_name, content in py_files:
            safe_name = Path(rel_name).name
            (tmp_path / safe_name).write_text(content, encoding="utf-8")

        # Bloqueo explícito de socket/red mediante sitecustomize en el directorio temporal
        guard = (
            "import socket\n"
            "def _blocked(*args, **kwargs):\n"
            "    raise RuntimeError('Acceso a red bloqueado en sandbox')\n"
            "socket.socket = _blocked\n"
            "socket.create_connection = _blocked\n"
        )
        (tmp_path / "sitecustomize.py").write_text(guard, encoding="utf-8")

        clean_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "PYTHONPATH": str(tmp_path),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(tmp_path), "-v"],
                cwd=str(tmp_path),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            output = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ran = None
            for line in output.splitlines():
                if line.startswith("Ran "):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        ran = int(parts[1])
            if proc.returncode == 0 and ran is not None:
                return ran, ran, f"Pruebas unitarias ejecutadas en sandbox aislado: {ran}/{ran} OK."
            return 0, ran, f"Pruebas unitarias finalizaron con código {proc.returncode}."
        except subprocess.TimeoutExpired:
            return 0, None, f"Ejecución abortada por timeout ({timeout_seconds}s) en sandbox."
        except Exception as exc:
            return None, None, f"Error en runner aislado: {exc}"
