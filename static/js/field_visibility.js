// Field Visibility Management
class FieldVisibilityManager {
    constructor(fieldId) {
        this.fieldId = fieldId;
        this.hiddenFields = new Set();
    }

    async handleFieldChange(field) {
        const fieldValue = field.value;
        const fieldGroup = field.closest('.form-group');
        if (!fieldGroup) return;
        
        try {
            // Skip hidden fields and csrf_token
            if (field.type === 'hidden' || field.name === 'csrf_token' || field.name === 'client_id' || field.name === 'client_type') return;

            const response = await fetch(`/api/field-dependencies/${this.fieldId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch dependencies');
            }
            
            const dependencies = await response.json();
            for (const dep of dependencies) {
                const dependentField = document.querySelector(`[data-field-id="${dep.dependent_field}"]`);
                if (!dependentField) continue;

                const shouldShow = dep.show_values.includes(fieldValue);
                const input = dependentField.querySelector('input, select, textarea');
                if (!input) continue;

                if (shouldShow) {
                    // Store the current value before showing
                    if (this.hiddenFields.has(dep.dependent_field)) {
                        input.value = input.dataset.lastValue || '';
                        this.hiddenFields.delete(dep.dependent_field);
                    }
                    
                    // Show field with transition
                    dependentField.classList.remove('field-hidden');
                    setTimeout(() => {
                        dependentField.classList.remove('field-invisible');
                    }, 10);
                } else {
                    // Store the current value before hiding
                    if (!this.hiddenFields.has(dep.dependent_field)) {
                        input.dataset.lastValue = input.value;
                        this.hiddenFields.add(dep.dependent_field);
                    }
                    
                    // Hide field with transition
                    dependentField.classList.add('field-invisible');
                    setTimeout(() => {
                        dependentField.classList.add('field-hidden');
                        input.value = '';
                        // Trigger change event for cascading dependencies
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }, 300);
                }
            }
        } catch (error) {
            console.error('Error handling field dependencies:', error);
        }
    }
}

// Initialize field visibility for all form fields
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.form-group[data-field-id]').forEach(formGroup => {
        const fieldId = formGroup.dataset.fieldId;
        if (!fieldId) return;

        const manager = new FieldVisibilityManager(fieldId);
        const input = formGroup.querySelector('input, select, textarea');
        if (!input) return;

        input.addEventListener('change', () => manager.handleFieldChange(input));
        // Initial check for fields with values
        if (input.value) {
            manager.handleFieldChange(input);
        }
    });
});

// Add CSS classes for transitions
const style = document.createElement('style');
style.textContent = `
    .field-hidden {
        display: none !important;
    }
    .field-invisible {
        opacity: 0;
        height: 0;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    .form-group {
        transition: opacity 0.3s ease-in-out, height 0.3s ease-in-out, margin 0.3s ease-in-out, padding 0.3s ease-in-out;
    }
`;
document.head.appendChild(style);
