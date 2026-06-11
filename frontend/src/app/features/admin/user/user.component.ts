import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { HttpErrorResponse } from '@angular/common/http';

import { UserService } from '../../../core/services/user.service';
import { User, newUser } from '../../../core/models/user.models';
import { UserValidator } from '../../../core/utils/user.validator';


@Component({
  selector: 'app-user',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './user.html',
  styleUrls: ['./user.css'],
})
export class UserComponent implements OnInit {
  // TABLE STATE
  dataSource = new MatTableDataSource<User>([]);
  selectedUser: User | null = null;
  originalUser: User | null = null;

  searchQuery = '';
  loading = false;

  displayedColumns = [
    'username',
    'first_name',
    'last_name',
    'email',
    'role',
    'is_active',
    'actions',
  ];

  passwordUser: User | null = null;
  resetPassword: string = '';
  confirmPassword: string = '';
  passwordMinLength: number = 6;

  successMessage: string | null = null;
  successVisible = false;
  successState: 'success' | 'error' = 'success';

  newUser: newUser = this.buildNewUser();
  showAddUserForm = false;

  constructor(
    private userService: UserService,
    private userValidator: UserValidator,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;

    this.userService.getAllUsers().subscribe({
      next: (users: User[]) => {
        this.dataSource.data = users;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err: HttpErrorResponse) => {
        this.showResponse({
          success: false,
          message: err.error.detail ?? 'Unknown error',
        });
        this.loading = false;
        this.cdr.detectChanges();

      },
    });
  }

  resetUsers(): void {
    this.searchQuery = '';
    this.loadUsers();
  }

  searchUsers(): void {
    const query = this.searchQuery.trim();

    if (!query) {
      this.loadUsers();
      return;
    }

    this.loading = true;

    this.userService.searchUsers(query).subscribe({
      next: (users: User[]) => {
        this.dataSource.data = users;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err: HttpErrorResponse) => {
        console.error(err)
        this.showResponse({
          success: false,
          message: err.error.detail ?? 'Unknown error'
        });
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  editUser(user: User): void {
    this.selectedUser = { ...user };
    this.originalUser = { ...user };
  }

  cancelEdit(): void {
    this.selectedUser = null;
    this.originalUser = null;
  }

  isUserChanged(): boolean {
    if (!this.selectedUser || !this.originalUser) return false;
    return JSON.stringify(this.selectedUser) !== JSON.stringify(this.originalUser);
  }

  saveUser(): void {
    if (!this.selectedUser || !this.originalUser) return;

    const updated = { ...this.selectedUser };

    this.userService
      .updateUser(updated.username, {
        first_name: updated.first_name,
        last_name: updated.last_name,
        email: updated.email,
        role: updated.role,
        is_active: updated.is_active,
      })
      .subscribe({
        next: (res) => {
          this.dataSource.data = this.dataSource.data.map((u) =>
            u.username === updated.username ? updated : u,
          );

          this.selectedUser = null;
          this.originalUser = null;
          this.showResponse(res);
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error(err);
          this.showResponse({
            success: false,
            message: err.error.detail ?? 'Unknown error',
          });
          this.cdr.detectChanges();
        },
      });
  }

  deleteUser(user: User): void {
    const confirmed = confirm(`Delete user "${user.username}"?`);
    if (!confirmed) return;

    this.userService.deleteUser(user.username).subscribe({
      next: (res) => {
        this.dataSource.data = this.dataSource.data.filter((u) => u.username !== user.username);
        this.showResponse(res);
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.showResponse({
          success: false,
          message: err.error.detail ?? 'Unknown error',
        });
        this.cdr.detectChanges();
      },
    });
  }

  openPasswordReset(user: User): void {
    this.passwordUser = user;
    this.resetPassword = '';
    this.confirmPassword = '';
  }

  closePasswordReset(): void {
    this.passwordUser = null;
    this.resetPassword = '';
    this.confirmPassword = '';
  }

  resetUserPassword(): void {
    if (!this.passwordUser) return;

    this.userService.resetPassword(this.passwordUser.username, this.resetPassword).subscribe({
      next: (res) => {
        this.closePasswordReset();
        this.showResponse(res);
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        console.error(err);
        this.showResponse({
          success: false,
          message: err.error.detail ?? 'Unknown error',
        });
        this.cdr.detectChanges();
      },
    });
  }

  isPasswordValid(): boolean {
    return this.userValidator.isPasswordResetValid(
      this.resetPassword,
      this.confirmPassword,
      this.passwordMinLength,
    );
  }

  isPasswordLengthValid(password: string): boolean {
    return this.userValidator.isPasswordLengthValid(password, this.passwordMinLength);
  }

  isNameValid(name: string):boolean{
    return this.userValidator.isNameValid(name);
  }

  isUserNameValid(username: string):boolean{
    return this.userValidator.isUserNameValid(username);
  }

  createUser(): void {
    this.userService.createUser(this.newUser).subscribe({
      next: (res) => {
        this.showResponse(res);
        this.loadUsers();
        this.closeAddUser();
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.showResponse({
          success: false,
          message: err.error.detail ?? 'Unknown error',
        });
        this.cdr.detectChanges();
      }
    });
  }

  buildNewUser(): newUser {
    return {
      username: '',
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      role: '',
    };
  }

  openAddUser(): void {
    this.showAddUserForm = true;
  }

  closeAddUser(): void {
    this.showAddUserForm = false;
    this.newUser = this.buildNewUser();
  }

  isNewUserValid(): boolean {
    if (!this.newUser) return false;
    return this.userValidator.isNewUserValid(this.newUser, this.passwordMinLength);
  }

  isEmailValid(email: string): boolean {
    return this.userValidator.isEmailValid(email);
  }

  showResponse(res: any): void {

    this.successState = res.success ? 'success' : 'error';
    this.successMessage = res.message;

    this.successVisible = true;
    this.cdr.detectChanges();

    setTimeout(() => {
      this.successVisible = false;
      this.successMessage = null;
      this.cdr.detectChanges();
    }, 5000);
  }

}


