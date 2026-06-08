import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../environment';

import { LoginRequest, RegisterRequest, LoginResponse, RegisterResponse } from '../models/auth.models';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  login(data: LoginRequest) {
    return this.http.post<LoginResponse>(`${this.api}/auth/login`, data);
  }

  register(data: RegisterRequest) {
    return this.http.post<RegisterResponse>(`${this.api}/auth/register`, data);
  }
  logout(): void {
    localStorage.removeItem('token');
  }
