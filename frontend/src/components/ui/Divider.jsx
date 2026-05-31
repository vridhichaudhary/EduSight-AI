export default function Divider({ label, className = '' }) {
  if (label) {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <div className="flex-1 h-px bg-[#1f1f1f]" />
        <span className="text-[11px] font-medium text-[#52525b] uppercase tracking-widest">
          {label}
        </span>
        <div className="flex-1 h-px bg-[#1f1f1f]" />
      </div>
    )
  }

  return <div className={`h-px bg-[#1f1f1f] ${className}`} />
}
