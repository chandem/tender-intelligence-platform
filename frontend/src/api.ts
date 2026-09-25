import { supabase } from "./auth";

export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", "Bearer " + token);
  const response = await fetch(API_BASE + path, { ...options, headers });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.detail || "Request failed");
  return result;
}

export type Tender = {
  id: string;
  title: string;
  tender_number?: string;
  organization?: string;
  location?: string;
  status: string;
  closing_date?: string;
};

export type TenderAnalysis = {
  summary: string;
  tender_type: string;
  organization: string;
  location: string;
  closing_date: string;
  eligibility: string[];
  required_documents: string[];
  technical_requirements: string[];
  financial_requirements: string[];
  equipment_requirements: string[];
  personnel_requirements: string[];
  important_dates: string[];
  risks_or_missing_information: string[];
};
