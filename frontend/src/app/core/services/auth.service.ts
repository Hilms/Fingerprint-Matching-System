import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environment';

import { LoginRequest, RegisterRequest, LoginResponse, RegisterResponse } from '../models/auth.models';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient, private router: Router) {}

  login(data: LoginRequest) {
    return this.http.post<LoginResponse>(`${this.api}/auth/login`, data);
  }

  register(data: RegisterRequest) {
    return this.http.post<RegisterResponse>(`${this.api}/auth/register`, data);
  }

  refresh_token() {
    return this.http.post<any>(`${this.api}/auth/refresh`, {
      refresh_token: this.get_refresh_token(),
    });
  }

  store_access_token(token: string): void {
    localStorage.setItem('access_token', token);
  }

  get_access_token(): string | null {
    return localStorage.getItem('access_token');
  }

  store_refresh_token(token: string): void{
     localStorage.setItem('refresh_token', token);
  }

  get_refresh_token(): string | null {
    return localStorage.getItem('refresh_token');
  }

  get_role(): string | null {
    const token = this.get_access_token();
    if (!token) return null;

    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role;
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.router.navigate(['/auth']);
  }

  is_authenticated(): boolean {
    return !!this.get_access_token();
  }
}
