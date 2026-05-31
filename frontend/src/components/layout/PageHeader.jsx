/**
 * PageHeader — consistent heading across all pages
 */

export default function PageHeader({ title, description, actions, badge }) {
  return (
    <div className="flex items-start justify-between mb-8">
      <div>
        {badge && (
          <div className="inline-flex items-center gap-1.5 mb-2
            text-[11px] font-medium text-[#52525b]
            uppercase tracking-widest"
          >
            <div className="w-1 h-1 rounded-full bg-[#4f46e5]" />
            {badge}
          </div>
        )}
        <h1 className="text-xl font-semibold text-[#f5f5f5] tracking-tight">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-[#52525b] mt-1 leading-relaxed">
            {description}
          </p>
        )}
      </div>
      {actions && (
        <div className="flex items-center gap-2 flex-shrink-0 ml-8">
          {actions}
        </div>
      )}
    </div>
  )
}
