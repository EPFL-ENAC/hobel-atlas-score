<template>
  <div class="file-upload-container">
    <!-- File Upload Header Line -->
    <div class="upload-header">
      <input
        ref="fileInput"
        type="file"
        accept=".csv"
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import { parseCSVData } from '../utils/chartUtils'
import CSVExplorer from './CSVExplorer.vue'
import atlasScoreData from '../assets/atlas_score_example.csv?raw'

// Emits
const emit = defineEmits<{
  dataChanged: [data: EnvironmentalData[] | null]
  fileStatusChanged: [isCustom: boolean, fileName: string]
}>()

// Refs
const fileInput = ref<HTMLInputElement | null>(null)
const fileName = ref<string>('')
const isUsingCustomData = ref<boolean>(false)
const uploadedData = ref<EnvironmentalData[] | null>(null)
const isDataPreviewExpanded = ref<boolean>(false)

// Load default data on mount
onMounted(() => {
  uploadedData.value = parseCSVData(atlasScoreData)
})

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  try {
    const text = await file.text()
    const parsedData = parseCSVData(text)

    if (parsedData.length === 0) {
      alert('No valid data found in the CSV file. Please check the format.')
      return
    }

    fileName.value = file.name
    isUsingCustomData.value = true
    uploadedData.value = parsedData

    emit('dataChanged', parsedData)
    emit('fileStatusChanged', true, file.name)
  } catch (error) {
    console.error('Error parsing CSV file:', error)
    alert('Error parsing CSV file. Please check the format.')
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
