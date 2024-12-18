document.addEventListener('DOMContentLoaded', function() {
    const fieldTypeSelect = document.querySelector('#field_type');
    const textValidations = document.querySelector('#text-validations');
    const numberValidations = document.querySelector('#number-validations');
    const dateValidations = document.querySelector('#date-validations');

    function updateValidationFields() {
        const selectedType = fieldTypeSelect.value;
        
        // Hide all validation sections first
        textValidations.classList.add('hidden');
        numberValidations.classList.add('hidden');
        dateValidations.classList.add('hidden');

        // Show relevant validation section based on field type
        switch(selectedType) {
            case 'text':
            case 'textarea':
            case 'email':
            case 'password':
            case 'tel':
                textValidations.classList.remove('hidden');
                break;
            case 'number':
                numberValidations.classList.remove('hidden');
                break;
            case 'date':
                dateValidations.classList.remove('hidden');
                break;
        }
    }

    // Update validation fields when field type changes
    if (fieldTypeSelect) {
        fieldTypeSelect.addEventListener('change', updateValidationFields);
        // Initial update on page load
        updateValidationFields();
    }
});
