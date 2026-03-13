// Simple login function as requested
async function loginUser() {
    // Step 1: Read email and password from input fields
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Step 2: Create the data object to send
    const loginData = {
        email: email,
        password: password
    };

    try {
        // Step 3: Send POST request to the login API using fetch()
        const response = await fetch('http://localhost:8001/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        // Step 4: Convert the response to JSON
        const data = await response.json();

        // Step 5: Check if login is successful
        if (!data.error) {
            // Show success alert and redirect to dashboard
            alert('Login Successful');
            window.location.href = 'dashboard.html';
        } else {
            // Show failure alert
            alert('Invalid email or password');
        }

    } catch (error) {
        console.error('Error during login:', error);
        alert('Network error occurred during login');
    }
}

document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    // Clear previous error message
    errorMessage.textContent = '';

    try {
        const response = await fetch('http://localhost:8001/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (data.error || data.detail) {
            // Login failed
            errorMessage.textContent = data.error || data.detail;
        } else {
            // Login successful
            // Store user information in localStorage
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.name);
            localStorage.setItem('user_role', data.role);

            if (data.role === 'student') {
                window.location.href = `student_dashboard.html?student_id=${data.user_id}`;
            } else if (data.role === 'educator') {
                window.location.href = `educator_dashboard.html?educator_id=${data.user_id}`;
            } else {
                errorMessage.textContent = 'Unknown user role';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        errorMessage.textContent = 'Network error. Please check your connection and try again.';
    }
});
