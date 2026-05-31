/**
 * Input Component
 * Label, error state, icon support.
 */

export function Input({
  label,
  error,
  hint,
  icon: Icon,
  className = '',
  required,
  ...props
}) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-[#a1a1aa]">
          {label}
          {required && <span className="text-[#ef4444] ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#52525b]">
            <Icon size={14} strokeWidth={1.5} />
          </div>
        )}
        <input
          className={`
            w-full h-8 bg-[#111111]
            border ${error ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}
            rounded-[6px]
            ${Icon ? 'pl-9 pr-3' : 'px-3'}
            text-sm text-[#f5f5f5]
            placeholder:text-[#3f3f46]
            focus:outline-none focus:border-[#4f46e5]
            focus:ring-1 focus:ring-[rgba(79,70,229,0.2)]
            transition-all duration-150
            disabled:opacity-40 disabled:cursor-not-allowed
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="text-xs text-[#ef4444]">{error}</p>
      )}
      {hint && !error && (
        <p className="text-xs text-[#52525b]">{hint}</p>
      )}
    </div>
  )
}

export function Textarea({ label, error, hint, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-[#a1a1aa]">
          {label}
        </label>
      )}
      <textarea
        className={`
          w-full bg-[#111111]
          border ${error ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}
          rounded-[6px] p-3
          text-sm text-[#f5f5f5]
          placeholder:text-[#3f3f46]
          focus:outline-none focus:border-[#4f46e5]
          focus:ring-1 focus:ring-[rgba(79,70,229,0.2)]
          transition-all duration-150
          resize-none
          ${className}
        `}
        {...props}
      />
      {error && <p className="text-xs text-[#ef4444]">{error}</p>}
      {hint && !error && <p className="text-xs text-[#52525b]">{hint}</p>}
    </div>
  )
}
