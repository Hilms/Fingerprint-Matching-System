import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { MyProfileService } from '../../core/services/profile.service';
import { SelfUserUpdate, PasswordUpdate} from '../../core/models/profile.models'
import { User } from '../../core/models/user.models';
import { UserValidator } from '../../core/utils/user.validator';



@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css'],
})
export class MyProfileComponent implements OnInit {
  constructor(
    private myProfileService: MyProfileService,
    private userValidator: UserValidator,
    private cdr: ChangeDetectorRef,
  ) {}

  successVisible: boolean = false;
  successMessage: string | null = null;
  successState: 'success' | 'error' = 'success';

  currentUser: User | null = null;

  editingProfile: boolean = false;
  showPasswordForm: boolean = false;

  editUser: SelfUserUpdate = {};

  passwordData: PasswordUpdate = {
    current_password: '',
    new_password: '',
  };

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.myProfileService.getMe().subscribe({
      next: (user: User): void => {
        this.currentUser = user;
        this.cdr.detectChanges();
      },
      error: (err: HttpErrorResponse): void => {
        this.handleError(err);
      },
    });
  }

  openEditProfile(): void {
    this.editUser = {
      email: this.currentUser!.email,
      first_name: this.currentUser!.first_name,
      last_name: this.currentUser!.last_name,
    };

    this.editingProfile = true;
  }

  closeEditProfile(): void {
    this.editingProfile = false;
    this.editUser = {};
  }

  inputChanged(): boolean {
    const current: User = this.currentUser!;
    const edit: SelfUserUpdate = this.editUser;
    return (
      current.first_name != edit.first_name ||
      current.last_name != edit.last_name ||
      current.email != edit.email
    );
  }

  updateProfile(): void {
    this.myProfileService.updateMe(this.editUser).subscribe({
      next: (res: Object): void => {
        this.showResponse(res);
        this.closeEditProfile();
        this.loadProfile();
      },

      error: (err: HttpErrorResponse): void => {
        this.handleError(err);
      },
    });
  }

  openPasswordForm(): void {
    this.showPasswordForm = true;
  }

  closePasswordForm(): void {
    this.showPasswordForm = false;
    this.passwordData = {
      current_password: '',
      new_password: '',
    };
  }

  isPasswordValid(): boolean {
    return (
      this.passwordData.current_password != '' &&
      this.passwordData.new_password != '' &&
      !this.isPasswordLengthValid(this.passwordData.new_password) &&
      this.passwordData.current_password != this.passwordData.new_password
    )
  }

  isPasswordLengthValid(password: string): boolean {
    return this.userValidator.isPasswordLengthValid(password,  6);
  }

  changePassword(): void {
    this.myProfileService.updateMyPassword(this.passwordData).subscribe({
      next: (res: Object): void => {
        this.showResponse(res);
        this.closePasswordForm();
        this.cdr.detectChanges();
      },

      error: (err: HttpErrorResponse): void => {
        this.handleError(err);
      },
    });
  }

  /* =========================
     UI HELPERS
  ========================= */
  showResponse(res: any): void {
    this.successState = res.success ? 'success' : 'error';
    this.successMessage = res.message;

    this.successVisible = true;
    this.cdr.detectChanges();

    setTimeout((): void => {
      this.successVisible = false;
      this.successMessage = null;
      this.cdr.detectChanges();
    }, 5000);
  }

  handleError(err: HttpErrorResponse): void {
    this.successMessage = err.error?.detail ?? 'Error';
    this.successState = 'error';
    this.successVisible = true;

    this.passwordData = {
      current_password: '',
      new_password: '',
    };

    this.cdr.detectChanges();

    setTimeout((): void => {
      this.successMessage = null;
      this.successVisible = false;
      this.cdr.detectChanges();
    }, 10000);
  }

}
