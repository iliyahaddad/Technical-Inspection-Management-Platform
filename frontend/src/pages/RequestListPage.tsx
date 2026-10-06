import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  Box,
  Button,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  IconButton,
  TablePagination,
} from '@mui/material'
import { Add as AddIcon, Visibility as ViewIcon } from '@mui/icons-material'
import { requestsApi } from '../api/requests'
import { projectsApi } from '../api/projects'
import { useTranslation } from '../utils/I18nProvider'
import { useNavigate } from 'react-router-dom'

const STATUS_MAP: Record<string, { label: string; color: any }> = {
  draft: { label: 'common.draft', color: 'default' },
  submitted: { label: 'common.submitted', color: 'info' },
  under_review: { label: 'Under Review', color: 'warning' },
  clarification_required: { label: 'Clarification Required', color: 'warning' },
  accepted: { label: 'common.approved', color: 'success' },
  rejected: { label: 'common.rejected', color: 'error' },
  ready_for_scheduling: { label: 'Ready for Scheduling', color: 'info' },
}

const PRIORITY_MAP: Record<string, string> = {
  low: 'Low',
  normal: 'Normal',
  high: 'High',
  urgent: 'Urgent',
}

export default function RequestListPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(10)
  const { data: requestPage, isLoading } = useQuery({ queryKey: ['requests-page', page, pageSize], queryFn: () => requestsApi.listPage(page + 1, pageSize), placeholderData: (previous) => previous })
  const requests = requestPage?.results || []
  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('common.requests')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/requests/new')}>{t('requests.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('requests.number')}</TableCell>
              <TableCell>{t('requests.project')}</TableCell>
              <TableCell>{t('requests.discipline')}</TableCell>
              <TableCell>{t('requests.type')}</TableCell>
              <TableCell>{t('requests.priority')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {requests.map((request: any) => (
              <TableRow key={request.id}>
                <TableCell>{request.id}</TableCell>
                <TableCell>{request.request_number}</TableCell>
                <TableCell>{projects.find((p: any) => p.id === request.project)?.name || request.project}</TableCell>
                <TableCell>{request.discipline}</TableCell>
                <TableCell>{request.inspection_type}</TableCell>
                <TableCell>{PRIORITY_MAP[request.priority] || request.priority}</TableCell>
                <TableCell><Chip label={t(STATUS_MAP[request.status]?.label || request.status)} color={STATUS_MAP[request.status]?.color || 'default'} size="small" /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => navigate(`/requests/${request.id}`)}><ViewIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {requests.length === 0 && (<TableRow><TableCell colSpan={8} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
        <TablePagination component="div" count={requestPage?.count || 0} page={page} onPageChange={(_, next) => setPage(next)} rowsPerPage={pageSize} onRowsPerPageChange={e => { setPageSize(Number(e.target.value)); setPage(0) }} rowsPerPageOptions={[10, 25, 50]} />
      </TableContainer>
    </Box>
  )
}



