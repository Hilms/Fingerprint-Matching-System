import { Component, ChangeDetectorRef, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { MatchingService } from '../../core/services/matching.service'
import { Subject, Fingerprint, MatchingResult} from '../../core/models/matching.models';

@Component({
  selector: 'app-matching',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './matching.html',
  styleUrls: ['./matching.css'],
})
export class MatchingComponent {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  constructor(
    private matchingService: MatchingService,
    private cdr: ChangeDetectorRef,
  ) {}

  /* =========================
     UI STATE
  ========================= */

  uploadedImage: string | null = null;
  selectedFile: File | null = null;

  resultImage: string | null = null;

  isSearching: boolean = false;

  matchingResult: MatchingResult | null = null;
  subject: Subject | null = null;
  fingerprint: Fingerprint | null = null;

  /* =========================
     FILE SELECT
  ========================= */

  openFileDialog(): void {
    this.fileInput.nativeElement.click();
  }

  onFingerprintSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];

    const reader = new FileReader();

    reader.onload = () => {
      // IMPORTANT: force Angular update-safe assignment
      this.uploadedImage = reader.result as string;

      // reset previous result
      this.resultImage = null;
      this.matchingResult = null;

      this.cdr.detectChanges();
    };

    reader.readAsDataURL(file);
    this.cdr.detectChanges();
  }

  /* =========================
     SEARCH
  ========================= */

  searchFingerprint(): void {
    if (!this.uploadedImage) {
      return;
    }

    this.isSearching = true;

    /*
      TODO:
      Call your API here.

      Example:

      this.fingerprintService.search(this.selectedFile)
        .subscribe(...)
    */

    // MOCK RESPONSE

    setTimeout(() => {
      this.resultImage = this.uploadedImage;

      this.matchingResult = {
        accuracy: 96.42,
        total_matches: 1,
        query_minutiae_count: 84,
        candidate_minutiae_count: 89,
        matched_points: 77,
      };

      this.subject = {
        external_id: 1001,
        first_name: 'John',
        last_name: 'Doe',
        age: 34,
        address: 'Main Street 10',
        city: 'Berlin',
        country: 'Germany',
        phone_number: '+49 123456789',
      };

      this.fingerprint = {
        subject_external_id: 1001,
        sex: 'M',
        hand: 'Right',
        finger: 'Index',
        filename: 'SUB-1001_M_R_Index.bmp',
      };
      this.isSearching = false;
      this.cdr.detectChanges();
    }, 3000);
  }

  /* =========================
     RESET
  ========================= */

  reset(): void {

    this.isSearching = false;

    this.subject = null;
    this.fingerprint = null;

    this.resetUpload();

  }

  resetUpload(): void {
    this.uploadedImage = null;
    this.selectedFile = null;

    this.resultImage = null;
    this.matchingResult = null;

    // reset file input so same file can be selected again
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }

    this.cdr.detectChanges();
  }
}

