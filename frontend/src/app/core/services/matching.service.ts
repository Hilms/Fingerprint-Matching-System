import { Injectable } from '@angular/core';
import { environment } from '../../../environment';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class MatchingService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMatchings(image: File) {

    const data = new FormData();

    data.append('fingerprint', image);

    return this.http.post(`${this.api}/imports/admin/dataset`, data);
  }
}
