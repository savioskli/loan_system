// Form validation and field handling
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dynamicForm');
    const clientTypeSelect = document.getElementById('client_type');
    
    // Real-time field validation
    function validateField(field) {
        const fieldValue = field.value.trim();
        const fieldName = field.getAttribute('name');
        const fieldType = field.type;
        const validationRules = JSON.parse(field.getAttribute('data-validation-rules') || '{}');
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !fieldValue) {
            isValid = false;
            errorMessage = validationRules.custom_message || 'This field is required';
            return { isValid, errorMessage };
        }

        // Skip further validation if field is empty and not required
        if (!fieldValue && !field.hasAttribute('required')) {
            return { isValid, errorMessage };
        }

        // Length validations
        if (validationRules.min_length && fieldValue.length < validationRules.min_length) {
            isValid = false;
            errorMessage = `Minimum length is ${validationRules.min_length} characters`;
            return { isValid, errorMessage };
        }

        if (validationRules.max_length && fieldValue.length > validationRules.max_length) {
            isValid = false;
            errorMessage = `Maximum length is ${validationRules.max_length} characters`;
            return { isValid, errorMessage };
        }

        // Pattern validation
        if (validationRules.pattern && !new RegExp(validationRules.pattern).test(fieldValue)) {
            isValid = false;
            errorMessage = validationRules.custom_message || 'Invalid format';
            return { isValid, errorMessage };
        }

        // Type-specific validations
        switch(fieldType) {
            case 'tel':
                if (!validatePhone(fieldValue)) {
                    isValid = false;
                    errorMessage = 'Invalid phone number format. Use +254 or 0 prefix followed by 9 digits';
                }
                break;

            case 'email':
                if (!validateEmail(fieldValue)) {
                    isValid = false;
                    errorMessage = 'Invalid email format';
                }
                break;

            case 'number':
            case 'range':
                const numValue = parseFloat(fieldValue);
                if (validationRules.min_value !== undefined && numValue < validationRules.min_value) {
                    isValid = false;
                    errorMessage = `Value must be at least ${validationRules.min_value}`;
                }
                if (validationRules.max_value !== undefined && numValue > validationRules.max_value) {
                    isValid = false;
                    errorMessage = `Value must be at most ${validationRules.max_value}`;
                }
                if (validationRules.step) {
                    const step = parseFloat(validationRules.step);
                    if ((numValue % step) !== 0) {
                        isValid = false;
                        errorMessage = `Value must be in increments of ${step}`;
                    }
                }
                break;

            case 'date':
                const dateValue = new Date(fieldValue);
                if (validationRules.min_date && dateValue < new Date(validationRules.min_date)) {
                    isValid = false;
                    errorMessage = `Date must be after ${validationRules.min_date}`;
                }
                if (validationRules.max_date && dateValue > new Date(validationRules.max_date)) {
                    isValid = false;
                    errorMessage = `Date must be before ${validationRules.max_date}`;
                }
                break;

            default:
                // Custom field validations
                if (fieldName === 'id_number') {
                    const idType = document.querySelector('[name="id_type"]')?.value;
                    if (!validateIdNumber(fieldValue, idType)) {
                        isValid = false;
                        errorMessage = `Invalid ${idType} format`;
                    }
                }
        }

        // Dependency validation
        if (validationRules.depends_on) {
            const dependentField = document.querySelector(`[name="${validationRules.depends_on.field}"]`);
            if (dependentField) {
                const dependentValue = dependentField.value;
                if (!validationRules.depends_on.values.includes(dependentValue)) {
                    isValid = false;
                    errorMessage = `This field depends on ${validationRules.depends_on.field}`;
                }
            }
        }

        // Update UI
        const feedbackDiv = field.nextElementSibling?.classList.contains('feedback') 
            ? field.nextElementSibling 
            : (() => {
                const div = document.createElement('div');
                div.className = 'feedback text-sm mt-1';
                field.parentNode.insertBefore(div, field.nextSibling);
                return div;
            })();

        if (!isValid) {
            field.classList.add('border-red-500');
            field.classList.remove('border-green-500');
            feedbackDiv.className = 'feedback text-sm mt-1 text-red-600';
            feedbackDiv.textContent = errorMessage;
        } else if (fieldValue) {
            field.classList.add('border-green-500');
            field.classList.remove('border-red-500');
            feedbackDiv.className = 'feedback text-sm mt-1 text-green-600';
            feedbackDiv.textContent = 'Looks good!';
        } else {
            field.classList.remove('border-red-500', 'border-green-500');
            feedbackDiv.textContent = '';
        }

        return { isValid, errorMessage };
    }

    // Helper validation functions
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validatePhone(phone) {
        // Supports formats: +254XXXXXXXXX, 0XXXXXXXXX
        const phoneRegex = /^(?:\+254|0)\d{9}$/;
        return phoneRegex.test(phone);
    }

    function validateIdNumber(value, idType) {
        switch(idType) {
            case 'National ID':
                return /^\d{8}$/.test(value);
            case 'Passport':
                return /^[A-Z]\d{7}$/.test(value);
            case 'Alien ID':
                return /^\d{9}$/.test(value);
            case 'Military ID':
                return /^[A-Z]\d{8}$/.test(value);
            default:
                return true;
        }
    }

    // Handle dependent fields
    function updateDependentFields(parentField) {
        const parentValue = parentField.value;
        const dependentFields = document.querySelectorAll(`[data-depends-on="${parentField.id}"]`);
        
        dependentFields.forEach(field => {
            // Store current selection
            const currentSelection = field.value;
            
            // Clear existing options
            field.innerHTML = `<option value="">${field.getAttribute('placeholder') || 'Select an option'}</option>`;
            
            if (parentValue) {
                // Get all options from the data attribute
                const allOptions = JSON.parse(field.getAttribute('data-options') || '[]');
                
                // Filter options based on parent value
                const filteredOptions = allOptions.filter(option => {
                    if (option.client_types) {
                        return option.client_types.includes(parentValue);
                    }
                    return true;
                });
                
                // Add filtered options
                filteredOptions.forEach(option => {
                    const optElement = document.createElement('option');
                    optElement.value = option.value;
                    optElement.textContent = option.label;
                    field.appendChild(optElement);
                });
                
                // Restore previous selection if it's still valid
                if (currentSelection) {
                    const options = Array.from(field.options);
                    const hasOption = options.some(opt => opt.value === currentSelection);
                    if (hasOption) {
                        field.value = currentSelection;
                    }
                }
            }
            
            // Trigger change event to update any fields that depend on this one
            field.dispatchEvent(new Event('change'));
        });
    }
    
    // Handle client type field restrictions
    function updateFieldVisibility() {
        const clientType = clientTypeSelect ? clientTypeSelect.value : '';
        
        // Update dependent fields when client type changes
        if (clientTypeSelect) {
            updateDependentFields(clientTypeSelect);
        }
        
        const formGroups = document.querySelectorAll('.form-group[data-client-types]');
        
        // Update field visibility based on client type
        formGroups.forEach(group => {
            const allowedTypes = JSON.parse(group.dataset.clientTypes || '[]');
            const inputs = group.querySelectorAll('input, select, textarea');
            
            if (allowedTypes.length === 0 || allowedTypes.includes(parseInt(clientType))) {
                group.style.display = 'block';
                inputs.forEach(input => {
                    input.disabled = false;
                });
            } else {
                group.style.display = 'none';
                inputs.forEach(input => {
                    input.disabled = true;
                    if (input.type !== 'radio') {
                        input.value = '';
                    }
                });
            }
        });
    }
    
    // Form submission handling
    if (form) {
        form.addEventListener('submit', function(e) {
            let hasError = false;
            const errors = [];
            
            // Get visible required fields
            const visibleRequiredFields = Array.from(form.querySelectorAll('.form-group[style*="block"] [required]'));
            
            visibleRequiredFields.forEach(field => {
                const fieldName = field.getAttribute('name');
                const fieldLabel = field.closest('.form-group').querySelector('label').textContent.trim();
                const fieldValue = field.value.trim();
                
                // Check required fields
                if (!fieldValue) {
                    errors.push(`${fieldLabel} is required`);
                    hasError = true;
                    return;
                }
                
                // Validate specific fields
                if (field.type === 'tel' && !validatePhone(fieldValue)) {
                    errors.push('Invalid phone number format. Use +254 or 0 prefix followed by 9 digits');
                    hasError = true;
                }
                
                if (field.type === 'email' && !validateEmail(fieldValue)) {
                    errors.push('Invalid email format');
                    hasError = true;
                }
                
                if (fieldName === 'id_number') {
                    const idType = form.querySelector('[name="id_type"]').value;
                    if (!validateIdNumber(fieldValue, idType)) {
                        errors.push('Invalid ID number format');
                        hasError = true;
                    }
                }
            });
            
            if (hasError) {
                e.preventDefault();
                // Show errors in a user-friendly way
                const errorContainer = document.getElementById('error-container') || 
                                    (() => {
                                        const div = document.createElement('div');
                                        div.id = 'error-container';
                                        div.className = 'bg-red-50 border-l-4 border-red-400 p-4 mb-4';
                                        form.insertBefore(div, form.firstChild);
                                        return div;
                                    })();
                
                errorContainer.innerHTML = `
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">Please correct the following errors:</h3>
                            <div class="mt-2 text-sm text-red-700">
                                <ul class="list-disc pl-5 space-y-1">
                                    ${errors.map(error => `<li>${error}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                `;
                
                // Scroll to error container
                errorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
    
    // Event listeners
    if (clientTypeSelect) {
        clientTypeSelect.addEventListener('change', () => {
            updateFieldVisibility();
            // Clear validation state when client type changes
            document.querySelectorAll('.form-group input, .form-group select, .form-group textarea').forEach(field => {
                field.classList.remove('border-red-500', 'border-green-500');
                const feedbackDiv = field.nextElementSibling;
                if (feedbackDiv?.classList.contains('feedback')) {
                    feedbackDiv.textContent = '';
                }
            });
        });
        // Initial field visibility update
        updateFieldVisibility();
    }

    // Add real-time validation to all form fields
    document.querySelectorAll('.form-group input, .form-group select, .form-group textarea').forEach(field => {
        field.addEventListener('blur', () => validateField(field));
        field.addEventListener('input', () => {
            if (field.classList.contains('border-red-500')) {
                validateField(field);
            }
        });
    });
    
    // Handle ID type change
    const idTypeSelect = document.querySelector('[name="id_type"]');
    const idNumberInput = document.querySelector('[name="id_number"]');
    if (idTypeSelect && idNumberInput) {
        idTypeSelect.addEventListener('change', function() {
            idNumberInput.value = ''; // Clear ID number when type changes
            
            // Update placeholder based on ID type
            if (this.value === 'National ID') {
                idNumberInput.placeholder = '8 digits (e.g., 12345678)';
            } else if (this.value === 'Passport') {
                idNumberInput.placeholder = 'Letter followed by 7 digits (e.g., A1234567)';
            } else {
                idNumberInput.placeholder = 'Enter ID number';
            }
        });
    }
    
    // Add event listeners for fields with dependencies
    document.querySelectorAll('select[data-depends-on]').forEach(field => {
        const parentField = document.getElementById(field.getAttribute('data-depends-on'));
        if (parentField) {
            parentField.addEventListener('change', () => {
                updateDependentFields(parentField);
            });
        }
    });
});
