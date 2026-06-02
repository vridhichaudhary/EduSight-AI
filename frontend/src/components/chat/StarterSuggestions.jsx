/**
 * EduSight AI — Starter Suggestions (Data-Aware)
 * Suggestions adapt to student's actual weak areas.
 */

import { TrendingUp, Target, BookOpen, BarChart2, AlertCircle } from 'lucide-react'

function buildSuggestions(weakSubjects = []) {
  const primary = weakSubjects[0] || null
  const secondary = weakSubjects[1] || null

  return [
    {
      icon:  BarChart2,
      label: 'How is my overall performance trending?',
    },
    {
      icon:  Target,
      label: primary
        ? `Why am I struggling with ${primary}?`
        : 'What are my weakest subjects?',
    },
    {
      icon:  TrendingUp,
      label: 'What are my predicted scores next exam?',
    },
    {
      icon:  BookOpen,
      label: secondary
        ? `Give me a study plan to improve ${secondary}.`
        : 'Give me a personalized study plan.',
    },
  ]
}

export default function StarterSuggestions({ onSelect, weakSubjects }) {
  const suggestions = buildSuggestions(weakSubjects)

  return (
    <div className="flex flex-col items-center justify-center h-full py-16 px-6">
      {/* Logo mark */}
      <div
        className="
          w-10 h-10 rounded-xl mb-6
          bg-[#111111] border border-[#1f1f1f]
          flex items-center justify-center
        "
      >
        <div className="w-4 h-4 rounded-md bg-[#4f46e5]" />
      </div>

      {/* Heading */}
      <h2 className="text-sm font-medium text-[#f5f5f5] mb-1 tracking-tight">
        Ask EduSight AI
      </h2>
      <p className="text-xs text-[#52525b] mb-8 text-center max-w-xs leading-relaxed">
        Ask questions about your performance, predictions, and study recommendations.
      </p>

      {/* Suggestion chips */}
      <div className="w-full max-w-sm space-y-2">
        {suggestions.map(({ icon: Icon, label }) => (
          <button
            key={label}
            onClick={() => onSelect(label)}
            className="
              w-full flex items-center gap-3
              px-4 py-3 rounded-lg
              bg-[#111111] border border-[#1f1f1f]
              hover:border-[#2a2a2a] hover:bg-[#161616]
              transition-all duration-150
              text-left group
            "
          >
            <div
              className="
                w-6 h-6 rounded-md flex-shrink-0
                bg-[#161616] border border-[#1f1f1f]
                flex items-center justify-center
                group-hover:border-[#2a2a2a]
                transition-colors duration-150
              "
            >
              <Icon
                size={12}
                strokeWidth={1.5}
                className="
                  text-[#52525b]
                  group-hover:text-[#71717a]
                  transition-colors
                "
              />
            </div>
            <span className="text-xs text-[#71717a] group-hover:text-[#a1a1aa] transition-colors">
              {label}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
