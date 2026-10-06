import { useQuery } from '@tanstack/react-query'
import {
  Box, Typography, Grid, Paper, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, CircularProgress, LinearProgress
} from '@mui/material'
import { assignmentsApi } from '../api/assignments'
import { visitsApi } from '../api/visits'
import { reportsApi } from '../api/reports'
import { ncrsApi } from '../api/ncrs'
import { financialApi } from '../api/financial'
import { useTranslation } from '../utils/I18nProvider'

interface KpiCardProps {
  title: string
  value: number
  subtitle?: string
  color?: string
}

function KpiCard({ title, value, subtitle, color = 'primary' }: KpiCardProps) {
  return (
    <Card>
      <CardContent>
        <Typography color="text.secondary" variant="body2">{title}</Typography>
        <Typography variant="h3" color={color}>{value}</Typography>
        {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
      </CardContent>
    </Card>
  )
}

export default function AnalyticsPage() {
  const { t } = useTranslation()

  const { data: assignments = [], isLoading: assignmentsLoading } = useQuery({ queryKey: ['assignments'], queryFn: assignmentsApi.list })
  const { data: visits = [], isLoading: visitsLoading } = useQuery({ queryKey: ['visits'], queryFn: visitsApi.list })
  const { data: reports = [], isLoading: reportsLoading } = useQuery({ queryKey: ['reports'], queryFn: reportsApi.list })
  const { data: ncrs = [], isLoading: ncrsLoading } = useQuery({ queryKey: ['ncrs'], queryFn: ncrsApi.list })
  const { data: statements = [], isLoading: statementsLoading } = useQuery({ queryKey: ['statements'], queryFn: financialApi.list })

  if (assignmentsLoading || visitsLoading || reportsLoading || ncrsLoading || statementsLoading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>
  }

  const totalAssignments = assignments.length
  const completedAssignments = assignments.filter((a: any) => a.status === 'completed').length
  const totalVisits = visits.length
  const completedVisits = visits.filter((v: any) => v.status === 'completed').length
  const totalReports = reports.length
  const approvedReports = reports.filter((r: any) => r.status === 'approved' || r.status === 'issued').length
  const openNcrs = ncrs.filter((n: any) => n.status === 'open' || n.status === 'in_progress').length
  const totalStatements = statements.length
  const totalBillable = statements.reduce((sum: number, s: any) => sum + (s.total_billable || 0), 0)
  const totalDue = statements.reduce((sum: number, s: any) => sum + (s.total_due || 0), 0)

  const utilization = totalAssignments > 0 ? Math.round((completedAssignments / totalAssignments) * 100) : 0
  const approvalRate = totalReports > 0 ? Math.round((approvedReports / totalReports) * 100) : 0

  const statusBreakdown = [
    { label: 'Draft', count: assignments.filter((a: any) => a.status === 'proposed').length, color: 'default' },
    { label: 'Approved', count: assignments.filter((a: any) => a.status === 'approved').length, color: 'primary' },
    { label: 'Completed', count: assignments.filter((a: any) => a.status === 'completed').length, color: 'success' },
    { label: 'Cancelled', count: assignments.filter((a: any) => a.status === 'cancelled').length, color: 'error' },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('common.analytics') || 'Analytics'}</Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard title="Active Assignments" value={totalAssignments} subtitle={`${utilization}% completion rate`} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard title="Completed Visits" value={completedVisits} subtitle={`of ${totalVisits} total`} color="success" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard title="Approved Reports" value={approvedReports} subtitle={`${approvalRate}% approval rate`} color="primary" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard title="Open NCRs" value={openNcrs} color="error" />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Financial Summary</Typography>
            <Typography variant="body1">Total Billable: {totalBillable.toLocaleString()}</Typography>
            <Typography variant="body1">Total Due: {totalDue.toLocaleString()}</Typography>
            <Typography variant="body1">Statements: {totalStatements}</Typography>
            <LinearProgress variant="determinate" value={totalStatements > 0 ? Math.round((totalDue / totalBillable) * 100) : 0} sx={{ mt: 2 }} />
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Assignment Status Breakdown</Typography>
            {statusBreakdown.map((item) => (
              <Box key={item.label} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Chip label={item.label} size="small" color={item.color as any} />
                <Typography variant="body2">{item.count}</Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>Recent Reports</Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Report #</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Submitted</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports.slice(0, 10).map((r: any) => (
                <TableRow key={r.id}>
                  <TableCell>{r.report_number}</TableCell>
                  <TableCell><Chip label={r.status} size="small" /></TableCell>
                  <TableCell>{r.submitted_at ? new Date(r.submitted_at).toLocaleDateString() : '-'}</TableCell>
                </TableRow>
              ))}
              {reports.length === 0 && (<TableRow><TableCell colSpan={3} align="center">No data</TableCell></TableRow>)}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  )
}




