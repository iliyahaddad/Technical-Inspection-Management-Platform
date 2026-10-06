import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert, Select, MenuItem, FormControl, InputLabel
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { inspectorsApi } from '../api/inspectors'
import { useTranslation } from '../utils/I18nProvider'

const EMPLOYMENT_TYPES = ['employee', 'contractor']

export default function InspectorsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState<{ user: number; employee_number: string; employment_type: string; disciplines: string[]; specializations: string[]; years_of_experience: number | null; geographic_location: string; coverage_areas: string[]; conflict_of_interest_declared: boolean; performance_score: number | null; is_active: boolean }>({ user: 0, employee_number: '', employment_type: 'contractor', disciplines: [], specializations: [], years_of_experience: null, geographic_location: '', coverage_areas: [], conflict_of_interest_declared: false, performance_score: null, is_active: true })

  const { data: inspectors = [], isLoading } = useQuery({ queryKey: ['inspectors'], queryFn: inspectorsApi.list })
  const createMutation = useMutation({ mutationFn: inspectorsApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['inspectors'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => inspectorsApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['inspectors'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: inspectorsApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['inspectors'] }) })

  const resetForm = () => { setForm({ user: 0, employee_number: '', employment_type: 'contractor', disciplines: [], specializations: [], years_of_experience: null, geographic_location: '', coverage_areas: [], conflict_of_interest_declared: false, performance_score: null, is_active: true }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('inspectors.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('inspectors.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('inspectors.user')}</TableCell>
              <TableCell>{t('inspectors.employmentType')}</TableCell>
              <TableCell>{t('inspectors.disciplines')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {inspectors.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.user_detail?.first_name} {item.user_detail?.last_name} ({item.user_detail?.email})</TableCell>
                <TableCell>{item.employment_type}</TableCell>
                <TableCell>{(item.disciplines || []).join(', ')}</TableCell>
                <TableCell><Chip label={item.is_active ? t('common.active') : t('common.inactive')} color={item.is_active ? 'success' : 'default'} size="small" /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {inspectors.length === 0 && (<TableRow><TableCell colSpan={6} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('inspectors.edit') : t('inspectors.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>{t('inspectors.employmentType')}</InputLabel>
                <Select value={form.employment_type} label={t('inspectors.employmentType')} onChange={e => setForm({ ...form, employment_type: e.target.value })}>
                  {EMPLOYMENT_TYPES.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('inspectors.user') + ' ID'} type="number" value={form.user || ''} onChange={e => setForm({ ...form, user: parseInt(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('inspectors.disciplines')} value={form.disciplines.join(', ')} onChange={e => setForm({ ...form, disciplines: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('inspectors.employmentType') + ' Number'} value={form.employee_number} onChange={e => setForm({ ...form, employee_number: e.target.value })} /></Grid>
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



