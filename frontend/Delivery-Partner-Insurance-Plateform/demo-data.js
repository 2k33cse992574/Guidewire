(function () {
  const STORAGE_KEYS = {
    user: "deliveryUser",
    plan: "selectedPlan",
    claims: "claims",
    activity: "activityLog"
  };

  const defaults = {
    user: {
      name: "Aarav Singh",
      platform: "Swiggy",
      phone: "9876543210"
    },
    plan: {
      plan: 99,
      coverage: 2500
    },
    claims: {
      rain: 1,
      traffic: 1,
      outage: 0
    },
    activity: [
      {
        label: "premium paid for current week",
        tone: "success",
        time: "Today, 9:30 AM"
      },
      {
        label: "claim initiated after route slowdown",
        tone: "warning",
        time: "Today, 11:05 AM"
      },
      {
        label: "payout processed for recent disruption",
        tone: "success",
        time: "Today, 11:40 AM"
      }
    ]
  };

  const payouts = {
    rain: 1000,
    traffic: 800,
    outage: 1200
  };

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function readJson(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : clone(fallback);
    } catch (error) {
      return clone(fallback);
    }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function ensureDemoData() {
    if (!localStorage.getItem(STORAGE_KEYS.user)) {
      writeJson(STORAGE_KEYS.user, defaults.user);
    }
    if (!localStorage.getItem(STORAGE_KEYS.plan)) {
      writeJson(STORAGE_KEYS.plan, defaults.plan);
    }
    if (!localStorage.getItem(STORAGE_KEYS.claims)) {
      writeJson(STORAGE_KEYS.claims, defaults.claims);
    }
    if (!localStorage.getItem(STORAGE_KEYS.activity)) {
      writeJson(STORAGE_KEYS.activity, defaults.activity);
    }
  }

  function clearDemoData() {
    Object.values(STORAGE_KEYS).forEach(function (key) {
      localStorage.removeItem(key);
    });
  }

  function getUser() {
    return readJson(STORAGE_KEYS.user, defaults.user);
  }

  function getPlan() {
    return readJson(STORAGE_KEYS.plan, defaults.plan);
  }

  function getClaims() {
    return readJson(STORAGE_KEYS.claims, defaults.claims);
  }

  function getActivity() {
    return readJson(STORAGE_KEYS.activity, defaults.activity);
  }

  function setUser(user) {
    writeJson(STORAGE_KEYS.user, user);
  }

  function setPlan(plan) {
    writeJson(STORAGE_KEYS.plan, plan);
  }

  function setClaims(claims) {
    writeJson(STORAGE_KEYS.claims, claims);
  }

  function setActivity(activity) {
    writeJson(STORAGE_KEYS.activity, activity);
  }

  function appendActivity(label, tone) {
    const activity = getActivity();
    activity.unshift({
      label: label,
      tone: tone || "neutral",
      time: "Now"
    });
    setActivity(activity.slice(0, 8));
  }

  function getTotalSaved(claims) {
    return claims.rain * payouts.rain + claims.traffic * payouts.traffic + claims.outage * payouts.outage;
  }

  function getRiskLevel(score) {
    if (score >= 75) {
      return "High";
    }
    if (score >= 50) {
      return "Medium";
    }
    return "Low";
  }

  async function getMetrics() {
    const user = getUser();
    const plan = getPlan();
    const activity = getActivity();
    
    try {
      const response = await fetch('/api/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: user, plan: plan })
      });
      const data = await response.json();
      
      return {
        user: user,
        plan: plan,
        claims: data.claims,
        activity: activity,
        totalClaims: data.totalClaims,
        totalSaved: data.totalSaved,
        riskScore: data.riskScore,
        coverageUsed: data.coverageUsed,
        riskLevel: data.riskLevel
      };
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      const claims = getClaims();
      return {
        user: user,
        plan: plan,
        claims: claims,
        activity: activity,
        totalClaims: 0,
        totalSaved: 0,
        riskScore: 0,
        coverageUsed: 0,
        riskLevel: "Low"
      };
    }
  }

  function formatMoney(value) {
    return "Rs " + Number(value).toLocaleString("en-IN");
  }

  window.DeliveryProtect = {
    STORAGE_KEYS: STORAGE_KEYS,
    payouts: payouts,
    defaults: defaults,
    ensureDemoData: ensureDemoData,
    clearDemoData: clearDemoData,
    getUser: getUser,
    getPlan: getPlan,
    getClaims: getClaims,
    getActivity: getActivity,
    setUser: setUser,
    setPlan: setPlan,
    setClaims: setClaims,
    setActivity: setActivity,
    appendActivity: appendActivity,
    getMetrics: getMetrics,
    formatMoney: formatMoney,
    getTotalSaved: getTotalSaved
  };
})();
