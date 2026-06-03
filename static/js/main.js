// General client-side scripting for Resume Booster
document.addEventListener("DOMContentLoaded", function() {
    console.log("[Resume Booster] Platform loaded successfully.");
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
