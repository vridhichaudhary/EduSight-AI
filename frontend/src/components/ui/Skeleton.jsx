/**
 * Skeleton Loader Component
 * Used while data is loading.
 * Never show spinners for page content. Use skeletons.
 */

export function Skeleton({ className = '', ...props }) {
  return (
    <div
      className={`skeleton rounded-md ${className}`}
      {...props}
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-5 space-y-3">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-7 w-32" />
      <Skeleton className="h-3 w-48" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }) {
  return (
    <div className="space-y-px">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="flex gap-4 px-4 py-3 bg-[#111111] border-b border-[#1f1f1f]"
        >
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-20 ml-auto" />
        </div>
      ))}
    </div>
  )
}

export function SkeletonChart() {
  return (
    <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-5">
      <div className="flex items-center justify-between mb-6">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-6 w-20 rounded-md" />
      </div>
      <Skeleton className="h-48 w-full rounded-md" />
    </div>
  )
}
