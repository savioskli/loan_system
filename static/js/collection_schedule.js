document.addEventListener('DOMContentLoaded', function() {
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
                            <div class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
                                <div class="flex flex-col md:flex-row justify-between">
                                    <div class="flex-1">
                                        <div class="flex items-center mb-2">
                                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                                                ${borrowerInfo}
                                            </h3>
                                            ${schedule.collection_priority ? `
                                            <span class="ml-2 px-2 py-1 text-xs font-medium rounded-full 
                                                ${getPriorityClass(schedule.collection_priority)}">
                                                ${schedule.collection_priority}
                                            </span>
                                            ` : ''}
                                        </div>
                                        
                                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                                            <div>
                                                <p class="text-sm text-gray-600 dark:text-gray-400">Assigned To</p>
                                                <p class="font-medium">${staffName}</p>
                                            </div>
                                            <div>
                                                <p class="text-sm text-gray-600 dark:text-gray-400">Next Follow-up</p>
                                                <p class="font-medium">${nextFollowUp}</p>
                                            </div>
                                            <div>
                                                <p class="text-sm text-gray-600 dark:text-gray-400">Method</p>
                                                <p class="font-medium">${method}</p>
                                            </div>
                                            ${schedule.promised_payment_date ? `
                                            <div>
                                                <p class="text-sm text-gray-600 dark:text-gray-400">Promised Payment</p>
                                                <p class="font-medium">${formatDate(schedule.promised_payment_date)}</p>
                                            </div>
                                            ` : ''}
                                            <div>
                                                <p class="text-sm text-gray-600 dark:text-gray-400">Attempts</p>
                                                <p class="font-medium">${schedule.attempts_made || 0} / ${schedule.attempts_allowed || '-'}</p>
                                            </div>
                                        </div>
                                        
                                        ${schedule.task_description ? `
                                        <div class="mb-4">
                                            <p class="text-sm text-gray-600 dark:text-gray-400">Task Description</p>
                                            <p class="mt-1">${schedule.task_description}</p>
                                        </div>
                                        ` : ''}
                                        
                                        ${schedule.special_instructions ? `
                                        <div class="mb-4">
                                            <p class="text-sm text-gray-600 dark:text-gray-400">Special Instructions</p>
                                            <p class="mt-1">${schedule.special_instructions}</p>
                                        </div>
                                        ` : ''}
                                        
                                        ${schedule.progress_status ? `
                                        <div class="mt-2">
                                            <span class="px-2 py-1 text-xs font-medium rounded-full ${getStatusClass(schedule.progress_status)}">
                                                ${schedule.progress_status}
                                            </span>
                                            ${schedule.escalation_level ? `
                                            <span class="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                                                Escalation Level ${schedule.escalation_level}
                                            </span>
                                            ` : ''}
                                        </div>
                                        ` : ''}
                                    </div>
                                    
                                    <div class="flex flex-col space-y-2 mt-4 md:mt-0 md:ml-4">
                                        <button class="update-progress-btn px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded hover:bg-blue-600"
                                                data-id="${schedule.id}" data-loan-id="${schedule.loan_id}" data-borrower-name="${schedule.borrower_name || 'Unknown'}">
                                            Update Progress
                                        </button>
                                        ${schedule.progress_status !== 'Escalated' ? `
                                        <button class="escalate-btn px-4 py-2 text-sm font-medium text-white bg-yellow-500 rounded hover:bg-yellow-600"
                                                data-id="${schedule.id}">
                                            Escalate
                                        </button>
                                        ` : ''}
                                        <button class="delete-btn px-4 py-2 text-sm font-medium text-white bg-red-500 rounded hover:bg-red-600"
                                                data-id="${schedule.id}">
                                            Delete
                                        </button>
                                    </div>
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
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${payment.amount.toLocaleString('en-US', { style: 'currency', currency: 'KES' })}</td>
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
                document.getElementById('loan-details-amount').textContent = loan.outstanding_balance?.toFixed(2) || '0.00';
                document.getElementById('loan-details-arrears').textContent = loan.days_in_arrears || '0';
                
                // Remove reference to due_date since it's not available
                const dueDateElement = document.getElementById('loan-details-due-date');
                if (dueDateElement) {
                    dueDateElement.textContent = 'N/A';
                }
                
                // Show modal using custom implementation
                modal.style.display = 'block';
                
                // Add event listeners to close buttons
                const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        modal.style.display = 'none';
                    });
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
        
        tbody.innerHTML = '';

        if (!Array.isArray(data.data)) {
            throw new Error('Data is not an array');
        }

        data.data.forEach(loan => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">${loan.loan_no || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap">${loan.customer_name || 'N/A'}</td>
                <td class="px-6 py-4 text-right whitespace-nowrap">${loan.outstanding_balance?.toFixed(2) || '0.00'}</td>
                <td class="px-6 py-4 text-right whitespace-nowrap">${loan.arrears_amount?.toFixed(2) || '0.00'}</td>
                <td class="px-6 py-4 text-right whitespace-nowrap">${loan.arrears_days || 0}</td>
                <td class="px-6 py-4 text-right whitespace-nowrap">
                    <button class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700" onclick="viewLoanDetails('${loan.loan_id}')">
                        View Details
                    </button>
                </td>
            `;
        });
        
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
                    <td colspan="6" class="px-6 py-4 text-center text-red-500">
                        Error loading overdue loans: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
}

    // Initialize collection schedules on page load
    loadCollectionSchedules();
    loadOverdueLoans();

    // Refresh overdue loans every 5 minutes
    setInterval(loadOverdueLoans, 5 * 60 * 1000);
});