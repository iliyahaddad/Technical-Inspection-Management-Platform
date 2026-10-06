import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material'
import { requestsApi } from '../api/requests'
import { projectsApi } from '../api/projects'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_MAP: Record<string, { label: string; color: any }> = {
  draft: { label: 'common.draft', color: 'default' },
  submitted: { label: 'common.submitted', color: 'info' },
  under_review: { label: 'Under Review', color: 'warning' },
  clarification_required: { label: 'Clarification Required', color: 'warning' },
  accepted: { label: 'common.approved', color: 'success' },
  rejected: { label: 'common.rejected', color: 'error' },
  ready_for_scheduling: { label: 'Ready for Scheduling', color: 'info' },
}

export default function ReviewPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { data: requests = [], isLoading } = useQuery({ queryKey: ['requests'], queryFn: requestsApi.list })
  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })
  const [selected, setSelected] = useState<any>(null)
  const [action, setAction] = useState<'accept' | 'reject' | 'clarification'>('accept')
  const [comments, setComments] = useState('')

  const reviewMutation = useMutation({
    mutationFn: (vars: { id: number; data: any }) => requestsApi.review(vars.id, vars.data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['requests'] }); setSelected(null); setComments('') },
  })

  const reviewable = requests.filter((r: any) => r.status === 'submitted')

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('common.review')}</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('requests.number')}</TableCell>
              <TableCell>{t('requests.project')}</TableCell>
              <TableCell>{t('requests.discipline')}</TableCell>
              <TableCell>{t('requests.priority')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reviewable.map((request: any) => (
              <TableRow key={request.id}>
                <TableCell>{request.id}</TableCell>
                <TableCell>{request.request_number}</TableCell>
                <TableCell>{projects.find((p: any) => p.id === request.project)?.name || request.project}</TableCell>
                <TableCell>{request.discipline}</TableCell>
                <TableCell>{request.priority}</TableCell>
                <TableCell><Chip label={t(STATUS_MAP[request.status]?.label || request.status)} color={STATUS_MAP[request.status]?.color || 'default'} size="small" /></TableCell>
                <TableCell align="right">
                  <Button variant="outlined" size="small" onClick={() => setSelected(request)}>{t('common.review')}</Button>
                </TableCell>
              </TableRow>
            ))}
            {reviewable.length === 0 && (<TableRow><TableCell colSpan={7} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Review Request {selected?.request_number}</DialogTitle>
        <DialogContent>
          {selected && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <Typography><strong>Project:</strong> {projects.find((p: any) => p.id === selected.project)?.name || selected.project}</Typography>
              <Typography><strong>Discipline:</strong> {selected.discipline}</Typography>
              <Typography><strong>Type:</strong> {selected.inspection_type}</Typography>
              <Typography><strong>Priority:</strong> {selected.priority}</Typography>
              <Typography><strong>Instructions:</strong> {selected.special_instructions || '-'}</Typography>
              <Typography variant="subtitle2" sx={{ mt: 2 }}>Decision</Typography>
              <RadioGroup value={action} onChange={e => setAction(e.target.value as any)}>
                <FormControlLabel value="accept" control={<Radio />} label="Accept" />
                <FormControlLabel value="reject" control={<Radio />} label="Reject" />
                <FormControlLabel value="clarification" control={<Radio />} label="Request Clarification" />
              </RadioGroup>
              <TextField fullWidth label="Comments" multiline rows={3} value={comments} onChange={e => setComments(e.target.value)} />
            </Box>
          )}
          {reviewMutation.error && <Alert severity="error" sx={{ mt: 2 }}>{JSON.stringify((reviewMutation.error as any)?.response?.data?.detail ?? (reviewMutation.error as any)?.message)}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelected(null)}>{t('app.cancel')}</Button>
          <Button variant="contained" onClick={() => selected && reviewMutation.mutate({ id: selected.id, data: { decision: action, comments } })} disabled={reviewMutation.isPending}>{t('app.save')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}



