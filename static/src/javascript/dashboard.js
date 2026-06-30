// VirtualHelpDesk - Dashboard charts
// 注意: このファイルは static/src/javascript/ に配置される純粋なJSのため、
// Jinja2の {{ }} はここでは使えません。
// dashboard.html 側で <body> に data-* 属性として値を埋め込み、
// このスクリプトで読み取る方式にしています。

document.addEventListener('DOMContentLoaded', function () {

    const dataEl = document.getElementById('dashboard-data');
    if (!dataEl) {
        console.error('dashboard-data element not found; charts will not render.');
        return;
    }

    const compliancePercent = parseFloat(dataEl.dataset.compliancePercent);
    const riskPercent = parseFloat(dataEl.dataset.riskPercent);
    const riskLabels = JSON.parse(dataEl.dataset.riskLabels);
    const riskCounts = JSON.parse(dataEl.dataset.riskCounts);
    const trendDates = JSON.parse(dataEl.dataset.trendDates);
    const trendPercent = JSON.parse(dataEl.dataset.trendPercent);
    const waveLabels = JSON.parse(dataEl.dataset.waveLabels);
    const waveCounts = JSON.parse(dataEl.dataset.waveCounts);
    const deptLabels = JSON.parse(dataEl.dataset.deptLabels);
    const deptCounts = JSON.parse(dataEl.dataset.deptCounts);
    
    const deviceStatus =  JSON.parase(dataEl.dataset.device_status);

    const labels = deviceStatus.map(item => item.status);
    const values = deviceStatus.map(item => item.count);

    const ctx = document.getElementById('deviceStatusChart');

    new Chart(ctx, {

        type: 'pie',

        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#2ecc71',
                    '#e74c3c',
                    '#f1c40f'
                ]
            }]
        },

        options: {

            responsive: true,

            plugins: {
                datalabels: {

                formatter: (value, context) => {

                const total = context.dataset.data.reduce((a,b)=>a+b,0);

                return Math.round(value / total * 100) + "%";
                      }
                      }
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    

    const centerTextPlugin = {
        id: 'centerText',
        afterDraw(chart) {
            const { ctx } = chart;
            const meta = chart.getDatasetMeta(0);
            if (!meta.data.length) return;

            const x = meta.data[0].x;
            const y = meta.data[0].y;

            ctx.save();
            ctx.textAlign = 'center';

            ctx.fillStyle = '#0fb9b1';
            ctx.font = 'bold 42px Segoe UI';
            ctx.fillText(compliancePercent + '%', x, y - 10);

            ctx.fillStyle = '#6b7280';
            ctx.font = '16px Segoe UI';
            ctx.fillText('Compliance', x, y + 25);

            ctx.restore();
        }
    };

    new Chart(document.getElementById('complianceChart'), {
        type: 'doughnut',
        data: {
            labels: ['Compliant', 'At Risk'],
            datasets: [{
                data: [compliancePercent, riskPercent],
                backgroundColor: ['#0fb9b1', '#e63946'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 15, bottom: 15, left: 10, right: 20 } },
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#1f2933', padding: 20 }
                },
                tooltip: { enabled: true }
            }
        },
        plugins: [centerTextPlugin]
    });

    new Chart(document.getElementById('riskBreakdownChart'), {
        type: 'bar',
        data: {
            labels: riskLabels,
            datasets: [{
                label: 'Risk Devices',
                data: riskCounts,
                backgroundColor: '#ff9f1c'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 15, bottom: 15, left: 10, right: 20 } },
            scales: {
                y: { ticks: { color: '#1f2933' }, grid: { color: '#e2e8ea' } },
                x: { ticks: { color: '#1f2933' }, grid: { color: '#e2e8ea' } }
            },
            plugins: { legend: { display: false } }
        }
    });

    new Chart(document.getElementById('patchTrendChart'), {
        type: 'line',
        data: {
            labels: trendDates,
            datasets: [{
                label: 'Patch Compliance %',
                data: trendPercent,
                tension: 0.4,
                fill: true,
                borderColor: '#0fb9b1',
                backgroundColor: 'rgba(15,185,177,0.12)',
                pointRadius: 4,
                pointBackgroundColor: '#0fb9b1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 15, bottom: 15, left: 10, right: 20 } },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    ticks: { color: '#6b7280' },
                    grid: { color: '#e2e8ea' }
                },
                x: {
                    ticks: { color: '#6b7280' },
                    grid: { color: '#e2e8ea' }
                }
            },
            plugins: { legend: { labels: { color: '#1f2933' } } }
        }
    });

    new Chart(document.getElementById('PatchWaveBreakdownChart'), {
        type: 'bar',
        data: {
            labels: waveLabels,
            datasets: [{
                data: waveCounts,
                label: '% Completed',
                backgroundColor: '#0fb9b1'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    min: 0,
                    max: 100,
                    ticks: { color: '#1f2933' },
                    grid: { color: '#e2e8ea' }
                },
                y: {
                    ticks: { color: '#1f2933' },
                    grid: { color: '#e2e8ea' }
                }
            },
            layout: { padding: { top: 15, bottom: 15, left: 10, right: 20 } },
            plugins: { legend: { display: false } }
        }
    });

    new Chart(document.getElementById('PatchDeptBreakdownChart'), {
        type: 'bar',
        data: {
            labels: deptLabels,
            datasets: [{
                label: '% Completed',
                data: deptCounts,
                backgroundColor: '#0a8f89'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    min: 0,
                    max: 100,
                    ticks: { color: '#1f2933' },
                    grid: { color: '#e2e8ea' }
                },
                y: {
                    ticks: { color: '#1f2933' },
                    grid: { color: '#e2e8ea' }
                }
            },
            layout: { padding: { top: 15, bottom: 15, left: 10, right: 20 } },
            plugins: { legend: { display: false } }
        }
    });

});
