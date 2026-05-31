/**
 * EduSight AI — Home / Landing Page
 * Clean. No marketing fluff. Direct.
 * Think: Vercel homepage, not a startup landing page.
 */

import { Link } from 'react-router-dom'
import { ArrowRight, BarChart2, TrendingUp, Target, Zap } from 'lucide-react'
import Button from '../components/ui/Button'
import Divider from '../components/ui/Divider'

const features = [
  {
    icon: BarChart2,
    title: 'Performance Analytics',
    description:
      'Subject-wise radar charts, grade trends, and cohort comparisons — all from a single CSV.',
  },
  {
    icon: TrendingUp,
    title: 'Predictive Insights',
    description:
      'ML models forecast upcoming exam performance with confidence intervals.',
  },
  {
    icon: Target,
    title: 'Weak Area Detection',
    description:
      'Automatically identifies and ranks improvement areas by impact on overall performance.',
  },
  {
    icon: Zap,
    title: 'AI Study Plans',
    description:
      'RAG-powered recommendations match each student\'s gaps to curated study resources.',
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* ── Hero ── */}
      <section className="max-w-3xl mx-auto px-6 pt-24 pb-16 text-center">
        {/* Label */}
        <div className="inline-flex items-center gap-2 px-3 py-1
          bg-[#111111] border border-[#1f1f1f] rounded-full
          text-[11px] font-medium text-[#52525b] uppercase tracking-widest
          mb-8"
        >
          <div className="w-1.5 h-1.5 rounded-full bg-[#4f46e5]" />
          Student Intelligence Platform
        </div>

        {/* Heading */}
        <h1 className="text-[2.5rem] font-semibold text-[#f5f5f5]
          tracking-[-0.04em] leading-[1.15] mb-4">
          Understand every student.<br />
          <span className="text-[#52525b]">Improve every outcome.</span>
        </h1>

        {/* Subtext */}
        <p className="text-sm text-[#52525b] leading-relaxed max-w-lg mx-auto mb-10">
          Upload a marks CSV. EduSight AI analyzes patterns, predicts performance,
          identifies weak areas, and generates personalized study recommendations.
        </p>

        {/* CTAs */}
        <div className="flex items-center justify-center gap-3">
          <Link to="/upload">
            <Button
              variant="primary"
              size="lg"
              iconRight={ArrowRight}
            >
              Upload CSV
            </Button>
          </Link>
          <Link to="/students">
            <Button variant="secondary" size="lg">
              View Students
            </Button>
          </Link>
        </div>
      </section>

      <Divider className="max-w-3xl mx-auto" />

      {/* ── Features Grid ── */}
      <section className="max-w-3xl mx-auto px-6 py-16">
        <p className="text-[11px] font-medium text-[#52525b] uppercase
          tracking-widest mb-8">
          What it does
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-px
          bg-[#1f1f1f] border border-[#1f1f1f] rounded-lg overflow-hidden"
        >
          {features.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="bg-[#0a0a0a] p-6 hover:bg-[#111111]
                transition-colors duration-150"
            >
              <div className="w-8 h-8 rounded-md bg-[#111111] border
                border-[#1f1f1f] flex items-center justify-center mb-4"
              >
                <Icon size={15} strokeWidth={1.5} className="text-[#4f46e5]" />
              </div>
              <h3 className="text-sm font-medium text-[#f5f5f5] mb-1.5">
                {title}
              </h3>
              <p className="text-xs text-[#52525b] leading-relaxed">
                {description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-[#1f1f1f] py-6">
        <div className="max-w-3xl mx-auto px-6 flex items-center
          justify-between">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-[#4f46e5] rounded-md
              flex items-center justify-center">
              <BarChart2 size={11} strokeWidth={2} className="text-white" />
            </div>
            <span className="text-xs text-[#52525b]">EduSight AI</span>
          </div>
          <p className="text-xs text-[#3f3f46]">
            Built for student success
          </p>
        </div>
      </footer>
    </div>
  )
}
