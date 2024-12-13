// Edit form validation and field handling
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('editForm');
    const clientTypeInput = document.querySelector('input[name="client_type"]');
    const purposeSelect = document.getElementById('purpose_of_visit');
    const countySelect = document.getElementById('county');
    const subCountySelect = document.getElementById('sub_county');
    const postalTownSelect = document.getElementById('postal_town');

    // Function to update purpose of visit options
    function updatePurposeOptions() {
        const clientTypeValue = clientTypeInput ? clientTypeInput.value : null;
        const currentPurpose = purposeSelect ? purposeSelect.value : null;
        
        if (purposeSelect && clientTypeValue) {
            // Store all options with their client types
            const allOptions = Array.from(purposeSelect.options).map(option => ({
                value: option.value,
                label: option.textContent,
                clientTypes: JSON.parse(option.dataset.clientTypes || '[]')
            }));
            
            // Filter options based on client type
            const availableOptions = allOptions.filter(option => 
                option.clientTypes.length === 0 || option.clientTypes.includes(clientTypeValue)
            );
            
            // Clear current options
            purposeSelect.innerHTML = '<option value="">Select Purpose of Visit</option>';
            
            // Add filtered options
            availableOptions.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                optionElement.dataset.clientTypes = JSON.stringify(option.clientTypes);
                purposeSelect.appendChild(optionElement);
            });
            
            // Restore previous selection if it's still valid
            if (currentPurpose) {
                const isValidPurpose = availableOptions.some(opt => opt.value === currentPurpose);
                if (isValidPurpose) {
                    purposeSelect.value = currentPurpose;
                }
            }
            
            // Enable/disable the select
            purposeSelect.disabled = availableOptions.length === 0;
        }
    }

    // Client type field restrictions
    function updateFieldVisibility() {
        const clientTypeValue = clientTypeInput ? clientTypeInput.value : null;
        const formGroups = document.querySelectorAll('.form-group[data-field-name]');

        formGroups.forEach(group => {
            try {
                const fieldName = group.dataset.fieldName;
                const allowedTypes = JSON.parse(group.dataset.clientTypes || '[]');
                console.log('Field:', fieldName, 'Allowed Types:', allowedTypes, 'Client Type:', clientTypeValue);
                
                // Individual client fields that should always show for individual clients
                const individualFields = ['first_name', 'middle_name', 'last_name', 'gender', 'id_type', 'serial_number'];
                const isIndividualClient = clientTypeValue === '1';
                const isIndividualField = individualFields.includes(fieldName);
                
                // Show field if:
                // 1. It has no restrictions (allowedTypes is empty array)
                // 2. It's specifically allowed for this client type
                // 3. For individual clients, show individual-specific fields
                const shouldShow = allowedTypes.length === 0 || 
                                 allowedTypes.includes(clientTypeValue) ||
                                 (isIndividualClient && isIndividualField);
                
                console.log('Should show:', shouldShow, 'Is Individual:', isIndividualClient, 'Is Individual Field:', isIndividualField);
                
                group.style.display = shouldShow ? 'block' : 'none';
                
                // Handle required fields
                const inputs = group.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    if (shouldShow) {
                        if (input.dataset.wasRequired) {
                            input.required = true;
                            delete input.dataset.wasRequired;
                        }
                    } else {
                        if (input.required) {
                            input.dataset.wasRequired = true;
                            input.required = false;
                        }
                    }
                });
            } catch (e) {
                console.error('Error parsing client types for field:', group.dataset.fieldName, e);
            }
        });

        // Update purpose options
        updatePurposeOptions();
    }

    // Initialize field visibility when page loads
    updateFieldVisibility();

    // Function to update sub-counties
    function updateSubCounties() {
        if (countySelect && subCountySelect) {
            const selectedCounty = countySelect.value;
            const currentSubCounty = subCountySelect.value;

            // Disable sub-county select if no county is selected
            subCountySelect.disabled = !selectedCounty;

            if (selectedCounty) {
                // Make AJAX request to get sub-counties
                fetch(`/user/get_sub_counties/${selectedCounty}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Clear current options
                            subCountySelect.innerHTML = '<option value="">Select Sub-County</option>';

                            // Add new options
                            data.data.forEach(subCounty => {
                                const option = document.createElement('option');
                                option.value = subCounty;
                                option.textContent = subCounty;
                                subCountySelect.appendChild(option);
                            });

                            // Restore previous selection if it exists in new options
                            if (currentSubCounty && data.data.includes(currentSubCounty)) {
                                subCountySelect.value = currentSubCounty;
                            }

                            // Enable the select
                            subCountySelect.disabled = false;
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching sub-counties:', error);
                    });
            } else {
                // Reset and disable the sub-county select
                subCountySelect.innerHTML = '<option value="">Select Sub-County</option>';
                subCountySelect.disabled = true;
            }
        }
    }

    // Initialize sub-county if county is already selected
    if (countySelect && countySelect.value) {
        updateSubCounties();
    }

    // County change listener
    if (countySelect) {
        countySelect.addEventListener('change', updateSubCounties);
    }

    // Validation functions
    function validatePhone(phone) {
        const phoneRegex = /^(?:\+254|0)\d{9}$/;
        return phoneRegex.test(phone);
    }

    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validateIdNumber(idNumber, idType) {
        switch(idType) {
            case 'National ID':
                return /^\d{8}$/.test(idNumber);
            case 'Passport':
                return /^[A-Z]\d{7}$/.test(idNumber);
            case 'Alien ID':
                return /^[A-Z]\d{8}$/.test(idNumber);
            case 'Military ID':
                return /^[A-Z]\d{6}$/.test(idNumber);
            default:
                return true;
        }
    }

    // Field validation
    function validateField(field) {
        const fieldValue = field.value.trim();
        const fieldName = field.getAttribute('name');
        const fieldType = field.type;
        let isValid = true;
        let errorMessage = '';

        if (field.hasAttribute('required') && !fieldValue) {
            isValid = false;
            errorMessage = 'This field is required';
        } else if (fieldValue) {
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
                default:
                    if (fieldName === 'id_number') {
                        const idType = document.querySelector('[name="id_type"]')?.value;
                        if (!validateIdNumber(fieldValue, idType)) {
                            isValid = false;
                            errorMessage = 'Invalid ID number format for the selected ID type';
                        }
                    }
                    break;
            }
        }

        // Update UI
        const formGroup = field.closest('.form-group');
        if (formGroup) {  
            const errorElement = formGroup.querySelector('.error-message') || 
                               (() => {
                                   const el = document.createElement('p');
                                   el.className = 'error-message mt-1 text-sm text-red-600';
                                   formGroup.appendChild(el);
                                   return el;
                               })();

            if (!isValid) {
                field.classList.add('border-red-300');
                field.classList.remove('border-gray-300');
                errorElement.textContent = errorMessage;
                errorElement.style.display = 'block';
            } else {
                field.classList.remove('border-red-300');
                field.classList.add('border-gray-300');
                errorElement.style.display = 'none';
            }
        }

        return isValid;
    }

    // Event listeners
    if (form) {
        // Form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            let hasError = false;

            // Validate all visible required fields
            form.querySelectorAll('input, select, textarea').forEach(field => {
                const formGroup = field.closest('.form-group');
                if (formGroup && formGroup.style.display !== 'none') {
                    if (!validateField(field)) {
                        hasError = true;
                    }
                }
            });

            if (!hasError) {
                form.submit();
            }
        });

        // Real-time validation
        form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => validateField(field));
            field.addEventListener('input', () => validateField(field));
            field.addEventListener('change', () => validateField(field));
        });
    }

    if (subCountySelect) {
        subCountySelect.disabled = !countySelect.value;
    }

    if (postalTownSelect) {
        postalTownSelect.disabled = false;
    }

    // ID type and number validation
    const idTypeSelect = document.querySelector('[name="id_type"]');
    const idNumberInput = document.querySelector('[name="id_number"]');
    if (idTypeSelect && idNumberInput) {
        idTypeSelect.addEventListener('change', () => {
            if (idNumberInput.value) {
                validateField(idNumberInput);
            }
        });
    }
});
