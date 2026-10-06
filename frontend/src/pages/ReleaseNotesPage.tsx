import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Chip, CircularProgress, Alert
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { releaseNotesApi } from '../api/releaseNotes'
import { useTranslation } from '../utils/I18nProvider'

export default function ReleaseNotesPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<any>(null)
  const [form, setForm] = useState({ inspection_visit: 0, notes: '', is_final: false })

  const { data: notes = [], isLoading } = useQuery({ queryKey: ['releaseNotes'], queryFn: releaseNotesApi.list })
  const createMutation = useMutation({ mutationFn: releaseNotesApi.create, onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['releaseNotes'] }); setOpen(false); resetForm() } })
  const updateMutation = useMutation({ mutationFn: (vars: { id: number; data: any }) => releaseNotesApi.update(vars.id, vars.data), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['releaseNotes'] }); setOpen(false); resetForm() } })
  const deleteMutation = useMutation({ mutationFn: releaseNotesApi.delete, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['releaseNotes'] }) })

  const resetForm = () => { setForm({ inspection_visit: 0, notes: '', is_final: false }); setEditItem(null) }
  const handleOpen = (item?: any) => { if (item) { setEditItem(item); setForm({ ...item }) } else { resetForm() } setOpen(true) }
  const handleClose = () => { setOpen(false); resetForm() }
  const handleSubmit = () => { if (editItem) { updateMutation.mutate({ id: editItem.id, data: form as any }) } else { createMutation.mutate(form as any) } }

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('common.releaseNotes')}</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>{t('common.releaseNotes')}</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>{t('common.releaseNotes')}</TableCell>
              <TableCell>{t('common.status')}</TableCell>
              <TableCell>{t('app.date')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {notes.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.release_number}</TableCell>
                <TableCell><Chip label={item.is_final ? t('common.approved') : t('common.draft')} size="small" color={item.is_final ? 'success' : 'default'} /></TableCell>
                <TableCell>{item.released_at ? new Date(item.released_at).toLocaleString() : '-'}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpen(item)}><EditIcon /></IconButton>
                  <IconButton size="small" color="error" onClick={() => deleteMutation.mutate(item.id)}><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
            {notes.length === 0 && (<TableRow><TableCell colSpan={5} align="center">{t('common.noData')}</TableCell></TableRow>)}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? t('common.releaseNotes') : t('common.releaseNotes')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid size={{ xs: 12 }}><TextField fullWidth label={t('app.description')} multiline rows={4} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} required /></Grid>
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



