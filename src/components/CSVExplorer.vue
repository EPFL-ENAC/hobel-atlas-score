<template>
  <div v-if="data && data.length > 0" class="csv-explorer">
    <div class="explorer-header">
      <h5>Data Preview ({{ filteredData.length }} rows)</h5>
      <q-btn
        @click="toggleExpanded"
        flat
        dense
        :icon="isExpanded ? 'expand_less' : 'expand_more'"
        :label="isExpanded ? 'Hide' : 'Show'"
        class="toggle-btn"
      />
    </div>

    <div v-if="isExpanded" class="explorer-content">
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

      <!-- Table -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th
                v-for="column in columns"
                :key="column.name"
                @click="sortBy(column.name)"
                class="sortable-header"
              >
                <div class="header-content">
                  <span>{{ column.label }}</span>
                  <q-icon
                    v-if="sortColumn === column.name"
                    :name="sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward'"
                    size="xs"
                  />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in paginatedData" :key="index">
              <td>{{ row.id }}</td>
              <td>{{ formatDate(row.time) }}</td>
              <td>{{ row.category }}</td>
              <td>{{ row.field }}</td>
              <td>{{ formatNumber(row.value) }}</td>
              <td>{{ formatNumber(row.score) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination controls -->
      <div class="pagination-controls">
        <div class="rows-per-page">
          <span>Rows per page:</span>
          <q-select
            v-model="rowsPerPage"
            :options="[10, 25, 50, 100]"
            dense
            outlined
            class="rows-select"
          />
        </div>
        <div class="pagination-info">
          {{ paginationInfo }}
        </div>
        <div class="pagination-buttons">
          <q-btn
            @click="previousPage"
            flat
            dense
            round
            icon="chevron_left"
            :disable="currentPage === 1"
          />
          <span class="page-number">{{ currentPage }} / {{ totalPages }}</span>
          <q-btn
            @click="nextPage"
            flat
            dense
            round
            icon="chevron_right"
            :disable="currentPage === totalPages"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { EnvironmentalData } from '../composables/useHorizonChart'

// Props
const props = defineProps<{
  data: EnvironmentalData[] | null
}>()

// State
const isExpanded = ref(false)
const searchText = ref('')
const sortColumn = ref<keyof EnvironmentalData>('id')
const sortDirection = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)
const rowsPerPage = ref(10)

// Column configuration
const columns = [
  { name: 'id' as const, label: 'ID' },
  { name: 'time' as const, label: 'Time' },
  { name: 'category' as const, label: 'Category' },
  { name: 'field' as const, label: 'Field' },
  { name: 'value' as const, label: 'Value' },
  { name: 'score' as const, label: 'Score' }
]

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const sortBy = (column: keyof EnvironmentalData) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  currentPage.value = 1
}

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

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
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

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / rowsPerPage.value)
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  const end = start + rowsPerPage.value
  return filteredData.value.slice(start, end)
})

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value + 1
  const end = Math.min(currentPage.value * rowsPerPage.value, filteredData.value.length)
  return `${start}-${end} of ${filteredData.value.length}`
})

// Watch for data changes and reset page
watch(() => props.data, () => {
  currentPage.value = 1
  searchText.value = ''
})

// Watch for search changes and reset page
watch(searchText, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.csv-explorer {
  margin: 20px 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.explorer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.explorer-header h5 {
  margin: 0;
  font-size: 1em;
  font-weight: 600;
  color: #333;
}

.toggle-btn {
  color: #666;
}

.explorer-content {
  padding: 16px;
}

.search-bar {
  margin-bottom: 16px;
}

.search-input {
  max-width: 400px;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.data-table thead {
  background: #f8f9fa;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.sortable-header:hover {
  background: #e9ecef;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 4px;
}

.data-table tbody tr {
  border-bottom: 1px solid #e9ecef;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.data-table td {
  padding: 8px;
  color: #212529;
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.rows-per-page {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  color: #666;
}

.rows-select {
  width: 80px;
}

.pagination-info {
  font-size: 0.9em;
  color: #666;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-number {
  font-size: 0.9em;
  color: #666;
  min-width: 60px;
  text-align: center;
}

@media (max-width: 768px) {
  .explorer-content {
    padding: 12px;
  }

  .pagination-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .rows-per-page,
  .pagination-info,
  .pagination-buttons {
    justify-content: center;
  }

  .data-table {
    font-size: 0.8em;
  }

  .data-table td,
  .sortable-header {
    padding: 6px 4px;
  }
}
</style>
