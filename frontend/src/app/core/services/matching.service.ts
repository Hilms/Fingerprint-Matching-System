import { Injectable } from '@angular/core';
import { environment } from '../../../environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class MatchingService {
  private api: string = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMatchings(image: File):Observable<any> {
    const data = new FormData();
    data.append('file', image);
    return this.http.post(`${this.api}/fingerprints/match`, data);
  }

  getFingerprintImg(filename: string): Observable<Blob> {
    return this.http.get(`${this.api}/fingerprints/image/${filename}`, {
      responseType: 'blob',
    });
  }
}
