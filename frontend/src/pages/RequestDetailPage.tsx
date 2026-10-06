import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert, Box, Button, Chip, CircularProgress, Divider, Grid, Paper, Stack, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Typography,
} from '@mui/material'
import { ArrowBack, RateReview, Send } from '@mui/icons-material'
import { requestsApi } from '../api/requests'
import { projectsApi } from '../api/projects'
import { useTranslation } from '../utils/I18nProvider'

const SUBMITTABLE = ['draft', 'clarification_required']

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <Grid size={{ xs: 12, md: 4 }}>
      <Typography color="text.secondary" variant="body2">{label}</Typography>
      <Typography>{children}</Typography>
    </Grid>
  )
}

export default function RequestDetailPage() {
  const { id } = useParams()
  const requestId = Number(id)
  const navigate = useNavigate()
  const { t } = useTranslation()
  const qc = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['request', requestId],
    queryFn: () => requestsApi.retrieve(requestId),
    enabled: Number.isFinite(requestId),
  })
  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })
  const submit = useMutation({
    mutationFn: () => requestsApi.submit(requestId),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['request', requestId] }); void qc.invalidateQueries({ queryKey: ['requests'] }) },
  })

  if (isLoading) return <Box sx={{ display: 'grid', placeItems: 'center', p: 6 }}><CircularProgress /></Box>
  if (error || !data) return <Alert severity="error">{t('requests.loadError')}</Alert>

  const projectName = projects.find((p) => p.id === data.project)?.name ?? data.project
  const submitError = (submit.error as { response?: { data?: { detail?: string } }; message?: string } | null)
  return (
    <Box>
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/requests')}>{t('app.back')}</Button>
        <Typography variant="h4" sx={{ flex: 1 }}>{data.request_number}</Typography>
        <Chip label={data.status} />
      </Stack>

      <Paper sx={{ p: 3, mb: 2 }}>
        <Grid container spacing={2}>
          <Field label={t('requests.project')}>{projectName}</Field>
          <Field label={t('requests.discipline')}>{data.discipline}</Field>
          <Field label={t('requests.type')}>{data.inspection_type}</Field>
          <Field label={t('requests.priority')}>{data.priority}</Field>
          <Field label={t('requests.requestedDate')}>{data.requested_inspection_date || '-'}</Field>
          <Grid size={12}>
            <Divider sx={{ my: 1 }} />
            <Typography color="text.secondary" variant="body2">{t('requests.instructions')}</Typography>
            <Typography sx={{ whiteSpace: 'pre-wrap' }}>{data.special_instructions || '-'}</Typography>
          </Grid>
          {data.review_comments && (
            <Grid size={12}>
              <Alert severity="warning">{data.review_comments}</Alert>
            </Grid>
          )}
        </Grid>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>{t('requests.items')}</Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell><TableCell>{t('requests.tag')}</TableCell><TableCell>{t('common.description')}</TableCell>
                <TableCell>{t('requests.specification')}</TableCell><TableCell>{t('requests.quantity')}</TableCell><TableCell>{t('requests.requestedQty')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(data.items ?? []).map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.item_number}</TableCell>
                  <TableCell>{item.equipment_tag || '-'}</TableCell>
                  <TableCell>{item.description}</TableCell>
                  <TableCell>{item.specification || '-'}</TableCell>
                  <TableCell>{item.quantity} {item.unit}</TableCell>
                  <TableCell>{item.requested_qty}</TableCell>
                </TableRow>
              ))}
              {(data.items ?? []).length === 0 && <TableRow><TableCell colSpan={6} align="center">{t('common.noData')}</TableCell></TableRow>}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
        {SUBMITTABLE.includes(data.status) && (
          <Button variant="contained" startIcon={<Send />} onClick={() => submit.mutate()} disabled={submit.isPending}>{t('common.submit')}</Button>
        )}
        <Button variant="outlined" startIcon={<RateReview />} onClick={() => navigate('/review')}>{t('common.review')}</Button>
      </Stack>
      {submit.error && <Alert severity="error" sx={{ mt: 2 }}>{submitError?.response?.data?.detail ?? submitError?.message ?? t('requests.submitError')}</Alert>}
    </Box>
  )
}
