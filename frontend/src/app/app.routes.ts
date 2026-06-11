import { Routes } from '@angular/router';
import { AuthComponent } from './features/auth/auth.component';
import { AppLayoutComponent } from './layout/app-layout.component';
import { ImportComponent } from './features/admin/import/import.component';
import { UserComponent } from './features/admin/user/user.component';

import { AuthGuard } from './core/guards/auth.guard';
import { RoleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'auth', pathMatch: 'full' },

  { path: 'auth', component: AuthComponent },

  // PROTECTED ROUTES
  {
    path: 'app',
    component: AppLayoutComponent,
    canActivate: [AuthGuard],
    children: [
      // logged-in user paths
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },

      // admin only paths
      {
        path: 'admin/import',
        component: ImportComponent,
        canActivate: [RoleGuard],
        data: { role: 'admin' },
      },
      {
        path: 'admin/user',
        component: UserComponent,
        canActivate: [RoleGuard],
        data: { role: 'admin' },
      },

      // fallback inside app
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    ],
  },

  { path: '**', redirectTo: 'auth' },
];
