<template>
  <div class="file-upload-container">
    <div class="upload-controls">
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
        :label="isUsingCustomData ? 'Change file' : 'Upload CSV'"
        class="upload-btn"
      />

      <div v-if="isUsingCustomData" class="file-info">
        <span class="filename">{{ fileName }}</span>
        <q-btn
          @click="resetFile"
          flat
          dense
          round
          icon="close"
          size="sm"
          class="reset-btn"
          title="Use default data"
        />
      </div>
    </div>

    <!-- CSV Explorer -->
    <CSVExplorer v-if="isUsingCustomData" :data="uploadedData" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import { parseCSVData } from '../utils/chartUtils'
import CSVExplorer from './CSVExplorer.vue'

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

const resetFile = () => {
  fileName.value = ''
  isUsingCustomData.value = false
  uploadedData.value = null

  if (fileInput.value) {
    fileInput.value.value = ''
  }

  emit('dataChanged', null)
  emit('fileStatusChanged', false, '')
}
</script>

<style scoped>
.file-upload-container {
  margin-bottom: 20px;
  justify-items: center;
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
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

.reset-btn {
  color: #6c757d;
}

.reset-btn:hover {
  color: #495057;
}

@media (max-width: 768px) {
  .upload-controls {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
