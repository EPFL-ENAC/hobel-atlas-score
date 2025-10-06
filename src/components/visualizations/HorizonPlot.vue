<template>
  <div class="horizon-plot-container">
    <div ref="chartContainer" class="chart-container"></div>

    <!-- Detailed chart overlay -->
    <div v-if="showDetailedChart" class="overlay" @click="closeDetailedChart">
      <DetailedChart :data="selectedFieldData" :field="selectedField" @close="closeDetailedChart" />
    </div>
    <q-btn @click="downloadSVG" outline icon="download" label="Download SVG" class="download-btn" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import atlasScoreData from '../../assets/atlas_score_example.csv?raw'
import DetailedChart from './DetailedChart.vue'

// Define props
const props = defineProps<{
  bandHeight: number
  numBands: number
  dataProperty: 'value' | 'score'
}>()

const chartContainer = ref<HTMLElement | null>(null)
const selectedFieldData = ref<Array<{ time: Date; value: number }>>([])
const selectedField = ref<string>('')
const showDetailedChart = ref<boolean>(false)

interface EnvironmentalData {
  id: number
  time: Date
  category: string
  field: string
  value: number
  score: number
}

// Download the SVG as a file
const downloadSVG = () => {
  if (!chartContainer.value) return

  // Get the SVG element
  const svgElement = chartContainer.value.querySelector('svg')
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
  link.download = `horizon-plot-${props.dataProperty}.svg`

  // Trigger the download
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  // Clean up the URL object
  URL.revokeObjectURL(url)
}

// Parse CSV data
const parseData = (): EnvironmentalData[] => {
  const lines = atlasScoreData.trim().split('\n')
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

const openDetailedChart = (field: string, data: Array<{ time: Date; value: number }>) => {
  selectedField.value = field
  selectedFieldData.value = data
  showDetailedChart.value = true
}

const closeDetailedChart = () => {
  showDetailedChart.value = false
}

// Create horizon plot
const createHorizonPlot = (data: EnvironmentalData[]) => {
  if (!chartContainer.value) return

  // Clear previous chart
  chartContainer.value.innerHTML = ''

  // Group data by category first, then by field
  const groupedByCategory = d3.group(data, (d) => d.category)

  // Define custom order for categories
  const categoryOrder = ['Luminous comfort', 'Air quality', 'Acoustic comfort', 'Thermal comfort']

  // Sort categories according to custom order
  const categories = Array.from(groupedByCategory.keys()).sort((a, b) => {
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

  // Function to get color scheme for a category
  const getCategoryColors = (category: string, bands: number): string[] => {
    let colorScheme: readonly string[] | undefined

    switch (category) {
      case 'Air quality':
        colorScheme = d3.schemeGreens[bands + 1]
        break
      case 'Acoustic comfort':
        // Using blues for acoustic comfort (associated with calmness and tranquility)
        colorScheme = d3.schemeBlues[bands + 1]
        break
      case 'Thermal comfort':
        // Using reds/oranges for thermal comfort (associated with heat/warmth)
        colorScheme = d3.schemeReds[bands + 1]
        break
      case 'Luminous comfort':
        // Using yellows for luminous comfort (associated with light/brightness)
        colorScheme = d3.schemeYlOrBr[bands + 1]
        break
      default:
        colorScheme = d3.schemeGreys[bands + 1]
    }

    return colorScheme?.slice(1) || ['#deebf7', '#9ecae1', '#3182bd']
  }

  // Calculate total number of fields across all categories
  let totalFields = 0
  categories.forEach((category) => {
    const categoryData = groupedByCategory.get(category) || []
    const fieldsInCategory = Array.from(new Set(categoryData.map((d) => d.field)))
    totalFields += fieldsInCategory.length
  })

  // Set dimensions and margins
  const marginTop = 30
  const marginBottom = 0
  const marginLeft = 30
  const marginRight = 15
  const width = 928
  const size = props.bandHeight // height of each band
  const height = totalFields * size + categories.length * 30 + marginTop + marginBottom // Extra space for category labels
  const padding = 1
  const bands = props.numBands // number of bands for horizon effect

  // Create SVG
  const svg = d3
    .select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .attr(
      'style',
      'max-width: 100%; height: auto; font: 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;'
    )

  // Create a global time scale using the extent of the entire dataset
  const globalTimeExtent = d3.extent(data, (d) => d.time) as [Date, Date]
  const globalX = d3
    .scaleTime()
    .domain(globalTimeExtent)
    .nice()
    .range([0, width - marginLeft - marginRight])

  let yOffset = marginTop
  let globalIndex = 0

  // Process each category
  categories.forEach((category, catIndex) => {
    const categoryData = groupedByCategory.get(category) || []
    const groupedByField = d3.group(categoryData, (d) => d.field)
    const fields = Array.from(groupedByField.keys())

    // Calculate the vertical center of this category's fields
    const fieldsInCategory = fields.length
    const categoryHeight = fieldsInCategory * size
    const categoryCenter = yOffset + categoryHeight / 2

    // Get color scheme for this category
    const colors = getCategoryColors(category, bands)

    // Add category header on the left side, rotated 90 degrees
    svg
      .append('text')
      .attr('x', 10)
      .attr('y', categoryCenter)
      .attr('dy', '0.35em')
      .attr('font-weight', 'bold')
      .attr('text-anchor', 'middle')
      .attr('transform', `rotate(-90, 10, ${categoryCenter})`)
      .attr('stroke', 'white')
      .attr('stroke-width', 0.5)
      .attr('stroke-opacity', 0.7)
      .attr('paint-order', 'stroke')
      .text(category)

    // Process each field within the category
    fields.forEach((field, fieldIndex) => {
      const fieldData = groupedByField.get(field) || []

      // Get the property to use for plotting
      const plotProperty = props.dataProperty

      // Use the global time scale for all fields
      const x = globalX

      // Create the vertical scale
      const y = d3
        .scaleLinear()
        .domain([0, d3.max(fieldData, (d) => d[plotProperty]) as number])
        .range([size, size - bands * (size - padding)])

      // Create area generator
      const area = d3
        .area<EnvironmentalData>()
        .defined((d) => !isNaN(d[plotProperty]) && d[plotProperty] > 0)
        .x((d) => x(d.time))
        .y0(size)
        .y1((d) => y(d[plotProperty]))

      // Unique identifier for clip rect and reusable paths
      const uid = `O-${Math.random().toString(16).slice(2)}`

      // Create a G element for each field, accounting for left margin
      const g = svg.append('g').attr('transform', `translate(${marginLeft},${yOffset})`)

      // Add a rectangular clipPath and the reference area
      const defs = g.append('defs')

      defs
        .append('clipPath')
        .attr('id', `${uid}-clip-${globalIndex}`)
        .append('rect')
        .attr('y', padding)
        .attr('width', width - marginLeft - marginRight)
        .attr('height', size - padding)

      defs.append('path').attr('id', `${uid}-path-${globalIndex}`).attr('d', area(fieldData))

      // Create a group for each field, in which the reference area will be replicated
      // (with the SVG:use element) for each band, and translated
      const bandGroup = g.append('g').attr('clip-path', `url(#${uid}-clip-${globalIndex})`)

      // Add click handler to the group
      g.style('cursor', 'pointer').on('click', () => {
        // Prepare data for detailed chart (using the current plot property)
        const chartData = fieldData.map((d) => ({ time: d.time, value: d[plotProperty] }))
        openDetailedChart(`${category} - ${field}`, chartData)
      })

      bandGroup
        .selectAll('use')
        .data(new Array(bands).fill(globalIndex))
        .enter()
        .append('use')
        .attr('xlink:href', `#${uid}-path-${globalIndex}`)
        .attr('fill', (_, j) => colors[j] ?? '#ccc')
        .attr('transform', (_, j) => `translate(0,${j * size})`)

      // Add the labels with a subtle stroke for better readability
      g.append('text')
        .attr('x', 10)
        .attr('y', (size + padding) / 2)
        .attr('dy', '0.35em')
        .attr('font-size', 12)
        .attr(
          'font-family',
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
        )
        .attr('font-weight', 'bold')
        .attr('stroke', 'white')
        .attr('stroke-width', 3)
        .attr('stroke-opacity', 0.8)
        .attr('paint-order', 'stroke')
        .text(field.replace(/_/g, ' ').toUpperCase())

      // Add the horizontal axis (only for the first field of the first category)
      if (catIndex === 0 && fieldIndex === 0) {
        svg
          .append('g')
          .attr('transform', `translate(${marginLeft},${marginTop})`)
          .call(
            d3
              .axisTop(globalX)
              .ticks(d3.timeDay.every(1))
              .tickFormat(d3.timeFormat('%d/%m') as any)
          )
      }

      yOffset += size
      globalIndex++
    })

    // Add more spacing between categories
    yOffset += 30
  })
}

// Watch for prop changes and recreate the plot
watch(
  () => [props.bandHeight, props.numBands, props.dataProperty],
  () => {
    const data = parseData()
    createHorizonPlot(data)
  }
)

onMounted(() => {
  const data = parseData()
  createHorizonPlot(data)
})
</script>

<style scoped>
.horizon-plot-container {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.plot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.download-btn {
  margin-left: 10px;
}

.chart-container {
  width: 100%;
  overflow-x: auto;
}

.chart-container svg {
  display: block;
  margin: 0 auto;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}
</style>
