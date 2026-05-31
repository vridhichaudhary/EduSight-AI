/**
 * Dashboard Layout — wraps dashboard pages with sidebar
 */

import { Outlet, useParams } from 'react-router-dom'
import Sidebar from './Sidebar'
import useStore from '../../store/useStore'

export default function DashboardLayout() {
  const { studentId } = useParams()
  const { sidebarCollapsed } = useStore()

  return (
    <div className="flex min-h-[calc(100vh-3rem)]">
      <Sidebar studentId={studentId} />
      <main
        className={`
          flex-1 min-w-0
          transition-all duration-200 ease-in-out
          ${sidebarCollapsed ? 'ml-14' : 'ml-52'}
          p-8
        `}
      >
        <div className="page-enter max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
