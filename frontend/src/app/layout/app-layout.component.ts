import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './app-layout.html',
  styleUrls: ['./app-layout.css'],
})
export class AppLayoutComponent {
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  get role(): string | null {
    return this.authService.get_role();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }
}
