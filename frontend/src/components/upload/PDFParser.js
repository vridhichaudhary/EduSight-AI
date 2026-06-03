/**
 * EduSight AI — PDF File Parser
 * Validates a PDF client-side; actual table extraction happens server-side via pdfplumber.
 */

/**
 * Validate a PDF file client-side (checks magic bytes).
 * @param {File} file
 * @returns {Promise<{valid, errors, note}>}
 */
export async function parsePDFFile(file) {
  return new Promise((resolve) => {
    const reader = new FileReader()

    reader.onload = () => {
      const arr    = new Uint8Array(reader.result).subarray(0, 4)
      const header = Array.from(arr).map((b) => b.toString(16).padStart(2, '0')).join('')
      const isPDF  = header.startsWith('25504446') // %PDF

      if (!isPDF) {
        resolve({
          valid:  false,
          errors: ['File does not appear to be a valid PDF'],
          note:   null,
        })
        return
      }

      resolve({
        valid:  true,
        errors: [],
        note: 'PDF validated ✓ — Table extraction happens server-side. Upload to see results.',
      })
    }

    reader.onerror = () => resolve({ valid: false, errors: ['Could not read PDF file'], note: null })
    reader.readAsArrayBuffer(file)
  })
}
