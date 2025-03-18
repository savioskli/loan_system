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
        } else if (commType === 'email' && clientData.email) {
            $('#recipient').val(clientData.email);
        }
    }

    function initializeEventListeners() {
        console.log('Initializing event listeners');
        
        // Initialize Select2 for type filter
        $('#typeFilter').select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: 'All Types'
        });

        // Initialize Select2 for per page filter
        $('#perPage').select2({
            theme: 'bootstrap-5',
            width: '100%',
            minimumResultsForSearch: Infinity // Disable search
        });

        // Initialize date pickers with better formatting
        $('#startDate, #endDate').on('change', function() {
            loadCommunications(1);
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
            $('#smsEmailFields, #callFields').addClass('hidden');
            
            // Show relevant fields based on type
            switch(type) {
                case 'sms':
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

            $.ajax({
                url: '/api/communications',
                method: 'POST',
                data: JSON.stringify(jsonData),
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': $('input[name=csrf_token]').val()
                },
                success: function(response) {
                    console.log('Communication saved:', response);
                    if (response.status === 'success') {
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
    }

    function loadCommunications(page = 1) {
        const filters = {
            page: page,
            per_page: $('#perPage').val() || 10,
            member_id: $('#clientSelect').val() || '',
            start_date: $('#startDate').val() || '',
            end_date: $('#endDate').val() || '',
            type: $('#typeFilter').val() || ''
        };
        
        console.log('Loading communications with filters:', filters);
        
        $.ajax({
            url: '/user/loans/communications',
            method: 'GET',
            data: filters,
            success: function(response) {
                console.log('Communications loaded:', response);
                if (response.error) {
                    $('#communicationsList').html(`<p class="text-center text-red-500">${response.error}</p>`);
                    return;
                }
                displayCommunications(response.communications || []);
                updatePagination(response.page, response.total_pages, 'system');
            },
            error: function(xhr, status, error) {
                console.error('Error loading communications:', error);
                $('#communicationsList').html('<p class="text-center text-red-500">Error loading communications</p>');
            }
        });
    }

    function loadCoreCommunications(page = 1) {
        const filters = {
            page: page,
            per_page: $('#perPage').val() || 10,
            member_id: $('#clientSelect').val() || '',
            start_date: $('#startDate').val() || '',
            end_date: $('#endDate').val() || '',
            type: $('#typeFilter').val() || ''
        };
        
        console.log('Loading core communications with filters:', filters);
        
        $.ajax({
            url: '/user/loans/communications/core',
            method: 'GET',
            data: filters,
            success: function(response) {
                console.log('Core communications loaded:', response);
                if (response.error) {
                    $('#coreCommunicationsList').html(`<p class="text-center text-red-500">${response.error}</p>`);
                    return;
                }
                displayCoreCommunications(response.communications || []);
                updatePagination(response.page, response.total_pages, 'core');
            },
            error: function(xhr, status, error) {
                console.error('Error loading core communications:', error);
                $('#coreCommunicationsList').html('<p class="text-center text-red-500">Error loading communications</p>');
            }
        });
    }

    function displayCommunications(communications) {
        const container = $('#communicationsList');
        container.empty();
        
        if (communications.length === 0) {
            container.html('<p class="text-center text-gray-500">No communications found</p>');
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
            container.html('<p class="text-center text-gray-500">No communications found</p>');
            return;
        }
        
        communications.forEach(comm => {
            container.append(createCommunicationItem(comm));
        });
    }

    function createCommunicationItem(comm) {
        return `
            <div class="communication-item communication-type-${comm.type}">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-medium">${comm.member_name}</h3>
                        <p class="text-sm text-gray-500">Member: ${comm.member_no}</p>
                        <p class="text-sm text-gray-500">Loan: ${comm.loan_no || 'N/A'}</p>
                    </div>
                    <div class="text-right">
                        <span class="text-sm font-medium status-${comm.status}">${comm.status}</span>
                        <p class="text-sm text-gray-500">${comm.created_at}</p>
                    </div>
                </div>
                <div class="mt-2">
                    <p class="text-gray-700">${comm.message}</p>
                </div>
                <div class="mt-2 text-sm text-gray-500">
                    <span class="capitalize">${comm.type}</span> • Sent by ${comm.sent_by}
                    ${comm.response ? ` • Response: ${comm.response}` : ''}
                </div>
            </div>
        `;
    }

    function updatePagination(currentPage, totalPages, type) {
        const container = type === 'system' ? $('#systemPagination') : $('#corePagination');
        container.empty();
        
        if (totalPages <= 1) return;
        
        const loadFunc = type === 'system' ? loadCommunications : loadCoreCommunications;
        
        // Previous button
        container.append(`
            <button 
                class="px-3 py-1 rounded-md ${currentPage === 1 ? 'text-gray-400 cursor-not-allowed' : 'text-gray-700 hover:bg-gray-100'}"
                ${currentPage === 1 ? 'disabled' : ''}
                onclick="${currentPage > 1 ? `${loadFunc.name}(${currentPage - 1})` : ''}"
            >
                Previous
            </button>
        `);
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            container.append(`
                <button 
                    class="px-3 py-1 rounded-md ${i === currentPage ? 'bg-primary text-white' : 'text-gray-700 hover:bg-gray-100'}"
                    onclick="${loadFunc.name}(${i})"
                >
                    ${i}
                </button>
            `);
        }
        
        // Next button
        container.append(`
            <button 
                class="px-3 py-1 rounded-md ${currentPage === totalPages ? 'text-gray-400 cursor-not-allowed' : 'text-gray-700 hover:bg-gray-100'}"
                ${currentPage === totalPages ? 'disabled' : ''}
                onclick="${currentPage < totalPages ? `${loadFunc.name}(${currentPage + 1})` : ''}"
            >
                Next
            </button>
        `);
    }
});
