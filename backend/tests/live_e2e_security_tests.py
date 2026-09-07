"""
BuildTrack live E2E + security smoke tests.

Run this after starting the backend:
    cd backend
    python tests/live_e2e_security_tests.py

Optional:
    python tests/live_e2e_security_tests.py http://localhost:8000

This script uses only Python standard library modules.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")


def request(method: str, path: str, body: Any | None = None, token: str | None = None, expected: set[int] | None = None) -> tuple[int, Any, dict[str, str]]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return resp.status, parsed, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed, dict(exc.headers)


results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: Any = "") -> None:
    results.append((name, ok, str(detail)[:300]))
    print(("PASS" if ok else "FAIL") + " - " + name + (f" :: {str(detail)[:160]}" if detail else ""))


def login(email: str, password: str) -> str:
    status, data, _ = request("POST", "/auth/login-json", {"email": email, "password": password})
    check(f"login {email}", status == 200 and isinstance(data, dict) and bool(data.get("access_token")), status)
    return data.get("access_token", "") if isinstance(data, dict) else ""


def main() -> int:
    status, data, headers = request("GET", "/")
    check("backend root reachable", status == 200, status)
    check("security header X-Content-Type-Options", headers.get("X-Content-Type-Options") == "nosniff", headers)
    check("security header X-Frame-Options", headers.get("X-Frame-Options") == "DENY", headers)

    stamp = int(time.time())
    user_email = f"e2e_client_{stamp}@example.com"
    status, data, _ = request("POST", "/auth/register", {
        "name": "E2E Client",
        "email": user_email,
        "password": "Client@1234",
        "phone": "9999999999",
        "role": "CLIENT",
    })
    check("public client registration", status in {200, 201}, data)

    status, data, _ = request("POST", "/auth/register", {
        "name": "Bad Admin",
        "email": f"bad_admin_{stamp}@example.com",
        "password": "Admin@1234",
        "phone": "9999999999",
        "role": "ADMIN",
    })
    check("public ADMIN registration blocked", status == 403, data)

    status, data, _ = request("POST", "/auth/register", {
        "name": "Weak Password User",
        "email": f"weak_{stamp}@example.com",
        "password": "password",
        "phone": "9999999999",
        "role": "CLIENT",
    })
    check("weak password rejected", status == 422, data)

    for protected_path in ["/documents/", "/milestones/", "/report/", "/projects/1/tracking", "/projects/1/budget-cost"]:
        status, data, _ = request("GET", protected_path)
        check(f"unauthenticated request blocked: {protected_path}", status in {401, 403}, status)

    for i in range(6):
        status, data, _ = request("POST", "/auth/login-json", {"email": f"brute_{stamp}@example.com", "password": "wrong"})
    check("login brute-force rate limit triggers", status == 429, status)

    admin_token = login("admin@buildtrack.com", "Admin@123")
    worker_token = login("worker@buildtrack.com", "Worker@123")

    status, users, _ = request("GET", "/users/", token=admin_token)
    check("admin can list users", status == 200 and isinstance(users, list), status)
    manager_id = next((u.get("id") for u in users if str(u.get("role", "")).upper() == "PROJECT_MANAGER"), None) if isinstance(users, list) else None
    check("project manager user exists", bool(manager_id), users)

    status, project, _ = request("POST", "/projects/", {
        "project_name": f"E2E Security Project {stamp}",
        "project_code": f"E2E-{stamp}",
        "project_category": "Commercial",
        "description": "Created by live E2E security test script.",
        "location": "Chennai",
        "start_date": "2026-09-01",
        "end_date": "2027-01-01",
        "budget": 1000000,
        "priority": "High",
        "status": "Planning",
        "manager_id": manager_id,
    }, token=admin_token)
    check("admin can create project", status in {200, 201}, project)
    project_id = project.get("id") if isinstance(project, dict) else None

    status, worker, _ = request("POST", "/workers/", {
        "name": f"E2E Worker {stamp}",
        "role": "Worker",
        "phone": "9876543210",
        "email": f"e2e_worker_{stamp}@example.com",
        "category": "Skilled Worker",
        "status": "Active",
    }, token=admin_token)
    check("admin can create worker", status in {200, 201}, worker)

    status, resource, _ = request("POST", "/resources/", {
        "name": f"E2E Crane {stamp}",
        "type": "Equipment",
        "quantity": 1,
        "status": "Available",
        "project_id": project_id,
    }, token=admin_token)
    check("admin can create resource", status in {200, 201}, resource)

    status, budget, _ = request("POST", "/budgets/", {
        "project_id": project_id,
        "total_budget": 250000,
        "category_allocations": [{"category": "Labor Cost", "amount": 250000}],
    }, token=admin_token)
    check("admin can save budget plan", status in {200, 201}, budget)

    for path in ["/projects/", "/workers/", "/resources/", "/notification/my", "/analytics/", "/report/", "/milestones/", "/documents/"]:
        status, data, _ = request("GET", path, token=admin_token)
        check(f"admin can read {path}", status == 200, status)

    status, data, _ = request("POST", "/projects/", {
        "project_name": "Worker Should Not Create",
        "project_code": f"BAD-{stamp}",
        "project_category": "Commercial",
        "description": "RBAC negative test.",
        "location": "Chennai",
        "start_date": "2026-09-01",
        "end_date": "2027-01-01",
        "budget": 1000,
        "priority": "Low",
        "status": "Planning",
        "manager_id": manager_id,
    }, token=worker_token)
    check("worker blocked from creating project", status == 403, data)

    status, data, _ = request("GET", "/users/", token=worker_token)
    check("worker blocked from user management", status == 403, data)

    status, data, _ = request("GET", "/report/", token=worker_token)
    check("worker blocked from reports list", status == 403, data)

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print("\nSUMMARY: %s/%s checks passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
