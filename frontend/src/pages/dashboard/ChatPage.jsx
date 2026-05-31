import PageHeader from '../../components/layout/PageHeader'

export default function ChatPage() {
  return (
    <div>
      <PageHeader
        badge="Dashboard"
        title="Chat"
        description="Interact with the EduSight AI assistant."
      />
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 text-center">
        <p className="text-sm text-[#52525b]">
          Chat interface coming in Task 7.
        </p>
      </div>
    </div>
  )
}
