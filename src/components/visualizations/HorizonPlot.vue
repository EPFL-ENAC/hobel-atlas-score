<template>
  <div class="horizon-plot-container">
    <h2>Environmental Data Horizon Plot</h2>
    <div class="controls">
      <q-btn
        @click="toggleDataProperty"
        color="primary"
        :label="'Plotting: ' + (dataProperty === 'value' ? 'Raw Value' : 'Score')"
      />
    </div>
    <div ref="chartContainer" class="chart-container"></div>

    <!-- Detailed chart overlay -->
    <div v-if="showDetailedChart" class="overlay" @click="closeDetailedChart">
      <DetailedChart :data="selectedFieldData" :field="selectedField" @close="closeDetailedChart" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import atlasScoreData from '../../assets/atlas_score_example.csv?raw'
import DetailedChart from './DetailedChart.vue'

const chartContainer = ref<HTMLElement | null>(null)
const selectedFieldData = ref<Array<{ time: Date; value: number }>>([])
const selectedField = ref<string>('')
const showDetailedChart = ref<boolean>(false)
const dataProperty = ref<'value' | 'score'>('score')

interface EnvironmentalData {
  id: number
  time: Date
  category: string
  field: string
  value: number
  score: number
}

// Toggle between value and score properties
const toggleDataProperty = () => {
  dataProperty.value = dataProperty.value === 'value' ? 'score' : 'value'
  const data = parseData()
  createHorizonPlot(data)
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

  // Group data by field
  const groupedData = d3.group(data, (d) => d.field)

  // Get all unique fields
  const fields = Array.from(groupedData.keys())

  // Set dimensions and margins
  const marginTop = 30
  const marginRight = 10
  const marginBottom = 0
  const marginLeft = 10
  const width = 928
  const size = 60 // height of each band
  const height = fields.length * size + marginTop + marginBottom
  const padding = 1
  const bands = 3 // number of bands for horizon effect

  // Color scheme for bands
  const colors = d3.schemeBlues[bands + 1]?.slice(1) || ['#deebf7', '#9ecae1', '#3182bd']

  // Create SVG
  const svg = d3
    .select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;')

  // Process each field
  fields.forEach((field, i) => {
    const fieldData = groupedData.get(field) || []

    // Get the property to use for plotting
    const plotProperty = dataProperty.value

    // Create the horizontal (temporal) scale
    const x = d3
      .scaleUtc()
      .domain(d3.extent(fieldData, (d) => d.time) as [Date, Date])
      .range([0, width])

    // Create the vertical scale
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(fieldData, (d) => d[plotProperty]) as number])
      .range([size, size - bands * (size - padding)])

    // Create area generator
    const area = d3
      .area<EnvironmentalData>()
      .defined((d) => !isNaN(d[plotProperty]))
      .x((d) => x(d.time))
      .y0(size)
      .y1((d) => y(d[plotProperty]))

    // Unique identifier for clip rect and reusable paths
    const uid = `O-${Math.random().toString(16).slice(2)}`

    // Create a G element for each field
    const g = svg.append('g').attr('transform', `translate(0,${i * size + marginTop})`)

    // Add a rectangular clipPath and the reference area
    const defs = g.append('defs')

    defs
      .append('clipPath')
      .attr('id', `${uid}-clip-${i}`)
      .append('rect')
      .attr('y', padding)
      .attr('width', width)
      .attr('height', size - padding)

    defs.append('path').attr('id', `${uid}-path-${i}`).attr('d', area(fieldData))

    // Create a group for each field, in which the reference area will be replicated
    // (with the SVG:use element) for each band, and translated
    const bandGroup = g.append('g').attr('clip-path', `url(#${uid}-clip-${i})`)

    // Add click handler to the group
    g.style('cursor', 'pointer').on('click', () => {
      // Prepare data for detailed chart (using the current plot property)
      const chartData = fieldData.map((d) => ({ time: d.time, value: d[plotProperty] }))
      openDetailedChart(field, chartData)
    })

    bandGroup
      .selectAll('use')
      .data(new Array(bands).fill(i))
      .enter()
      .append('use')
      .attr('xlink:href', `#${uid}-path-${i}`)
      .attr('fill', (_, j) => colors[j] ?? '#ccc')
      .attr('transform', (_, j) => `translate(0,${j * size})`)

    // Add the labels
    g.append('text')
      .attr('x', 4)
      .attr('y', (size + padding) / 2)
      .attr('dy', '0.35em')
      .text(field)

    // Add the horizontal axis (only for the first field)
    if (i === 0) {
      svg
        .append('g')
        .attr('transform', `translate(0,${marginTop})`)
        .call(
          d3
            .axisTop(x)
            .ticks(width / 80)
            .tickSizeOuter(0)
        )
        .call((g) =>
          g
            .selectAll('.tick')
            .filter((d) => x(d as any) < marginLeft || x(d as any) >= width - marginRight)
            .remove()
        )
        .call((g) => g.select('.domain').remove())
    }
  })
}

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

.controls {
  margin-bottom: 10px;
}

.toggle-button {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
}

.toggle-button:hover {
  background-color: #45a049;
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
