// Get student ID from URL parameters
function getStudentId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('student_id');
}

document.addEventListener('DOMContentLoaded', function() {
    const studentId = getStudentId();

    if (!studentId) {
        alert('Student ID is required. Please login first.');
        window.location.href = 'login.html';
        return;
    }

    loadStudentCourses(studentId);
});

async function loadStudentCourses(studentId) {
    const loading = document.getElementById('loading');
    const coursesContainer = document.getElementById('courses-container');
    const noCourses = document.getElementById('no-courses');
    const totalCourses = document.getElementById('total-courses');

    loading.style.display = 'block';
    coursesContainer.innerHTML = '';

    try {
        const response = await fetch(`http://localhost:8000/student/my-courses/${studentId}`);
        const courses = await response.json();

        loading.style.display = 'none';

        // Update total courses count
        totalCourses.textContent = courses.length;

        if (courses.length === 0) {
            noCourses.style.display = 'block';
            return;
        }

        displayCourses(courses);

    } catch (error) {
        console.error('Error loading courses:', error);
        loading.style.display = 'none';
        noCourses.textContent = 'Error loading courses. Please try again later.';
        noCourses.style.display = 'block';
    }
}

function displayCourses(courses) {
    const coursesContainer = document.getElementById('courses-container');
    const noCourses = document.getElementById('no-courses');

    coursesContainer.innerHTML = '';
    noCourses.style.display = 'none';

    courses.forEach(course => {
        const courseCard = createCourseCard(course);
        coursesContainer.appendChild(courseCard);
    });
}

function createCourseCard(course) {
    const card = document.createElement('div');
    card.className = 'course-card';

    card.innerHTML = `
        <div class="course-header">
            <h3 class="course-title">${course.title}</h3>
        </div>
        <div class="course-content">
            <p class="course-description">${course.description || 'No description available.'}</p>
            <div class="course-actions">
                <button class="btn btn-primary" onclick="viewLectures(${course.id}, '${course.title}')">
                    View Lectures
                </button>
                <button class="btn btn-secondary" onclick="submitAssignment(${course.id}, '${course.title}')">
                    Submit Assignment
                </button>
            </div>
        </div>
    `;

    return card;
}

function viewLectures(courseId, courseTitle) {
    // TODO: Implement view lectures functionality
    alert(`View lectures for "${courseTitle}" - This feature will be implemented soon!`);
}

function submitAssignment(courseId, courseTitle) {
    // TODO: Implement submit assignment functionality
    alert(`Submit assignment for "${courseTitle}" - This feature will be implemented soon!`);
}