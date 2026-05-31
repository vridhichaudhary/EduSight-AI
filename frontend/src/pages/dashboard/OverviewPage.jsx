import PageHeader from '../../components/layout/PageHeader'

export default function OverviewPage() {
  return (
    <div>
      <PageHeader
        badge="Dashboard"
        title="Overview"
        description="Complete performance summary."
      />
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 text-center">
        <p className="text-sm text-[#52525b]">
          Charts and analytics coming in Task 6.
        </p>
      </div>
    </div>
  )
}
