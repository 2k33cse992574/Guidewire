(function () {
  const app = window.DeliveryProtect;
  const disruptionInfo = {
    rain: {
      label: "Rain disruption detected",
      amount: app.payouts.rain,
      activity: "weather trigger detected and payout credited"
    },
    traffic: {
      label: "Traffic slowdown detected",
      amount: app.payouts.traffic,
      activity: "traffic claim initiated for route delay"
    },
    outage: {
      label: "Network outage detected",
      amount: app.payouts.outage,
      activity: "outage protection triggered"
    }
  };

  async function renderClaimStats() {
    const target = document.getElementById("claimStats");
    if (!target) {
      return;
    }

    const metrics = await app.getMetrics();
    target.innerHTML = ""
      + `<div class="stat-pill"><span>Protected so far</span><strong>${app.formatMoney(metrics.totalSaved)}</strong></div>`
      + `<div class="stat-pill"><span>Total claims</span><strong>${metrics.totalClaims}</strong></div>`
      + `<div class="stat-pill"><span>Risk level</span><strong>${metrics.riskLevel}</strong></div>`;
  }

  async function simulate(type) {
    const message = document.getElementById("msg");
    const entry = disruptionInfo[type];

    app.appendActivity(entry.activity, type === "rain" ? "danger" : "warning");

    try {
      await fetch('/api/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: type })
      });
    } catch (error) {
      console.error("Failed to trigger API:", error);
    }

    if (message) {
      message.textContent = `${entry.label}. ${app.formatMoney(entry.amount)} credited to the partner wallet.`;
    }

    await renderClaimStats();

    setTimeout(function () {
      window.location.href = "dashboard.html";
    }, 1400);
  }

  document.addEventListener("DOMContentLoaded", function () {
    app.ensureDemoData();
    renderClaimStats();
  });

  window.simulate = simulate;
})();
