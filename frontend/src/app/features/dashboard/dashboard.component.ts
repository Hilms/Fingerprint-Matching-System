import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { forkJoin} from 'rxjs';
import { EChartsOption } from 'echarts';

import { DashboardService } from '../../core/services/dashboard.service';
import { AuthService } from '../../core/services/auth.service';
import { NgxEchartsDirective } from 'ngx-echarts';
import {
  GenderStat,
  AgeStat,
  HandStat,
  FingerStat,
  CountryStat,
  CityStat,
  AgeGenderStat,
  CountryGenderStat,
  CityGenderStat,
  UserRoleStat,
  UserRegistrationStat,
  DashboardResponse,
  AdminDashboardResponse,
} from '../../core/models/dashboard.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, NgxEchartsDirective],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css'],
})
export class DashboardComponent implements OnInit {
  constructor(
    private dashboardService: DashboardService,
    private auth: AuthService,
    private cdr: ChangeDetectorRef,
  ) {}

  errorVisible: boolean = false;
  successMessage: string | null = null;

  genderChart!: EChartsOption;
  ageChart!: EChartsOption;
  fingerChart!: EChartsOption;
  handChart!: EChartsOption;
  countryChart!: EChartsOption;
  cityChart!: EChartsOption;
  ageGenderChart!: EChartsOption;
  countryGenderChart!: EChartsOption;
  cityGenderChart!: EChartsOption;

  roleChart!: EChartsOption;
  registrationChart!: EChartsOption;

  data: DashboardResponse | null = null;
  adminData: AdminDashboardResponse | null = null;
  isAdmin: boolean = false;
  loading: boolean = true;

  ngOnInit(): void {
    this.isAdmin = this.auth.get_role() === 'admin';
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;

    const userRequest = this.dashboardService.getUserDashboard();

    if (this.isAdmin) {
      forkJoin({
        user: userRequest,
        admin: this.dashboardService.getAdminDashboard(),
      }).subscribe({
        next: (res: { user: DashboardResponse; admin: AdminDashboardResponse }): void => {
          this.data = res.user;
          this.adminData = res.admin;
          this.loading = false;

          this.buildCharts();
          this.buildAdminCharts();

          this.cdr.detectChanges();
        },
        error: (err: HttpErrorResponse): void => {
          this.loading = false;
          this.handleError(err);
        },
      });
    } else {
      userRequest.subscribe({
        next: (res: DashboardResponse): void => {
          this.data = res;
          this.loading = false;

          this.buildCharts();

          this.cdr.detectChanges();
        },
        error: (err: HttpErrorResponse): void => {
          this.loading = false;
          this.handleError(err);
        },
      });
    }
  }

  private buildCharts(): void {
    this.buildGenderChart();
    this.buildAgeChart();
    this.buildHandChart();
    this.buildFingerChart();
    this.buildCountriesChart();
    this.buildCitiesChart();
    this.buildAgeGenderChart();
    this.buildCountryGenderChart();
    this.buildCityGenderChart();
  }

  private buildAdminCharts(): void {
    this.buildUserRoleChart();
    this.buildUserRegistrationChart();
  }

  private buildGenderChart(): void {
    const genders: GenderStat[] = this.data!.gender;
    this.genderChart = {
      tooltip: {
        trigger: 'item',
      },

      legend: {
        bottom: 0,
        textStyle: {
          color: '#fff',
        },
      },

      series: [
        {
          name: 'Gender',
          type: 'pie',
          radius: '70%',

          data: genders.map((g: GenderStat): { name: string; value: number } => ({
            name: g.gender === 'm' ? 'Male' : 'Female',
            value: g.count,
          })),
        },
      ],
    };
  }

  private buildAgeChart(): void {
    const ages: AgeStat[] = this.data!.age;

    this.ageChart = {
      tooltip: {
        trigger: 'axis',
      },

      xAxis: {
        type: 'category',
        data: ages.map((a: AgeStat): string => a.age_group),
        axisLabel: {
          color: '#fff',
        },
      },

      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#fff',
        },
      },

      series: [
        {
          type: 'bar',
          data: ages.map((a: AgeStat): number => a.count),
        },
      ],
    };
  }

  private buildHandChart(): void {
    const hands: HandStat[] = this.data!.hands;
    this.handChart = {
      tooltip: {
        trigger: 'item',
      },

      legend: {
        bottom: 0,
        textStyle: {
          color: '#fff',
        },
      },

      series: [
        {
          type: 'pie',
          radius: '70%',

          data: hands.map((h: HandStat): { name: string; value: number } => ({
            name: h.hand,
            value: h.count,
          })),
        },
      ],
    };
  }

  private buildFingerChart(): void {
    const fingers: FingerStat[] = this.data!.fingers;

    this.fingerChart = {
      tooltip: {},

      xAxis: {
        type: 'category',
        data: fingers.map((f: FingerStat): string => f.finger),
        axisLabel: {
          color: '#fff',
        },
      },

      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#fff',
        },
      },

      series: [
        {
          type: 'bar',
          data: fingers.map((f: FingerStat): number => f.count),
        },
      ],
    };
  }

  private buildCountriesChart(): void {
    const countries: CountryStat[] = this.data!.countries;

    this.countryChart = {
      tooltip: {
        trigger: 'axis',
      },

      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },

      xAxis: {
        type: 'value',
        axisLabel: { color: '#fff' },
      },

      yAxis: {
        type: 'category',
        data: countries.map((c: CountryStat): string => c.country),
        axisLabel: { color: '#fff' },
      },

      series: [
        {
          type: 'bar',
          data: countries.map((c: CountryStat): number => c.count),
          barWidth: '60%',
        },
      ],
    };
  }

  private buildCitiesChart(): void {
    const cities: CityStat[] = this.data!.cities;

    this.cityChart = {
      tooltip: {
        trigger: 'axis',
      },

      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },

      xAxis: {
        type: 'value',
        axisLabel: { color: '#fff' },
      },

      yAxis: {
        type: 'category',
        data: cities.map((c: CityStat): string => c.city),
        axisLabel: { color: '#fff' },
      },

      series: [
        {
          type: 'bar',
          data: cities.map((c: CityStat): number => c.count),
          barWidth: '60%',
        },
      ],
    };
  }

  private buildAgeGenderChart(): void {
    const raw: AgeGenderStat[] = this.data!.age_gender;

    const groups: string[] = [...new Set(raw.map((x: AgeGenderStat): string => x.age_group))];

    const male: number[] = groups.map((group: string): number => {
      const item: AgeGenderStat | undefined = raw.find(
        (x: AgeGenderStat): boolean => x.age_group === group && x.gender === 'm',
      );
      return item ? item.count : 0;
    });

    const female: number[] = groups.map((group: string): number => {
      const item: AgeGenderStat | undefined = raw.find(
        (x: any): boolean => x.age_group === group && x.gender === 'f',
      );
      return item ? item.count : 0;
    });

    this.ageGenderChart = {
      tooltip: {
        trigger: 'axis',
      },

      legend: {
        data: ['Male', 'Female'],
        textStyle: { color: '#fff' },
      },

      xAxis: {
        type: 'category',
        data: groups,
        axisLabel: { color: '#fff' },
      },

      yAxis: {
        type: 'value',
        axisLabel: { color: '#fff' },
      },

      series: [
        {
          name: 'Male',
          type: 'bar',
          stack: 'total',
          data: male,
        },
        {
          name: 'Female',
          type: 'bar',
          stack: 'total',
          data: female,
        },
      ],
    };
  }

  private buildCountryGenderChart(): void {
    const raw: CountryGenderStat[] = this.data!.country_gender;

    const countries: string[] = [...new Set(raw.map((x: CountryGenderStat): string => x.country))];

    const male: number[] = countries.map((country: string): number => {
      const item: CountryGenderStat | undefined = raw.find(
        (x: CountryGenderStat): boolean => x.country === country && x.gender === 'm',
      );
      return item ? item.count : 0;
    });

    const female: number[] = countries.map((country: string): number => {
      const item: CountryGenderStat | undefined = raw.find(
        (x: CountryGenderStat): boolean => x.country === country && x.gender === 'f',
      );
      return item ? item.count : 0;
    });

    this.countryGenderChart = {
      tooltip: { trigger: 'axis' },

      legend: {
        data: ['Male', 'Female'],
        textStyle: { color: '#fff' },
      },

      xAxis: {
        type: 'category',
        data: countries,
        axisLabel: { color: '#fff' },
      },

      yAxis: {
        type: 'value',
        axisLabel: { color: '#fff' },
      },

      series: [
        {
          name: 'Male',
          type: 'bar',
          stack: 'total',
          data: male,
        },
        {
          name: 'Female',
          type: 'bar',
          stack: 'total',
          data: female,
        },
      ],
    };
  }

  private buildCityGenderChart(): void {
    const raw: CityGenderStat[] = this.data!.city_gender;

    const cities: string[] = [...new Set(raw.map((x: CityGenderStat): string => x.city))];

    const male: number[] = cities.map((city: string): number => {
      const item: CityGenderStat | undefined = raw.find(
        (x: CityGenderStat): boolean => x.city === city && x.gender === 'm',
      );
      return item ? item.count : 0;
    });

    const female: number[] = cities.map((city: string): number => {
      const item: CityGenderStat | undefined = raw.find(
        (x: CityGenderStat): boolean => x.city === city && x.gender === 'f',
      );
      return item ? item.count : 0;
    });

    this.cityGenderChart = {
      tooltip: { trigger: 'axis' },

      legend: {
        data: ['Male', 'Female'],
        textStyle: { color: '#fff' },
      },

      xAxis: {
        type: 'category',
        data: cities,
        axisLabel: {
          color: '#fff',
          rotate: 45, // important for long city names
        },
      },

      yAxis: {
        type: 'value',
        axisLabel: { color: '#fff' },
      },

      series: [
        {
          name: 'Male',
          type: 'bar',
          stack: 'total',
          data: male,
        },
        {
          name: 'Female',
          type: 'bar',
          stack: 'total',
          data: female,
        },
      ],
    };
  }

  private buildUserRoleChart(): void {
    const raw: UserRoleStat[] = this.adminData!.roles;

    const data: { name: string; value: number }[] = raw.map(
      (item: UserRoleStat): { name: string; value: number } => ({
        name: item.role,
        value: item.count,
      }),
    );

    this.roleChart = {
      tooltip: {
        trigger: 'item',
      },

      legend: {
        orient: 'horizontal',
        bottom: 0,
        textStyle: { color: '#fff' },
      },

      series: [
        {
          name: 'User Roles',
          type: 'pie',
          radius: '65%',
          data,
        },
      ],
    };
  }

  private buildUserRegistrationChart(): void {
    const raw: UserRegistrationStat[] = this.adminData!.registrations;

    raw.sort(
      (a: UserRegistrationStat, b: UserRegistrationStat): number =>
        new Date(a.date).getTime() - new Date(b.date).getTime(),
    );

    const dates: string[] = raw.map((item: UserRegistrationStat): string => item.date);
    const values: number[] = raw.map((item: UserRegistrationStat): number => item.count);

    this.registrationChart = {
      tooltip: {
        trigger: 'axis',
      },

      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: { color: '#fff' },
      },

      yAxis: {
        type: 'value',
        axisLabel: { color: '#fff' },
      },

      series: [
        {
          name: 'Registrations',
          type: 'line',
          smooth: true,
          data: values,
        },
      ],
    };
  }

  handleError(err: HttpErrorResponse): void {
    this.successMessage = err.error?.detail ?? 'Error';
    this.errorVisible = true;
    this.cdr.detectChanges();

    setTimeout((): void => {
      this.successMessage = null;
      this.errorVisible = false;
      this.cdr.detectChanges();
    }, 60000);
  }
}
