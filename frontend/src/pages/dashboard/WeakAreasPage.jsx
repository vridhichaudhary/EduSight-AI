import PageHeader from '../../components/layout/PageHeader'

export default function WeakAreasPage() {
  return (
    <div>
      <PageHeader
        badge="Dashboard"
        title="Weak Areas"
        description="Identified areas requiring attention."
      />
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 text-center">
        <p className="text-sm text-[#52525b]">
          Weak Areas coming in Task 6.
        </p>
      </div>
    </div>
  )
}
