// System Reference Field Handler
class SystemReferenceHandler {
    constructor() {
        this.loadedFields = new Set();
    }

    async loadFieldOptions(field) {
        const referenceId = field.dataset.referenceId;
        
        if (!referenceId || this.loadedFields.has(field.id)) {
            return;
        }

        try {
            const response = await fetch(`/api/system-references/${referenceId}`);
            if (!response.ok) {
                throw new Error('Failed to load reference data');
            }

            const data = await response.json();
            
            // Clear existing options except the first one (placeholder)
            while (field.options.length > 1) {
                field.remove(1);
            }

            // Add new options
            data.forEach(item => {
                const option = new Option(item.label, item.value);
                field.add(option);
            });

            // Mark as loaded
            this.loadedFields.add(field.id);

            // If there was a previously selected value, restore it
            const previousValue = field.dataset.previousValue;
            if (previousValue) {
                field.value = previousValue;
            }

        } catch (error) {
            console.error('Error loading system reference data:', error);
            // Add an error option
            const errorOption = new Option('Error loading options', '');
            field.add(errorOption);
        }
    }

    init() {
        // Find all system reference fields
        const systemFields = document.querySelectorAll('select[data-is-system-field="true"]');
        
        // Load options for each field
        systemFields.forEach(field => {
            // Store current value if any
            if (field.value) {
                field.dataset.previousValue = field.value;
            }
            
            // Remove disabled attribute to make it interactive
            field.disabled = false;
            
            // Load the options
            this.loadFieldOptions(field);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const handler = new SystemReferenceHandler();
    handler.init();
});
