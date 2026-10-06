import { api } from './client'

export type Timesheet = {
  id: number
  inspector: number
  project: number
  assignment?: number
  month: string
  status: 'draft' | 'submitted' | 'approved' | 'locked'
  submitted_at?: string
  approved_by?: number
  approved_at?: string
  created_at: string
  updated_at: string
  entries?: TimesheetEntry[]
}

export type TimesheetEntry = {
  id: number
  timesheet: number
  work_date: string
  start_time?: string
  end_time?: string
  break_duration?: number
  actual_hours: number
  travel_hours: number
  waiting_hours: number
  overtime_hours: number
  location?: string
  description?: string
  visit?: number
  created_at: string
}

export const timesheetsApi = {
  list: () => api.get<Timesheet[]>('/mts/timesheets/').then(r => r.data),
  retrieve: (id: number) => api.get<Timesheet>(`/mts/timesheets/${id}/`).then(r => r.data),
  create: (data: Partial<Timesheet>) => api.post<Timesheet>('/mts/timesheets/', data).then(r => r.data),
  update: (id: number, data: Partial<Timesheet>) => api.put<Timesheet>(`/mts/timesheets/${id}/`, data).then(r => r.data),
  partialUpdate: (id: number, data: Partial<Timesheet>) => api.patch<Timesheet>(`/mts/timesheets/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/mts/timesheets/${id}/`),
  submit: (id: number) => api.post(`/mts/timesheets/${id}/submit/`).then(r => r.data),
  approve: (id: number) => api.post(`/mts/timesheets/${id}/approve/`).then(r => r.data),
  lock: (id: number) => api.post(`/mts/timesheets/${id}/lock/`).then(r => r.data),
}
