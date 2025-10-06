import * as d3 from 'd3'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import type { ChartDimensions } from './expandedChart'

export const createHorizonBand = (
  svg: any,
  fieldData: EnvironmentalData[],
  plotProperty: 'value' | 'score',
  x: any,
  yOffset: number,
  size: number,
  dimensions: ChartDimensions,
  colors: string[],
  bands: number,
  field: string,
  fieldKey: string,
  globalIndex: number,
  onToggle: (fieldKey: string) => void
) => {
  const { marginLeft, marginRight, width, padding } = dimensions

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
  const bandGroup = g.append('g').attr('clip-path', `url(#${uid}-clip-${globalIndex})`)

  bandGroup
    .selectAll('use')
    .data(new Array(bands).fill(globalIndex))
    .enter()
    .append('use')
    .attr('xlink:href', `#${uid}-path-${globalIndex}`)
    .attr('fill', (_: any, j: number) => colors[j] ?? '#ccc')
    .attr('transform', (_: any, j: number) => `translate(0,${j * size})`)

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

  // Add a transparent rectangle that covers the entire band area to make it clickable
  g.append('rect')
    .attr('x', 0)
    .attr('y', padding)
    .attr('width', width - marginLeft - marginRight)
    .attr('height', size - padding)
    .attr('fill', 'transparent')
    .style('cursor', 'pointer')
    .on('click', () => onToggle(fieldKey))
}
