<template>
  <div v-if="data && data.length > 0" class="csv-explorer">
    <div class="explorer-content">
      <!-- Search bar -->
      <div class="search-bar">
        <q-input
          v-model="searchText"
          outlined
          dense
          placeholder="Search in data..."
          clearable
          class="search-input"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>

      <!-- Quasar Table with Virtual Scroll and Sticky Headers -->
      <q-table
        :rows="filteredData"
        :columns="columns"
        row-key="id"
        :filter="searchText"
        flat
        bordered
        class="data-table my-sticky-dynamic"
        :virtual-scroll="true"
        :virtual-scroll-item-size="48"
        :virtual-scroll-sticky-size-start="48"
        :rows-per-page-options="[0]"
        :pagination="{ rowsPerPage: 0 }"
      >
        <template v-slot:body-cell-time="props">
          <q-td :props="props">
            {{ formatDate(props.row.time) }}
          </q-td>
        </template>

        <template v-slot:body-cell-value="props">
          <q-td :props="props">
            {{ formatNumber(props.row.value) }}
          </q-td>
        </template>

        <template v-slot:body-cell-score="props">
          <q-td :props="props">
            {{ formatNumber(props.row.score) }}
          </q-td>
        </template>
      </q-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { EnvironmentalData } from '../composables/useHorizonChart'
import type { QTableColumn } from 'quasar'

// Props
const props = defineProps<{
  data: EnvironmentalData[] | null
}>()

// State
const searchText = ref('')
const sortColumn = ref<keyof EnvironmentalData>('id')
const sortDirection = ref<'asc' | 'desc'>('asc')

// Column configuration
const columns: QTableColumn[] = [
  {
    name: 'id',
    label: 'ID',
    field: 'id',
    align: 'left',
    sortable: true
  },
  {
    name: 'time',
    label: 'Time',
    field: 'time',
    align: 'left',
    sortable: true
  },
  {
    name: 'category',
    label: 'Category',
    field: 'category',
    align: 'left',
    sortable: true
  },
  {
    name: 'field',
    label: 'Field',
    field: 'field',
    align: 'left',
    sortable: true
  },
  {
    name: 'value',
    label: 'Value',
    field: 'value',
    align: 'right',
    sortable: true
  },
  {
    name: 'score',
    label: 'Score',
    field: 'score',
    align: 'right',
    sortable: true
  }
]

const formatDate = (date: Date): string => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatNumber = (num: number): string => {
  return num.toFixed(2)
}

// Computed properties
const filteredData = computed(() => {
  if (!props.data) return []

  let result = [...props.data]

  // Apply search filter
  if (searchText.value && searchText.value.trim()) {
    const search = searchText.value.toLowerCase()
    result = result.filter((row) => {
      return (
        row.id.toString().includes(search) ||
        row.category.toLowerCase().includes(search) ||
        row.field.toLowerCase().includes(search) ||
        row.value.toString().includes(search) ||
        row.score.toString().includes(search) ||
        formatDate(row.time).toLowerCase().includes(search)
      )
    })
  }

  // Apply sorting
  result.sort((a, b) => {
    const aVal = a[sortColumn.value]
    const bVal = b[sortColumn.value]

    let comparison = 0
    if (aVal < bVal) comparison = -1
    if (aVal > bVal) comparison = 1

    return sortDirection.value === 'asc' ? comparison : -comparison
  })

  return result
})

// Watch for data changes and reset search
watch(
  () => props.data,
  () => {
    searchText.value = ''
  }
)
</script>

<style scoped>
.csv-explorer {
  margin: 20px 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.explorer-content {
  padding: 16px;
}

.search-bar {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
}

@media (max-width: 768px) {
  .explorer-content {
    padding: 12px;
  }
}

/* Sticky header styles for the Quasar table */
.my-sticky-dynamic {
  /* height is important */
  height: 400px;
}

.my-sticky-dynamic .q-table__top,
.my-sticky-dynamic .q-table__bottom,
.my-sticky-dynamic thead tr:first-child th {
  /* bg color is important for th; just specify one */
  background-color: #ffffff;
  backdrop-filter: blur(2px);
}

.my-sticky-dynamic thead tr th {
  position: sticky;
  z-index: 1;
}

.my-sticky-dynamic thead tr:first-child th {
  top: 0;
  position: sticky;
  z-index: 10;
}
/* Alternative approach for sticky headers */
.data-table :deep(.q-table thead th) {
  position: sticky !important;
  top: 0;
  background: white !important;
  z-index: 10;
}

/* prevent scrolling behind sticky top row on focus */
.my-sticky-dynamic tbody {
  scroll-margin-top: 48px;
}
</style>
