document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('notificationForm');
    const searchCustomer = document.getElementById('searchCustomer');
    const customerInfo = document.getElementById('customerInfo');
    const accountSection = document.getElementById('accountSection');
    const guarantorSection = document.getElementById('guarantorSection');
    const notificationDetails = document.getElementById('notificationDetails');
    const fileList = document.getElementById('fileList');
    const attachmentsInput = document.getElementById('attachments');

    let selectedFiles = [];

    // Initialize customer search
    function initializeCustomerSearch() {
        $('#searchCustomer').select2({
            ajax: {
                url: 'http://localhost:5003/api/mock/customers/search',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function (data, params) {
                    params.page = params.page || 1;
                    return {
                        results: data.items,
                        pagination: {
                            more: data.has_more
                        }
                    };
                },
                cache: true
            },
            placeholder: 'Search for a customer...',
            minimumInputLength: 1,
            templateResult: formatCustomer,
            templateSelection: formatCustomer
        }).on('select2:select', function (e) {
            const customer = e.params.data;
            selectCustomer(customer);
        });
    }

    function formatCustomer(customer) {
        if (!customer.id) return customer.text;
        return $('<span>' + customer.text + '</span>');
    }

    // Initialize customer search on page load
    $(document).ready(function() {
        initializeCustomerSearch();
    });

    // Select customer
    function selectCustomer(customer) {
        document.getElementById('selectedCustomerId').value = customer.id;
        document.getElementById('selectedCustomerName').value = customer.name;
        document.getElementById('customerNameDisplay').textContent = customer.name;
        document.getElementById('customerIdDisplay').textContent = customer.id;
        customerInfo.classList.remove('hidden');
        
        // If accounts are included in the customer data, display them directly
        if (customer.accounts) {
            displayCustomerAccounts(customer.accounts);
        } else {
            // Fallback to loading accounts via API if not included
            loadCustomerAccounts(customer.id);
        }
        
        // If guarantors are included in the customer data, display them directly
        if (customer.guarantors) {
            displayGuarantors(customer.guarantors);
        } else {
            // Fallback to loading guarantors via API if not included
            loadGuarantors(customer.id);
        }
    }

    // Display customer accounts
    function displayCustomerAccounts(accounts) {
        const tbody = document.getElementById('accountsTableBody');
        tbody.innerHTML = accounts.map(account => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4">
                    <input type="radio" name="account_no" value="${account.account_number}" 
                           class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                </td>
                <td class="px-6 py-4">${account.account_number}</td>
                <td class="px-6 py-4">${account.product_name || 'Standard Loan'}</td>
                <td class="px-6 py-4">KES ${(account.due_amount || 0).toLocaleString()}</td>
                <td class="px-6 py-4">${account.due_date || 'N/A'}</td>
            </tr>
        `).join('');

        accountSection.classList.remove('hidden');

        // Add change handler for account selection
        tbody.querySelectorAll('input[name="account_no"]').forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    const selectedAccount = accounts.find(a => a.account_number === this.value);
                    if (selectedAccount) {
                        displayGuarantors(selectedAccount.guarantors || []);
                    }
                }
            });
        });
    }

    // Display guarantors
    function displayGuarantors(guarantors) {
        const tbody = document.getElementById('guarantorsTableBody');
        tbody.innerHTML = guarantors.map(guarantor => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4">
                    <input type="checkbox" name="guarantor_ids" value="${guarantor.id}" 
                           class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                </td>
                <td class="px-6 py-4">${guarantor.name}</td>
                <td class="px-6 py-4">${guarantor.id_no || '-'}</td>
                <td class="px-6 py-4">${guarantor.phone || '-'}</td>
                <td class="px-6 py-4">${guarantor.email || '-'}</td>
            </tr>
        `).join('');

        guarantorSection.classList.remove('hidden');
        notificationDetails.classList.remove('hidden');

        // Add change handler for guarantor selection
        tbody.querySelectorAll('input[name="guarantor_ids"]').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateNotificationForm();
            });
        });
    }

    // Customer search with debounce
    let searchTimeout;
    searchCustomer.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const searchTerm = this.value.trim();
            if (searchTerm.length >= 3) {
                searchCustomers(searchTerm);
            }
        }, 300);
    });

    // Search customers
    function searchCustomers(term) {
        fetch(`http://localhost:5003/api/mock/customers/search?q=${encodeURIComponent(term)}&page=1`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                // Transform the response to match the expected format
                const items = data.customers.map(customer => ({
                    id: customer.id,
                    text: `${customer.name} (${customer.account_number})`
                }));
                showCustomerDropdown(items);
            })
            .catch(error => {
                console.error('Error searching customers:', error);
                showNotification('Error', 'Failed to search customers', 'error');
            });
    }

    // Show customer dropdown
    function showCustomerDropdown(customers) {
        let dropdown = document.getElementById('customerDropdown');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.id = 'customerDropdown';
            dropdown.className = 'absolute z-10 w-full bg-white rounded-md shadow-lg max-h-60 overflow-auto';
            searchCustomer.parentNode.appendChild(dropdown);
        }

        dropdown.innerHTML = customers.map(customer => `
            <div class="customer-item p-2 hover:bg-gray-100 cursor-pointer" 
                 data-id="${customer.id}" 
                 data-name="${customer.text.split('(')[0].trim()}">
                ${customer.text}
            </div>
        `).join('');

        // Add click handlers
        dropdown.querySelectorAll('.customer-item').forEach(item => {
            item.addEventListener('click', function() {
                selectCustomer({
                    id: this.dataset.id,
                    name: this.dataset.name
                });
                dropdown.remove();
            });
        });
    }

    // Load customer accounts
    function loadCustomerAccounts(customerId) {
        fetch(`http://localhost:5003/api/mock/customers/${customerId}/accounts`)
            .then(response => response.json())
            .then(data => {
                const accounts = data.accounts || [];
                const tbody = document.getElementById('accountsTableBody');
                tbody.innerHTML = accounts.map(account => `
                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td class="px-6 py-4">
                            <input type="radio" name="account_no" value="${account.account_number}" 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                        </td>
                        <td class="px-6 py-4">${account.account_number}</td>
                        <td class="px-6 py-4">${account.product_name || 'Standard Loan'}</td>
                        <td class="px-6 py-4">KES ${(account.due_amount || 0).toLocaleString()}</td>
                        <td class="px-6 py-4">${account.due_date || 'N/A'}</td>
                    </tr>
                `).join('');

                accountSection.classList.remove('hidden');

                // Add change handler for account selection
                tbody.querySelectorAll('input[name="account_no"]').forEach(radio => {
                    radio.addEventListener('change', function() {
                        if (this.checked) {
                            loadGuarantors(customerId, this.value);
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error loading accounts:', error);
                showNotification('Error', 'Failed to load customer accounts', 'error');
            });
    }

    // Load guarantors for selected account
    function loadGuarantors(customerId, accountNo) {
        fetch(`http://localhost:5003/api/mock/customers/${customerId}/guarantors`)
            .then(response => response.json())
            .then(data => {
                const guarantors = data.guarantors || [];
                const tbody = document.getElementById('guarantorsTableBody');
                tbody.innerHTML = guarantors.map(guarantor => `
                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td class="px-6 py-4">
                            <input type="checkbox" name="guarantor_ids" value="${guarantor.id}" 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                        </td>
                        <td class="px-6 py-4">${guarantor.name}</td>
                        <td class="px-6 py-4">${guarantor.id_no || '-'}</td>
                        <td class="px-6 py-4">${guarantor.phone || '-'}</td>
                        <td class="px-6 py-4">${guarantor.email || '-'}</td>
                    </tr>
                `).join('');

                guarantorSection.classList.remove('hidden');
                notificationDetails.classList.remove('hidden');

                // Add change handler for guarantor selection
                tbody.querySelectorAll('input[name="guarantor_ids"]').forEach(checkbox => {
                    checkbox.addEventListener('change', function() {
                        updateNotificationForm();
                    });
                });
            })
            .catch(error => {
                console.error('Error loading guarantors:', error);
                showNotification('Error', 'Failed to load guarantors', 'error');
            });
    }

    // Handle file selection
    attachmentsInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        selectedFiles = [...selectedFiles, ...files];
        updateFileList();
    });

    // Update file list display
    function updateFileList() {
        fileList.innerHTML = selectedFiles.map((file, index) => `
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-900 dark:text-white">${file.name}</span>
                <button type="button" data-index="${index}" class="text-red-600 hover:text-red-900">Remove</button>
            </div>
        `).join('');

        // Add remove handlers
        fileList.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', function() {
                selectedFiles.splice(this.dataset.index, 1);
                updateFileList();
            });
        });
    }

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        selectedFiles.forEach(file => {
            formData.append('attachments', file);
        });

        fetch('/api/notifications/create', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Success', data.message, 'success');
                // Reset form
                form.reset();
                selectedFiles = [];
                updateFileList();
                customerInfo.classList.add('hidden');
                accountSection.classList.add('hidden');
                guarantorSection.classList.add('hidden');
                notificationDetails.classList.add('hidden');
            } else {
                showNotification('Warning', data.message, 'warning');
            }
        })
        .catch(error => {
            console.error('Error creating notification:', error);
            showNotification('Error', 'Failed to create notification', 'error');
        });
    });

    // Helper function to show notifications
    function showNotification(title, message, type = 'info') {
        // TODO: Implement notification display
        console.log(`${type.toUpperCase()}: ${title} - ${message}`);
    }
});
