import { api } from './client'

export type InspectionVisit = {
  id: number
  assignment: number
  assignment_detail?: { id: number; inspector: number; status: string }
  visit_number: string
  scheduled_start: string
  scheduled_end: string
  actual_start?: string
  actual_end?: string
  location?: number
  status: 'scheduled' | 'in_progress' | 'completed' | 'postponed' | 'cancelled'
  notes?: string
  created_at: string
  updated_at: string
}

export const visitsApi = {
  list: () => api.get<InspectionVisit[]>('/inspections/visits/').then(r => r.data),
  retrieve: (id: number) => api.get<InspectionVisit>(`/inspections/visits/${id}/`).then(r => r.data),
  create: (data: Partial<InspectionVisit>) => api.post<InspectionVisit>('/inspections/visits/', data).then(r => r.data),
  update: (id: number, data: Partial<InspectionVisit>) => api.put<InspectionVisit>(`/inspections/visits/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<InspectionVisit>) => api.patch<InspectionVisit>(`/inspections/visits/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/inspections/visits/${id}/`),
}
