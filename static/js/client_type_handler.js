class ClientTypeHandler {
    constructor() {
        // Find the client type select field
        this.clientTypeSelect = document.querySelector('select[data-reference-id="1"]');
        console.log('Client type select:', this.clientTypeSelect);
        
        if (this.clientTypeSelect) {
            this.initializeHandler();
        } else {
            console.error('Client type select not found');
        }
    }

    initializeHandler() {
        console.log('Initializing client type handler');
        
        // Initial visibility setup
        this.updateFieldVisibility(this.clientTypeSelect.value);

        // Add change event listener
        this.clientTypeSelect.addEventListener('change', (e) => {
            console.log('Client type changed to:', e.target.value);
            this.updateFieldVisibility(e.target.value);
        });
    }

    updateFieldVisibility(selectedClientType) {
        console.log('Updating visibility for client type:', selectedClientType);
        
        // Get all form fields
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const field = group.querySelector('input, select, textarea');
            if (!field || !field.dataset.clientTypes) return;

            try {
                const allowedTypes = JSON.parse(field.dataset.clientTypes);
                console.log('Field:', field.id, 'Allowed types:', allowedTypes);
                
                // Show field if it has no restrictions or if selected type is in allowed types
                const shouldShow = !allowedTypes.length || allowedTypes.includes(selectedClientType);
                
                // Update visibility
                group.style.display = shouldShow ? '' : 'none';
                
                // Update required attribute
                if (shouldShow) {
                    // Check if field was originally required
                    if (field.dataset.isRequired === 'true') {
                        field.required = true;
                    }
                } else {
                    field.required = false;
                    // Clear value
                    if (field.tagName === 'SELECT') {
                        field.value = '';
                    } else {
                        field.value = '';
                    }
                }
                
                console.log('Field:', field.id, 'Visibility:', shouldShow);
            } catch (e) {
                console.error('Error parsing client types for field:', field.id, e);
            }
        });
    }
}

// Initialize the handler when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ClientTypeHandler();
});
