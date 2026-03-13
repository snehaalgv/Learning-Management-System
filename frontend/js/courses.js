// Call loadCourses() when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadCourses();
});

// Simple function to load courses from the API
async function loadCourses() {
    try {
        // Step 1: Call the API using fetch()
        const response = await fetch('http://127.0.0.1:8000/courses');

        // Step 2: Convert the response to JSON
        const courses = await response.json();

        // Get the div where we want to display courses
        const courseListDiv = document.getElementById('courseList');

        // Clear any existing content
        courseListDiv.innerHTML = '';

        // Step 3: Display courses dynamically
        courses.forEach(course => {
            // Create a div for each course
            const courseDiv = document.createElement('div');
            courseDiv.className = 'course-item';

            // Add course title
            const titleElement = document.createElement('h3');
            titleElement.textContent = course.title;
            courseDiv.appendChild(titleElement);

            // Add course description
            const descriptionElement = document.createElement('p');
            descriptionElement.textContent = course.description;
            courseDiv.appendChild(descriptionElement);

            // Add Enroll button
            const enrollButton = document.createElement('button');
            enrollButton.textContent = 'Enroll';
            enrollButton.onclick = function() {
                alert('Enrolled in: ' + course.title);
            };
            courseDiv.appendChild(enrollButton);

            // Add the course div to the courseList div
            courseListDiv.appendChild(courseDiv);
        });

    } catch (error) {
        console.error('Error loading courses:', error);
        document.getElementById('courseList').innerHTML = '<p>Error loading courses. Please try again later.</p>';
    }
}