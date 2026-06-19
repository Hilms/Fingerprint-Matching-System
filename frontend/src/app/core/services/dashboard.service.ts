import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environment';

import { DashboardResponse, AdminDashboardResponse } from '../models/dashboard.models';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private api: string = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getUserDashboard(): Observable<DashboardResponse> {
    return this.http.post<DashboardResponse>(`${this.api}/dashboard/data`, {});
  }

  getAdminDashboard(): Observable<AdminDashboardResponse> {
    return this.http.post<AdminDashboardResponse>(`${this.api}/dashboard/admin/data`, {});
  }
}
