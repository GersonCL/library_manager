document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const bookSearch = document.getElementById('bookSearch');
    const searchResults = document.getElementById('searchResults');
    const selectedBooks = document.getElementById('selectedBooks');
    const selectedBooksInput = document.getElementById('selectedBooksInput');
    const loanForm = document.getElementById('loanForm');
    
    let selectedBooksArray = [];
    
    bookSearch.addEventListener('input', debounce(searchBooks, 300));
    
    function searchBooks() {
        const query = bookSearch.value;
        console.log('Searching for:', query);
        
        if (query.length < 2) {
            console.log('Query too short, not searching');
            return;
        }
        
        console.log('Fetching results for:', query);
        fetch(`/books/search?query=${encodeURIComponent(query)}`)
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(books => {
                console.log('Books received:', books);
                searchResults.innerHTML = books.map(book => `
                    <div class="book-result">
                        ${book.title} (${book.code}) - Disponibles: ${book.available}
                        <button class="btn btn-sm btn-primary" onclick="addBook(${book.id}, '${book.title}', ${book.available})">Agregar</button>
                    </div>
                `).join('');
            })
            .catch(error => {
                console.error('Error fetching books:', error);
            });
    }
    
    window.addBook = function(id, title, available) {
        console.log('Adding book:', id, title, available);
        const existingBook = selectedBooksArray.find(book => book.id === id);
        if (existingBook) {
            if (existingBook.quantity < available) {
                existingBook.quantity++;
                console.log('Increased quantity for existing book');
            } else {
                console.log('No more copies available');
                alert('No hay más copias disponibles de este libro.');
                return;
            }
        } else {
            selectedBooksArray.push({ id, title, quantity: 1 });
            console.log('Added new book to selection');
        }
        updateSelectedBooksList();
    }
    
    function updateSelectedBooksList() {
        console.log('Updating selected books list');
        selectedBooks.innerHTML = selectedBooksArray.map(book => `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${book.title} - Cantidad: ${book.quantity}
                <button class="btn btn-sm btn-danger" onclick="removeBook(${book.id})">Eliminar</button>
            </li>
        `).join('');
        selectedBooksInput.value = JSON.stringify(selectedBooksArray);
        console.log('Selected books:', selectedBooksArray);
    }
    
    window.removeBook = function(id) {
        console.log('Removing book:', id);
        selectedBooksArray = selectedBooksArray.filter(book => book.id !== id);
        updateSelectedBooksList();
    }
    
    function debounce(func, delay) {
        let timeoutId;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                console.log('Debounce triggered');
                func.apply(context, args);
            }, delay);
        };
    }
    
    loanForm.addEventListener('submit', function(e) {
        console.log('Form submitted');
        if (selectedBooksArray.length === 0) {
            console.log('No books selected, preventing submission');
            e.preventDefault();
            alert('Por favor, seleccione al menos un libro.');
        }
    });
});