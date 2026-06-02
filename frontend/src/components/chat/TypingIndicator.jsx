/**
 * EduSight AI — Typing Indicator
 * 3 animated dots shown while AI generates response.
 * Staggered pulse animation, not a spinner.
 */

export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-6 py-3">
      {/* AI avatar */}
      <div
        className="
          w-6 h-6 rounded-md
          bg-[#111111] border border-[#1f1f1f]
          flex items-center justify-center
          flex-shrink-0 mt-0.5
        "
      >
        <div className="w-2 h-2 rounded-sm bg-[#4f46e5]" />
      </div>

      {/* Dots */}
      <div className="flex items-center gap-1.5 h-8 pt-2">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[#3f3f46]"
            style={{
              animation: 'typingDot 1.2s ease-in-out infinite',
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes typingDot {
          0%, 60%, 100% {
            transform: translateY(0);
            background-color: #3f3f46;
          }
          30% {
            transform: translateY(-4px);
            background-color: #71717a;
          }
        }
      `}</style>
    </div>
  )
}
