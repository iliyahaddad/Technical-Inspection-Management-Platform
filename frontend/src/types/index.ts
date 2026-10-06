export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone?: string
  preferred_language: 'fa' | 'en'
  date_format: 'jalali' | 'gregorian'
  is_active: boolean
  last_login?: string
}

export interface Client {
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

export interface Project {
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

export interface InspectionRequest {
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

export interface RequestItem {
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
