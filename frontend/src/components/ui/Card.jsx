/**
 * Card Component
 * Clean surface container with optional header and footer.
 */

export function Card({ children, className = '', hover = false, ...props }) {
  return (
    <div
      className={`
        bg-[#111111] border border-[#1f1f1f] rounded-lg
        ${hover ? 'hover:border-[#2a2a2a] transition-colors duration-150 cursor-pointer' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }) {
  return (
    <div
      className={`
        px-5 py-4 border-b border-[#1f1f1f]
        flex items-center justify-between
        ${className}
      `}
    >
      {children}
    </div>
  )
}

export function CardTitle({ children, className = '' }) {
  return (
    <h3
      className={`
        text-sm font-medium text-[#f5f5f5]
        tracking-[-0.01em]
        ${className}
      `}
    >
      {children}
    </h3>
  )
}

export function CardDescription({ children, className = '' }) {
  return (
    <p className={`text-xs text-[#52525b] mt-0.5 ${className}`}>
      {children}
    </p>
  )
}

export function CardBody({ children, className = '' }) {
  return (
    <div className={`p-5 ${className}`}>
      {children}
    </div>
  )
}

export function CardFooter({ children, className = '' }) {
  return (
    <div
      className={`
        px-5 py-3 border-t border-[#1f1f1f]
        flex items-center justify-between
        ${className}
      `}
    >
      {children}
    </div>
  )
}
