import { useState } from 'react'
import {
  AppBar, Avatar, Box, Divider, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  Menu, MenuItem, Toolbar, Typography, useMediaQuery, useTheme,
} from '@mui/material'
import { Logout as LogoutIcon, Menu as MenuIcon } from '@mui/icons-material'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { logout } from '../../api/client'
import { hasAnyRole, useCurrentUser } from '../../hooks/useCurrentUser'
import { useTranslation } from '../../utils/I18nProvider'
import { NAV_ITEMS } from './navigation'

const drawerWidth = 260

export default function MainLayout() {
  const theme = useTheme()
  const { t } = useTranslation()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [mobileOpen, setMobileOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const { data: user } = useCurrentUser()

  const items = NAV_ITEMS.filter((item) => !item.roles || hasAnyRole(user, item.roles))

  const drawer = (
    <Box>
      <Toolbar sx={{ bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h6" noWrap>{t('app.name')}</Typography>
      </Toolbar>
      <Divider />
      <List>
        {items.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname.startsWith(item.path)}
              onClick={() => { navigate(item.path); if (isMobile) setMobileOpen(false) }}
            >
              <ListItemIcon sx={{ color: 'inherit' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={t(item.label)} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={() => setMobileOpen((v) => !v)} sx={{ mr: 2, display: { md: 'none' } }} aria-label="menu">
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>{t('app.name')}</Typography>
          <Typography variant="body2" sx={{ mx: 2, display: { xs: 'none', sm: 'block' } }}>{user?.full_name || user?.email}</Typography>
          <IconButton color="inherit" onClick={(e) => setAnchorEl(e.currentTarget)} aria-label="account">
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>{user?.email?.charAt(0).toUpperCase()}</Avatar>
          </IconButton>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
            <MenuItem onClick={() => { setAnchorEl(null); void logout() }}>
              <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>
              <ListItemText>{t('auth.logout')}</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer variant="temporary" open={mobileOpen} onClose={() => setMobileOpen(false)} ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth } }}>
          {drawer}
        </Drawer>
        <Drawer variant="permanent" open sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth } }}>
          {drawer}
        </Drawer>
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - ${drawerWidth}px)` }, minHeight: '100vh', bgcolor: 'grey.50' }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  )
}
