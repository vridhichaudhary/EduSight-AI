/**
 * Badge Component
 * Status indicators. Minimal dot + text style.
 */

const variants = {
  default: 'bg-[#1a1a1a] text-[#a1a1aa] border border-[#2a2a2a]',
  success: 'bg-[rgba(34,197,94,0.08)] text-[#22c55e] border border-[rgba(34,197,94,0.15)]',
  warning: 'bg-[rgba(245,158,11,0.08)] text-[#f59e0b] border border-[rgba(245,158,11,0.15)]',
  danger:  'bg-[rgba(239,68,68,0.08)] text-[#ef4444] border border-[rgba(239,68,68,0.15)]',
  accent:  'bg-[rgba(79,70,229,0.08)] text-[#4f46e5] border border-[rgba(79,70,229,0.15)]',
  info:    'bg-[rgba(59,130,246,0.08)] text-[#3b82f6] border border-[rgba(59,130,246,0.15)]',
}

const dotColors = {
  default: '#52525b',
  success: '#22c55e',
  warning: '#f59e0b',
  danger:  '#ef4444',
  accent:  '#4f46e5',
  info:    '#3b82f6',
}

export default function Badge({
  children,
  variant = 'default',
  dot = false,
  className = '',
}) {
  return (
    <span
      className={`
        inline-flex items-center gap-1.5
        px-2 py-0.5 rounded-[4px]
        text-[11px] font-medium
        ${variants[variant]}
        ${className}
      `}
    >
      {dot && (
        <span
          className="w-1.5 h-1.5 rounded-full flex-shrink-0"
          style={{ backgroundColor: dotColors[variant] }}
        />
      )}
      {children}
    </span>
  )
}
