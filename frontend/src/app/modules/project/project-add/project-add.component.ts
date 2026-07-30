import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-project-add',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './project-add.component.html',
  styleUrl: './project-add.component.scss'
})
export class ProjectAddComponent {
  projectForm = this.fb.group({
    name: ['', Validators.required],
    description: [''],
    startDate: ['', Validators.required],
    endDate: [''],
    budget: [null, [Validators.required, Validators.min(0)]],
    status: ['planning', Validators.required]
  });

  constructor(private fb: FormBuilder) {}

  get name() {
    return this.projectForm.get('name');
  }

  get startDate() {
    return this.projectForm.get('startDate');
  }

  get budget() {
    return this.projectForm.get('budget');
  }

  onSubmit() {
    if (this.projectForm.invalid) {
      this.projectForm.markAllAsTouched();
      return;
    }

    const project = this.projectForm.value;
    console.log('Project created:', project);
    alert(`Project created: ${project.name}`);
    this.projectForm.reset({ status: 'planning' });
  }
}
