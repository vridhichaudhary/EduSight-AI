import PageHeader from '../../components/layout/PageHeader'

export default function PredictionsPage() {
  return (
    <div>
      <PageHeader
        badge="Dashboard"
        title="Predictions"
        description="AI forecasted academic outcomes."
      />
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 text-center">
        <p className="text-sm text-[#52525b]">
          Predictions coming in Task 6.
        </p>
      </div>
    </div>
  )
}
