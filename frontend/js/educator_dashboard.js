// Get educator ID from URL parameters
function getEducatorId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('educator_id');
}

document.addEventListener('DOMContentLoaded', function() {
    const educatorId = getEducatorId();

    if (!educatorId) {
        alert('Educator ID is required. Please login first.');
        window.location.href = 'login.html';
        return;
    }

    loadEducatorDashboard(educatorId);
    loadEducatorCourses(educatorId);
});

async function loadEducatorDashboard(educatorId) {
    try {
        const response = await fetch(`http://localhost:8000/educator/dashboard/${educatorId}`);
        const data = await response.json();

        // Update stats
        document.getElementById('total-courses').textContent = data.courses_created;
        document.getElementById('total-submissions').textContent = data.total_assignment_submissions;

        // Calculate total enrollments
        const totalEnrollments = data.course_enrollments.reduce((sum, course) => sum + course.enrolled_students, 0);
        document.getElementById('total-enrollments').textContent = totalEnrollments;

    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadEducatorCourses(educatorId) {
    const loading = document.getElementById('loading');
    const coursesContainer = document.getElementById('courses-container');
    const noCourses = document.getElementById('no-courses');

    loading.style.display = 'block';
    coursesContainer.innerHTML = '';

    try {
        const response = await fetch(`http://localhost:8000/educator/dashboard/${educatorId}`);
        const data = await response.json();

        loading.style.display = 'none';

        if (data.course_enrollments.length === 0) {
            noCourses.style.display = 'block';
            return;
        }

        displayCourses(data.course_enrollments);

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
            <h3 class="course-title">${course.course_title}</h3>
        </div>
        <div class="course-content">
            <p class="course-description">Enrolled Students: ${course.enrolled_students}</p>
            <div class="course-actions">
                <button class="btn btn-primary" onclick="viewEnrollments(${course.course_id}, '${course.course_title}')">
                    View Enrollments
                </button>
                <button class="btn btn-secondary" onclick="manageAssignments(${course.course_id}, '${course.course_title}')">
                    Manage Assignments
                </button>
            </div>
        </div>
    `;

    return card;
}

function viewEnrollments(courseId, courseTitle) {
    // TODO: Implement view enrollments functionality
    alert(`View enrollments for "${courseTitle}" - This feature will be implemented soon!`);
}

function manageAssignments(courseId, courseTitle) {
    // TODO: Implement manage assignments functionality
    alert(`Manage assignments for "${courseTitle}" - This feature will be implemented soon!`);
}