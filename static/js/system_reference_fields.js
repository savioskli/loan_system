// Handle system reference fields
function initializeSystemReferenceFields() {
    const systemReferenceFields = document.querySelectorAll('[data-field-type="system_reference"]');
    
    systemReferenceFields.forEach(field => {
        const referenceCode = field.dataset.referenceCode;
        const isCascading = field.dataset.isCascading === 'true';
        const parentFieldId = field.dataset.parentFieldId;
        
        // Initialize the field with choices.js
        const choices = new Choices(field, {
            searchEnabled: true,
            itemSelectText: '',
            removeItemButton: true
        });
        
        // Load initial values
        if (!isCascading || !parentFieldId) {
            loadReferenceValues(referenceCode, null, choices);
        }
        
        // Set up cascading relationship
        if (isCascading && parentFieldId) {
            const parentField = document.getElementById(parentFieldId);
            if (parentField) {
                parentField.addEventListener('change', (e) => {
                    const parentValue = e.target.value;
                    loadReferenceValues(referenceCode, parentValue, choices);
                });
            }
        }
    });
}

// Load reference values from the server
function loadReferenceValues(referenceCode, parentValue, choices) {
    const url = `/api/system-references/${referenceCode}` + 
                (parentValue ? `?parent_value=${parentValue}` : '');
                
    fetch(url)
        .then(response => response.json())
        .then(data => {
            choices.setChoices(data.map(item => ({
                value: item.value,
                label: item.label
            })), 'value', 'label', true);
        })
        .catch(error => console.error('Error loading reference values:', error));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSystemReferenceFields);
