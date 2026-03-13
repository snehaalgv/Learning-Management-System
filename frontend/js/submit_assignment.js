// Get parameters from URL
function getUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        assignmentId: urlParams.get('assignment_id'),
        studentId: urlParams.get('student_id'),
        courseId: urlParams.get('course_id')
    };
}

// Simple submitAssignment function as requested
async function submitAssignment() {
    try {
        // Step 1: Read the PDF file from input id="pdfFile"
        const fileInput = document.getElementById('pdf-file');
        const pdfFile = fileInput.files[0];

        if (!pdfFile) {
            alert('Please select a PDF file first!');
            return;
        }

        // Step 2: Create FormData
        const formData = new FormData();

        // Step 3: Append file, student_id, and assignment_id
        formData.append('file', pdfFile);

        // For demo purposes, using hardcoded values. In real app, get from form inputs or URL
        formData.append('student_id', '1');  // Replace with actual student ID
        formData.append('assignment_id', '1');  // Replace with actual assignment ID

        // Step 4: Send POST request using fetch()
        const response = await fetch('http://127.0.0.1:8000/student/submit-assignment', {
            method: 'POST',
            body: formData
        });

        // Check if request was successful
        if (response.ok) {
            // Step 5: Show alert after successful submission
            alert('Assignment submitted successfully!');
        } else {
            alert('Failed to submit assignment. Please try again.');
        }

    } catch (error) {
        console.error('Error submitting assignment:', error);
        alert('Error occurred while submitting assignment.');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const params = getUrlParams();

    if (!params.assignmentId || !params.studentId) {
        showError('Missing required parameters. Please go back and try again.');
        return;
    }

    // Load assignment details
    loadAssignmentDetails(params.assignmentId, params.courseId);

    // Setup form submission
    setupFormSubmission(params.assignmentId, params.studentId);
});

async function loadAssignmentDetails(assignmentId, courseId) {
    // For now, just show basic info. In a real implementation, you might fetch assignment details
    document.getElementById('assignment-title').textContent = `Assignment ${assignmentId}`;

    if (courseId) {
        document.getElementById('course-info').textContent = `Course ID: ${courseId}`;
    }
}

function setupFormSubmission(assignmentId, studentId) {
    const form = document.getElementById('submit-form');
    const submitBtn = document.getElementById('submit-btn');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const fileInput = document.getElementById('pdf-file');
        const file = fileInput.files[0];

        if (!file) {
            showError('Please select a PDF file to submit.');
            return;
        }

        // Validate file type
        if (file.type !== 'application/pdf') {
            showError('Only PDF files are allowed.');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            showError('File size must be less than 10MB.');
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            await submitAssignment(assignmentId, studentId, file);
        } catch (error) {
            console.error('Submission error:', error);
            showError('Failed to submit assignment. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Assignment';
        }
    });
}

async function submitAssignment(assignmentId, studentId, file) {
    const formData = new FormData();
    formData.append('assignment_id', assignmentId);
    formData.append('student_id', studentId);
    formData.append('pdf_file', file);

    const response = await fetch('http://localhost:8001/student/submit-assignment', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Submission failed');
    }

    const result = await response.json();

    // Hide form and show success message
    document.getElementById('submit-form').style.display = 'none';
    document.getElementById('assignment-info').style.display = 'none';
    document.getElementById('success-message').style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    // Hide error after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}