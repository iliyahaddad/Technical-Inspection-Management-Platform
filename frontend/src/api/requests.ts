import { api } from './client'

export type RequestItem = {
  id: number
  request: number
  item_number: number
  equipment_tag?: string
  description: string
  material_type?: string
  specification?: string
  drawing_reference?: string
  quantity: number
  unit: string
  previously_inspected_qty: number
  requested_qty: number
  remarks?: string
}

export type InspectionRequest = {
  id: number
  request_number: string
  revision: number
  project: number
  submitted_by: number
  contract?: number
  purchase_order?: number
  vendor?: number
  location?: number
  requested_inspection_date?: string
  discipline: string
  inspection_type: string
  inspection_level?: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  special_instructions?: string
  status: 'draft' | 'submitted' | 'under_review' | 'clarification_required' | 'accepted' | 'rejected' | 'ready_for_scheduling'
  submitted_at?: string
  reviewed_by?: number
  reviewed_at?: string
  review_comments?: string
  items?: RequestItem[]
  created_at: string
  updated_at: string
}

export type PagedRequests = { count: number; next: string | null; previous: string | null; results: InspectionRequest[] }

export const requestsApi = {
  list: () => api.get<InspectionRequest[]>('/inspections/requests/').then(r => r.data),
  listPage: (page=1, pageSize=10) => api.get<PagedRequests>(`/inspections/requests/?page=${page}&page_size=${pageSize}`, { keepPagination: true }).then(r => r.data),
  retrieve: (id: number) => api.get<InspectionRequest>(`/inspections/requests/${id}/`).then(r => r.data),
  create: (data: Partial<InspectionRequest>) => api.post<InspectionRequest>('/inspections/requests/', data).then(r => r.data),
  update: (id: number, data: Partial<InspectionRequest>) => api.put<InspectionRequest>(`/inspections/requests/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<InspectionRequest>) => api.patch<InspectionRequest>(`/inspections/requests/${id}/`, data).then(r => r.data),
  submit: (id: number) => api.post(`/inspections/requests/${id}/submit/`).then(r => r.data),
  review: (id: number, data: { decision: 'accept' | 'reject' | 'clarification'; comments?: string }) =>
    api.post(`/inspections/requests/${id}/review/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/inspections/requests/${id}/`),
}
