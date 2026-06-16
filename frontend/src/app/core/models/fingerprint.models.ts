/* SUBJECT MODELS */

export interface Subject {
  external_id: number;
  first_name: string;
  last_name: string;
  age: number;
  address: string;
  city: string;
  country: string;
  phone_number: string;
  has_fingerprints: boolean;
  created_at: string;
}

export interface SubjectCreate {
  external_id: number | null;
  first_name?: string;
  last_name?: string;
  age?: number | null;
  address?: string;
  city?: string;
  country?: string;
  phone_number?: string;
}

export interface SubjectUpdate {
  first_name?: string;
  last_name?: string;
  age?: number;
  address?: string;
  city?: string;
  country?: string;
  phone_number?: string;
}

/* FINGERPRINT MODELS */

export interface Fingerprint {
  id: number;
  subject_external_id: number;
  image_url: string;
  sex: string;
  hand: string;
  finger: string;
  filename: string;
  created_at: string;
}

export interface FingerprintCreate {
  subject_external_id: number | null;
  sex: string;
  hand: string;
  finger: string;
  filename: string;
  image: File | null;
}
