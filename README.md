# atlas-score

Interactive visualization of the ATLAS Indoor Environmental Quality Index using horizon charts to display temporal variations across multiple environmental aspects.

## About ATLAS Index

The ATLAS index evaluates holistic indoor environmental quality across four key aspects:

- **Indoor Air Quality** (with sub-parameters: CO2, formaldehyde, etc.)
- **Thermal Comfort**
- **Lighting**
- **Acoustics**

Each aspect receives a score from 0-100, along with an overall environmental quality score. The visualization displays temporal variations at hourly resolution using color-coded horizon charts.

## Features

### Interactive Visualizations

- **Horizon Charts**: Compact multi-series time series visualization with configurable band heights and number of bands
- **Circular Category Overview**: Radial chart showing average scores across environmental categories
- **Expandable Detail View**: Click any horizon band to see detailed line chart with full temporal resolution

### Data Flexibility

- **Custom CSV Upload**: Upload your own ATLAS data files for analysis
- **Series Filtering**: Option to display only the first data series for cleaner visualization of datasets with multiple series
- **Dual Data Views**: Toggle between raw values and normalized scores (0-100)

### Interactive Controls

- Adjustable visualization parameters (band height, number of bands)
- Real-time chart updates
- SVG export functionality for high-quality outputs

## Contributors

- EPFL - HOBEL Lab (Research & Data): Bowen Du, Son Pham-Ba, Dusan Licina
- EPFL - ENAC-IT4R (Implementation): Pierre Jean Ripoll

## Tech Stack

- [Vite](https://vitejs.dev/) - Build Tool & Development Server
- [Vue.js 3](https://vuejs.org/) - Progressive JavaScript Framework with Composition API
- [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript development
- [D3.js](https://d3js.org/) - Data Visualization Library for charts and interactions
- [Quasar Framework](https://quasar.dev/) - Vue.js UI components and utilities

## Visualization Approach

The platform uses **horizon charts** to efficiently display multiple time series in compact vertical space. This innovative approach allows visualization of large temporal datasets by:

- **Color-coded bands**: Values are mapped to colored horizontal bands, with intensity indicating magnitude
- **Vertical stacking**: Multiple data series are stacked vertically for easy comparison
- **Interactive expansion**: Click any band to expand into a detailed line chart view
- **Smart grouping**: Data is automatically grouped by environmental categories with custom ordering

### Supported Data Categories

- 4 main environmental categories with customizable visualization parameters
- Sub-category parameters (particularly detailed for indoor air quality metrics)
- Multi-series datasets with automatic series detection and filtering options

## Development

### Prerequisites

- Node.js (v22+)
- npm

### Setup & Usage

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Environment

The development environment includes:

- Frontend at http://localhost:5173
- Hot module replacement for rapid development
- TypeScript compilation and type checking
- ESLint and Prettier for code quality

## Getting Started

### Using the Application

1. **Default Data**: The application loads with sample ATLAS data for demonstration
2. **Upload Custom Data**: Use the upload button to load your own CSV files
3. **Adjust Visualization**:
   - Toggle between "Value" and "Score" views
   - Adjust band height and number of bands
   - Filter to show first series only for cleaner multi-series datasets
4. **Interact with Charts**:
   - Click any horizon band to expand to detailed line chart
   - Click again to collapse back to horizon view
   - Download visualizations as SVG files

### Example Workflow

```bash
# 1. Start the application
npm run dev

# 2. Open http://localhost:5173 in your browser
# 3. Upload your ATLAS CSV data using the upload button
# 4. Adjust visualization parameters as needed
# 5. Click horizon bands to explore detailed temporal patterns
# 6. Export charts as SVG for reports or presentations
```

## Data Structure

### CSV Format

The application expects CSV data with the following columns:

```csv
id,time,category,field,value,score
0,2025-03-15 00:00:00+00:00,Air quality,co2,3500.0,0.0
1,2025-03-15 01:00:00+00:00,Air quality,co2,2800.0,10.0
...
```

### Required Fields

- **id**: Unique identifier for each data point
- **time**: ISO timestamp (hourly resolution recommended)
- **category**: Environmental category (e.g., "Air quality", "Thermal comfort")
- **field**: Specific parameter within category (e.g., "co2", "temperature")
- **value**: Raw measurement value
- **score**: Normalized score (0-100 scale)

### Supported Categories

- **Air quality**: CO2, formaldehyde, humidity, PM2.5, PM10, etc.
- **Thermal comfort**: Temperature, humidity-related comfort metrics
- **Lighting**: Light levels, daylight availability
- **Acoustics**: Sound level indicators

### Multi-Series Support

The application automatically detects multiple data series based on non-consecutive ID sequences and provides filtering options to display either all series or just the first series for cleaner visualization.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Status

Under active development. [Report bugs here](https://github.com/EPFL-ENAC/atlas-viz/issues).

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE) - see the LICENSE file for details.

This is free software: you can redistribute it and/or modify it under the terms of the GPL-3.0 as published by the Free Software Foundation.
