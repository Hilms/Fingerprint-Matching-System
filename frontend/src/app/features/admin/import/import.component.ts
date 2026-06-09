import { Component, ChangeDetectorRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { ImportService } from '../../../core/services/import.service';

@Component({
  selector: 'app-import',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule],
  templateUrl: './import.html',
  styleUrls: ['./import.css'],
})
export class ImportComponent {
  fingerprintFiles: File[] = [];
  csvFile: File | null = null;

  importResult: any = null;

  private autoDismissTimer: any;

  @ViewChild('folderInput') folderInput!: any;
  @ViewChild('csvInput') csvInput!: any;

  constructor(
    private importService: ImportService,
    private cdr: ChangeDetectorRef,
  ) {}

  onFolderSelected(event: any) {
    this.fingerprintFiles = Array.from(event.target.files);
  }

  onCsvSelected(event: any) {
    this.csvFile = event.target.files[0];
  }

  import() {
    if (!this.csvFile || this.fingerprintFiles.length === 0) return;

    this.importService.importDataset(this.csvFile, this.fingerprintFiles).subscribe({
      next: (res) => {

        // SHOW RESULT FIRST
        this.importResult = res;
        // CLEAR INPUTS
        this.resetInputs();
        // OPTIONAL auto-hide result
        setTimeout(() => {
          this.dismissResult();
        }, 20000);
      },
      error: (err) => {
        console.error(err);
      },
    });
  }

  resetInputs() {
    this.fingerprintFiles = [];
    this.csvFile = null;

    if (this.folderInput) {
      this.folderInput.nativeElement.value = '';
    }

    if (this.csvInput) {
      this.csvInput.nativeElement.value = '';
    }
    this.cdr.detectChanges();
  }

  dismissResult() {
    clearTimeout(this.autoDismissTimer);
    this.importResult = null;
    this.cdr.detectChanges();
  }
}
