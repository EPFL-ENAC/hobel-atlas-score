<script setup lang="ts">
import { ref } from 'vue'
import HorizonPlot from './components/visualizations/HorizonPlot.vue'
import CircularCategoryPlot from './components/visualizations/CircularCategoryPlot.vue'
import FileUpload from './components/FileUpload.vue'
import ColorSchemePreview from './components/ColorSchemePreview.vue'
import type { EnvironmentalData } from './composables/useHorizonChart'
import { useColorSchemes, availableSchemes } from './composables/useColorSchemes'

// Reactive variables for controlling the plots
const bandHeight = ref<number>(60)
const numBands = ref<number>(3)
const circularPlotBands = ref<number>(4)
const dataProperty = ref<'value' | 'score'>('score')

// Data management
const csvData = ref<EnvironmentalData[] | null>(null)

// Color scheme management
const colorSchemesComposable = useColorSchemes()
const { categoryColorSchemes, customColors, updateCategoryColorScheme, updateCustomColor } =
  colorSchemesComposable

// Helper function to get scheme info by value
const getSchemeInfo = (value: string) => {
  return (
    availableSchemes.find((s) => s.value === value) || {
      label: 'Blues',
      value: 'schemeBlues',
      schemeName: 'schemeBlues'
    }
  )
}

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

const updateCircularPlotBands = (value: number | null) => {
  if (value !== null) {
    circularPlotBands.value = value
  }
}

const updateDataProperty = (value: 'value' | 'score') => {
  dataProperty.value = value
}

// File upload handlers
const handleDataChanged = (data: EnvironmentalData[] | null) => {
  csvData.value = data
}

const handleFileStatusChanged = (_isCustom: boolean, _fileName: string) => {
  // We can use these values if needed for additional UI feedback
}
</script>

<template>
  <div class="app-container">
    <h3>Atlas Score Visualization</h3>

    <!-- File Upload Section -->
    <FileUpload @data-changed="handleDataChanged" @file-status-changed="handleFileStatusChanged" />

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
          <label>Horizon Bands: {{ numBands }}</label>
          <q-slider
            :model-value="numBands"
            :min="2"
            :max="6"
            :step="1"
            class="slider"
            @update:model-value="updateNumBands"
          />
        </div>

        <div class="control-item">
          <label>Circular Bands: {{ circularPlotBands }}</label>
          <q-slider
            :model-value="circularPlotBands"
            :min="2"
            :max="10"
            :step="1"
            class="slider"
            @update:model-value="updateCircularPlotBands"
          />
        </div>
      </div>

      <!-- Color Scheme Controls -->
      <div class="color-controls">
        <h6>Color Schemes</h6>
        <div class="color-scheme-grid">
          <div
            class="category-color-control"
            v-for="category in [
              'Air quality',
              'Thermal comfort',
              'Lighting',
              'Acoustics',
              'Overall IEQ'
            ] as const"
            :key="category"
          >
            <label>{{ category }}:</label>
            <q-select
              :model-value="categoryColorSchemes[category]"
              :options="availableSchemes"
              option-label="label"
              option-value="value"
              emit-value
              map-options
              outlined
              dense
              class="color-select"
              @update:model-value="(value) => updateCategoryColorScheme(category, value)"
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps" class="scheme-option">
                  <q-item-section>
                    <ColorSchemePreview
                      :scheme-name="scope.opt.schemeName"
                      :label="scope.opt.label"
                      :custom-color="
                        scope.opt.schemeName === 'custom' ? customColors[category] : undefined
                      "
                    />
                  </q-item-section>
                </q-item>
              </template>

              <template v-slot:selected-item>
                <ColorSchemePreview
                  :scheme-name="getSchemeInfo(categoryColorSchemes[category]).schemeName"
                  :label="getSchemeInfo(categoryColorSchemes[category]).label"
                  :custom-color="
                    categoryColorSchemes[category] === 'custom' ? customColors[category] : undefined
                  "
                />
              </template>
            </q-select>

            <!-- Custom color picker - only show when custom is selected -->
            <div v-if="categoryColorSchemes[category] === 'custom'" class="custom-color-picker">
              <label class="custom-color-label">Custom Color:</label>
              <input
                type="color"
                :value="customColors[category]"
                @input="
                  (event) => updateCustomColor(category, (event.target as HTMLInputElement).value)
                "
                class="color-input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Visualization Components -->
    <div class="visualization-section">
      <h5>Horizon Plot</h5>
      <HorizonPlot
        :band-height="bandHeight"
        :num-bands="numBands"
        :data-property="dataProperty"
        :custom-data="csvData"
        :color-schemes-composable="colorSchemesComposable"
      />
    </div>

    <div class="visualization-section">
      <h5>Category Overview</h5>
      <CircularCategoryPlot
        :data-property="dataProperty"
        :custom-data="csvData"
        :color-schemes-composable="colorSchemesComposable"
        :num-bands="circularPlotBands"
      />
    </div>
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

.color-controls {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.color-controls h6 {
  margin: 0 0 15px 0;
  font-weight: bold;
  color: #333;
}

.color-scheme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.category-color-control {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.category-color-control label {
  font-weight: 500;
  font-size: 0.9em;
  color: #555;
}

.custom-color-picker {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.custom-color-label {
  font-size: 0.8em;
  color: #666;
  margin: 0;
}

.color-input {
  width: 40px;
  height: 30px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  background: none;
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: none;
  border-radius: 3px;
}

.color-select {
  width: 100%;
  min-height: 40px;
}

.color-select :deep(.q-field__native) {
  padding-top: 8px;
  padding-bottom: 8px;
}

.scheme-option {
  padding: 4px 8px !important;
  min-height: 44px;
}

.scheme-option:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.scheme-option .q-item__section {
  padding: 0;
}

.visualization-section {
  margin-bottom: 40px;
  padding: 20px 0;
}

.visualization-section h4 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
  font-size: 1.2em;
}

@media (max-width: 768px) {
  .control-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
