(function () {
  const app = window.DeliveryProtect;

  // CSS bars removed in favor of Chart.js Pie Chart as requested in README

  async function renderAdmin() {
    app.ensureDemoData();
    const metrics = await app.getMetrics();
    const claims = metrics.claims;

    document.getElementById("adminRoot").innerHTML = `
      <div class="container page-shell admin-shell">
        <span class="eyebrow">Quantitative Terminal</span>
        <h2>Algorithmic Executions</h2>
        <p class="subtext">A live demo risk-terminal evaluating anomaly interception and injected liquidity limits.</p>

        <div class="metric-grid admin-metric-grid">
          <article class="metric-card purple">
            <p class="metric-label">Total Executions</p>
            <h3>${metrics.totalClaims}</h3>
            <span>Across all anomalies</span>
          </article>
          <article class="metric-card teal">
            <p class="metric-label">Liquidity Injected</p>
            <h3>${app.formatMoney(metrics.totalSaved)}</h3>
            <span>Total hedge payouts</span>
          </article>
          <article class="metric-card red">
            <p class="metric-label">Systemic Risk</p>
            <h3>${metrics.riskLevel}</h3>
            <span>Score ${metrics.riskScore}</span>
          </article>
          <article class="metric-card amber">
            <p class="metric-label">Predictive Forecast</p>
            <h3>${metrics.predictiveRisk}%</h3>
            <span>Disruption prob. next 72 hrs</span>
          </article>
          <article class="metric-card cyan">
            <p class="metric-label">Fraud Flags</p>
            <h3>${metrics.fraudFlags}</h3>
            <span>Anomalous claims intercepted</span>
          </article>
        </div>

        <div class="card admin-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; min-height: 400px; padding: 24px;">
          <h3 style="margin-bottom: 24px; text-align: center;">Disruption Distribution (Chart.js)</h3>
          <div style="position: relative; width: 90%; max-width: 400px; aspect-ratio: 1; display:flex; justify-content:center;">
            <canvas id="claimsPieChart"></canvas>
          </div>
        </div>

        <div class="hero-actions">
          <button onclick="location.href='dashboard.html'">Back to Terminal</button>
          <button class="secondary" onclick="location.href='claim.html'">Inject Anomaly Simulation</button>
        </div>
      </div>`;

    setTimeout(() => {
      const ctx = document.getElementById('claimsPieChart');
      if (ctx && window.Chart) {
        new Chart(ctx, {
          type: 'pie',
          data: {
            labels: ['Hydro-Anomaly (Rain)', 'Velocity Loss (Traffic)', 'Routing Outage (Network)'],
            datasets: [{
              data: [claims.rain, claims.traffic, claims.outage],
              backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444'],
              borderWidth: 0,
              hoverOffset: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: { color: document.body.classList.contains('dark') ? '#e2e8f0' : '#475569', padding: 20, font: { size: 14 } }
              }
            }
          }
        });
      }
    }, 100);
  }

  document.addEventListener("DOMContentLoaded", renderAdmin);
})();
