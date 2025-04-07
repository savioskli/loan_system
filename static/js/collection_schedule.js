document.addEventListener('DOMContentLoaded', function() {
    updateSummaryCardsPeriodically();
    
    
    // Helper functions
    function formatCurrency(amount) {
        if (amount === undefined || amount === null) return 'N/A';
        
        // Remove any existing commas and convert to number
        const cleanAmount = parseFloat(String(amount).replace(/,/g, ''));
        if (isNaN(cleanAmount)) return 'N/A';
        
        // Format with commas and 2 decimal places
        return cleanAmount.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
       // Utility functions
       function showLoading() {
        $('.loading-overlay').show();
        $('.loading-spinner').show();
    }
    
    function hideLoading() {
        $('.loading-overlay').hide();
        $('.loading-spinner').hide();
    }
    
    function showSuccess(message) {
        showNotification('Success', message);
    }
    
    function showError(message) {
        showNotification('Error', message);
    }

    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    }

    // Initialize tabs and filters
    initializeTabs();
    initializeFilterToggle();
    
    // Modal handling
    const modal = document.getElementById('newCollectionScheduleModal');
    const openModalBtn = document.getElementById('newCollectionScheduleBtn');
    const closeModalBtn = document.getElementById('closeCollectionScheduleModal');

    // Function to update loan details in form
    function updateLoanDetailsInForm(loan, formPrefix = '') {
        console.log('Updating loan details in form:', loan);
        
        // Update outstanding balance
        const outstandingBalanceInput = document.getElementById(formPrefix + 'outstandingBalance');
        if (outstandingBalanceInput) {
            const outstandingBalance = loan.OutstandingBalance || loan.outstanding_balance || 0;
            console.log('Setting outstanding balance:', outstandingBalance);
            outstandingBalanceInput.value = formatCurrency(outstandingBalance);
            console.log('Outstanding balance input value set to:', outstandingBalanceInput.value);
        } else {
            console.log('Outstanding balance input not found with ID:', formPrefix + 'outstandingBalance');
        }

        // Update missed payments
        const missedPaymentsInput = document.getElementById(formPrefix + 'missedPayments');
        if (missedPaymentsInput) {
            // Get days in arrears and ensure it's a number
            let daysInArrears = 0;
            if (loan.days_in_arrears !== undefined) {
                daysInArrears = Number(loan.days_in_arrears);
            } else if (loan.DaysInArrears !== undefined) {
                daysInArrears = Number(loan.DaysInArrears);
            }
            
            // Calculate missed installments (1 per 30 days)
            const missedInstallments = Math.ceil(daysInArrears / 30);
            console.log('Setting missed payments:', missedInstallments, 'calculated from days in arrears:', daysInArrears);
            missedPaymentsInput.value = missedInstallments;
        } else {
            console.log('Missed payments input not found with ID:', formPrefix + 'missedPayments');
        }

        // Set priority based on days in arrears
        const prioritySelect = document.getElementById(formPrefix + 'priority');
        if (prioritySelect) {
            let priorityValue = 'Low';
            if (daysInArrears >= 90) {
                priorityValue = 'Critical';
            } else if (daysInArrears >= 60) {
                priorityValue = 'High';
            } else if (daysInArrears >= 30) {
                priorityValue = 'Medium';
            }
            console.log('Setting priority to:', priorityValue, 'based on days in arrears:', daysInArrears);
            prioritySelect.value = priorityValue;
        } else {
            console.log('Priority select not found with ID:', formPrefix + 'priority');
        }
    }

    // Event handler for client select change in new collection schedule modal
    document.getElementById('collectionClientSelect').addEventListener('change', function() {
        console.log('Client selected:', this.options[this.selectedIndex]);
        const selectedOption = this.options[this.selectedIndex];
        const loanSelect = document.getElementById('loanSelect');
        
        // Clear existing options
        loanSelect.innerHTML = '';
        
        // Access loans directly from the option object
        if (selectedOption && selectedOption.loans && selectedOption.loans.length > 0) {
            console.log('Client loans:', selectedOption.loans);
            
            // Store loans in the client option for later access
            this.loans = selectedOption.loans;
            
            selectedOption.loans.forEach(loan => {
                const option = new Option(
                    `${loan.LoanNo} - ${formatCurrency(loan.LoanAmount)}`,
                    loan.LoanAppID
                );
                loanSelect.add(option);
            });
            
            // If there's only one loan, select it automatically
            if (selectedOption.loans.length === 1) {
                loanSelect.selectedIndex = 0;
                const loan = selectedOption.loans[0];
                console.log('Auto-selecting first loan:', loan);
                updateLoanDetailsInForm(loan);
            }
        }
    });

    // Event handler for loan select change in new collection schedule modal
    document.getElementById('loanSelect').addEventListener('change', function() {
        console.log('Loan selected:', this.options[this.selectedIndex]);
        const selectedOption = this.options[this.selectedIndex];
        const clientSelect = document.getElementById('collectionClientSelect');
        
        if (clientSelect && clientSelect.loans && clientSelect.loans.length > 0) {
            // Find the selected loan by ID
            const selectedLoan = clientSelect.loans.find(loan => loan.LoanAppID === selectedOption.value);
            if (selectedLoan) {
                console.log('Found selected loan:', selectedLoan);
                
                // Update outstanding balance
                const outstandingBalance = selectedLoan.OutstandingBalance || 0;
                document.getElementById('outstandingBalance').value = formatCurrency(outstandingBalance);
                window.outstandingBalance = outstandingBalance; // Store raw value
                
                // Calculate missed payments based on days in arrears
                const daysInArrears = selectedLoan.DaysInArrears || 0;
                const missedInstallments = Math.ceil(daysInArrears / 30); // 1 missed payment per 30 days
                document.getElementById('missedPayments').value = missedInstallments;
                window.missedPayments = missedInstallments; // Store raw value
                
                // Set priority based on days in arrears
                const prioritySelect = document.getElementById('priority');
                if (prioritySelect) {
                    if (daysInArrears >= 90) {
                        prioritySelect.value = 'Critical';
                    } else if (daysInArrears >= 60) {
                        prioritySelect.value = 'High';
                    } else if (daysInArrears >= 30) {
                        prioritySelect.value = 'Medium';
                    } else {
                        prioritySelect.value = 'Low';
                    }
                }
            } else {
                console.log('Selected loan not found in client loans');
            }
        } else {
            console.log('Client loans not available');
        }
    });

    // Event handler for create collection from loan details modal
    document.getElementById('create-collection-from-loan').addEventListener('click', function() {
        console.log('Create collection from loan details clicked');
        
        // Get loan details from the modal
        const loanDetailsAmount = document.getElementById('loan-details-amount').textContent;
        const loanDetailsArrears = document.getElementById('loan-details-arrears').textContent;
        
        console.log('Loan details amount:', loanDetailsAmount);
        console.log('Loan details arrears:', loanDetailsArrears);
        
        // Wait for the new modal to be visible before updating fields
        setTimeout(() => {
            // Update the fields in the new collection schedule modal
            const outstandingBalanceInput = document.getElementById('outstandingBalance');
            if (outstandingBalanceInput) {
                outstandingBalanceInput.value = loanDetailsAmount;
                console.log('Set outstanding balance to:', loanDetailsAmount);
            } else {
                console.log('Outstanding balance input not found');
            }
            
            const missedPaymentsInput = document.getElementById('missedPayments');
            if (missedPaymentsInput) {
                // Calculate missed installments from days in arrears
                const daysInArrears = parseInt(loanDetailsArrears) || 0;
                const missedInstallments = Math.ceil(daysInArrears / 30);
                missedPaymentsInput.value = missedInstallments;
                console.log('Set missed payments to:', missedInstallments, 'calculated from days in arrears:', daysInArrears);
            } else {
                console.log('Missed payments input not found');
            }
            
            // Set priority based on days in arrears
            const daysInArrears = parseInt(loanDetailsArrears) || 0;
            const prioritySelect = document.getElementById('priority');
            if (prioritySelect) {
                let priorityValue = 'Low';
                if (daysInArrears >= 90) {
                    priorityValue = 'Critical';
                } else if (daysInArrears >= 60) {
                    priorityValue = 'High';
                } else if (daysInArrears >= 30) {
                    priorityValue = 'Medium';
                }
                console.log('Setting priority to:', priorityValue);
                prioritySelect.value = priorityValue;
            } else {
                console.log('Priority select not found');
            }
        }, 500); // Wait 500ms for the modal to be fully visible
    });

    // Initialize staff select with Select2
    const staffSelect2Config = {
    theme: 'bootstrap-5',
    placeholder: 'Select a collection officer',
    allowClear: true,
    width: '100%',
    ajax: {
        url: '/api/collection-schedules/staff',
        dataType: 'json',
        delay: 250,
        data: function(params) {
            console.log('Sending staff search:', params.term);
            return {
                term: params.term,
                role_type: 'officer',  // Filter for collection officers only
                page: params.page || 1
            };
        },
        processResults: function(data) {
            console.log('Received staff data:', data);
            if (!data || !Array.isArray(data)) {
                console.error('Expected data to be an array:', data);
                return { results: [] };
            }
            return {
                results: data.map(item => ({
                    id: item.id,
                    text: item.name,
                    role: item.role,
                    branchId: item.branch_id
                }))
            };
        },
        cache: true
    },
    minimumInputLength: 0,
    templateResult: function(staff) {
        if (staff.loading) {
            return 'Loading...';
        }
        return staff.text;
    },
    templateSelection: function(staff) {
        // Set the hidden input value for BranchID when a staff member is selected
        $('#branchInput').val(staff.branchId);
        return staff.text;
    }
};

// Configuration for supervisorSelect
const supervisorSelect2Config = {
    theme: 'bootstrap-5',
    placeholder: 'Select a supervisor',
    allowClear: true,
    width: '100%',
    ajax: {
        url: '/api/collection-schedules/staff',
        dataType: 'json',
        delay: 250,
        data: function(params) {
            console.log('Sending supervisor search:', params.term);
            return {
                term: params.term,
                role_type: 'supervisor',  // Filter for collection supervisors and managers only
                page: params.page || 1
            };
        },
        processResults: function(data) {
            console.log('Received supervisor data:', data);
            if (!data || !Array.isArray(data)) {
                console.error('Expected data to be an array:', data);
                return { results: [] };
            }
            return {
                results: data.map(item => ({
                    id: item.id,
                    text: item.name,
                    role: item.role
                }))
            };
        },
        cache: true
    },
    minimumInputLength: 0,
    templateResult: function(staff) {
        if (staff.loading) {
            return 'Loading...';
        }
        return staff.text;
    },
    templateSelection: function(staff) {
        return staff.text;
    }
};

// Configuration for managerSelect
const managerSelect2Config = {
    theme: 'bootstrap-5',
    placeholder: 'Select a Collections Manager',
    allowClear: true,
    width: '100%',
    ajax: {
        url: '/api/collection-schedules/staff',
        dataType: 'json',
        delay: 250,
        data: function(params) {
            console.log('Sending manager search:', params.term);
            return {
                term: params.term,
                role_type: 'manager',  // Filter for Collections Managers only
                page: params.page || 1
            };
        },
        processResults: function(data) {
            console.log('Received manager data:', data);
            if (!data || !Array.isArray(data)) {
                console.error('Expected data to be an array:', data);
                return { results: [] };
            }
            return {
                results: data.map(item => ({
                    id: item.id,
                    text: item.name,
                    role: item.role
                }))
            };
        },
        cache: true
    },
    minimumInputLength: 0,
    templateResult: function(manager) {
        if (manager.loading) {
            return 'Loading...';
        }
        return manager.text;
    },
    templateSelection: function(manager) {
        return manager.text;
    }
};

// Initialize Select2 for both staff select fields
$(document).ready(function() {
    $('#staffSelect').select2({
        ...staffSelect2Config,
        dropdownParent: $('#newCollectionScheduleModal')
    });
    $('#supervisorSelect').select2({
        ...supervisorSelect2Config,
        dropdownParent: $('#newCollectionScheduleModal')
    });
    $('#managerSelect').select2({
        ...managerSelect2Config,
        dropdownParent: $('#newCollectionScheduleModal')
    });
});

    $(document).ready(function() {
   
        // Initialize client select
        initializeClientSelect('#collectionClientSelect', true);

         $('#loanSelect').select2({
            theme: 'bootstrap-5',
            placeholder: 'Select a Loan Account',
            width: '100%',
            dropdownParent: $('#newCollectionScheduleModal')
        }).on('select2:select', function(e) {
            const loanId = $(this).val();
            const clientSelect = $('#collectionClientSelect');
            const clientData = clientSelect.select2('data')[0];
            
            console.log('Loan selected with ID:', loanId);
            console.log('Client data:', clientData);
            
            if (clientData && clientData.loans && clientData.loans.length > 0) {
                const selectedLoan = clientData.loans.find(loan => loan.LoanAppID === loanId);
                if (selectedLoan) {
                    console.log('Found loan with OutstandingBalance:', selectedLoan.OutstandingBalance);
                    $('#outstandingBalance').val(formatCurrency(selectedLoan.OutstandingBalance || 0));
                    
                    // Calculate missed payments based on days in arrears and repayment frequency
                    console.log('Days in arrears value:', selectedLoan.DaysInArrears);
                    console.log('Type of DaysInArrears:', typeof selectedLoan.DaysInArrears);
                    
                    // Force conversion to number to ensure proper calculation
                    let daysInArrears = 0;
                    if (selectedLoan.DaysInArrears !== undefined) {
                        daysInArrears = Number(selectedLoan.DaysInArrears);
                    }
                    
                    const repaymentPeriod = selectedLoan.RepaymentPeriod || 12; // Default to monthly (12 per year)
                    
                    // Calculate missed installments (assuming monthly payments by default)
                    // For monthly payments: 30 days = 1 missed payment
                    const missedInstallments = Math.ceil(daysInArrears / 30);
                    console.log('Calculated missed installments:', missedInstallments, 'from days in arrears:', daysInArrears);
                    
                    $('#missedPayments').val(missedInstallments);
                    
                    // Set priority based on days in arrears
                    const prioritySelect = document.getElementById('priority');
                    if (prioritySelect) {
                        if (daysInArrears >= 90) {
                            prioritySelect.value = 'Critical';
                        } else if (daysInArrears >= 60) {
                            prioritySelect.value = 'High';
                        } else if (daysInArrears >= 30) {
                            prioritySelect.value = 'Medium';
                        } else {
                            prioritySelect.value = 'Low';
                        }
                    }
                }
            }
        }); 
    });

    // Modal event listeners
    openModalBtn.addEventListener('click', function() {
        modal.classList.remove('hidden');
        resetForm();
    });

    closeModalBtn.addEventListener('click', function() {
        modal.classList.add('hidden');
    });

    // Form handling
    function resetForm() {
        $('#newCollectionScheduleForm')[0].reset();
        $('#staffSelect').val(null).trigger('change');
        $('#loanSelect').val(null).trigger('change');
    }

function initializeClientSelect(selector, isModal) {
    console.log('Initializing select2 for:', selector);
    const select = $(selector);
    const loanSelect = $('#loanSelect'); // Reference to the loanSelect element

    const config = {
        theme: 'bootstrap-5',
        placeholder: 'Search for a client...',
        allowClear: true,
        width: '100%',
        ajax: {
            url: '/api/customers/search',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term || '',
                    page: params.page || 1,
                    per_page: 10
                };
            },
            processResults: function(data) {
                if (!data || !Array.isArray(data.items)) {
                    return { results: [] };
                }
                return {
                    results: data.items.map(item => ({
                        id: item.id,
                        text: item.text,
                        loans: item.loans // Include loans array
                    })),
                    pagination: {
                        more: data.has_more
                    }
                };
            },
            cache: true
        },
        minimumInputLength: 2,
        templateResult: function(client) {
            return client.loading ? 'Loading...' : client.text;
        },
        templateSelection: function(client) {
            return client.text; // Display only the client's name in the main select
        }
    };

    if (isModal) {
        config.dropdownParent = $('#newCollectionScheduleModal');
    }

    // Initialize Select2 for the client select
    select.select2(config)
        .on('select2:select', function(e) {
            const data = e.params.data;
            console.log('Selected:', data);
            if (isModal) {
                console.log('Client selected in modal:', data);
            }
            // Populate the loanSelect with all LoanNos for the selected client
            loanSelect.empty(); // Clear previous options
            data.loans.forEach(loan => {
                const option = new Option(
                    `${loan.LoanNo} - ${formatCurrency(loan.LoanAmount)}`,
                    loan.LoanAppID, false, false
                );
                loanSelect.append(option);
            });
            
            // Update outstanding balance if there's only one loan
            if (data.loans.length === 1) {
                const loan = data.loans[0];
                console.log('Auto-selecting first loan:', loan);
                document.getElementById('outstandingBalance').value = formatCurrency(loan.OutstandingBalance || 0);
                document.getElementById('missedPayments').value = loan.DaysInArrears || 0;
                
                // Set priority based on days in arrears
                const daysInArrears = loan.DaysInArrears || 0;
                const prioritySelect = document.getElementById('priority');
                if (prioritySelect) {
                    if (daysInArrears >= 90) {
                        prioritySelect.value = 'Critical';
                    } else if (daysInArrears >= 60) {
                        prioritySelect.value = 'High';
                    } else if (daysInArrears >= 30) {
                        prioritySelect.value = 'Medium';
                    } else {
                        prioritySelect.value = 'Low';
                    }
                }
            }
            
            // If we have a loan, update the outstanding balance field directly
            if (data.loans && data.loans.length > 0) {
                // Store loans in a data attribute for later access
                $(this).data('loans', data.loans);
                
                // If there's only one loan, update fields immediately
                if (data.loans.length === 1) {
                    const loan = data.loans[0];
                    console.log('Auto-selecting first loan with OutstandingBalance:', loan.OutstandingBalance);
                    $('#outstandingBalance').val(formatCurrency(loan.OutstandingBalance || 0));
                    
                    // Calculate missed payments based on days in arrears
                    const daysInArrears = loan.DaysInArrears || 0;
                    const missedInstallments = Math.ceil(daysInArrears / 30);
                    console.log('Calculated missed installments:', missedInstallments, 'from days in arrears:', daysInArrears);
                    $('#missedPayments').val(missedInstallments);
                }
            }
            
            loanSelect.trigger('change'); // Trigger change event to update the UI
        })
        .on('select2:clear', function() {
            console.log('Selection cleared');
            loanSelect.empty(); // Clear loanSelect when client selection is cleared
        })
        .on('select2:error', function(e) {
            console.error('Select2 error:', e);
        });
}


    // Load collection schedules
    function loadCollectionSchedules(filters = {}) {
        console.log('Loading collection schedules with filters:', filters);
        const queryParams = new URLSearchParams(filters);
        
        $.ajax({
            url: `/api/collection-schedules?${queryParams}`,
            method: 'GET',
            success: function(response) {
                console.log('Received response:', response);
                const scheduleList = $('#collectionSchedulesList');
                scheduleList.empty();
                
                if (!response.items || response.items.length === 0) {
                    scheduleList.append(`
                        <div class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
                            <p class="text-center text-gray-600 dark:text-gray-400">No collection schedules found.</p>
                        </div>
                    `);
                    // Update pagination even when no results
                    updatePagination(response.pagination);
                    return;
                }
                
                response.items.forEach(schedule => {
                    try {
                        const borrowerInfo = schedule.borrower_name ? 
                            `${schedule.loan_account} - ${schedule.borrower_name}` : 
                            schedule.loan_account || 'Unknown Borrower';
                        
                        const staffName = schedule.staff_name || 'Unassigned';
                        const nextFollowUp = schedule.next_follow_up_date ? formatDate(schedule.next_follow_up_date) : 'Not scheduled';
                        const method = schedule.preferred_collection_method || 'Not specified';
                        
                        // Fetch borrower name from core banking system
                        const fetchBorrowerName = async (loanId) => {
                            try {
                                const response = await fetch(`/api/borrower/${loanId}`);
                                if (response.ok) {
                                    const data = await response.json();
                                    if (data.success) {
                                        return data.borrower_name;
                                    }
                                }
                                console.error('Error fetching borrower name:', await response.text());
                                return 'Unknown';
                            } catch (error) {
                                console.error('Error fetching borrower name:', error);
                                return 'Unknown';
                            }
                        };

                        // Format values
                        const outstandingAmount = schedule.outstanding_balance !== undefined && schedule.outstanding_balance !== null 
                            ? formatCurrency(String(schedule.outstanding_balance).replace(/,/g, '')) 
                            : 'N/A';
                        const missedPayments = schedule.missed_payments || 0;
                        const collectionLocation = schedule.collection_location || 'Not Specified';

                        // Fetch borrower name and update the card
                        fetchBorrowerName(schedule.loan_id).then(borrowerName => {
                            const scheduleHtml = `<div class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden border border-gray-200 dark:border-gray-700 mb-4">
                                    <!-- Card Header -->
                                    <div class="px-6 py-4 bg-gradient-to-r from-blue-200 to-blue-100 dark:from-gray-600 dark:to-gray-500 border-b border-gray-300 dark:border-gray-600">
                                        <div class="flex justify-between items-center">
                                            <div class="flex items-center space-x-3">
                                                <h3 class="text-xl font-semibold text-blue-900 dark:text-white">
                                                    ${borrowerName}
                                                </h3>
                                                ${schedule.collection_priority ? `
                                                <span class="px-2 py-0.5 text-xs font-bold rounded-full ${getPriorityClass(schedule.collection_priority)}">
                                                    ${schedule.collection_priority}
                                                </span>
                                                ` : ''}
                                                ${schedule.progress_status ? `
                                                <span class="px-2 py-0.5 text-xs font-bold rounded-full ${getStatusClass(schedule.progress_status)}">
                                                    ${schedule.progress_status}
                                                </span>
                                                ` : ''}
                                            </div>
                                            <div class="flex items-center gap-2">
                                                ${currentUser.role === 'admin' || currentUser.role === 'supervisor' || schedule.staff_name === currentUser.name ? `
                                                    <button class="edit-schedule-btn bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-full text-xs transition" data-schedule-id="${schedule.id}" data-loan-id="${schedule.loan_id}" data-borrower-name="${schedule.borrower_name || ''}">
                                                        <i class="fas fa-edit"></i>
                                                    </button>
                                                ` : ''}
                                                <button class="view-progress-btn bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-full text-xs transition" data-schedule-id="${schedule.id}" title="View Progress">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="update-progress-btn bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded-full text-xs transition" data-schedule-id="${schedule.id}" data-loan-id="${schedule.loan_id}" data-borrower-name="${schedule.borrower_name || ''}" title="Update Progress">
                                                    <i class="fas fa-tasks"></i>
                                                </button>
                                                <button class="submit-schedule-btn bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-full text-xs transition" data-schedule-id="${schedule.id}" data-loan-id="${schedule.loan_id}" data-borrower-name="${schedule.borrower_name || ''}" title="Submit Schedule">
                                                    <i class="fas fa-paper-plane"></i>
                                                </button>
                                                <button class="delete-schedule-btn bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-full text-xs transition" data-schedule-id="${schedule.id}" data-loan-id="${schedule.loan_id}" data-borrower-name="${schedule.borrower_name || ''}" title="Delete Schedule">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <div class="mt-3 flex justify-between text-sm text-gray-700 dark:text-gray-300">
                                            <div>
                                                Attempts: <span class="font-medium">${schedule.attempts_made}/${schedule.attempts_allowed}</span><br>
                                                Loan Account: <span class="font-medium">${schedule.loan_account || 'N/A'}</span>
                                            </div>
                                            <div>
                                                Branch: <span class="font-medium">${schedule.branch_name || 'N/A'}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <!-- Card Body -->
                                    <div class="px-6 py-4">
                                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                            <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                                                <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">Collection Details</h4>
                                                <ul class="space-y-1 text-gray-700 dark:text-gray-300">
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Outstanding:</span> ${outstandingAmount}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Missed Payments:</span> ${missedPayments}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Method:</span> ${method}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Promised Payment:</span> ${formatDateTime(schedule.promised_payment_date) || 'Not Set'}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Location:</span> ${collectionLocation}</li>
                                                </ul>
                                            </div>
                                            <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                                                <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">Staff Assignment</h4>
                                                <ul class="space-y-1 text-gray-700 dark:text-gray-300">
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Officer:</span> ${staffName}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Supervisor:</span> ${schedule.supervisor_name || 'Not Assigned'}</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                            <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                                                <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">Follow-up Schedule</h4>
                                                <ul class="space-y-1 text-gray-700 dark:text-gray-300">
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Next Follow-up:</span> ${formatDateTime(schedule.next_follow_up_date) || 'Not Set'}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Frequency:</span> ${schedule.follow_up_frequency || 'Not Set'}</li>
                                                    <li><span class="font-medium text-blue-700 dark:text-blue-300">Best Time:</span> ${schedule.best_contact_time || 'Not Specified'}</li>
                                                </ul>
                                            </div>
                                            <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                                                <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">Contact Information</h4>
                                                <p class="break-words text-gray-700 dark:text-gray-300">
                                                    <span class="font-medium text-blue-700 dark:text-blue-300">Alternative:</span> ${schedule.alternative_contact || 'None'}
                                                </p>
                                            </div>
                                        </div>
                                        ${(schedule.task_description || schedule.special_instructions) ? `
                                        <div class="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 text-sm">
                                            <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">Task Information</h4>
                                            <div class="space-y-3 text-gray-700 dark:text-gray-300">
                                                ${schedule.task_description ? `
                                                <div>
                                                    <p class="font-medium text-blue-700 dark:text-blue-300">Description</p>
                                                    <p class="text-sm">${schedule.task_description}</p>
                                                </div>
                                                ` : ''}
                                                ${schedule.special_instructions ? `
                                                <div>
                                                    <p class="font-medium text-blue-700 dark:text-blue-300">Special Instructions</p>
                                                    <p class="text-sm">${schedule.special_instructions}</p>
                                                </div>
                                                ` : ''}
                                            </div>
                                        </div>
                                        ` : ''}
                                        <!-- Workflow Status Section -->
                                        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                                            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Workflow Status</h4>
                                            <div class="flex items-center justify-between">
                                                <span class="text-sm text-gray-500 dark:text-gray-400">Submission Status:</span>
                                                <span id="submission-status-${schedule.id}" class="text-sm font-medium">Loading...</span>
                                            </div>
                                            <div class="flex items-center justify-between mt-1">
                                                <span class="text-sm text-gray-500 dark:text-gray-400">Current Step:</span>
                                                <span id="current-step-${schedule.id}" class="text-sm font-medium">Loading...</span>
                                            </div>
                                        </div>
                                    </div>
                                    <!-- Card Footer -->
                                    ${schedule.escalation_level ? `
                                    <div class="px-6 pb-4">
                                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                                            Escalated Level ${schedule.escalation_level}
                                        </span>
                                    </div>` : ''}
                                </div>
                                `;

                            // Create a new div for the schedule
                            scheduleList.append(scheduleHtml);
                            loadSubmissionStatus(schedule.id);
                        });
                    } catch (error) {
                        console.error('Error rendering schedule:', error, schedule);
                    }
                });
                
                // Update pagination controls
                updatePagination(response.pagination);
            },
            error: function(xhr, status, error) {
                console.error('Error loading collection schedules:', error);
                const scheduleList = $('#collectionSchedulesList');
                scheduleList.empty().append(`
                    <div class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
                        <p class="text-center text-red-600 dark:text-red-400">Error loading collection schedules.</p>
                    </div>
                `);
                // Clear pagination on error
                updatePagination(null);
            }
        });
    }

    // Create or update collection schedule
$('#newCollectionScheduleForm').submit(function(event) {
    event.preventDefault();
    
    // Get the outstanding balance value and strip the currency formatting
    const outstandingBalanceText = $('#outstandingBalance').val();
    const outstandingBalance = parseFloat(outstandingBalanceText.replace(/[^0-9.-]+/g, ''));
    
    // Get current date in ISO format
    const currentDate = new Date().toISOString();
    
    // Validate required fields
    const requiredFields = {
        'staffSelect': 'Staff Member',
        'collectionClientSelect': 'Client',
        'loanSelect': 'Loan Account',
        'priority': 'Priority Level',
        'method': 'Collection Method',
        'frequency': 'Follow-up Frequency',
        'nextFollowUp': 'Next Follow-up Date',
        'promisedPaymentDate': 'Expected Payment Date',
        'task_description': 'Collection Notes'
    };
    
    let missingFields = [];
    for (const [fieldId, fieldName] of Object.entries(requiredFields)) {
        if (!$('#' + fieldId).val()) {
            missingFields.push(fieldName);
        }
    }
    
    if (missingFields.length > 0) {
        showNotification('Error', 'Please fill in all required fields: ' + missingFields.join(', '));
        return;
    }
    
    // Log supervisor and manager selection for debugging
    const supervisorVal = $('#supervisorSelect').val();
    const managerVal = $('#managerSelect').val();
    console.log('Raw supervisor value:', supervisorVal);
    console.log('Raw manager value:', managerVal);

    // Get values from form
    const bestContactTime = $('#bestContactTime').val();
    const collectionLocation = $('#collectionLocation').val();
    const alternativeContact = $('#alternativeContact').val();
    
    // Get form mode
    const formMode = $(this).data('mode');
    
    // Log form values for debugging
    console.log('Contact time:', bestContactTime);
    console.log('Location:', collectionLocation);
    console.log('Alt contact:', alternativeContact);
    console.log('Outstanding balance:', window.outstandingBalance);
    console.log('Missed payments:', window.missedPayments);
    
    const formData = {
        // Required fields in exact order of API route
        client_id: parseInt($('#collectionClientSelect').val()),
        loan_id: parseInt($('#loanSelect').val()),
        follow_up_deadline: $('#nextFollowUp').val(),
        collection_priority: $('#priority').val(),
        follow_up_frequency: $('#frequency').val(),
        next_follow_up_date: $('#nextFollowUp').val(),
        promised_payment_date: $('#promisedPaymentDate').val(),
        attempts: parseInt($('#attemptsAllowed').val()) || 3,
        preferred_collection_method: $('#method').val() || 'Phone Call',
        task_description: $('#task_description').val(),
        csrf_token: $('input[name="csrf_token"]').val(),
        special_instructions: $('#instructions').val() || '',
        branch_id: $('#branchInput').val(),  // API expects branch_id which maps to assigned_branch

        // Additional fields from modal
        assigned_id: parseInt($('#staffSelect').val()),
        supervisor_id: supervisorVal ? parseInt(supervisorVal) : null,
        manager_id: managerVal ? parseInt(managerVal) : null,
        
        // Contact and loan details
        outstanding_balance: parseFloat($('#outstandingBalance').val().replace(/[^0-9.-]+/g, '')) || 0,
        missed_payments: parseInt($('#missedPayments').val()) || 0,
        best_contact_time: bestContactTime || null,
        collection_location: collectionLocation || null,
        alternative_contact: alternativeContact || null,
        
        // Status fields
        attempts_made: 0,
        progress_status: 'Not Started',
        escalation_level: null,
        resolution_date: null,
        reviewed_by: null,
        approval_date: null
    };

    // Log the final form data values for debugging
    console.log('Final supervisor_id:', formData.supervisor_id);
    console.log('Final manager_id:', formData.manager_id);
    console.log('Complete form data:', formData);

    // Determine URL and method based on form mode
    const isEditMode = formMode === 'edit';
    const targetScheduleId = $(this).data('schedule-id');
    const url = isEditMode ? `/api/collection-schedules/${targetScheduleId}` : '/api/collection-schedules';
    const method = isEditMode ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': $('input[name="csrf_token"]').val()
        },
        data: JSON.stringify(formData),
        success: function(response) {
            document.getElementById('newCollectionScheduleModal').classList.add('hidden');
            loadCollectionSchedules();
            
            // Reset form mode
            $('#newCollectionScheduleForm').data('mode', 'create');
            $('#newCollectionScheduleForm').data('schedule-id', '');
            $('#createScheduleModalTitle').text('Create Collection Schedule');
            $('#createScheduleModalSubmit').text('Create Schedule');
        },
        error: function(xhr) {
            showNotification('Error', xhr.responseJSON?.error || `Failed to ${isEditMode ? 'update' : 'create'} schedule`);
            console.error(`Error ${isEditMode ? 'updating' : 'creating'} schedule:`, xhr);
        }
    });
});

    // Update progress and show payment history modal
    $(document).on('click', '.update-progress-btn', function() {
        const scheduleId = $(this).attr('data-schedule-id'); // Use attr instead of data
        const loanId = $(this).attr('data-loan-id'); // Use attr instead of data
        const borrowerName = $(this).attr('data-borrower-name'); // Use attr instead of data
        
        console.log('Opening modal with schedule ID:', scheduleId);
        
        // Set the schedule ID and loan ID in the payment form
        $('#paymentScheduleId').val(scheduleId);
        $('#paymentLoanId').val(loanId);
        
        // Set default payment date to current date and time
        const now = new Date();
        const formattedDate = now.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:MM
        $('#paymentDate').val(formattedDate);
        
        // Show the payment history modal
        $('#paymentHistoryModal').removeClass('hidden');
    });
    
    // Handle modal close button
    $(document).on('click', '#closeCollectionScheduleModal, #closePaymentHistoryModal', function() {
        // Reset form
        $('#newPaymentForm')[0].reset();
        // Clear hidden fields
        $('#paymentScheduleId').val('');
        $('#paymentLoanId').val('');
        // Close modal
        $('#paymentHistoryModal').addClass('hidden');
    });

    // Handle form submission
    $('#newPaymentForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const scheduleId = $('#paymentScheduleId').val();
        
        if (!scheduleId) {
            console.error('Schedule ID is required');
            return;
        }

        // Add schedule ID to form data
        formData.set('schedule_id', scheduleId);

        $.ajax({
            url: `/api/collection-schedules/${scheduleId}/progress`,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('Progress update created:', response);
                // Reload schedules
                loadCollectionSchedules();
                // Close modal
                $('#paymentHistoryModal').addClass('hidden');
                // Show success notification
                showNotification('Success', 'Progress update saved successfully');
            },
            error: function(xhr) {
                console.error('Error creating progress update:', xhr.responseText);
                showNotification('Error', 'Failed to save progress update');
            }
        });
    });

    // Handle modal close button
    $('#updateProgressModal button[data-bs-dismiss="modal"]').click(function() {
        $('#updateProgressModal').addClass('hidden');
    });

    // Handle cancel button
    $('#cancelPaymentBtn').click(function() {
        $('#updateProgressModal').addClass('hidden');
    });
    
    // Close new collection schedule modal - using event delegation
    $(document).on('click', '#closeCollectionScheduleModal', function() {
        const modal = document.getElementById('newCollectionScheduleModal');
        modal.classList.add('hidden');
        
        // Reset form and mode
        const form = document.getElementById('newCollectionScheduleForm');
        form.reset();
        $(form).data('mode', 'create');
        $(form).data('schedule-id', '');
        $('#createScheduleModalTitle').text('Create Collection Schedule');
        $('#createScheduleModalSubmit').text('Create Schedule');
        
        // Reset select2 fields
        $('#collectionClientSelect').val('').trigger('change');
        $('#loanSelect').val('').trigger('change');
        $('#staffSelect').val('').trigger('change');
        $('#supervisorSelect').val('').trigger('change');
        $('#managerSelect').val('').trigger('change');
        
        // Re-enable selects
        document.getElementById('collectionClientSelect').disabled = false;
        document.getElementById('loanSelect').disabled = false;
    });
    
    // Load payment history for a schedule
    function loadPaymentHistory(scheduleId) {
        // No longer needed since we removed the table
    }

    // Escalate schedule
    $(document).on('click', '.escalate-btn', function() {
        const scheduleId = $(this).data('id');
        const level = prompt('Enter escalation level (1-3):');
        const notes = prompt('Enter escalation notes:');
        
        if (level) {
            $.ajax({
                url: `/api/collection-schedules/${scheduleId}/escalate`,
                method: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({
                    escalation_level: parseInt(level),
                    notes: notes
                }),
                success: function() {
                    showNotification('Success', 'Schedule escalated successfully');
                    loadCollectionSchedules();
                },
                error: function(xhr) {
                    showNotification('Error', xhr.responseJSON?.error || 'Failed to escalate schedule');
                }
            });
        }
    });

    // Delete schedule
    $(document).on('click', '.delete-btn', function() {
        const scheduleId = $(this).data('id');
        if (confirm('Are you sure you want to delete this schedule?')) {
            $.ajax({
                url: `/api/collection-schedules/${scheduleId}`,
                method: 'DELETE',
                success: function() {
                    showNotification('Success', 'Schedule deleted successfully');
                    loadCollectionSchedules();
                },
                error: function(xhr) {
                    showNotification('Error', xhr.responseJSON?.error || 'Failed to delete schedule');
                }
            });
        }
    });

    // Filter handling
    $('#filterStaff, #filterPriority, #filterStatus, #filterMethod').on('change', function() {
        const filters = {
            assigned_id: $('#filterStaff').val(),
            priority: $('#filterPriority').val(),
            status: $('#filterStatus').val(),
            method: $('#filterMethod').val()
        };
        loadCollectionSchedules(filters);
    });

    // Utility functions
    function formatDate(dateString) {
        if (!dateString) return 'Not Set';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid Date';
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function formatDateTime(dateString) {
        if (!dateString) return 'Not Set';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid Date';
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function getPriorityClass(priority) {
        switch (priority.toLowerCase()) {
            case 'high':
                return 'bg-red-100 text-red-800';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800';
            case 'low':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }

    function getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'not started':
                return 'bg-gray-100 text-gray-800';
            case 'in progress':
                return 'bg-blue-100 text-blue-800';
            case 'completed':
                return 'bg-green-100 text-green-800';
            case 'escalated':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }

    function showNotification(title, message) {
        // Implement your notification system here
        alert(`${title}: ${message}`);
    }

    // Make viewLoanDetails globally accessible
window.viewLoanDetails = function(loanId) {
        // Fetch loan details
        fetch(`/api/loans/${loanId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch loan details');
                }
                return response.json();
            })
            .then(loan => {
                // Populate modal with loan details
                const modal = document.getElementById('loanDetailsModal');
                document.getElementById('loan-details-id').textContent = loan.loan_id;
                document.getElementById('loan-details-customer').textContent = loan.customer_name;
                document.getElementById('loan-details-amount').textContent = formatCurrency(loan.outstanding_balance) || '0.00';
                document.getElementById('loan-details-arrears').textContent = loan.days_in_arrears || '0';
                
                // Remove reference to due_date since it's not available
                const dueDateElement = document.getElementById('loan-details-due-date');
                if (dueDateElement) {
                    dueDateElement.textContent = 'N/A';
                }
                
                // Populate guarantors table
                const guarantorsList = document.getElementById('guarantors-list');
                const noGuarantorsRow = document.getElementById('no-guarantors-row');
                
                // Clear existing guarantors
                while (guarantorsList.firstChild) {
                    guarantorsList.removeChild(guarantorsList.firstChild);
                }
                
                // Add guarantors if available
                if (loan.guarantors && loan.guarantors.length > 0) {
                    // Hide the "no guarantors" message
                    guarantorsList.appendChild(noGuarantorsRow);
                    noGuarantorsRow.style.display = 'none';
                    
                    // Add each guarantor to the table
                    loan.guarantors.forEach(guarantor => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td class="px-4 py-2 text-sm text-gray-500">${guarantor.name}</td>
                            <td class="px-4 py-2 text-sm text-gray-500">${formatCurrency(guarantor.guaranteed_amount)}</td>
                            <td class="px-4 py-2 text-sm text-gray-500">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    ${guarantor.status}
                                </span>
                            </td>
                        `;
                        guarantorsList.appendChild(row);
                    });
                } else {
                    // Show the "no guarantors" message
                    guarantorsList.appendChild(noGuarantorsRow);
                    noGuarantorsRow.style.display = 'table-row';
                }
                
                // Store loan data for create schedule functionality
                modal.dataset.loanId = loan.loan_id;
                modal.dataset.customerName = loan.customer_name;
                
                // Show modal using custom implementation
                modal.style.display = 'block';
                modal.classList.remove('hidden');
                
                // Add event listeners to close buttons
                const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        modal.style.display = 'none';
                        modal.classList.add('hidden');
                    });
                });
                
                // Function to format currency
                function formatCurrency(amount) {
                    return new Intl.NumberFormat('en-KE', {
                        style: 'currency',
                        currency: 'KES'
                    }).format(amount);
                }

                // Function to load loan details
                function loadLoanDetails(loanId) {
                    fetch(`/api/loans/${loanId}`)
                        .then(response => response.json())
                        .then(loan => {
                            // Update outstanding balance
                            document.getElementById('outstandingBalance').value = formatCurrency(loan.outstanding_balance);
                            
                            // Update missed payments if available
                            const daysInArrears = loan.days_in_arrears || 0;
                            const missedInstallments = Math.ceil(daysInArrears / 30);
                            console.log('Calculated missed installments:', missedInstallments, 'from days in arrears:', daysInArrears);
                            document.getElementById('missedPayments').value = missedInstallments;
                            
                            // Set priority based on days in arrears
                            const prioritySelect = document.getElementById('priority');
                            if (prioritySelect) {
                                if (daysInArrears >= 90) {
                                    prioritySelect.value = 'Critical';
                                } else if (daysInArrears >= 60) {
                                    prioritySelect.value = 'High';
                                } else if (daysInArrears >= 30) {
                                    prioritySelect.value = 'Medium';
                                } else {
                                    prioritySelect.value = 'Low';
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Error loading loan details:', error);
                            // Clear fields on error
                            document.getElementById('outstandingBalance').value = '';
                            document.getElementById('missedPayments').value = '';
                        });
                }

                // Add event listener for client select change
                document.getElementById('collectionClientSelect').addEventListener('change', function() {
                    console.log('Selected client:', this.options[this.selectedIndex]);
                    const selectedOption = this.options[this.selectedIndex];
                    const loanSelect = document.getElementById('loanSelect');
                    
                    // Clear existing options
                    loanSelect.innerHTML = '';
                    
                    // Access loans directly from the option object
                    if (selectedOption && selectedOption.loans && selectedOption.loans.length > 0) {
                        console.log('Loans:', selectedOption.loans);
                        selectedOption.loans.forEach(loan => {
                            const option = new Option(
                                `${loan.LoanNo} - ${formatCurrency(loan.LoanAmount)}`,
                                loan.LoanAppID
                            );
                            loanSelect.add(option);
                        });
                        
                        // If there's only one loan, select it automatically
                        if (selectedOption.loans.length === 1) {
                            loanSelect.selectedIndex = 0;
                            const loan = selectedOption.loans[0];
                            console.log('Auto-selecting first loan:', loan);
                            updateLoanDetailsInForm(loan);
                        }
                    }
                });

                // Add event listener for loan select change
                document.getElementById('loanSelect').addEventListener('change', function() {
                    console.log('Selected loan:', this.options[this.selectedIndex]);
                    const selectedOption = this.options[this.selectedIndex];
                    const clientSelect = document.getElementById('collectionClientSelect');
                    const selectedClient = clientSelect.options[clientSelect.selectedIndex];
                    
                    if (selectedClient && selectedClient.loans) {
                        const selectedLoan = selectedClient.loans.find(loan => loan.LoanAppID === selectedOption.value);
                        if (selectedLoan) {
                            console.log('Found selected loan:', selectedLoan);
                            document.getElementById('outstandingBalance').value = formatCurrency(selectedLoan.OutstandingBalance || 0);
                            
                            // Calculate missed payments based on days in arrears
                            const daysInArrears = selectedLoan.DaysInArrears || 0;
                            const missedInstallments = Math.ceil(daysInArrears / 30);
                            console.log('Calculated missed installments:', missedInstallments, 'from days in arrears:', daysInArrears);
                            document.getElementById('missedPayments').value = missedInstallments;
                            
                            // Set priority based on days in arrears
                            const prioritySelect = document.getElementById('priority');
                            if (prioritySelect) {
                                if (daysInArrears >= 90) {
                                    prioritySelect.value = 'Critical';
                                } else if (daysInArrears >= 60) {
                                    prioritySelect.value = 'High';
                                } else if (daysInArrears >= 30) {
                                    prioritySelect.value = 'Medium';
                                } else {
                                    prioritySelect.value = 'Low';
                                }
                            }
                        } else {
                            // Clear fields if no loan selected
                            document.getElementById('outstandingBalance').value = '';
                            document.getElementById('missedPayments').value = '';
                        }
                    }
                });

                // Function to update loan details in the form
                function updateLoanDetails(loan) {
                    console.log('Updating loan details with loan data:', loan);
                    
                    // Update outstanding balance
                    document.getElementById('outstandingBalance').value = formatCurrency(loan.OutstandingBalance || loan.outstanding_balance || 0);
                    
                    // Update missed payments if available
                    console.log('Days in arrears (camelCase):', loan.DaysInArrears);
                    console.log('Days in arrears (snake_case):', loan.days_in_arrears);
                    console.log('Types:', typeof loan.DaysInArrears, typeof loan.days_in_arrears);
                    
                    // Try to parse the value if it's a string or undefined
                    let daysInArrears = 0;
                    if (loan.days_in_arrears !== undefined) {
                        daysInArrears = parseInt(loan.days_in_arrears) || 0;
                    } else if (loan.DaysInArrears !== undefined) {
                        daysInArrears = parseInt(loan.DaysInArrears) || 0;
                    }
                    
                    console.log('Parsed days in arrears:', daysInArrears);
                    const missedInstallments = Math.ceil(daysInArrears / 30);
                    console.log('Calculated missed installments:', missedInstallments, 'from days in arrears:', daysInArrears);
                    
                    // Set the value and verify it was set correctly
                    const missedPaymentsField = document.getElementById('missedPayments');
                    missedPaymentsField.value = missedInstallments;
                    console.log('Set missed payments field to:', missedPaymentsField.value);
                    
                    // Auto-select priority based on days in arrears
                    const prioritySelect = document.getElementById('priority');
                    if (prioritySelect) {
                        if (daysInArrears >= 90) {
                            prioritySelect.value = 'Critical';
                        } else if (daysInArrears >= 60) {
                            prioritySelect.value = 'High';
                        } else if (daysInArrears >= 30) {
                            prioritySelect.value = 'Medium';
                        } else {
                            prioritySelect.value = 'Low';
                        }
                    }
                }

                // Add event listener for create schedule button
                const createScheduleBtn = document.getElementById('create-collection-from-loan');
                createScheduleBtn.addEventListener('click', function() {
                    console.log('Create collection from loan button clicked');
                    console.log('Full loan data:', loan);
                    console.log('Days in arrears:', loan.days_in_arrears);
                    
                    // Close the loan details modal
                    modal.style.display = 'none';
                    modal.classList.add('hidden');
                    
                    // Show the new collection schedule modal
                    const newScheduleModal = document.getElementById('newCollectionScheduleModal');
                    newScheduleModal.classList.remove('hidden');
                    
                    // Pre-populate the client and loan fields
                    const clientSelect = document.getElementById('collectionClientSelect');
                    const loanSelect = document.getElementById('loanSelect');
                    
                    // Create and select the client option
                    const clientOption = {
                        id: loan.loan_id,
                        text: loan.customer_name,
                        loans: [{
                            LoanAppID: loan.loan_id,
                            AccountNo: loan.loan_no,
                            OutstandingBalance: loan.outstanding_balance,
                            DaysInArrears: loan.days_in_arrears || 0
                        }]
                    };
                    
                    // Set client select with the option and data
                    const $clientSelect = $('#collectionClientSelect');
                    $clientSelect.empty()
                        .append(new Option(clientOption.text, clientOption.id, true, true))
                        .trigger('change');
                    
                    // Manually set the client data for loan select to use
                    $clientSelect.data('data', clientOption);
                    
                    // After client is set, populate loan select
                    if (loan.loan_id && loan.loan_no) {
                        const $loanSelect = $('#loanSelect');
                        $loanSelect.empty()
                            .append(new Option(`Loan #${loan.loan_no}`, loan.loan_id, true, true))
                            .trigger('change');
                    }
                    
                    // Update the outstanding balance and other fields
                    document.getElementById('outstandingBalance').value = formatCurrency(loan.outstanding_balance);
                    
                    // Calculate missed payments based on days in arrears
                    console.log('Loan data for missed payments calculation:', loan);
                    console.log('Days in arrears raw value:', loan.days_in_arrears);
                    console.log('Type of days_in_arrears:', typeof loan.days_in_arrears);
                    
                    // Make sure we get a valid number for days in arrears
                    let daysInArrears = 0;
                    if (loan.days_in_arrears !== undefined) {
                        // Force conversion to number
                        daysInArrears = Number(loan.days_in_arrears) || 0;
                    }
                    
                    console.log('Parsed days in arrears:', daysInArrears);
                    const missedInstallments = Math.ceil(daysInArrears / 30);
                    console.log('Calculated missed installments:', missedInstallments, 'from days in arrears:', daysInArrears);
                    
                    // Set the value and verify it was set correctly
                    const missedPaymentsField = document.getElementById('missedPayments');
                    missedPaymentsField.value = missedInstallments;
                    console.log('Set missed payments field to:', missedPaymentsField.value);

                    // Set priority based on days in arrears
                    const prioritySelect = document.getElementById('priority');
                    if (prioritySelect) {
                        if (daysInArrears >= 90) {
                            prioritySelect.value = 'Critical';
                        } else if (daysInArrears >= 60) {
                            prioritySelect.value = 'High';
                        } else if (daysInArrears >= 30) {
                            prioritySelect.value = 'Medium';
                        } else {
                            prioritySelect.value = 'Low';
                        }
                    }
                });
                
                // Close modal when clicking outside
                window.addEventListener('click', function(event) {
                    if (event.target === modal) {
                        modal.style.display = 'none';
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching loan details:', error);
                showNotification('Error', 'Failed to load loan details');
            });
    };

    // Load overdue loans
let overdueLoansData = [];
let overdueCurrentPage = 1;
const overdueItemsPerPage = 10;

async function loadOverdueLoans() {
    try {
        const response = await fetch('/api/overdue-loans');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        const tbody = document.getElementById('overdue-loans-body');
        if (!tbody) {
            throw new Error('Could not find the overdue loans table body element');
        }
        
        if (!Array.isArray(data.data)) {
            throw new Error('Data is not an array');
        }
        
        // Store the data globally for pagination
        overdueLoansData = data.data;
        
        // Update the overdue count in the summary cards
        $('#overdue-count').text(overdueLoansData.length);
        
        // Initialize pagination
        initializeOverduePagination();
        
        // Display the first page
        displayOverduePage(1);
        
        // Update last updated timestamp
        const lastUpdatedEl = document.getElementById('overdue-loans-last-updated');
        if (lastUpdatedEl) {
            lastUpdatedEl.textContent = new Date().toLocaleString();
        }
    } catch (error) {
        console.error('Error loading overdue loans:', error);
        const tbody = document.getElementById('overdue-loans-body');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-4 py-4 text-center">
                        <div class="flex flex-col items-center justify-center text-sm">
                            <svg class="w-8 h-8 text-red-500 dark:text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <p class="text-red-500 dark:text-red-400">Error loading overdue loans</p>
                            <p class="text-gray-500 dark:text-gray-400 text-xs mt-1">${error.message}</p>
                        </div>
                    </td>
                </tr>
            `;
            
            // Hide pagination when there's an error
            document.getElementById('overdue-pagination').classList.add('hidden');
        }
    }
}

// Display a specific page of overdue loans
function displayOverduePage(page) {
    const tbody = document.getElementById('overdue-loans-body');
    if (!tbody) return;
    
    // Clear the table
    tbody.innerHTML = '';
    
    // Calculate start and end indices
    const startIndex = (page - 1) * overdueItemsPerPage;
    const endIndex = Math.min(startIndex + overdueItemsPerPage, overdueLoansData.length);
    
    // No data case
    if (overdueLoansData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4 text-gray-500">
                    No overdue loans found
                </td>
            </tr>
        `;
        document.getElementById('overdue-pagination').classList.add('hidden');
        return;
    } else {
        document.getElementById('overdue-pagination').classList.remove('hidden');
    }
    
    // Update pagination info
    document.getElementById('overdue-range-start').textContent = startIndex + 1;
    document.getElementById('overdue-range-end').textContent = endIndex;
    document.getElementById('overdue-total').textContent = overdueLoansData.length;
    document.getElementById('overdue-current-page').textContent = page;
    document.getElementById('overdue-total-pages').textContent = Math.ceil(overdueLoansData.length / overdueItemsPerPage);
    
    // Display the current page data
    for (let i = startIndex; i < endIndex; i++) {
        const loan = overdueLoansData[i];
        const row = tbody.insertRow();
        row.innerHTML = `
            <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200 whitespace-nowrap">${loan.loan_no || 'N/A'}</td>
            <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200 whitespace-nowrap">${loan.customer_name || 'N/A'}</td>
            <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200 text-right whitespace-nowrap">${formatCurrency(loan.outstanding_balance || 0)}</td>
            <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200 text-right whitespace-nowrap">${formatCurrency(loan.arrears_amount || 0)}</td>
            <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200 text-right whitespace-nowrap">
                <span class="${loan.arrears_days > 30 ? 'text-red-600 dark:text-red-400 font-medium' : ''}">${loan.arrears_days || 0}</span>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-sm">
                <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500" onclick="viewLoanDetails('${loan.loan_id}')">
                    <span class="flex items-center">
                        <svg class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Details
                    </span>
                </button>
            </td>
        `;
    }
}

// Initialize pagination controls
function initializeOverduePagination() {
    const totalPages = Math.ceil(overdueLoansData.length / overdueItemsPerPage);
    
    // Update button states
    updateOverduePaginationButtons();
    
    // Add event listeners for pagination controls
    document.getElementById('overdue-prev').addEventListener('click', function() {
        if (overdueCurrentPage > 1) {
            overdueCurrentPage--;
            displayOverduePage(overdueCurrentPage);
            updateOverduePaginationButtons();
        }
    });
    
    document.getElementById('overdue-next').addEventListener('click', function() {
        if (overdueCurrentPage < totalPages) {
            overdueCurrentPage++;
            displayOverduePage(overdueCurrentPage);
            updateOverduePaginationButtons();
        }
    });
    
    document.getElementById('overdue-prev-mobile').addEventListener('click', function() {
        if (overdueCurrentPage > 1) {
            overdueCurrentPage--;
            displayOverduePage(overdueCurrentPage);
            updateOverduePaginationButtons();
        }
    });
    
    document.getElementById('overdue-next-mobile').addEventListener('click', function() {
        if (overdueCurrentPage < totalPages) {
            overdueCurrentPage++;
            displayOverduePage(overdueCurrentPage);
            updateOverduePaginationButtons();
        }
    });
}

// Update pagination button states
function updateOverduePaginationButtons() {
    const totalPages = Math.ceil(overdueLoansData.length / overdueItemsPerPage);
    
    // Disable/enable previous buttons
    document.getElementById('overdue-prev').disabled = overdueCurrentPage === 1;
    document.getElementById('overdue-prev').classList.toggle('opacity-50', overdueCurrentPage === 1);
    document.getElementById('overdue-prev-mobile').disabled = overdueCurrentPage === 1;
    document.getElementById('overdue-prev-mobile').classList.toggle('opacity-50', overdueCurrentPage === 1);
    
    // Disable/enable next buttons
    document.getElementById('overdue-next').disabled = overdueCurrentPage === totalPages || totalPages === 0;
    document.getElementById('overdue-next').classList.toggle('opacity-50', overdueCurrentPage === totalPages || totalPages === 0);
    document.getElementById('overdue-next-mobile').disabled = overdueCurrentPage === totalPages || totalPages === 0;
    document.getElementById('overdue-next-mobile').classList.toggle('opacity-50', overdueCurrentPage === totalPages || totalPages === 0);
}

    // Initialize tab functionality
    function initializeTabs() {
        const tabs = document.querySelectorAll('[data-tabs-target]');
        const tabContents = document.querySelectorAll('[role=\'tabpanel\']');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = document.querySelector(tab.dataset.tabsTarget);
                
                // Hide all tab contents
                tabContents.forEach(tabContent => {
                    tabContent.classList.add('hidden');
                    tabContent.classList.remove('block');
                });
                
                // Remove active class from all tabs
                tabs.forEach(t => {
                    t.classList.remove('active', 'border-blue-600', 'text-blue-600');
                    t.classList.add('border-transparent');
                    t.setAttribute('aria-selected', 'false');
                });
                
                // Show the selected tab content
                target.classList.remove('hidden');
                target.classList.add('block');
                
                // Add active class to the clicked tab
                tab.classList.add('active', 'border-blue-600', 'text-blue-600');
                tab.classList.remove('border-transparent');
                tab.setAttribute('aria-selected', 'true');
                
                // If switching to overdue loans tab, refresh the data
                if (tab.id === 'overdue-tab') {
                    loadOverdueLoans();
                }
            });
        });
    }
    
    // Initialize filter toggle functionality
    function initializeFilterToggle() {
        const filterToggle = document.getElementById('filter-toggle');
        const filterContent = document.getElementById('filter-content');
        const filterArrow = document.getElementById('filter-arrow');
        
        if (filterToggle && filterContent) {
            filterToggle.addEventListener('click', () => {
                filterContent.classList.toggle('hidden');
                filterArrow.classList.toggle('rotate-180');
            });
        }
        
        // Initialize filter buttons
        const applyFiltersBtn = document.getElementById('apply-filters');
        const resetFiltersBtn = document.getElementById('reset-filters');
        
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                const filters = {
                    staff: $('#filterStaff').val(),
                    priority: $('#filterPriority').val(),
                    status: $('#filterStatus').val(),
                    method: $('#filterMethod').val()
                };
                loadCollectionSchedules(filters);
            });
        }
        
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', () => {
                $('#filterStaff').val('');
                $('#filterPriority').val('');
                $('#filterStatus').val('');
                $('#filterMethod').val('');
                loadCollectionSchedules();
            });
        }
    }
    
// Update summary cards with improved error handling
function updateSummaryCards() {
    console.log('Updating summary cards...');
    fetch('/api/collection-schedules/total')
        .then(response => {
            if (!response.ok) {
                console.error(`HTTP error: ${response.status}`);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('API response:', data);
            // Ensure that the API returned success and the expected data exists
            if (data.status === 'success' && data.data) {
                const stats = data.data;
                console.log('Statistics:', stats);
                
                // Update total schedules element
                const totalSchedulesEl = document.getElementById('total-schedules');
                if (totalSchedulesEl) {
                    totalSchedulesEl.textContent = stats.total_schedules;
                } else {
                    console.error('Element with id "total-schedules" not found.');
                }
                
                // Update pending followups element
                const pendingFollowupsEl = document.getElementById('pending-followups');
                if (pendingFollowupsEl) {
                    pendingFollowupsEl.textContent = stats.pending_schedules;
                } else {
                    console.error('Element with id "pending-followups" not found.');
                }
                
                // Update completion rate element
                const completionRateEl = document.getElementById('completion-rate');
                if (completionRateEl) {
                    if (typeof stats.completion_rate === 'number') {
                        completionRateEl.textContent = stats.completion_rate.toFixed(1) + '%';
                    } else {
                        console.error('Completion rate is not a number:', stats.completion_rate);
                        completionRateEl.textContent = '--';
                    }
                } else {
                    console.error('Element with id "completion-rate" not found.');
                }
            } else {
                console.error('API returned error or unexpected data format:', data);
                // Set default values in case of error
                document.getElementById('total-schedules').textContent = '--';
                document.getElementById('pending-followups').textContent = '--';
                document.getElementById('completion-rate').textContent = '--';
            }
        })
        .catch(error => {
            console.error('Error fetching schedule statistics:', error);
            // Show error message or default values for each card
            const totalSchedulesEl = document.getElementById('total-schedules');
            const pendingFollowupsEl = document.getElementById('pending-followups');
            const completionRateEl = document.getElementById('completion-rate');
            if (totalSchedulesEl) totalSchedulesEl.textContent = '--';
            if (pendingFollowupsEl) pendingFollowupsEl.textContent = '--';
            if (completionRateEl) completionRateEl.textContent = '--';
        });
}

    // Add a function to update summary cards periodically
    function updateSummaryCardsPeriodically() {
        console.log('Starting periodic updates...');
        updateSummaryCards();
        // Update every 5 minutes
        setInterval(updateSummaryCards, 300000);
    }


    // Event handler for new collection schedule button
    $('#newCollectionScheduleBtn').on('click', function() {
        // Reset form to create mode
        $('#newCollectionScheduleForm').data('mode', 'create');
        $('#newCollectionScheduleForm').data('schedule-id', '');
        $('#createScheduleModalTitle').text('Create Collection Schedule');
        $('#createScheduleModalSubmit').text('Create Schedule');
        
        // Reset form fields
        $('#newCollectionScheduleForm')[0].reset();
        $('#collectionClientSelect').val('').trigger('change');
        $('#loanSelect').val('').trigger('change');
        $('#staffSelect').val('').trigger('change');
        $('#supervisorSelect').val('').trigger('change');
        $('#managerSelect').val('').trigger('change');
        
        // Show the modal
        document.getElementById('newCollectionScheduleModal').classList.remove('hidden');
    });

    // Event handler for update button (only shown to assigned staff)
    $(document).on('click', '.edit-schedule-btn', function() {
        const scheduleId = $(this).attr('data-schedule-id'); // Use attr instead of data
        
        // Fetch schedule details
        $.ajax({
            url: `/api/collection-schedules/${scheduleId}`,
            method: 'GET',
            success: function(response) {
                if (response.status === 'success') {
                    const schedule = response.data;
                    
                    console.log('API Response:', response);
                    console.log('Collection Location:', schedule.collection_location);
                    
                    // Update form to edit mode
                    $('#newCollectionScheduleForm').data('mode', 'edit');
                    // Set form to edit mode and update UI
                    $('#newCollectionScheduleForm').data('schedule-id', scheduleId);
                    $('#createScheduleModalTitle').text('Update Collection Schedule');
                    $('button[type="submit"]', '#newCollectionScheduleForm').text('Update Schedule');
                    
                    // Populate client and loan information with proper data
                    if (schedule.client_id && schedule.borrower_name) {
                        // Create client option with loans data
                        const clientOption = {
                            id: schedule.client_id,
                            text: schedule.borrower_name,
                            loans: [{
                                LoanAppID: schedule.loan_id,
                                AccountNo: schedule.loan_account,
                                OutstandingBalance: schedule.outstanding_balance,
                                DaysInArrears: schedule.missed_payments * 30 // Approximate based on missed payments
                            }]
                        };
                        
                        // Set client select with the option and data
                        const $clientSelect = $('#collectionClientSelect');
                        $clientSelect.empty()
                            .append(new Option(clientOption.text, clientOption.id, true, true))
                            .trigger('change');
                        
                        // Manually set the client data for loan select to use
                        $clientSelect.data('data', clientOption);
                        
                        // After client is set, populate loan select
                        if (schedule.loan_id && schedule.loan_account) {
                            const $loanSelect = $('#loanSelect');
                            $loanSelect.empty()
                                .append(new Option(schedule.loan_account, schedule.loan_id, true, true))
                                .trigger('change');
                        }
                    }
                    
                    // Update display fields and form inputs
                    $('#loanAccountDisplay').text(schedule.loan_account || 'N/A');
                    $('#memberNameDisplay').text(schedule.borrower_name || 'N/A');
                    
                    // Set Outstanding Balance
                    const outstandingBalance = schedule.outstanding_balance || 0;
                    $('#outstandingBalanceDisplay').text(formatCurrency(outstandingBalance));
                    $('#outstandingBalance').val(formatCurrency(outstandingBalance));
                    
                    // Set Missed Payments
                    const missedPayments = schedule.missed_payments || 0;
                    $('#missedPaymentsDisplay').text(missedPayments);
                    $('#missedPayments').val(missedPayments);
                    
                    // Set Collection Notes and Special Instructions
                    $('#task_description').val(schedule.task_description || '');
                    $('#instructions').val(schedule.special_instructions || '');
                    
                    // Populate staff assignments with proper data
                    if (schedule.assigned_id && schedule.staff_name) {
                        const staffOption = new Option(schedule.staff_name, schedule.assigned_id, true, true);
                        $('#staffSelect').empty().append(staffOption).trigger('change');
                    }
                    
                    if (schedule.supervisor_id && schedule.supervisor_name) {
                        const supervisorOption = new Option(schedule.supervisor_name, schedule.supervisor_id, true, true);
                        $('#supervisorSelect').empty().append(supervisorOption).trigger('change');
                    }
                    
                    if (schedule.manager_id && schedule.manager_name) {
                        const managerOption = new Option(schedule.manager_name, schedule.manager_id, true, true);
                        $('#managerSelect').empty().append(managerOption).trigger('change');
                    }
                    
                    // Update display fields for staff
                    $('#assignedOfficerDisplay').text(schedule.staff_name || 'Not Assigned');
                    $('#supervisorDisplay').text(schedule.supervisor_name || 'Not Assigned');
                    
                    // Populate collection strategy
                    $('#priority').val(schedule.collection_priority);
                    $('#method').val(schedule.preferred_collection_method);
                    $('#frequency').val(schedule.follow_up_frequency);
                    
                    // Populate schedule details
                    $('#nextFollowUp').val(schedule.next_follow_up_date || '');
                    $('#promisedPaymentDate').val(schedule.promised_payment_date || '');
                    
                    // Populate additional information
                    $('#collectionLocation').val(schedule.collection_location || '');
                    $('#bestContactTime').val(schedule.best_contact_time || '');
                    $('#alternativeContact').val(schedule.alternative_contact || '');
                    $('#task_description').val(schedule.task_description || '');
                    $('#instructions').val(schedule.special_instructions || '');
                    
                    // Show the modal
                    document.getElementById('newCollectionScheduleModal').classList.remove('hidden');
                } else {
                    showNotification('Error', response.message || 'Failed to fetch schedule details');
                }
            },
            error: function(xhr) {
                showNotification('Error', 'Failed to fetch schedule details');
                console.error('Error fetching schedule:', xhr);
            }
        });
    });

    // Event handler for submit button (only shown to assigned staff)
    $(document).on('click', '.submit-schedule-btn', function() {
        const scheduleId = $(this).attr('data-schedule-id'); // Use attr instead of data
        $('#commentScheduleId').val(scheduleId);
        $('#commentAction').val('submit');
        $('#comment').val(''); // Clear any previous comments
        document.getElementById('commentModal').classList.remove('hidden');
    });

    // Event handler for edit button
    $(document).on('click', '.edit-schedule-btn', function() {
        const scheduleId = $(this).attr('data-schedule-id'); // Use attr instead of data
        // TODO: Implement edit functionality
        console.log('Edit schedule:', scheduleId);
    });

    // Event handler for delete button
    $(document).on('click', '.delete-schedule-btn', function() {
        const scheduleId = $(this).data('id');
        if (confirm('Are you sure you want to delete this schedule?')) {
            $.ajax({
                url: `/api/collection-schedules/${scheduleId}`,
                method: 'DELETE',
                success: function() {
                    showNotification('Success', 'Schedule deleted successfully');
                    loadCollectionSchedules(); // Refresh the list
                },
                error: function(xhr) {
                    showNotification('Error', xhr.responseJSON?.error || 'Failed to delete schedule');
                }
            });
        }
    });

    // Handle comment submission
    $('#submitComment').click(function() {
        const scheduleId = $('#commentScheduleId').val();
        const action = $('#commentAction').val();
        const comment = $('#comment').val();

        if (!comment) {
            alert('Please enter a comment');
            return;
        }

        // Send to appropriate endpoint based on action
        const endpoint = action === 'update' ? 'update-progress' : 'submit';
        
        $.ajax({
            url: `/api/collection-schedules/${scheduleId}/${endpoint}`,
            method: 'POST',
            data: JSON.stringify({ comment: comment }),
            contentType: 'application/json',
            success: function(response) {
                $('#commentModal').modal('hide');
                showNotification('Success', `Collection schedule ${action}d successfully`);
                loadCollectionSchedules(); // Refresh the list
                $('#comment').val(''); // Clear the comment
            },
            error: function(xhr) {
                showNotification('Error', `Failed to ${action} collection schedule`);
                console.error(`Error ${action}ing schedule:`, xhr);
            }
        });
    });

    // Store current user info
    let currentUser = null;

    // Function to update pagination controls
    function updatePagination(pagination) {
        const paginationContainer = $('#paginationContainer');
        if (!pagination || pagination.total === 0) {
            paginationContainer.empty();
            return;
        }

        const { page, pages, total, per_page } = pagination;
        
        let paginationHtml = `
            <div class="flex flex-col sm:flex-row justify-between items-center gap-4">
                <div>
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                        Showing <span class="font-medium">${Math.min((page - 1) * per_page + 1, total)}</span> to 
                        <span class="font-medium">${Math.min(page * per_page, total)}</span> of 
                        <span class="font-medium">${total}</span> schedules
                    </p>
                </div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <!-- Previous button -->
                    <button ${page > 1 ? '' : 'disabled'} data-page="${page - 1}"
                        class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        <span class="sr-only">Previous</span>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </button>`;

        // Add page numbers
        for (let i = 1; i <= pages; i++) {
            if (
                i === 1 || // First page
                i === pages || // Last page
                (i >= page - 1 && i <= page + 1) // Pages around current page
            ) {
                paginationHtml += `
                    <button data-page="${i}" 
                        class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium 
                        ${page === i 
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600 dark:bg-blue-900 dark:border-blue-500 dark:text-blue-300' 
                            : 'bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 dark:border-gray-600'}"
                        ${page === i ? 'aria-current="page"' : ''}>
                        ${i}
                    </button>`;
            } else if (
                i === 2 || // Ellipsis after first page
                i === pages - 1 // Ellipsis before last page
            ) {
                paginationHtml += `
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400">
                        ...
                    </span>`;
            }
        }

        paginationHtml += `
                    <!-- Next button -->
                    <button ${page < pages ? '' : 'disabled'} data-page="${page + 1}"
                        class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        <span class="sr-only">Next</span>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </button>
                </nav>
            </div>`;

        paginationContainer.html(paginationHtml);

        // Add click handlers for pagination buttons
        paginationContainer.find('button[data-page]').on('click', function() {
            const newPage = $(this).data('page');
            const currentFilters = new URLSearchParams(window.location.search);
            currentFilters.set('page', newPage);
            loadCollectionSchedules(Object.fromEntries(currentFilters));
        });
    }

    // Function to fetch current user info
    function fetchCurrentUser() {
        return $.ajax({
            url: '/api/current-user',
            method: 'GET'
        }).then(function(response) {
            if (response.status === 'success') {
                currentUser = response.data;
                return currentUser;
            } else {
                throw new Error(response.message || 'Failed to fetch user info');
            }
        });
    }

    // Initialize application
    async function initializeApp() {
        try {
            await fetchCurrentUser();
            loadCollectionSchedules();
            loadOverdueLoans();
            initializeTabs();
        } catch (error) {
            console.error('Error initializing app:', error);
            showNotification('Error', 'Failed to initialize application');
        }
    }

    // Initialize application
    initializeApp();
    initializeFilterToggle();

    // Refresh overdue loans every 5 minutes
    setInterval(loadOverdueLoans, 5 * 60 * 1000);
});

// Update overdue loans endpoint to use the correct API path
async function loadOverdueLoans() {
    try {
        const response = await fetch('/api/overdue-loans');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        const tbody = document.getElementById('overdue-loans-body');
        if (!tbody) {
            throw new Error('Could not find the overdue loans table body element');
        }
        
        if (!Array.isArray(data.data)) {
            throw new Error('Data is not an array');
        }
        
        // Store the data globally for pagination
        overdueLoansData = data.data;
        
        // Update the overdue count in the summary cards
        $('#overdue-count').text(overdueLoansData.length);
        
        // Initialize pagination
        initializeOverduePagination();
        
        // Display the first page
        displayOverduePage(1);
        
        // Update last updated timestamp
        const lastUpdatedEl = document.getElementById('overdue-loans-last-updated');
        if (lastUpdatedEl) {
            lastUpdatedEl.textContent = new Date().toLocaleString();
        }
    } catch (error) {
        console.error('Error loading overdue loans:', error);
        const tbody = document.getElementById('overdue-loans-body');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-4 py-4 text-center">
                        <div class="flex flex-col items-center justify-center text-sm">
                            <svg class="w-8 h-8 text-red-500 dark:text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <p class="text-red-500 dark:text-red-400">Error loading overdue loans</p>
                            <p class="text-gray-500 dark:text-gray-400 text-xs mt-1">${error.message}</p>
                        </div>
                    </td>
                </tr>
            `;
            
            // Hide pagination when there's an error
            document.getElementById('overdue-pagination').classList.add('hidden');
        }
    }
}

// Handle view progress button click
$(document).on('click', '.view-progress-btn', function() {
    const scheduleId = $(this).attr('data-schedule-id'); // Use attr instead of data
    
    // Load progress updates
    loadProgressUpdates(scheduleId);
});

// Handle modal close button
$(document).on('click', '[data-bs-dismiss="modal"]', function() {
    const modal = document.getElementById('viewProgressModal');
    if (modal) {
        modal.classList.add('hidden');
    }
});

// Function to load progress updates
function loadProgressUpdates(scheduleId) {
    console.log('Loading progress updates for schedule ID:', scheduleId);
    
    $.ajax({
        url: `/api/collection-schedules/${scheduleId}/progress`,
        method: 'GET',
        success: function(response) {
            console.log('Progress updates response:', response);
            console.log('Response type:', typeof response);
            console.log('Response keys:', Object.keys(response));
            
            if (response.error) {
                console.error('Error loading progress updates:', response.error);
                showNotification('Error', 'Failed to load progress updates. Please try again.');
                return;
            }

            const updatesList = $('#progressUpdatesList');
            updatesList.empty();

            // Get the updates array from the response
            const updates = response.updates || [];
            console.log('Updates array:', updates);
            console.log('Updates array length:', updates.length);

            if (!Array.isArray(updates)) {
                console.error('Invalid response format:', response);
                updatesList.append(`
                    <tr>
                        <td colspan="6" class="text-center py-4 text-gray-500">
                            No progress updates yet
                        </td>
                    </tr>
                `);
                return;
            }

            if (updates.length === 0) {
                updatesList.append(`
                    <tr>
                        <td colspan="6" class="text-center py-4 text-gray-500">
                            No progress updates yet
                        </td>
                    </tr>
                `);
                return;
            }

            updates.forEach(update => {
                console.log('Processing update:', update);
                
                // Format date directly
                const date = new Date(update.created_at);
                const formattedDate = date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit'
                });
                
                // Format amount directly
                const amount = update.amount || 0;
                const cleanAmount = parseFloat(String(amount).replace(/[^0-9.-]+/g, ''));
                const formattedAmount = isNaN(cleanAmount) ? 'N/A' : cleanAmount.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });

                // Format method with better styling
                const method = update.collection_method || 'Not specified';
                const formattedMethod = `
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${method}
                    </span>
                `;

                // Format status with color coding
                const status = update.status || 'Not specified';
                let statusClass = 'bg-gray-100 text-gray-800';
                if (status.toLowerCase() === 'in_progress') {
                    statusClass = 'bg-yellow-100 text-yellow-800';
                } else if (status.toLowerCase() === 'completed') {
                    statusClass = 'bg-green-100 text-green-800';
                } else if (status.toLowerCase() === 'failed') {
                    statusClass = 'bg-red-100 text-red-800';
                }
                const formattedStatus = `
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusClass}">
                        ${status}
                    </span>
                `;

                updatesList.append(`
                    <tr>
                        <td class="px-4 py-3 whitespace-nowrap text-sm">${formattedDate}</td>
                        <td class="px-4 py-3 whitespace-nowrap text-sm">${formattedAmount}</td>
                        <td class="px-4 py-3 whitespace-nowrap text-sm">${formattedMethod}</td>
                        <td class="px-4 py-3 whitespace-nowrap text-sm">${formattedStatus}</td>
                        <td class="px-4 py-3 whitespace-normal text-sm">${update.notes || 'No notes provided'}</td>
                        <td class="px-4 py-3 whitespace-nowrap text-sm">
                            ${update.attachment_url ? `
                                <a href="${update.attachment_url}" class="text-sm text-blue-600 hover:text-blue-800 flex items-center" target="_blank">
                                    <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    View attachment
                                </a>
                            ` : 'N/A'}
                        </td>
                    </tr>
                `);
            });

            // Show the modal after data is loaded
            const modal = document.getElementById('viewProgressModal');
            if (modal) {
                modal.classList.remove('hidden');
            }
        },
        error: function(xhr) {
            console.error('Error loading progress updates:', xhr.responseText);
            showNotification('Error', 'Failed to load progress updates. Please try again.');
        }
    });
}


$(document).on('click', '.submit-schedule-btn', function() {
    const scheduleId = $(this).attr('data-schedule-id');
    
    console.log("Button Clicked, Schedule ID:", scheduleId);
    
    // Set the schedule ID in the form
    $('#supervisorUpdateScheduleId').val(scheduleId);
    
    // Reset the form
    $('#supervisorUpdateForm')[0].reset();
    
    // Hide other modals if any
    $('.modal').addClass('hidden');

    // Show the modal
    const modal = document.getElementById('submitSupervisorUpdateModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'block'; // Ensure visibility
    } else {
        console.error("Modal not found!");
    }
});


// Handle supervisor update form submission
$(document).on('submit', '#supervisorUpdateForm', function(e) {
    e.preventDefault();
    
    const form = $(this);
    const scheduleId = form.find('#supervisorUpdateScheduleId').val();
    const action = form.find('#workflowAction').val();
    const comment = form.find('#supervisorComment').val();
    const attachment = form.find('#supervisorAttachment')[0].files[0];

    // Validate required fields
    if (!action || !comment) {
        showError('Please select an action and provide a comment.');
        return;
    }

    // Create FormData object
    const formData = new FormData();
    formData.append('action', action);
    formData.append('comment', comment);
    
    if (attachment) {
        formData.append('attachment', attachment);
    }


    // Submit the form
    $.ajax({
        url: `/api/collection-schedules/${scheduleId}/supervisor-update`,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.message) {
                // Close modal and reset form
                closeSupervisorUpdateModal();
                $('#supervisorUpdateForm')[0].reset();
                
                // Refresh schedule details
                //loadCollectionScheduleDetails(scheduleId);
            }
        },
        error: function(xhr) {
            if (xhr.responseJSON && xhr.responseJSON.error) {
                showError(xhr.responseJSON.error);
            } else {
                showError('An error occurred while submitting the update.');
            }
        }
    });
});

function closeSupervisorUpdateModal() {
    const modal = document.getElementById('submitSupervisorUpdateModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('block'); // optional depending on how you show it
        modal.classList.remove('opacity-100');
        modal.classList.add('opacity-0');
    } else {
        console.warn("Modal not found!");
    }
}

// Function to fetch and display submission status for a schedule
function loadSubmissionStatus(scheduleId) {
    $.ajax({
        url: '/api/collection-schedules/submission-status',
        method: 'GET',
        success: function(response) {
            if (response.status === 'error') {
                console.error('Error loading submission status:', response.message);
                return;
            }
            
            // Find the status for this specific schedule
            const status = response.data.schedules.find(s => s.schedule_id == scheduleId);
            
            if (status) {
                $(`#submission-status-${scheduleId}`).text(status.submitted ? 'Submitted' : 'Not Submitted');
                $(`#current-step-${scheduleId}`).text(status.current_step || '--');
            } else {
                $(`#submission-status-${scheduleId}`).text('Not Submitted');
                $(`#current-step-${scheduleId}`).text('--');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching submission status:', error);
        }
    });
}
