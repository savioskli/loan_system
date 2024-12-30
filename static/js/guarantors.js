document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let currentPage = 1;
    const itemsPerPage = 10;
    let guarantorsData = [];

    // DOM elements
    const searchInput = document.getElementById('searchGuarantor');
    const filterStatus = document.getElementById('filterStatus');
    const filterIncome = document.getElementById('filterIncome');
    const tableBody = document.getElementById('guarantorsTableBody');
    const syncButton = document.getElementById('syncGuarantorsBtn');

    // Load guarantors
    function loadGuarantors() {
        fetch('/user/api/guarantors/search' + buildQueryString())
            .then(response => response.json())
            .then(data => {
                guarantorsData = data;
                updateTable();
                updatePagination();
            })
            .catch(error => {
                console.error('Error loading guarantors:', error);
                showNotification('Error', 'Failed to load guarantors', 'error');
            });
    }

    // Build query string from filters
    function buildQueryString() {
        const params = new URLSearchParams();
        if (searchInput.value) params.append('q', searchInput.value);
        if (filterStatus.value) params.append('status', filterStatus.value);
        if (filterIncome.value) params.append('income', filterIncome.value);
        if (params.toString()) {
            return '?' + params.toString();
        } else {
            return '';
        }
    }

    // Update table with current data
    function updateTable() {
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = guarantorsData.slice(start, end);

        tableBody.innerHTML = pageData.map(guarantor => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div>
                            <div class="text-sm font-medium text-gray-900 dark:text-white">
                                ${guarantor.name}
                            </div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900 dark:text-white">${guarantor.id_no}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900 dark:text-white">${guarantor.customer_name}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-300">${guarantor.customer_id}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900 dark:text-white">
                        KES ${guarantor.monthly_income.toLocaleString()}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        guarantor.status === 'Active' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                    }">
                        ${guarantor.status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button onclick="viewGuarantor('${guarantor.guarantor_no}')" 
                            class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">
                        View Details
                    </button>
                </td>
            </tr>
        `).join('');

        // Update pagination info
        document.getElementById('startIndex').textContent = start + 1;
        document.getElementById('endIndex').textContent = Math.min(end, guarantorsData.length);
        document.getElementById('totalItems').textContent = guarantorsData.length;
    }

    // Update pagination controls
    function updatePagination() {
        const totalPages = Math.ceil(guarantorsData.length / itemsPerPage);
        const pagination = document.getElementById('pagination');
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <button onclick="changePage(${currentPage - 1})" 
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${currentPage === 1 ? 'cursor-not-allowed opacity-50' : ''}"
                    ${currentPage === 1 ? 'disabled' : ''}>
                <span class="sr-only">Previous</span>
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        // Page numbers
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }

        if (startPage > 1) {
            paginationHTML += `
                <button onclick="changePage(1)"
                        class="bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                    1
                </button>
            `;
            if (startPage > 2) {
                paginationHTML += `
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                        ...
                    </span>
                `;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            if (i === currentPage) {
                paginationHTML += `
                    <button aria-current="page" 
                            class="z-10 bg-indigo-50 border-indigo-500 text-indigo-600 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                        ${i}
                    </button>
                `;
            } else {
                paginationHTML += `
                    <button onclick="changePage(${i})"
                            class="bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                        ${i}
                    </button>
                `;
            }
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                        ...
                    </span>
                `;
            }
            paginationHTML += `
                <button onclick="changePage(${totalPages})"
                        class="bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                    ${totalPages}
                </button>
            `;
        }

        // Next button
        paginationHTML += `
            <button onclick="changePage(${currentPage + 1})"
                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${currentPage === totalPages ? 'cursor-not-allowed opacity-50' : ''}"
                    ${currentPage === totalPages ? 'disabled' : ''}>
                <span class="sr-only">Next</span>
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        pagination.innerHTML = paginationHTML;
    }

    // Change page
    window.changePage = function(page) {
        const totalPages = Math.ceil(guarantorsData.length / itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
            updateTable();
            updatePagination();
        }
    };

    // Event listeners
    searchInput.addEventListener('input', debounce(() => {
        currentPage = 1;
        loadGuarantors();
    }, 300));

    filterStatus.addEventListener('change', () => {
        currentPage = 1;
        loadGuarantors();
    });

    filterIncome.addEventListener('change', () => {
        currentPage = 1;
        loadGuarantors();
    });

    syncButton.addEventListener('click', () => {
        fetch('/user/api/guarantors/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNotification('Success', 'Guarantors synced successfully', 'success');
                loadGuarantors();
            } else {
                showNotification('Error', data.error || 'Failed to sync guarantors', 'error');
            }
        })
        .catch(error => {
            console.error('Error syncing guarantors:', error);
            showNotification('Error', 'Failed to sync guarantors', 'error');
        });
    });

    // View guarantor details
    window.viewGuarantor = function(guarantorNo) {
        window.location.href = `/user/guarantors/${guarantorNo}`;
    };

    // Show notification
    function showNotification(title, message, type = 'info') {
        const event = new CustomEvent('show-notification', {
            detail: { title, message, type }
        });
        window.dispatchEvent(event);
    }

    // Helper function for debouncing
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initial load
    loadGuarantors();
});
