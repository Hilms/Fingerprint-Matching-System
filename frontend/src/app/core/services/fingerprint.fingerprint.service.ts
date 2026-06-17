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
      responseType: 'blob',
    });
  }

  // -------------------------
  // ADMIN UPLOAD FINGERPRINT
  // -------------------------
  uploadFingerprint(fingerprint: FingerprintCreate): Observable<any> {
    const data = new FormData();

    data.append('external_id', String(fingerprint.subject_external_id!));
    data.append('file', fingerprint.image!);

    return this.http.post(`${this.api}/fingerprints/admin/upload`, data);
  }

  // -------------------------
  // ADMIN DELETE
  // -------------------------
  deleteFingerprint(id: number) {
    return this.http.delete(`${this.api}/fingerprints/admin/delete/id/${id}`);
  }
}
