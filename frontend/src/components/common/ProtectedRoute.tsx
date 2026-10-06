import { Navigate, Outlet } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { tokenStore } from '../../api/client'
import { hasAnyRole, useCurrentUser } from '../../hooks/useCurrentUser'

interface ProtectedRouteProps {
  /** Roles allowed to open this route; omit to allow any authenticated user. */
  roles?: string[]
  children?: React.ReactNode
}

export default function ProtectedRoute({ roles, children }: ProtectedRouteProps) {
  const { data: user, isLoading, isError } = useCurrentUser()

  if (!tokenStore.access() || isError) return <Navigate to="/login" replace />
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }}>
        <CircularProgress />
      </Box>
    )
  }
  if (roles && !hasAnyRole(user, roles)) return <Navigate to="/dashboard" replace />
  return <>{children ?? <Outlet />}</>
}
