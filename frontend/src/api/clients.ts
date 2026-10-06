import { api } from './client'

export type Client = {
  id: number
  name: string
  trade_name?: string
  registration_number?: string
  tax_number?: string
  address?: string
  billing_address?: string
  contact_email?: string
  contact_phone?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export const clientsApi = {
  list: () => api.get<Client[]>('/clients/').then(r => r.data),
  retrieve: (id: number) => api.get<Client>(`/clients/${id}/`).then(r => r.data),
  create: (data: Partial<Client>) => api.post<Client>('/clients/', data).then(r => r.data),
  update: (id: number, data: Partial<Client>) => api.put<Client>(`/clients/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<Client>) => api.patch<Client>(`/clients/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/clients/${id}/`),
}
