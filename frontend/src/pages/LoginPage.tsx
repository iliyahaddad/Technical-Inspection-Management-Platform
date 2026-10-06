import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Paper, TextField, Typography } from '@mui/material'
import { api, tokenStore } from '../api/client'
import { useTranslation } from '../utils/I18nProvider'

export default function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [otp, setOtp] = useState('')

  const login = useMutation({
    mutationFn: async () => (await api.post('/auth/token/', { email, password, ...(otp ? { otp } : {}) })).data,
    onSuccess: async (data) => {
      tokenStore.set(data.access, data.refresh)
      await queryClient.invalidateQueries({ queryKey: ['me'] })
      navigate(data.requires_2fa_setup ? '/security/2fa' : '/dashboard', { replace: true })
    },
  })

  const status = (login.error as { response?: { status?: number } } | null)?.response?.status
  const code = (login.error as { response?: { data?: { detail?: string } } } | null)?.response?.data?.detail
  const message = status === 429 ? t('auth.tooManyAttempts') : /one-time/i.test(String(code ?? '')) ? t('auth.otpRequired') : t('auth.invalidCredentials')

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    login.mutate()
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', bgcolor: 'grey.100', p: 2 }}>
      <Paper sx={{ width: '100%', maxWidth: 420, p: 4 }} elevation={3}>
        <Typography variant="h5" align="center" gutterBottom>{t('auth.signIn')}</Typography>
        {login.isError && <Alert severity="error" sx={{ mb: 1 }}>{message}</Alert>}
        <form onSubmit={submit}>
          <TextField label={t('auth.email')} type="email" autoComplete="username" fullWidth margin="normal" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <TextField label={t('auth.password')} type="password" autoComplete="current-password" fullWidth margin="normal" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <TextField label={t('auth.otp')} inputMode="numeric" autoComplete="one-time-code" fullWidth margin="normal" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="123456" />
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={login.isPending}>{t('auth.signIn')}</Button>
        </form>
      </Paper>
    </Box>
  )
}
