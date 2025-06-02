// System Reference Field Handler
class SystemReferenceHandler {
    constructor() {
        this.loadedFields = new Set();
        this.activeDropdown = null;
    }

    makeSearchable(select) {
        // Create wrapper div
        const wrapper = document.createElement('div');
        wrapper.className = 'relative';
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        // Create dropdown container
        const dropdown = document.createElement('div');
        dropdown.className = 'absolute z-50 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-auto hidden';
        wrapper.appendChild(dropdown);

        // Create search input
        const searchDiv = document.createElement('div');
        searchDiv.className = 'p-2 border-b border-gray-200 sticky top-0 bg-white';
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Type to search...';
        searchInput.className = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        searchDiv.appendChild(searchInput);
        dropdown.appendChild(searchDiv);

        // Create options container
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'py-1';
        dropdown.appendChild(optionsDiv);

        // Store original options
        const options = Array.from(select.options).slice(1); // Skip placeholder

        // Create custom options
        const createOptions = (filterText = '') => {
            optionsDiv.innerHTML = '';
            options.forEach(option => {
                if (!filterText || option.text.toLowerCase().includes(filterText.toLowerCase())) {
                    const optionDiv = document.createElement('div');
                    optionDiv.className = 'px-4 py-2 hover:bg-blue-50 cursor-pointer';
                    optionDiv.textContent = option.text;
                    optionDiv.dataset.value = option.value;
                    if (option.value === select.value) {
                        optionDiv.classList.add('bg-blue-50');
                    }
                    optionDiv.addEventListener('click', () => {
                        select.value = option.value;
                        dropdown.classList.add('hidden');
                        this.activeDropdown = null;
                    });
                    optionsDiv.appendChild(optionDiv);
                }
            });
        };

        // Position dropdown based on available space
        const positionDropdown = () => {
            const selectRect = select.getBoundingClientRect();
            const spaceBelow = window.innerHeight - selectRect.bottom;
            const spaceAbove = selectRect.top;
            const dropdownHeight = Math.min(300, options.length * 40 + 60); // Approximate height

            // Reset classes
            dropdown.classList.remove('bottom-full', 'top-full', 'mb-1', 'mt-1');

            if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
                // Show above
                dropdown.classList.add('bottom-full', 'mb-1');
            } else {
                // Show below
                dropdown.classList.add('top-full', 'mt-1');
            }
        };

        // Show dropdown on select click
        select.addEventListener('mousedown', (e) => {
            e.preventDefault();
            if (this.activeDropdown && this.activeDropdown !== dropdown) {
                this.activeDropdown.classList.add('hidden');
            }
            dropdown.classList.toggle('hidden');
            if (!dropdown.classList.contains('hidden')) {
                positionDropdown();
                this.activeDropdown = dropdown;
                searchInput.value = '';
                createOptions();
                searchInput.focus();
            } else {
                this.activeDropdown = null;
            }
        });

        // Update position on scroll
        window.addEventListener('scroll', () => {
            if (!dropdown.classList.contains('hidden')) {
                positionDropdown();
            }
        }, true);

        // Filter options on search
        searchInput.addEventListener('input', () => {
            createOptions(searchInput.value);
        });

        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                dropdown.classList.add('hidden');
                if (this.activeDropdown === dropdown) {
                    this.activeDropdown = null;
                }
            }
        });
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

            // Make the select searchable
            this.makeSearchable(field);

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

        // Make all select fields searchable
        document.querySelectorAll('select.form-control:not([data-is-system-field="true"])').forEach(select => {
            if (select.options.length > 10) { // Only add search for selects with many options
                this.makeSearchable(select);
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const handler = new SystemReferenceHandler();
    handler.init();
});
