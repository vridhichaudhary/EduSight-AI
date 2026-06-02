/**
 * EduSight AI — Top Navbar
 * Minimal. Logo left. Actions right.
 * Sticky. Subtle bottom border only.
 */

import { Link, useLocation } from 'react-router-dom'
import { BarChart2, Upload, Users, MessageSquare } from 'lucide-react'
import Button from '../ui/Button'

const navLinks = [
  { href: '/students', label: 'Students', icon: Users },
  { href: '/upload',   label: 'Upload',   icon: Upload },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <header
      className="
        fixed top-0 left-0 right-0 z-40
        h-12 bg-[#0a0a0a]
        border-b border-[#1f1f1f]
        flex items-center px-6
        gap-8
      "
    >
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 flex-shrink-0">
        <div className="w-6 h-6 bg-[#4f46e5] rounded-md flex items-center justify-center">
          <BarChart2 size={13} strokeWidth={2} className="text-white" />
        </div>
        <span className="text-sm font-semibold text-[#f5f5f5] tracking-tight">
          EduSight
          <span className="text-[#4f46e5] ml-0.5">AI</span>
        </span>
      </Link>

      {/* Divider */}
      <div className="h-4 w-px bg-[#1f1f1f]" />

      {/* Nav Links */}
      <nav className="flex items-center gap-1">
        {navLinks.map(({ href, label, icon: Icon }) => {
          const isActive = pathname.startsWith(href)
          return (
            <Link
              key={href}
              to={href}
              className={`
                inline-flex items-center gap-1.5
                h-7 px-3 rounded-md text-xs font-medium
                transition-all duration-150
                ${
                  isActive
                    ? 'bg-[#161616] text-[#f5f5f5]'
                    : 'text-[#71717a] hover:text-[#a1a1aa] hover:bg-[#161616]'
                }
              `}
            >
              <Icon size={13} strokeWidth={1.5} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Right Actions */}
      <div className="ml-auto flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => window.open('http://localhost:8000/api/docs/', '_blank')}
        >
          API Docs
        </Button>
        <Link to="/upload">
          <Button variant="primary" size="sm">
            Upload CSV
          </Button>
        </Link>
      </div>
    </header>
  )
}
