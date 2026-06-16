import { Injectable } from '@angular/core';
import { SubjectUpdate } from '../models/fingerprint.models';

@Injectable({
  providedIn: 'root',
})
export class FingerprintSubjectValidator {
  NAMEREGEX: RegExp = /^[A-Za-zÀ-ž\s'-]{3,12}$/;
  PHONEREGEX: RegExp = /^[+0-9]{6,10}$/;
  CITYREGEX: RegExp = /^[A-Za-zÀ-ž\s'-]{2,10}$/;
  COUNTRYREGEX: RegExp = /^[A-Za-zÀ-ž\s'-]{2,15}$/;
  ADDRESSREGEX: RegExp = /^[A-Za-zÀ-ž0-9\s.'\-#,\/]{3,50}$/;

  MIN_AGE = 0;
  MAX_AGE = 100;

  isNameValid(name: string): boolean {
    if (!name) return false;
    const n = name.trim();
    return this.NAMEREGEX.test(n);
  }

  isAgeValid(age: number | null | undefined): boolean {
    if (age === null || age === undefined) return false;
    if (!Number.isInteger(age)) return false;
    return age >= this.MIN_AGE && age <= this.MAX_AGE;
  }

  isPhoneValid(phone: string): boolean {
    if (!phone) return false;
    return this.PHONEREGEX.test(phone.trim());
  }

  isAddressValid(address: string): boolean {
    if (!address) return false;
    const a = address.trim();
    return this.ADDRESSREGEX.test(a);
  }

  isCityValid(city: string): boolean {
    if (!city) return false;
    return this.CITYREGEX.test(city.trim());
  }

  isCountryValid(country: string): boolean {
    if (!country) return false;
    return this.COUNTRYREGEX.test(country.trim());
  }

}
