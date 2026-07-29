/// <reference types="jasmine" />

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';

import { RegisterComponent } from './register.component';

describe('RegisterComponent', () => {
  let component: RegisterComponent;
  let fixture: ComponentFixture<RegisterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegisterComponent, RouterTestingModule, HttpClientTestingModule]
    }).compileComponents();

    fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should reject an invalid email', () => {
    component.registerForm.controls['email'].setValue('invalid-email');
    expect(component.registerForm.controls['email'].valid).toBeFalse();
  });

  it('should reject a weak password', () => {
    component.registerForm.controls['password'].setValue('weak');
    expect(component.registerForm.controls['password'].valid).toBeFalse();
  });

  it('should reject mismatched passwords', () => {
    component.registerForm.controls['password'].setValue('Strong123');
    component.registerForm.controls['confirmPassword'].setValue('Different123');
    expect(component.registerForm.errors?.['mismatch']).toBeTrue();
  });
});
