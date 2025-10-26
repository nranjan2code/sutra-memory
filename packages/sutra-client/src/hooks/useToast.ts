import { useSnackbar, VariantType } from 'notistack';

/**
 * Custom hook for displaying toast notifications
 * 
 * Usage:
 * ```tsx
 * const toast = useToast();
 * 
 * toast.success('Message sent successfully!');
 * toast.error('Failed to send message');
 * toast.info('Session expires in 5 minutes');
 * toast.warning('Unsaved changes');
 * ```
 */
export const useToast = () => {
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();

  const showToast = (message: string, variant: VariantType = 'default') => {
    return enqueueSnackbar(message, {
      variant,
      autoHideDuration: 4000,
      anchorOrigin: {
        vertical: 'bottom',
        horizontal: 'right',
      },
    });
  };

  return {
    /**
     * Show success toast (green)
     */
    success: (message: string) => showToast(message, 'success'),
    
    /**
     * Show error toast (red)
     */
    error: (message: string) => showToast(message, 'error'),
    
    /**
     * Show info toast (blue)
     */
    info: (message: string) => showToast(message, 'info'),
    
    /**
     * Show warning toast (orange)
     */
    warning: (message: string) => showToast(message, 'warning'),
    
    /**
     * Show default toast (gray)
     */
    default: (message: string) => showToast(message, 'default'),
    
    /**
     * Close a specific toast by key
     */
    close: (key: string | number) => closeSnackbar(key),
    
    /**
     * Close all toasts
     */
    closeAll: () => closeSnackbar(),
  };
};
