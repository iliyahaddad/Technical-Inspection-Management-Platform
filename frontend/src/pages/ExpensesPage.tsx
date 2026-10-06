import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert, Select, MenuItem, FormControl, InputLabel
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { expensesApi } from '../api/expenses'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_CHOICES = ['draft', 'submitted', 'approved', 'rejected']

export default function ExpensesPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ inspector: 0, project: 0, expense_date: '', category: '', amount: 0, currency: 'IRR', description: '', status: 'draft' })

  const { data: expenses = [], isLoading } = useQuery({ queryKey: ['expenses'], queryFn: expensesApi.list })
  const createMutation = useMutation({ mutationFn: expensesApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['expenses'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => expensesApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['expenses'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: expensesApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['expenses'] }) })

  const resetForm = () => { setForm({ inspector: 0, project: 0, expense_date: '', category: '', amount: 0, currency: 'IRR', description: '', status: 'draft' }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('expenses.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('expenses.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('expenses.inspector')}</TableCell>
              <TableCell>{t('expenses.project')}</TableCell>
              <TableCell>{t('expenses.category')}</TableCell>
              <TableCell>{t('expenses.amount')}</TableCell>
              <TableCell>{t('expenses.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {expenses.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.inspector}</TableCell>
                <TableCell>{item.project}</TableCell>
                <TableCell>{item.category}</TableCell>
                <TableCell>{item.amount} {item.currency}</TableCell>
                <TableCell><Chip label={item.status} size="small" /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {expenses.length === 0 && (<TableRow><TableCell colSpan={7} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('expenses.create') : t('expenses.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('expenses.inspector') + ' ID'} type="number" value={form.inspector || ''} onChange={e => setForm({ ...form, inspector: parseInt(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('expenses.project') + ' ID'} type="number" value={form.project || ''} onChange={e => setForm({ ...form, project: parseInt(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('expenses.category')} value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} required /></Grid>
            <Grid size={{ xs: 6 }}><TextField fullWidth label={t('expenses.amount')} type="number" value={form.amount} onChange={e => setForm({ ...form, amount: parseFloat(e.target.value) || 0 })} required /></Grid>
            <Grid size={{ xs: 6 }}><TextField fullWidth label={t('expenses.currency')} value={form.currency} onChange={e => setForm({ ...form, currency: e.target.value })} /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('expenses.date')} type="date" value={form.expense_date} onChange={e => setForm({ ...form, expense_date: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>{t('expenses.status')}</InputLabel>
                <Select value={form.status} label={t('expenses.status')} onChange={e => setForm({ ...form, status: e.target.value })}>
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



