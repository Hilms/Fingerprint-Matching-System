import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  login(data: {
    username: string;
    password: string
  }) {
    return this.http.post(`${this.api}/auth/login`, data);
  }

  register(data: {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) {
    return this.http.post(`${this.api}/auth/register`, data);
  }
}
