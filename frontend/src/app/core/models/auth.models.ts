export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginResponse {
  refresh_token: string;
  access_token: string;
  token_type: string;
}

export interface RegisterResponse {
  message: string;
}
