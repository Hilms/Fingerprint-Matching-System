import { Component, ChangeDetectorRef, ViewChild, ElementRef, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { HttpErrorResponse } from '@angular/common/http';

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

  @ViewChild('queryImg') queryImg!: ElementRef<HTMLImageElement>;
  @ViewChild('queryCanvas') queryCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('candidateImg') candidateImg!: ElementRef<HTMLImageElement>;
  @ViewChild('candidateCanvas') candidateCanvas!: ElementRef<HTMLCanvasElement>;

  @HostListener('window:resize')
  onResize(): void {
    if (!this.candidateImg?.nativeElement) return;

    this.syncCanvasToImage();
    this.drawMinutiaes();
  }

  constructor(
    private matchingService: MatchingService,
    private cdr: ChangeDetectorRef,
  ) {}

  /* =========================
     UI STATE
  ========================= */
  successVisible: boolean = false;
  successMessage: string | null = null;
  successState: 'success' | 'error' = 'success';

  uploadedImage: string | null = null;
  selectedFile: File | null = null;

  resultImage: string | null = null;

  isSearching: boolean = false;

  /* =========================
     DATA
  ========================= */

  matchingResult: MatchingResult | null = null;
  subject: Subject | null = null;
  fingerprint: Fingerprint | null = null;

  matchedPoints: any;
  querySize: any;
  candidateSize: any;

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

    this.selectedFile = input.files[0];

    const reader = new FileReader();

    reader.onload = () => {
      // IMPORTANT: force Angular update-safe assignment
      // this is for preview - UI only
      this.uploadedImage = reader.result as string;

      // reset previous result
      this.resultImage = null;
      this.matchingResult = null;

      this.cdr.detectChanges();
    };

    reader.readAsDataURL(this.selectedFile);
    this.cdr.detectChanges();
  }

  /* =========================
     MATCHING
  ========================= */

  searchFingerprint(): void {
    if (!this.uploadedImage) {
      return;
    }

    this.isSearching = true;

    this.matchingService.getMatchings(this.selectedFile!).subscribe({
      next: (res: any): void => {
        if (!res.success) {
          this.isSearching = false;
          this.showResponse(res);
          return;
        }

        this.mapResponse(res.data);
        this.isSearching = false;
        this.loadFingerprintImage(this.fingerprint!.filename);
        this.cdr.detectChanges();
      },
      error: (err: any): void => {
        this.isSearching = false;
        this.handleError(err);
      },
    });
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

  private loadFingerprintImage(filename: string): void {
    this.matchingService.getFingerprintImg(filename).subscribe({
      next: (blob: Blob): void => {
        if (this.resultImage) {
          URL.revokeObjectURL(this.resultImage);
        }
        this.resultImage = URL.createObjectURL(blob);
        this.cdr.detectChanges();
      },
      error: (err: HttpErrorResponse): void => {
        this.handleError(err);
      },
    });
  }

  private mapResponse(data: any[]): void {
    const bestMatch = data[0];

    const result: any = bestMatch.result;
    this.matchingResult = this.mapResult(result);
    this.subject = this.mapSubject(bestMatch.subject);
    this.fingerprint = this.mapFingerprint(bestMatch.fingerprint);

    this.matchedPoints = result.matched_points;
    this.querySize = result.image_size.query;
    this.candidateSize = result.image_size.candidate;
  }

  private mapResult(result: any): MatchingResult {
    return {
      accuracy: result?.accuracy ? result.accuracy * 100 : 0,
      total_matches: result?.total_matches ?? 0,
      query_minutiae_count: result?.query_minutiae_count ?? 0,
      candidate_minutiae_count: result?.candidate_minutiae_count ?? 0,
    };
  }

  private mapSubject(subject: any): Subject {
    return {
      external_id: subject?.external_id ?? null,
      first_name: subject?.first_name ?? '',
      last_name: subject?.last_name ?? '',
      age: subject?.age ?? null,
      address: subject?.address ?? '',
      city: subject?.city ?? '',
      country: subject?.country ?? '',
      phone_number: subject?.phone_number ?? '',
    };
  }

  private mapFingerprint(fingerprint: any): Fingerprint {
    return {
      subject_external_id: fingerprint?.subject_external_id ?? null,
      sex: fingerprint?.sex ?? '',
      hand: fingerprint?.hand ?? '',
      finger: fingerprint?.finger ?? '',
      filename: fingerprint?.filename ?? '',
    };
  }

  onCandidateImageLoad(): void {
    this.syncCanvasToImage();
    this.drawMinutiaes();
  }

  syncCanvasToImage(): void {
    this.syncQueryCanvas();
    this.syncCandidateCanvas();
  }

  syncQueryCanvas(): void {
    const img = this.queryImg.nativeElement;
    const canvas = this.queryCanvas.nativeElement;
    const ctx = canvas.getContext('2d')!;

    const rect = img.getBoundingClientRect();

    // anvas MUST match rendered image size (NOT natural size)
    canvas.width = rect.width;
    canvas.height = rect.height;

    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
  }

  syncCandidateCanvas(): void {
    const img = this.candidateImg.nativeElement;
    const canvas = this.candidateCanvas.nativeElement;

    const rect = img.getBoundingClientRect();

    // anvas MUST match rendered image size (NOT natural size)
    canvas.width = rect.width;
    canvas.height = rect.height;

    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
  }

  drawMinutiaes(): void {
    if (!this.candidateImg || !this.queryImg) return;
    if (!this.matchedPoints) return;

    this.drawCandidateCanvas();
    this.drawQueryCanvas();
  }

  drawCandidateCanvas(): void {
    const img = this.candidateImg.nativeElement;
    const canvas = this.candidateCanvas.nativeElement;
    const ctx = canvas.getContext('2d')!;

    const container = canvas.parentElement!;

    const containerW: number = container.clientWidth;
    const containerH: number = container.clientHeight;

    const imgNaturalW: number = img.naturalWidth;
    const imgNaturalH: number = img.naturalHeight;

    // match CSS "contain"
    const scale: number = Math.min(containerW / imgNaturalW, containerH / imgNaturalH);

    const renderedW: number = imgNaturalW * scale;
    const renderedH: number = imgNaturalH * scale;

    const offsetX: number = (containerW - renderedW) / 2;
    const offsetY: number = (containerH - renderedH) / 2;

    // IMPORTANT: match canvas size to container
    canvas.width = containerW;
    canvas.height = containerH;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = 'red';
    ctx.fillStyle = 'red';

    this.matchedPoints.forEach((m: any, i: number): void => {
      const x: number = offsetX + m.candidate.x * scale;
      const y: number = offsetY + m.candidate.y * scale;

      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillText(String(i + 1), x + 6, y + 6);
    });
  }

  drawQueryCanvas(): void {
    const img = this.queryImg.nativeElement;
    const canvas = this.queryCanvas.nativeElement;
    const ctx = canvas.getContext('2d')!;

    const container = canvas.parentElement!;

    const containerW: number = container.clientWidth;
    const containerH: number = container.clientHeight;

    const imgNaturalW: number = img.naturalWidth;
    const imgNaturalH: number = img.naturalHeight;

    // SAME "contain" scaling logic
    const scale: number = Math.min(containerW / imgNaturalW, containerH / imgNaturalH);

    const renderedW: number = imgNaturalW * scale;
    const renderedH = imgNaturalH * scale;

    const offsetX: number = (containerW - renderedW) / 2;
    const offsetY: number = (containerH - renderedH) / 2;

    // canvas must match container
    canvas.width = containerW;
    canvas.height = containerH;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = 'red';
    ctx.fillStyle = 'red';

    this.matchedPoints.forEach((m: any, i: number): void => {
      const x: number = offsetX + m.query.x * scale;
      const y: number = offsetY + m.query.y * scale;

      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillText(String(i + 1), x + 6, y + 6);
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
    this.cdr.detectChanges();
  }
}

