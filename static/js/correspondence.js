console.log('Correspondence.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Initialize client select with search
    $(document).ready(function() {
        const select = $('#clientSelect');

        // Initialize Select2
        select.select2({
            theme: 'bootstrap-5',
            placeholder: 'Search for a client...',
            allowClear: true,
            width: '100%',
            ajax: {
                url: 'http://localhost:5003/api/mock/clients/search', // Updated URL
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
                        results: data.clients.map(item => ({
                            id: item.id,
                            text: item.name // Use the correct property for display
                        })),
                        pagination: {
                            more: data.has_more
                        }
                    };
                },
                cache: true
            },
            minimumInputLength: 1,
            templateResult: function(data) {
                if (data.loading) {
                    return data.text;
                }
                return $('<span>' + data.text + '</span>');
            },
            templateSelection: function(data) {
                return data.text || data.id;
            }
        }).on('select2:select', function(e) {
            console.log('Selected:', e.params.data);
            loadCorrespondence(e.params.data.id);
        });
    });

        // Initialize client select with search
        $(document).ready(function() {
            const select = $('#clientSelect2');
    
            // Initialize Select2
            select.select2({
                theme: 'bootstrap-5',
                placeholder: 'Search for a client...',
                allowClear: true,
                width: '100%',
                ajax: {
                    url: 'http://localhost:5003/api/mock/clients/search', // Updated URL
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
                            results: data.clients.map(item => ({
                                id: item.id,
                                text: item.name // Use the correct property for display
                            })),
                            pagination: {
                                more: data.has_more
                            }
                        };
                    },
                    cache: true
                },
                minimumInputLength: 1,
                templateResult: function(data) {
                    if (data.loading) {
                        return data.text;
                    }
                    return $('<span>' + data.text + '</span>');
                },
                templateSelection: function(data) {
                    return data.text || data.id;
                }
            }).on('select2:select', function(e) {
                console.log('Selected:', e.params.data);
                loadCorrespondence(e.params.data.id);
            });
        });

    // Load correspondence for a client
    function loadCorrespondence(clientId) {
        console.log('Loading correspondence for client:', clientId);
        // Fetch account numbers for the selected client
        $.ajax({
            url: `http://localhost:5003/api/mock/clients/${clientId}/accounts`,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                console.log('Accounts for client:', data);
                // Assuming data.accounts is an array of account numbers
                const accountInput = $('#account_no');
                accountInput.val(data.accounts.join(', ')); // Display account numbers as comma-separated
            },
            error: function(error) {
                console.error('Error loading accounts:', error);
            }
        });
        $.ajax({
            url: '/user/api/correspondence/' + clientId,
            method: 'GET',
            success: function(data) {
                console.log('Correspondence loaded:', data);
                displayCorrespondence(data.correspondence);
                setupPagination(data.total, data.current_page, data.per_page);
            },
            error: function(xhr, status, error) {
                console.error('Error loading correspondence:', error);
            }
        });
    }

    // Display correspondence in timeline view
    function displayCorrespondence(correspondence) {
        const list = $('#correspondenceList ul');
        list.empty();

        // Add padding to the results section
        $('#correspondenceList').css('padding-top', '10px');

        if (!correspondence || correspondence.length === 0) {
            list.append('<li class="text-center text-gray-500 py-4">No correspondence found</li>');
            return;
        }

        correspondence.forEach(function(item) {
            const html = `
                <li class="bg-white shadow-md rounded-lg p-4 mb-4">
                    <div class="relative flex space-x-3">
                        <div>
                            <span class="h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white bg-${getTypeColor(item.type)}">
                                ${getTypeIcon(item.type)}
                            </span>
                        </div>
                        <div class="flex min-w-0 flex-1 justify-between space-x-4">
                            <div>
                                <p class="text-sm font-semibold text-gray-900">${item.content}</p>
                            </div>
                            <div class="whitespace-nowrap text-sm text-gray-500">
                                <span>${formatDate(item.created_at)}</span>
                            </div>
                        </div>
                    </div>
                </li>
            `;
            list.append(html);
        });
    }

    // Helper functions
    function getTypeColor(type) {
        const colors = {
            'email': 'blue-500',
            'sms': 'green-500',
            'call': 'yellow-500'
        };
        return colors[type] || 'gray-500';
    }

    function getTypeIcon(type) {
        const icons = {
            'email': '<i class="fas fa-envelope text-white"></i>',
            'sms': '<i class="fas fa-sms text-white"></i>',
            'call': '<i class="fas fa-phone text-white"></i>'
        };
        return icons[type] || '<i class="fas fa-comment text-white"></i>';
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function setupPagination(total, currentPage, perPage) {
        const totalPages = Math.ceil(total / perPage);
        const paginationContainer = $('#pagination');

        paginationContainer.empty(); // Clear existing pagination

        if (currentPage > 1) {
            paginationContainer.append(`<button onclick="loadPage(${currentPage - 1})">Previous</button>`);
        }

        for (let i = 1; i <= totalPages; i++) {
            paginationContainer.append(`<button onclick="loadPage(${i})">${i}</button>`);
        }

        if (currentPage < totalPages) {
            paginationContainer.append(`<button onclick="loadPage(${currentPage + 1})">Next</button>`);
        }
    }

    function loadPage(page) {
        $.ajax({
            url: `/user/api/correspondence?page=${page}`,
            method: 'GET',
            success: function(data) {
                displayCorrespondence(data.correspondence);
                setupPagination(data.total, data.current_page, data.per_page);
            },
            error: function(xhr, status, error) {
                console.error('Error loading correspondence:', error);
            }
        });
    }

    function saveCorrespondence() {
        const correspondenceData = {
            account_no: document.getElementById('account_no').value,
            client_name: document.getElementById('client_name').value,
            type: document.getElementById('type').value,
            message: document.getElementById('message').value,
            status: document.getElementById('status').value,
            sent_by: document.getElementById('sent_by').value,
            recipient: document.getElementById('recipient').value,
            delivery_status: document.getElementById('delivery_status').value,
            delivery_time: document.getElementById('delivery_time').value,
            call_duration: document.getElementById('call_duration').value,
            call_outcome: document.getElementById('call_outcome').value,
            location: document.getElementById('location').value,
            visit_purpose: document.getElementById('visit_purpose').value,
            visit_outcome: document.getElementById('visit_outcome').value,
            staff_id: document.getElementById('staff_id').value,
            loan_id: document.getElementById('loan_id').value,
            attachment_path: document.getElementById('attachment_path').value,
        };

        createCorrespondence(correspondenceData);
    }

   function createCorrespondence(data) {
       const csrfToken = document.querySelector('input[name="csrf_token"]').value; // Get CSRF token
       const formData = new FormData();
       formData.append('csrf_token', csrfToken);
       for (const key in data) {
           formData.append(key, data[key]);
       }
   
       console.log('Form Data:', Array.from(formData.entries()));
       fetch('/api/correspondence', {
           method: 'POST',
           body: formData, // Send as FormData
       })
       .then(response => response.json())
       .then(data => {
           if (data.success) {
               alert('Correspondence saved successfully!');
           } else {
               alert('Error saving correspondence: ' + data.message);
           }
       })
       .catch(error => {
           console.error('Error:', error);
           alert('An unexpected error occurred.');
       });
   }

    // Modal handling
    const modal = document.getElementById('newCorrespondenceModal');
    const newCorrespondenceBtn = document.getElementById('newCorrespondenceBtn');
    const closeModalBtn = document.getElementById('closeCorrespondenceModal');

    function openNewCorrespondenceModal() {
        modal.classList.remove('hidden');
    }

    function closeNewCorrespondenceModal() {
        modal.classList.add('hidden');
    }

    newCorrespondenceBtn.addEventListener('click', openNewCorrespondenceModal);
    closeModalBtn.addEventListener('click', closeNewCorrespondenceModal);

    // Handle new correspondence form submission
    $('#newCorrespondenceForm').on('submit', function(e) {
        e.preventDefault();
        
        const clientId = $('#clientSelect2').val();
        if (!clientId) {
            // alert('Please select a client first'); 
            return;
        }

        const formData = new FormData(this);
        formData.append('client_id', clientId);

        $.ajax({
            url: '/user/api/correspondence',
            method: 'POST',
            data: formData,
            processData: false,
            //contentType: false,
            success: function(response) {
                closeNewCorrespondenceModal();
                loadCorrespondence(clientId);
            },
            error: function(xhr, status, error) {
                console.error('Error saving correspondence:', error);
                alert('Failed to save correspondence');
            }
        });
    });
});
