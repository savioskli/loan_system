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
        // TODO: Replace with actual API endpoint
        fetch(`/api/customers/search?q=${encodeURIComponent(term)}`)
            .then(response => response.json())
            .then(customers => {
                // Create and show dropdown
                showCustomerDropdown(customers);
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
                 data-name="${customer.name}">
                ${customer.name} (${customer.id})
            </div>
        `).join('');

        // Add click handlers
        dropdown.querySelectorAll('.customer-item').forEach(item => {
            item.addEventListener('click', function() {
                selectCustomer(
                    this.dataset.id,
                    this.dataset.name
                );
                dropdown.remove();
            });
        });
    }

    // Select customer
    function selectCustomer(id, name) {
        document.getElementById('selectedCustomerId').value = id;
        document.getElementById('selectedCustomerName').value = name;
        document.getElementById('customerNameDisplay').textContent = name;
        document.getElementById('customerIdDisplay').textContent = id;
        searchCustomer.value = name;
        customerInfo.classList.remove('hidden');
        
        // Load customer accounts
        loadCustomerAccounts(id);
    }

    // Load customer accounts
    function loadCustomerAccounts(customerId) {
        fetch(`/api/notifications/customers/${customerId}/accounts`)
            .then(response => response.json())
            .then(accounts => {
                const tbody = document.getElementById('accountsTableBody');
                tbody.innerHTML = accounts.map(account => `
                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td class="px-6 py-4">
                            <input type="radio" name="account_no" value="${account.account_no}" 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                        </td>
                        <td class="px-6 py-4">${account.account_no}</td>
                        <td class="px-6 py-4">${account.product_name}</td>
                        <td class="px-6 py-4">KES ${account.due_amount.toLocaleString()}</td>
                        <td class="px-6 py-4">${account.due_date}</td>
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
        fetch(`/user/api/guarantors/search?customer_id=${customerId}`)
            .then(response => response.json())
            .then(guarantors => {
                const tbody = document.getElementById('guarantorsTableBody');
                tbody.innerHTML = guarantors.map(guarantor => `
                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td class="px-6 py-4">
                            <input type="checkbox" name="guarantor_ids" value="${guarantor.id_no}" 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                        </td>
                        <td class="px-6 py-4">${guarantor.name}</td>
                        <td class="px-6 py-4">${guarantor.id_no}</td>
                        <td class="px-6 py-4">${guarantor.phone_no || '-'}</td>
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
