import { api } from './client'

export type ReleaseNote = {
  id: number
  release_number: string
  inspection_visit: number
  released_by: number
  notes: string
  is_final: boolean
  released_at: string
}

export const releaseNotesApi = {
  list: () => api.get<ReleaseNote[]>('/reports/release-notes/').then(r => r.data),
  retrieve: (id: number) => api.get<ReleaseNote>(`/reports/release-notes/${id}/`).then(r => r.data),
  create: (data: Partial<ReleaseNote>) => api.post<ReleaseNote>('/reports/release-notes/', data).then(r => r.data),
  update: (id: number, data: Partial<ReleaseNote>) => api.put<ReleaseNote>(`/reports/release-notes/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<ReleaseNote>) => api.patch<ReleaseNote>(`/reports/release-notes/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/reports/release-notes/${id}/`),
}
