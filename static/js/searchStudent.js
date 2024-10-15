document.getElementById('searchButton').addEventListener('click', function() {
    // console.log('Search button clicked');
    const studentId = document.getElementById('searchStudentId').value;
    if (studentId) {
        fetchStudentDetails(studentId);
    } else {
        alert('Please enter a student ID');
    }
});

function fetchStudentDetails(studentId) {
    console.log('Fetching details for student ID:', studentId);
    fetch(`/students/${studentId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayStudentDetails(data.student);
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
}

function displayStudentDetails(student) {
    console.log('Displaying student details:', student);
    const studentDetailsDiv = document.getElementById('studentDetails');
    studentDetailsDiv.innerHTML = `
        <p>Name: ${student.name}</p>
        <p>Last Name: ${student.lastname}</p>
        <p>Student ID: ${student.student_id}</p>
        <p>Secondary School: ${student.secondary_school}</p>
        <p>Grade: ${student.grade}</p>
        <p>Section: ${student.section}</p>
    `;
}