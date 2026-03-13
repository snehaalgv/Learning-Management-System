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
        // Step 3: Send POST request using fetch()
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        // Step 4: Convert response to JSON
        const data = await response.json();

        // Step 5: Log the response to console
        console.log('Login response:', data);

        // Step 6: Show alert if login is successful
        if (!data.error) {
            alert('Login successful!');
        } else {
            alert('Login failed: ' + data.error);
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
        const response = await fetch('http://localhost:8000/auth/login', {
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

        if (data.error) {
            // Login failed
            errorMessage.textContent = data.error;
        } else {
            // Login successful
            // Store user information in localStorage
            localStorage.setItem('student_id', data.user_id);
            localStorage.setItem('user_name', data.name);
            localStorage.setItem('user_role', data.role);

            if (data.role === 'student') {
                window.location.href = 'student_dashboard.html';
            } else if (data.role === 'educator') {
                window.location.href = 'educator_dashboard.html';
            } else {
                errorMessage.textContent = 'Unknown user role.';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        errorMessage.textContent = 'Network error. Please check your connection and try again.';
    }
});
