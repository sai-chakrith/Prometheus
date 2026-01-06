import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import PrometheusApp from './PrometheusApp.jsx'
import { queryClient } from './api'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <PrometheusApp />
    </QueryClientProvider>
  </StrictMode>,
)
