<template>
  <q-dialog v-model="showDialog" persistent>
    <q-card style="min-width: 520px; max-width: 600px">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Input File Format</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-md">
        <p class="text-body1">
          Upload a <strong>CSV</strong> or <strong>XLSX</strong> (Excel) file with the columns
          described below.
        </p>

        <!-- Required Columns Table -->
        <q-table
          :rows="columns"
          :columns="tableColumns"
          row-key="name"
          flat
          bordered
          :pagination="{ rowsPerPage: 0 }"
          :rows-per-page-options="[0]"
          class="format-table"
        />

        <!-- Score note -->
        <div class="q-mt-lg">
          <q-banner inline-actions rounded class="bg-grey-2 text-grey-9">
            <template v-slot:avatar>
              <q-icon name="info" color="secondary" />
            </template>
            If the <code>score</code> and <code>category</code> columns are omitted, they will be
            computed automatically by the backend.
          </q-banner>
        </div>

        <!-- Context note -->
        <div class="q-mt-md">
          <q-banner inline-actions rounded class="bg-blue-1 text-grey-9">
            <template v-slot:avatar>
              <q-icon name="settings" color="primary" />
            </template>
            For temperature scoring, fill in the building type, cooling/conditionning type, and
            heating-season coverage. If outdoor temperature data are supplied (e.g.
            <code>outdoor temperature</code>), the backend will use the adaptive comfort method when
            applicable; otherwise it falls back to fixed mechanical-cooling criteria.
          </q-banner>
        </div>

        <!-- Download examples buttons -->
        <div class="q-mt-lg row q-gutter-sm">
          <q-btn
            outlined
            unelevated
            no-caps
            color="secondary"
            label="Download example (with scores)"
            type="a"
            :href="exampleWithScoresUrl"
            download="atlas_score_example.csv"
            class="col"
          />
          <q-btn
            outlined
            unelevated
            no-caps
            color="secondary"
            label="Download example (without scores)"
            type="a"
            :href="exampleWithoutScoresUrl"
            download="atlas_raw_example.csv"
            class="col"
          />
        </div>

        <!-- Categories -->
        <div class="q-mt-lg">
          <div class="text-subtitle2 q-mb-sm">
            <q-icon name="category" size="sm" class="q-mr-xs" />
            Possible categories
          </div>
          <q-chip
            v-for="cat in categories"
            :key="cat"
            color="secondary"
            text-color="white"
            class="q-ma-xs"
          >
            {{ cat }}
          </q-chip>
        </div>

        <!-- Fields -->
        <div class="q-mt-lg">
          <div class="text-subtitle2 q-mb-sm">
            <q-icon name="track_changes" size="sm" class="q-mr-xs" />
            Possible fields patterns (and variants)
          </div>
          <div v-for="fieldInfo in fields" :key="fieldInfo.key" class="field-item">
            <div class="field-header row items-center">
              <q-chip size="md" color="grey-7" text-color="white" class="q-mr-sm">
                {{ fieldInfo.key }}
              </q-chip>
              <span class="text-caption">{{ fieldInfo.category }}</span>
            </div>
            <div class="field-patterns">
              <q-chip
                v-for="pattern in fieldInfo.patterns"
                :key="pattern"
                size="sm"
                color="grey-3"
                text-color="grey-8"
                class="q-ma-xs"
              >
                {{ pattern }}
              </q-chip>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const showDialog = defineModel<boolean>({ default: false })

const exampleWithScoresUrl = new URL('../assets/atlas_score_example.csv', import.meta.url).href
const exampleWithoutScoresUrl = new URL('../assets/atlas_raw_example.csv', import.meta.url).href

const columns = [
  {
    name: 'time',
    type: 'datetime',
    required: 'yes',
    description: 'Timestamp of the measurement (ISO 8601 format)'
  },
  {
    name: 'category',
    type: 'string',
    required: 'no',
    description: 'One of the 4 possible categories'
  },
  {
    name: 'field',
    type: 'string',
    required: 'yes',
    description: 'Field name containing one of the recognized patterns'
  },
  { name: 'value', type: 'number', required: 'yes', description: 'The raw measurement value' },
  { name: 'score', type: 'number', required: 'no', description: 'Score between 0 and 100' }
] as const

const tableColumns = [
  { name: 'name', label: 'Column', field: 'name', align: 'left' as const },
  { name: 'type', label: 'Type', field: 'type', align: 'left' as const },
  { name: 'required', label: 'Required', field: 'required', align: 'center' as const },
  { name: 'description', label: 'Description', field: 'description', align: 'left' as const }
]

const categories = ['Acoustics', 'Air quality', 'Lighting', 'Thermal comfort']

const fields = computed(() => [
  {
    key: 'co2',
    category: 'Air quality',
    patterns: ['co2', 'co_2', 'co_{2}', 'carbon dioxide', 'carbon dioxyde']
  },
  {
    key: 'pm25',
    category: 'Air quality',
    patterns: ['pm2.5', 'pm_{2.5}', 'pm_2.5', 'pm25', 'fine particulate matter']
  },
  {
    key: 'pm10',
    category: 'Air quality',
    patterns: ['pm10', 'pm_{10}', 'pm_10', 'coarse particulate matter']
  },
  {
    key: 'o3',
    category: 'Air quality',
    patterns: ['o3', 'o_3', 'o_{3}', 'ozone']
  },
  {
    key: 'ch2o',
    category: 'Air quality',
    patterns: ['ch2o', 'ch_{2}o', 'ch_2o', 'formaldehyde']
  },
  {
    key: 'humidity',
    category: 'Air quality',
    patterns: ['humidity', 'relative humidity', 'r.h.', 'r. h.', 'rh']
  },
  {
    key: 'no2',
    category: 'Air quality',
    patterns: ['no2', 'no_2', 'no_{2}', 'nitrogen dioxide']
  },
  {
    key: 'so2',
    category: 'Air quality',
    patterns: ['so2', 'so_2', 'so_{2}', 'sulfur dioxide']
  },
  {
    key: 'co',
    category: 'Air quality',
    patterns: ['co', 'carbon monoxide']
  },
  {
    key: 'temperature',
    category: 'Thermal comfort',
    patterns: ['temperature', 'temp']
  },
  {
    key: 'light_percent',
    category: 'Lighting',
    patterns: ['light percent', 'illuminance', 'light', 'lux', 'lighting']
  },
  {
    key: 'sla',
    category: 'Acoustics',
    patterns: ['sla', 'sound pressure', 'sound', 'db(a)', 'noise', 'acoustic']
  }
])
</script>

<style scoped>
.format-table {
  width: 100%;
}

.field-item {
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.field-item:last-child {
  border-bottom: none;
}

.field-header {
  margin-bottom: 4px;
}

.field-patterns {
  padding-left: 20px;
}
</style>
