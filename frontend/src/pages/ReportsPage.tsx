import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Alert, Box, Button, Chip, CircularProgress, Divider, Grid, IconButton, Paper, Stack, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TablePagination, TextField, Typography,
} from '@mui/material'
import { Add as AddIcon, CloudUpload, Edit as EditIcon, PictureAsPdf } from '@mui/icons-material'
import { reportsApi, InspectionReport } from '../api/reports'
import { useTranslation } from '../utils/I18nProvider'

type Form = {
  inspection_visit: string; scope: string; narrative: string; deviations: string; recommendations: string
  inspected_qty: string; accepted_qty: string; rejected_qty: string; remaining_qty: string
}

const EMPTY: Form = {
  inspection_visit: '', scope: '', narrative: '', deviations: '', recommendations: '',
  inspected_qty: '', accepted_qty: '', rejected_qty: '', remaining_qty: '',
}

const QTY_FIELDS = ['inspected_qty', 'accepted_qty', 'rejected_qty', 'remaining_qty'] as const
/** Server locks reports once submitted; the editor is only meaningful for these states. */
const EDITABLE = ['draft', 'revision_required']

const num = (v: number | string | null | undefined) => (v === null || v === undefined ? '' : String(v))

function errorText(err: unknown): string {
  const e = err as { response?: { data?: { detail?: unknown } }; message?: string }
  const detail = e.response?.data?.detail
  return detail ? (typeof detail === 'string' ? detail : JSON.stringify(detail)) : e.message ?? 'Request failed'
}

export default function ReportsPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(10)
  const [editing, setEditing] = useState<InspectionReport | null>(null)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState<Form>(EMPTY)
  const [file, setFile] = useState<File | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: ['reports-page', page, pageSize],
    queryFn: () => reportsApi.listPage(page + 1, pageSize),
    placeholderData: (previous) => previous,
  })

  const refresh = () => qc.invalidateQueries({ queryKey: ['reports-page'] })

  const save = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      editing ? reportsApi.partialUpdate(editing.id, payload) : reportsApi.create(payload),
    onSuccess: () => { void refresh(); setOpen(false); setEditing(null) },
  })
  const submit = useMutation({ mutationFn: (id: number) => reportsApi.submit(id), onSuccess: () => void refresh() })
  const upload = useMutation({
    mutationFn: async () => {
      const revision = editing?.revisions?.[0]
      if (!revision || !file) throw new Error('Select a file and an existing report first.')
      return reportsApi.uploadAttachment(revision.id, file)
    },
    onSuccess: () => setFile(null),
  })
  const pdf = useMutation({ mutationFn: (id: number) => reportsApi.openPdf(id) })

  const startNew = () => { setEditing(null); setForm(EMPTY); setFile(null); setOpen(true) }
  const startEdit = (r: InspectionReport) => {
    setEditing(r)
    setForm({
      inspection_visit: String(r.inspection_visit), scope: r.scope ?? '', narrative: r.narrative ?? '',
      deviations: r.deviations ?? '', recommendations: r.recommendations ?? '',
      inspected_qty: num(r.inspected_qty), accepted_qty: num(r.accepted_qty),
      rejected_qty: num(r.rejected_qty), remaining_qty: num(r.remaining_qty),
    })
    setFile(null)
    setOpen(true)
  }

  const set = (key: keyof Form) => (e: React.ChangeEvent<HTMLInputElement>) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const onSave = () => {
    const payload: Record<string, unknown> = {
      scope: form.scope, narrative: form.narrative, deviations: form.deviations, recommendations: form.recommendations,
    }
    // DRF DecimalField rejects '' -> send null for blanks.
    for (const k of QTY_FIELDS) payload[k] = form[k] === '' ? null : form[k]
    if (!editing) payload.inspection_visit = Number(form.inspection_visit)
    save.mutate(payload)
  }

  if (isLoading) return <Box sx={{ display: 'grid', placeItems: 'center', p: 6 }}><CircularProgress /></Box>
  if (error) return <Alert severity="error">{errorText(error)}</Alert>

  const reports = data?.results ?? []
  const canEdit = !editing || EDITABLE.includes(editing.status)

  return (
    <Box>
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
        <Typography variant="h4" sx={{ flex: 1 }}>{t('reports.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={startNew}>{t('reports.create')}</Button>
      </Stack>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('reports.number')}</TableCell>
              <TableCell>{t('reports.revision')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.map((r) => (
              <TableRow key={r.id} hover>
                <TableCell>{r.report_number}</TableCell>
                <TableCell>{r.revision}</TableCell>
                <TableCell><Chip size="small" label={r.status} /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" aria-label="edit" onClick={() => startEdit(r)}><EditIcon /></IconButton>
                  <IconButton size="small" aria-label="pdf" onClick={() => pdf.mutate(r.id)}><PictureAsPdf /></IconButton>
                  {EDITABLE.includes(r.status) && (
                    <Button size="small" onClick={() => submit.mutate(r.id)} disabled={submit.isPending}>{t('common.submit')}</Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {reports.length === 0 && <TableRow><TableCell colSpan={4} align="center">{t('common.noData')}</TableCell></TableRow>}
          </TableBody>
        </Table>
        <TablePagination
          component="div" count={data?.count ?? 0} page={page} rowsPerPage={pageSize}
          onPageChange={(_, p) => setPage(p)}
          onRowsPerPageChange={(e) => { setPageSize(Number(e.target.value)); setPage(0) }}
          rowsPerPageOptions={[10, 25, 50]}
        />
      </TableContainer>

      {(submit.error || pdf.error) && <Alert severity="error" sx={{ mt: 2 }}>{errorText(submit.error ?? pdf.error)}</Alert>}

      {open && (
        <Paper sx={{ p: 3, mt: 2 }}>
          <Typography variant="h6">{editing ? editing.report_number : t('reports.create')}</Typography>
          {!canEdit && <Alert severity="info" sx={{ mt: 1 }}>{t('reports.locked')}</Alert>}
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            {!editing && (
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth required type="number" label={t('reports.visitId')} value={form.inspection_visit} onChange={set('inspection_visit')} />
              </Grid>
            )}
            {QTY_FIELDS.map((k) => (
              <Grid key={k} size={{ xs: 6, md: 2 }}>
                <TextField fullWidth type="number" label={t(`reports.${k}`)} value={form[k]} onChange={set(k)} disabled={!canEdit} />
              </Grid>
            ))}
            <Grid size={12}><TextField fullWidth multiline minRows={2} label={t('reports.scope')} value={form.scope} onChange={set('scope')} disabled={!canEdit} /></Grid>
            <Grid size={12}><TextField fullWidth multiline minRows={4} label={t('reports.narrative')} value={form.narrative} onChange={set('narrative')} disabled={!canEdit} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth multiline minRows={3} label={t('reports.deviations')} value={form.deviations} onChange={set('deviations')} disabled={!canEdit} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth multiline minRows={3} label={t('reports.recommendations')} value={form.recommendations} onChange={set('recommendations')} disabled={!canEdit} /></Grid>
          </Grid>

          {editing && canEdit && (
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mt: 2 }}>
              <Button component="label" variant="outlined" startIcon={<CloudUpload />}>
                {t('reports.attach')}
                <input hidden type="file" accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx,.txt" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
              </Button>
              <Typography variant="body2" sx={{ flex: 1 }}>{file?.name ?? ''}</Typography>
              <Button onClick={() => upload.mutate()} disabled={!file || upload.isPending}>{t('reports.upload')}</Button>
            </Stack>
          )}
          {upload.isSuccess && <Alert severity="success" sx={{ mt: 2 }}>{t('reports.uploaded')}</Alert>}
          {(save.error || upload.error) && <Alert severity="error" sx={{ mt: 2 }}>{errorText(save.error ?? upload.error)}</Alert>}

          <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
            <Button variant="contained" onClick={onSave} disabled={!canEdit || save.isPending || (!editing && !form.inspection_visit)}>{t('app.save')}</Button>
            <Button onClick={() => { setOpen(false); setEditing(null) }}>{t('app.cancel')}</Button>
          </Stack>
        </Paper>
      )}
    </Box>
  )
}
