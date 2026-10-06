import { useQuery } from '@tanstack/react-query'
import { Box, CircularProgress, Grid, Paper, Typography } from '@mui/material'
import { api } from '../api/client'
import { useTranslation } from '../utils/I18nProvider'

type Row = Record<string, unknown>

/** Each widget loads independently: a role without access to one resource just sees "–" there. */
async function load(path: string): Promise<Row[] | null> {
  try {
    return (await api.get(path)).data as Row[]
  } catch {
    return null
  }
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const [projects, requests, ncrs, inspectors] = await Promise.all([
        load('/projects/projects/'),
        load('/inspections/requests/'),
        load('/reports/ncrs/'),
        load('/inspections/inspectors/'),
      ])
      const count = (rows: Row[] | null, pred: (r: Row) => boolean = () => true) => (rows ? rows.filter(pred).length : null)
      return {
        activeProjects: count(projects, (p) => p.status === 'active'),
        totalProjects: count(projects),
        pendingRequests: count(requests, (r) => r.status === 'submitted'),
        totalRequests: count(requests),
        openNcrs: count(ncrs, (n) => ['open', 'in_progress', 'verification'].includes(String(n.status))),
        activeInspectors: count(inspectors, (i) => i.is_active === true),
      }
    },
  })

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>

  const show = (v: number | null | undefined) => (v === null || v === undefined ? '–' : v)
  const cards = [
    { title: t('common.projects'), value: data?.activeProjects, sub: `${t('dashboard.active')} / ${show(data?.totalProjects)} ${t('dashboard.total')}` },
    { title: t('common.requests'), value: data?.pendingRequests, sub: `${t('dashboard.pending')} / ${show(data?.totalRequests)} ${t('dashboard.total')}` },
    { title: t('common.ncr'), value: data?.openNcrs, sub: t('dashboard.open') },
    { title: t('common.inspectors'), value: data?.activeInspectors, sub: t('dashboard.active') },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('app.dashboard')}</Typography>
      <Grid container spacing={2}>
        {cards.map((c) => (
          <Grid key={c.title} size={{ xs: 12, sm: 6, md: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">{c.title}</Typography>
              <Typography variant="h3">{show(c.value)}</Typography>
              <Typography variant="body2" color="text.secondary">{c.sub}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
