import type { EnvironmentalData } from '../composables/useHorizonChart';

export const parseCSVData = (csvData: string): EnvironmentalData[] => {
  const lines = csvData.trim().split('\n');
  if (lines.length < 2 || !lines[0]) return [];

  // Parse header row to determine column positions
  const headers = lines[0].split(',').map((h) => h.trim().toLowerCase());

  const colIndex = (field: string) => {
    const idx = headers.indexOf(field.toLowerCase());
    if (idx === -1) {
      console.warn(`CSV parser: missing column "${field}" in header: ${headers.join(', ')}`);
    }
    return idx;
  };

  const timeIdx = colIndex('time');
  const categoryIdx = colIndex('category');
  const fieldIdx = colIndex('field');
  const valueIdx = colIndex('value');
  const scoreIdx = colIndex('score');

  // Validate all required columns were found
  if ([timeIdx, categoryIdx, fieldIdx, valueIdx, scoreIdx].includes(-1)) {
    console.error('CSV parser: one or more required columns are missing');
    return [];
  }

  // Parse data rows
  return lines
    .slice(1)
    .map((line) => {
      const values = line.split(',');

      const timeStr = values[timeIdx] || '';
      const category = values[categoryIdx] || '';
      const field = values[fieldIdx] || '';
      const value = parseFloat(values[valueIdx] || '0');
      const score = parseFloat(values[scoreIdx] || '0');

      if (!timeStr || isNaN(value) || isNaN(score)) return null;

      return {
        time: new Date(timeStr),
        category,
        field,
        value,
        score,
      };
    })
    .filter((item): item is EnvironmentalData => item !== null);
};

export const downloadSVG = (container: HTMLElement, filename: string) => {
  const svgElement = container.querySelector('svg');
  if (!svgElement) return;

  // Serialize the SVG to a string
  const serializer = new XMLSerializer();
  let svgString = serializer.serializeToString(svgElement);

  // Add namespaces if they're missing
  if (!svgString.includes('xmlns')) {
    svgString = svgString.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  if (!svgString.includes('xmlns:xlink')) {
    svgString = svgString.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
  }

  // Create a blob from the SVG string
  const blob = new Blob([svgString], { type: 'image/svg+xml' });

  // Create a download link
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;

  // Trigger the download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Clean up the URL object
  URL.revokeObjectURL(url);
};

export const downloadPNG = (container: HTMLElement, filename: string, dpi: number = 300) => {
  const svgElement = container.querySelector('svg');
  if (!svgElement) return;

  // Get original SVG dimensions
  const bbox = svgElement.getBoundingClientRect();
  const width = bbox.width;
  const height = bbox.height;

  // Calculate scale factor for DPI (72 DPI is the default screen resolution)
  const scale = dpi / 72;

  // Serialize the SVG
  const serializer = new XMLSerializer();
  let svgString = serializer.serializeToString(svgElement);

  // Add namespaces if missing
  if (!svgString.includes('xmlns')) {
    svgString = svgString.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  if (!svgString.includes('xmlns:xlink')) {
    svgString = svgString.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
  }

  // Create a blob and object URL
  const blob = new Blob([svgString], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);

  // Create an image element
  const img = new Image();
  img.onload = () => {
    // Create canvas with scaled dimensions
    const canvas = document.createElement('canvas');
    canvas.width = width * scale;
    canvas.height = height * scale;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Scale the context to achieve higher DPI
    ctx.scale(scale, scale);

    // Draw the image
    ctx.drawImage(img, 0, 0);

    // Convert to PNG and download
    canvas.toBlob((pngBlob) => {
      if (!pngBlob) return;

      const pngUrl = URL.createObjectURL(pngBlob);
      const link = document.createElement('a');
      link.href = pngUrl;
      link.download = filename.replace(/\.svg$/, '.png');

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up
      URL.revokeObjectURL(pngUrl);
      URL.revokeObjectURL(url);
    }, 'image/png');
  };

  img.src = url;
};

export const sortCategoriesByOrder = (categories: string[]): string[] => {
  const categoryOrder = ['Air quality', 'Thermal comfort', 'Lighting', 'Acoustics'];

  return categories.sort((a, b) => {
    const indexA = categoryOrder.indexOf(a);
    const indexB = categoryOrder.indexOf(b);

    // If both categories are in our custom order, sort according to that order
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB;
    }

    // If only one category is in our custom order, it comes first
    if (indexA !== -1) {
      return -1;
    }
    if (indexB !== -1) {
      return 1;
    }

    // If neither category is in our custom order, maintain natural order
    return 0;
  });
};
