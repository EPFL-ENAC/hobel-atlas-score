<template>
  <div class="file-upload-container">
    <!-- Contextual inputs for temperature-score logic -->
    <div class="context-form">
      <div class="context-row">
        <q-select
          v-model="buildingType"
          :options="buildingTypeOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          outlined
          dense
          hide-bottom-space
          label="Building type"
          :error="!!formErrors.buildingType"
          :error-message="formErrors.buildingType"
          class="context-select"
        >
          <template v-slot:append>
            <q-icon name="help_outline" size="xs">
              <q-tooltip>
                Determines the ATLAS threshold profile. School thresholds will be added once the
                separate school profile is available.
              </q-tooltip>
            </q-icon>
          </template>
        </q-select>

        <q-select
          v-model="coolingType"
          :options="coolingTypeOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          outlined
          dense
          hide-bottom-space
          label="Cooling/conditionning type"
          :error="!!formErrors.coolingType"
          :error-message="formErrors.coolingType"
          class="context-select"
        >
          <template v-slot:append>
            <q-icon name="help_outline" size="xs">
              <q-tooltip>
                The adaptive comfort model only applies when no mechanical cooling is operating.
              </q-tooltip>
            </q-icon>
          </template>
        </q-select>

        <q-select
          v-model="heatingSeason"
          :options="heatingSeasonOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          outlined
          dense
          hide-bottom-space
          label="Heating-season coverage"
          :error="!!formErrors.heatingSeason"
          :error-message="formErrors.heatingSeason"
          class="context-select"
        >
          <template v-slot:append>
            <q-icon name="help_outline" size="xs">
              <q-tooltip>
                Does the uploaded dataset cover the heating season, the non-heating season, or a mix
                of both?
              </q-tooltip>
            </q-icon>
          </template>
        </q-select>
      </div>

      <div v-if="heatingSeason === 'mixed'" class="season-dates row q-gutter-md q-mt-xs">
        <q-input
          v-model="heatingSeasonStart"
          outlined
          dense
          hide-bottom-space
          mask="##/##"
          label="Heating season start (MM/DD)"
          placeholder="MM/DD"
          :error="!!formErrors.heatingSeasonStart"
          :error-message="formErrors.heatingSeasonStart"
          class="date-input"
        />
        <q-input
          v-model="heatingSeasonEnd"
          outlined
          dense
          hide-bottom-space
          mask="##/##"
          label="Heating season end (MM/DD)"
          placeholder="MM/DD"
          :error="!!formErrors.heatingSeasonEnd"
          :error-message="formErrors.heatingSeasonEnd"
          class="date-input"
        />
      </div>
    </div>

    <!-- File Upload Header Line -->
    <div class="upload-header">
      <input
        ref="fileInput"
        type="file"
        accept=".csv,.xlsx"
        @change="handleFileChange"
        class="file-input"
      />

      <q-btn
        @click="triggerFileInput"
        flat
        icon="upload_file"
        label="Change file"
        class="upload-btn"
      />

      <q-btn @click="showFormatInfo = true" flat dense round icon="info" color="primary" size="md">
        <q-tooltip class="text-caption"> File format info </q-tooltip>
      </q-btn>

      <div v-if="isUsingCustomData" class="file-info">
        <span class="filename">{{ fileName }}</span>
      </div>

      <q-btn
        v-if="uploadedData && uploadedData.length > 0"
        @click="toggleDataPreview"
        flat
        dense
        :icon="isDataPreviewExpanded ? 'expand_less' : 'expand_more'"
        :label="isDataPreviewExpanded ? 'Hide' : 'Show'"
        class="preview-toggle-btn"
      />
    </div>

    <!-- CSV Explorer -->
    <CSVExplorer v-if="isDataPreviewExpanded" :data="uploadedData" />

    <!-- File Format Info Dialog -->
    <FileFormatInfoDialog v-model="showFormatInfo" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import type { BuildingType, CoolingType, HeatingSeason } from '../models'
import { parseCSVData } from '../utils/chartUtils'
import { baseUrl } from '../boot/api'
import CSVExplorer from './CSVExplorer.vue'
import FileFormatInfoDialog from './FileFormatInfoDialog.vue'
import atlasScoreData from '../assets/atlas_score_example.csv?raw'

// Emits
const emit = defineEmits<{
  dataChanged: [data: EnvironmentalData[] | null]
  fileStatusChanged: [isCustom: boolean, fileName: string]
  scoreNoteChanged: [note: string | null]
}>()

// Refs
const fileInput = ref<HTMLInputElement | null>(null)
const fileName = ref<string>('')
const isUsingCustomData = ref<boolean>(false)
const uploadedData = ref<EnvironmentalData[] | null>(null)
const isDataPreviewExpanded = ref<boolean>(false)
const showFormatInfo = ref<boolean>(false)

// Contextual inputs
const buildingType = ref<BuildingType | ''>('')
const coolingType = ref<CoolingType | ''>('')
const heatingSeason = ref<HeatingSeason | ''>('')
const heatingSeasonStart = ref<string>('')
const heatingSeasonEnd = ref<string>('')

const buildingTypeOptions = [
  { label: 'Residential', value: 'residential' },
  { label: 'School', value: 'school' }
]

const coolingTypeOptions = [
  { label: 'Natural / no mechanical cooling', value: 'natural' },
  { label: 'Mechanical cooling', value: 'mechanical' }
]

const heatingSeasonOptions = [
  { label: 'Heating', value: 'heating' },
  { label: 'Non-heating', value: 'non-heating' },
  { label: 'Mixed', value: 'mixed' }
]

const formErrors = reactive({
  buildingType: '',
  coolingType: '',
  heatingSeason: '',
  heatingSeasonStart: '',
  heatingSeasonEnd: ''
})

// Load default data on mount
onMounted(() => {
  uploadedData.value = parseCSVData(atlasScoreData)
  emit('scoreNoteChanged', null)
})

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const isValidMonthDay = (value: string): boolean => {
  if (!/^\d{2}\/\d{2}$/.test(value)) return false
  const [monthStr, dayStr] = value.split('/')
  const month = Number(monthStr)
  const day = Number(dayStr)
  if (Number.isNaN(month) || Number.isNaN(day)) return false
  if (month < 1 || month > 12 || day < 1 || day > 31) return false
  const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  return day <= (daysInMonth[month - 1] ?? 0)
}

const validateForm = (): boolean => {
  formErrors.buildingType = buildingType.value ? '' : 'Building type is required.'
  formErrors.coolingType = coolingType.value ? '' : 'Cooling/conditionning type is required.'
  formErrors.heatingSeason = heatingSeason.value ? '' : 'Heating-season coverage is required.'

  formErrors.heatingSeasonStart = ''
  formErrors.heatingSeasonEnd = ''

  if (heatingSeason.value === 'mixed') {
    formErrors.heatingSeasonStart = isValidMonthDay(heatingSeasonStart.value)
      ? ''
      : 'Enter a valid month/day (MM/DD).'
    formErrors.heatingSeasonEnd = isValidMonthDay(heatingSeasonEnd.value)
      ? ''
      : 'Enter a valid month/day (MM/DD).'
  }

  return (
    !formErrors.buildingType &&
    !formErrors.coolingType &&
    !formErrors.heatingSeason &&
    !formErrors.heatingSeasonStart &&
    !formErrors.heatingSeasonEnd
  )
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  if (!validateForm()) {
    alert('Please fill in all required contextual information before uploading a file.')
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file)

    const params = new URLSearchParams()
    params.append('building_type', buildingType.value)
    params.append('cooling_type', coolingType.value)
    params.append('heating_season', heatingSeason.value)
    if (heatingSeason.value === 'mixed') {
      params.append('heating_season_start', heatingSeasonStart.value)
      params.append('heating_season_end', heatingSeasonEnd.value)
    }

    const response = await fetch(`${baseUrl}/data/score?${params.toString()}`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || `Server error: ${response.status}`)
    }

    const fallbackNote = response.headers.get('X-ATLAS-Fallback-Note')
    emit('scoreNoteChanged', fallbackNote)

    const csvText = await response.text()
    const parsedData = parseCSVData(csvText)

    if (parsedData.length === 0) {
      alert('No valid data found in the response. Please check the format.')
      return
    }

    fileName.value = file.name
    isUsingCustomData.value = true
    uploadedData.value = parsedData

    emit('dataChanged', parsedData)
    emit('fileStatusChanged', true, file.name)
  } catch (error) {
    console.error('Error processing file:', error)
    alert(`Error processing file: ${error instanceof Error ? error.message : 'Unknown error'}`)
    emit('scoreNoteChanged', null)
  } finally {
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const toggleDataPreview = () => {
  isDataPreviewExpanded.value = !isDataPreviewExpanded.value
}
</script>

<style scoped>
.file-upload-container {
  margin-bottom: 20px;
}

.context-form {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: rgba(128, 128, 128, 0.05);
}

.context-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;
}

.context-select {
  flex: 1 1 220px;
  min-width: 220px;
}

.season-dates {
  align-items: flex-start;
}

.date-input {
  flex: 1 1 180px;
  max-width: 220px;
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.file-input {
  display: none;
}

.upload-btn {
  color: #666;
  border: 1px solid #ddd;
}

.upload-btn:hover {
  border-color: #999;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.filename {
  font-size: 0.9em;
  color: #495057;
  font-weight: 500;
}

.preview-toggle-btn {
  margin-left: auto;
  color: #666;
}

@media (max-width: 768px) {
  .upload-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-toggle-btn {
    margin-left: 0;
    align-self: flex-end;
  }
}
</style>
