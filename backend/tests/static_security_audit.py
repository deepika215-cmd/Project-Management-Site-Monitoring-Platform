"""
Static security audit for BuildTrack backend/frontend source files.
Run from the backend folder:
    python tests/static_security_audit.py
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

BACKEND = Path(__file__).resolve().parents[1]
PROJECT = BACKEND.parent
checks: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + " - " + name + (f" :: {detail}" if detail else ""))


def read(path: str) -> str:
    p = PROJECT / path
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

main_py = read("backend/app/main.py")
auth_py = read("backend/app/api/auth.py")
user_schema = read("backend/app/schemas/user_schema.py")
document_py = read("backend/app/api/document.py")
config_py = read("backend/app/core/config.py")
api_files = list((BACKEND / "app" / "api").glob("*.py"))
frontend_files = list((PROJECT / "frontend" / "src").rglob("*.ts")) if (PROJECT / "frontend" / "src").exists() else []

check("CORS is not wildcard", "allow_origins=[\n        \"http://localhost:4200\"" in main_py or "allow_origins=[\"http://localhost:4200\"]" in main_py)
check("Security headers middleware exists", "X-Content-Type-Options" in main_py and "X-Frame-Options" in main_py)
check("Public ADMIN registration blocked", "Public registration as ADMIN is not allowed" in auth_py)
check("Password strength validation exists", all(x in user_schema for x in ["uppercase", "lowercase", "number", "special character"]))
check("Forgot password response is enumeration-safe", "If an account with that email exists" in auth_py)
check("Reset link exposure is off by default", "BUILDTRACK_EXPOSE_RESET_LINK" in config_py and "False" in config_py)
check("Login rate limiting exists", "LOGIN_RATE_LIMIT_MAX_FAILURES" in auth_py and "429" in auth_py)
check("Document upload has size limit", "MAX_UPLOAD_SIZE_BYTES" in document_py and "413" in document_py)
check("Document upload has file type allowlist", "ALLOWED_DOCUMENT_EXTENSIONS" in document_py and "Unsupported file type" in document_py)
check("Documents endpoints require RBAC", "DOCUMENT_READ_ROLES" in document_py and "DOCUMENT_WRITE_ROLES" in document_py)
check("Milestones endpoints require RBAC", "MILESTONE_READ_ROLES" in read("backend/app/api/milestone.py"))
check("Reports endpoints require RBAC", "REPORT_READ_ROLES" in read("backend/app/api/report.py"))

bad_patterns = []
for path in list((BACKEND / "app").rglob("*.py")) + frontend_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = str(path.relative_to(PROJECT))
    for pattern in ["eval(", "exec(", "shell=True", "bypassSecurityTrustHtml", "innerHTML"]:
        if pattern in text:
            bad_patterns.append(f"{rel}: {pattern}")
check("No obvious dangerous code patterns", not bad_patterns, "; ".join(bad_patterns[:10]))

failed = [c for c in checks if not c[1]]
print("\nSUMMARY: %s/%s checks passed" % (len(checks) - len(failed), len(checks)))
sys.exit(1 if failed else 0)
