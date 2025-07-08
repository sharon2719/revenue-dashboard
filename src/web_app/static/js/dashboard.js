// Updated Dashboard JavaScript with Chart Destruction Fix
class RevenueDashboard {
    constructor() {
        console.log('RevenueDashboard constructor called');
        this.charts = {};
        this.data = {};
        this.init();
    }

    init() {
        console.log('Dashboard initializing...');
        console.log('Chart.js available:', typeof Chart !== 'undefined');
        this.checkDOMElements();
        this.loadSummaryData();
        this.loadChartData();
        this.setupEventListeners();
    }

    checkDOMElements() {
        const requiredElements = [
            'summary-cards',
            'paymentTermsChart',
            'topClientsChart',
            'monthlyTrendChart',
            'contractsTable',
            'loading'
        ];
        requiredElements.forEach(id => {
            const element = document.getElementById(id);
            if (!element) {
                console.error(`Missing required element: ${id}`);
            } else {
                console.log(`✓ Found element: ${id}`);
            }
        });
    }

    async loadSummaryData() {
        console.log('Loading summary data...');
        try {
            const response = await fetch('/api/summary');
            console.log('Summary response status:', response.status);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            console.log('Summary data loaded:', data);
            this.data.summary = data;
            this.renderSummaryCards();
        } catch (error) {
            console.error('Error loading summary data:', error);
            this.showError('Failed to load summary data: ' + error.message);
        }
    }

    async loadChartData() {
        console.log('Loading chart data...');
        try {
            const endpoints = [
                '/api/payment_terms',
                '/api/top_clients',
                '/api/monthly_trend',
                '/api/contracts'
            ];
            console.log('Fetching from endpoints:', endpoints);
            const responses = await Promise.all(endpoints.map(endpoint => fetch(endpoint)));
            responses.forEach((response, i) => {
                console.log(`${endpoints[i]} response status:`, response.status);
                if (!response.ok) throw new Error(`HTTP error at ${endpoints[i]}! status: ${response.status}`);
            });
            const [paymentTerms, topClients, monthlyTrend, contracts] = await Promise.all(responses.map(r => r.json()));
            this.data.paymentTerms = paymentTerms;
            this.data.topClients = topClients;
            this.data.monthlyTrend = monthlyTrend;
            this.data.contracts = contracts;
            this.renderCharts();
            this.renderContractsTable();
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showError('Failed to load chart data: ' + error.message);
        }
    }

    renderSummaryCards() {
        const data = this.data.summary;
        const container = document.getElementById('summary-cards');
        if (!container) return console.error('Summary cards container not found');
        const cards = [
            {
                title: 'Total Contracts',
                value: data.total_contracts,
                icon: 'fas fa-file-contract',
                class: 'contracts'
            },
            {
                title: 'Recognized Revenue',
                value: this.formatCurrency(data.total_recognized_revenue),
                icon: 'fas fa-dollar-sign',
                class: 'revenue'
            },
            {
                title: 'Remaining Revenue',
                value: this.formatCurrency(data.total_remaining_revenue),
                icon: 'fas fa-hourglass-half',
                class: 'remaining'
            },
            {
                title: 'Recognition Rate',
                value: `${data.recognition_rate}%`,
                icon: 'fas fa-percentage',
                class: 'percentage'
            }
        ];
        container.innerHTML = cards.map(card => `
            <div class="col-md-3 mb-3">
                <div class="card summary-card ${card.class}">
                    <div class="card-body">
                        <div class="card-icon"><i class="${card.icon}"></i></div>
                        <div class="card-value">${card.value}</div>
                        <div class="card-label">${card.title}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderCharts() {
        this.renderPaymentTermsChart();
        this.renderTopClientsChart();
        this.renderMonthlyTrendChart();
    }

    renderPaymentTermsChart() {
        const canvas = document.getElementById('paymentTermsChart');
        if (!canvas) return console.error('Payment terms chart canvas not found');
        const existing = Chart.getChart(canvas);
        if (existing) existing.destroy();

        const data = this.data.paymentTerms;
        if (!data || !data.length) return console.error('No payment terms data available');

        const colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6610f2'];

        this.charts.paymentTerms = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.payment_terms),
                datasets: [{
                    data: data.map(d => d.total_recognized_revenue),
                    backgroundColor: colors.slice(0, data.length),
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 20, usePointStyle: true }
                    },
                    tooltip: {
                        callbacks: {
                            label: context => `${context.label}: ${this.formatCurrency(context.parsed)}`
                        }
                    }
                }
            }
        });
    }

    renderTopClientsChart() {
        const canvas = document.getElementById('topClientsChart');
        if (!canvas) return console.error('Top clients chart canvas not found');
        const existing = Chart.getChart(canvas);
        if (existing) existing.destroy();

        const data = this.data.topClients;
        if (!data || !data.length) return console.error('No top clients data available');

        const top = data.slice(0, 5);
        this.charts.topClients = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: top.map(c => c.client_name),
                datasets: [{
                    label: 'Recognized Revenue',
                    data: top.map(c => c.total_recognized_revenue),
                    backgroundColor: '#0d6efd',
                    borderColor: '#0b5ed7',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: val => this.formatCurrency(val)
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `Revenue: ${this.formatCurrency(ctx.parsed.y)}`
                        }
                    }
                }
            }
        });
    }

    renderMonthlyTrendChart() {
        const canvas = document.getElementById('monthlyTrendChart');
        if (!canvas) return console.error('Monthly trend chart canvas not found');
        const existing = Chart.getChart(canvas);
        if (existing) existing.destroy();

        const data = this.data.monthlyTrend;
        if (!data || !data.length) return console.error('No monthly trend data available');

        this.charts.monthlyTrend = new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [{
                    label: 'Monthly Recognized Revenue',
                    data: data.map(d => d.monthly_recognized_revenue),
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: val => this.formatCurrency(val)
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `Revenue: ${this.formatCurrency(ctx.parsed.y)}`
                        }
                    }
                }
            }
        });
    }

    renderContractsTable() {
        const tbody = document.querySelector('#contractsTable tbody');
        if (!tbody) return console.error('Contracts table tbody not found');

        const data = this.data.contracts;
        if (!data || !data.length) return console.error('No contracts data available');

        tbody.innerHTML = data.slice(0, 10).map(c => `
            <tr>
                <td>${c.client_name}</td>
                <td class="currency">${this.formatCurrency(c.total_value)}</td>
                <td class="currency positive">${this.formatCurrency(c.total_recognized_revenue)}</td>
                <td class="currency">${this.formatCurrency(c.remaining_revenue)}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar ${this.getProgressBarClass(c.avg_completion_percentage)}" style="width: ${c.avg_completion_percentage}%">
                            ${Math.round(c.avg_completion_percentage)}%
                        </div>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getProgressBarClass(pct) {
        if (pct >= 90) return 'bg-success';
        if (pct >= 70) return 'bg-info';
        if (pct >= 50) return 'bg-warning';
        return 'bg-danger';
    }

    setupEventListeners() {
        setInterval(() => {
            console.log('Auto-refreshing...');
            this.loadSummaryData();
            this.loadChartData();
        }, 5 * 60 * 1000);

        document.addEventListener('keydown', e => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                console.log('Manual refresh triggered');
                this.showLoading();
                this.loadSummaryData();
                this.loadChartData();
            }
        });
    }

    formatCurrency(val) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(val || 0);
    }

    showError(message) {
        console.error('Showing error:', message);
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            <strong>Error!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            setTimeout(() => alert.remove(), 5000);
        }
    }

    showLoading() {
        const el = document.getElementById('loading');
        if (el) {
            el.style.display = 'block';
            setTimeout(() => el.style.display = 'none', 2000);
        }
    }
}

// Global init
function loadDashboard() {
    console.log('loadDashboard() called');
    try {
        window.dashboard = new RevenueDashboard();
    } catch (e) {
        console.error('Failed to initialize dashboard:', e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM ready → loading dashboard');
    loadDashboard();
});
