document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const testConnectionBtn = document.getElementById('testConnectionBtn');
    const fetchTablesBtn = document.getElementById('fetchTablesBtn');
    const systemSelect = document.querySelector('select[name="core_banking_system"]');
    const tablesContainer = document.getElementById('tablesContainer');
    const tablesList = document.getElementById('tablesList');
    const selectedTablesList = document.getElementById('selectedTablesList');

    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Show/hide relevant fields based on selected system
    systemSelect.addEventListener('change', function() {
        const apiKeyField = document.querySelector('input[name="api_key"]').closest('.space-y-2');
        if (this.value === 'brnet') {
            apiKeyField.style.display = 'block';
        } else {
            apiKeyField.style.display = 'none';
        }
    });

    // Get form configuration
    function getFormConfig() {
        return {
            system_type: systemSelect.value,
            server_url: document.querySelector('input[name="server_url"]').value,
            port: document.querySelector('input[name="port"]').value,
            database: document.querySelector('input[name="database"]').value,
            username: document.querySelector('input[name="username"]').value,
            password: document.querySelector('input[name="password"]').value,
            api_key: document.querySelector('input[name="api_key"]').value
        };
    }

    // Test connection
    if (testConnectionBtn) {
        console.log('Test connection button found');
        testConnectionBtn.addEventListener('click', async function() {
            console.log('Test connection button clicked');
            try {
                const config = getFormConfig();
                console.log('Form config:', config);
                
                const response = await fetch('/api/integrations/core-banking/test-connection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(config)
                });
                console.log('Response received:', response);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                console.log('Response parsed:', result);
                
                if (result.success) {
                    console.log('Connection test successful');
                    showNotification('success', result.message || 'Connection test successful');
                } else {
                    console.error('Connection test failed:', result.message);
                    showNotification('error', result.message || 'Connection test failed');
                }
            } catch (error) {
                console.error('Error in test connection:', error);
                showNotification('error', 'Error testing connection: ' + error.message);
            }
        });
    } else {
        console.error('Test connection button not found');
    }

    // Fetch available tables
    if (fetchTablesBtn) {
        fetchTablesBtn.addEventListener('click', async function() {
            try {
                const config = getFormConfig();
                console.log('Fetching tables with config:', config);
                
                const response = await fetch('/api/integrations/core-banking/fetch-tables', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(config)
                });
                console.log('Response received:', response);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                console.log('Tables response:', result);

                if (result.success) {
                    console.log('Successfully retrieved tables:', result.tables);
                    displayTables(result.tables);
                    showNotification('success', 'Successfully retrieved tables');
                } else {
                    console.error('Failed to retrieve tables:', result.message);
                    showNotification('error', `Failed to retrieve tables: ${result.message}`);
                }
            } catch (error) {
                console.error('Error fetching tables:', error);
                showNotification('error', 'Error fetching tables: ' + error.message);
            }
        });
    }

    // Display tables in the UI
    function displayTables(tables) {
        // Create containers if they don't exist
        let tablesContainer = document.getElementById('tablesContainer');
        if (!tablesContainer) {
            // Create the tables container
            tablesContainer = document.createElement('div');
            tablesContainer.id = 'tablesContainer';
            tablesContainer.className = 'bg-gray-50 dark:bg-gray-700 p-6 rounded-lg mt-6';

            // Add header
            const header = document.createElement('h3');
            header.className = 'text-lg font-medium text-gray-900 dark:text-white mb-6';
            header.textContent = 'Available Tables';
            tablesContainer.appendChild(header);

            // Add search box
            const searchBox = document.createElement('div');
            searchBox.className = 'relative mb-4';
            searchBox.innerHTML = `
                <input type="text" id="tableSearch" placeholder="Search tables..." 
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary">
                <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                    <i class="fas fa-search text-gray-400"></i>
                </div>
            `;
            tablesContainer.appendChild(searchBox);

            // Append to form
            document.querySelector('form').appendChild(tablesContainer);
        }

        let tablesList = document.getElementById('tablesList');
        if (!tablesList) {
            const listContainer = document.createElement('div');
            listContainer.className = 'bg-white dark:bg-gray-800 shadow overflow-hidden rounded-md';
            tablesList = document.createElement('ul');
            tablesList.id = 'tablesList';
            tablesList.className = 'divide-y divide-gray-200 dark:divide-gray-700';
            listContainer.appendChild(tablesList);
            tablesContainer.appendChild(listContainer);
        }

        // Display tables
        tablesList.innerHTML = '';
        if (!tables || tables.length === 0) {
            tablesList.innerHTML = `
                <li class="px-4 py-4 sm:px-6">
                    <div class="text-sm text-gray-500">No tables available</div>
                </li>`;
        } else {
            tables.forEach(table => {
                const li = document.createElement('li');
                li.className = 'px-4 py-4 sm:px-6 hover:bg-gray-50 dark:hover:bg-gray-700';
                li.innerHTML = `
                    <div class="flex items-center justify-between">
                        <div>
                            <h4 class="text-sm font-medium text-gray-900 dark:text-white">${table.name}</h4>
                            <p class="mt-1 text-sm text-gray-500">${table.description || ''}</p>
                        </div>
                        <div>
                            <button type="button" class="select-table-btn inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary" data-table-name="${table.name}">
                                <i class="fas fa-plus mr-1"></i>
                                Select
                            </button>
                        </div>
                    </div>`;
                tablesList.appendChild(li);
            });
        }

        // Show the container by removing the hidden class if it exists
        if (tablesContainer.classList.contains('hidden')) {
            tablesContainer.classList.remove('hidden');
        }
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const formData = {
                system_type: systemSelect.value,
                server_url: document.querySelector('input[name="server_url"]').value,
                port: document.querySelector('input[name="port"]').value,
                database: document.querySelector('input[name="database"]').value,
                username: document.querySelector('input[name="username"]').value,
                password: document.querySelector('input[name="password"]').value,
                api_key: document.querySelector('input[name="api_key"]').value,
                sync_interval: document.querySelector('input[name="sync_interval"]').value,
                sync_loan_details: document.querySelector('input[name="sync_loan_details"]').checked,
                sync_payments: document.querySelector('input[name="sync_payments"]').checked,
                sync_customer_info: document.querySelector('input[name="sync_customer_info"]').checked
            };

            const response = await fetch('/api/integrations/core-banking/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('success', result.message);
                if (result.warning) {
                    showNotification('warning', result.warning);
                }
            } else {
                showNotification('error', result.message);
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            showNotification('error', 'Error saving configuration: ' + error.message);
        }
    });

    // Show notifications
    function showNotification(type, message, details = null) {
        let container = document.getElementById('notificationContainer');
        
        // Create container if it doesn't exist
        if (!container) {
            container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'mb-6';
            const form = document.querySelector('form');
            form.parentNode.insertBefore(container, form);
        }

        const notification = document.createElement('div');
        notification.className = `rounded-lg p-4 mb-4 text-sm ${
            type === 'success' 
                ? 'bg-green-100 text-green-700 border border-green-400'
                : type === 'error'
                ? 'bg-red-100 text-red-700 border border-red-400'
                : 'bg-yellow-100 text-yellow-700 border border-yellow-400'
        }`;
        
        let content = `<div class="flex items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'exclamation-triangle'} mr-2"></i>
            <span>${message}</span>
        </div>`;
        
        if (details) {
            content += `<div class="mt-2 ml-6 text-xs">${details}</div>`;
        }
        
        notification.innerHTML = content;
        container.appendChild(notification);
        
        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }

    // Trigger initial system selection check
    systemSelect.dispatchEvent(new Event('change'));
});
