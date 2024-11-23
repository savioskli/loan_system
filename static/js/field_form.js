$(document).ready(function() {
    // Function to add new option row
    function addOptionRow(label = '', value = '') {
        const optionRow = `
            <div class="option-row grid grid-cols-2 gap-4">
                <div>
                    <input type="text" 
                        name="options-label[]" 
                        value="${label}" 
                        class="mt-1 block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" 
                        placeholder="Option Label">
                </div>
                <div class="flex">
                    <input type="text" 
                        name="options-value[]" 
                        value="${value}" 
                        class="mt-1 block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" 
                        placeholder="Option Value">
                    <button type="button" class="remove-option ml-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        $('#options-container').append(optionRow);
    }

    // Add option button click handler
    $('#add-option').click(function() {
        addOptionRow();
    });

    // Remove option button click handler
    $(document).on('click', '.remove-option', function() {
        $(this).closest('.option-row').remove();
    });

    // Show/hide options section based on field type
    function toggleOptionsSection() {
        const fieldType = $('#field_type').val();
        if (['select', 'radio', 'checkbox'].includes(fieldType)) {
            $('.field-options-section').show();
            // If no options exist, add an empty one
            if ($('.option-row').length === 0) {
                addOptionRow();
            }
        } else {
            $('.field-options-section').hide();
        }
    }

    // Field type change handler
    $('#field_type').change(toggleOptionsSection);
    
    // Initialize on page load
    toggleOptionsSection();

    // Initialize Select2 for client type restrictions
    $('#client_type_restrictions').select2({
        placeholder: 'Select client types',
        allowClear: true
    });
});
