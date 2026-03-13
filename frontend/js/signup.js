document.getElementById('signup-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const errorMessage = document.getElementById('error-message');

    // Clear previous error message
    errorMessage.textContent = '';

    try {
        const response = await fetch('http://localhost:8001/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                role: role
            })
        });

        const data = await response.json();

        if (data.error || data.detail) {
            // Signup failed
            errorMessage.textContent = data.error || data.detail;
        } else {
            // Signup successful - show alert and redirect
            alert('Signup successful');
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Error:', error);
        errorMessage.textContent = 'Network error. Please check your connection and try again.';
    }
});