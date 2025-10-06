import { ref } from 'vue'
import * as d3 from 'd3'

export interface EnvironmentalData {
  id: number
  time: Date
  category: string
  field: string
  value: number
  score: number
}

export const useHorizonChart = () => {
  const expandedField = ref<string | null>(null)

  const toggleFieldExpansion = (fieldKey: string, recreateChart: () => void) => {
    if (expandedField.value === fieldKey) {
      expandedField.value = null // Collapse if already expanded
    } else {
      expandedField.value = fieldKey // Expand this field
    }
    recreateChart()
  }

  const getCategoryColors = (category: string, bands: number): string[] => {
    let colorScheme: readonly string[] | undefined

    switch (category) {
      case 'Air quality':
        colorScheme = d3.schemeGreens[bands + 1]
        break
      case 'Acoustic comfort':
        colorScheme = d3.schemeBlues[bands + 1]
        break
      case 'Thermal comfort':
        colorScheme = d3.schemeReds[bands + 1]
        break
      case 'Luminous comfort':
        colorScheme = d3.schemeYlOrBr[bands + 1]
        break
      default:
        colorScheme = d3.schemeGreys[bands + 1]
    }

    return colorScheme?.slice(1) || ['#deebf7', '#9ecae1', '#3182bd']
  }

  const calculateTotalHeight = (
    categories: string[],
    groupedByCategory: Map<string, EnvironmentalData[]>,
    bandHeight: number,
    expandedHeight = 200
  ): number => {
    let totalHeight = 0

    categories.forEach((category) => {
      const categoryData = groupedByCategory.get(category) || []
      const fieldsInCategory = Array.from(new Set(categoryData.map((d) => d.field)))

      fieldsInCategory.forEach((field) => {
        const fieldKey = `${category}|${field}`
        const isExpanded = expandedField.value === fieldKey
        totalHeight += isExpanded ? expandedHeight : bandHeight
      })

      totalHeight += 30 // Space between categories
    })

    return totalHeight
  }

  return {
    expandedField,
    toggleFieldExpansion,
    getCategoryColors,
    calculateTotalHeight
  }
}
