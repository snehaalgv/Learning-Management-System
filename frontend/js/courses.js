let allCourses = [];

document.addEventListener('DOMContentLoaded', function() {
    loadCourses();
    setupSearch();
});

async function loadCourses() {
    const loading = document.getElementById('loading');
    const coursesContainer = document.getElementById('courses-container');
    const noCourses = document.getElementById('no-courses');

    loading.style.display = 'block';
    coursesContainer.innerHTML = '';

    try {
        const response = await fetch('http://localhost:8000/courses');
        const courses = await response.json();

        loading.style.display = 'none';

        if (courses.length === 0) {
            noCourses.style.display = 'block';
            return;
        }

        allCourses = courses;
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

    if (courses.length === 0) {
        noCourses.style.display = 'block';
        return;
    }

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
            <p class="course-description">${course.description}</p>
            <button class="enroll-btn" data-course-id="${course.id}">Enroll Now</button>
        </div>
    `;

    // Add event listener to enroll button
    const enrollBtn = card.querySelector('.enroll-btn');
    enrollBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        enrollInCourse(course.id, course.title);
    });

    return card;
}

function enrollInCourse(courseId, courseTitle) {
    // For now, just show an alert. In a real implementation, this would call an enroll API
    alert(`Enrollment functionality for "${courseTitle}" will be implemented soon!`);
    // TODO: Implement enrollment API call
    // fetch('http://localhost:8000/enroll', { method: 'POST', body: JSON.stringify({ courseId }) })
}

function setupSearch() {
    const searchInput = document.getElementById('search-input');

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm === '') {
            displayCourses(allCourses);
        } else {
            const filteredCourses = allCourses.filter(course =>
                course.title.toLowerCase().includes(searchTerm)
            );
            displayCourses(filteredCourses);
        }
    });
}