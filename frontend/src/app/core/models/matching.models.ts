export interface Subject {
  external_id: number | null;
  first_name: string;
  last_name: string;
  age: number | null;
  address: string;
  city: string;
  country: string;
  phone_number: string;
}

export interface Fingerprint {
  subject_external_id: number | null;
  sex: string;
  hand: string;
  finger: string;
  filename: string;
}

export interface MatchingResult {
  accuracy: number | null;
  total_matches: number | null;
  query_minutiae_count: number | null;
  candidate_minutiae_count: number | null;
}
