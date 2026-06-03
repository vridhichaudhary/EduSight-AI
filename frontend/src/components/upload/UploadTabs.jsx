/**
 * EduSight AI — Upload Tabs
 * Toggles between File Upload and Manual Entry modes.
 */

export default function UploadTabs({ activeTab, onChange }) {
  const tabs = [
    { id: 'file',   label: 'Upload File',  desc: 'CSV, Excel, or PDF' },
    { id: 'manual', label: 'Manual Entry', desc: 'Type marks directly' },
  ]

  return (
    <div className="flex gap-1 p-1 bg-[#111111] border border-[#1f1f1f] rounded-lg mb-8 w-fit">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`
            flex flex-col items-start px-5 py-2.5 rounded-md
            transition-all duration-150
            ${activeTab === tab.id
              ? 'bg-[#1a1a2e] border border-[rgba(79,70,229,0.25)] shadow-sm'
              : 'hover:bg-[#161616] border border-transparent'
            }
          `}
        >
          <span className={`text-xs font-medium ${activeTab === tab.id ? 'text-[#f5f5f5]' : 'text-[#71717a]'}`}>
            {tab.label}
          </span>
          <span className="text-[11px] text-[#52525b] mt-0.5">{tab.desc}</span>
        </button>
      ))}
    </div>
  )
}
