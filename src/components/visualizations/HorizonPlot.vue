<template>
  <div class="horizon-plot-container">
    <div class="controls-section">
      <div class="control-item">
        <label>Variable:</label>
        <q-option-group
          :model-value="dataProperty"
          :options="[
            { label: 'Value', value: 'value' },
            { label: 'Score', value: 'score' }
          ]"
          type="radio"
          class="option-group"
          inline
          @update:model-value="updateDataProperty"
        />
      </div>
      <q-btn
        @click="handleDownloadSVG"
        outline
        icon="download"
        label="Download SVG"
        class="download-btn"
      />
      <q-btn
        @click="handleDownloadPNG"
        outline
        icon="download"
        label="Download PNG"
        class="download-btn"
      />
    </div>
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import atlasScoreData from '../../assets/atlas_score_example.csv?raw'
import { useHorizonChart } from '../../composables/useHorizonChart'
import {
  parseCSVData,
  downloadSVG,
  sortCategoriesByOrder,
  downloadPNG
} from '../../utils/chartUtils'
import { createExpandedLineChart, type ChartDimensions } from '../../utils/expandedChart'
import { createHorizonBand } from '../../utils/horizonBand'
import type { EnvironmentalData } from '../../composables/useHorizonChart'

// Define props
const props = defineProps<{
  bandHeight: number
  numBands: number
  customData?: EnvironmentalData[] | null
  colorSchemesComposable?: any
}>()

const dataProperty = ref<'value' | 'score'>('score')

const chartContainer = ref<HTMLElement | null>(null)
const { expandedField, toggleFieldExpansion, getCategoryColors, calculateTotalHeight } =
  useHorizonChart(props.colorSchemesComposable)

const handleDownloadSVG = () => {
  if (chartContainer.value) {
    downloadSVG(chartContainer.value, `horizon-plot-${dataProperty.value}.svg`)
  }
}
const handleDownloadPNG = () => {
  if (chartContainer.value) {
    downloadPNG(chartContainer.value, `horizon-plot-${dataProperty.value}.png`)
  }
}

const updateDataProperty = (value: 'value' | 'score') => {
  dataProperty.value = value
}

const createChart = () => {
  // Use custom data if available, otherwise use default data
  let data = props.customData || parseCSVData(atlasScoreData)

  createHorizonPlot(data)
}

const handleToggle = (fieldKey: string) => {
  toggleFieldExpansion(fieldKey, createChart)
}

// Create horizon plot
const createHorizonPlot = (data: EnvironmentalData[]) => {
  if (!chartContainer.value) return

  // Clear previous chart
  chartContainer.value.innerHTML = ''

  // Group data by category first, then by field
  const groupedByCategory = d3.group(data, (d) => d.category)
  const categories = sortCategoriesByOrder(Array.from(groupedByCategory.keys()))

  // Set dimensions and margins
  const dimensions: ChartDimensions = {
    marginTop: 30,
    marginBottom: 0,
    marginLeft: 30,
    marginRight: 15,
    width: 1024,
    height: 0, // Will be calculated
    padding: 0
  }

  const expandedHeight = 200
  const totalHeight = calculateTotalHeight(
    categories,
    groupedByCategory,
    props.bandHeight,
    expandedHeight
  )
  dimensions.height = totalHeight + dimensions.marginTop + dimensions.marginBottom

  // Create SVG
  const svg = d3
    .select(chartContainer.value)
    .append('svg')
    .attr('width', dimensions.width)
    .attr('height', dimensions.height)
    .attr('viewBox', [0, 0, dimensions.width, dimensions.height])
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
    .range([0, dimensions.width - dimensions.marginLeft - dimensions.marginRight])

  let yOffset = dimensions.marginTop
  let globalIndex = 0

  // Process each category
  categories.forEach((category, catIndex) => {
    const categoryData = groupedByCategory.get(category) || []
    const groupedByField = d3.group(categoryData, (d) => d.field)
    const fields = Array.from(groupedByField.keys())

    // Calculate the vertical center of this category's fields
    let categoryHeight = 0
    fields.forEach((field) => {
      const fieldKey = `${category}|${field}`
      const isExpanded = expandedField.value === fieldKey
      categoryHeight += isExpanded ? expandedHeight : props.bandHeight
    })

    const categoryCenter = yOffset + categoryHeight / 2

    // Get color scheme for this category
    const colors = getCategoryColors(category, props.numBands)

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
      const fieldKey = `${category}|${field}`
      const isExpanded = expandedField.value === fieldKey
      const currentSize = isExpanded ? expandedHeight : props.bandHeight

      if (isExpanded) {
        createExpandedLineChart(
          svg,
          fieldData,
          dataProperty.value,
          globalX,
          yOffset,
          currentSize,
          dimensions,
          field,
          fieldKey,
          handleToggle
        )
      } else {
        createHorizonBand(
          svg,
          fieldData,
          dataProperty.value,
          globalX,
          yOffset,
          currentSize,
          dimensions,
          colors,
          props.numBands,
          field,
          fieldKey,
          globalIndex,
          handleToggle
        )
      }

      // Add the horizontal axis (only for the first field of the first category)
      if (catIndex === 0 && fieldIndex === 0) {
        svg
          .append('g')
          .attr('transform', `translate(${dimensions.marginLeft},${dimensions.marginTop})`)
          .call(
            d3
              .axisTop(globalX)
              .ticks(d3.timeDay.every(1))
              .tickFormat(d3.timeFormat('%d/%m') as any)
          )
      }

      yOffset += currentSize
      globalIndex++
    })

    // Add a border line between categories (except after the last category)
    if (catIndex < categories.length - 1) {
      svg
        .append('line')
        .attr('x1', dimensions.marginLeft + 5)
        .attr('x2', dimensions.width - dimensions.marginRight)
        .attr('y1', yOffset + 25) // Center the line in the spacing
        .attr('y2', yOffset + 25)
        .attr('stroke', '#d1d5db') // Light gray color
        .attr('stroke-width', 5)
        // .attr('stroke-dasharray', '3,3') // Optional: make it dashed for subtlety
        .attr('opacity', 0.7)
    }

    // Add more spacing between categories
    yOffset += 50
  })

  // Add legend
  createLegend(svg, dimensions, props.numBands)
}

// Create legend for the horizon plot
const createLegend = (svg: any, dimensions: ChartDimensions, numBands: number) => {
  const legendWidth = 200
  const legendHeight = 80
  const legendX = dimensions.width - dimensions.marginRight - legendWidth - 10
  const legendY = dimensions.marginTop + 10

  const legendGroup = svg
    .append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${legendX}, ${legendY})`)

  // Add legend background
  legendGroup
    .append('rect')
    .attr('x', -10)
    .attr('y', -5)
    .attr('width', legendWidth + 20)
    .attr('height', legendHeight + 15)
    .attr('fill', 'rgba(255, 255, 255, 0.95)')
    .attr('stroke', '#ccc')
    .attr('stroke-width', 1)
    .attr('rx', 5)

  // Add legend title
  legendGroup
    .append('text')
    .attr('x', legendWidth / 2)
    .attr('y', 10)
    .attr('text-anchor', 'middle')
    .attr('font-weight', 'bold')
    .attr('font-size', '12px')
    .text('Horizon Bands')

  // Create explanation text
  legendGroup
    .append('text')
    .attr('x', legendWidth / 2)
    .attr('y', 25)
    .attr('text-anchor', 'middle')
    .attr('font-size', '9px')
    .attr('fill', '#666')
    .text('Each band represents value ranges')

  // Show band ranges
  const bandWidth = legendWidth / numBands

  for (let i = 0; i < numBands; i++) {
    // Use a gradient from light to dark blue for the legend
    const opacity = 0.3 + (i / (numBands - 1)) * 0.7
    const color = `rgba(49, 130, 189, ${opacity})`

    // Add color band
    legendGroup
      .append('rect')
      .attr('x', i * bandWidth)
      .attr('y', 35)
      .attr('width', bandWidth)
      .attr('height', 15)
      .attr('fill', color)
      .attr('stroke', 'white')
      .attr('stroke-width', 0.5)

    // Add percentage labels
    if (i === 0 || i === numBands - 1) {
      legendGroup
        .append('text')
        .attr('x', i === 0 ? 0 : legendWidth)
        .attr('y', 65)
        .attr('text-anchor', i === 0 ? 'start' : 'end')
        .attr('font-size', '9px')
        .text(`${i === 0 ? '0' : '100'}%`)
    }
  }

  // Add color scheme note
  legendGroup
    .append('text')
    .attr('x', legendWidth / 2)
    .attr('y', 78)
    .attr('text-anchor', 'middle')
    .attr('font-size', '8px')
    .attr('fill', '#888')
    .text('Colors vary by category')
}

// Watch for prop changes and recreate the plot
watch(
  () => [
    props.bandHeight,
    props.numBands,
    dataProperty.value,
    props.customData,
    props.colorSchemesComposable?.categoryColorSchemes,
    props.colorSchemesComposable?.customColors
  ],
  () => {
    createChart()
  },
  { deep: true }
)

onMounted(() => {
  createChart()
})
</script>

<style scoped>
.horizon-plot-container {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.controls-section {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
}

.series-filter {
  margin-right: auto;
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
</style>
