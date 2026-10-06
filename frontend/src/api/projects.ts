import { api } from './client'

export type Project = {
  id: number
  client: number
  project_code: string
  name: string
  description?: string
  project_manager?: number
  status: 'draft' | 'active' | 'on_hold' | 'completed' | 'closed'
  start_date?: string
  end_date?: string
  contract_value?: number
  currency: string
  created_at: string
  updated_at: string
}

export const projectsApi = {
  list: () => api.get<Project[]>('/projects/projects/').then(r => r.data),
  retrieve: (id: number) => api.get<Project>(`/projects/projects/${id}/`).then(r => r.data),
  create: (data: Partial<Project>) => api.post<Project>('/projects/projects/', data).then(r => r.data),
  update: (id: number, data: Partial<Project>) => api.put<Project>(`/projects/projects/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<Project>) => api.patch<Project>(`/projects/projects/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/projects/projects/${id}/`),
}
