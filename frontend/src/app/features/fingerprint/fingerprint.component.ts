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
import { Subject, SubjectUpdate, Fingerprint} from '../../core/models/fingerprint.models';

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
  isAdmin = false;

  successVisible = false;
  successMessage: string | null = null;
  successState: 'success' | 'error' = 'success';

  /* SUBJECTS */
  subjects: Subject[] = [];
  subjectDataSource = new MatTableDataSource<Subject>([]);
  subjectSearchQuery = '';
  selectedSubject: Subject | null = null;
  originalSubject: Subject | null = null;
  editingSubject: SubjectUpdate | null = null;

  subjectColumns = [
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
  fingerprintSearchQuery = '';

  selectedFingerprint: Fingerprint | null = null;
  viewImg: string | null = null;
  image_url: string | null = null;

  fingerprintColumns = [
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
  showFingerprintForm = false;

  newFingerprint = {
    subject_external_id: null as number | null,
    sex: '',
    hand: '',
    finger: '',
    filename: '',
    image: null as File | null,
  };

  constructor(
    private subjectService: SubjectService,
    private fingerprintService: FingerprintService,
    private auth: AuthService,
    private subjectValidator: FingerprintSubjectValidator,
    private cdr: ChangeDetectorRef,
  ) {}

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
      next: (res: Subject[]) => {
        this.subjects = res;
        this.subjectDataSource.data = res;
      },
      error: (err: HttpErrorResponse) => this.handleError(err),
    });
  }

  searchSubjects(query: string): void {
    this.subjectService.searchSubjects(query).subscribe({
      next: (res: Subject[]) => {
        this.subjects = res;
        this.subjectDataSource.data = res;
      },
      error: (err: HttpErrorResponse) => this.handleError(err),
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
      error: (err: HttpErrorResponse) => this.handleError(err),
    });
  }

  openUpdateSubject(s: Subject): void {
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

  closeUpdateSubject(): void {
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
      next: (res) => {
        this.showResponse(res);
        this.closeUpdateSubject();
        this.loadSubjects();
        this.cdr.detectChanges();
      },
      error: (err) => this.handleError(err),
    });
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
      error: (err: HttpErrorResponse) => this.handleError(err),
    });
  }

  resetFingerprints(): void {
    this.loadFingerprints();
  }

  selectFingerprint(fp: Fingerprint): void {
    this.selectedFingerprint = fp;

    // sync subject selection (reverse relation)
    const subject = this.subjects.find((s) => s.external_id === fp.subject_external_id);

    if (subject) {
      this.selectedSubject = subject;
    }
  }

  /* =========================
     VIEW (IMAGE MODAL)
  ========================= */

  loadFingerprintImage(filename: string): void {
    this.fingerprintService.getFingerprintImg(filename).subscribe({
      next: (blob: Blob) => {
        if (this.image_url) {
          URL.revokeObjectURL(this.image_url);
        }

        this.image_url = URL.createObjectURL(blob);

        this.cdr.detectChanges();
      },
      error: (err: HttpErrorResponse) => this.handleError(err),
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

  openAddFingerprint(): void {
    this.showFingerprintForm = true;

    this.newFingerprint.subject_external_id = this.selectedSubject?.external_id ?? null;

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

  createFingerprint(): void {
    this.fingerprintService.createFingerprint(this.newFingerprint).subscribe({
      next: () => {
        this.showSuccess('Fingerprint created');
        this.closeFingerprintForm();
      },
      error: (err: any) => this.handleError(err),
    });
  }

  /* =========================
     ACTIONS
  ========================= */

  deleteFingerprint(fingerprint_id: number): void {
    if (!confirm('Delete fingerprint?')) return;

    this.fingerprintService.deleteFingerprint(fingerprint_id).subscribe({
      next: () => {
        this.showSuccess('Fingerprint successfully deleted');
      },
      error: (err: any) => this.handleError(err),
    });
  }

  deleteSubject(subject_id: number): void {
    if (!confirm('Delete subject?\n This also deletes corresponding Fingerprints!')) return;

    this.subjectService.deleteSubject(subject_id).subscribe({
      next: () => {
        this.showSuccess('Subject and corresponding fingerprints successfully deleted');
      },
      error: (err: any) => this.handleError(err),
    });
  }

  /* =========================
     UI HELPERS
  ========================= */

  showSuccess(msg: string): void {
    this.successMessage = msg;
    this.successState = 'success';
    this.successVisible = true;

    setTimeout(() => {
      this.successVisible = false;
    }, 3000);
  }

  handleError(err: HttpErrorResponse): void {
    this.successMessage = err.error?.detail ?? 'Error';
    this.successState = 'error';
    this.successVisible = true;
  }
}
