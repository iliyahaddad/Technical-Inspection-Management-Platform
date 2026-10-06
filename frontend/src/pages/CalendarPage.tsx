import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, Card, CardContent, Grid, TextField, MenuItem, Select
} from '@mui/material'
import { assignmentsApi } from '../api/assignments'
import { visitsApi } from '../api/visits'
import { useTranslation } from '../utils/I18nProvider'

const STATUS_COLORS: Record<string, string> = {
  proposed: 'default',
  approved: 'primary',
  notified: 'info',
  accepted: 'success',
  declined: 'error',
  confirmed: 'warning',
  completed: 'success',
  cancelled: 'default',
  scheduled: 'info',
  in_progress: 'warning',
  postponed: 'error',
}

export default function CalendarPage() {
  const { t } = useTranslation()
  const [view, setView] = useState<'week' | 'month'>('week')
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])

  const { data: assignments = [] } = useQuery({ queryKey: ['assignments'], queryFn: assignmentsApi.list })
  const { data: visits = [] } = useQuery({ queryKey: ['visits'], queryFn: visitsApi.list })

  const allEvents = [
    ...assignments.map((a: any) => ({
      id: a.id,
      title: `Assignment #${a.id}`,
      start: a.proposed_at,
      end: a.completed_at || a.proposed_at,
      status: a.status,
      type: 'assignment',
    })),
    ...visits.map((v: any) => ({
      id: v.id,
      title: `Visit #${v.id}`,
      start: v.scheduled_start,
      end: v.scheduled_end || v.scheduled_start,
      status: v.status,
      type: 'visit',
    })),
  ].sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())

  const filteredEvents = allEvents.filter((e) => {
    if (view === 'week') {
      const eventDate = new Date(e.start)
      const selectedDate = new Date(date)
      const weekStart = new Date(selectedDate)
      weekStart.setDate(weekStart.getDate() - weekStart.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 7)
      return eventDate >= weekStart && eventDate < weekEnd
    }
    return true
  })

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">{t('common.calendar') || 'Calendar'}</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            size="small"
          />
          <Select value={view} size="small" onChange={(e) => setView(e.target.value as 'week' | 'month')}>
            <MenuItem value="week">Week</MenuItem>
            <MenuItem value="month">Month</MenuItem>
          </Select>
        </Box>
      </Box>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 2, minHeight: 400 }}>
            <Typography variant="h6" gutterBottom>{view === 'week' ? 'Week View' : 'Month View'}</Typography>
            {filteredEvents.length === 0 && (
              <Typography color="text.secondary">No events found</Typography>
            )}
            {filteredEvents.map((event: any) => (
              <Card key={event.id} sx={{ mb: 1, borderLeft: `4px solid ${STATUS_COLORS[event.status] || 'gray'}` }}>
                <CardContent sx={{ py: 1 }}>
                  <Typography variant="body2" noWrap>{event.title}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(event.start).toLocaleString()} - {event.type}
                  </Typography>
                  <Chip label={event.status} size="small" color={STATUS_COLORS[event.status] as any} sx={{ ml: 1 }} />
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>{t('common.status')}</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Count</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(
                    allEvents.reduce((acc: Record<string, number>, e: any) => {
                      acc[e.status] = (acc[e.status] || 0) + 1
                      return acc
                    }, {})
                  ).map(([status, count]) => (
                    <TableRow key={status}>
                      <TableCell><Chip label={status} size="small" color={STATUS_COLORS[status] as any} /></TableCell>
                      <TableCell align="right">{count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}




