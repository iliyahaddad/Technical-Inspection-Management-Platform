import { useQuery } from '@tanstack/react-query'
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, CircularProgress
} from '@mui/material'
import { assignmentsApi } from '../api/assignments'
import { useTranslation } from '../utils/I18nProvider'

export default function AssignmentsPage() {
  const { t } = useTranslation()
  const { data: assignments = [], isLoading } = useQuery({ queryKey: ['assignments'], queryFn: assignmentsApi.list })

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('assignments.title')}</Typography>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('assignments.inspector')}</TableCell>
              <TableCell>{t('assignments.inspectionRequest')}</TableCell>
              <TableCell>{t('assignments.status')}</TableCell>
              <TableCell>{t('assignments.assignedAt')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {assignments.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.inspector_detail?.user || item.inspector}</TableCell>
                <TableCell>{item.notification_detail?.inspection_request || item.notification}</TableCell>
                <TableCell><Chip label={item.status} size="small" /></TableCell>
                <TableCell>{item.proposed_at ? new Date(item.proposed_at).toLocaleString() : '-'}</TableCell>
              </TableRow>
            ))}
            {assignments.length === 0 && (<TableRow><TableCell colSpan={5} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}




