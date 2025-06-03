class ClientTypeHandler {
    constructor() {
        console.log('Initializing ClientTypeHandler');
        // Find the client type field
        this.clientTypeField = document.querySelector('select[name="client_type"]');
        console.log('Client type field:', this.clientTypeField);
        
        if (this.clientTypeField) {
            // Trigger initial visibility update immediately
            this.updateFieldVisibility(this.clientTypeField.value);
            this.initializeHandler();
        } else {
            console.error('Client type field not found');
        }
    }

    initializeHandler() {
        console.log('Setting up client type handler');
        
        // Initial visibility setup
        const initialValue = this.clientTypeField.value;
        console.log('Initial client type value:', initialValue);
        this.updateFieldVisibility(initialValue);

        // Add change event listener
        this.clientTypeField.addEventListener('change', (e) => {
            console.log('Client type changed to:', e.target.value);
            this.updateFieldVisibility(e.target.value);
        });
    }

    updateFieldVisibility(selectedClientType) {
        console.log('Updating field visibility for client type:', selectedClientType);
        
        // Get all form fields
        const formGroups = document.querySelectorAll('.form-group');
        console.log('Found form groups:', formGroups.length);
        
        formGroups.forEach(group => {
            const field = group.querySelector('input, select, textarea');
            if (!field) {
                console.log('No input field found in group');
                return;
            }
            
            if (field.name === 'client_type') {
                console.log('Skipping client type field itself');
                return;
            }

            const restrictions = field.dataset.clientTypeRestrictions;
            console.log('Field:', field.name, 'Restrictions:', restrictions);
            
            if (!restrictions) {
                console.log('No restrictions for field:', field.name);
                return;
            }

            try {
                const allowedTypes = JSON.parse(restrictions).map(String);
                console.log('Allowed types for', field.name + ':', allowedTypes);
                
                const shouldShow = !allowedTypes.length || allowedTypes.includes(selectedClientType);
                console.log('Should show', field.name + '?', shouldShow, '(selected:', selectedClientType + ')', '(allowed:', allowedTypes.join(',') + ')');
                
                // Update visibility
                group.style.display = shouldShow ? '' : 'none';
                console.log('Updated visibility for', field.name);
                
                // Update required attribute
                if (shouldShow) {
                    // Re-enable required if the field was originally required
                    if (field.dataset.isRequired === 'true') {
                        field.required = true;
                        console.log('Re-enabled required for:', field.name);
                    }
                } else {
                    // Remove required and clear value when hidden
                    field.required = false;
                    field.value = '';
                    console.log('Cleared value and removed required for:', field.name);
                }
            } catch (e) {
                console.error('Error parsing client type restrictions for field:', field.name, e);
            }
        });
    }
}

// Initialize the handler when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ClientTypeHandler();
});
