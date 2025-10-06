<script setup lang="ts">
import { ref } from 'vue'
import HorizonPlot from './components/visualizations/HorizonPlot.vue'

// Reactive variables for controlling the horizon plot
const bandHeight = ref<number>(60)
const numBands = ref<number>(3)
const dataProperty = ref<'value' | 'score'>('score')

// Functions to update the plot parameters
const updateBandHeight = (value: number | null) => {
  if (value !== null) {
    bandHeight.value = value
  }
}

const updateNumBands = (value: number | null) => {
  if (value !== null) {
    numBands.value = value
  }
}

const updateDataProperty = (value: 'value' | 'score') => {
  dataProperty.value = value
}
</script>

<template>
  <div class="app-container">
    <h3>Atlas Score Visualization</h3>
    <div class="controls">
      <div class="control-group">
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

        <div class="control-item">
          <label>Height: {{ bandHeight }}</label>
          <q-slider
            :model-value="bandHeight"
            :min="20"
            :max="200"
            :step="5"
            class="slider"
            @update:model-value="updateBandHeight"
          />
        </div>

        <div class="control-item">
          <label>Bands: {{ numBands }}</label>
          <q-slider
            :model-value="numBands"
            :min="2"
            :max="6"
            :step="1"
            class="slider"
            @update:model-value="updateNumBands"
          />
        </div>
      </div>
    </div>
    <HorizonPlot :band-height="bandHeight" :num-bands="numBands" :data-property="dataProperty" />
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  margin-bottom: 20px;
  padding: 10px 15px;
  border-radius: 4px;
}

.control-group {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-between;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-item label {
  font-weight: bold;
  margin-bottom: 0;
}

.control-item .slider {
  width: 200px;
}

@media (max-width: 768px) {
  .control-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
