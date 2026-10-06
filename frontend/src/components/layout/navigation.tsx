import type { ReactNode } from 'react'
import {
  Dashboard as DashboardIcon, Assignment as RequestIcon, People as ClientsIcon, Business as ProjectsIcon,
  RateReview as ReviewIcon, Engineering as InspectorsIcon, AssignmentInd as AssignmentsIcon,
  Visibility as VisitsIcon, Description as ReportsIcon, Warning as NcrIcon, Notes as ReleaseIcon,
  AccessTime as TimesheetIcon, Receipt as ExpenseIcon, AccountBalance as FinancialIcon,
  CalendarMonth as CalendarIcon, Analytics as AnalyticsIcon, Security as SecurityIcon,
} from '@mui/icons-material'

/** Role keys match backend apps.accounts.roles. `sys_admin`/staff always pass (see hasAnyRole). */
const INTERNAL = ['gm', 'tech_manager', 'quality_manager', 'coordinator', 'project_manager', 'reviewer']
const CLIENT = ['client_admin', 'client_requester', 'client_approver']

export const ROUTE_ROLES = {
  clients: [...INTERNAL, 'finance_officer', 'auditor'],
  projects: [...INTERNAL, 'finance_officer', 'auditor', ...CLIENT, 'vendor_rep'],
  requests: [...INTERNAL, 'auditor', ...CLIENT, 'inspector'],
  'requests/new': ['coordinator', 'project_manager', 'client_admin', 'client_requester'],
  review: ['coordinator', 'quality_manager', 'tech_manager', 'gm'],
  inspectors: [...INTERNAL, 'auditor'],
  assignments: [...INTERNAL, 'auditor', 'inspector'],
  visits: [...INTERNAL, 'auditor', 'inspector'],
  reports: [...INTERNAL, 'auditor', 'inspector', ...CLIENT],
  ncr: [...INTERNAL, 'auditor', 'inspector', ...CLIENT],
  'release-notes': [...INTERNAL, 'auditor', 'inspector', ...CLIENT],
  timesheets: ['project_manager', 'gm', 'finance_officer', 'auditor', 'inspector'],
  expenses: ['project_manager', 'gm', 'finance_officer', 'auditor', 'inspector'],
  financial: ['project_manager', 'gm', 'finance_officer', 'auditor'],
  calendar: [...INTERNAL, 'inspector'],
  analytics: ['gm', 'quality_manager', 'tech_manager', 'finance_officer', 'auditor', 'project_manager'],
} satisfies Record<string, string[]>

export type NavItem = { label: string; icon: ReactNode; path: string; roles?: string[] }

export const NAV_ITEMS: NavItem[] = [
  { label: 'common.dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { label: 'common.clients', icon: <ClientsIcon />, path: '/clients', roles: ROUTE_ROLES.clients },
  { label: 'common.projects', icon: <ProjectsIcon />, path: '/projects', roles: ROUTE_ROLES.projects },
  { label: 'common.requests', icon: <RequestIcon />, path: '/requests', roles: ROUTE_ROLES.requests },
  { label: 'common.review', icon: <ReviewIcon />, path: '/review', roles: ROUTE_ROLES.review },
  { label: 'common.inspectors', icon: <InspectorsIcon />, path: '/inspectors', roles: ROUTE_ROLES.inspectors },
  { label: 'common.assignments', icon: <AssignmentsIcon />, path: '/assignments', roles: ROUTE_ROLES.assignments },
  { label: 'common.visits', icon: <VisitsIcon />, path: '/visits', roles: ROUTE_ROLES.visits },
  { label: 'common.reports', icon: <ReportsIcon />, path: '/reports', roles: ROUTE_ROLES.reports },
  { label: 'common.ncr', icon: <NcrIcon />, path: '/ncr', roles: ROUTE_ROLES.ncr },
  { label: 'common.releaseNotes', icon: <ReleaseIcon />, path: '/release-notes', roles: ROUTE_ROLES['release-notes'] },
  { label: 'common.timesheets', icon: <TimesheetIcon />, path: '/timesheets', roles: ROUTE_ROLES.timesheets },
  { label: 'common.expenses', icon: <ExpenseIcon />, path: '/expenses', roles: ROUTE_ROLES.expenses },
  { label: 'common.financial', icon: <FinancialIcon />, path: '/financial', roles: ROUTE_ROLES.financial },
  { label: 'common.calendar', icon: <CalendarIcon />, path: '/calendar', roles: ROUTE_ROLES.calendar },
  { label: 'common.analytics', icon: <AnalyticsIcon />, path: '/analytics', roles: ROUTE_ROLES.analytics },
  { label: 'common.security', icon: <SecurityIcon />, path: '/security/2fa' },
]
