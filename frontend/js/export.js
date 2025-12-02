function initExport() {
    const exportContainer = document.getElementById('export-container');
    if (!exportContainer) return;

    exportContainer.innerHTML = `
        <div class="export-panel">
            <div class="export-header">
                <span style="font-size: 1.5rem;">📥</span>
                <h3>Export to PDF</h3>
            </div>
            
            <div class="export-filters-section" style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 0.875rem; font-weight: 600; color: #1e40af; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🔍</span>
                    <span>Filter Data to Export</span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem;">
                    <input type="text" id="export-search" class="search-input" placeholder="Search by name or indication..." style="padding: 0.5rem 0.75rem; font-size: 0.875rem;">
                    
                    <select id="export-category" class="filter-select" style="padding: 0.5rem 0.75rem; font-size: 0.875rem;">
                        <option value="">All Categories</option>
                    </select>
                    
                    <select id="export-manufacturer" class="filter-select" style="padding: 0.5rem 0.75rem; font-size: 0.875rem;">
                        <option value="">All Manufacturers</option>
                    </select>
                    
                    <select id="export-classification" class="filter-select" style="padding: 0.5rem 0.75rem; font-size: 0.875rem;">
                        <option value="">All Classifications</option>
                        <option value="Prescription">Prescription</option>
                        <option value="Over-the-Counter">Over-the-Counter</option>
                    </select>
                </div>
                
                <div id="export-preview" style="margin-top: 0.75rem; font-size: 0.8rem; color: #64748b;">
                    Loading record count...
                </div>
            </div>

            <button id="export-btn" class="export-btn-main">
                📑 Export to PDF
            </button>

            <div id="export-status" style="display: none;"></div>

            <div class="export-tip">
                <strong>Tip:</strong> Use the filters above to narrow down the data before exporting. Leave filters empty to export all medicines.
            </div>
        </div>
    `;

    loadExportFilterOptions();

    const filterInputs = ['export-search', 'export-category', 'export-manufacturer', 'export-classification'];
    filterInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', updateExportPreview);
            el.addEventListener('input', debounce(updateExportPreview, 300));
        }
    });

    updateExportPreview();

    const exportBtn = document.getElementById('export-btn');
    exportBtn.addEventListener('click', async function() {
        const filters = getExportFilters();

        const statusDiv = document.getElementById('export-status');
        statusDiv.style.display = 'block';
        statusDiv.className = 'export-status loading';
        statusDiv.innerHTML = '<span>⏳</span><span>Generating PDF...</span>';

        try {
            const response = await fetch('/api/export/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filters: filters
                })
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `medicine_report_${Date.now()}.pdf`;
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            statusDiv.className = 'export-status success';
            statusDiv.innerHTML = '<span>✅</span><span>PDF exported successfully! Check your downloads.</span>';
            
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);

        } catch (error) {
            console.error('Export error:', error);
            statusDiv.className = 'export-status error';
            statusDiv.innerHTML = `<span>❌</span><span>Export failed: ${error.message}</span>`;
        }
    });
}

function getExportFilters() {
    const filters = {};
    
    const search = document.getElementById('export-search')?.value?.trim();
    const category = document.getElementById('export-category')?.value;
    const manufacturer = document.getElementById('export-manufacturer')?.value;
    const classification = document.getElementById('export-classification')?.value;
    
    if (search) filters.q = search;
    if (category) filters.category = category;
    if (manufacturer) filters.manufacturer = manufacturer;
    if (classification) filters.classification = classification;
    
    return filters;
}

async function loadExportFilterOptions() {
    try {
        const response = await fetch('/api/medicines/filters');
        const data = await response.json();
        
        const catSelect = document.getElementById('export-category');
        if (catSelect && data.categories) {
            data.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.name;
                option.textContent = cat.name;
                catSelect.appendChild(option);
            });
        }
        
        const mfrSelect = document.getElementById('export-manufacturer');
        if (mfrSelect && data.manufacturers) {
            data.manufacturers.forEach(mfr => {
                const option = document.createElement('option');
                option.value = mfr.name;
                option.textContent = mfr.name;
                mfrSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load export filter options:', error);
    }
}

async function updateExportPreview() {
    const previewDiv = document.getElementById('export-preview');
    if (!previewDiv) return;
    
    const filters = getExportFilters();
    
    try {
        const params = new URLSearchParams();
        if (filters.q) params.append('q', filters.q);
        if (filters.category) params.append('category', filters.category);
        if (filters.manufacturer) params.append('manufacturer', filters.manufacturer);
        
        const response = await fetch(`/api/medicines?${params.toString()}&limit=10000`);
        const data = await response.json();
        
        const count = data.results?.length || 0;
        const filterDesc = Object.keys(filters).length > 0 
            ? `with current filters` 
            : `(no filters applied - all medicines)`;
        
        previewDiv.innerHTML = `<strong>${count.toLocaleString()}</strong> medicines will be exported ${filterDesc}`;
    } catch (error) {
        previewDiv.innerHTML = 'Unable to preview count';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
