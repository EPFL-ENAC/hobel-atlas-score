import * as d3 from 'd3'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import { formatWithUnicodeSubscripts } from './textFormatting'

export interface ChartDimensions {
  marginTop: number
  marginBottom: number
  marginLeft: number
  marginRight: number
  width: number
  height: number
  padding: number
}

export const createExpandedLineChart = (
  svg: any,
  fieldData: EnvironmentalData[],
  plotProperty: 'value' | 'score',
  x: any,
  yOffset: number,
  height: number,
  dimensions: ChartDimensions,
  field: string,
  fieldKey: string,
  onToggle: (fieldKey: string) => void
) => {
  const { marginLeft, marginRight, width } = dimensions
  const g = svg.append('g').attr('transform', `translate(${marginLeft},${yOffset})`)

  // Create vertical scale for line chart
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(fieldData, (d) => d[plotProperty]) as number])
    .nice()
    .range([height - 20, 20])

  // Create line generator
  const line = d3
    .line<EnvironmentalData>()
    .defined((d) => !isNaN(d[plotProperty]))
    .x((d) => x(d.time))
    .y((d) => y(d[plotProperty]))

  // Add background
  g.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', width - marginLeft - marginRight)
    .attr('height', height)
    .attr('fill', '#f8f9fa')
    .attr('stroke', '#dee2e6')
    .attr('stroke-width', 1)

  // Add grid lines
  const yAxis = d3.axisLeft(y).ticks(5)
  g.append('g')
    .call(yAxis.tickSize(-(width - marginLeft - marginRight)).tickFormat(() => ''))
    .attr('stroke-opacity', 0.1)

  // Add the line
  g.append('path')
    .datum(fieldData)
    .attr('fill', 'none')
    .attr('stroke', 'steelblue')
    .attr('stroke-width', 2)
    .attr('d', line)

  // Add dots
  g.selectAll('.dot')
    .data(fieldData.filter((d) => !isNaN(d[plotProperty]) && d[plotProperty] > 0))
    .enter()
    .append('circle')
    .attr('class', 'dot')
    .attr('cx', (d: EnvironmentalData) => x(d.time))
    .attr('cy', (d: EnvironmentalData) => y(d[plotProperty]))
    .attr('r', 3)
    .attr('fill', 'steelblue')

  // Add Y axis
  g.append('g').call(d3.axisLeft(y))

  // Add field label
  g.append('text')
    .attr('x', 10)
    .attr('y', 15)
    .attr('font-size', 14)
    .attr('font-weight', 'bold')
    .attr('fill', '#333')
    .text(formatWithUnicodeSubscripts(field) + ' (EXPANDED - Click to collapse)')

  // Add clickable area to collapse
  g.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', width - marginLeft - marginRight)
    .attr('height', height)
    .attr('fill', 'transparent')
    .style('cursor', 'pointer')
    .on('click', () => onToggle(fieldKey))
}
