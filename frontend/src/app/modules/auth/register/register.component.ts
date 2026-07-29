import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  submitted = false;
  roles = ['Admin', 'Manager', 'Employee', 'Viewer'];

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.registerForm = this.fb.group({
      fullName: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      mobileNumber: ['', [Validators.required, Validators.pattern(/^\d{10}$/)]],
      password: ['', [Validators.required, Validators.minLength(8), Validators.pattern(/^(?=.*[A-Z])(?=.*\d).+/)]],
      confirmPassword: ['', [Validators.required]],
      role: ['Employee', Validators.required],
      employeeId: ['', [Validators.required, Validators.minLength(3)]],
      department: ['', [Validators.required, Validators.minLength(2)]],
      designation: ['', [Validators.required, Validators.minLength(2)]],
      address: [''],
      profilePicture: ['']
    }, {
      validators: this.passwordMatchValidator
    });
  }

  passwordMatchValidator(group: FormGroup) {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  onSubmit(): void {
    this.submitted = true;

    if (this.registerForm.invalid) {
      return;
    }

    const payload = {
      ...this.registerForm.value,
      password: this.registerForm.value.password
    };

    console.log('Registration submitted', payload);
  }

  get f() {
    return this.registerForm.controls;
  }
}
