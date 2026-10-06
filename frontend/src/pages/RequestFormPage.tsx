import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  Paper,
} from '@mui/material'
import { ArrowBack as BackIcon, Save as SaveIcon } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { requestsApi } from '../api/requests'
import { projectsApi } from '../api/projects'
import { useTranslation } from '../utils/I18nProvider'

const DISCIPLINES = ['Mechanical', 'Electrical', 'Civil', 'Piping', 'Instrumentation', 'Structural']
const INSPECTION_TYPES = ['Visual', 'Dimensional', 'NDT', 'PMI', 'Hydrotest', 'Pneumatic', 'Functional']
const PRIORITIES = ['low', 'normal', 'high', 'urgent']

export default function RequestFormPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState({ project: '', discipline: '', inspection_type: '', inspection_level: '', priority: 'normal', special_instructions: '', requested_inspection_date: '', items: [{ id: 0, request: 0, item_number: 1, equipment_tag: '', description: '', material_type: '', specification: '', drawing_reference: '', quantity: 1, unit: 'pcs', requested_qty: 1, previously_inspected_qty: 0, remarks: '' }] })
  const [error, setError] = useState('')

  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })

  const createMutation = useMutation({
    mutationFn: requestsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['requests'] })
      navigate('/requests')
    },
  })

  useEffect(() => { if (projects.length > 0 && !form.project) setForm(f => ({ ...f, project: String(projects[0].id) })) }, [projects])

  const handleSubmit = () => {
    setError('')
    if (!form.project || !form.discipline || !form.inspection_type || !form.priority) { setError('Please fill required fields'); return }
    createMutation.mutate({ ...form, project: Number(form.project), items: form.items.filter(i => i.description) } as any)
  }

  const updateItem = (index: number, field: string, value: any) => {
    const items = [...form.items]
    items[index] = { ...items[index], [field]: value }
    setForm({ ...form, items })
  }

  const addItem = () => setForm({ ...form, items: [...form.items, { id: 0, request: 0, item_number: form.items.length + 1, equipment_tag: '', description: '', material_type: '', specification: '', drawing_reference: '', quantity: 1, unit: 'pcs', requested_qty: 1, previously_inspected_qty: 0, remarks: '' }] })
  const removeItem = (index: number) => setForm({ ...form, items: form.items.filter((_, i) => i !== index) })

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/requests')}>{t('app.cancel')}</Button>
        <Typography variant="h4">{t('requests.create')}</Typography>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>{t('requests.project')}</InputLabel>
              <Select value={form.project} label={t('requests.project')} onChange={e => setForm({ ...form, project: e.target.value })}>
                {projects.map((p: any) => <MenuItem key={p.id} value={String(p.id)}>{p.name} ({p.project_code})</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>{t('requests.discipline')}</InputLabel>
              <Select value={form.discipline} label={t('requests.discipline')} onChange={e => setForm({ ...form, discipline: e.target.value })}>
                {DISCIPLINES.map(d => <MenuItem key={d} value={d}>{d}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>{t('requests.type')}</InputLabel>
              <Select value={form.inspection_type} label={t('requests.type')} onChange={e => setForm({ ...form, inspection_type: e.target.value })}>
                {INSPECTION_TYPES.map(tp => <MenuItem key={tp} value={tp}>{tp}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>{t('requests.level')}</InputLabel>
              <Select value={form.inspection_level} label={t('requests.level')} onChange={e => setForm({ ...form, inspection_level: e.target.value })}>
                <MenuItem value="hold_point">Hold Point</MenuItem>
                <MenuItem value="witness">Witness</MenuItem>
                <MenuItem value="surveillance">Surveillance</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>{t('requests.priority')}</InputLabel>
              <Select value={form.priority} label={t('requests.priority')} onChange={e => setForm({ ...form, priority: e.target.value })}>
                {PRIORITIES.map(p => <MenuItem key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField fullWidth label={t('requests.requestedInspectionDate')} type="date" InputLabelProps={{ shrink: true }} value={form.requested_inspection_date} onChange={e => setForm({ ...form, requested_inspection_date: e.target.value })} />
          </Grid>
          <Grid size={{ xs: 12 }}>
            <TextField fullWidth label={t('requests.specialInstructions')} multiline rows={3} value={form.special_instructions} onChange={e => setForm({ ...form, special_instructions: e.target.value })} />
          </Grid>
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">{t('requests.items')}</Typography>
            <Button variant="outlined" size="small" onClick={addItem}>Add Item</Button>
          </Box>
          {form.items.map((item, index) => (
            <Paper key={index} sx={{ p: 2, mb: 2 }}>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 3 }}><TextField fullWidth size="small" label={t('requests.equipmentTag')} value={item.equipment_tag} onChange={e => updateItem(index, 'equipment_tag', e.target.value)} /></Grid>
                <Grid size={{ xs: 12, md: 3 }}><TextField fullWidth size="small" label={t('requests.specification')} value={item.specification} onChange={e => updateItem(index, 'specification', e.target.value)} /></Grid>
                <Grid size={{ xs: 12, md: 3 }}><TextField fullWidth size="small" label={t('requests.quantity')} type="number" value={item.quantity} onChange={e => updateItem(index, 'quantity', Number(e.target.value))} /></Grid>
                <Grid size={{ xs: 12, md: 3 }}><TextField fullWidth size="small" label={t('requests.requestedQty')} type="number" value={item.requested_qty} onChange={e => updateItem(index, 'requested_qty', Number(e.target.value))} /></Grid>
                <Grid size={{ xs: 12 }}><TextField fullWidth size="small" label={t('requests.description')} value={item.description} onChange={e => updateItem(index, 'description', e.target.value)} required /></Grid>
                <Grid size={{ xs: 12 }}><Button color="error" size="small" onClick={() => removeItem(index)}>Remove</Button></Grid>
              </Grid>
            </Paper>
          ))}
        </Box>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {createMutation.error && <Alert severity="error" sx={{ mt: 2 }}>{(createMutation.error as any)?.message}</Alert>}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSubmit} disabled={createMutation.isPending}>{t('app.save')}</Button>
        </Box>
      </Paper>
    </Box>
  )
}



