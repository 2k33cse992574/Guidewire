(function () {
  const app = window.DeliveryProtect;
  const disruptionInfo = {
    rain: {
      label: "Hydro-Anomaly injected",
      amount: app.payouts.rain,
      activity: "algorithmic trigger reached consensus: liquidity executed"
    },
    traffic: {
      label: "Velocity loss anomaly injected",
      amount: app.payouts.traffic,
      activity: "execution protocol initiated for route velocity drop"
    },
    outage: {
      label: "Routing Network block injected",
      amount: app.payouts.outage,
      activity: "routing outage micro-hedge executed"
    },
    spoof: {
      label: "Adversarial GPS Teleportation Detected",
      amount: 0,
      activity: "algorithmic oracle blocked fraudulent execution attempt"
    }
  };

  async function renderClaimStats() {
    const target = document.getElementById("claimStats");
    if (!target) {
      return;
    }

    const metrics = await app.getMetrics();
    target.innerHTML = ""
      + `<div class="stat-pill"><span>Injected so far</span><strong>${app.formatMoney(metrics.totalSaved)}</strong></div>`
      + `<div class="stat-pill"><span>Total Settlements</span><strong>${metrics.totalClaims}</strong></div>`
      + `<div class="stat-pill"><span>Systemic Risk</span><strong>${metrics.riskLevel}</strong></div>`;
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
      if (type === 'spoof') {
        message.style.color = '#ef4444';
        message.textContent = `${entry.label}. Execution rejected by Oracle. Wallet secured.`;
      } else {
        message.style.color = 'inherit';
        message.textContent = `${entry.label}. ${app.formatMoney(entry.amount)} injected into partner liquidity pool.`;
      }
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
