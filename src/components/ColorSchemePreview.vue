<template>
  <div class="color-scheme-preview">
    <div class="color-bar">
      <div
        v-for="(color, index) in colors"
        :key="index"
        class="color-segment"
        :style="{ backgroundColor: color }"
      ></div>
    </div>
    <span class="scheme-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{
  schemeName: string
  label: string
}>()

// Get the colors for this scheme
const colors = computed(() => {
  const count = 6 // Generate 6 colors for preview

  try {
    // First try discrete scheme if not an interpolation scheme
    if (!props.schemeName.startsWith('interpolate')) {
      const scheme = (d3 as any)[props.schemeName]
      if (scheme && scheme[count]) {
        return scheme[count]
      }
    }

    // Try interpolation function (either direct or converted name)
    const interpolateName = props.schemeName.startsWith('interpolate')
      ? props.schemeName
      : `interpolate${props.schemeName.replace('scheme', '')}`

    const interpolator = (d3 as any)[interpolateName]
    if (typeof interpolator === 'function') {
      const colors: string[] = []
      for (let i = 0; i < count; i++) {
        const t = i / (count - 1) // Map index to [0, 1] range
        // Use d3.rgb().hex() for consistent color format (inspired by Observable ramp function)
        colors.push(d3.rgb(interpolator(t)).hex())
      }
      return colors
    }

    // Fallback: try discrete scheme with different sizes
    const scheme = (d3 as any)[props.schemeName]
    if (scheme) {
      for (const size of [6, 5, 4, 3]) {
        if (scheme[size] && Array.isArray(scheme[size])) {
          return scheme[size]
        }
      }
    }
  } catch (error) {
    console.warn(`Failed to load color scheme: ${props.schemeName}`, error)
  }

  // Default fallback colors (blue scheme)
  return ['#f7fbff', '#c6dbef', '#6baed6', '#3182bd', '#08519c', '#08306b']
})
</script>

<style scoped>
.color-scheme-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 4px;
  width: 100%;
}

.color-scheme-preview:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.color-bar {
  display: flex;
  width: 70px;
  height: 18px;
  border-radius: 3px;
  overflow: hidden;
}

.color-segment {
  flex: 1;
  height: 100%;
  border: none;
}

.scheme-label {
  font-size: 0.9em;
  color: #424242;
  font-weight: 500;
  white-space: nowrap;
  flex: 1;
}
</style>
