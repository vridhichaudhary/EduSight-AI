import PageHeader from '../components/layout/PageHeader'

export default function UploadPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <PageHeader
        badge="Upload"
        title="Upload CSV"
        description="Import student marks to generate insights."
      />
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 text-center">
        <p className="text-sm text-[#52525b]">
          Upload page with react-dropzone coming in Task 6.
        </p>
      </div>
    </div>
  )
}
