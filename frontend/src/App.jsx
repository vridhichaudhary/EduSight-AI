/**
 * EduSight AI — App Router
 * All routes defined here.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Layouts
import RootLayout      from './components/layout/RootLayout'
import DashboardLayout from './components/layout/DashboardLayout'

// Pages (we create these next)
import HomePage            from './pages/HomePage'
import StudentsPage        from './pages/StudentsPage'
import UploadPage          from './pages/UploadPage'
import DashboardOverview   from './pages/dashboard/OverviewPage'
import PredictionsPage     from './pages/dashboard/PredictionsPage'
import WeakAreasPage       from './pages/dashboard/WeakAreasPage'
import RecommendationsPage from './pages/dashboard/RecommendationsPage'
import ChatPage            from './pages/dashboard/ChatPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime:   1000 * 60 * 5,   // 5 minutes
      retry:       1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route element={<RootLayout />}>
            <Route path="/"        element={<HomePage />} />
            <Route path="/students" element={<StudentsPage />} />
            <Route path="/upload"   element={<UploadPage />} />

            {/* Dashboard routes (with sidebar) */}
            <Route
              path="/dashboard/:studentId"
              element={<DashboardLayout />}
            >
              <Route index element={<Navigate to="overview" replace />} />
              <Route path="overview"        element={<DashboardOverview />} />
              <Route path="predictions"     element={<PredictionsPage />} />
              <Route path="weak-areas"      element={<WeakAreasPage />} />
              <Route path="recommendations" element={<RecommendationsPage />} />
              <Route path="chat"            element={<ChatPage />} />
            </Route>

            {/* 404 fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
