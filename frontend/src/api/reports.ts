import { api } from './client'

export type InspectionReport = {
  id: number
  report_number: string
  revision: number
  inspection_visit: number
  template_version?: number
  submitted_by: number
  status: 'draft' | 'submitted' | 'under_review' | 'revision_required' | 'approved' | 'issued'
  scope?: string
  inspected_qty?: number
  accepted_qty?: number
  rejected_qty?: number
  remaining_qty?: number
  instruments_used?: any[]
  narrative?: string
  deviations?: string
  recommendations?: string
  submitted_at?: string
  reviewed_by?: number
  reviewed_at?: string
  review_comments?: string
  issued_at?: string
  issued_by?: number
  content_hash: string
  created_at: string
  updated_at: string
  revisions?: Array<{ id: number; revision_number: number; content: any }>
}

export type Paged<T> = { count: number; next: string | null; previous: string | null; results: T[] }

export const reportsApi = {
  list: () => api.get<InspectionReport[]>('/reports/reports/').then(r => r.data),
  listPage: (page=1, pageSize=10) => api.get<Paged<InspectionReport>>(`/reports/reports/?page=${page}&page_size=${pageSize}`, { keepPagination: true }).then(r => r.data),
  retrieve: (id: number) => api.get<InspectionReport>(`/reports/reports/${id}/`).then(r => r.data),
  create: (data: Partial<InspectionReport>) => api.post<InspectionReport>('/reports/reports/', data).then(r => r.data),
  update: (id: number, data: Partial<InspectionReport>) => api.put<InspectionReport>(`/reports/reports/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<InspectionReport>) => api.patch<InspectionReport>(`/reports/reports/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/reports/reports/${id}/`),
  submit: (id: number) => api.post(`/reports/reports/${id}/submit/`).then(r => r.data),
  approve: (id: number) => api.post(`/reports/reports/${id}/approve/`).then(r => r.data),
  issue: (id: number) => api.post(`/reports/reports/${id}/issue/`).then(r => r.data),
  createRevision: (report: number, content: any) => api.post('/reports/revisions/', { report, revision_number: 1, content }).then(r => r.data),
  uploadAttachment: (report_revision: number, file: File, description = '') => {
    const fd = new FormData()
    fd.append('report_revision', String(report_revision))
    fd.append('file', file)
    fd.append('description', description)
    return api.post('/reports/attachments/', fd).then(r => r.data)
  },
  /** PDF needs the Authorization header, so fetch as a blob and open it (a plain link would 401). */
  openPdf: async (id: number) => {
    const res = await api.get(`/documents/reports/${id}/pdf/`, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data as Blob)
    const tab = window.open(url, '_blank', 'noopener,noreferrer')
    if (!tab) {
      URL.revokeObjectURL(url)
      throw new Error('The browser blocked the PDF window. Please allow pop-ups for this site.')
    }
    window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
  },
}
