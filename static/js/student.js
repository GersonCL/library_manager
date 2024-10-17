document.addEventListener('DOMContentLoaded', function() {
    const studentSearch = document.getElementById('studentSearch');
    const studentResults = document.getElementById('studentResults');
    const selectedStudentInput = document.getElementById('selectedStudentInput');

    if (studentSearch) {
        studentSearch.addEventListener('input', debounce(searchStudents, 300));
    }

    function searchStudents() {
        const query = studentSearch.value;
        if (query.length < 2) {
            studentResults.innerHTML = '';
            selectedStudentInput.value = '';
            return;
        }

        fetch(`/students/search?query=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(students => {
                studentResults.innerHTML = students.map(student => `
                    <div class="list-group-item list-group-item-action" onclick="selectStudent(${student.id}, '${student.name}', '${student.student_id}', ${student.books_borrowed})">
                        ${student.name} (${student.student_id})
                        <span class="float-end"> <strong>Libros prestados: ${student.books_borrowed}</strong></span>
                    </div>
                `).join('');
            })
            .catch(error => {
                console.error('Error:', error);
                studentResults.innerHTML = '<p>Error al buscar estudiantes. Por favor, intente de nuevo.</p>';
            });
    }

    window.selectStudent = function(id, name, studentId, booksBorrowed) {
        studentSearch.value = `${name} (${studentId}) - Libros prestados: ${booksBorrowed}`;
        selectedStudentInput.value = id;
        studentResults.innerHTML = '';
    }

    function debounce(func, delay) {
        let timeoutId;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(context, args), delay);
        };
    }
});