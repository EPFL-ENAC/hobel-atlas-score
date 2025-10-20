<template>
  <div class="circular-plot-container">
    <div class="controls">
      <q-btn
        @click="handleDownloadSVG"
        outline
        icon="download"
        label="Download SVG"
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
import { parseCSVData, downloadSVG } from '../../utils/chartUtils'
import type { EnvironmentalData } from '../../composables/useHorizonChart'
import { useColorSchemes } from '../../composables/useColorSchemes'

// Define props
const props = defineProps<{
  dataProperty: 'value' | 'score'
  radius?: number
  innerRadius?: number
  customData?: EnvironmentalData[] | null
  colorSchemesComposable?: any
  numBands?: number
}>()

const chartContainer = ref<HTMLElement | null>(null)

const handleDownloadSVG = () => {
  if (chartContainer.value) {
    downloadSVG(chartContainer.value, `circular-category-plot-${props.dataProperty}.svg`)
  }
}

// Calculate average scores by category with banded colors
const calculateCategoryAverages = (data: EnvironmentalData[]) => {
  const groupedByCategory = d3.group(data, (d) => d.category)
  const categoryAverages: Array<{
    category: string
    average: number
    color: string
    band: number
  }> = []

  // Use color schemes from props or fallback to defaults
  const { getCategoryColors } = props.colorSchemesComposable || useColorSchemes()

  const numBands = props.numBands || 4
  const categoryOrder = ['Thermal comfort', 'Acoustics', 'Lighting', 'Air quality']

  // Process categories in the specified order
  categoryOrder.forEach((category) => {
    const categoryData = groupedByCategory.get(category)
    if (categoryData && categoryData.length > 0) {
      const values = categoryData.map((d) => (props.dataProperty === 'score' ? d.score : d.value))
      const average = d3.mean(values) || 0
      const roundedAverage = Math.round(average)

      // Get colors for this category based on the number of bands
      const colors = getCategoryColors(category, numBands)

      // Calculate which band this average falls into
      const bandSize = 100 / numBands
      let bandIndex = Math.floor(roundedAverage / bandSize)
      // Handle edge case where average is exactly 100
      if (bandIndex >= numBands) bandIndex = numBands - 1
      // Ensure bandIndex is not negative
      if (bandIndex < 0) bandIndex = 0

      // Get the color for this band
      const color = colors[bandIndex] || colors[colors.length - 1]

      categoryAverages.push({
        category,
        average: roundedAverage,
        color,
        band: bandIndex
      })
    }
  })

  return categoryAverages
}

const createCircularPlot = () => {
  if (!chartContainer.value) return

  // Use custom data if available, otherwise use default data
  const data = props.customData || parseCSVData(atlasScoreData)
  const categoryData = calculateCategoryAverages(data)

  // Clear previous chart
  chartContainer.value.innerHTML = ''

  // Set dimensions
  const width = 400
  const height = 400
  const outerRadius = props.radius || 150
  const innerRadius = props.innerRadius || 50

  // Create SVG
  const svg = d3
    .select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .attr(
      'style',
      'max-width: 100%; height: auto; font: 14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;'
    )

  const g = svg.append('g').attr('transform', `translate(${width / 2}, ${height / 2})`)

  type CategoryData = {
    category: string
    average: number
    color: string
    band: number
  }

  // Create pie generator
  const pie = d3
    .pie<CategoryData>()
    .value(() => 100) // Equal slices for all categories
    .sort(null)
    .startAngle(0) // Start at the top (12 o'clock position)
    .endAngle(2 * Math.PI) // Full circle

  // Create arc generator
  const arc = d3
    .arc<d3.PieArcDatum<CategoryData>>()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius)

  // Generate pie data
  const pieData = pie(categoryData)

  // Create the slices
  const slices = g.selectAll('.slice').data(pieData).enter().append('g').attr('class', 'slice')

  // Create tooltip
  const tooltip = d3
    .select('body')
    .append('div')
    .attr('class', 'circular-tooltip')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.8)')
    .style('color', 'white')
    .style('padding', '8px')
    .style('border-radius', '4px')
    .style('font-size', '12px')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 1000)

  // Add the arcs
  slices
    .append('path')
    .attr('d', arc)
    .attr('fill', (d) => d.data.color)
    .attr('stroke', 'white')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')
    .on('mouseover', function (event, d) {
      d3.select(this).transition().duration(200).attr('transform', 'scale(1.05)')

      const numBands = props.numBands || 4
      const bandSize = 100 / numBands
      const minRange = Math.round(d.data.band * bandSize)
      const maxRange = Math.round((d.data.band + 1) * bandSize)

      tooltip
        .style('opacity', 1)
        .html(
          `
          <strong>${d.data.category}</strong><br/>
          Average: ${d.data.average}<br/>
          Band: ${minRange}%-${maxRange}% (${d.data.band + 1}/${numBands})
        `
        )
        .style('left', event.pageX + 10 + 'px')
        .style('top', event.pageY - 10 + 'px')
    })
    .on('mouseout', function () {
      d3.select(this).transition().duration(200).attr('transform', 'scale(1)')
      tooltip.style('opacity', 0)
    })
    .each(function (d, i) {
      // Extract just the outer arc path for text positioning
      const firstArcSection = /(^.+?)L/
      const fullPath = d3.select(this).attr('d')

      if (fullPath) {
        // Grab everything up to the first Line statement
        let newArc = firstArcSection.exec(fullPath)?.[1] || ''
        // Replace commas with spaces for better compatibility
        newArc = newArc.replace(/,/g, ' ')

        // Calculate the middle angle of the slice to determine text direction
        const midAngle = (d.startAngle + d.endAngle) / 2
        // If the middle angle is in the bottom half (right side going down), flip the arc direction
        if (midAngle > Math.PI / 2 && midAngle < (3 * Math.PI) / 2) {
          const startLoc = /M(.*?)A/
          const middleLoc = /A(.*?)0 0 1/
          const endLoc = /0 0 1 (.*?)$/

          const startMatch = startLoc.exec(newArc)
          const middleMatch = middleLoc.exec(newArc)
          const endMatch = endLoc.exec(newArc)

          if (startMatch && middleMatch && endMatch) {
            const newStart = endMatch[1]
            const newEnd = startMatch[1]
            const middleSec = middleMatch[1]

            // Build up the new arc notation, set the sweep-flag to 0
            newArc = `M${newStart}A${middleSec}0 0 0 ${newEnd}`
          }
        }

        // Create invisible arc for text path
        g.append('path')
          .attr('class', 'hiddenArc')
          .attr('id', `textArc${i}`)
          .attr('d', newArc)
          .style('fill', 'none')
      }
    })

  // Add text labels that follow the arc paths
  g.selectAll('.arcText')
    .data(pieData)
    .enter()
    .append('text')
    .attr('class', 'arcText')
    // Move the labels below the arcs for those slices in the bottom half
    .attr('dy', (d) => {
      const midAngle = (d.startAngle + d.endAngle) / 2
      return midAngle > Math.PI / 2 && midAngle < (3 * Math.PI) / 2 ? 18 : -11
    })
    .style('font-weight', 'bold')
    .style('font-size', '12px')
    .style('fill', '#333')
    .append('textPath')
    .attr('startOffset', '50%')
    .style('text-anchor', 'middle')
    .attr('xlink:href', (_, i) => `#textArc${i}`)
    .text((d) => d.data.category.toLocaleUpperCase())

  // Add value labels inside the slices
  slices
    .append('text')
    .attr('transform', (d) => `translate(${arc.centroid(d)})`)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .style('font-weight', 'bold')
    .style('font-size', '16px')
    .style('fill', 'white')
    .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.5)')
    .text((d) => d.data.average)

  // Add center circle with overall info
  const overallAverage = Math.round(d3.mean(categoryData, (d) => d.average) || 0)

  // Create Red-Yellow-Green color scale for the center circle (0 = bad/red, 100 = good/green)
  const redYellowGreenColorScale = d3.scaleSequential(d3.interpolateRdYlGn).domain([0, 100])

  // Get color based on the overall average score
  const centerColor = redYellowGreenColorScale(overallAverage)

  g.append('circle')
    .attr('r', innerRadius)
    .attr('fill', centerColor)
    .attr('stroke', 'white')
    .attr('stroke-width', 2)

  // Add center text
  const centerGroup = g.append('g')

  const textColor = (d: number) => (d < 30 || d > 70 ? 'white' : 'black') // Dark text for low scores, light text for high scores
  centerGroup
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('y', -8)
    .style('font-weight', 'bold')
    .style('font-size', '14px')
    .style('fill', textColor(overallAverage))
    .text('IEQ')

  centerGroup
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('y', 12)
    .style('font-weight', 'bold')
    .style('font-size', '18px')
    .style('fill', textColor(overallAverage))
    .text(overallAverage)
}

// Watch for prop changes and recreate the plot
watch(
  () => [
    props.dataProperty,
    props.radius,
    props.innerRadius,
    props.customData,
    props.numBands,
    props.colorSchemesComposable?.categoryColorSchemes,
    props.colorSchemesComposable?.customColors
  ],
  () => {
    createCircularPlot()
  },
  { deep: true }
)

onMounted(() => {
  createCircularPlot()
})
</script>

<style scoped>
.circular-plot-container {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.controls {
  display: flex;
  justify-content: end;
  width: 100%;
  margin-bottom: 10px;
}

.download-btn {
  margin-top: 20px;
}

.chart-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.chart-container svg {
  display: block;
}
</style>
