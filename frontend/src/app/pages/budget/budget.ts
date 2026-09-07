import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { catchError, finalize, forkJoin, Observable, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

type BudgetTab = 'dashboard' | 'planning' | 'estimates' | 'expenses' | 'monitoring' | 'report' | 'categories';

interface CostCategory {
  key: string;
  label: string;
}

@Component({
  selector: 'app-budget',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './budget.html',
  styleUrl: './budget.css'
})
export class Budget implements OnInit {
  readonly categories: CostCategory[] = [
    { key: 'LABOR', label: 'Labor Cost' },
    { key: 'MATERIAL', label: 'Material Cost' },
    { key: 'EQUIPMENT', label: 'Equipment Cost' },
    { key: 'TRANSPORTATION', label: 'Transportation Cost' },
    { key: 'MAINTENANCE', label: 'Maintenance Cost' },
    { key: 'ADMINISTRATIVE', label: 'Administrative Cost' }
  ];

  activeTab: BudgetTab = 'dashboard';
  loading = true;
  saving = false;
  deletingId: string | null = null;
  error = '';
  message = '';
  backendReady = true;
  role = '';
  projects: any[] = [];
  selectedProjectId: number | null = null;
  budgetPlan: any = null;
  estimates: any[] = [];
  expenses: any[] = [];
  summary: any = null;

  planForm = this.emptyPlanForm();
  estimateForm = { category: 'LABOR', activity: '', estimated_amount: 0, notes: '' };
  expenseForm = { category: 'LABOR', description: '', amount: 0, expense_date: '', reference: '', source_module: 'MANUAL' };

  private loadVersion = 0;

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.role = this.currentRole();
    this.loadProjects();
  }

  get canEdit(): boolean { return this.role === 'ADMIN' || this.role === 'PROJECT_MANAGER'; }
  get canView(): boolean { return ['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CLIENT'].includes(this.role); }
  get formTotal(): number { return this.sumPlan(); }

  loadProjects(): void {
    const version = ++this.loadVersion;
    this.loading = true;
    this.error = '';
    this.backendReady = true;

    this.api.getProjects().pipe(
      timeout(9000),
      catchError((err) => {
        this.error = this.detail(err, 'Unable to load projects. Please check whether the backend is running.');
        return of([] as any[]);
      }),
      finalize(() => this.cdr.detectChanges())
    ).subscribe((projects) => {
      if (version !== this.loadVersion) return;
      this.projects = this.list(projects);

      if (this.selectedProjectId && !this.projects.some((p) => Number(p.id) === Number(this.selectedProjectId))) {
        this.selectedProjectId = null;
      }

      if (!this.selectedProjectId && this.projects.length) {
        this.selectedProjectId = Number(this.projects[0].id);
      }

      if (this.selectedProjectId) {
        this.loadProjectFinancials();
      } else {
        this.resetFinancialData();
      }
    });
  }

  onProjectChange(): void {
    this.error = '';
    this.message = '';
    if (this.selectedProjectId) this.loadProjectFinancials();
    else this.resetFinancialData();
  }

  refresh(): void {
    if (this.selectedProjectId) this.loadProjectFinancials();
    else this.loadProjects();
  }

  loadProjectFinancials(): void {
    if (!this.selectedProjectId) {
      this.resetFinancialData();
      return;
    }

    const version = ++this.loadVersion;
    const id = Number(this.selectedProjectId);
    this.loading = true;
    this.error = '';
    this.message = '';
    this.backendReady = true;

    forkJoin({
      plan: this.safe(this.api.getBudgetPlan(id), null),
      estimates: this.safe(this.api.getCostEstimates(id), [] as any[]),
      expenses: this.safe(this.api.getExpenses(id), [] as any[]),
      summary: this.safe(this.api.getBudgetSummary(id), null)
    }).pipe(
      finalize(() => {
        if (version === this.loadVersion) this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe((data) => {
      if (version !== this.loadVersion) return;
      this.budgetPlan = data.plan;
      this.estimates = this.list(data.estimates);
      this.expenses = this.list(data.expenses);
      this.summary = data.summary;
      this.planForm = this.toPlanForm(this.budgetPlan);
    });
  }

  saveBudgetPlan(): void {
    if (!this.canEdit || !this.selectedProjectId || this.saving) return;
    const allocations = this.categories.map((c) => ({ category: c.key, amount: this.num(this.planForm[c.key]) }));
    const total = allocations.reduce((sum, x) => sum + x.amount, 0);

    if (total <= 0) {
      this.error = 'Enter at least one category allocation.';
      return;
    }

    this.saving = true;
    this.error = '';
    this.message = '';

    const payload = {
      project_id: Number(this.selectedProjectId),
      total_budget: total,
      category_allocations: allocations
    };

    const request = this.budgetPlan?.id
      ? this.api.updateBudgetPlan(Number(this.budgetPlan.id), payload)
      : this.api.createBudgetPlan(payload);

    request.pipe(
      timeout(10000),
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (saved) => {
        const plan = this.normalizePlan(saved, payload);
        this.budgetPlan = plan;
        this.planForm = this.toPlanForm(plan);
        this.summary = { ...(this.summary || {}), total_budget: total, remaining_budget: total - this.amountSpent };
        this.message = 'Budget plan saved.';
        this.loadProjectFinancials();
      },
      error: (e) => {
        this.error = this.detail(e, 'Unable to save the budget plan. Please check the backend terminal for the exact error.');
      }
    });
  }

  addEstimate(): void {
    if (!this.canEdit || !this.selectedProjectId || this.saving) return;
    if (!this.estimateForm.activity.trim() || this.num(this.estimateForm.estimated_amount) <= 0) {
      this.error = 'Activity and a positive estimated amount are required.';
      return;
    }

    this.saving = true;
    this.error = '';
    this.message = '';

    const payload = {
      category: this.estimateForm.category,
      activity: this.estimateForm.activity.trim(),
      item_name: this.estimateForm.activity.trim(),
      estimated_amount: this.num(this.estimateForm.estimated_amount),
      notes: this.estimateForm.notes?.trim() || '',
      description: this.estimateForm.notes?.trim() || '',
      project_id: Number(this.selectedProjectId)
    };

    this.api.createCostEstimate(payload).pipe(
      timeout(10000),
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (saved) => {
        this.estimates = [...this.estimates, saved || payload];
        this.estimateForm = { category: 'LABOR', activity: '', estimated_amount: 0, notes: '' };
        this.message = 'Cost estimate added.';
        this.loadProjectFinancials();
      },
      error: (e) => {
        this.error = this.detail(e, 'Unable to save the cost estimate.');
      }
    });
  }

  deleteEstimate(item: any): void {
    if (!this.canEdit || !item?.id || !confirm('Delete this cost estimate?')) return;
    this.deletingId = `estimate-${item.id}`;
    this.api.deleteCostEstimate(Number(item.id)).pipe(
      timeout(10000),
      finalize(() => {
        this.deletingId = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.estimates = this.estimates.filter((x) => Number(x.id) !== Number(item.id));
        this.message = 'Cost estimate deleted.';
        this.loadProjectFinancials();
      },
      error: (e) => this.error = this.detail(e, 'Unable to delete the estimate.')
    });
  }

  addExpense(): void {
    if (!this.canEdit || !this.selectedProjectId || this.saving) return;
    if (!this.expenseForm.description.trim() || this.num(this.expenseForm.amount) <= 0 || !this.expenseForm.expense_date) {
      this.error = 'Description, expense date and a positive amount are required.';
      return;
    }

    this.saving = true;
    this.error = '';
    this.message = '';

    const payload = {
      category: this.expenseForm.category,
      description: this.expenseForm.description.trim(),
      expense_name: this.expenseForm.description.trim(),
      amount: this.num(this.expenseForm.amount),
      expense_date: this.expenseForm.expense_date,
      reference: this.expenseForm.reference?.trim() || '',
      source_module: this.expenseForm.source_module || 'MANUAL',
      project_id: Number(this.selectedProjectId)
    };

    this.api.createExpense(payload).pipe(
      timeout(10000),
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (saved) => {
        this.expenses = [...this.expenses, saved || payload];
        this.expenseForm = { category: 'LABOR', description: '', amount: 0, expense_date: '', reference: '', source_module: 'MANUAL' };
        this.message = 'Expense recorded.';
        this.loadProjectFinancials();
      },
      error: (e) => {
        this.error = this.detail(e, 'Unable to record the expense.');
      }
    });
  }

  deleteExpense(item: any): void {
    if (!this.canEdit || !item?.id || !confirm('Delete this expense?')) return;
    this.deletingId = `expense-${item.id}`;
    this.api.deleteExpense(Number(item.id)).pipe(
      timeout(10000),
      finalize(() => {
        this.deletingId = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.expenses = this.expenses.filter((x) => Number(x.id) !== Number(item.id));
        this.message = 'Expense deleted.';
        this.loadProjectFinancials();
      },
      error: (e) => this.error = this.detail(e, 'Unable to delete the expense.')
    });
  }

  selectTab(tab: BudgetTab): void { this.activeTab = tab; this.error = ''; this.message = ''; }

  get totalBudget(): number { return this.firstNumber(this.summary?.total_budget, this.budgetPlan?.total_budget, this.sumPlan()); }
  get estimatedCost(): number { return this.firstNumber(this.summary?.estimated_cost, this.summary?.total_estimated, this.sum(this.estimates, 'estimated_amount')); }
  get amountSpent(): number { return this.firstNumber(this.summary?.amount_spent, this.summary?.actual_cost, this.summary?.total_actual, this.sum(this.expenses, 'amount')); }
  get remainingBudget(): number { const explicit = this.numberOrNull(this.summary?.remaining_budget); return explicit ?? Math.max(0, this.totalBudget - this.amountSpent); }
  get utilization(): number { const explicit = this.numberOrNull(this.summary?.utilization_percentage); return explicit ?? (this.totalBudget > 0 ? Math.round((this.amountSpent / this.totalBudget) * 1000) / 10 : 0); }

  categoryPlanned(key: string): number {
    const row = this.findCategory(this.budgetPlan?.category_allocations || this.budgetPlan?.allocations || [], key);
    return this.firstNumber(row?.amount, row?.allocated_amount, this.planForm[key]);
  }
  categoryEstimated(key: string): number { return this.estimates.filter((x) => this.key(x.category || x.category_name) === key).reduce((s, x) => s + this.num(x.estimated_amount ?? x.amount), 0); }
  categorySpent(key: string): number { return this.expenses.filter((x) => this.key(x.category || x.category_name) === key).reduce((s, x) => s + this.num(x.amount ?? x.actual_amount), 0); }
  categoryRemaining(key: string): number { return Math.max(0, this.categoryPlanned(key) - this.categorySpent(key)); }
  categoryUtilization(key: string): number { const p = this.categoryPlanned(key); return p > 0 ? Math.min(100, Math.round((this.categorySpent(key) / p) * 1000) / 10) : 0; }

  money(value: any): string { const n = this.num(value); return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n); }
  projectName(): string { const p = this.projects.find((x) => Number(x.id) === Number(this.selectedProjectId)); return p?.project_name || p?.name || 'Selected project'; }
  categoryLabel(value: any): string { const key = this.key(value); return this.categories.find((c) => c.key === key)?.label || String(value || 'Uncategorized'); }

  private safe<T>(request: Observable<T>, fallback: T): Observable<T> {
    return request.pipe(
      timeout(9000),
      catchError((err) => {
        this.markBackendUnavailable(err);
        return of(fallback as T);
      })
    );
  }

  private list(value: any): any[] {
    if (Array.isArray(value)) return value;
    if (Array.isArray(value?.data)) return value.data;
    if (Array.isArray(value?.items)) return value.items;
    if (Array.isArray(value?.results)) return value.results;
    return [];
  }

  private normalizePlan(saved: any, payload: any): any {
    if (saved && typeof saved === 'object') {
      return {
        ...saved,
        project_id: saved.project_id ?? payload.project_id,
        total_budget: this.num(saved.total_budget ?? payload.total_budget),
        category_allocations: Array.isArray(saved.category_allocations) ? saved.category_allocations : payload.category_allocations,
        allocations: Array.isArray(saved.allocations) ? saved.allocations : (Array.isArray(saved.category_allocations) ? saved.category_allocations : payload.category_allocations)
      };
    }
    return { id: this.budgetPlan?.id, ...payload, allocations: payload.category_allocations };
  }

  private emptyPlanForm(): any { return { LABOR: 0, MATERIAL: 0, EQUIPMENT: 0, TRANSPORTATION: 0, MAINTENANCE: 0, ADMINISTRATIVE: 0 }; }
  private toPlanForm(plan: any): any {
    const form = this.emptyPlanForm();
    const allocations = plan?.category_allocations || plan?.allocations || [];
    if (Array.isArray(allocations)) {
      allocations.forEach((row: any) => {
        const key = this.key(row.category || row.category_name || row.name);
        if (key in form) form[key] = this.num(row.amount ?? row.allocated_amount ?? row.value);
      });
    } else {
      this.categories.forEach((c) => { if (plan?.[c.key.toLowerCase()] != null) form[c.key] = this.num(plan[c.key.toLowerCase()]); });
    }
    return form;
  }
  private sumPlan(): number { return this.categories.reduce((s, c) => s + this.num(this.planForm[c.key]), 0); }
  private sum(rows: any[], field: string): number { return (rows || []).reduce((s, row) => s + this.num(row?.[field]), 0); }
  private num(v: any): number { const n = Number(v); return Number.isFinite(n) ? n : 0; }
  private numberOrNull(v: any): number | null { if (v === '' || v == null) return null; const n = Number(v); return Number.isFinite(n) ? n : null; }
  private firstNumber(...values: any[]): number { for (const v of values) { const n = this.numberOrNull(v); if (n != null) return n; } return 0; }
  private key(v: any): string { return String(v || '').trim().toUpperCase().replace(/\s+COST$/, '').replace(/\s+/g, '_'); }
  private findCategory(rows: any[], key: string): any { return (rows || []).find((x: any) => this.key(x.category || x.category_name || x.name) === key); }
  private currentRole(): string { try { return String(JSON.parse(localStorage.getItem('currentUser') || '{}')?.role || '').toUpperCase(); } catch { return ''; } }
  private markBackendUnavailable(err: any): void { if ([0, 404, 405, 501].includes(Number(err?.status))) this.backendReady = false; }
  private detail(err: any, fallback: string): string {
    const detail = err?.error?.detail ?? err?.error?.message ?? err?.message;
    if (Array.isArray(detail)) return detail.map((x: any) => x?.msg || JSON.stringify(x)).join(', ');
    return detail || fallback;
  }
  private resetFinancialData(): void {
    this.budgetPlan = null;
    this.estimates = [];
    this.expenses = [];
    this.summary = null;
    this.planForm = this.emptyPlanForm();
    this.loading = false;
    this.cdr.detectChanges();
  }
}
