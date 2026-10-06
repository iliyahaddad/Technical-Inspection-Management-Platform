import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { financialApi } from '../api/financial'
import { useTranslation } from '../utils/I18nProvider'

export default function FinancialPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ project: 0, period_start: '', period_end: '', currency: 'IRR', total_billable: 0, total_invoiced: 0, current_amount: 0, tax_amount: 0, lines: [] })

  const { data: statements = [], isLoading } = useQuery({ queryKey: ['statements'], queryFn: financialApi.list })
  const createMutation = useMutation({ mutationFn: financialApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['statements'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => financialApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['statements'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: financialApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['statements'] }) })

  const resetForm = () => { setForm({ project: 0, period_start: '', period_end: '', currency: 'IRR', total_billable: 0, total_invoiced: 0, current_amount: 0, tax_amount: 0, lines: [] }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('financial.title')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('financial.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('financial.title')}</TableCell>
              <TableCell>{t('financial.periodStart')}</TableCell>
              <TableCell>{t('financial.periodEnd')}</TableCell>
              <TableCell>{t('financial.totalBillable')}</TableCell>
              <TableCell>{t('financial.totalDue')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {statements.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.statement_number}</TableCell>
                <TableCell>{item.period_start}</TableCell>
                <TableCell>{item.period_end}</TableCell>
                <TableCell>{item.total_billable} {item.currency}</TableCell>
                <TableCell>{item.total_due} {item.currency}</TableCell>
                <TableCell><Chip label={item.status} size="small" /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {statements.length === 0 && (<TableRow><TableCell colSpan={7} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('financial.create') : t('financial.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('financial.periodStart')} type="date" value={form.period_start} onChange={e => setForm({ ...form, period_start: e.target.value })} InputLabelProps={{ shrink: true }} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('financial.periodEnd')} type="date" value={form.period_end} onChange={e => setForm({ ...form, period_end: e.target.value })} InputLabelProps={{ shrink: true }} required /></Grid>
            <Grid size={{ xs: 6 }}><TextField fullWidth label={t('financial.totalBillable')} type="number" value={form.total_billable} onChange={e => setForm({ ...form, total_billable: parseFloat(e.target.value) || 0 })} /></Grid>
            <Grid size={{ xs: 6 }}><TextField fullWidth label={t('financial.totalInvoiced')} type="number" value={form.total_invoiced} onChange={e => setForm({ ...form, total_invoiced: parseFloat(e.target.value) || 0 })} /></Grid>
            <Grid size={{ xs: 6 }}><TextField fullWidth label={t('financial.currentAmount')} type="number" value={form.current_amount} onChange={e => setForm({ ...form, current_amount: parseFloat(e.target.value) || 0 })} /></Grid>
            <Grid size={{ xs: 6 }}><TextField fullWidth label={t('financial.taxAmount')} type="number" value={form.tax_amount} onChange={e => setForm({ ...form, tax_amount: parseFloat(e.target.value) || 0 })} /></Grid>
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



