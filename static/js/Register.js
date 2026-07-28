let nameInput = document.querySelector("#name");
let emailInput = document.querySelector("#email");
let pass = document.querySelector("#password");
let repass = document.querySelector("#Repassword");
let show = document.querySelector("#showButton");
let regBtn = document.querySelector("#reg");
let regForm = document.querySelector("form");

// Toggle show password
show.onchange = () => {
    pass.type = show.checked ? "text" : "password";
    repass.type = show.checked ? "text" : "password";
};

// Handle Registration API Request
regForm.onsubmit = async (event) => {
    event.preventDefault();

    let user = nameInput.value.trim();
    let mail = emailInput.value.trim();
    let passval = pass.value;
    let repassval = repass.value;

    if (!user || !mail || !passval || !repassval) {
        alert("Please fill in all fields.");
        return;
    }

    if (passval !== repassval) {
        alert("Passwords do not match. Please try again.");
        return;
    }

    regBtn.innerText = "Registering...";
    regBtn.disabled = true;

    try {
        let response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: user,
                email: mail,
                password: passval
            })
        });

        let data = await response.json();

        if (response.status === 201 && data.access_token) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            alert("Registration successful!");
            window.location.href = '/';
        } else {
            alert(data.message || "Registration failed. Please try again.");
        }
    } catch (err) {
        console.error("Registration error:", err);
        alert("Server error. Please try again later.");
    } finally {
        regBtn.innerText = "Register";
        regBtn.disabled = false;
    }
};
