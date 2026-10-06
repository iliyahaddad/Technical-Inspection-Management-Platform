import { api } from './client'

export type Assignment = {
  id: number
  notification: number
  notification_detail?: { id: number; notification_number: string; inspection_request: number }
  inspector: number
  inspector_detail?: { id: number; user: number; employment_type: string }
  proposed_by: number
  approved_by?: number
  status: 'proposed' | 'approved' | 'notified' | 'accepted' | 'declined' | 'confirmed' | 'completed' | 'cancelled'
  proposed_at: string
  approved_at?: string
  notified_at?: string
  responded_at?: string
  completed_at?: string
  cancellation_reason?: string
  created_at: string
  updated_at: string
}

export const assignmentsApi = {
  list: () => api.get<Assignment[]>('/inspections/assignments/').then(r => r.data),
  retrieve: (id: number) => api.get<Assignment>(`/inspections/assignments/${id}/`).then(r => r.data),
  create: (data: Partial<Assignment>) => api.post<Assignment>('/inspections/assignments/', data).then(r => r.data),
  update: (id: number, data: Partial<Assignment>) => api.put<Assignment>(`/inspections/assignments/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<Assignment>) => api.patch<Assignment>(`/inspections/assignments/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/inspections/assignments/${id}/`),
}
