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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { clientsApi } from '../api/clients'
import { useTranslation } from '../utils/I18nProvider'

export default function ClientsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ name: '', trade_name: '', registration_number: '', tax_number: '', address: '', billing_address: '', contact_email: '', contact_phone: '', is_active: true })

  const { data: clients = [], isLoading } = useQuery({ queryKey: ['clients'], queryFn: clientsApi.list })
  const createMutation = useMutation({ mutationFn: clientsApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['clients'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => clientsApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['clients'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: clientsApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['clients'] }) })

  const resetForm = () => { setForm({ name: '', trade_name: '', registration_number: '', tax_number: '', address: '', billing_address: '', contact_email: '', contact_phone: '', is_active: true }); setEditItem(null) }

  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('common.clients')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('clients.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('clients.name')}</TableCell>
              <TableCell>{t('clients.contactEmail')}</TableCell>
              <TableCell>{t('clients.contactPhone')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {clients.map((client: any) => (
              <TableRow key={client.id}>
                <TableCell>{client.id}</TableCell>
                <TableCell>{client.name}</TableCell>
                <TableCell>{client.contact_email}</TableCell>
                <TableCell>{client.contact_phone}</TableCell>
                <TableCell><Chip label={client.is_active ? t('common.active') : t('common.inactive')} color={client.is_active ? 'success' : 'default'} size="small" /></TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(client)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(client.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {clients.length === 0 && (<TableRow><TableCell colSpan={6} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('clients.edit') : t('clients.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('clients.name')} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('clients.tradeName')} value={form.trade_name} onChange={e => setForm({ ...form, trade_name: e.target.value })} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth label={t('clients.registrationNumber')} value={form.registration_number} onChange={e => setForm({ ...form, registration_number: e.target.value })} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth label={t('clients.taxNumber')} value={form.tax_number} onChange={e => setForm({ ...form, tax_number: e.target.value })} /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('clients.address')} value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('clients.billingAddress')} value={form.billing_address} onChange={e => setForm({ ...form, billing_address: e.target.value })} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth label={t('clients.contactEmail')} type="email" value={form.contact_email} onChange={e => setForm({ ...form, contact_email: e.target.value })} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth label={t('clients.contactPhone')} value={form.contact_phone} onChange={e => setForm({ ...form, contact_phone: e.target.value })} /></Grid>
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



