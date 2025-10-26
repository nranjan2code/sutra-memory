import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  IconButton,
  Divider,
  Chip,
} from '@mui/material';
import { Close, Keyboard } from '@mui/icons-material';

interface KeyboardShortcutsDialogProps {
  open: boolean;
  onClose: () => void;
}

interface Shortcut {
  keys: string[];
  description: string;
}

interface ShortcutCategory {
  title: string;
  shortcuts: Shortcut[];
}

const isMac = /Mac|iPod|iPhone|iPad/.test(navigator.userAgent);
const modKey = isMac ? '⌘' : 'Ctrl';

const categories: ShortcutCategory[] = [
  {
    title: 'Navigation',
    shortcuts: [
      { keys: [modKey, 'K'], description: 'Open command palette (search)' },
      { keys: ['Esc'], description: 'Close dialogs / Cancel' },
      { keys: ['↑', '↓'], description: 'Navigate search results' },
      { keys: ['Enter'], description: 'Select item / Send message' },
      { keys: ['Shift', 'Enter'], description: 'New line in message input' },
    ],
  },
  {
    title: 'Chat',
    shortcuts: [
      { keys: [modKey, 'N'], description: 'New conversation' },
      { keys: [modKey, 'S'], description: 'Search conversations' },
      { keys: [modKey, '/'], description: 'Focus message input' },
    ],
  },
  {
    title: 'General',
    shortcuts: [
      { keys: ['?'], description: 'Show keyboard shortcuts' },
      { keys: [modKey, ','], description: 'Open settings' },
      { keys: [modKey, 'Q'], description: 'Logout' },
    ],
  },
];

/**
 * Keyboard shortcuts dialog
 */
export default function KeyboardShortcutsDialog({ open, onClose }: KeyboardShortcutsDialogProps) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          pb: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Keyboard color="primary" />
          <Typography variant="h6">Keyboard Shortcuts</Typography>
        </Box>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{ ml: 2 }}
          aria-label="Close"
        >
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        {categories.map((category, catIndex) => (
          <Box key={category.title} sx={{ mb: catIndex < categories.length - 1 ? 3 : 0 }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              sx={{
                textTransform: 'uppercase',
                fontSize: '0.75rem',
                fontWeight: 600,
                mb: 1.5,
                letterSpacing: 0.5,
              }}
            >
              {category.title}
            </Typography>

            {category.shortcuts.map((shortcut, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  py: 1,
                  '&:not(:last-child)': {
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                  },
                }}
              >
                <Typography variant="body2" sx={{ flex: 1 }}>
                  {shortcut.description}
                </Typography>

                <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                  {shortcut.keys.map((key, keyIndex) => (
                    <React.Fragment key={keyIndex}>
                      <Chip
                        label={key}
                        size="small"
                        sx={{
                          height: 24,
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          bgcolor: 'action.hover',
                          fontFamily: 'monospace',
                          border: '1px solid',
                          borderColor: 'divider',
                          borderBottomWidth: 2,
                          '& .MuiChip-label': {
                            px: 1,
                          },
                        }}
                      />
                      {keyIndex < shortcut.keys.length - 1 && (
                        <Typography
                          variant="caption"
                          sx={{ color: 'text.secondary', mx: 0.5 }}
                        >
                          +
                        </Typography>
                      )}
                    </React.Fragment>
                  ))}
                </Box>
              </Box>
            ))}
          </Box>
        ))}

        <Divider sx={{ my: 3 }} />

        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Press <Chip label="?" size="small" sx={{ mx: 0.5, height: 20, fontSize: '0.7rem' }} /> anytime to view this dialog
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
