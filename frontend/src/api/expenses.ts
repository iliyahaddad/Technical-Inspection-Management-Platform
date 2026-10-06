import { api } from './client'

export type Expense = {
  id: number
  inspector: number
  project: number
  assignment?: number
  expense_date: string
  category: string
  amount: number
  currency: string
  description?: string
  receipt?: string
  status: 'draft' | 'submitted' | 'approved' | 'rejected'
  submitted_at?: string
  approved_by?: number
  approved_at?: string
  created_at: string
  updated_at: string
}

export const expensesApi = {
  list: () => api.get<Expense[]>('/mts/expenses/').then(r => r.data),
  retrieve: (id: number) => api.get<Expense>(`/mts/expenses/${id}/`).then(r => r.data),
  create: (data: Partial<Expense>) => api.post<Expense>('/mts/expenses/', data).then(r => r.data),
  update: (id: number, data: Partial<Expense>) => api.put<Expense>(`/mts/expenses/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<Expense>) => api.patch<Expense>(`/mts/expenses/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/mts/expenses/${id}/`),
  submit: (id: number) => api.post(`/mts/expenses/${id}/submit/`).then(r => r.data),
  approve: (id: number) => api.post(`/mts/expenses/${id}/approve/`).then(r => r.data),
}
