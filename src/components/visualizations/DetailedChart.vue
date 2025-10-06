<template>
  <div class="detailed-chart-container">
    <div class="chart-header">
      <h2>{{ field }} - Detailed View</h2>
      <button @click="closeChart" class="close-button">Close</button>
    </div>
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{
  data: Array<{ time: Date; value: number }>
  field: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const chartContainer = ref<HTMLElement | null>(null)

const closeChart = () => {
  emit('close')
}

// Create detailed line chart
const createLineChart = () => {
  if (!chartContainer.value || !props.data.length) return

  // Clear previous chart
  chartContainer.value.innerHTML = ''

  // Set dimensions and margins
  const marginTop = 20
  const marginRight = 30
  const marginBottom = 30
  const marginLeft = 40
  const width = 800
  const height = 400

  // Create SVG
  const svg = d3
    .select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;')

  // Create scales
  const x = d3
    .scaleTime()
    .domain(d3.extent(props.data, (d) => d.time) as [Date, Date])
    .range([marginLeft, width - marginRight])

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(props.data, (d) => d.value) as number])
    .nice()
    .range([height - marginBottom, marginTop])

  // Create axes
  const xAxis = d3.axisBottom(x).ticks(width / 80)
  const yAxis = d3.axisLeft(y).ticks(height / 40)

  // Add X axis
  svg
    .append('g')
    .attr('transform', `translate(0,${height - marginBottom})`)
    .call(xAxis)

  // Add Y axis
  svg.append('g').attr('transform', `translate(${marginLeft},0)`).call(yAxis)

  // Add grid lines
  svg
    .append('g')
    .attr('transform', `translate(0,${height - marginBottom})`)
    .call(xAxis.tickSize(-height + marginTop + marginBottom).tickFormat(() => ''))
    .attr('stroke-opacity', 0.1)

  svg
    .append('g')
    .attr('transform', `translate(${marginLeft},0)`)
    .call(yAxis.tickSize(-width + marginLeft + marginRight).tickFormat(() => ''))
    .attr('stroke-opacity', 0.1)

  // Create line generator
  const line = d3
    .line<{ time: Date; value: number }>()
    .defined((d) => !isNaN(d.value))
    .x((d) => x(d.time))
    .y((d) => y(d.value))

  // Add the line
  svg
    .append('path')
    .datum(props.data)
    .attr('fill', 'none')
    .attr('stroke', 'steelblue')
    .attr('stroke-width', 1.5)
    .attr('d', line)

  // Add dots
  svg
    .append('g')
    .selectAll('circle')
    .data(props.data.filter((d) => !isNaN(d.value)))
    .enter()
    .append('circle')
    .attr('cx', (d) => x(d.time))
    .attr('cy', (d) => y(d.value))
    .attr('r', 2)
    .attr('fill', 'steelblue')

  // Add labels
  svg
    .append('text')
    .attr('transform', `translate(${width / 2},${height - 5})`)
    .style('text-anchor', 'middle')
    .text('Time')

  svg
    .append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', 0)
    .attr('x', 0 - height / 2)
    .attr('dy', '1em')
    .style('text-anchor', 'middle')
    .text('Value')
}

onMounted(() => {
  createLineChart()
})

watch(
  () => props.data,
  () => {
    createLineChart()
  }
)
</script>

<style scoped>
.detailed-chart-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 20px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-button {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
}

.close-button:hover {
  background-color: #d32f2f;
}

.chart-container {
  width: 100%;
  overflow-x: auto;
}
</style>
