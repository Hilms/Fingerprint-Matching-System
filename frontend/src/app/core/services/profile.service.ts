import { Injectable } from '@angular/core';
import { environment } from '../../../environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { SelfUserUpdate, PasswordUpdate } from '../models/profile.models';
import { User } from '../models/user.models';


@Injectable({ providedIn: 'root' })
export class MyProfileService {
  private api: string = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMe()  {
    return this.http.get<User>(`${this.api}/users/me`);
  }

  updateMe(data: SelfUserUpdate) {
    return this.http.patch(`${this.api}/users/me`, data);
  }

  updateMyPassword(data: PasswordUpdate) {
    return this.http.patch(`${this.api}/users/me/password`, data);
  }
}
