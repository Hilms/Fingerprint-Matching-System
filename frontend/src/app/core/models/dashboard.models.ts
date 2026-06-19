export interface DashboardSummary {
  total_subjects: number;
  total_fingerprints: number;
  total_countries: number;
  total_cities: number;
  total_with_age?: number;
}

/* =========================
   CORE DISTRIBUTIONS
========================= */

export interface GenderStat {
  gender: string;
  count: number;
}

export interface FingerStat {
  finger: string;
  count: number;
}

export interface HandStat {
  hand: string;
  count: number;
}

export interface CountryStat {
  country: string;
  count: number;
}

export interface CityStat {
  city: string;
  count: number;
}

/* =========================
   STACKED ANALYTICS
========================= */

export interface CountryGenderStat {
  country: string;
  gender: string;
  count: number;
}

export interface CityGenderStat {
  city: string;
  gender: string;
  count: number;
}

/* =========================
   AGE ANALYTICS
========================= */

export interface AgeStat {
  age_group: string;
  count: number;
}

export interface AgeGenderStat {
  age_group: string;
  gender: string;
  count: number;
}

/* =========================
   USER DASHBOARD RESPONSE
========================= */

export interface DashboardResponse {
  summary: DashboardSummary;

  gender: GenderStat[];
  fingers: FingerStat[];
  hands: HandStat[];

  countries: CountryStat[];
  cities: CityStat[];

  country_gender: CountryGenderStat[];
  city_gender: CityGenderStat[];

  age: AgeStat[];
  age_gender: AgeGenderStat[];
}

/* =========================
   ADMIN MODELS
========================= */

export interface UserSummary {
  total_users: number;
  active_users: number;
  inactive_users: number;
  admin_users: number;
  normal_users: number;
}

export interface UserRoleStat {
  role: string;
  count: number;
}

export interface UserRegistrationStat {
  date: string;
  count: number;
}

export interface AdminDashboardResponse {
  summary: UserSummary;
  roles: UserRoleStat[];
  registrations: UserRegistrationStat[];
}
