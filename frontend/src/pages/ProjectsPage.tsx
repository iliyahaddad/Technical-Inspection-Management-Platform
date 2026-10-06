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
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { projectsApi } from '../api/projects'
import { clientsApi } from '../api/clients'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_OPTIONS = [
  { value: 'draft', label: 'common.draft' },
  { value: 'active', label: 'common.active' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'completed', label: 'common.completed' },
  { value: 'closed', label: 'common.cancelled' },
]

export default function ProjectsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ name: '', project_code: '', client: '', description: '', status: 'draft', start_date: '', end_date: '', contract_value: '', currency: 'IRR' })

  const { data: projects = [], isLoading } = useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })
  const { data: clients = [] } = useQuery({ queryKey: ['clients'], queryFn: clientsApi.list })
  const createMutation = useMutation({ mutationFn: projectsApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['projects'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => projectsApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['projects'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: projectsApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }) })

  const resetForm = () => { setForm({ name: '', project_code: '', client: '', description: '', status: 'draft', start_date: '', end_date: '', contract_value: '', currency: 'IRR' }); setEditItem(null) }

  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ name: item.name, project_code: item.project_code, client: String(item.client), description: item.description || '', status: item.status, start_date: item.start_date || '', end_date: item.end_date || '', contract_value: item.contract_value?.toString() || '', currency: item.currency }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => {
    const data = { ...form, client: Number(form.client), contract_value: form.contract_value ? Number(form.contract_value) : undefined }
    if (editItem) { updateMutation.mutate({ id: editItem.id, data: data as any }) } else { createMutation.mutate(data as any) }
  }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('common.projects')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('projects.create')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('projects.code')}</TableCell>
              <TableCell>{t('projects.name')}</TableCell>
              <TableCell>{t('clients.name')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell>{t('projects.currency')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {projects.map((project: any) => (
              <TableRow key={project.id}>
                <TableCell>{project.id}</TableCell>
                <TableCell>{project.project_code}</TableCell>
                <TableCell>{project.name}</TableCell>
                <TableCell>{project.client}</TableCell>
                <TableCell><Chip label={t(STATUS_OPTIONS.find(s => s.value === project.status)?.label || project.status)} size="small" /></TableCell>
                <TableCell>{project.currency}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(project)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(project.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {projects.length === 0 && (<TableRow><TableCell colSpan={7} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('projects.edit') : t('projects.create')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('projects.name')} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('projects.code')} value={form.project_code} onChange={e => setForm({ ...form, project_code: e.target.value })} required /></Grid>
            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>{t('projects.client')}</InputLabel>
                <Select value={form.client} label={t('projects.client')} onChange={e => setForm({ ...form, client: e.target.value })}>
                  {clients.map((client: any) => <MenuItem key={client.id} value={client.id}>{client.name}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('projects.description')} multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>{t('common.status')}</InputLabel>
                <Select value={form.status} label={t('common.status')} onChange={e => setForm({ ...form, status: e.target.value })}>
                  {STATUS_OPTIONS.map(opt => <MenuItem key={opt.value} value={opt.value}>{t(opt.label)}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>{t('projects.currency')}</InputLabel>
                <Select value={form.currency} label={t('projects.currency')} onChange={e => setForm({ ...form, currency: e.target.value })}>
                  <MenuItem value="IRR">IRR</MenuItem>
                  <MenuItem value="EUR">EUR</MenuItem>
                  <MenuItem value="USD">USD</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth label={t('projects.startDate')} type="date" InputLabelProps={{ shrink: true }} value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} /></Grid>
            <Grid size={{ xs: 12, md: 6 }}><TextField fullWidth label={t('projects.endDate')} type="date" InputLabelProps={{ shrink: true }} value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} /></Grid>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('projects.contractValue')} type="number" value={form.contract_value} onChange={e => setForm({ ...form, contract_value: e.target.value })} /></Grid>
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



