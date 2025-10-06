import type { EnvironmentalData } from '../composables/useHorizonChart'

export const parseCSVData = (csvData: string): EnvironmentalData[] => {
  const lines = csvData.trim().split('\n')
  // Skip header line
  return lines
    .slice(1)
    .map((line) => {
      const values = line.split(',')
      // Ensure we have enough values
      if (values.length < 6) return null

      const id = parseInt(values[0] || '0')
      const timeStr = values[1] || ''
      const category = values[2] || ''
      const field = values[3] || ''
      const value = parseFloat(values[4] || '0')
      const score = parseFloat(values[5] || '0')

      // Validate parsed values
      if (isNaN(id) || !timeStr || isNaN(value) || isNaN(score)) return null

      return {
        id,
        time: new Date(timeStr),
        category,
        field,
        value,
        score
      }
    })
    .filter((item): item is EnvironmentalData => item !== null)
}

export const downloadSVG = (container: HTMLElement, filename: string) => {
  const svgElement = container.querySelector('svg')
  if (!svgElement) return

  // Serialize the SVG to a string
  const serializer = new XMLSerializer()
  let svgString = serializer.serializeToString(svgElement)

  // Add namespaces if they're missing
  if (!svgString.includes('xmlns')) {
    svgString = svgString.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
  }
  if (!svgString.includes('xmlns:xlink')) {
    svgString = svgString.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"')
  }

  // Create a blob from the SVG string
  const blob = new Blob([svgString], { type: 'image/svg+xml' })

  // Create a download link
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename

  // Trigger the download
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  // Clean up the URL object
  URL.revokeObjectURL(url)
}

export const sortCategoriesByOrder = (categories: string[]): string[] => {
  const categoryOrder = ['Luminous comfort', 'Air quality', 'Acoustic comfort', 'Thermal comfort']

  return categories.sort((a, b) => {
    const indexA = categoryOrder.indexOf(a)
    const indexB = categoryOrder.indexOf(b)

    // If both categories are in our custom order, sort according to that order
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB
    }

    // If only one category is in our custom order, it comes first
    if (indexA !== -1) {
      return -1
    }
    if (indexB !== -1) {
      return 1
    }

    // If neither category is in our custom order, maintain natural order
    return 0
  })
}
