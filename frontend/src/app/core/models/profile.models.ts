export interface SelfUserUpdate {
  email?: string;
  first_name?: string;
  last_name?: string;
}

export interface PasswordUpdate {
  current_password: string;
  new_password: string;
}
