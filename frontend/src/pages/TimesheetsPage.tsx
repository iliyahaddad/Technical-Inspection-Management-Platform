import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert, Select, MenuItem, FormControl, InputLabel
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { timesheetsApi } from '../api/timesheets'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_CHOICES = ['draft', 'submitted', 'approved', 'locked']

export default function TimesheetsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ inspector: 0, project: 0, month: '', status: 'draft' })

  const { data: timesheets = [], isLoading } = useQuery({ queryKey: ['timesheets'], queryFn: timesheetsApi.list })
  const createMutation = useMutation({ mutationFn: timesheetsApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['timesheets'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => timesheetsApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['timesheets'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: timesheetsApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['timesheets'] }) })

  const resetForm = () => { setForm({ inspector: 0, project: 0, month: '', status: 'draft' }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('timesheets.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('timesheets.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('timesheets.inspector')}</TableCell>
              <TableCell>{t('timesheets.project')}</TableCell>
              <TableCell>{t('timesheets.month')}</TableCell>
              <TableCell>{t('timesheets.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {timesheets.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.inspector}</TableCell>
                <TableCell>{item.project}</TableCell>
                <TableCell>{item.month}</TableCell>
                <TableCell><Chip label={item.status} size="small" /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {timesheets.length === 0 && (<TableRow><TableCell colSpan={6} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('timesheets.create') : t('timesheets.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('timesheets.inspector') + ' ID'} type="number" value={form.inspector || ''} onChange={e => setForm({ ...form, inspector: parseInt(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('timesheets.project') + ' ID'} type="number" value={form.project || ''} onChange={e => setForm({ ...form, project: parseInt(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('timesheets.month')} type="date" value={form.month} onChange={e => setForm({ ...form, month: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>{t('timesheets.status')}</InputLabel>
                <Select value={form.status} label={t('timesheets.status')} onChange={e => setForm({ ...form, status: e.target.value })}>
                  {STATUS_CHOICES.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
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



