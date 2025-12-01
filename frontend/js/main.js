const API_BASE = '';
let insightsLoaded = false;

async function fetchAPI(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
}

async function loadOverviewStats() {
    const container = document.getElementById('stats-container');

    try {
        const data = await fetchAPI('/api/insights/overview');

        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon">💊</div>
                <div class="stat-value">${data.total_medicines.toLocaleString()}</div>
                <div class="stat-label">Total Medicines</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🏭</div>
                <div class="stat-value">${data.total_manufacturers.toLocaleString()}</div>
                <div class="stat-label">Manufacturers</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📁</div>
                <div class="stat-value">${data.total_categories}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📋</div>
                <div class="stat-value">${(data.classification_split['Prescription'] || 0).toLocaleString()}</div>
                <div class="stat-label">Prescription</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🛒</div>
                <div class="stat-value">${(data.classification_split['Over-the-Counter'] || 0).toLocaleString()}</div>
                <div class="stat-label">Over-the-Counter</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🏆</div>
                <div class="stat-value" style="font-size: 1.125rem;">${data.top_manufacturer?.name || 'N/A'}</div>
                <div class="stat-label">Top Manufacturer</div>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `
            <div class="stat-card" style="grid-column: 1 / -1;">
                <div class="stat-icon">⚠️</div>
                <div class="stat-value" style="font-size: 1rem; color: var(--error);">Failed to load data</div>
                <div class="stat-label">Check console for details</div>
            </div>
        `;
        console.error('Error loading stats:', error);
    }
}

function setupTabs() {
    const navLinks = document.querySelectorAll('.nav-link');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = link.getAttribute('data-tab');

            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === targetTab) {
                    panel.classList.add('active');
                }
            });

            if (targetTab === 'insights' && !insightsLoaded) {
                loadInsightsTab();
            }
        });
    });
}

async function loadInsightsTab() {
    if (insightsLoaded) return;
    await loadOverviewStats();
    if (typeof initializeInsights === 'function') {
        await initializeInsights();
    }
    insightsLoaded = true;
}

function createTooltip() {
    let tooltip = document.querySelector('.tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        document.body.appendChild(tooltip);
    }
    return {
        show: (html) => { tooltip.innerHTML = html; tooltip.classList.add('visible'); },
        hide: () => tooltip.classList.remove('visible'),
        move: (x, y) => { tooltip.style.left = `${x + 15}px`; tooltip.style.top = `${y - 10}px`; }
    };
}

const CHART_COLORS = ['#2563eb', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6'];

function getChartColor(i) {
    return CHART_COLORS[i % CHART_COLORS.length];
}

async function checkHealth() {
    try {
        const health = await fetchAPI('/health');
        console.log('MDVS Health:', health);
        if (health.database.status === 'error') {
            alert('Database connection failed. Check PostgreSQL.');
        }
    } catch (e) {
        console.error('Health check failed:', e);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await checkHealth();
    setupTabs();
});

window.MDVS = { fetchAPI, createTooltip, getChartColor, CHART_COLORS };