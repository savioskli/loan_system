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

    // Load correspondence for a client
    function loadCorrespondence(clientId) {
        console.log('Loading correspondence for client:', clientId);
        $.ajax({
            url: '/user/api/correspondence/' + clientId,
            method: 'GET',
            success: function(data) {
                console.log('Correspondence loaded:', data);
                displayCorrespondence(data.correspondence);
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
        
        const clientId = $('#clientSelect').val();
        if (!clientId) {
            alert('Please select a client first');
            return;
        }

        const formData = new FormData(this);
        formData.append('client_id', clientId);

        $.ajax({
            url: '/user/api/correspondence',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
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
