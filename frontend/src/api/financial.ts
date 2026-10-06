import { api } from './client'

export type StatementLine = {
  id: number
  statement: number
  line_type: string
  reference_type?: string
  reference_id?: string
  description: string
  quantity?: number
  unit_rate?: number
  amount: number
  currency: string
  created_at: string
}

export type FinancialStatement = {
  id: number
  project: number
  project_detail?: { id: number; name: string; project_code: string }
  statement_number: string
  period_start: string
  period_end: string
  currency: string
  total_billable: number
  total_invoiced: number
  current_amount: number
  tax_amount?: number
  total_due: number
  status: 'draft' | 'approved' | 'sent' | 'paid' | 'partial'
  approved_by?: number
  approved_at?: string
  locked_at?: string
  lines?: StatementLine[]
  created_at: string
  updated_at: string
}

export const financialApi = {
  list: () => api.get<FinancialStatement[]>('/mts/statements/').then(r => r.data),
  retrieve: (id: number) => api.get<FinancialStatement>(`/mts/statements/${id}/`).then(r => r.data),
  create: (data: Partial<FinancialStatement>) => api.post<FinancialStatement>('/mts/statements/', data).then(r => r.data),
  update: (id: number, data: Partial<FinancialStatement>) => api.put<FinancialStatement>(`/mts/statements/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<FinancialStatement>) => api.patch<FinancialStatement>(`/mts/statements/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/mts/statements/${id}/`),
  approve: (id: number) => api.post(`/mts/statements/${id}/approve/`).then(r => r.data),
  lock: (id: number) => api.post(`/mts/statements/${id}/lock/`).then(r => r.data),
}
