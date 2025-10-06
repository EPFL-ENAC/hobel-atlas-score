# atlas-score

Interactive visualization of the ATLAS Indoor Environmental Quality Index using horizon charts to display temporal variations across multiple environmental aspects.

## About ATLAS Index

The ATLAS index evaluates holistic indoor environmental quality across four key aspects:

- **Indoor Air Quality** (with sub-parameters: CO2, formaldehyde, etc.)
- **Thermal Comfort**
- **Luminous Comfort**
- **Acoustic Comfort**

Each aspect receives a score from 0-100, along with an overall environmental quality score. The visualization displays temporal variations at hourly resolution using color-coded horizon charts.

## Contributors

- EPFL - HOBEL Lab (Research & Data): Bowen Du, Son Pham-Ba, Dusan Licina
- EPFL - ENAC-IT4R (Implementation): Pierre Jean Ripoll

## Tech Stack

- [Vite](https://vitejs.dev/) - Build Tool
- [Vue.js 3](https://vuejs.org/) - Progressive JavaScript Framework
- [D3.js](https://d3js.org/) - Data Visualization Library

## Visualization Approach

The platform uses **horizon charts** to efficiently display multiple time series in compact vertical space. Values are represented through color-coded bands, allowing easy comparison of trends across:

- 4 main environmental categories
- Overall environmental quality score
- Sub-category parameters (particularly for indoor air quality)

## Development

### Prerequisites

- Node.js (v22+)
- npm

### Setup & Usage

```bash
npm install
npm run dev
npm run build
npm run preview
```

### Development Environment

The development environment includes:

- Frontend at http://localhost:5173

## Data Structure

The ATLAS index data includes:

- Timestamp (hourly resolution)
- Overall score (0-100)
- Category scores: Indoor Air Quality, Thermal Comfort, Luminous Comfort, Acoustic Comfort (0-100 each)
- Sub-category parameters under Indoor Air Quality (CO2, formaldehyde, etc.)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Status

Under active development. [Report bugs here](https://github.com/EPFL-ENAC/atlas-viz/issues).

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE) - see the LICENSE file for details.

This is free software: you can redistribute it and/or modify it under the terms of the GPL-3.0 as published by the Free Software Foundation.
