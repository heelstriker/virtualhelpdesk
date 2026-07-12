/**
 * network-live-sync.js
 * ---------------------------------------------------------------
 * Refreshes the Dashboard's Active Alerts / Alert Breakdown /
 * Managed Devices / Device Status chart / Risk Devices table from
 * /api/dashboard/summary, without a full page reload.
 *
 * Called automatically after every Network Topology widget toggle
 * (see templates/partials/_network_diagram.html), since toggling a
 * device/link there cascades into the real `devices.status` column
 * (services/network_topology_service.py::_sync_devices_with_topology),
 * which is exactly what dashboard_service.py queries.
 *
 * Chart.js instances are looked up via Chart.getChart(canvas) — the
 * built-in Chart.js registry — so this doesn't need to know anything
 * about how dashboard.js constructed them.
 */
(function (global) {
  "use strict";

  async function refreshDashboardLive() {
    let data;
    try {
      const res = await fetch("/api/dashboard/summary");
      data = await res.json();
    } catch (e) {
      console.warn("Dashboard live refresh failed:", e);
      return;
    }

    // Active Alerts count
    const alertsEl = document.getElementById("active-alerts-value");
    if (alertsEl) alertsEl.textContent = data.summary.alert_count;

    // Alert Breakdown messages
    const noticesEl = document.getElementById("alertboard-notices");
    if (noticesEl) {
      noticesEl.innerHTML = "";
      if (data.alertboard.length === 0) {
        const div = document.createElement("div");
        div.className = "notice";
        div.textContent = "✓ No active alerts.";
        noticesEl.appendChild(div);
      } else {
        data.alertboard.forEach((msg) => {
          const div = document.createElement("div");
          div.className = "notice";
          div.textContent = "⚠ " + msg;
          noticesEl.appendChild(div);
        });
      }
    }

    // Managed Devices count
    const managedEl = document.getElementById("managed-devices-value");
    if (managedEl) managedEl.textContent = data.summary.total_devices;

    // Charts, via Chart.js's own registry — no dashboard.js internals needed
    updateChart("complianceChart", (chart) => {
      chart.data.datasets[0].data = [data.summary.compliance_percent, data.summary.risk_percent];
    });
    updateChart("riskBreakdownChart", (chart) => {
      chart.data.labels = data.summary.risk_labels;
      chart.data.datasets[0].data = data.summary.risk_counts;
    });
    updateChart("deviceStatusChart", (chart) => {
      chart.data.labels = data.device_status_labels;
      chart.data.datasets[0].data = data.device_status_counts;
    });

    // Risk Devices table
    const tbody = document.getElementById("risk-devices-body");
    if (tbody) {
      tbody.innerHTML = "";
      data.risks.forEach((device) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><a href="/devices/${device.hostname}">${device.hostname}</a></td>
          <td>${device.owner ?? ""}</td>
          <td><span class="critical">Alert Detected</span></td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  function updateChart(canvasId, mutate) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;
    const chart = Chart.getChart(canvas);
    if (!chart) return;
    mutate(chart);
    chart.update();
  }

  global.refreshDashboardLive = refreshDashboardLive;
})(window);
