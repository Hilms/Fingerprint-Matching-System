import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environment';
import { Observable } from 'rxjs';

import { Fingerprint, FingerprintCreate } from '../models/fingerprint.models';

@Injectable({
  providedIn: 'root',
})
export class FingerprintService {
  private api = `${environment.apiUrl}`;

  constructor(private http: HttpClient) {}

  // -------------------------
  // SINGLE ITEM
  // -------------------------

  getFingerprintsBySubjectId(external_id: number): Observable<Fingerprint[]> {
    return this.http.get<Fingerprint[]>(`${this.api}/fingerprints/id/${external_id}`);
  }

  getFingerprints(): Observable<Fingerprint[]> {
    return this.http.get<Fingerprint[]>(`${this.api}/fingerprints/all`);
  }

  getFingerprintImg(filename: string): Observable<Blob> {
    return this.http.get(`${this.api}/fingerprints/image/${filename}`, {
      responseType: 'blob'
    });
  }

  // -------------------------
  // MATCH (UPLOAD FOR SEARCH)
  // -------------------------
  matchFingerprint(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(`${this.api}/fingerprints/match`, formData);
  }

  // -------------------------
  // ADMIN UPLOAD (image + subject)
  // -------------------------
  uploadFingerprint(externalId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(
      `${this.api}/fingerprints/admin/upload?external_id=${externalId}`,
      formData,
    );
  }

  // -------------------------
  // MANUAL CREATE
  // -------------------------
  createFingerprint(data: FingerprintCreate) {
    return this.http.post(`${this.api}/fingerprints/admin/create`, data);
  }

  // -------------------------
  // DELETE
  // -------------------------
  deleteFingerprint(id: number) {
    return this.http.delete(`${this.api}/fingerprints/admin/delete/id/${id}`);
  }
}
