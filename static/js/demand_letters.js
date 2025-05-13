document.addEventListener('DOMContentLoaded', function() {
    // Initialize member select
    $(document).ready(function() {
        // CSRF Token Handling
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
        
        // Initialize the dropdowns when the modal is shown
        $('[data-modal-toggle="create-demand-letter-modal"], [data-modal-target="create-demand-letter-modal"]').on('click', function() {
            // Ensure modal is properly positioned before initializing dropdowns
            $('#create-demand-letter-modal').addClass('flex items-center justify-center');
            
            // Wait for modal to be fully visible before initializing
            setTimeout(function() {
                // Initialize dropdowns if not already initialized
                if ($('#member_id').hasClass('select2-hidden-accessible')) {
                    $('#member_id').select2('destroy');
                }
                if ($('#loan_id').hasClass('select2-hidden-accessible')) {
                    $('#loan_id').select2('destroy');
                }
                
                // Reset form and hide loan details
                $('#demand-letter-form')[0].reset();
                $('#loan_details_container').hide();
                
                // Initialize dropdowns after modal is fully visible
                initializeMemberSelect();
                initializeLoanSelect();
            }, 300);
        });
        
        // Also initialize on document ready to ensure they're available
        initializeMemberSelect();
        initializeLoanSelect();

        // Form Validation Function
        function validateDemandLetterForm() {
            const form = $('#demand-letter-form');
            const memberId = $('#member_id').val();
            const loanId = $('#loan_id').val();
            const letterTypeId = $('#letter_type_id').val();
            const letterTemplateId = $('#letter_template_id').val();
            const amountOutstanding = parseFloat($('#amount_outstanding').val());

            // Reset previous error states
            form.find('.error-message').remove();
            form.find('.border-red-500').removeClass('border-red-500');

            let isValid = true;

            // Validation checks
            if (!memberId) {
                $('#member_id').addClass('border-red-500');
                form.append('<div class="error-message text-red-500 text-sm mt-1">Please select a member</div>');
                isValid = false;
            }

            if (!loanId) {
                $('#loan_id').addClass('border-red-500');
                form.append('<div class="error-message text-red-500 text-sm mt-1">Please select a loan</div>');
                isValid = false;
            }

            if (!letterTypeId) {
                $('#letter_type_id').addClass('border-red-500');
                form.append('<div class="error-message text-red-500 text-sm mt-1">Please select a letter type</div>');
                isValid = false;
            }

            if (!letterTemplateId) {
                $('#letter_template_id').addClass('border-red-500');
                form.append('<div class="error-message text-red-500 text-sm mt-1">Please select a letter template</div>');
                isValid = false;
            }

            if (isNaN(amountOutstanding) || amountOutstanding <= 0) {
                $('#amount_outstanding').addClass('border-red-500');
                form.append('<div class="error-message text-red-500 text-sm mt-1">Please enter a valid amount</div>');
                isValid = false;
            }

            return isValid;
        }

        // Attach form validation to submit button
        $('#demand-letter-submit').on('click', function(e) {
            e.preventDefault();
            
            if (validateDemandLetterForm()) {
                const form = $('#demand-letter-form');
                
                $.ajax({
                    url: '/user/create_demand_letter',  
                    method: 'POST',
                    data: form.serialize(),
                    success: function(response) {
                        // Close modal and refresh table or show success message
                        $('#create-demand-letter-modal').modal('hide');
                        
                        // Optionally reload demand letters table
                        if (response.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: 'Demand Letter Created',
                                text: response.message || 'Demand letter has been successfully created.'
                            }).then(() => {
                                // Reload page or update table dynamically
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: response.message || 'An error occurred while creating the demand letter.'
                            });
                        }
                    },
                    error: function(xhr) {
                        // Handle AJAX errors
                        let errorMessage = 'Failed to submit demand letter. Please try again.';
                        
                        // Check if there are specific validation errors
                        if (xhr.responseJSON && xhr.responseJSON.errors) {
                            const errors = xhr.responseJSON.errors;
                            errorMessage = Object.values(errors).flat().join('\n');
                        } else if (xhr.responseJSON && xhr.responseJSON.message) {
                            errorMessage = xhr.responseJSON.message;
                        }
                        
                        Swal.fire({
                            icon: 'error',
                            title: 'Submission Error',
                            text: errorMessage
                        });
                        
                        // Optional: Display field-specific errors
                        if (xhr.responseJSON && xhr.responseJSON.errors) {
                            const errors = xhr.responseJSON.errors;
                            Object.keys(errors).forEach(field => {
                                $(`#${field}`).addClass('border-red-500');
                                // Optionally add error messages next to fields
                                $(`#${field}`).after(`<div class="text-red-500 text-sm">${errors[field].join(', ')}</div>`);
                            });
                        }
                    }
                });
            }
        });

        // Global variables to store current selections
        let currentMemberData = null;

        // Debugging function to log detailed object information
        function debugLog(label, obj) {
            console.group(label);
            console.log('Type:', typeof obj);
            console.log('Is null:', obj === null);
            console.log('Is undefined:', obj === undefined);
            
            try {
                console.log('Stringified:', JSON.stringify(obj, null, 2));
            } catch (e) {
                console.log('Could not stringify object');
            }
            
            if (obj && typeof obj === 'object') {
                console.log('Keys:', Object.keys(obj));
            }
            
            console.groupEnd();
        }

        function initializeMemberSelect() {
            // Destroy existing select2 instances if they exist
            if ($('#member_id').hasClass("select2-hidden-accessible")) {
                $('#member_id').select2('destroy');
            }

            // Initialize member select
            $('#member_id').select2({
                theme: 'bootstrap-5',
                placeholder: 'Search for a customer...',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#create-demand-letter-modal'),
                ajax: {
                    url: '/api/customers/search',  
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        console.log('Search params:', params);
                        return {
                            q: params.term || '',
                            page: params.page || 1
                        };
                    },
                    processResults: function(data) {
                        console.group('Member Search processResults');
                        debugLog('Raw search data', data);

                        // Validate data structure
                        if (!data || !data.items || !Array.isArray(data.items)) {
                            console.error('Invalid data structure', data);
                            console.groupEnd();
                            return { results: [] };
                        }

                        // Safe mapping of results
                        const results = data.items.map(item => {
                            debugLog('Processing member item', item);

                            return {
                                id: item.id || '',
                                text: item.text || 'Unknown Member',
                                loans: Array.isArray(item.loans) ? item.loans : [],
                                // Include full item data for reference
                                _originalItem: item
                            };
                        });

                        console.log('Processed results:', results);
                        console.groupEnd();

                        return {
                            results: results,
                            pagination: {
                                more: data.has_more || false
                            }
                        };
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error('AJAX Search Error:', {
                            status: textStatus,
                            error: errorThrown,
                            responseText: jqXHR.responseText
                        });
                    },
                    cache: true
                },
                minimumInputLength: 0,
                templateResult: function(item) {
                    // Custom template to show more details
                    if (!item.id || item.loading) {
                        return item.text || 'Loading...';
                    }
                    
                    const loans = item.loans || [];
                    const loanInfo = loans.length > 0 
                        ? `${loans.length} loan(s), Total Outstanding: ${formatCurrency(
                            loans.reduce((total, loan) => total + (loan.OutstandingBalance || 0), 0)
                        )}` 
                        : 'No loans';
                    
                    return $(`
                        <div>
                            <strong>${item.text}</strong>
                            <br>
                            <small>${loanInfo}</small>
                        </div>
                    `);
                }
            }).on('select2:select', function(e) {
                console.group('Member Select Event');
                currentMemberData = e.params.data;
                debugLog('Selected member data', currentMemberData);
                
                // Populate loan dropdown
                const loanSelect = $('#loan_id');
                loanSelect.empty().append(new Option('Select a loan', '', true, true));
                
                // Get the name attribute for the hidden member name field
                const memberNameFieldName = $(this).data('name');
                
                // Determine member name and number
                const memberName = currentMemberData.text || currentMemberData.name || '';
                const memberNumber = currentMemberData.member_number || memberName;
                
                // Set hidden fields with member details
                $(`input[name="${memberNameFieldName}"]`).val(memberName);
                $('input[name="member_number"]').val(memberNumber);
                
                // Hide loan details container when changing member
                $('#loan_details_container').hide();
                
                // Defensive check for loans
                if (currentMemberData && 
                    currentMemberData.loans && 
                    Array.isArray(currentMemberData.loans) && 
                    currentMemberData.loans.length > 0) {
                    
                    currentMemberData.loans.forEach(loan => {
                        // Defensive checks for loan properties
                        const loanNo = loan.LoanNo || 'Unknown Loan';
                        const outstandingBalance = loan.OutstandingBalance || 0;
                        const loanAppId = loan.LoanAppID || '';
                        const daysInArrears = loan.DaysInArrears || 0;
                        // Use outstanding balance as fallback for installment amount per requirements
                        const installmentAmount = loan.InstallmentAmount || loan.OutstandingBalance || 0;
                        
                        // Calculate missed payments based on days in arrears (round up) per requirements
                        const missedPayments = Math.ceil(daysInArrears / 30);
                        
                        const option = new Option(
                            `${loanNo} (Outstanding: ${formatCurrency(outstandingBalance)})`, 
                            loanAppId,
                            false, 
                            false
                        );
                        
                        // Store all loan data including calculated fields
                        $(option).data('loan', {
                            ...loan,
                            missedPayments: missedPayments,
                            installmentAmount: installmentAmount
                        });
                        
                        loanSelect.append(option);
                        console.log('Added loan option:', loanNo, loanAppId);
                    });
                    
                    // Log the number of loans added
                    console.log(`Added ${currentMemberData.loans.length} loans to dropdown`);
                } else {
                    // No loans found
                    loanSelect.append(new Option('No loans available', '', true, true));
                    console.warn('No loans found for member:', currentMemberData);
                }
                
                loanSelect.trigger('change');
                console.groupEnd();
            }).on('select2:clear', function() {
                currentMemberData = null;
                $('#loan_id').empty().append(new Option('Select a loan', '', true, true)).trigger('change');
            });
        }

        function initializeLoanSelect() {
            // Initialize loan select
            $('#loan_id').select2({
                theme: 'bootstrap-5',
                placeholder: 'Select a Loan',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#create-demand-letter-modal')
            }).on('select2:select', function(e) {
                const selectedLoanId = e.target.value;
                const loan = $(e.target.selectedOptions[0]).data('loan');
                
                if (loan && loan.OutstandingBalance !== undefined) {
                    const outstandingAmount = loan.OutstandingBalance;
                    const daysInArrears = loan.DaysInArrears || 0;
                    const missedPayments = loan.missedPayments || 0;
                    const installmentAmount = loan.installmentAmount || 0;
                    
                    // Set amount outstanding field with raw numeric value
                    $('#amount_outstanding').val(outstandingAmount.toFixed(2));
                    
                    // Set demand amount to match outstanding balance by default
                    $('#demand_amount').val(outstandingAmount.toFixed(2));
                    
                    // Optional: Set a max value for the demand letter amount
                    $('#demand_amount').attr({
                        'max': outstandingAmount,
                        'min': '0',
                        'step': '0.01'
                    });
                    
                    // Set hidden raw values
                    $('#raw_days_in_arrears').val(daysInArrears);
                    $('#raw_missed_payments').val(missedPayments);
                    $('#raw_installment_amount').val(installmentAmount);
                    
                    // Update display fields
                    $('#outstanding_balance_display').val(formatCurrency(outstandingAmount));
                    $('#days_in_arrears_display').val(daysInArrears);
                    $('#missed_payments_display').val(missedPayments);
                    $('#installment_amount_display').val(formatCurrency(installmentAmount));
                    
                    // Show the loan details container after a slight delay to prevent modal jumping
                    setTimeout(function() {
                        $('#loan_details_container').show();
                    }, 50);
                    
                    // Log for debugging
                    console.log('Selected Loan Details:', {
                        loanId: selectedLoanId,
                        outstandingBalance: outstandingAmount,
                        daysInArrears: daysInArrears,
                        missedPayments: missedPayments,
                        installmentAmount: installmentAmount
                    });
                } else {
                    $('#amount_outstanding').val('0.00');
                    $('#demand_amount').val('0.00');
                    console.warn('No outstanding balance found for loan:', loan);
                    
                    // Hide the loan details container
                    $('#loan_details_container').hide();
                }
            }).on('select2:clear', function() {
                // Reset fields when loan is cleared
                $('#amount_outstanding').val('0.00');
                $('#demand_amount').val('0.00').removeAttr('max min step');
                
                // Reset hidden raw values
                $('#raw_days_in_arrears').val('');
                $('#raw_missed_payments').val('');
                $('#raw_installment_amount').val('');
                
                // Hide the loan details container
                $('#loan_details_container').hide();
            });
        }

        function formatCurrency(amount) {
            // Defensive check for amount
            const safeAmount = (amount === null || amount === undefined) ? 0 : amount;
            
            try {
                return new Intl.NumberFormat('en-KE', {
                    style: 'currency',
                    currency: 'KES',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(safeAmount);
            } catch (error) {
                console.error('Error formatting currency:', error);
                return 'KES 0.00';
            }
        }

        // Remove any legacy event handlers
        $('#member_id').off('select2:select');
        $('#loan_id').off('select2:select').off('select2:clear');

        // Dynamically populate letter templates based on letter type
        $('#letter_type_id').on('change', function() {
            var letterTypeId = $(this).val();
            $.ajax({
                url: '/api/letter_templates',
                method: 'GET',
                data: { letter_type_id: letterTypeId },
                success: function(response) {
                    var $templateSelect = $('#letter_template_id');
                    $templateSelect.empty();
                    
                    // Check if response has templates
                    if (response && response.length > 0) {
                        response.forEach(function(template) {
                            $templateSelect.append(
                                $('<option>', {
                                    value: template.id,
                                    text: template.name,
                                    'data-content': template.template_content
                                })
                            );
                        });
                    } else {
                        $templateSelect.append(
                            $('<option>', {
                                value: '',
                                text: 'No templates available'
                            })
                        );
                    }
                    $templateSelect.trigger('change');
                },
                error: function() {
                    var $templateSelect = $('#letter_template_id');
                    $templateSelect.empty();
                    $templateSelect.append(
                        $('<option>', {
                            value: '',
                            text: 'Error loading templates'
                        })
                    );
                    $templateSelect.trigger('change');
                }
            });
        });

        // Load template content when a template is selected
        $('#letter_template_id').on('change', function() {
            var $selectedOption = $(this).find('option:selected');
            var templateContent = $selectedOption.data('content') || '';
            $('#letter_content').val(templateContent);
        });

        // Remove any legacy event handlers or functions
        // This ensures we don't have conflicting event listeners
        $('#member_id').off('select2:select');
    });
});
