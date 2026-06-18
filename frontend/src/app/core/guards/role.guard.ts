import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root',
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const requiredRole = route.data['role'];
    const userRole = this.authService.get_role();

    // not logged in → go login
    if (!userRole) {
      this.router.navigate(['/auth']);
      return false;
    }

    // wrong role → redirect to dashboard
    if (requiredRole && userRole !== requiredRole) {
      this.router.navigate(['/app/dashboard']);
      return false;
    }

    return true;
  }
}
