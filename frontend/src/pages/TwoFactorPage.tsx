import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material'
import { api } from '../api/client'
import { useTranslation } from '../utils/I18nProvider'

type Status = { enabled: boolean; required: boolean }
type Setup = { secret: string; provisioning_uri: string }

export default function TwoFactorPage() {
  const { t } = useTranslation()
  const [setupData, setSetupData] = useState<Setup | null>(null)
  const [token, setToken] = useState('')
  const [password, setPassword] = useState('')

  const status = useQuery<Status>({ queryKey: ['2fa-status'], queryFn: async () => (await api.get('/auth/2fa/status/')).data })
  const setup = useMutation({ mutationFn: async () => (await api.post('/auth/2fa/setup/')).data as Setup, onSuccess: setSetupData })
  const verify = useMutation({
    mutationFn: async () => (await api.post('/auth/2fa/verify/', { token })).data,
    onSuccess: () => { setSetupData(null); setToken(''); void status.refetch() },
  })
  const disable = useMutation({
    mutationFn: async () => (await api.post('/auth/2fa/disable/', { token, password })).data,
    onSuccess: () => { setToken(''); setPassword(''); void status.refetch() },
  })

  const failure = (setup.error ?? verify.error ?? disable.error) as { response?: { data?: { detail?: string } } } | null
  const enabled = status.data?.enabled

  return (
    <Box sx={{ maxWidth: 640, mx: 'auto' }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>{t('twofa.title')}</Typography>
        <Typography sx={{ mb: 2 }}>{enabled ? t('twofa.enabled') : t('twofa.disabled')}</Typography>
        {status.data?.required && !enabled && <Alert severity="warning" sx={{ mb: 2 }}>{t('twofa.required')}</Alert>}

        {!enabled && !setupData && (
          <Button variant="contained" onClick={() => setup.mutate()} disabled={setup.isPending}>{t('twofa.start')}</Button>
        )}

        {setupData && (
          <Stack spacing={2}>
            <Alert severity="info">{t('twofa.scan')}</Alert>
            <TextField label={t('twofa.secret')} value={setupData.secret} InputProps={{ readOnly: true }} fullWidth />
            <TextField label={t('twofa.uri')} value={setupData.provisioning_uri} InputProps={{ readOnly: true }} fullWidth />
            <TextField label={t('twofa.code')} inputMode="numeric" value={token} onChange={(e) => setToken(e.target.value)} fullWidth />
            <Button variant="contained" onClick={() => verify.mutate()} disabled={!token || verify.isPending}>{t('twofa.confirm')}</Button>
          </Stack>
        )}

        {enabled && (
          <Stack spacing={2}>
            <TextField label={t('auth.password')} type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth />
            <TextField label={t('twofa.code')} inputMode="numeric" value={token} onChange={(e) => setToken(e.target.value)} fullWidth />
            <Button color="error" variant="outlined" onClick={() => disable.mutate()} disabled={!token || !password || disable.isPending}>{t('twofa.disable')}</Button>
          </Stack>
        )}
        {failure && <Alert severity="error" sx={{ mt: 2 }}>{failure.response?.data?.detail ?? t('twofa.error')}</Alert>}
      </Paper>
    </Box>
  )
}
