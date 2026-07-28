let show = document.querySelector("#showPassword");
let pass = document.querySelector("#password");
let emailInput = document.querySelector("#email");
let loginBtn = document.querySelector("#log");
let loginForm = document.querySelector("form");

// Toggle show password
show.onchange = () => {
    pass.type = show.checked ? "text" : "password";
};

// Handle Login API Request
loginForm.onsubmit = async (event) => {
    event.preventDefault();

    let email = emailInput.value.trim();
    let password = pass.value;

    if (!email || !password) {
        alert("Please enter email and password.");
        return;
    }

    loginBtn.innerText = "Logging in...";
    loginBtn.disabled = true;

    try {
        let response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        });

        let data = await response.json();

        if (response.ok && data.access_token) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            window.location.href = '/';
        } else {
            alert(data.message || "Login failed. Please check your credentials.");
        }
    } catch (err) {
        console.error("Login error:", err);
        alert("Server error. Please try again later.");
    } finally {
        loginBtn.innerText = "Login";
        loginBtn.disabled = false;
    }
};