import { api } from './client'

export type NCR = {
  id: number
  ncr_number: string
  inspection_visit?: number
  report_revision?: number
  itp_activity?: number
  description: string
  requirement_reference?: string
  evidence?: any[]
  severity: 'minor' | 'major' | 'critical'
  responsible_party?: number
  proposed_corrective_action?: string
  root_cause?: string
  target_completion_date?: string
  status: 'open' | 'in_progress' | 'verification' | 'closed' | 'waived'
  closed_at?: string
  closed_by?: number
  created_at: string
  updated_at: string
}

export const ncrsApi = {
  list: () => api.get<NCR[]>('/reports/ncrs/').then(r => r.data),
  retrieve: (id: number) => api.get<NCR>(`/reports/ncrs/${id}/`).then(r => r.data),
  create: (data: Partial<NCR>) => api.post<NCR>('/reports/ncrs/', data).then(r => r.data),
  update: (id: number, data: Partial<NCR>) => api.put<NCR>(`/reports/ncrs/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<NCR>) => api.patch<NCR>(`/reports/ncrs/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/reports/ncrs/${id}/`),
}
