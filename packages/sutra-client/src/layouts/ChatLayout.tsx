import { useState, ReactNode } from 'react'
import { Box, AppBar, Toolbar, Typography } from '@mui/material'
import Sidebar, { SidebarToggle } from '../components/Sidebar'
import UserMenu from '../components/UserMenu'

interface ChatLayoutProps {
  children: ReactNode
}

export default function ChatLayout({ children }: ChatLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* App Bar */}
        <AppBar
          position="static"
          elevation={1}
          sx={{
            bgcolor: 'background.paper',
            color: 'text.primary',
          }}
        >
          <Toolbar>
            <SidebarToggle onClick={() => setSidebarOpen(true)} />
            
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Sutra AI
            </Typography>

            <UserMenu />
          </Toolbar>
        </AppBar>

        {/* Chat Content */}
        <Box
          sx={{
            flex: 1,
            overflow: 'hidden',
            bgcolor: 'background.default',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  )
}
