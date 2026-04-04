(function () {
  const app = window.DeliveryProtect;

  function saveUser() {
    const nameInput = document.getElementById("name");
    const phoneInput = document.getElementById("phone");
    const platformInput = document.getElementById("platform");
    const error = document.getElementById("signupError");

    if (!nameInput || !phoneInput || !platformInput) {
      return;
    }

    const name = nameInput.value.trim();
    const phone = phoneInput.value.trim();

    if (!name || !phone) {
      error.textContent = "Please enter the partner name and phone number.";
      return;
    }

    app.setUser({
      name: name,
      phone: phone,
      platform: platformInput.value
    });

    app.appendActivity("partner profile created", "success");
    window.location.href = "policy.html";
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
    document.getElementById("name").value = demoUser.name;
    document.getElementById("phone").value = demoUser.phone;
    document.getElementById("platform").value = demoUser.platform;
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
  window.selectPlan = selectPlan;
  window.startDemo = startDemo;
  window.resetDemo = resetDemo;
  window.fillDemoProfile = fillDemoProfile;
})();
