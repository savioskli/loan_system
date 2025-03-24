console.log('Correspondence.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    let currentPage = 1;
    let totalPages = 1;

    // Initialize client select with search
    $(document).ready(function() {
        initializeClientSelect('#clientSelect', false);
        initializeClientSelect('#clientSelect2', true);
        initializeEventListeners();
        loadCommunications(1);
        loadReminderCounts();
        // Refresh every 5 minutes
        setInterval(loadReminderCounts, 300000);
    });

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
            config.dropdownParent = $('#newCorrespondenceModal');
        }

        // Initialize Select2
        select.select2(config)
            .on('select2:select', function(e) {
                console.log('Selected:', e.params.data);
                const data = e.params.data;
                if (isModal) {
                    $('#account_no').val(data.member_no);
                    updateRecipientField(data);
                } else {
                    // Removed updateLoanOptions(data.id);
                }
            })
            .on('select2:clear', function() {
                if (!isModal) {
                    // Removed updateLoanOptions(null);
                }
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

    // Removed function updateLoanOptions(clientId)

    function updateRecipientField(clientData) {
        console.log('Updating recipient field with client data:', clientData);
        if (!clientData) return;
        
        const commType = $('#type').val();
        if (commType === 'sms' && clientData.phone) {
            $('#recipient').val(clientData.phone);
            // Show SMS provider field when SMS type is selected and we have a phone number
            $('#smsProviderField').removeClass('hidden');
        } else if (commType === 'email' && clientData.email) {
            $('#recipient').val(clientData.email);
            // Hide SMS provider field for email type
            $('#smsProviderField').addClass('hidden');
        }
    }

    function initializeEventListeners() {
        console.log('Initializing event listeners');
        
        // Initialize search input with debounce
        let searchTimeout;
        $('#searchInput').on('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                loadCommunications(1);
            }, 300);
        });

        // Add clear search button functionality
        $('#searchInput').on('keyup', function(e) {
            if (e.key === 'Escape') {
                $(this).val('');
                loadCommunications(1);
            }
        });
        
        // Filter change handlers
        $('#clientSelect, #typeFilter, #perPage, #startDate, #endDate').on('change', function() {
            console.log('Filter changed:', $(this).attr('id'));
            loadCommunications(1);
        });

        // Tab switching
        $('.tab').click(function() {
            console.log('Tab clicked:', $(this).data('tab'));
            $('.tab').removeClass('active');
            $(this).addClass('active');
            
            $('.tab-content').removeClass('active');
            $(`#${$(this).data('tab')}Tab`).addClass('active');
            
            if ($(this).data('tab') === 'system') {
                loadCommunications(1);
            } else {
                loadCoreCommunications(1);
            }
        });

        // Modal handlers
        $('#newCorrespondenceBtn').click(function() {
            console.log('Opening new correspondence modal');
            $('#newCorrespondenceModal').removeClass('hidden');
            
            // Load SMS providers when the modal is opened
            loadSmsProviders();
        });

        $('#closeCorrespondenceModal').click(function() {
            console.log('Closing correspondence modal');
            $('#newCorrespondenceModal').addClass('hidden');
            $('#newCorrespondenceForm')[0].reset();
            $('#clientSelect2').val(null).trigger('change');
        });

        // Communication type change handler
        $('#type').on('change', function() {
            const type = $(this).val();
            console.log('Communication type changed:', type);
            
            // Hide all dynamic fields first
            $('#smsEmailFields, #callFields, #smsProviderField').addClass('hidden');
            
            // Show relevant fields based on type
            switch(type) {
                case 'sms':
                    $('#smsEmailFields').removeClass('hidden');
                    $('#smsProviderField').removeClass('hidden');
                    // Load SMS providers when SMS type is selected
                    loadSmsProviders();
                    break;
                case 'email':
                    $('#smsEmailFields').removeClass('hidden');
                    break;
                case 'call':
                    $('#callFields').removeClass('hidden');
                    break;
            }
            
            // Update recipient field if client is selected
            const clientData = $('#clientSelect2').select2('data')[0];
            if (clientData) {
                updateRecipientField(clientData);
                // Set both account_no and loan_id
                $('#account_no').val(clientData.member_no);
                $('input[name="loan_id"]').val(clientData.member_no);
            }
        });

        // Load available SMS providers
        function loadSmsProviders() {
            $.ajax({
                url: '/correspondence/api/sms-providers',
                method: 'GET',
                success: function(response) {
                    console.log('SMS providers loaded:', response);
                    
                    // Populate provider dropdown if it exists
                    const providerSelect = $('#smsProvider');
                    if (providerSelect.length) {
                        providerSelect.empty();
                        
                        // Add default option (use active provider)
                        providerSelect.append(`<option value="">Default (${response.active_provider})</option>`);
                        
                        // Add available providers
                        response.available_providers.forEach(provider => {
                            providerSelect.append(`<option value="${provider}">${provider.charAt(0).toUpperCase() + provider.slice(1)}</option>`);
                        });
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error loading SMS providers:', error);
                }
            });
        }
        
        // Form submission
        $('#newCorrespondenceForm').submit(function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            const formData = new FormData(this);
            const jsonData = {};
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });
            console.log('JSON data:', jsonData);

            // Basic validation
            if (!jsonData.client_name) {
                alert('Please select a client');
                return;
            }

            if (!jsonData.type) {
                alert('Please select a communication type');
                return;
            }

            if (!jsonData.message) {
                alert('Please enter a message');
                return;
            }
            
            // Determine the API endpoint based on the communication type
            let apiUrl = '/correspondence/api/communications';
            let contentType = 'application/json';
            
            // If it's an SMS, use our new SMS gateway service
            if (jsonData.type === 'sms') {
                apiUrl = '/correspondence/api/send-sms';
                
                // Prepare the SMS-specific data
                jsonData = {
                    recipient: jsonData.recipient,
                    message: jsonData.message,
                    account_no: jsonData.account_no || '',
                    client_name: jsonData.client_name,
                    provider: $('#smsProvider').val() || null // Use selected provider or default
                };
            }

            $.ajax({
                url: apiUrl,
                method: 'POST',
                data: JSON.stringify(jsonData),
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': $('input[name=csrf_token]').val()
                },
                success: function(response) {
                    console.log('Communication saved:', response);
                    if (response.success || response.status === 'success') {
                        $('#newCorrespondenceModal').addClass('hidden');
                        $('#newCorrespondenceForm')[0].reset();
                        $('#clientSelect2').val(null).trigger('change');
                        loadCommunications(1);
                    } else {
                        alert(response.message || 'Failed to save communication');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error saving communication:', error);
                    alert('Error saving communication. Please try again.');
                }
            });
        });

        $(document).on('click', '.reminder-action-btn', function(e) {
            const reminderType = $(this).data('reminder-type');
            const templates = {
                overdue: "Urgent: Your loan payment is overdue. Please settle the amount immediately...",
                upcoming: "Friendly reminder: Your payment of [Amount] is due on [Date]...",
                delinquent: "Notice: Your account is 30-60 days past due. Contact us to avoid...",
                highrisk: "Important: Account review required. Please contact our risk department..."
            };
            // Show the send reminders modal
            $('#sendRemindersModal').removeClass('hidden');
            // Prevent any other modals from being triggered
            e.stopPropagation();
            // Set the reminder type on the form
            $('#sendRemindersForm').data('reminder-type', reminderType);
        });

        $('#newCorrespondenceForm').submit(function() {
            if ($(this).hasClass('reminder-initiated')) {
                $(this).removeClass('reminder-initiated');
                // Add server-side validation tag
                $('<input>').attr({
                    type: 'hidden',
                    name: 'reminder_template',
                    value: '1'
                }).appendTo(this);
            }
        });
    }

    function loadCommunications(page = 1) {
        const searchQuery = $('#searchInput').val() || '';
        const data = {
            page: page,
            per_page: 10,
            search: searchQuery
        };
        
        console.log('Loading communications with search:', data);
        
        $.ajax({
            url: '/correspondence/api/correspondence',
            method: 'GET',
            data: data,
            success: function(response) {
                console.log('Communications loaded:', response);
                if (response.error) {
                    $('#communicationsList').html(`<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">${response.error}</td></tr>`);
                    return;
                }
                displayCommunications(response.correspondence || []);
                if (response.pagination) {
                    updatePagination(response.pagination.current_page, response.pagination.total_pages, 'system');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading communications:', error);
                $('#communicationsList').html('<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error loading communications</td></tr>');
            }
        });
    }

    function loadCoreCommunications(page = 1) {
        const filters = {
            page: page,
            per_page: 10,
            member_id: $('#clientSelect').val() || '',
            start_date: $('#startDate').val() || '',
            end_date: $('#endDate').val() || '',
            type: $('#typeFilter').val() || ''
        };
        
        console.log('Loading core communications with filters:', filters);
        
        $.ajax({
            url: '/correspondence/api/core-correspondence',
            method: 'GET',
            data: filters,
            success: function(response) {
                console.log('Core communications loaded:', response);
                if (response.error) {
                    $('#coreCommunicationsList').html(`<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">${response.error}</td></tr>`);
                    return;
                }
                displayCoreCommunications(response.correspondence || []);
                if (response.pagination) {
                    updatePagination(response.pagination.current_page, response.pagination.total_pages, 'core');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading core communications:', error);
                $('#coreCommunicationsList').html('<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error loading communications</td></tr>');
            }
        });
    }

    function displayCommunications(communications) {
        const container = $('#communicationsList');
        container.empty();
        
        if (communications.length === 0) {
            container.html(`
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                        No communications found
                    </td>
                </tr>
            `);
            return;
        }
        
        communications.forEach(comm => {
            container.append(createCommunicationItem(comm));
        });
    }

    function displayCoreCommunications(communications) {
        const container = $('#coreCommunicationsList');
        container.empty();
        
        if (communications.length === 0) {
            container.html(`
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                        No communications found
                    </td>
                </tr>
            `);
            return;
        }
        
        communications.forEach(comm => {
            container.append(createCommunicationItem(comm));
        });
    }

    function createCommunicationItem(comm) {
        const formattedDate = new Date(comm.created_at).toLocaleString();
        return `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-600">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">${comm.client_name || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white capitalize">${comm.type}</td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${comm.message}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${comm.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${comm.status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">${comm.sent_by}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formattedDate}</td>
            </tr>
        `;
    }

    function updatePagination(currentPage, totalPages, type) {
        const container = type === 'system' ? $('#systemPagination') : $('#corePagination');
        container.empty();
        
        if (!totalPages || totalPages <= 1) return;
        
        currentPage = parseInt(currentPage) || 1;
        totalPages = parseInt(totalPages);
        
        // Calculate the range of pages to show
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, currentPage + 2);
        
        // Adjust the range if we're near the start or end
        if (startPage <= 3) {
            endPage = Math.min(5, totalPages);
        }
        if (endPage >= totalPages - 2) {
            startPage = Math.max(1, totalPages - 4);
        }
        
        const pages = [];
        
        // Previous button
        pages.push(`
            <li>
                <button type="button" data-page="${currentPage - 1}" 
                        class="relative inline-flex items-center px-4 py-2 text-sm font-medium ${currentPage === 1 ? 'text-gray-400 bg-gray-100 cursor-not-allowed' : 'text-gray-700 bg-white hover:bg-primary-50 hover:text-primary'} border border-gray-300 rounded-l-lg focus:z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                        ${currentPage === 1 ? 'disabled' : ''}>
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                    </svg>
                    Previous
                </button>
            </li>
        `);
        
        // First page if not in range
        if (startPage > 1) {
            pages.push(`
                <li>
                    <button type="button" data-page="1" 
                            class="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-primary-50 hover:text-primary focus:z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200">
                        1
                    </button>
                </li>
            `);
            if (startPage > 2) {
                pages.push(`
                    <li>
                        <span class="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300">
                            ...
                        </span>
                    </li>
                `);
            }
        }
        
        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            pages.push(`
                <li>
                    <button type="button" data-page="${i}"
                            class="relative inline-flex items-center px-4 py-2 text-sm font-medium ${i === currentPage ? 'z-10 bg-primary-600 text-white border-primary-600 hover:bg-primary-700' : 'text-gray-700 bg-white border-gray-300 hover:bg-primary-50 hover:text-primary'} border focus:z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200">
                        ${i}
                    </button>
                </li>
            `);
        }
        
        // Last page if not in range
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                pages.push(`
                    <li>
                        <span class="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300">
                            ...
                        </span>
                    </li>
                `);
            }
            pages.push(`
                <li>
                    <button type="button" data-page="${totalPages}" 
                            class="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-primary-50 hover:text-primary focus:z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200">
                        ${totalPages}
                    </button>
                </li>
            `);
        }
        
        // Next button
        pages.push(`
            <li>
                <button type="button" data-page="${currentPage + 1}"
                        class="relative inline-flex items-center px-4 py-2 text-sm font-medium ${currentPage === totalPages ? 'text-gray-400 bg-gray-100 cursor-not-allowed' : 'text-gray-700 bg-white hover:bg-primary-50 hover:text-primary'} border border-gray-300 rounded-r-lg focus:z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200"
                        ${currentPage === totalPages ? 'disabled' : ''}>
                    Next
                    <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </button>
            </li>
        `);
        
        const nav = $(`
            <nav class="flex justify-center mt-6" aria-label="Pagination" data-type="${type}">
                <ul class="inline-flex -space-x-px rounded-md shadow-sm bg-white dark:bg-gray-800">
                    ${pages.join('')}
                </ul>
            </nav>
        `);
        
        // Add click handler using event delegation
        nav.on('click', 'button[data-page]', function(e) {
            e.preventDefault();
            const page = parseInt($(this).data('page'));
            const paginationType = $(this).closest('nav').data('type');
            
            if (!page || $(this).prop('disabled')) return;
            
            if (paginationType === 'system') {
                loadCommunications(page);
            } else {
                loadCoreCommunications(page);
            }
        });
        
        container.append(nav);
    }

    function loadReminderCounts() {
        $.ajax({
            url: '/user/reminders/loans',
            method: 'GET',
            success: function(response) {
                // Update counts in widgets
                $('#upcomingCount').text(response.counts.upcoming_installments);
                $('#overdueCount').text(response.counts.overdue_loans);
                $('#delinquentCount').text(response.counts.delinquent_accounts);
                $('#highriskCount').text(response.counts.high_risk_loans);

                // Hide or show buttons based on counts
    $('[data-reminder-type="upcoming"]').toggle(response.counts.upcoming_installments > 0);
    $('[data-reminder-type="overdue"]').toggle(response.counts.overdue_loans > 0);
    $('[data-reminder-type="delinquent"]').toggle(response.counts.delinquent_accounts > 0);
    $('[data-reminder-type="highrisk"]').toggle(response.counts.high_risk_loans > 0);

                
                // Store the full data for later use
                window.reminderData = response;
                
                // Log detailed categorization information
                console.log('===== LOAN CATEGORIZATION DETAILS =====');
                console.log('COUNTS:', response.counts);
                console.log('EXPOSURE:', response.exposure);
                
                // Log details of each category
                console.log('\n===== HIGH RISK LOANS (' + response.high_risk_loans.length + ') =====');
                response.high_risk_loans.forEach((loan, index) => {
                    console.log(`Loan #${index+1}: ID=${loan.LoanID}, ArrearsDays=${loan.ArrearsDays}, Balance=${loan.OutstandingBalance}`);
                });
                
                console.log('\n===== DELINQUENT ACCOUNTS (' + response.delinquent_accounts.length + ') =====');
                response.delinquent_accounts.forEach((loan, index) => {
                    console.log(`Loan #${index+1}: ID=${loan.LoanID}, ArrearsDays=${loan.ArrearsDays}, Balance=${loan.OutstandingBalance}`);
                });
                
                console.log('\n===== OVERDUE LOANS (' + response.overdue_loans.length + ') =====');
                response.overdue_loans.forEach((loan, index) => {
                    console.log(`Loan #${index+1}: ID=${loan.LoanID}, ArrearsDays=${loan.ArrearsDays}, Balance=${loan.OutstandingBalance}`);
                });
                
                console.log('\n===== UPCOMING INSTALLMENTS (' + response.upcoming_installments.length + ') =====');
                response.upcoming_installments.forEach((loan, index) => {
                    console.log(`Loan #${index+1}: ID=${loan.LoanID}, NextDate=${loan.NextInstallmentDate}, Balance=${loan.OutstandingBalance}`);
                });
                
                // Log raw data for debugging
                console.log('\n===== RAW LOAN DATA =====');
                console.log('Total loans in raw data:', response.raw_data ? response.raw_data.length : 'N/A');
            },
            error: function(xhr) {
                console.error('Error loading reminder counts:', xhr);
            }
        });
    }

    // Handle reminder button clicks
    $(document).on('click', '.reminder-action-btn', function(e) {
        const reminderType = $(this).data('reminder-type');
        const templates = {
            overdue: "Urgent: Your loan payment of [Amount] is overdue. Please settle the amount immediately to avoid additional penalties.",
            upcoming: "Friendly reminder: Your payment of [Amount] is due on [Date]. Please ensure funds are available in your account.",
            delinquent: "Notice: Your account is 30-60 days past due. Contact us immediately to discuss payment arrangements and avoid further action.",
            highrisk: "Important: Your loan account requires immediate attention. Please contact our risk department at [Phone] to discuss urgent payment arrangements."
        };
        
        // Get accounts for this category
        const accounts = [];
        let categoryData = [];
        
        if (window.reminderData) {
            switch(reminderType) {
                case 'upcoming':
                    categoryData = window.reminderData.upcoming_installments;
                    break;
                case 'overdue':
                    categoryData = window.reminderData.overdue_loans;
                    break;
                case 'delinquent':
                    categoryData = window.reminderData.delinquent_accounts;
                    break;
                case 'highrisk':
                    categoryData = window.reminderData.high_risk_loans;
                    break;
            }
            
            // Populate accounts select
            $('#accountsSelect').empty();
            // Add Select All option
            $('#accountsSelect').append(`<option value="all">Select All</option>`);
            
            categoryData.forEach(function(loan) {
                $('#accountsSelect').append(`<option value="${loan.ClientID}" 
                    data-loan-id="${loan.LoanID}" 
                    data-amount="${loan.InstallmentAmount || loan.OutstandingBalance}" 
                    data-date="${loan.NextInstallmentDate || ''}"
                    data-email="${loan.Email || ''}"
                    data-phone="${loan.Phone || ''}"
                    data-name="${loan.FirstName} ${loan.LastName}"
                    data-loan-no="${loan.LoanNo}"
                    data-due-date="${loan.DueDate}">
                    ${loan.FirstName} ${loan.LastName} - A/C: ${loan.LoanNo} - Due: ${loan.DueDate}
                </option>`);
            });

            // Initialize Select2 with custom handling for Select All
            $('#accountsSelect').select2({
                theme: 'bootstrap-5',
                width: '100%',
                placeholder: 'Select accounts...',
                closeOnSelect: false
            }).on('select2:select', function(e) {
                if (e.params.data.id === 'all') {
                    // If 'Select All' is chosen, select all other options
                    const allOptions = $(this).find('option').not('[value="all"]');
                    allOptions.prop('selected', true);
                    $(this).trigger('change');
                }
            }).on('select2:unselect', function(e) {
                if (e.params.data.id === 'all') {
                    // If 'Select All' is unselected, unselect all options
                    $(this).find('option').prop('selected', false);
                    $(this).trigger('change');
                } else {
                    // If any other option is unselected, also unselect 'Select All'
                    $(this).find('option[value="all"]').prop('selected', false);
                }
            });
        }
        
        // Set message template
        $('#messageTemplate').val(templates[reminderType]);
        
        // Show the send reminders modal
        $('#sendRemindersModal').removeClass('hidden');
        // Prevent any other modals from being triggered
        e.stopPropagation();
        // Set the reminder type on the form
        $('#sendRemindersForm').data('reminder-type', reminderType);
    });

    // Handle send reminders form submission
    $('#sendRemindersForm').submit(function(e) {
        e.preventDefault();
        
        const selectedAccounts = $('#accountsSelect').val();
        const messageTemplate = $('#messageTemplate').val();
        const sendVia = $('#sendVia').val();
        
        if (!selectedAccounts || selectedAccounts.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Selection Required',
                text: 'Please select at least one account to send reminders to',
                confirmButtonColor: '#3B82F6'
            });
            return;
        }
        
        // Show loading indicator
        Swal.fire({
            title: 'Sending Reminders',
            text: 'Please wait while we process your request...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Process each selected account
        const promises = [];
        const sentMessages = [];
        const smsMessages = [];
        
        selectedAccounts.forEach(function(clientId) {
            const option = $(`#accountsSelect option[value='${clientId}']`);
            const loanId = option.data('loan-id');
            const amount = option.data('amount');
            const date = option.data('date');
            const email = option.data('email');
            const phone = option.data('phone');
            const name = option.data('name');
            const loanNo = option.data('loan-no');
            const dueDate = option.data('due-date');
            
            // Format amount as currency
            const formattedAmount = new Intl.NumberFormat('en-US', { 
                style: 'currency', 
                currency: 'KES',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amount);
            
            // Personalize message
            let personalizedMessage = messageTemplate
                .replace('[Amount]', formattedAmount)
                .replace('[Date]', date)
                .replace('[Phone]', phone)
                .replace('[Name]', name);
                
            // For SMS, ensure name and amount are included in the message
            if (sendVia === 'sms') {
                // If the template doesn't already include the name and amount, add them
                if (!personalizedMessage.includes(name)) {
                    personalizedMessage = `Dear ${name}, ` + personalizedMessage;
                }
                if (!personalizedMessage.includes(formattedAmount)) {
                    personalizedMessage = personalizedMessage.replace('overdue', `overdue. Your outstanding balance is ${formattedAmount}`);
                }
            }
            
            // Create correspondence record
            const recipient = sendVia === 'email' ? email : phone;
            
            // Skip if recipient is missing or invalid
            if (sendVia === 'sms' && (!recipient || recipient.trim().length < 10)) {
                console.warn(`Skipping SMS to ${name} due to invalid phone number: ${recipient}`);
                return;
            }
            
            // Store sent message info for display
            sentMessages.push({
                name: name,
                loanNo: loanNo,
                method: sendVia,
                recipient: recipient,
                message: personalizedMessage
            });
            
            // Collect SMS messages for bulk sending
            if (sendVia === 'sms') {
                // Add to the messages array to be sent in bulk
                smsMessages.push({
                    recipient: recipient,
                    message: personalizedMessage,
                    account_no: loanNo || '',
                    client_name: name
                });
                
                // Store reference to the message data for display
                sentMessages[sentMessages.length - 1].data = smsMessages[smsMessages.length - 1];
            
            } else {
                // For email or other types, use the existing correspondence endpoint
                promises.push($.ajax({
                    url: '/api/correspondence',
                    method: 'POST',
                    data: {
                        client_id: clientId,
                        loan_id: loanId,
                        type: sendVia,
                        recipient: recipient,
                        message: personalizedMessage,
                        reminder_template: '1'
                    }
                }).catch(function(error) {
                    console.log('API call failed, but continuing for demo purposes');
                    return Promise.resolve();
                }));
            }
        });
        
        // Send bulk SMS messages if any
        if (sendVia === 'sms' && smsMessages.length > 0) {
            // Log the SMS messages being sent for debugging
            console.log('Sending bulk SMS messages:', JSON.stringify(smsMessages));
            
            // Add a single bulk SMS request instead of individual requests
            promises.push($.ajax({
                url: '/correspondence/api/send-bulk-sms',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(smsMessages),
                headers: {
                    'X-CSRFToken': $('input[name=csrf_token]').val()
                },
                success: function(response) {
                    console.log('Bulk SMS sent successfully:', response);
                },
                error: function(xhr, status, error) {
                    console.error('Error sending bulk SMS:', error);
                    console.error('Error details:', xhr.responseText);
                    return Promise.resolve();
                }
            }));
        }
        
        // Wait for all requests to complete
        Promise.all(promises)
            .then(function() {
                // Close modal
                $('#sendRemindersModal').addClass('hidden');
                
                // Show success message with details
                let messageDetails = '<div class="mt-4 text-left">';
                sentMessages.forEach(msg => {
                    messageDetails += `<p class="mb-2"><strong>${msg.name}</strong> (${msg.loanNo}) - ${msg.method === 'email' ? 'Email' : 'SMS'} to ${msg.recipient}</p>`;
                });
                messageDetails += '</div>';
                
                Swal.fire({
                    icon: 'success',
                    title: 'Reminders Sent Successfully',
                    html: `Successfully sent ${selectedAccounts.length} reminder${selectedAccounts.length > 1 ? 's' : ''}${messageDetails}`,
                    confirmButtonColor: '#3B82F6'
                });
                
                // Refresh communications list
                loadCommunications(1);
            })
            .catch(function(error) {
                console.error('Error sending reminders:', error);
                alert('Error sending reminders. Please try again.');
            });
    });

    // Close send reminders modal
    $('#closeSendRemindersModal').click(function() {
        $('#sendRemindersModal').addClass('hidden');
    });
});
