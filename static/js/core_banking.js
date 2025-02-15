document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    const fetchTablesBtn = document.getElementById('fetchTablesBtn');
    const tablesContainer = document.getElementById('tablesContainer');
    const tablesList = document.getElementById('tablesList');
    const selectedTablesList = document.getElementById('selectedTablesList');

    // Get form configuration
    function getFormConfig() {
        return {
            server_url: document.querySelector('input[name="server_url"]').value,
            port: document.querySelector('input[name="port"]').value,
            database: document.querySelector('input[name="database"]').value,
            username: document.querySelector('input[name="username"]').value,
            password: document.querySelector('input[name="password"]').value,
            api_key: document.querySelector('input[name="api_key"]').value
        };
    }

    // Show notification
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

    // Display tables in the UI
    function displayTables(tables, selectedTables = []) {
        // Create containers if they don't exist
        let tablesContainer = document.getElementById('tablesContainer');
        if (!tablesContainer) {
            // Create the tables container
            tablesContainer = document.createElement('div');
            tablesContainer.id = 'tablesContainer';
            tablesContainer.className = 'bg-gray-50 dark:bg-gray-700 p-6 rounded-lg mt-6';

            // Add header with save button
            const headerDiv = document.createElement('div');
            headerDiv.className = 'flex justify-between items-center mb-6';
            
            const header = document.createElement('h3');
            header.className = 'text-lg font-medium text-gray-900 dark:text-white';
            header.textContent = 'Available Tables';
            headerDiv.appendChild(header);

            const saveButton = document.createElement('button');
            saveButton.type = 'button';
            saveButton.id = 'saveTablesBtn';
            saveButton.className = 'px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2';
            saveButton.innerHTML = '<i class="fas fa-save mr-2"></i>Save Selected Tables';
            headerDiv.appendChild(saveButton);

            tablesContainer.appendChild(headerDiv);

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
            // Convert selectedTables array to a Set of table names for faster lookup
            const selectedTableNames = new Set(selectedTables.map(t => t.name));

            tables.forEach(table => {
                const li = document.createElement('li');
                li.className = 'px-4 py-4 sm:px-6 hover:bg-gray-50 dark:hover:bg-gray-700';
                li.innerHTML = `
                    <div class="flex items-center space-x-4">
                        <input type="checkbox" 
                               id="table-${table.name}" 
                               name="selected_tables" 
                               value="${table.name}"
                               ${selectedTableNames.has(table.name) ? 'checked' : ''}
                               class="h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary">
                        <div class="flex-1">
                            <label for="table-${table.name}" class="block">
                                <span class="text-sm font-medium text-gray-900 dark:text-white">${table.name}</span>
                                ${table.description ? `
                                    <p class="mt-1 text-sm text-gray-500">${table.description}</p>
                                ` : ''}
                            </label>
                        </div>
                    </div>`;
                tablesList.appendChild(li);
            });
        }

        // Add save button click handler
        const saveButton = document.getElementById('saveTablesBtn');
        if (saveButton) {
            saveButton.addEventListener('click', async function() {
                const selectedTables = Array.from(document.querySelectorAll('input[name="selected_tables"]:checked')).map(checkbox => ({
                    name: checkbox.value,
                    description: tables.find(t => t.name === checkbox.value)?.description || ''
                }));

                if (selectedTables.length === 0) {
                    showNotification('error', 'Please select at least one table');
                    return;
                }

                try {
                    const response = await fetch('/api/integrations/core-banking/save-selected-tables', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ tables: selectedTables })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    if (result.success) {
                        showNotification('success', 'Selected tables saved successfully');
                    } else {
                        showNotification('error', result.message || 'Failed to save selected tables');
                    }
                } catch (error) {
                    console.error('Error saving tables:', error);
                    showNotification('error', 'Error saving tables: ' + error.message);
                }
            });
        }

        // Add search functionality
        const searchInput = document.getElementById('tableSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const tableItems = document.querySelectorAll('#tablesList li');
                
                tableItems.forEach(item => {
                    const tableName = item.querySelector('span').textContent.toLowerCase();
                    const tableDesc = item.querySelector('p')?.textContent.toLowerCase() || '';
                    
                    if (tableName.includes(searchTerm) || tableDesc.includes(searchTerm)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        }

        // Show the container
        tablesContainer.style.display = 'block';
    }

    // Load and display selected tables on page load
    (async function loadInitialTables() {
        try {
            // Get active configuration
            const configResponse = await fetch('/api/integrations/core-banking/get-active-config');
            const configResult = await configResponse.json();
            
            if (!configResult.success) {
                console.log('No active configuration found');
                return;
            }

            const config = configResult.config;
            
            // Fill in the form with active configuration
            document.querySelector('input[name="server_url"]').value = config.server_url;
            document.querySelector('input[name="port"]').value = config.port;
            document.querySelector('input[name="database"]').value = config.database;
            document.querySelector('input[name="username"]').value = config.username;
            
            // Fetch tables and selected tables
            const [tablesResponse, savedTablesResponse] = await Promise.all([
                fetch('/api/integrations/core-banking/fetch-tables', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(getFormConfig())
                }),
                fetch('/api/integrations/core-banking/get-selected-tables')
            ]);

            const result = await tablesResponse.json();
            const savedResult = await savedTablesResponse.json();
            
            if (result.success) {
                console.log('Tables fetched successfully:', result.tables);
                displayTables(result.tables, savedResult.success ? savedResult.tables : []);
            }
        } catch (error) {
            console.error('Error loading initial tables:', error);
        }
    })();

    // Handle fetch tables button click
    if (fetchTablesBtn) {
        fetchTablesBtn.addEventListener('click', async function() {
            try {
                const config = getFormConfig();
                console.log('Fetching tables with config:', config);
                
                const [tablesResponse, savedTablesResponse] = await Promise.all([
                    fetch('/api/integrations/core-banking/fetch-tables', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(config)
                    }),
                    fetch('/api/integrations/core-banking/get-selected-tables')
                ]);

                const result = await tablesResponse.json();
                const savedResult = await savedTablesResponse.json();
                
                if (result.success) {
                    console.log('Tables fetched successfully:', result.tables);
                    displayTables(result.tables, savedResult.success ? savedResult.tables : []);
                    showNotification('success', result.message || 'Tables fetched successfully');
                } else {
                    console.error('Failed to fetch tables:', result.message);
                    showNotification('error', result.message || 'Failed to fetch tables');
                }
            } catch (error) {
                console.error('Error fetching tables:', error);
                showNotification('error', 'Error fetching tables: ' + error.message);
            }
        });
    }

    // Test connection for edit system modal
    async function testEditConnection() {
        const systemId = document.getElementById('editSystemId').value;
        const baseUrl = document.getElementById('editBaseUrl').value;
        const port = document.getElementById('editPort').value;
        const authType = document.getElementById('editAuthType').value;
        
        // Get auth credentials based on type
        let authData = {};
        if (authType === 'basic') {
            authData = {
                username: document.getElementById('editUsername').value,
                password: document.getElementById('editPassword').value
            };
        } else if (authType === 'bearer') {
            authData = {
                token: document.getElementById('editToken').value
            };
        } else if (authType === 'api_key') {
            authData = {
                key_name: document.getElementById('editKeyName').value,
                key_value: document.getElementById('editKeyValue').value
            };
        } else if (authType === 'oauth2') {
            authData = {
                client_id: document.getElementById('editClientId').value,
                client_secret: document.getElementById('editClientSecret').value,
                token_url: document.getElementById('editTokenUrl').value
            };
        }
        
        // Show testing message
        const testStatusDiv = document.getElementById('editTestStatus');
        testStatusDiv.innerHTML = '<div class="alert alert-info">Testing connection...</div>';
        
        // Make test request
        fetch(`/admin/core-banking/${systemId}/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                base_url: baseUrl,
                port: port,
                auth_type: authType,
                ...authData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                testStatusDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            } else {
                testStatusDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
            }
        })
        .catch(error => {
            testStatusDiv.innerHTML = `<div class="alert alert-danger">Error testing connection: ${error}</div>`;
        });
    }

    // Add event listener for edit test connection button
    document.addEventListener('DOMContentLoaded', function() {
        const editTestConnectionBtn = document.getElementById('editTestConnectionBtn');
        if (editTestConnectionBtn) {
            editTestConnectionBtn.addEventListener('click', testEditConnection);
        }
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const formData = {
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
});
