import { Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { forkJoin } from 'rxjs';
import { EChartsOption } from 'echarts';

import { DashboardService } from '../../core/services/dashboard.service';
import { AuthService } from '../../core/services/auth.service';
import { NgxEchartsDirective } from 'ngx-echarts';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, NgxEchartsDirective],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css'],
})
export class DashboardComponent implements OnInit {

  genderChart!: EChartsOption;
  ageChart!: EChartsOption;
  fingerChart!: EChartsOption;
  handChart!: EChartsOption;
  countryChart!: EChartsOption;
  cityChart!: EChartsOption;
  ageGenderChart!: EChartsOption;
  countryGenderChart!: EChartsOption;

  roleChart!: EChartsOption;
  registrationChart!: EChartsOption;


  data: any;
  adminData: any;
  isAdmin: boolean = false;
  loading: boolean = true;

  constructor(
    private dashboardService: DashboardService,
    private auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.isAdmin = this.auth.get_role() === 'admin';
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;

    const userRequest: any = this.dashboardService.getUserDashboard();

    if (this.isAdmin) {
      forkJoin({
        user: userRequest,
        admin: this.dashboardService.getAdminDashboard(),
      }).subscribe({
        next: (res): void => {
          this.data = res.user;
          this.adminData = res.admin;
          this.loading = false;
        },
        error: (err: HttpErrorResponse): void => {
          console.error(err);
          this.loading = false;
        },
      });
    } else {
      userRequest.subscribe({
        next: (res: any): void => {
          this.data = res;
          this.loading = false;
        },
        error: (err: HttpErrorResponse): void => {
          console.error(err);
          this.loading = false;
        },
      });
    }
  }
}
