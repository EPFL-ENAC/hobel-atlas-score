<template>
  <div class="app-container">
    <h3>Atlas Score Visualization</h3>

    <!-- File Upload Section -->
    <FileUpload
      @data-changed="handleDataChanged"
      @file-status-changed="handleFileStatusChanged"
      @score-note-changed="handleScoreNoteChanged"
    />

    <q-banner v-if="scoreNote" rounded class="bg-warning text-dark q-mb-md">
      <template v-slot:avatar>
        <q-icon name="warning" color="dark" />
      </template>
      {{ scoreNote }}
    </q-banner>

    <div class="controls">
      <div class="control-group">
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

    <!-- Credits / Acknowledgements Section -->
    <div class="credits-section">
      <p class="text-caption text-grey-8">
        This work was led by four researchers: Dr Reza Daneshazarian, Dr Bowen Du, Dr Sarah Crosby,
        and Dr Cairan Van Rooyen.
      </p>
      <p class="text-caption text-grey-8">
        The research was supported by the INPERSO Project (Industrialised and Personalised
        Renovation for Sustainable Societies), funded by the European Union's Horizon Europe
        programme. The related paper, "ATLAS: A Performance-Based Index for Integrated Evaluation
        and Benchmarking of Indoor Environmental Quality," is available in Building and Environment:
        <a
          href="https://doi.org/10.1016/j.buildenv.2026.114985"
          target="_blank"
          rel="noopener noreferrer"
          >https://doi.org/10.1016/j.buildenv.2026.114985</a
        >
      </p>
      <p class="text-caption text-grey-8">
        Developers:
        <a href="https://enacit4r.epfl.ch" target="_blank" rel="noopener noreferrer"
          >ENAC-IT4R team</a
        >. Submit feedback and issues to
        <a
          href="https://github.com/EPFL-ENAC/hobel-atlas-score/issues"
          target="_blank"
          rel="noopener noreferrer"
          >https://github.com/EPFL-ENAC/hobel-atlas-score/issues</a
        >.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HorizonPlot from 'components/visualizations/HorizonPlot.vue'
import CircularCategoryPlot from 'components/visualizations/CircularCategoryPlot.vue'
import FileUpload from 'components/FileUpload.vue'
import ColorSchemePreview from 'components/ColorSchemePreview.vue'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import { useColorSchemes, availableSchemes } from '../composables/useColorSchemes'

// Reactive variables for controlling the plots
const bandHeight = ref<number>(60)
const numBands = ref<number>(3)
const circularPlotBands = ref<number>(4)
const dataProperty = ref<'value' | 'score'>('score')

// Data management
const csvData = ref<EnvironmentalData[] | null>(null)
const scoreNote = ref<string | null>(null)

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

// File upload handlers
const handleDataChanged = (data: EnvironmentalData[] | null) => {
  csvData.value = data
}

const handleFileStatusChanged = (_isCustom: boolean, _fileName: string) => {
  void _isCustom
  void _fileName
}

const handleScoreNoteChanged = (note: string | null) => {
  scoreNote.value = note
}
</script>

<style scoped>
.app-container {
  margin: 0 auto;
  max-width: 1500px;
  text-align: center;
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
  border-top: 1px solid rgba(128, 128, 128, 0.3);
}

.color-controls h6 {
  margin: 0 0 15px 0;
  font-weight: bold;
  color: currentColor;
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
  color: currentColor;
}

.custom-color-picker {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  padding: 8px;
  background-color: rgba(128, 128, 128, 0.15);
  border-radius: 4px;
  border: 1px solid currentColor;
}

.custom-color-label {
  font-size: 0.8em;
  color: currentColor;
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
  background-color: rgba(var(--q-primary-rgb), 0.12);
}

.scheme-option .q-item__section {
  padding: 0;
}

.visualization-section {
  margin-bottom: 40px;
  padding: 20px 0;
}

.credits-section {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid rgba(128, 128, 128, 0.3);
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  text-align: left;
}

.credits-section h6 {
  font-weight: bold;
  color: currentColor;
  margin: 0 0 15px 0;
  text-align: center;
}

.credits-section p {
  margin-bottom: 8px;
  line-height: 1.5;
}

.credits-section a {
  color: var(--q-primary, #1976d2);
  word-break: break-all;
}

.visualization-section h4 {
  text-align: center;
  margin-bottom: 20px;
  color: currentColor;
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
