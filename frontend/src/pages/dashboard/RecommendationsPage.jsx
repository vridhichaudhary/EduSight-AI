import PageHeader from '../../components/layout/PageHeader'

export default function RecommendationsPage() {
  return (
    <div>
      <PageHeader
        badge="Dashboard"
        title="Recommendations"
        description="Personalized study plans."
      />
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 text-center">
        <p className="text-sm text-[#52525b]">
          Recommendations coming in Task 6.
        </p>
      </div>
    </div>
  )
}
