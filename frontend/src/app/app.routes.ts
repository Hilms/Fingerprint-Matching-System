import { Routes } from '@angular/router';
import { AuthComponent } from './features/auth/auth.component';

export const routes: Routes = [
  // default redirect
  { path: '', redirectTo: 'auth', pathMatch: 'full' },
  // AUTH (public)
  { path: 'auth', component: AuthComponent },

  // PROTECTED AREA (later guarded)
  {
    path: 'app',
    children: [
      // routing to services
    ]
  },

  // fallback
  { path: '**', redirectTo: 'auth' },
];

