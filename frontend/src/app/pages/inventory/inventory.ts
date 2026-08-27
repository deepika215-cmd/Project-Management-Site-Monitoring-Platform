import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

interface InventoryForm {
  material_name: string;
  category: string;
  quantity: number;
  unit: string;
  supplier: string;
  status: string;
}

interface MaterialRequestForm {
  category: string;
  material_name: string;
  quantity: number;
  supplier: string;
  project_id: number;
}

@Component({
  selector: 'app-inventory',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './inventory.html',
  styleUrl: './inventory.css'
})
export class Inventory implements OnInit {
  readonly categories = [
    'Cement',
    'Steel',
    'Bricks',
    'Sand',
    'Concrete',
    'Electrical Materials',
    'Plumbing Materials'
  ];

  readonly categoryMaterials: Record<string, string[]> = {
    Cement: ['Cement'],
    Steel: ['Steel', 'Rebar', 'TMT Bars'],
    Bricks: ['Bricks', 'Blocks'],
    Sand: ['Sand', 'M-Sand'],
    Concrete: ['Concrete', 'Ready Mix Concrete'],
    'Electrical Materials': ['Electrical Materials', 'Cables', 'Wires', 'Switches'],
    'Plumbing Materials': ['Plumbing Materials', 'Pipes', 'Fittings']
  };

  items: any[] = [];
  filtered: any[] = [];
  requests: any[] = [];
  projects: any[] = [];

  search = '';
  categoryFilter = 'All';
  loading = false;
  loadingRequests = false;
  saving = false;
  error = '';

  showForm = false;
  showRequestForm = false;
  editingId: number | null = null;

  form: InventoryForm = this.emptyForm();
  requestForm: MaterialRequestForm = this.emptyRequestForm();

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.load();
    this.loadProjects();
    this.loadRequests();
  }

  private emptyForm(): InventoryForm {
    return {
      material_name: '',
      category: 'Cement',
      quantity: 0,
      unit: 'bags',
      supplier: '',
      status: 'Available'
    };
  }

  private emptyRequestForm(): MaterialRequestForm {
    return {
      category: 'Cement',
      material_name: 'Cement',
      quantity: 1,
      supplier: '',
      project_id: 0
    };
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getInventory().subscribe({
      next: (rows: any[]) => {
        this.items = Array.isArray(rows) ? rows : [];
        this.filter();
        this.loading = false;
      },
      error: (e: any) => {
        this.loading = false;
        this.error = e?.error?.detail || 'Unable to load inventory.';
      }
    });
  }

  loadProjects(): void {
    this.api.getProjects().subscribe({
      next: (rows: any[]) => this.projects = Array.isArray(rows) ? rows : [],
      error: () => this.projects = []
    });
  }

  loadRequests(): void {
    this.loadingRequests = true;
    this.api.getProcurements().subscribe({
      next: (rows: any[]) => {
        this.requests = Array.isArray(rows) ? rows : [];
        this.loadingRequests = false;
      },
      error: (_e: any) => {
        this.requests = [];
        this.loadingRequests = false;
      }
    });
  }

  filter(): void {
    const search = this.search.toLowerCase().trim();
    this.filtered = this.items.filter(item => {
      const name = String(item?.material_name || '').toLowerCase();
      const supplier = String(item?.supplier || '').toLowerCase();
      const category = this.getCategory(item).toLowerCase();
      const matchesSearch = !search || name.includes(search) || supplier.includes(search) || category.includes(search);
      const matchesCategory = this.categoryFilter === 'All' || this.getCategory(item) === this.categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }

  getCategory(item: any): string {
    const name = String(item?.material_name || '').toLowerCase();
    const match = this.categories.find(category => {
      const lowerCategory = category.toLowerCase();
      return name.startsWith(`${lowerCategory} -`) || name === lowerCategory || name.includes(lowerCategory);
    });
    if (match) return match;

    if (name.includes('rebar') || name.includes('tmt') || name.includes('steel')) return 'Steel';
    if (name.includes('brick') || name.includes('block')) return 'Bricks';
    if (name.includes('sand')) return 'Sand';
    if (name.includes('concrete')) return 'Concrete';
    if (name.includes('cable') || name.includes('wire') || name.includes('switch')) return 'Electrical Materials';
    if (name.includes('pipe') || name.includes('fitting') || name.includes('plumbing')) return 'Plumbing Materials';
    if (name.includes('cement')) return 'Cement';
    return 'Other';
  }

  categoryChanged(): void {
    const suggestions = this.categoryMaterials[this.form.category] || [];
    if (!this.form.material_name || this.form.material_name === this.categoryMaterials[this.form.category]?.[0]) {
      this.form.material_name = suggestions[0] || '';
    }
  }

  requestCategoryChanged(): void {
    const suggestions = this.categoryMaterials[this.requestForm.category] || [];
    this.requestForm.material_name = suggestions[0] || '';
  }

  availableUnits(): number {
    return this.items.reduce((sum, item) => sum + Math.max(0, (Number(item.quantity) || 0) - (Number(item.used) || 0)), 0);
  }

  usedUnits(): number {
    return this.items.reduce((sum, item) => sum + (Number(item.used) || 0), 0);
  }

  lowStockCount(): number {
    return this.items.filter(item => {
      const total = Number(item.quantity) || 0;
      const available = Math.max(0, total - (Number(item.used) || 0));
      return total > 0 && available / total <= 0.2;
    }).length;
  }

  pendingRequests(): number {
    return this.requests.filter(request => ['Pending', 'Ordered'].includes(String(request?.status || ''))).length;
  }

  openCreate(): void {
    this.editingId = null;
    this.form = this.emptyForm();
    this.showForm = true;
    this.error = '';
  }

  edit(item: any): void {
    this.editingId = Number(item.id);
    this.form = {
      material_name: this.cleanStoredName(String(item.material_name || '')),
      category: this.getCategory(item) === 'Other' ? 'Cement' : this.getCategory(item),
      quantity: Number(item.quantity) || 0,
      unit: String(item.unit || ''),
      supplier: String(item.supplier || ''),
      status: String(item.status || 'Available')
    };
    this.showForm = true;
    this.error = '';
  }

  private cleanStoredName(name: string): string {
    const prefix = this.categories.find(category => name.toLowerCase().startsWith(`${category.toLowerCase()} -`));
    return prefix ? name.substring(prefix.length + 3).trim() : name;
  }

  cancel(): void {
    this.showForm = false;
    this.editingId = null;
    this.saving = false;
  }

  save(): void {
    const name = this.form.material_name.trim();
    if (!name || this.form.quantity < 0 || !this.form.unit.trim() || !this.form.supplier.trim()) {
      this.error = 'Material, quantity, unit and supplier are required.';
      return;
    }

    this.saving = true;
    const storedName = this.withCategory(name, this.form.category);
    const payload = {
      material_name: storedName,
      quantity: Number(this.form.quantity),
      unit: this.form.unit.trim(),
      supplier: this.form.supplier.trim(),
      status: this.form.status
    };

    const request = this.editingId
      ? this.api.updateInventory(this.editingId, payload)
      : this.api.createInventory(payload);

    request.subscribe({
      next: () => {
        this.cancel();
        this.load();
      },
      error: (e: any) => {
        this.saving = false;
        this.error = e?.error?.detail || 'Unable to save material.';
      }
    });
  }

  private withCategory(name: string, category: string): string {
    const alreadyCategorized = this.categories.some(item => name.toLowerCase().startsWith(`${item.toLowerCase()} -`) || name.toLowerCase() === item.toLowerCase());
    return alreadyCategorized ? name : `${category} - ${name}`;
  }

  openRequest(): void {
    this.requestForm = this.emptyRequestForm();
    this.requestForm.project_id = Number(this.projects[0]?.id || 0);
    this.showRequestForm = true;
    this.error = '';
  }

  cancelRequest(): void {
    this.showRequestForm = false;
  }

  submitRequest(): void {
    if (!this.requestForm.material_name.trim() || this.requestForm.quantity < 1 || !this.requestForm.supplier.trim() || !this.requestForm.project_id) {
      this.error = 'Material, quantity, supplier and project are required for a material request.';
      return;
    }

    this.saving = true;
    const itemName = this.withCategory(this.requestForm.material_name.trim(), this.requestForm.category);
    this.api.createProcurement({
      item_name: itemName,
      quantity: Number(this.requestForm.quantity),
      supplier: this.requestForm.supplier.trim(),
      status: 'Pending',
      project_id: Number(this.requestForm.project_id)
    }).subscribe({
      next: () => {
        this.saving = false;
        this.showRequestForm = false;
        this.loadRequests();
      },
      error: (e: any) => {
        this.saving = false;
        this.error = e?.error?.detail || 'Unable to submit material request.';
      }
    });
  }

  allocate(item: any): void {
    const available = Math.max(0, Number(item.quantity) - Number(item.used));
    if (!available) {
      this.error = `${item.material_name} has no available stock to allocate.`;
      return;
    }

    const quantity = Number(prompt(`Quantity to allocate (available: ${available})`, '1'));
    if (!Number.isInteger(quantity) || quantity < 1) return;
    if (quantity > available) {
      this.error = `Only ${available} ${item.unit || 'units'} of ${item.material_name} are available.`;
      return;
    }

    this.api.useInventory(Number(item.id), { quantity }).subscribe({
      next: () => this.load(),
      error: (e: any) => this.error = e?.error?.detail || 'Unable to allocate material.'
    });
  }

  release(item: any): void {
    const used = Number(item.used) || 0;
    if (!used) return;

    const quantity = Number(prompt(`Quantity to release (allocated: ${used})`, '1'));
    if (!Number.isInteger(quantity) || quantity < 1) return;
    if (quantity > used) {
      this.error = `Only ${used} ${item.unit || 'units'} are currently allocated.`;
      return;
    }

    this.api.releaseInventory(Number(item.id), quantity).subscribe({
      next: () => this.load(),
      error: (e: any) => this.error = e?.error?.detail || 'Unable to release material.'
    });
  }

  remove(item: any): void {
    if (!confirm(`Delete ${item.material_name}?`)) return;
    this.api.deleteInventory(Number(item.id)).subscribe({
      next: () => this.load(),
      error: (e: any) => this.error = e?.error?.detail || 'Unable to delete material.'
    });
  }
}
