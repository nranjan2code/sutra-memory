import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, holographicTheme } from '@sutra/ui-framework';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={holographicTheme}>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
