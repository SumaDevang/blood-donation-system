// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    // Enhanced Delete Confirmation
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const confirmDelete = confirm('Are you sure you want to delete this record? This action cannot be undone.');
            if (!confirmDelete) {
                e.preventDefault(); // Prevent the link from being followed
            }
        });
    });

    // Search/Filter Functionality for Tables
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search table...';
    searchInput.className = 'form-control mb-3';
    searchInput.style.maxWidth = '300px';

    // Insert search input before the table
    const table = document.querySelector('.table');
    if (table) {
        table.parentElement.insertBefore(searchInput, table);

        searchInput.addEventListener('input', () => {
            const filter = searchInput.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
});