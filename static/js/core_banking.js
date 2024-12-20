document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const testConnectionBtn = document.querySelector('button[type="button"]:first-of-type');
    const testSyncBtn = document.querySelector('button[type="button"]:last-of-type');
    const systemSelect = document.querySelector('select[name="core_banking_system"]');

    // Show/hide relevant fields based on selected system
    systemSelect.addEventListener('change', function() {
        const apiKeyField = document.querySelector('input[name="api_key"]').closest('.space-y-2');
        if (this.value === 'brnet') {
            apiKeyField.style.display = 'block';
        } else {
            apiKeyField.style.display = 'none';
        }
    });

    // Test connection
    testConnectionBtn.addEventListener('click', async function() {
        try {
            const config = getFormConfig();
            const response = await fetch('/integrations/api/core-banking/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('success', 'Connection test successful');
            } else {
                showNotification('error', `Connection test failed: ${result.message}`);
            }
        } catch (error) {
            showNotification('error', 'Error testing connection: ' + error.message);
        }
    });

    // Test data sync
    testSyncBtn.addEventListener('click', async function() {
        try {
            const config = getFormConfig();
            const response = await fetch('/integrations/api/core-banking/test-sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('success', 'Data synchronization test successful', result.details);
            } else {
                showNotification('error', `Data synchronization test failed: ${result.message}`);
            }
        } catch (error) {
            showNotification('error', 'Error testing synchronization: ' + error.message);
        }
    });

    // Save configuration
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        try {
            const config = getFormConfig();
            const response = await fetch('/integrations/api/core-banking/save-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('success', 'Configuration saved successfully');
            } else {
                showNotification('error', `Failed to save configuration: ${result.message}`);
            }
        } catch (error) {
            showNotification('error', 'Error saving configuration: ' + error.message);
        }
    });

    function getFormConfig() {
        return {
            system_type: systemSelect.value,
            server_url: document.querySelector('input[name="server_url"]').value,
            port: document.querySelector('input[name="port"]').value,
            database: document.querySelector('input[name="database"]').value,
            username: document.querySelector('input[name="username"]').value,
            password: document.querySelector('input[name="password"]').value,
            api_key: document.querySelector('input[name="api_key"]').value,
            sync_interval: document.querySelector('input[name="sync_interval"]').value,
            sync_settings: {
                loan_details: document.querySelector('input[name="sync_loan_details"]').checked,
                payments: document.querySelector('input[name="sync_payments"]').checked,
                customer_info: document.querySelector('input[name="sync_customer_info"]').checked
            }
        };
    }

    function showNotification(type, message, details = null) {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`;

        let notificationContent = `<div class="flex items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2"></i>
            <div>
                <p class="font-medium">${message}</p>
                ${details ? `<ul class="mt-2 text-sm">
                    ${Object.entries(details).map(([key, value]) => `
                        <li>${key.replace('_', ' ').toUpperCase()}: ${value}</li>
                    `).join('')}
                </ul>` : ''}
            </div>
        </div>`;

        notificationDiv.innerHTML = notificationContent;
        document.body.appendChild(notificationDiv);

        setTimeout(() => {
            notificationDiv.remove();
        }, 5000);
    }

    // Trigger initial system selection check
    systemSelect.dispatchEvent(new Event('change'));
});
