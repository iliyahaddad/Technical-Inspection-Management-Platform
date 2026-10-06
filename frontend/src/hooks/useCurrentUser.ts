import { useQuery } from '@tanstack/react-query'
import { api, tokenStore } from '../api/client'
import type { User } from '../types'

export type CurrentUser = User & { roles: string[]; is_staff: boolean; full_name: string }

export function useCurrentUser() {
  return useQuery<CurrentUser>({
    queryKey: ['me'],
    queryFn: async () => (await api.get('/accounts/me/')).data,
    enabled: Boolean(tokenStore.access()),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}

const ADMIN_ROLES = ['sys_admin']

export function hasAnyRole(user: CurrentUser | undefined, roles: string[]): boolean {
  if (!user) return false
  if (user.is_staff || user.roles.some((r) => ADMIN_ROLES.includes(r))) return true
  return user.roles.some((r) => roles.includes(r))
}
