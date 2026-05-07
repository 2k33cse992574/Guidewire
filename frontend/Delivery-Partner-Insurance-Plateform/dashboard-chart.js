function renderClaimsChart() {
  const chartCanvas = document.getElementById("chart");

  if (!chartCanvas || typeof Chart === "undefined") {
    return;
  }

  const claims = JSON.parse(localStorage.getItem("claims")) || {
    rain: 0,
    traffic: 0,
    outage: 0
  };

  new Chart(chartCanvas, {
    type: "bar",
    data: {
      labels: ["Rain", "Traffic", "Outage"],
      datasets: [{
        label: "Triggered claims",
        data: [claims.rain, claims.traffic, claims.outage],
        backgroundColor: ["#38bdf8", "#f97316", "#ef4444"],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", renderClaimsChart);
