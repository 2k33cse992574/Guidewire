(function () {
  const app = window.DeliveryProtect;

  function renderBar(label, count, colorClass) {
    return `
      <div class="admin-bar-row">
        <div class="admin-bar-head">
          <span>${label}</span>
          <strong>${count}</strong>
        </div>
        <div class="admin-bar-track">
          <div class="admin-bar-fill ${colorClass}" style="width: ${Math.max(count * 18, 12)}%;"></div>
        </div>
      </div>`;
  }

  async function renderAdmin() {
    app.ensureDemoData();
    const metrics = await app.getMetrics();
    const claims = metrics.claims;

    document.getElementById("adminRoot").innerHTML = `
      <div class="container page-shell admin-shell">
        <span class="eyebrow">Admin View</span>
        <h2>Operations Analytics</h2>
        <p class="subtext">A reliable demo-safe analytics page with no external chart library dependency.</p>

        <div class="metric-grid admin-metric-grid">
          <article class="metric-card purple">
            <p class="metric-label">Total Claims</p>
            <h3>${metrics.totalClaims}</h3>
            <span>Across all tracked disruptions</span>
          </article>
          <article class="metric-card teal">
            <p class="metric-label">Protected Amount</p>
            <h3>${app.formatMoney(metrics.totalSaved)}</h3>
            <span>Partner payout impact</span>
          </article>
          <article class="metric-card red">
            <p class="metric-label">Current Risk</p>
            <h3>${metrics.riskLevel}</h3>
            <span>Score ${metrics.riskScore}</span>
          </article>
        </div>

        <div class="card admin-card">
          <h3>Disruption Breakdown</h3>
          ${renderBar("Rain", claims.rain, "fill-rain")}
          ${renderBar("Traffic", claims.traffic, "fill-traffic")}
          ${renderBar("Outage", claims.outage, "fill-outage")}
        </div>

        <div class="hero-actions">
          <button onclick="location.href='dashboard.html'">Back to Dashboard</button>
          <button class="secondary" onclick="location.href='claim.html'">Open Trigger Screen</button>
        </div>
      </div>`;
  }

  document.addEventListener("DOMContentLoaded", renderAdmin);
})();
