# Backend comparison and selective merge

Compared:
- User backend: 95b44ced-2588-40e7-816f-bcb00fbeb829.zip
- Friend backend: e013769b-30e7-49d6-9ade-07e2722abe99.zip

## Comparison result
The user's backend is the more complete base. It contains additional project scheduling,
procurement/vendor/PO/invoice functionality, report preview/export support, frontend-oriented
authentication behavior, and other fixes that are not present in the friend's backend.

The friend's backend was therefore NOT copied wholesale.

## Useful functionality merged
The following useful single-record read endpoints found in the friend's implementation were
added to the user's backend while preserving the user's existing response shape and RBAC:

- GET /budgets/{budget_id}
- GET /budget-categories/{category_id}
- GET /cost-estimates/{estimate_id}
- GET /expenses/{expense_id}

For budgets, the new endpoint returns the complete project budget plan containing the requested
budget row, so it remains compatible with the existing frontend plan structure.

## Intentionally preserved from the user's backend
- Project scheduling APIs/models
- JSON login/frontend authentication integration
- Vendors and procurement requests/items
- Purchase orders/items and invoices
- Report preview, PDF export and Excel export
- Existing Module 11 project summary APIs
- Existing role-based access control
- Lowercase app/models/budget.py (portable on Linux)
- reportlab/openpyxl dependencies

## Validation
All Python source files in the updated backend were compiled with py_compile.
