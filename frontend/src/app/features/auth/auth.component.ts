import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import {
  ReactiveFormsModule,
  FormGroup,
  FormControl,
  Validators,
  AbstractControl,
  ValidationErrors,
  ValidatorFn
} from '@angular/forms';

import { AuthService } from '../../core/services/auth.service';
import { Router } from '@angular/router';

import {
  LoginRequest,
  RegisterRequest,
  LoginResponse,
  RegisterResponse
} from '../../core/models/auth.models';

// Custom Validators
export function username_validator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value;
    if (!value) return null;

    const valid = /^[a-zA-Z0-9._]{3,20}$/.test(value);
    return valid ? null : { invalidUsername: true };
  };
}

export function name_validator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value;
    if (!value) return null;

    const valid = /^[A-Za-zÀ-ž\s'-]+$/.test(value);
    return valid ? null : { invalidName: true };
  };
}

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  templateUrl: './auth.html',
  styleUrls: ['./auth.css'],
})
export class AuthComponent {
  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
  ) {}

  login_error: string | null = null;
  register_error: string | null = null;
  register_success: string |null = null;

  mode: 'login' | 'register' = 'login';

  loginForm = new FormGroup({
    username: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, username_validator()]
    }),
    password: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required]
    })
  });

  registerForm = new FormGroup({
    username: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, username_validator()]
    }),
    email: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email]
    }),
    password: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, Validators.minLength(6)]
    }),
    first_name: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, name_validator()]
    }),
    last_name: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, name_validator()]
    })
  });

  set_mode(m: 'login' | 'register') {
    this.mode = m;
    this.register_error = null;
    this.login_error = null;
    this.register_success = null;
    this.loginForm.reset();
    this.registerForm.reset();
  }

  login() {
    if (this.loginForm.invalid) return;

    const raw = this.loginForm.getRawValue();

    const data: LoginRequest = {
      username: raw.username.trim(),
      password: raw.password,
    };

    this.authService.login(data).subscribe({
        localStorage.setItem('token', res.access_token);
      next: (res: LoginResponse) => {
        this.router.navigate(['/app/dashboard']);
      },
      error: (err) => {
        if (err.status === 401 || err.status === 403) {
          this.login_error = 'Invalid username or password';
        } else {
          this.login_error = 'Login failed';
        }
        this.cdr.detectChanges();
      },
    });
  }

  register() {
    if (this.registerForm.invalid) return;

    const raw = this.registerForm.getRawValue();

    const data: RegisterRequest = {
      username: raw.username.trim(),
      email: raw.email.trim().toLowerCase(),
      password: raw.password,
      first_name: raw.first_name.trim(),
      last_name: raw.last_name.trim(),
    };

    this.authService.register(data).subscribe({
      next: (res: RegisterResponse) => {
        this.set_mode('login');
        this.register_success = res.message + ', please log in';
      },
      error: (err) => {
        if (err.status === 409) {
          this.register_error = err.error.detail || 'User already exists';
        } else {
          this.register_error = 'Something went wrong';
        }
        this.cdr.detectChanges();
      },
    });
  }
}
