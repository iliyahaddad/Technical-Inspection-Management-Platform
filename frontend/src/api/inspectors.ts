import { api } from './client'

export type InspectorProfile = {
  id: number
  user: number
  user_detail?: { id: number; email: string; first_name: string; last_name: string }
  employee_number?: string
  employment_type: 'employee' | 'contractor'
  disciplines: string[]
  specializations?: string[]
  years_of_experience?: number
  geographic_location?: string
  coverage_areas?: string[]
  travel_preferences?: Record<string, any>
  conflict_of_interest_declared: boolean
  performance_score?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export const inspectorsApi = {
  list: () => api.get<InspectorProfile[]>('/inspections/inspectors/').then(r => r.data),
  retrieve: (id: number) => api.get<InspectorProfile>(`/inspections/inspectors/${id}/`).then(r => r.data),
  create: (data: Partial<InspectorProfile>) => api.post<InspectorProfile>('/inspections/inspectors/', data).then(r => r.data),
  update: (id: number, data: Partial<InspectorProfile>) => api.put<InspectorProfile>(`/inspections/inspectors/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<InspectorProfile>) => api.patch<InspectorProfile>(`/inspections/inspectors/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/inspections/inspectors/${id}/`),
}
