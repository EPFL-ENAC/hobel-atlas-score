import { ref } from 'vue'
import * as d3 from 'd3'

// Available D3 color schemes
export const availableSchemes = [
  // Discrete color schemes
  { label: 'Blues', value: 'schemeBlues', schemeName: 'schemeBlues' },
  { label: 'Greens', value: 'schemeGreens', schemeName: 'schemeGreens' },
  { label: 'Greys', value: 'schemeGreys', schemeName: 'schemeGreys' },
  { label: 'Oranges', value: 'schemeOranges', schemeName: 'schemeOranges' },
  { label: 'Purples', value: 'schemePurples', schemeName: 'schemePurples' },
  { label: 'Reds', value: 'schemeReds', schemeName: 'schemeReds' },
  { label: 'Blue-Green', value: 'schemeBuGn', schemeName: 'schemeBuGn' },
  { label: 'Blue-Purple', value: 'schemeBuPu', schemeName: 'schemeBuPu' },
  { label: 'Green-Blue', value: 'schemeGnBu', schemeName: 'schemeGnBu' },
  { label: 'Orange-Red', value: 'schemeOrRd', schemeName: 'schemeOrRd' },
  { label: 'Purple-Blue-Green', value: 'schemePuBuGn', schemeName: 'schemePuBuGn' },
  { label: 'Purple-Blue', value: 'schemePuBu', schemeName: 'schemePuBu' },
  { label: 'Purple-Red', value: 'schemePuRd', schemeName: 'schemePuRd' },
  { label: 'Red-Purple', value: 'schemeRdPu', schemeName: 'schemeRdPu' },
  { label: 'Yellow-Green-Blue', value: 'schemeYlGnBu', schemeName: 'schemeYlGnBu' },
  { label: 'Yellow-Green', value: 'schemeYlGn', schemeName: 'schemeYlGn' },
  { label: 'Yellow-Orange-Brown', value: 'schemeYlOrBr', schemeName: 'schemeYlOrBr' },
  { label: 'Yellow-Orange-Red', value: 'schemeYlOrRd', schemeName: 'schemeYlOrRd' },
  // Interpolation-based color schemes
  { label: 'Turbo', value: 'interpolateTurbo', schemeName: 'interpolateTurbo' },
  { label: 'Viridis', value: 'interpolateViridis', schemeName: 'interpolateViridis' },
  { label: 'Inferno', value: 'interpolateInferno', schemeName: 'interpolateInferno' },
  { label: 'Magma', value: 'interpolateMagma', schemeName: 'interpolateMagma' },
  { label: 'Plasma', value: 'interpolatePlasma', schemeName: 'interpolatePlasma' },
  { label: 'Cividis', value: 'interpolateCividis', schemeName: 'interpolateCividis' },
  { label: 'Warm', value: 'interpolateWarm', schemeName: 'interpolateWarm' },
  { label: 'Cool', value: 'interpolateCool', schemeName: 'interpolateCool' }
]

// Default color schemes for each category
const defaultSchemes = {
  'Air quality': 'schemeGreens',
  'Thermal comfort': 'schemeReds',
  'Luminous comfort': 'schemeYlOrBr',
  'Acoustic comfort': 'schemeBlues'
}

export const useColorSchemes = () => {
  // Reactive color scheme selections for each category
  const categoryColorSchemes = ref({
    'Air quality': defaultSchemes['Air quality'],
    'Thermal comfort': defaultSchemes['Thermal comfort'],
    'Luminous comfort': defaultSchemes['Luminous comfort'],
    'Acoustic comfort': defaultSchemes['Acoustic comfort']
  })

  // Helper function to generate discrete colors from interpolation functions
  // Inspired by Observable's ramp function for better color sampling
  const generateColorsFromInterpolation = (
    interpolator: (t: number) => string,
    count: number
  ): string[] => {
    const colors: string[] = []
    for (let i = 0; i < count; i++) {
      const t = i / (count - 1) // Map index to [0, 1] range
      // Use d3.rgb().hex() to ensure proper color format and consistency
      colors.push(d3.rgb(interpolator(t)).hex())
    }
    return colors
  }

  // Enhanced function to get colors for any scheme (discrete or interpolation)
  const getSchemeColors = (schemeName: string, count: number): string[] => {
    // First try to get discrete scheme if it exists
    if (!schemeName.startsWith('interpolate')) {
      try {
        const discreteScheme = (d3 as any)[schemeName]
        if (discreteScheme && discreteScheme[count]) {
          return [...discreteScheme[count]] // Return copy of the array
        }
      } catch {
        // Continue to interpolation fallback
      }
    }

    // Try interpolation function
    const interpolateName = schemeName.startsWith('interpolate')
      ? schemeName
      : `interpolate${schemeName.replace('scheme', '')}`

    try {
      const interpolator = (d3 as any)[interpolateName]
      if (typeof interpolator === 'function') {
        return generateColorsFromInterpolation(interpolator, count)
      }
    } catch {
      // Continue to fallback
    }

    // Fallback to default blue scheme
    const defaultInterpolator = d3.interpolateBlues
    return generateColorsFromInterpolation(defaultInterpolator, count)
  }

  // Function to get colors for a category with specified number of bands
  const getCategoryColors = (category: string, bands: number): string[] => {
    const schemeName =
      categoryColorSchemes.value[category as keyof typeof categoryColorSchemes.value]

    // Use the enhanced getSchemeColors function and slice to exclude the lightest color
    // This follows D3's convention where the first color is typically too light for good contrast
    const colors = getSchemeColors(schemeName, bands + 1)
    return colors.slice(1) // Remove the first (lightest) color
  }

  // Function to get the base color (darkest) for a category
  const getCategoryBaseColor = (category: string): string => {
    const colors = getCategoryColors(category, 6) // Get max colors
    return colors[colors.length - 1] || '#6b7280'
  }

  // Function to update a category's color scheme
  const updateCategoryColorScheme = (category: string, scheme: string) => {
    if (category in categoryColorSchemes.value) {
      categoryColorSchemes.value[category as keyof typeof categoryColorSchemes.value] = scheme
    }
  }

  return {
    categoryColorSchemes,
    availableSchemes,
    getCategoryColors,
    getCategoryBaseColor,
    updateCategoryColorScheme
  }
}
