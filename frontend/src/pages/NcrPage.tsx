import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert, Select, MenuItem, FormControl, InputLabel
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { ncrsApi } from '../api/ncrs'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_CHOICES = ['open', 'in_progress', 'verification', 'closed', 'waived']
const SEVERITY_CHOICES = ['minor', 'major', 'critical']

export default function NcrPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ inspection_visit: 0, description: '', severity: 'minor', status: 'open', proposed_corrective_action: '', root_cause: '', target_completion_date: '' })

  const { data: ncrs = [], isLoading } = useQuery({ queryKey: ['ncrs'], queryFn: ncrsApi.list })
  const createMutation = useMutation({ mutationFn: ncrsApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ncrs'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => ncrsApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ncrs'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: ncrsApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['ncrs'] }) })

  const resetForm = () => { setForm({ inspection_visit: 0, description: '', severity: 'minor', status: 'open', proposed_corrective_action: '', root_cause: '', target_completion_date: '' }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('ncr.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('ncr.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('ncr.number')}</TableCell>
              <TableCell>{t('ncr.severity')}</TableCell>
              <TableCell>{t('ncr.status')}</TableCell>
              <TableCell>{t('ncr.description')}</TableCell>
              <TableCell>{t('ncr.closedAt')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ncrs.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.ncr_number}</TableCell>
                <TableCell><Chip label={item.severity} size="small" color={item.severity === 'critical' ? 'error' : item.severity === 'major' ? 'warning' : 'default'} /></TableCell>
                <TableCell><Chip label={item.status} size="small" /></TableCell>
                <TableCell>{item.description.slice(0, 80)}...</TableCell>
                <TableCell>{item.closed_at ? new Date(item.closed_at).toLocaleDateString() : '-'}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {ncrs.length === 0 && (<TableRow><TableCell colSpan={6} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('ncr.create') : t('ncr.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('ncr.description')} multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} required /></Grid>
            <Grid size={{ xs: 6 }}>
              <FormControl fullWidth>
                <InputLabel>{t('ncr.severity')}</InputLabel>
                <Select value={form.severity} label={t('ncr.severity')} onChange={e => setForm({ ...form, severity: e.target.value })}>
                  {SEVERITY_CHOICES.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 6 }}>
              <FormControl fullWidth>
                <InputLabel>{t('ncr.status')}</InputLabel>
                <Select value={form.status} label={t('ncr.status')} onChange={e => setForm({ ...form, status: e.target.value })}>
                  {STATUS_CHOICES.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('ncr.correctiveActions')} multiline rows={3} value={form.proposed_corrective_action} onChange={e => setForm({ ...form, proposed_corrective_action: e.target.value })} /></Grid>
          </Grid>
          {(createMutation.error || updateMutation.error) && <Alert severity="error" sx={{ mt: 2 }}>{(createMutation.error as any)?.message || (updateMutation.error as any)?.message}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>{t('app.cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={createMutation.isPending || updateMutation.isPending}>{t('app.save')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}



