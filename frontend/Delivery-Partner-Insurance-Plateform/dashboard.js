(function () {
  const app = window.DeliveryProtect;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function buildMonthSeries(totalSaved) {
    const floor = Math.max(1000, Math.round(totalSaved * 0.45));
    return [floor, floor + 350, floor + 240, floor + 620, floor + 500, floor + 920, floor + 780, Math.max(totalSaved, floor + 1200)];
  }

  function buildChartPoints(series) {
    return series.map(function (value, index) {
      const x = 30 + index * 44;
      const y = 160 - ((value - series[0]) / Math.max(series[series.length - 1] - series[0], 1)) * 105;
      return `${x},${Math.max(26, Math.min(150, y))}`;
    }).join(" ");
  }

  function animateCounters() {
    document.querySelectorAll("[data-count-to]").forEach(function (counter) {
      const target = Number(counter.getAttribute("data-count-to")) || 0;
      const prefix = counter.getAttribute("data-prefix") || "";
      const suffix = counter.getAttribute("data-suffix") || "";

      if (reducedMotion.matches) {
        counter.textContent = `${prefix}${target.toLocaleString("en-IN")}${suffix}`;
        return;
      }

      const start = performance.now();
      const duration = 1100;

      function update(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = Math.round(target * eased);
        counter.textContent = `${prefix}${value.toLocaleString("en-IN")}${suffix}`;

        if (progress < 1) {
          requestAnimationFrame(update);
        }
      }

      requestAnimationFrame(update);
    });
  }

  function animateProgressBars() {
    document.querySelectorAll(".progress-fill").forEach(function (bar) {
      const targetWidth = bar.getAttribute("data-width") || "0%";
      bar.style.setProperty("--target-width", targetWidth);

      if (reducedMotion.matches) {
        bar.style.width = targetWidth;
        return;
      }

      requestAnimationFrame(function () {
        bar.style.width = targetWidth;
      });
    });
  }

  function animateGauge(metrics) {
    const gauge = document.querySelector(".gauge-ring");

    if (!gauge) {
      return;
    }

    const finalAngle = Math.round((metrics.riskScore / 100) * 240);

    if (reducedMotion.matches) {
      gauge.style.background = `conic-gradient(#ef4444 0deg ${finalAngle}deg, #334155 ${finalAngle}deg 240deg, transparent 240deg 360deg)`;
      return;
    }

    const start = performance.now();
    const duration = 1200;

    function update(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const angle = Math.round(finalAngle * eased);
      gauge.style.background = `conic-gradient(#ef4444 0deg ${angle}deg, #334155 ${angle}deg 240deg, transparent 240deg 360deg)`;

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  function revealPanels() {
    const items = document.querySelectorAll(".reveal");

    items.forEach(function (item) {
      const delay = Number(item.getAttribute("data-delay")) || 0;
      item.style.setProperty("--delay", `${delay}ms`);
    });

    if (reducedMotion.matches || typeof IntersectionObserver === "undefined") {
      items.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.16 });

    items.forEach(function (item) {
      observer.observe(item);
    });
  }

  function animateDashboard(metrics) {
    revealPanels();
    animateCounters();
    animateProgressBars();
    animateGauge(metrics);
  }

  async function renderDashboard() {
    app.ensureDemoData();
    const metrics = await app.getMetrics();
    const series = buildMonthSeries(Math.max(metrics.totalSaved, 2200));
    const chartPoints = buildChartPoints(series);
    const coverageLabel = metrics.coverageUsed + "% used";
    const riskTone = metrics.riskScore >= 75 ? "critical" : metrics.riskScore >= 50 ? "warning" : "stable";
    const weather = metrics.claims.rain > 0 ? {
      type: "rainy",
      label: "Rainy",
      title: "Rainfall alert across Mumbai South",
      detail: "Slower routes and claim-ready protection are active.",
      helper: "Rain-trigger monitoring is enabled."
    } : {
      type: "sunny",
      label: "Sunny",
      title: "Clear skies across Mumbai South",
      detail: "Routes are moving normally with lower weather disruption risk.",
      helper: "Protection remains active in the background."
    };
    const alerts = [
      {
        tone: "critical",
        title: "Heavy Rain and Flood Warning",
        details: "Affected duration: next 120 minutes",
        loss: "Estimated income loss: Rs 650",
        action: "Auto-trigger ready"
      },
      {
        tone: "warning",
        title: "Severe Heat Alert",
        details: "Reduced order velocity in your route cluster",
        loss: "Claim assistance available",
        action: "Monitoring live"
      }
    ];

    const metricCards = [
      ["Weekly Premium", app.formatMoney(metrics.plan.plan), "Current period", "violet", "Rs"],
      ["Coverage Status", "Active Protection", `Weekly limit: ${app.formatMoney(metrics.plan.coverage)}`, "green", "SH"],
      ["Protected Earnings", app.formatMoney(metrics.totalSaved), `Across ${metrics.totalClaims} claims`, "cyan", "UP"],
      ["Current Risk Level", metrics.riskLevel, `Risk score ${metrics.riskScore}`, "red", "AL"],
      ["Primary Zone", "Mumbai South", `${metrics.user.platform} rider hub`, "amber", "MP"]
    ];

    const watchlist = [
      ["Coverage reserve", `${Math.max(0, 100 - metrics.coverageUsed)}% left`],
      ["Live zone health", metrics.riskScore >= 75 ? "Volatile" : "Stable watch"],
      ["Next payout path", metrics.totalClaims > 0 ? "Fast-track enabled" : "Ready on standby"]
    ];

    const timelineHtml = metrics.activity.map(function (item) {
      const toneClass = item.tone === "danger" ? "danger-dot" : item.tone === "warning" ? "warning-dot" : "success-dot";
      return `
        <div class="timeline-row">
          <span class="timeline-dot ${toneClass}"></span>
          <div>
            <p>${item.label}</p>
            <small>${item.time}</small>
          </div>
        </div>`;
    }).join("");

    const weatherVisual = weather.type === "rainy"
      ? `
        <div class="weather-visual rainy" aria-hidden="true">
          <div class="weather-cloud cloud-one"></div>
          <div class="weather-cloud cloud-two"></div>
          <div class="rain-lines">
            <span></span><span></span><span></span><span></span><span></span><span></span>
          </div>
        </div>`
      : `
        <div class="weather-visual sunny" aria-hidden="true">
          <div class="weather-sun">
            <span class="sun-core"></span>
            <span class="sun-ray ray-one"></span>
            <span class="sun-ray ray-two"></span>
            <span class="sun-ray ray-three"></span>
            <span class="sun-ray ray-four"></span>
          </div>
          <div class="weather-cloud soft-cloud"></div>
        </div>`;
    const weatherMascot = weather.type === "rainy"
      ? `
        <div class="weather-mascot rainy frog-mascot" aria-hidden="true">
          <div class="frog-lily"></div>
          <div class="frog-body"></div>
          <div class="frog-belly"></div>
          <div class="frog-head">
            <span class="frog-eye frog-eye-left"><span class="frog-pupil"></span></span>
            <span class="frog-eye frog-eye-right"><span class="frog-pupil"></span></span>
            <span class="frog-smile"></span>
          </div>
          <div class="frog-arm left"></div>
          <div class="frog-arm right"></div>
          <div class="frog-leg left"></div>
          <div class="frog-leg right"></div>
          <div class="umbrella">
            <span class="umbrella-top"></span>
            <span class="umbrella-stick"></span>
          </div>
        </div>`
      : `
        <div class="weather-mascot sunny" aria-hidden="true">
          <div class="mascot-head">
            <span class="eye left"></span>
            <span class="eye right"></span>
            <span class="smile"></span>
          </div>
          <div class="mascot-body light"></div>
          <div class="mascot-arm left wave"></div>
          <div class="mascot-arm right"></div>
          <div class="mascot-leg left"></div>
          <div class="mascot-leg right"></div>
        </div>`;

    const alertHtml = alerts.map(function (alert) {
      return `
        <div class="alert-card ${alert.tone}">
          <strong>${alert.title}</strong>
          <p>${alert.details}</p>
          <p>${alert.loss}</p>
          <span>${alert.action}</span>
        </div>`;
    }).join("");

    const cardsHtml = metricCards.map(function (card, index) {
      return `
        <article class="metric-card ${card[3]} reveal" data-delay="${220 + index * 50}">
          <div class="metric-topline">
            <span class="metric-icon-badge">${card[4]}</span>
            <p class="metric-label">${card[0]}</p>
          </div>
          <h3>${card[1]}</h3>
          <span>${card[2]}</span>
        </article>`;
    }).join("");

    const watchlistHtml = watchlist.map(function (item) {
      return `
        <div class="watchlist-row">
          <span>${item[0]}</span>
          <strong>${item[1]}</strong>
        </div>`;
    }).join("");

    const pointHtml = series.map(function (value, index) {
      const x = 30 + index * 44;
      const y = 160 - ((value - series[0]) / Math.max(series[series.length - 1] - series[0], 1)) * 105;
      return `<circle cx="${x}" cy="${Math.max(26, Math.min(150, y))}" r="4" class="chart-point" style="animation-delay: ${0.45 + index * 0.08}s;"></circle>`;
    }).join("");

    document.getElementById("root").innerHTML = `
      <div class="dashboard-shell">
        <div class="browser-frame">
          <div class="browser-bar">
            <div class="browser-dots">
              <span class="dot dot-red"></span>
              <span class="dot dot-yellow"></span>
              <span class="dot dot-green"></span>
            </div>
            <div class="browser-address">deliveryprotect.io/demo</div>
          </div>

          <div class="app-surface">
            <header class="topbar">
              <div class="brand-wrap reveal" data-delay="0">
                <div class="brand-mark">DP</div>
                <div>
                  <h1>DeliveryProtect AI</h1>
                  <p>${metrics.user.name} | ${metrics.user.platform} partner protection dashboard</p>
                </div>
              </div>

              <nav class="topnav reveal" data-delay="80">
                <a class="active" href="dashboard.html">Dashboard</a>
                <a href="policy.html">My Coverage</a>
                <a href="claim.html">Activity</a>
                <a href="signup.html">Profile</a>
              </nav>

              <div class="nav-actions reveal" data-delay="140">
                <div class="status-pill"><span class="glow-dot"></span> AI Active</div>
                <button class="secondary-btn small-btn" onclick="location.href='index.html'">Home</button>
                <button class="secondary-btn small-btn" onclick="DeliveryProtect.clearDemoData(); location.href='index.html';">Reset</button>
                <div class="avatar">${metrics.user.name.charAt(0)}</div>
              </div>
            </header>

            <section class="dashboard-hero reveal" data-delay="120">
              <div class="hero-grid">
                <div class="hero-copy">
                  <span class="hero-badge"><span class="glow-dot"></span> Live protection center</span>
                  <h2>Insurance intelligence built for high-pressure delivery shifts.</h2>
                  <p>Track coverage, risk, disruption alerts, and protected earnings in one cleaner control room designed to feel more premium and more trustworthy at a glance.</p>

                  <div class="hero-chip-row">
                    <div class="hero-chip">Weekly plan <strong>${app.formatMoney(metrics.plan.plan)}</strong></div>
                    <div class="hero-chip">Coverage <strong>${app.formatMoney(metrics.plan.coverage)}</strong></div>
                    <div class="hero-chip">Zone <strong>Mumbai South</strong></div>
                  </div>

                  <div class="hero-actions-row">
                    <button class="primary-cta" onclick="location.href='claim.html'">Review Live Activity</button>
                    <button class="ghost-cta secondary-btn" onclick="location.href='policy.html'">Check Coverage</button>
                  </div>

                  <div class="hero-stats-bar">
                    <div class="hero-stat">
                      <span>Protected this period</span>
                      <strong data-count-to="${metrics.totalSaved}" data-prefix="Rs ">Rs 0</strong>
                    </div>
                    <div class="hero-stat">
                      <span>Total disruptions tracked</span>
                      <strong data-count-to="${metrics.totalClaims}">0</strong>
                    </div>
                    <div class="hero-stat">
                      <span>Current risk score</span>
                      <strong data-count-to="${metrics.riskScore}" data-suffix="%">0%</strong>
                    </div>
                  </div>

                  <div class="hero-character" aria-hidden="true">
                    <img class="hero-character-image" src="assets/delivery-boy.png" alt="Delivery boy character">
                    <div class="hero-character-shadow"></div>
                  </div>
                </div>

                <aside class="spotlight-card">
                  <div class="spotlight-topline">
                    <span class="spotlight-label">Shift Watch</span>
                    <span class="spotlight-risk ${riskTone}">${metrics.riskLevel} risk</span>
                  </div>
                  <p>System confidence is high and automated claim assistance is standing by for weather and route disruptions.</p>

                  <div class="hero-kpis">
                    <div class="hero-kpi">
                      <span>Auto-trigger readiness</span>
                      <strong>98%</strong>
                    </div>
                    <div class="hero-kpi">
                      <span>Payout confidence</span>
                      <strong>Fast lane</strong>
                    </div>
                    <div class="hero-kpi">
                      <span>Most likely disruption</span>
                      <strong>Rain surge</strong>
                    </div>
                    <div class="hero-kpi">
                      <span>Support status</span>
                      <strong>Monitoring live</strong>
                    </div>
                  </div>

                  <div class="watchlist-card">
                    <div class="watchlist-head">
                      <h4>Live watchlist</h4>
                      <span>Updated now</span>
                    </div>
                    ${watchlistHtml}
                  </div>
                </aside>
              </div>
            </section>

            <section class="metric-grid">${cardsHtml}</section>

            <section class="dashboard-grid">
              <article class="panel risk-panel reveal" data-delay="260">
                <div class="panel-header">
                  <h2>My Risk and Coverage</h2>
                  <span>Risk score: ${metrics.riskScore}%</span>
                </div>

                <div class="gauge-wrap">
                  <div class="gauge-ring">
                    <div class="gauge-inner">
                      <strong data-count-to="${metrics.riskScore}">0</strong>
                      <span>${metrics.riskLevel}</span>
                    </div>
                  </div>
                </div>

                <div class="progress-block">
                  <div class="progress-copy">
                    <span>Weekly Coverage Limit</span>
                    <span>${coverageLabel}</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" data-width="${metrics.coverageUsed}%"></div>
                  </div>
                </div>

                <div class="summary-tile">
                  <span>Total protected so far</span>
                  <strong data-count-to="${metrics.totalSaved}" data-prefix="Rs ">Rs 0</strong>
                </div>
              </article>

              <article class="panel earnings-panel reveal" data-delay="320">
                <div class="panel-header">
                  <h2>Earnings Saved to Date</h2>
                  <span>Live demo data</span>
                </div>

                <svg class="earnings-chart" viewBox="0 0 360 180" role="img" aria-label="Earnings saved line chart">
                  <defs>
                    <linearGradient id="lineGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#38bdf8"></stop>
                      <stop offset="100%" stop-color="#60a5fa"></stop>
                    </linearGradient>
                  </defs>
                  <line x1="30" y1="20" x2="30" y2="160" class="axis-line"></line>
                  <line x1="30" y1="160" x2="340" y2="160" class="axis-line"></line>
                  <polyline points="${chartPoints}" class="chart-line" style="stroke: url(#lineGlow);"></polyline>
                  ${pointHtml}
                  <g class="axis-labels">
                    <text x="25" y="170">Jan</text>
                    <text x="69" y="170">Feb</text>
                    <text x="113" y="170">Mar</text>
                    <text x="157" y="170">Apr</text>
                    <text x="201" y="170">May</text>
                    <text x="245" y="170">Jun</text>
                    <text x="289" y="170">Jul</text>
                    <text x="329" y="170">Now</text>
                  </g>
                </svg>

                <div class="summary-strip">
                  <strong data-count-to="${metrics.totalSaved}" data-prefix="Rs ">Rs 0</strong>
                  <span>protected across ${metrics.totalClaims} payout events</span>
                </div>

                <div class="mini-table">
                  <div class="mini-table-head">
                    <span>Date</span>
                    <span>Amount</span>
                    <span>Reason</span>
                  </div>
                  <div class="mini-table-row">
                    <span>Today</span>
                    <span>${app.formatMoney(metrics.totalSaved)}</span>
                    <span>Income protection saved</span>
                  </div>
                  <div class="mini-table-row">
                    <span>Today</span>
                    <span>${app.formatMoney(app.payouts.traffic)}</span>
                    <span>Traffic delay protection</span>
                  </div>
                  <div class="mini-table-row">
                    <span>Today</span>
                    <span>${app.formatMoney(app.payouts.rain)}</span>
                    <span>Rain payout protected</span>
                  </div>
                </div>
              </article>

              <article class="panel sidebar-panel reveal" data-delay="380">
                <div class="panel-group">
                  <div class="panel-header">
                    <h2>Weather</h2>
                    <span>${weather.label}</span>
                  </div>
                  <div class="weather-card ${weather.type}">
                    ${weatherVisual}
                    ${weatherMascot}
                    <div class="weather-copy">
                      <strong>${weather.title}</strong>
                      <p>${weather.detail}</p>
                      <span>${weather.helper}</span>
                    </div>
                  </div>
                </div>

                <div class="panel-group">
                  <div class="panel-header">
                    <h2>Active Disruptions</h2>
                    <span>Mumbai South</span>
                  </div>
                  ${alertHtml}
                </div>

                <div class="panel-group">
                  <div class="panel-header">
                    <h2>Activity Timeline</h2>
                    <span>Reverse order</span>
                  </div>
                  <div class="timeline">${timelineHtml}</div>
                </div>

                <div class="action-row">
                  <button onclick="location.href='claim.html'">Trigger Claim</button>
                  <button class="secondary-btn" onclick="location.href='admin.html'">Open Admin</button>
                </div>
              </article>
            </section>
          </div>
        </div>
      </div>`;

    animateDashboard(metrics);
  }

  document.addEventListener("DOMContentLoaded", renderDashboard);
})();
