/**
 * EduSight AI — Excel File Parser
 * Parses .xlsx and .xls files to structured data using SheetJS (xlsx).
 */

import * as XLSX from 'xlsx'

const REQUIRED_COLS = [
  'student_name', 'subject', 'marks_obtained',
  'max_marks', 'exam_type', 'exam_date',
]

const COLUMN_ALIASES = {
  name: 'student_name', student: 'student_name', studentname: 'student_name',
  course: 'subject', class: 'subject',
  marks: 'marks_obtained', score: 'marks_obtained', obtained: 'marks_obtained',
  max: 'max_marks', total: 'max_marks', total_marks: 'max_marks',
  type: 'exam_type', exam: 'exam_type',
  date: 'exam_date', time: 'exam_date',
}

function normalizeHeader(h) {
  const clean = String(h || '').toLowerCase().trim().replace(/\s+/g, '_').replace(/-/g, '_')
  return COLUMN_ALIASES[clean] || clean
}

/**
 * Parse Excel file to array of row objects.
 * @param {File} file
 * @returns {Promise<{data, fields, errors}>}
 */
export async function parseExcelFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const data     = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array', cellDates: true })
        const sheetName = workbook.SheetNames[0]
        const sheet     = workbook.Sheets[sheetName]

        const rows = XLSX.utils.sheet_to_json(sheet, { raw: false, header: 1 })

        if (rows.length < 2) {
          reject(new Error('Excel file is empty or has no data rows'))
          return
        }

        const headers = rows[0].map(normalizeHeader)

        const dataRows = rows.slice(1).map((row) => {
          const obj = {}
          headers.forEach((header, i) => {
            obj[header] = row[i] !== undefined ? String(row[i]) : ''
          })
          return obj
        }).filter((row) => Object.values(row).some((v) => v && String(v).trim() !== ''))

        const missing = REQUIRED_COLS.filter((col) => !headers.includes(col))

        resolve({
          data:    dataRows,
          fields:  headers,
          missing,
          errors:  missing.length > 0 ? [`Missing columns: ${missing.join(', ')}`] : [],
        })
      } catch (err) {
        reject(new Error(`Excel parse failed: ${err.message}`))
      }
    }

    reader.onerror = () => reject(new Error('File read failed'))
    reader.readAsArrayBuffer(file)
  })
}
