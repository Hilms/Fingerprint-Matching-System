import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environment';
import { Observable } from 'rxjs';

import { Subject, SubjectCreate, SubjectUpdate } from '../models/fingerprint.models';

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
  createSubject(data: SubjectCreate) {
    return this.http.post(`${this.api}/subject/admin/create`, data);
  }

  updateSubject(externalId: number, data: SubjectUpdate) {
    return this.http.patch(`${this.api}/subject/admin/update/id/${externalId}`, data);
  }

  deleteSubject(externalId: number) {
    return this.http.delete(`${this.api}/subject/admin/delete/id/${externalId}`);
  }
}
