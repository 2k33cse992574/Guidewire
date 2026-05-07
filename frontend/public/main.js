(function () {
  const app = window.DeliveryProtect;

  async function saveUser() {
    const nameInput = document.getElementById("name");
    const phoneInput = document.getElementById("phone");
    const passwordInput = document.getElementById("password");
    const platformInput = document.getElementById("platform");
    const error = document.getElementById("signupError");

    if (!nameInput || !phoneInput || !platformInput || !passwordInput) {
      return;
    }

    const name = nameInput.value.trim();
    const phone = phoneInput.value.trim();
    const password = passwordInput.value.trim();

    if (!name || !phone || !password) {
      error.textContent = "Please enter the node ID, name, and passkey.";
      return;
    }

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          phone: phone,
          password: password,
          platform: platformInput.value
        })
      });
      const data = await response.json();
      if (!response.ok) {
        error.textContent = data.detail || "Registration failed.";
        return;
      }
      localStorage.setItem("authToken", data.token);
      app.setUser(data.user);
      app.appendActivity("oracle node profile registered", "success");
      window.location.href = "policy.html";
    } catch (e) {
      error.textContent = "Server error during registration.";
    }
  }

  async function loginUser() {
    const phoneInput = document.getElementById("loginPhone");
    const passwordInput = document.getElementById("loginPassword");
    const error = document.getElementById("loginError");

    if (!phoneInput || !passwordInput) { return; }

    const phone = phoneInput.value.trim();
    const password = passwordInput.value.trim();

    if (!phone || !password) {
      error.textContent = "Please enter your Node ID and Passkey.";
      return;
    }

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: phone,
          password: password
        })
      });
      const data = await response.json();
      if (!response.ok) {
        error.textContent = data.detail || "Authentication failed.";
        return;
      }
      localStorage.setItem("authToken", data.token);
      app.setUser(data.user);
      app.appendActivity("oracle node authenticated", "success");
      window.location.href = "dashboard.html";
    } catch (e) {
      error.textContent = "Server error during login.";
    }
  }

  function selectPlan(plan, coverage) {
    app.setPlan({
      plan: plan,
      coverage: coverage
    });
    app.appendActivity("protection plan selected", "success");
    window.location.href = "dashboard.html";
  }

  function startDemo() {
    app.ensureDemoData();
    window.location.href = "signup.html";
  }

  function resetDemo(keepOnHome) {
    app.clearDemoData();
    app.ensureDemoData();
    if (keepOnHome) {
      window.location.href = "index.html";
    }
  }

  function fillDemoProfile() {
    const demoUser = app.defaults.user;
    const n = document.getElementById("name");
    const ph = document.getElementById("phone");
    const pw = document.getElementById("password");
    const pl = document.getElementById("platform");
    if(n) n.value = demoUser.name;
    if(ph) ph.value = demoUser.phone;
    if(pw) pw.value = "demo123";
    if(pl) pl.value = demoUser.platform;
  }

  function fillDemoLogin() {
    const ph = document.getElementById("loginPhone");
    const pw = document.getElementById("loginPassword");
    if(ph) ph.value = "9876543210";
    if(pw) pw.value = "demo123";
  }

  function hydrateSignup() {
    const nameInput = document.getElementById("name");
    const phoneInput = document.getElementById("phone");
    const platformInput = document.getElementById("platform");

    if (!nameInput || !phoneInput || !platformInput) {
      return;
    }

    const user = app.getUser();
    nameInput.value = user.name || "";
    phoneInput.value = user.phone || "";
    platformInput.value = user.platform || "Swiggy";
  }

  document.addEventListener("DOMContentLoaded", function () {
    app.ensureDemoData();
    hydrateSignup();
  });

  window.saveUser = saveUser;
  window.loginUser = loginUser;
  window.selectPlan = selectPlan;
  window.startDemo = startDemo;
  window.resetDemo = resetDemo;
  window.fillDemoProfile = fillDemoProfile;
  window.fillDemoLogin = fillDemoLogin;
})();
