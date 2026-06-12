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
import { Subject , Fingerprint} from '../../core/models/fingerprint.models';

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

  subjectColumns = [
    'external_id',
    'first_name',
    'last_name',
    'age',
    'country',
    'has_fingerprints',
    'actions',
  ];

  /* FINGERPRINTS */
  fingerprints: Fingerprint[] = [];
  fingerprintDataSource = new MatTableDataSource<Fingerprint>([]);
  fingerprintSearchQuery = '';

  selectedFingerprint: Fingerprint | null = null;

  fingerprintColumns = [
    'id',
    'hand',
    'finger',
    'sex',
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
    private cdr: ChangeDetectorRef,
  ) {}

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

  searchSubjects(): void {

  }

  resetSubjects(): void {
    this.loadSubjects();
  }

  selectSubject(subject: Subject): void {
    this.selectedSubject = subject;

    // sync fingerprint filter
    this.fingerprintSearchQuery = subject.external_id.toString();
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

  searchFingerprints(): void {
    let q: string = this.fingerprintSearchQuery;

    if (this.selectedSubject) {
      q = `${q} ${this.selectedSubject.external_id}`;
    }

  }

  resetFingerprints(): void {
    this.fingerprintSearchQuery = '';
    this.loadFingerprints();
  }

  selectFingerprint(fp: Fingerprint): void {
    this.selectedFingerprint = fp;

    // sync subject selection (reverse relation)
    const subject = this.subjects.find(
      s => s.external_id === fp.subject_external_id
    );

    if (subject) {
      this.selectedSubject = subject;
    }
  }

  /* =========================
     VIEW (IMAGE MODAL)
  ========================= */

  viewFingerprint(fp: Fingerprint): void {
    this.selectedFingerprint = fp;
  }

  closeFingerprintView(): void {
    this.selectedFingerprint = null;
  }

  /* =========================
     ADD FINGERPRINT
  ========================= */

  openAddFingerprint(): void {
    this.showFingerprintForm = true;

    this.newFingerprint.subject_external_id =
      this.selectedSubject?.external_id ?? null;

    setTimeout(() => {
      document.getElementById('fingerprintForm')?.scrollIntoView({
        block: 'nearest'
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

  deleteFingerprint(fp: Fingerprint): void {
    if (!confirm('Delete fingerprint?')) return;

    this.fingerprintService.deleteFingerprint(fp.id).subscribe({
      next: () => {
        this.showSuccess('Deleted');
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
