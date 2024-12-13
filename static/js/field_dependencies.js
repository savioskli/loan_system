// Field Dependencies Management
class FieldDependencyManager {
    constructor(fieldId, moduleId) {
        this.fieldId = fieldId;
        this.moduleId = moduleId;
        
        // Initialize DOM elements with null checks
        this.modal = document.getElementById('dependency-modal');
        if (!this.modal) {
            console.warn('Dependency modal not found on this page');
            return;
        }

        this.dependentFieldSelect = document.getElementById('dependent-field-select');
        this.showValuesSelect = document.getElementById('show-values-select');
        this.addDependencyBtn = document.getElementById('add-dependency-btn');
        this.saveDependencyBtn = document.getElementById('save-dependency-btn');
        this.closeModalBtn = document.querySelector('.cancel-modal-btn');
        this.dependenciesList = document.getElementById('dependencies-container');

        // Initialize Choices.js for both selects
        if (this.dependentFieldSelect) {
            // Check if Choices is already initialized
            if (!this.dependentFieldSelect.classList.contains('choices__input')) {
                this.dependentFieldChoices = new Choices(this.dependentFieldSelect, {
                    searchEnabled: true,
                    itemSelectText: '',
                    removeItemButton: false,
                    placeholder: true,
                    placeholderValue: 'Select a field...'
                });
            }
        }

        if (this.showValuesSelect) {
            // Check if Choices is already initialized
            if (!this.showValuesSelect.classList.contains('choices__input')) {
                this.showValuesChoices = new Choices(this.showValuesSelect, {
                    searchEnabled: true,
                    itemSelectText: '',
                    removeItemButton: true,
                    placeholder: true,
                    placeholderValue: 'Select values...',
                    duplicateItemsAllowed: false
                });
            }
        }

        // Only initialize if we have the required elements
        if (this.dependentFieldSelect && this.showValuesSelect && 
            this.addDependencyBtn && this.saveDependencyBtn && 
            this.closeModalBtn && this.dependenciesList) {
            this.initializeEventListeners();
            this.loadExistingDependencies();
        } else {
            console.warn('Some required elements for field dependencies are missing');
        }
    }

    initializeEventListeners() {
        if (!this.modal) return;

        // Modal open/close handlers
        if (this.addDependencyBtn) {
            this.addDependencyBtn.addEventListener('click', () => this.openModal());
        }
        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeModal());
        }
        if (this.saveDependencyBtn) {
            this.saveDependencyBtn.addEventListener('click', () => this.saveDependency());
        }

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Handle ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal && !this.modal.classList.contains('hidden')) {
                this.closeModal();
            }
        });
    }

    async openModal() {
        if (!this.modal) return;
        
        try {
            // Load field options for the parent field (the field we're adding dependencies for)
            await this.loadFieldOptions(this.fieldId);

            // Load available fields for selection
            const response = await fetch(`/api/fields/${this.moduleId}?current_field_id=${this.fieldId}`);
            if (!response.ok) throw new Error('Failed to load fields');
            
            const fields = await response.json();
            
            // Get the Choices instance
            const dependentFieldChoices = this.dependentFieldSelect.choices || this.dependentFieldChoices;
            if (dependentFieldChoices) {
                dependentFieldChoices.setChoices(fields, 'value', 'label', true);
            }

            this.modal.classList.remove('hidden');
            this.resetModal();
        } catch (error) {
            console.error('Error loading fields:', error);
            alert('Failed to load available fields. Please try again.');
        }
    }

    closeModal() {
        if (!this.modal) return;
        this.modal.classList.add('hidden');
        this.resetModal();
    }

    resetModal() {
        if (!this.dependentFieldSelect || !this.showValuesSelect) return;

        // Get Choices instances
        const dependentFieldChoices = this.dependentFieldSelect.choices || this.dependentFieldChoices;
        const showValuesChoices = this.showValuesSelect.choices || this.showValuesChoices;

        if (dependentFieldChoices) {
            dependentFieldChoices.setChoiceByValue('');
        }
        // Don't reset show values as they should stay loaded from the parent field
    }

    async saveDependency() {
        const showValuesChoices = this.showValuesSelect.choices || this.showValuesChoices;
        const dependentFieldId = this.dependentFieldSelect.value;
        const showValues = showValuesChoices ? showValuesChoices.getValue().map(choice => choice.value) : [];

        if (!dependentFieldId || showValues.length === 0) {
            alert('Please select both a dependent field and show values.');
            return;
        }

        try {
            // Get CSRF token from meta tag
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            const response = await fetch('/api/field-dependencies', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    parent_field_id: this.fieldId,
                    dependent_field_id: dependentFieldId,
                    show_on_values: showValues
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to save dependency');
            }

            const data = await response.json();
            
            // Close modal first
            this.closeModal();
            
            // Then load dependencies and show success message
            await this.loadExistingDependencies();
            
            // Show success message
            const successMessage = document.createElement('div');
            successMessage.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-[9999] flex items-center shadow-lg toast-enter';
            successMessage.innerHTML = `
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span>Dependency added successfully!</span>
            `;
            document.body.appendChild(successMessage);

            // Remove the message after 3 seconds
            setTimeout(() => {
                successMessage.classList.add('toast-exit');
                setTimeout(() => successMessage.remove(), 300);
            }, 3000);
        } catch (error) {
            console.error('Error saving dependency:', error);
            alert('Failed to save dependency. Please try again.');
        }
    }

    async loadExistingDependencies() {
        if (!this.dependenciesList) return;

        try {
            const response = await fetch(`/api/field-dependencies/${this.fieldId}`);
            if (!response.ok) throw new Error('Failed to load dependencies');
            
            const dependencies = await response.json();
            this.renderDependencies(dependencies);
        } catch (error) {
            console.error('Error loading dependencies:', error);
            alert('Failed to load existing dependencies. Please try again.');
        }
    }

    renderDependencies(dependencies) {
        if (!this.dependenciesList) return;
        
        this.dependenciesList.innerHTML = '';
        
        if (dependencies.length === 0) {
            this.dependenciesList.innerHTML = `
                <div class="text-gray-500 text-sm italic">
                    No dependencies configured yet
                </div>
            `;
            return;
        }

        dependencies.forEach(dep => {
            const depElement = document.createElement('div');
            depElement.className = 'bg-white rounded-lg shadow p-4 mb-4 border border-gray-200';
            depElement.innerHTML = `
                <div class="flex justify-between items-center">
                    <div>
                        <div class="font-medium text-gray-700">
                            ${dep.dependent_field_label || dep.dependent_field_name}
                        </div>
                        <div class="text-sm text-gray-500">
                            Show when values: ${dep.show_on_values.join(', ')}
                        </div>
                    </div>
                    <button 
                        class="text-red-600 hover:text-red-800 focus:outline-none"
                        onclick="deleteDependency(${dep.id})"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            `;
            this.dependenciesList.appendChild(depElement);
        });
    }

    async loadFieldOptions(fieldId) {
        try {
            const response = await fetch(`/api/fields/${fieldId}/options`);
            if (!response.ok) throw new Error('Failed to load field options');
            
            const options = await response.json();
            
            // Get the Choices instance
            const showValuesChoices = this.showValuesSelect.choices || this.showValuesChoices;
            if (showValuesChoices) {
                showValuesChoices.clearChoices();
                if (options && options.length > 0) {
                    showValuesChoices.setChoices(options.map(option => ({
                        value: option.value,
                        label: option.label || option.value
                    })), 'value', 'label', true);
                } else {
                    console.warn('No options found for field:', fieldId);
                }
            }
        } catch (error) {
            console.error('Error loading field options:', error);
            alert('Failed to load field options. Please try again.');
        }
    }
}

// Global function to delete dependencies
async function deleteDependency(dependencyId) {
    if (!confirm('Are you sure you want to delete this dependency?')) {
        return;
    }

    try {
        // Get CSRF token from meta tag
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        const response = await fetch(`/api/field-dependencies/${dependencyId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to delete dependency');
        }

        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-[9999] flex items-center shadow-lg toast-enter';
        successMessage.innerHTML = `
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            <span>Dependency deleted successfully!</span>
        `;
        document.body.appendChild(successMessage);

        // Remove the message after 3 seconds
        setTimeout(() => {
            successMessage.classList.add('toast-exit');
            setTimeout(() => successMessage.remove(), 300);
        }, 3000);

        // Reload the dependencies list
        const fieldIdElement = document.querySelector('#field-id');
        if (fieldIdElement) {
            const fieldId = fieldIdElement.value;
            const moduleIdElement = document.querySelector('#module-id');
            if (moduleIdElement) {
                const moduleId = moduleIdElement.value;
                const manager = new FieldDependencyManager(fieldId, moduleId);
                await manager.loadExistingDependencies();
            }
        }
    } catch (error) {
        console.error('Error deleting dependency:', error);
        alert(error.message || 'Failed to delete dependency. Please try again.');
    }
}
