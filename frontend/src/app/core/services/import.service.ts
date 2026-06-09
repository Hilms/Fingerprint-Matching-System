import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environment';

@Injectable({ providedIn: 'root' })
export class ImportService {

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  importDataset(subjectsCsv: File, fingerprints: File[]) {

    const formData = new FormData();

    formData.append('subjects_csv', subjectsCsv);

    fingerprints.forEach(file => {
      formData.append('fingerprints', file);
    });

    return this.http.post(
      `${this.api}/imports/admin/dataset`,
      formData
    );
  }
}
