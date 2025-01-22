// Function to open the configuration modal
function openConfigModal() {
    document.getElementById('config-modal').classList.remove('hidden');
    document.getElementById('modal-title').textContent = 'Add Configuration';
    document.getElementById('config-form').reset();
    document.getElementById('config-form').setAttribute('action', '/admin/credit-bureau/add');
}

// Function to close the configuration modal
function closeConfigModal() {
    document.getElementById('config-modal').classList.add('hidden');
}

// Function to edit a configuration
async function editConfig(configId) {
    try {
        const response = await fetch(`/admin/credit-bureau/${configId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch configuration');
        }
        
        const config = await response.json();
        
        // Update form fields
        document.getElementById('name').value = config.name;
        document.getElementById('provider').value = config.provider;
        document.getElementById('base_url').value = config.base_url;
        document.getElementById('api_key').value = config.api_key;
        document.getElementById('username').value = config.username;
        document.getElementById('is_active').checked = config.is_active;
        
        // Update form action and modal title
        document.getElementById('config-form').setAttribute('action', `/admin/credit-bureau/${configId}/edit`);
        document.getElementById('modal-title').textContent = 'Edit Configuration';
        
        // Show modal
        openConfigModal();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load configuration. Please try again.');
    }
}

// Function to toggle configuration status
async function toggleConfig(configId) {
    if (!confirm('Are you sure you want to change this configuration\'s status?')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/credit-bureau/${configId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to toggle configuration');
        }
        
        // Reload page to show updated status
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update configuration status. Please try again.');
    }
}

// Add form submission handler
document.getElementById('config-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        const formData = new FormData(this);
        const response = await fetch(this.action, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to save configuration');
        }
        
        // Reload page to show new/updated configuration
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save configuration. Please try again.');
    }
});
