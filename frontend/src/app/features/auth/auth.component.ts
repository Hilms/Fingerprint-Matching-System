import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';

import { AuthService } from './auth.service';
import { Router } from '@angular/router';

interface LoginRequest {
  username: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
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
  ) {}

  mode: 'login' | 'register' = 'login';

  setMode(m: 'login' | 'register') {
    this.mode = m;
  }

  loginForm = new FormGroup({
    username: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required]
    }),
    password: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required]
    })
  });

  registerForm = new FormGroup({
    username: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required]
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
      validators: [Validators.required]
    }),
    last_name: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required]
    })
  });

  login() {
    if (this.loginForm.invalid) return;

    const data: LoginRequest = this.loginForm.getRawValue();

    this.authService.login(data).subscribe({
      next: (res: any) => {
        localStorage.setItem('token', res.access_token);
        this.router.navigate(['/app/dashboard']);
      },
      error: (err) => console.error(err)
    });
  }

  register() {
    if (this.registerForm.invalid) return;

    const data: RegisterRequest = this.registerForm.getRawValue();

    this.authService.register(data).subscribe({
      next: () => {
        this.mode = 'login';
      },
      error: (err) => console.error(err),
    });
  }
}
