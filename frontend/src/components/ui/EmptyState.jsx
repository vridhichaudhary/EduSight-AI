import Button from './Button'

export default function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  actionLabel,
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
      {Icon && (
        <div className="w-10 h-10 rounded-lg bg-[#161616] border border-[#1f1f1f] flex items-center justify-center mb-4">
          <Icon size={18} strokeWidth={1.5} className="text-[#52525b]" />
        </div>
      )}
      <h3 className="text-sm font-medium text-[#f5f5f5] mb-1">{title}</h3>
      {description && (
        <p className="text-xs text-[#52525b] max-w-xs leading-relaxed mb-4">
          {description}
        </p>
      )}
      {action && actionLabel && (
        <Button variant="secondary" size="sm" onClick={action}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
