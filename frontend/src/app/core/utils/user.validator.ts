import { Injectable } from '@angular/core';

import { newUser } from '../models/user.models';

@Injectable({
  providedIn: 'root',
})
export class UserValidator {
  EMAILREGEX: RegExp = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  NAMEREGEX: RegExp = /^[A-Za-zÀ-ž\s'-]{3,15}$/;
  USERNAMEREGEX: RegExp = /^[a-zA-Z0-9._]{3,15}$/;
  MINLENGTH: number = 0;

  isNameValid(name: string): boolean {
    let n: string = name.trim();
    return n.length > this.MINLENGTH && !this.NAMEREGEX.test(n);
  }

  isUserNameValid(username: string): boolean {
    let u: string = username.trim();
    return u.length > this.MINLENGTH && !this.USERNAMEREGEX.test(u);
  }

  isEmailValid(mail: string): boolean {
    let m: string = mail.trim();
    return m.length > this.MINLENGTH && !this.EMAILREGEX.test(m);
  }

  isPasswordLengthValid(password: string, pwLength: number): boolean {
    let p: string = password.trim();
    return this.MINLENGTH < p.length && p.length < pwLength;
  }

  isPasswordResetValid(resetPw: string, confirmPw: string, pwLength: number): boolean {
    let r: string = resetPw.trim();
    let c: string = confirmPw.trim();
    return r.length >= pwLength && r === c;
  }

  isNewUserValid(user: newUser, pwLength: number): boolean {
    return (
      user.username.trim() !== '' &&
      user.first_name.trim() !== '' &&
      user.last_name.trim() !== '' &&
      this.EMAILREGEX.test(user.email.trim()) &&
      user.password.trim().length >= pwLength &&
      user.role.trim() !== ''
    );
  }
}


