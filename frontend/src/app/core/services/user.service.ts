import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environment';

import { User } from '../models/user.models';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getAllUsers() {
    return this.http.get<User[]>(`${this.api}/users/admin`);
  }

  searchUsers(query: string) {
    return this.http.get<User[]>(`${this.api}/users/admin/search?query=${query}`);
  }

  createUser(data: any){
    return this.http.post(`${this.api}/users/admin/create`, data);
  }

  updateUser(username: string, data: any){
    return this.http.patch(`${this.api}/users/admin/${username}`, data);
  }

  deleteUser(username: string){
    return this.http.delete(`${this.api}/users/admin/${username}`);
  }

  resetPassword(username: string, newPassword: string) {
    return this.http.patch(`${this.api}/users/admin/${username}/password`, {
      new_password: newPassword
    });
  }
}
