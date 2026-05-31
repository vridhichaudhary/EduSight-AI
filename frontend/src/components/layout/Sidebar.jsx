/**
 * EduSight AI — Dashboard Sidebar
 * Appears on /dashboard/* routes only.
 * Minimal. Icon + label. Active state = accent left border.
 */

import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  Target,
  BookOpen,
  MessageSquare,
  ChevronLeft,
} from 'lucide-react'
import useStore from '../../store/useStore'

const navItems = [
  { href: 'overview',        label: 'Overview',        icon: LayoutDashboard },
  { href: 'predictions',     label: 'Predictions',     icon: TrendingUp },
  { href: 'weak-areas',      label: 'Weak Areas',      icon: Target },
  { href: 'recommendations', label: 'Recommendations', icon: BookOpen },
  { href: 'chat',            label: 'Ask AI',          icon: MessageSquare },
]

export default function Sidebar({ studentId }) {
  const { sidebarCollapsed, toggleSidebar } = useStore()

  return (
    <aside
      className={`
        fixed left-0 top-12 bottom-0 z-30
        bg-[#0a0a0a] border-r border-[#1f1f1f]
        flex flex-col
        transition-all duration-200 ease-in-out
        ${sidebarCollapsed ? 'w-14' : 'w-52'}
      `}
    >
      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-0.5">
        {navItems.map(({ href, label, icon: Icon }) => (
          <NavLink
            key={href}
            to={`/dashboard/${studentId}/${href}`}
            className={({ isActive }) => `
              flex items-center gap-3
              h-8 px-3 rounded-md
              text-xs font-medium
              transition-all duration-150
              group relative
              ${
                isActive
                  ? 'bg-[rgba(79,70,229,0.08)] text-[#f5f5f5]'
                  : 'text-[#71717a] hover:text-[#a1a1aa] hover:bg-[#161616]'
              }
            `}
          >
            {({ isActive }) => (
              <>
                {/* Active left border indicator */}
                {isActive && (
                  <div className="absolute left-0 top-1 bottom-1 w-0.5 bg-[#4f46e5] rounded-full" />
                )}
                <Icon
                  size={15}
                  strokeWidth={1.5}
                  className={isActive ? 'text-[#4f46e5]' : ''}
                />
                {!sidebarCollapsed && (
                  <span className="truncate">{label}</span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-2 border-t border-[#1f1f1f]">
        <button
          onClick={toggleSidebar}
          className="
            w-full h-8 flex items-center justify-center gap-2
            text-xs text-[#52525b] hover:text-[#a1a1aa]
            hover:bg-[#161616] rounded-md
            transition-all duration-150
          "
        >
          <ChevronLeft
            size={14}
            strokeWidth={1.5}
            className={`transition-transform duration-200 ${
              sidebarCollapsed ? 'rotate-180' : ''
            }`}
          />
          {!sidebarCollapsed && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  )
}
