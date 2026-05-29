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

  const legendHeight = 100

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
    .attr('height', dimensions.height + legendHeight)
    .attr('viewBox', [0, 0, dimensions.width, dimensions.height + legendHeight])
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
  createLegend(svg, dimensions, props.numBands, categories)
}

// Create legend for the horizon plot
const createLegend = (
  svg: any,
  dimensions: ChartDimensions,
  numBands: number,
  categories: string[]
) => {
  const legendWidth = dimensions.width - dimensions.marginLeft - dimensions.marginRight
  const legendX = dimensions.marginLeft
  const legendY = dimensions.height - dimensions.marginBottom - 20

  const legendGroup = svg
    .append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${legendX}, ${legendY})`)

  // Add legend title
  legendGroup
    .append('text')
    .attr('x', 0)
    .attr('y', 15)
    .attr('text-anchor', 'left')
    .attr('font-weight', 'bold')
    .attr('font-size', '12px')
    .text('Legend')

  // Create explanation text
  legendGroup
    .append('text')
    .attr('x', 0)
    .attr('y', 30)
    .attr('text-anchor', 'left')
    .attr('font-size', '9px')
    .attr('fill', '#666')
    .text('Each band represents score ranges')

  // Show band ranges with spacing between categories
  const spacing = 20 // Space between categories
  const categoryWidth = (legendWidth - spacing * (categories.length - 1)) / categories.length
  const bandWidth = categoryWidth / numBands

  let xOffset = 0

  for (let y = 0; y < categories.length; y++) {
    const category = categories[y] as string
    const colors = getCategoryColors(category, numBands)

    // Create a group for each category
    const categoryGroup = legendGroup
      .append('g')
      .attr('class', `legend-category-${y}`)
      .attr('transform', `translate(${xOffset}, 0)`)

    // Add category title
    categoryGroup
      .append('text')
      .attr('x', categoryWidth / 2)
      .attr('y', 50)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text(category)

    console.log(colors)
    for (let i = 0; i < numBands; i++) {
      // Add color band
      categoryGroup
        .append('rect')
        .attr('x', i * bandWidth)
        .attr('y', 55)
        .attr('width', bandWidth)
        .attr('height', 15)
        .attr('fill', colors[i])
        .attr('stroke', 'white')
        .attr('stroke-width', 0.5)

      // Add percentage labels
      if (i === 0 || i === numBands - 1) {
        categoryGroup
          .append('text')
          .attr('x', i === 0 ? 0 : categoryWidth)
          .attr('y', 85)
          .attr('text-anchor', i === 0 ? 'start' : 'end')
          .attr('font-size', '9px')
          .text(`${i === 0 ? '0' : '100'}%`)
      }
    }

    xOffset += categoryWidth + spacing
  }
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
