document.addEventListener('DOMContentLoaded', function() {
    // Initialize member select
    $(document).ready(function() {
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
                placeholder: 'Search for a member...',
                allowClear: true,
                width: '100%',
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
                minimumInputLength: 2,
                templateResult: function(item) {
                    // Custom template to show more details
                    if (!item.id) {
                        return item.text;
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
                        
                        const option = new Option(
                            `${loanNo} (Outstanding: ${formatCurrency(outstandingBalance)})`, 
                            loanAppId,
                            false, 
                            false
                        );
                        $(option).data('loan', loan);
                        loanSelect.append(option);
                    });
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
                width: '100%'
            }).on('select2:select', function(e) {
                const selectedLoanId = e.target.value;
                const loan = $(e.target.selectedOptions[0]).data('loan');
                
                // Update amount outstanding with defensive checks
                if (loan && loan.OutstandingBalance !== undefined) {
                    $('#amount_outstanding').val(formatCurrency(loan.OutstandingBalance));
                } else {
                    $('#amount_outstanding').val('0.00');
                    console.warn('No outstanding balance found for loan:', loan);
                }
            }).on('select2:clear', function() {
                $('#amount_outstanding').val('0.00');
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

        // Initialize selects
        initializeMemberSelect();
        initializeLoanSelect();

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
        $('#member_id').off('select2:select', populateLoanDropdown);
    });
});
