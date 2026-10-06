import { Routes, Route, Navigate } from 'react-router-dom'
import { tokenStore } from './api/client'
import ProtectedRoute from './components/common/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import RequestListPage from './pages/RequestListPage'
import RequestFormPage from './pages/RequestFormPage'
import RequestDetailPage from './pages/RequestDetailPage'
import ReviewPage from './pages/ReviewPage'
import ClientsPage from './pages/ClientsPage'
import ProjectsPage from './pages/ProjectsPage'
import InspectorsPage from './pages/InspectorsPage'
import AssignmentsPage from './pages/AssignmentsPage'
import VisitsPage from './pages/VisitsPage'
import ReportsPage from './pages/ReportsPage'
import NcrPage from './pages/NcrPage'
import ReleaseNotesPage from './pages/ReleaseNotesPage'
import TimesheetsPage from './pages/TimesheetsPage'
import ExpensesPage from './pages/ExpensesPage'
import FinancialPage from './pages/FinancialPage'
import CalendarPage from './pages/CalendarPage'
import AnalyticsPage from './pages/AnalyticsPage'
import MainLayout from './components/layout/MainLayout'
import TwoFactorPage from './pages/TwoFactorPage'
import { ROUTE_ROLES } from './components/layout/navigation'

function App() {
  const loggedIn = Boolean(tokenStore.access())
  const guard = (path: keyof typeof ROUTE_ROLES, element: JSX.Element) => (
    <Route element={<ProtectedRoute roles={ROUTE_ROLES[path]} />}>
      <Route path={path} element={element} />
    </Route>
  )

  return (
    <Routes>
      <Route path="/login" element={loggedIn ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          {guard('clients', <ClientsPage />)}
          {guard('projects', <ProjectsPage />)}
          {guard('requests', <RequestListPage />)}
          {guard('requests/new', <RequestFormPage />)}
          <Route element={<ProtectedRoute roles={ROUTE_ROLES.requests} />}><Route path="requests/:id" element={<RequestDetailPage />} /></Route>
          {guard('review', <ReviewPage />)}
          {guard('inspectors', <InspectorsPage />)}
          {guard('assignments', <AssignmentsPage />)}
          {guard('visits', <VisitsPage />)}
          {guard('reports', <ReportsPage />)}
          {guard('ncr', <NcrPage />)}
          {guard('release-notes', <ReleaseNotesPage />)}
          {guard('timesheets', <TimesheetsPage />)}
          {guard('expenses', <ExpensesPage />)}
          {guard('financial', <FinancialPage />)}
          {guard('calendar', <CalendarPage />)}
          {guard('analytics', <AnalyticsPage />)}
          <Route path="security/2fa" element={<TwoFactorPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to={loggedIn ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}

export default App
