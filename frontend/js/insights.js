async function initializeInsights() {
    await Promise.all([
        renderCategoryChart(),
        renderManufacturerChart(),
        renderClassificationChart()
    ]);
}

async function renderCategoryChart() {
    const container = document.getElementById('category-chart');
    if (!container) return;

    container.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const response = await MDVS.fetchAPI('/api/insights/categories/distribution');
        const data = response.data;

        container.innerHTML = '';

        const margin = { top: 20, right: 40, bottom: 40, left: 110 };
        const width = container.clientWidth - margin.left - margin.right;
        const height = Math.max(320, data.length * 38) - margin.top - margin.bottom;

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([0, width]);
        const y = d3.scaleBand().domain(data.map(d => d.category)).range([0, height]).padding(0.25);

        const tooltip = MDVS.createTooltip();

        svg.selectAll('.bar')
            .data(data)
            .enter()
            .append('rect')
            .attr('class', 'bar')
            .attr('x', 0)
            .attr('y', d => y(d.category))
            .attr('height', y.bandwidth())
            .attr('fill', (d, i) => MDVS.getChartColor(i))
            .attr('rx', 5)
            .attr('width', 0)
            .on('mouseover', function (event, d) {
                d3.select(this).attr('opacity', 0.8);
                tooltip.show(`<strong>${d.category}</strong><br>Count: ${d.count.toLocaleString()}<br>Share: ${d.percentage}%`);
            })
            .on('mousemove', (event) => tooltip.move(event.pageX, event.pageY))
            .on('mouseout', function () { d3.select(this).attr('opacity', 1); tooltip.hide(); })
            .on('click', (event, d) => showCategoryDetails(d.category))
            .transition()
            .duration(600)
            .delay((d, i) => i * 40)
            .attr('width', d => x(d.count));

        svg.selectAll('.bar-label')
            .data(data)
            .enter()
            .append('text')
            .attr('x', d => x(d.count) + 8)
            .attr('y', d => y(d.category) + y.bandwidth() / 2)
            .attr('dy', '0.35em')
            .attr('fill', '#64748b')
            .attr('font-size', '11px')
            .attr('font-weight', '500')
            .attr('opacity', 0)
            .text(d => d.count.toLocaleString())
            .transition()
            .duration(600)
            .delay((d, i) => i * 40 + 300)
            .attr('opacity', 1);

        svg.append('g')
            .attr('class', 'axis')
            .call(d3.axisLeft(y))
            .selectAll('text')
            .style('cursor', 'pointer')
            .on('click', (event, category) => showCategoryDetails(category));

        svg.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(',d')));

    } catch (error) {
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:#ef4444;">Failed to load category data</div>';
        console.error(error);
    }
}

async function renderManufacturerChart() {
    const container = document.getElementById('manufacturer-chart');
    if (!container) return;

    container.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const response = await MDVS.fetchAPI('/api/insights/manufacturers/ranking?limit=10');
        const data = response.data;

        container.innerHTML = '';

        const margin = { top: 20, right: 70, bottom: 40, left: 140 };
        const width = container.clientWidth - margin.left - margin.right;
        const height = 360 - margin.top - margin.bottom;

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear().domain([0, d3.max(data, d => d.medicine_count)]).range([0, width]);
        const y = d3.scaleBand().domain(data.map(d => d.manufacturer)).range([0, height]).padding(0.25);

        const gradient = svg.append('defs')
            .append('linearGradient')
            .attr('id', 'mfr-gradient')
            .attr('x1', '0%')
            .attr('x2', '100%');
        gradient.append('stop').attr('offset', '0%').attr('stop-color', '#2563eb');
        gradient.append('stop').attr('offset', '100%').attr('stop-color', '#7c3aed');

        const tooltip = MDVS.createTooltip();

        svg.selectAll('.bar')
            .data(data)
            .enter()
            .append('rect')
            .attr('class', 'bar')
            .attr('x', 0)
            .attr('y', d => y(d.manufacturer))
            .attr('height', y.bandwidth())
            .attr('fill', 'url(#mfr-gradient)')
            .attr('rx', 5)
            .attr('width', 0)
            .on('mouseover', function (event, d) {
                d3.select(this).attr('opacity', 0.8);
                tooltip.show(`<strong>${d.manufacturer}</strong><br>Medicines: ${d.medicine_count.toLocaleString()}<br>Categories: ${d.category_count}<br>Market Share: ${d.market_share}%`);
            })
            .on('mousemove', (event) => tooltip.move(event.pageX, event.pageY))
            .on('mouseout', function () { d3.select(this).attr('opacity', 1); tooltip.hide(); })
            .on('click', (event, d) => showManufacturerDetails(d.manufacturer))
            .transition()
            .duration(600)
            .delay((d, i) => i * 60)
            .attr('width', d => x(d.medicine_count));

        svg.selectAll('.share-label')
            .data(data)
            .enter()
            .append('text')
            .attr('x', d => x(d.medicine_count) + 8)
            .attr('y', d => y(d.manufacturer) + y.bandwidth() / 2)
            .attr('dy', '0.35em')
            .attr('fill', '#64748b')
            .attr('font-size', '10px')
            .attr('font-weight', '600')
            .attr('opacity', 0)
            .text(d => `${d.market_share}%`)
            .transition()
            .duration(600)
            .delay((d, i) => i * 60 + 300)
            .attr('opacity', 1);

        svg.append('g')
            .attr('class', 'axis')
            .call(d3.axisLeft(y))
            .selectAll('text')
            .text(d => d.length > 16 ? d.substring(0, 14) + '...' : d)
            .style('cursor', 'pointer')
            .on('click', (event, mfr) => showManufacturerDetails(mfr));

        svg.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(',d')));

    } catch (error) {
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:#ef4444;">Failed to load manufacturer data</div>';
        console.error(error);
    }
}

async function renderClassificationChart() {
    const container = document.getElementById('classification-chart');
    if (!container) return;

    container.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const response = await MDVS.fetchAPI('/api/insights/categories/classification');
        const data = response.data;

        container.innerHTML = '';

        const margin = { top: 30, right: 140, bottom: 70, left: 60 };
        const width = container.clientWidth - margin.left - margin.right;
        const height = 320 - margin.top - margin.bottom;

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        const classifications = ['Prescription', 'Over-the-Counter'];
        const x0 = d3.scaleBand().domain(data.map(d => d.category)).range([0, width]).padding(0.2);
        const x1 = d3.scaleBand().domain(classifications).range([0, x0.bandwidth()]).padding(0.1);
        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => Math.max(d.Prescription || 0, d['Over-the-Counter'] || 0))])
            .nice()
            .range([height, 0]);
        const color = d3.scaleOrdinal().domain(classifications).range(['#2563eb', '#10b981']);

        const tooltip = MDVS.createTooltip();

        const groups = svg.selectAll('.category-group')
            .data(data)
            .enter()
            .append('g')
            .attr('transform', d => `translate(${x0(d.category)},0)`);

        groups.selectAll('rect')
            .data(d => classifications.map(cls => ({ classification: cls, value: d[cls] || 0, category: d.category })))
            .enter()
            .append('rect')
            .attr('class', 'bar')
            .attr('x', d => x1(d.classification))
            .attr('width', x1.bandwidth())
            .attr('fill', d => color(d.classification))
            .attr('rx', 4)
            .attr('y', height)
            .attr('height', 0)
            .on('mouseover', function (event, d) {
                d3.select(this).attr('opacity', 0.8);
                tooltip.show(`<strong>${d.category}</strong><br>${d.classification}: ${d.value.toLocaleString()}`);
            })
            .on('mousemove', (event) => tooltip.move(event.pageX, event.pageY))
            .on('mouseout', function () { d3.select(this).attr('opacity', 1); tooltip.hide(); })
            .transition()
            .duration(600)
            .delay((d, i) => i * 80)
            .attr('y', d => y(d.value))
            .attr('height', d => height - y(d.value));

        svg.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x0))
            .selectAll('text')
            .attr('transform', 'rotate(-35)')
            .style('text-anchor', 'end')
            .attr('dx', '-0.5em')
            .attr('dy', '0.5em');

        svg.append('g')
            .attr('class', 'axis')
            .call(d3.axisLeft(y).ticks(5).tickFormat(d3.format(',d')));

        const legend = svg.append('g').attr('transform', `translate(${width + 20}, 0)`);
        classifications.forEach((cls, i) => {
            const item = legend.append('g').attr('transform', `translate(0, ${i * 28})`);
            item.append('rect').attr('width', 18).attr('height', 18).attr('rx', 4).attr('fill', color(cls));
            item.append('text').attr('x', 26).attr('y', 14).attr('font-size', '12px').attr('fill', '#64748b').text(cls);
        });

    } catch (error) {
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:#ef4444;">Failed to load classification data</div>';
        console.error(error);
    }
}

async function showCategoryDetails(categoryName) {
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-content');

    panel.querySelector('.panel-title').textContent = 'Category Details';
    panel.style.display = 'block';
    content.innerHTML = '<div class="loading-spinner"></div>';
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    try {
        const data = await MDVS.fetchAPI(`/api/insights/categories/${encodeURIComponent(categoryName)}`);

        content.innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;">
                <div>
                    <h4 style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Category</h4>
                    <p style="font-size:1.25rem;font-weight:600;color:#1e293b;">${data.category.category}</p>
                    <p style="color:#64748b;font-size:0.875rem;margin-top:0.25rem;">${data.category.medicine_count.toLocaleString()} medicines from ${data.category.manufacturer_count} manufacturers</p>
                </div>
                <div>
                    <h4 style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Top Manufacturers</h4>
                    <ul style="list-style:none;padding:0;margin:0;">
                        ${data.top_manufacturers.map(m => `<li style="padding:0.375rem 0;display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;"><span style="color:#1e293b;">${m.manufacturer}</span><span style="color:#64748b;font-weight:500;">${m.count}</span></li>`).join('')}
                    </ul>
                </div>
                <div>
                    <h4 style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Dosage Forms</h4>
                    <ul style="list-style:none;padding:0;margin:0;">
                        ${data.dosage_forms.map(d => `<li style="padding:0.375rem 0;display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;"><span style="color:#1e293b;">${d.dosage_form}</span><span style="color:#64748b;font-weight:500;">${d.count}</span></li>`).join('')}
                    </ul>
                </div>
            </div>
            <button onclick="document.getElementById('detail-panel').style.display='none'" class="btn btn-secondary" style="margin-top:1.5rem;">Close</button>
        `;
    } catch (error) {
        content.innerHTML = `<p style="color:#ef4444;">Failed to load details</p><button onclick="document.getElementById('detail-panel').style.display='none'" class="btn btn-secondary" style="margin-top:1rem;">Close</button>`;
    }
}

async function showManufacturerDetails(manufacturerName) {
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-content');

    panel.querySelector('.panel-title').textContent = 'Manufacturer Details';
    panel.style.display = 'block';
    content.innerHTML = '<div class="loading-spinner"></div>';
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    try {
        const data = await MDVS.fetchAPI(`/api/insights/manufacturers/${encodeURIComponent(manufacturerName)}`);

        content.innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;">
                <div>
                    <h4 style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Manufacturer</h4>
                    <p style="font-size:1.25rem;font-weight:600;color:#1e293b;">${data.manufacturer.manufacturer}</p>
                    <p style="color:#64748b;font-size:0.875rem;margin-top:0.25rem;">${data.manufacturer.medicine_count.toLocaleString()} medicines across ${data.manufacturer.category_count} categories</p>
                </div>
                <div>
                    <h4 style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Categories</h4>
                    <ul style="list-style:none;padding:0;margin:0;">
                        ${data.categories.slice(0, 5).map(c => `<li style="padding:0.375rem 0;display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;"><span style="color:#1e293b;">${c.category}</span><span style="color:#64748b;font-weight:500;">${c.count}</span></li>`).join('')}
                    </ul>
                </div>
                <div>
                    <h4 style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Classification Split</h4>
                    <ul style="list-style:none;padding:0;margin:0;">
                        ${data.classifications.map(c => `<li style="padding:0.375rem 0;display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;"><span style="color:#1e293b;">${c.classification}</span><span style="color:#64748b;font-weight:500;">${c.count}</span></li>`).join('')}
                    </ul>
                </div>
            </div>
            <button onclick="document.getElementById('detail-panel').style.display='none'" class="btn btn-secondary" style="margin-top:1.5rem;">Close</button>
        `;
    } catch (error) {
        content.innerHTML = `<p style="color:#ef4444;">Failed to load details</p><button onclick="document.getElementById('detail-panel').style.display='none'" class="btn btn-secondary" style="margin-top:1rem;">Close</button>`;
    }
}

let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        renderCategoryChart();
        renderManufacturerChart();
        renderClassificationChart();
    }, 250);
});
