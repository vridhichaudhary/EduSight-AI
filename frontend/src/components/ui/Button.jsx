/**
 * Button Component
 * Variants: primary, secondary, ghost, danger, outline
 * Sizes: sm, md, lg
 */

import { Loader2 } from 'lucide-react'

const variants = {
  primary:
    'bg-accent text-white hover:bg-accent-hover border border-transparent',
  secondary:
    'bg-[#1a1a1a] text-[#f5f5f5] hover:bg-[#222] border border-[#2a2a2a]',
  ghost:
    'bg-transparent text-[#a1a1aa] hover:text-[#f5f5f5] hover:bg-[#161616] border border-transparent',
  danger:
    'bg-transparent text-[#ef4444] hover:bg-[rgba(239,68,68,0.08)] border border-[rgba(239,68,68,0.2)]',
  outline:
    'bg-transparent text-[#f5f5f5] border border-[#2a2a2a] hover:border-[#3f3f46]',
}

const sizes = {
  sm: 'h-7 px-3 text-xs gap-1.5',
  md: 'h-8 px-4 text-sm gap-2',
  lg: 'h-10 px-5 text-sm gap-2',
}

export default function Button({
  children,
  variant = 'secondary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  iconRight: IconRight,
  className = '',
  ...props
}) {
  return (
    <button
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center
        font-medium rounded-[6px]
        transition-all duration-150
        disabled:opacity-40 disabled:cursor-not-allowed
        select-none whitespace-nowrap
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {loading ? (
        <Loader2 size={14} className="animate-spin" />
      ) : Icon ? (
        <Icon size={14} strokeWidth={1.5} />
      ) : null}
      {children}
      {IconRight && !loading && (
        <IconRight size={14} strokeWidth={1.5} />
      )}
    </button>
  )
}
