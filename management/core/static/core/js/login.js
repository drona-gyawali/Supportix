document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault(); // Prevent the default form submission
  
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
  
      try {
        const response = await fetch("/api/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });
  
        if (response.ok) {
          //meter Simulate login success by redirecting with a query para
          window.location.href = "/?welcome=true";
        } else {
          const errorData = await response.json();
          console.log(errorData)
          window.location.href="/?UnauthorizedAccess=True";
        }
      } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again.");
      }
    });
  });