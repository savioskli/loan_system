document.addEventListener('DOMContentLoaded', function() {
    // Helper functions
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }
    
    // Initialize tabs and filters
    initializeTabs();
    initializeFilterToggle();
    
    // Modal handling
    const modal = document.getElementById('newCollectionScheduleModal');
    const openModalBtn = document.getElementById('newCollectionScheduleBtn');
    const closeModalBtn = document.getElementById('closeCollectionScheduleModal');

    // Initialize Select2 dropdowns
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
    $('#staffSelect').select2(staffSelect2Config);
    $('#supervisorSelect').select2(supervisorSelect2Config);
    $('#managerSelect').select2(managerSelect2Config);
});

    $(document).ready(function() {
   
        // Initialize client select
        initializeClientSelect('#collectionClientSelect', true);

         $('#loanSelect').select2({
            theme: 'bootstrap-5',
            placeholder: 'Select a Loan Account',
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
                loanSelect.append(new Option(loan.LoanNo, loan.LoanAppID, false, false)); // Add each LoanNo
            });
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
            success: function(schedules) {
                console.log('Received schedules:', schedules);
                const scheduleList = $('#collectionSchedulesList');
                scheduleList.empty();
                
                if (!schedules || schedules.length === 0) {
                    scheduleList.append(`
                        <div class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
                            <p class="text-center text-gray-600 dark:text-gray-400">No collection schedules found.</p>
                        </div>
                    `);
                    return;
                }
                
                schedules.forEach(schedule => {
                    try {
                        const borrowerInfo = schedule.borrower_name ? 
                            `${schedule.loan_account} - ${schedule.borrower_name}` : 
                            schedule.loan_account || 'Unknown Borrower';
                        
                        const staffName = schedule.staff_name || 'Unassigned';
                        const nextFollowUp = schedule.next_follow_up_date ? formatDate(schedule.next_follow_up_date) : 'Not scheduled';
                        const method = schedule.preferred_collection_method || 'Not specified';
                        
                        const scheduleHtml = `
                            <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden mb-4">
                                <!-- Card Header -->
                                <div class="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 flex flex-wrap items-center justify-between">
                                    <div class="flex items-center flex-wrap">
                                        <h3 class="text-md font-semibold text-gray-900 dark:text-white truncate mr-2">
                                            ${borrowerInfo}
                                        </h3>
                                        ${schedule.collection_priority ? `
                                        <span class="mr-2 px-2 py-0.5 text-xs font-medium rounded-full ${getPriorityClass(schedule.collection_priority)}">
                                            ${schedule.collection_priority}
                                        </span>
                                        ` : ''}
                                        ${schedule.progress_status ? `
                                        <span class="px-2 py-0.5 text-xs font-medium rounded-full ${getStatusClass(schedule.progress_status)}">
                                            ${schedule.progress_status}
                                        </span>
                                        ` : ''}
                                        ${schedule.escalation_level ? `
                                        <span class="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300">
                                            Escalation ${schedule.escalation_level}
                                        </span>
                                        ` : ''}
                                    </div>
                                    <div class="flex items-center mt-2 sm:mt-0">
                                        <button class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 mr-3" onclick="viewLoanDetails('${schedule.loan_id}')">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                        </button>
                                        <button class="update-progress-btn text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 mr-3"
                                                data-id="${schedule.id}" data-loan-id="${schedule.loan_id}" data-borrower-name="${schedule.borrower_name || 'Unknown'}">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        </button>
                                        ${schedule.progress_status !== 'Escalated' ? `
                                        <button class="escalate-btn text-yellow-500 hover:text-yellow-700 dark:text-yellow-400 dark:hover:text-yellow-300 mr-3"
                                                data-id="${schedule.id}">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                                        </button>
                                        ` : ''}
                                        <button class="delete-btn text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                                                data-id="${schedule.id}">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- Card Body -->
                                <div class="p-4">
                                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                        <div>
                                            <p class="text-gray-500 dark:text-gray-400">Assigned To</p>
                                            <p class="font-medium">${staffName}</p>
                                        </div>
                                        <div>
                                            <p class="text-gray-500 dark:text-gray-400">Next Follow-up</p>
                                            <p class="font-medium">${nextFollowUp}</p>
                                        </div>
                                        <div>
                                            <p class="text-gray-500 dark:text-gray-400">Method</p>
                                            <p class="font-medium">${method}</p>
                                        </div>
                                        <div>
                                            <p class="text-gray-500 dark:text-gray-400">Attempts</p>
                                            <p class="font-medium">${schedule.attempts_made || 0} / ${schedule.attempts_allowed || '-'}</p>
                                        </div>
                                        ${schedule.promised_payment_date ? `
                                        <div class="col-span-2">
                                            <p class="text-gray-500 dark:text-gray-400">Promised Payment</p>
                                            <p class="font-medium">${formatDate(schedule.promised_payment_date)}</p>
                                        </div>
                                        ` : ''}
                                    </div>
                                    
                                    ${(schedule.task_description || schedule.special_instructions) ? `
                                    <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                                        ${schedule.task_description ? `
                                        <div class="mb-2">
                                            <p class="text-gray-500 dark:text-gray-400 text-sm">Task Description</p>
                                            <p class="text-sm">${schedule.task_description}</p>
                                        </div>
                                        ` : ''}
                                        
                                        ${schedule.special_instructions ? `
                                        <div>
                                            <p class="text-gray-500 dark:text-gray-400 text-sm">Special Instructions</p>
                                            <p class="text-sm">${schedule.special_instructions}</p>
                                        </div>
                                        ` : ''}
                                    </div>
                                    ` : ''}
                                </div>
                            </div>
                        `;
                        scheduleList.append(scheduleHtml);
                    } catch (error) {
                        console.error('Error rendering schedule:', error, schedule);
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error('Error loading schedules:', error);
                const scheduleList = $('#collectionSchedulesList');
                scheduleList.empty().append(`
                    <div class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
                        <p class="text-center text-red-600">Error loading collection schedules. Please try again.</p>
                    </div>
                `);
            }
        });
    }

    // Create new collection schedule
$('#newCollectionScheduleForm').submit(function(event) {
    event.preventDefault();
    const formData = {
        staff_id: $('#staffSelect').val(),
        loan_id: $('#loanSelect').val(),
        client_id: $('#collectionClientSelect').val(),
        follow_up_deadline: $('#deadline').val(),
        collection_priority: $('#priority').val(),
        follow_up_frequency: $('#frequency').val(),
        next_follow_up_date: $('#nextFollowUp').val(),
        promised_payment_date: $('#promisedPaymentDate').val(), // New field
        attempts: $('#attempts').val(), // New field
        preferred_collection_method: $('#method').val(), // Ensure this is included
        task_description: $('#description').val(),
        special_instructions: $('#instructions').val(),
        branch_id: $('#branchInput').val() // Include assigned branch
    };

    $.ajax({
        url: '/api/new-collection-schedules',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            modal.classList.add('hidden');
            showNotification('Success', 'Collection schedule created successfully');
            loadCollectionSchedules();
        },
        error: function(xhr) {
            showNotification('Error', xhr.responseJSON?.error || 'Failed to create schedule');
        }
    });
});

    // Update progress and show payment history modal
    $(document).on('click', '.update-progress-btn', function() {
        const scheduleId = $(this).data('id');
        const loanId = $(this).data('loan-id');
        const borrowerName = $(this).data('borrower-name');
        
        // Set the schedule ID and loan ID in the payment form
        $('#paymentScheduleId').val(scheduleId);
        $('#paymentLoanId').val(loanId);
        
        // Set default payment date to current date and time
        const now = new Date();
        const formattedDate = now.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:MM
        $('#paymentDate').val(formattedDate);
        
        // Load payment history for this schedule
        loadPaymentHistory(scheduleId);
        
        // Show the payment history modal
        $('#paymentHistoryModal').removeClass('hidden');
    });
    
    // Close payment history modal
    $('#closePaymentHistoryModal, #cancelPaymentBtn').on('click', function() {
        $('#paymentHistoryModal').addClass('hidden');
    });
    
    // Close new collection schedule modal - using event delegation
    $(document).on('click', '#closeCollectionScheduleModal', function() {
        const modal = document.getElementById('newCollectionScheduleModal');
        modal.classList.add('hidden');
        // Reset form
        document.getElementById('newCollectionScheduleForm').reset();
        // Re-enable selects
        document.getElementById('collectionClientSelect').disabled = false;
        document.getElementById('loanSelect').disabled = false;
    });
    
    // Load payment history for a schedule
    function loadPaymentHistory(scheduleId) {
        $.ajax({
            url: `/api/collection-schedules/${scheduleId}/payments`,
            method: 'GET',
            success: function(data) {
                // Clear existing table rows
                const tableBody = $('#paymentHistoryTableBody');
                tableBody.empty();
                
                // Check if there are payments
                if (data && data.length > 0) {
                    // Add each payment to the table
                    data.forEach(payment => {
                        const attachmentLink = payment.attachment_url ? 
                            `<a href="${payment.attachment_url}" target="_blank" class="text-indigo-600 hover:text-indigo-900">View</a>` : 
                            'None';
                            
                        tableBody.append(`
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatDate(payment.payment_date)}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatCurrency(payment.amount)}</td>
                                <td class="px-6 py-4 text-sm text-gray-500">${payment.description}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${attachmentLink}</td>
                            </tr>
                        `);
                    });
                } else {
                    // Show no payments message
                    tableBody.append(`
                        <tr>
                            <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">No payment records found</td>
                        </tr>
                    `);
                }
            },
            error: function(xhr) {
                showNotification('Error', xhr.responseJSON?.error || 'Failed to load payment history');
                // Show error message in table
                $('#paymentHistoryTableBody').html(`
                    <tr>
                        <td colspan="4" class="px-6 py-4 text-center text-sm text-red-500">Failed to load payment history</td>
                    </tr>
                `);
            }
        });
    }
    
    // Handle new payment form submission
    $('#newPaymentForm').submit(function(event) {
        event.preventDefault();
        
        const scheduleId = $('#paymentScheduleId').val();
        const formData = new FormData(this);
        
        $.ajax({
            url: `/api/collection-schedules/${scheduleId}/payments`,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                showNotification('Success', 'Payment recorded successfully');
                
                // Reload payment history
                loadPaymentHistory(scheduleId);
                
                // Clear form
                $('#paymentDescription').val('');
                $('#paymentAmount').val('');
                $('#paymentAttachment').val('');
                
                // If payment was successful and marked as completed, update the collection schedule status
                if (response.update_status) {
                    $.ajax({
                        url: `/api/collection-schedules/${scheduleId}/progress`,
                        method: 'PUT',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            status: 'Completed',
                            resolution_date: new Date().toISOString()
                        }),
                        success: function() {
                            // Reload collection schedules in the background
                            loadCollectionSchedules();
                        }
                    });
                }
            },
            error: function(xhr) {
                showNotification('Error', xhr.responseJSON?.error || 'Failed to record payment');
            }
        });
    });

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
            staff_id: $('#filterStaff').val(),
            priority: $('#filterPriority').val(),
            status: $('#filterStatus').val(),
            method: $('#filterMethod').val()
        };
        loadCollectionSchedules(filters);
    });

    // Utility functions
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
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
                
                // Add event listener for create schedule button
                const createScheduleBtn = document.getElementById('create-collection-from-loan');
                createScheduleBtn.addEventListener('click', function() {
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
                    const clientOption = new Option(loan.customer_name, loan.loan_id, true, true);
                    clientSelect.innerHTML = '';
                    clientSelect.appendChild(clientOption);
                    clientSelect.disabled = true; // Disable changes since we're creating from loan details
                    
                    // Create and select the loan option
                    const loanOption = new Option(`Loan #${loan.loan_no}`, loan.loan_id, true, true);
                    loanSelect.innerHTML = '';
                    loanSelect.appendChild(loanOption);
                    loanSelect.disabled = true; // Disable changes since we're creating from loan details
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
        const response = await fetch('/api/overdue_loans');
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
                <td colspan="6" class="px-4 py-4 text-center">
                    <p class="text-gray-500 dark:text-gray-400">No overdue loans found</p>
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
            <td class="px-4 py-3 text-center whitespace-nowrap">
                <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500" onclick="viewLoanDetails('${loan.loan_id}')">
                    <span class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
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
    
    // Update summary cards
    function updateSummaryCards(data) {
        $('#total-schedules').text(data?.total || 0);
        $('#pending-followups').text(data?.pending || 0);
        $('#overdue-count').text(data?.overdue || 0);
        $('#completed-schedules').text(data?.completed || 0);
    }

    // Initialize collection schedules on page load
    loadCollectionSchedules();
    loadOverdueLoans();
    initializeTabs();
    initializeFilterToggle();

    // Refresh overdue loans every 5 minutes
    setInterval(loadOverdueLoans, 5 * 60 * 1000);
});