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

import { SubjectService } from '../../core/services/fingerprint.subject.service';
import { FingerprintService } from '../../core/services/fingerprint.fingerprint.service';
import { AuthService } from '../../core/services/auth.service';
import {
  Subject,
  SubjectUpdate,
  Fingerprint,
  SubjectCreate,
  FingerprintCreate,
  LatestSubjectIdResponse,
} from '../../core/models/fingerprint.models';
import { FingerprintSubjectValidator } from '../../core/utils/fingerprint.subject.validator';

@Component({
  selector: 'app-fingerprint',
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
  templateUrl: './fingerprint.html',
  styleUrls: ['./fingerprint.css'],
})
export class FingerprintComponent implements OnInit {

  constructor(
      private subjectService: SubjectService,
      private fingerprintService: FingerprintService,
      private auth: AuthService,
      private subjectValidator: FingerprintSubjectValidator,
      private cdr: ChangeDetectorRef,
  ) {}


  isAdmin: boolean = false;

  successVisible: boolean = false;
  successMessage: string | null = null;
  successState: 'success' | 'error' = 'success';

  /* SUBJECTS */
  subjects: Subject[] = [];
  subjectDataSource = new MatTableDataSource<Subject>([]);
  subjectSearchQuery: string = '';
  selectedSubject: Subject | null = null;
  originalSubject: Subject | null = null;
  editingSubject: SubjectUpdate | null = null;

  newSubject: SubjectCreate = {
    external_id: null,
    first_name: '',
    last_name: '',
    age: null,
    address: '',
    city: '',
    country: '',
    phone_number: '',
  };

  showNewSubjectForm: boolean = false;

  subjectColumns: string[] = [
    'external_id',
    'first_name',
    'last_name',
    'age',
    'address',
    'city',
    'country',
    'phone_number',
    'has_fingerprints',
    'created_at',
    'actions',
  ];

  /* FINGERPRINTS */
  fingerprints: Fingerprint[] = [];
  fingerprintDataSource = new MatTableDataSource<Fingerprint>([]);
  fingerprintSearchQuery: string = '';

  selectedFingerprint: Fingerprint | null = null;
  viewImg: string | null = null;
  image_url: string | null = null;

  fingerprintColumns: string[] = [
    //'id',
    'subject_external_id',
    'sex',
    'hand',
    'finger',
    'filename',
    'created_at',
    'actions',
  ];

  /* ADD / EDIT FINGERPRINT */
  showFingerprintForm: boolean = false;

  newFingerprint: FingerprintCreate = {
    subject_external_id: null as number | null,
    sex: '',
    hand: '',
    finger: '',
    filename: '',
    image: null as File | null,
  };

  ngOnInit(): void {
    this.isAdmin = this.auth.get_role() === 'admin';

    this.loadSubjects();
    this.loadFingerprints();
  }

  /* =========================
     SUBJECTS
  ========================= */

  loadSubjects(): void {
    this.subjectService.getSubjects().subscribe({
      next: (res: Subject[]): void => {
        this.subjects = res;
        this.subjectDataSource.data = res;
      },
      error: (err: HttpErrorResponse): void => this.handleError(err),
    });
  }

  searchSubjects(query: string): void {
    this.subjectService.searchSubjects(query).subscribe({
      next: (res: Subject[]): void => {
        this.subjects = res;
        this.subjectDataSource.data = res;
      },
      error: (err: HttpErrorResponse): void => this.handleError(err),
    });
  }

  resetSubjects(): void {
    this.loadSubjects();
  }

  getSubject(subject_external_id: number): void {
    this.subjectService.getSubject(subject_external_id).subscribe({
      next: (res: Subject) => {
        this.subjects = [res];
        this.subjectDataSource.data = [res];
      },
      error: (err: HttpErrorResponse): void => this.handleError(err),
    });
  }

  openNewSubjectForm(): void {
    this.showNewSubjectForm = true;

    this.subjectService.getLatestSubjectId().subscribe({
      next: (res: LatestSubjectIdResponse): void => {
        if (!res.latest_subject_id) return;
        this.newSubject.external_id = res.latest_subject_id + 1;
        this.cdr.detectChanges();
      },
      error: (err: any): void => this.handleError(err),
    });

    setTimeout((): void => {
      document.getElementById('newSubjectForm')?.scrollIntoView({
        block: 'nearest',
      });
    }, 100);
  }

  closeNewSubjectForm(): void {
    this.showNewSubjectForm = false;

    this.newSubject = {
      external_id: null,
      first_name: '',
      last_name: '',
      age: null,
      address: '',
      city: '',
      country: '',
      phone_number: '',
    };

    this.newFingerprint = {
      subject_external_id: null,
      sex: '',
      hand: '',
      finger: '',
      filename: '',
      image: null,
    };
  }

  uploadNewSubjectValid(): boolean{
    const a = this.newSubject.external_id;
    const b = this.newFingerprint.subject_external_id;

    return !!a && (!b || a === b)
  };

  uploadNewSubject(): void  {
    this.subjectService.uploadSubject(this.newSubject, this.newFingerprint).subscribe({
      next: (res: Object): void => {
        this.showResponse(res)
        this.loadSubjects();
        this.loadFingerprints();
        this.closeNewSubjectForm();
        this.cdr.detectChanges();
      },
      error: (err: any): void => this.handleError(err),
    });
  }

  onSubjectFingerprintSelected(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;

    this.newFingerprint.image = file;
    this.newFingerprint.filename = file.name;

    this.parseFilename(file.name);

    this.newSubject.external_id = this.newFingerprint.subject_external_id;
  }

  openUpdateSubjectForm(s: Subject): void {
    this.originalSubject = s;

    this.editingSubject = {
      first_name: s.first_name,
      last_name: s.last_name,
      age: s.age,
      address: s.address,
      city: s.city,
      country: s.country,
      phone_number: s.phone_number,
    };

    setTimeout(() => {
      document.getElementById('updateSubjectForm')?.scrollIntoView({
        block: 'nearest',
      });
    }, 100);
  }

  closeUpdateSubjectForm(): void {
    this.editingSubject = null;
    this.originalSubject = null;
  }

  resetEditSubject(): void {
    if (!this.originalSubject) return;

    this.editingSubject = {
      first_name: this.originalSubject.first_name,
      last_name: this.originalSubject.last_name,
      age: this.originalSubject.age,
      address: this.originalSubject.address,
      city: this.originalSubject.city,
      country: this.originalSubject.country,
      phone_number: this.originalSubject.phone_number,
    };
  }

  hasSubjectChanges(): boolean {
    return (
      Object.keys(this.getSubjectChanges(this.editingSubject!, this.originalSubject!)).length > 0
    );
  }

  getSubjectChanges(editing: SubjectUpdate, original: Subject): SubjectUpdate {
    const changes: SubjectUpdate = {};

    if (editing.first_name !== original.first_name) changes.first_name = editing.first_name;

    if (editing.last_name !== original.last_name) changes.last_name = editing.last_name;

    if (editing.age !== original.age) changes.age = editing.age;

    if (editing.address !== original.address) changes.address = editing.address;

    if (editing.city !== original.city) changes.city = editing.city;

    if (editing.country !== original.country) changes.country = editing.country;

    if (editing.phone_number !== original.phone_number) changes.phone_number = editing.phone_number;

    return changes;
  }

  updateSubject(): void {
    if (!this.originalSubject || !this.editingSubject) return;

    const changes = this.getSubjectChanges(this.editingSubject, this.originalSubject);

    if (Object.keys(changes).length === 0) return;

    this.subjectService.updateSubject(this.originalSubject.external_id, changes).subscribe({
      next: (res: Object): void => {
        this.showResponse(res);
        this.closeUpdateSubjectForm();
        this.loadSubjects();
        this.cdr.detectChanges();
      },
      error: (err: any): void => this.handleError(err),
    });
  }

  isNameValid(name?: string): boolean {
    return !!name && this.subjectValidator.isNameValid(name);
  }

  isAgeValid(age?: number): boolean {
    return !!age && this.subjectValidator.isAgeValid(age);
  }

  isAddressValid(address?: string): boolean {
    return !!address && this.subjectValidator.isAddressValid(address);
  }

  isCityValid(city?: string): boolean {
    return !!city && this.subjectValidator.isCityValid(city);
  }

  isCountryValid(country?: string): boolean {
    return !!country && this.subjectValidator.isCountryValid(country);
  }

  isPhoneValid(number?: string): boolean {
    return !!number && this.subjectValidator.isPhoneValid(number);
  }

  isValid(subject: SubjectUpdate): boolean {
    if (!subject) return false;

    return (
      this.validateOptional(subject.first_name, (v: string): boolean => this.isNameValid(v)) &&
      this.validateOptional(subject.last_name, (v: string): boolean => this.isNameValid(v)) &&
      this.validateOptional(subject.age, (v: number): boolean => this.isAgeValid(v)) &&
      this.validateOptional(subject.address, (v: string): boolean => this.isAddressValid(v)) &&
      this.validateOptional(subject.city, (v: string): boolean => this.isCityValid(v)) &&
      this.validateOptional(subject.country, (v: string): boolean => this.isCountryValid(v)) &&
      this.validateOptional(subject.phone_number, (v: string): boolean => this.isPhoneValid(v))
    );
  }

  private validateOptional<T>(value: T | undefined | null, validator: (v: T) => boolean): boolean {
    // not changed → ignore
    if (value === undefined || value === null) return true;

    // empty string is invalid (user actively cleared input)
    if (typeof value === 'string' && value.trim() === '') return false;

    return validator(value);
  }

  canUpdate(): boolean {
    if (!this.editingSubject || !this.originalSubject) return false;

    const changes: SubjectUpdate = this.getSubjectChanges(
      this.editingSubject,
      this.originalSubject,
    );

    if (Object.keys(changes).length === 0) return false;

    return this.isValid(changes);
  }

  /* =========================
     FINGERPRINTS
  ========================= */

  loadFingerprints(): void {
    this.fingerprintService.getFingerprints().subscribe({
      next: (res: Fingerprint[]) => {
        this.fingerprints = res;
        this.fingerprintDataSource.data = res;
      },
      error: (err: HttpErrorResponse) => this.handleError(err),
    });
  }

  getFingerprints(external_id: number): void {
    this.fingerprintService.getFingerprintsBySubjectId(external_id).subscribe({
      next: (res: Fingerprint[]) => {
        this.fingerprints = res;
        this.fingerprintDataSource.data = res;
      },
      error: (err: HttpErrorResponse): void => this.handleError(err),
    });
  }

  resetFingerprints(): void {
    this.loadFingerprints();
  }

  selectFingerprint(fingerprint: Fingerprint): void {
    this.selectedFingerprint = fingerprint;

    // sync subject selection (reverse relation)
    const subject = this.subjects.find(
      (s: Subject): boolean => s.external_id === fingerprint.subject_external_id,
    );

    if (subject) {
      this.selectedSubject = subject;
    }
  }

  /* =========================
     VIEW (IMAGE MODAL)
  ========================= */

  loadFingerprintImage(filename: string): void {
    this.fingerprintService.getFingerprintImg(filename).subscribe({
      next: (blob: Blob): void => {
        if (this.image_url) {
          URL.revokeObjectURL(this.image_url);
        }

        this.image_url = URL.createObjectURL(blob);

        this.cdr.detectChanges();
      },
      error: (err: HttpErrorResponse): void => this.handleError(err),
    });
  }

  viewFingerprintImg(filename: string): void {
    this.viewImg = filename;
    this.loadFingerprintImage(filename);
    this.cdr.detectChanges();
  }

  closeFingerprintView(): void {
    this.viewImg = null;
    this.image_url = null;
  }

  /* =========================
     ADD FINGERPRINT
  ========================= */

  openAddFingerprintForSubject(subject: Subject): void {
    this.showFingerprintForm = true;

    this.newFingerprint.subject_external_id = subject.external_id ?? null;

    setTimeout(() => {
      document.getElementById('fingerprintForm')?.scrollIntoView({
        block: 'nearest',
      });
    }, 100);
  }

  closeFingerprintForm(): void {
    this.showFingerprintForm = false;

    this.newFingerprint = {
      subject_external_id: null,
      sex: '',
      hand: '',
      finger: '',
      filename: '',
      image: null,
    };
  }

  onFileSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;

    this.newFingerprint.image = file;
    this.newFingerprint.filename = file.name;

    this.parseFilename(file.name);
  }

  parseFilename(filename: string): void {
    const nameWithoutExt: string = filename.split('.')[0];
    const parts: string[] = nameWithoutExt.split('_');

    if (parts.length < 6) return;

    this.newFingerprint.subject_external_id = Number(parts[0]);
    this.newFingerprint.sex = parts[2];
    this.newFingerprint.hand = parts[3];
    this.newFingerprint.finger = parts[4];
  }

  uploadNewFingerprint(): void {
    this.fingerprintService.uploadFingerprint(this.newFingerprint).subscribe({
      next: (res: any): void => {
        this.showResponse(res);
        this.closeFingerprintForm();
        this.loadFingerprints();
        this.cdr.detectChanges();
      },
      error: (err: any): void => this.handleError(err),
    });
  }

  /* =========================
     ACTIONS
  ========================= */

  deleteFingerprint(fingerprint_id: number): void {
    if (!confirm('Delete fingerprint permenantly?')) return;

    this.fingerprintService.deleteFingerprint(fingerprint_id).subscribe({
      next: (res) => {
        this.showResponse(res);
        this.loadFingerprints();
        this.cdr.detectChanges();
      },
      error: (err: any): void => this.handleError(err),
    });
  }

  deleteSubject(subject_id: number): void {
    if (!confirm('Delete subject?\n This also deletes corresponding Fingerprints!')) return;

    this.subjectService.deleteSubject(subject_id).subscribe({
      next: (res: Object): void => {
        this.showResponse(res);
        this.loadSubjects();
        this.loadFingerprints();
        this.cdr.detectChanges();
      },
      error: (err: any): void => this.handleError(err),
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
  }
}
