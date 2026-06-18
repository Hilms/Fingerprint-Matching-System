import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environment';
import { Observable } from 'rxjs';

import {
  Subject,
  SubjectCreate,
  SubjectUpdate,
  LatestSubjectIdResponse,
  FingerprintCreate,
} from '../models/fingerprint.models';


@Injectable({
  providedIn: 'root',
})
export class SubjectService {
  private api = `${environment.apiUrl}`;

  constructor(private http: HttpClient) {}

  // -------------------------
  // PUBLIC
  // -------------------------
  searchSubjects(query: string): Observable<Subject[]> {
    return this.http.get<Subject[]>(`${this.api}/subjects/search?query=${query}`);
  }

  getSubjects(): Observable<Subject[]> {
    return this.http.get<Subject[]>(`${this.api}/subjects/all`);
  }

  getSubject(externalId: number): Observable<Subject> {
    return this.http.get<Subject>(`${this.api}/subjects/id/${externalId}`);
  }

  // -------------------------
  // ADMIN
  // -------------------------

  private cleanObject<T>(obj: T): T {
    return Object.fromEntries(
      Object.entries(obj as Record<string, any>).map(([key, value]) => [
        key,
        typeof value === 'string' ? value.trim() || null : value,
      ]),
    ) as T;
  }

  uploadSubject(subject: SubjectCreate, fingerprint: FingerprintCreate) {

    const cleanedSubject = this.cleanObject(subject);

    const data = new FormData();

    data.append('subject_data', JSON.stringify(cleanedSubject));

    if(fingerprint.filename){
      data.append('file', fingerprint.image!);
    }

    return this.http.post(`${this.api}/fingerprints/admin/upload`, data);
  }

  updateSubject(externalId: number, data: SubjectUpdate) {
    return this.http.patch(`${this.api}/subjects/admin/update/id/${externalId}`, data);
  }

  deleteSubject(externalId: number) {
    return this.http.delete(`${this.api}/subjects/admin/delete/id/${externalId}`);
  }

  getLatestSubjectId() {
    return this.http.get<LatestSubjectIdResponse>(`${this.api}/subjects/admin/latest_id`);
  }
}
