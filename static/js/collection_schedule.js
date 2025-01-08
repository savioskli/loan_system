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
                return {
                    search: params.term,
                    page: params.page || 1
                };
            },
            processResults: function(data) {
                return {
                    results: data.map(staff => ({
                        id: staff.id,
                        text: `${staff.name} (${staff.branch || 'No Branch'})`
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

    $(document).ready(function() {
        // Initialize Select2 for both staff select fields
        $('#staffSelect').select2(staffSelect2Config);

        // Initialize client select
        initializeClientSelect('#collectionClientSelect', true);

        $('#loanSelect').select2({
            theme: 'bootstrap-5',
            placeholder: 'Select a loan',
            ajax: {
                url: '/api/collection-schedules/loans',
                dataType: 'json',
                processResults: function(data) {
                    return {
                        results: data.map(loan => ({
                            id: loan.id,
                            text: `${loan.account_no} - ${loan.borrower_name} (${loan.status})`
                        }))
                    };
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
                    console.log('Search params:', params);
                    return {
                        q: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function(data, params) {
                    console.log('Received data:', data);
                    params.page = params.page || 1;
                    return {
                        results: data.items.map(item => {
                            const name = item.text.split(' (')[0];
                            return {
                                id: name,
                                text: item.text,
                                member_no: item.member_no,
                                phone: item.phone,
                                email: item.email
                            };
                        }),
                        pagination: {
                            more: data.has_more
                        }
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            templateResult: formatClient,
            templateSelection: formatClientSelection
        };

        // Add modal-specific configurations
        if (isModal) {
            config.dropdownParent = $('#newCollectionScheduleModal');
        }

        // Initialize Select2
        select.select2(config)
            .on('select2:select', function(e) {
                console.log('Selected:', e.params.data);
                const data = e.params.data;
                if (isModal) {
                    // Handle modal-specific selection if needed
                    console.log('Client selected in modal:', data);
                }
            })
            .on('select2:clear', function() {
                console.log('Selection cleared');
            })
            .on('select2:error', function(e) {
                console.error('Select2 error:', e);
            });
    }

    function formatClient(client) {
        if (!client.id) return client.text;
        return $(`
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${client.text}</div>
                    <div class="text-muted small">
                        ${client.phone ? `<i class="bi bi-telephone"></i> ${client.phone}` : ''}
                        ${client.email ? `<i class="bi bi-envelope ms-2"></i> ${client.email}` : ''}
                    </div>
                </div>
            </div>
        `);
    }

    function formatClientSelection(client) {
        if (!client.id) return client.text;
        return client.text;
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
                                                data-id="${schedule.id}">
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
            assigned_branch: $('#branchInput').val(),
            follow_up_deadline: $('#followUpDeadline').val(),
            collection_priority: $('#prioritySelect').val(),
            follow_up_frequency: $('#frequencySelect').val(),
            next_follow_up_date: $('#nextFollowUpDate').val(),
            preferred_collection_method: $('#collectionMethodSelect').val(),
            promised_payment_date: $('#promisedPaymentDate').val() || null,
            attempts_allowed: $('#attemptsAllowed').val(),
            task_description: $('#taskDescription').val(),
            special_instructions: $('#specialInstructions').val()
        };

        $.ajax({
            url: '/api/collection-schedules',
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

    // Update progress
    $(document).on('click', '.update-progress-btn', function() {
        const scheduleId = $(this).data('id');
        const newStatus = prompt('Enter new status (Not Started, In Progress, Completed, Escalated):');
        if (newStatus) {
            $.ajax({
                url: `/api/collection-schedules/${scheduleId}/progress`,
                method: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({
                    status: newStatus,
                    resolution_date: newStatus === 'Completed' ? new Date().toISOString() : null
                }),
                success: function() {
                    showNotification('Success', 'Progress updated successfully');
                    loadCollectionSchedules();
                },
                error: function(xhr) {
                    showNotification('Error', xhr.responseJSON?.error || 'Failed to update progress');
                }
            });
        }
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

    // Function to fetch staff data from the search_users endpoint
    function fetchStaffData() {
        fetch('/users/search?limit=100')  // Updated endpoint path and added limit parameter
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const staffSelect = document.getElementById('staffSelect');
                // Clear existing options
                staffSelect.innerHTML = '<option value="">--Select Staff--</option>';
                // Add new options from the response
                data.staff.forEach(staff => {
                    const option = document.createElement('option');
                    option.value = staff.id;
                    option.textContent = staff.name;
                    staffSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching staff data:', error);
                showNotification('Error', 'Failed to load staff data');
            });
    }

    // Call the function to fetch and populate staff data on page load
    fetchStaffData();

    // Initialize collection schedules on page load
    loadCollectionSchedules();
});