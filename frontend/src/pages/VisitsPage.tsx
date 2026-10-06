import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert, Select, MenuItem, FormControl, InputLabel
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { visitsApi } from '../api/visits'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_CHOICES = ['scheduled', 'in_progress', 'completed', 'postponed', 'cancelled']

export default function VisitsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ assignment: 0, scheduled_start: '', scheduled_end: '', actual_start: '', actual_end: '', status: 'scheduled', notes: '' })

  const { data: visits = [], isLoading } = useQuery({ queryKey: ['visits'], queryFn: visitsApi.list })
  const createMutation = useMutation({ mutationFn: visitsApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['visits'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => visitsApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['visits'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: visitsApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['visits'] }) })

  const resetForm = () => { setForm({ assignment: 0, scheduled_start: '', scheduled_end: '', actual_start: '', actual_end: '', status: 'scheduled', notes: '' }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('visits.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('visits.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('visits.assignment')}</TableCell>
              <TableCell>{t('visits.visitDate')}</TableCell>
              <TableCell>{t('visits.status')}</TableCell>
              <TableCell>{t('visits.startedAt')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visits.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.assignment_detail?.id || item.assignment}</TableCell>
                <TableCell>{item.scheduled_start ? new Date(item.scheduled_start).toLocaleDateString() : '-'}</TableCell>
                <TableCell><Chip label={item.status} size="small" /></TableCell>
                <TableCell>{item.actual_start ? new Date(item.actual_start).toLocaleString() : '-'}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {visits.length === 0 && (<TableRow><TableCell colSpan={6} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('visits.create') : t('visits.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('visits.assignment') + ' ID'} type="number" value={form.assignment || ''} onChange={e => setForm({ ...form, assignment: parseInt(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('visits.visitDate') + ' Start'} type="datetime-local" value={form.scheduled_start} onChange={e => setForm({ ...form, scheduled_start: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('visits.visitDate') + ' End'} type="datetime-local" value={form.scheduled_end} onChange={e => setForm({ ...form, scheduled_end: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>{t('visits.status')}</InputLabel>
                <Select value={form.status} label={t('visits.status')} onChange={e => setForm({ ...form, status: e.target.value })}>
                  {STATUS_CHOICES.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('app.description')} multiline rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} /></Grid>
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



