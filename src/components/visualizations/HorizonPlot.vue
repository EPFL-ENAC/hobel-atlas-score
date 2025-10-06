<template>
  <div class="horizon-plot-container">
    <div ref="chartContainer" class="chart-container"></div>
    <q-btn
      @click="handleDownloadSVG"
      outline
      icon="download"
      label="Download SVG"
      class="download-btn"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import atlasScoreData from '../../assets/atlas_score_example.csv?raw'
import { useHorizonChart } from '../../composables/useHorizonChart'
import { parseCSVData, downloadSVG, sortCategoriesByOrder } from '../../utils/chartUtils'
import { createExpandedLineChart, type ChartDimensions } from '../../utils/expandedChart'
import { createHorizonBand } from '../../utils/horizonBand'
import type { EnvironmentalData } from '../../composables/useHorizonChart'

// Define props
const props = defineProps<{
  bandHeight: number
  numBands: number
  dataProperty: 'value' | 'score'
}>()

const chartContainer = ref<HTMLElement | null>(null)
const { expandedField, toggleFieldExpansion, getCategoryColors, calculateTotalHeight } =
  useHorizonChart()

const handleDownloadSVG = () => {
  if (chartContainer.value) {
    downloadSVG(chartContainer.value, `horizon-plot-${props.dataProperty}.svg`)
  }
}

const createChart = () => {
  const data = parseCSVData(atlasScoreData)
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
    width: 928,
    height: 0, // Will be calculated
    padding: 1
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
          props.dataProperty,
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
          props.dataProperty,
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

    // Add more spacing between categories
    yOffset += 30
  })
}

// Watch for prop changes and recreate the plot
watch(
  () => [props.bandHeight, props.numBands, props.dataProperty],
  () => {
    createChart()
  }
)

onMounted(() => {
  createChart()
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
</style>
