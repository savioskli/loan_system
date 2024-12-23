// Handle direct communication triggers
$(document).ready(function() {
    // SMS functionality
    $('#sendSmsBtn').on('click', function() {
        const phoneNumber = $('#phoneNumber').val();
        const message = $('#smsMessage').val();
        
        if (!phoneNumber || !message) {
            Swal.fire({
                icon: 'error',
                title: 'Missing Information',
                text: 'Please fill in both phone number and message'
            });
            return;
        }

        $.ajax({
            url: '/api/communications/send-sms',
            method: 'POST',
            data: {
                phone_number: phoneNumber,
                message: message
            },
            beforeSend: function() {
                $('#sendSmsBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-2"></i>Sending...');
            },
            success: function(response) {
                Swal.fire({
                    icon: 'success',
                    title: 'SMS Sent',
                    text: 'Message has been sent successfully'
                });
                // Auto-save correspondence
                $('#correspondenceForm').submit();
            },
            error: function(xhr) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: xhr.responseJSON?.message || 'Failed to send SMS'
                });
            },
            complete: function() {
                $('#sendSmsBtn').prop('disabled', false).html('<i class="fas fa-paper-plane mr-2"></i>Send SMS');
            }
        });
    });

    // Email functionality
    $('#sendEmailBtn').on('click', function() {
        const email = $('#emailAddress').val();
        const subject = $('#emailSubject').val();
        const message = $('#emailMessage').val();
        
        if (!email || !subject || !message) {
            Swal.fire({
                icon: 'error',
                title: 'Missing Information',
                text: 'Please fill in all email fields'
            });
            return;
        }

        $.ajax({
            url: '/api/communications/send-email',
            method: 'POST',
            data: {
                email: email,
                subject: subject,
                message: message
            },
            beforeSend: function() {
                $('#sendEmailBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-2"></i>Sending...');
            },
            success: function(response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Email Sent',
                    text: 'Email has been sent successfully'
                });
                // Auto-save correspondence
                $('#correspondenceForm').submit();
            },
            error: function(xhr) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: xhr.responseJSON?.message || 'Failed to send email'
                });
            },
            complete: function() {
                $('#sendEmailBtn').prop('disabled', false).html('<i class="fas fa-envelope mr-2"></i>Send Email');
            }
        });
    });

    // Call functionality
    let callInProgress = false;
    let callStartTime;

    $('#initiateCallBtn').on('click', function() {
        const phoneNumber = $('#callPhoneNumber').val();
        
        if (!phoneNumber) {
            Swal.fire({
                icon: 'error',
                title: 'Missing Information',
                text: 'Phone number is required'
            });
            return;
        }

        $.ajax({
            url: '/api/communications/initiate-call',
            method: 'POST',
            data: {
                phone_number: phoneNumber
            },
            beforeSend: function() {
                $('#initiateCallBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-2"></i>Initiating...');
            },
            success: function(response) {
                callInProgress = true;
                callStartTime = new Date();
                $('#initiateCallBtn').addClass('hidden');
                $('#endCallBtn').removeClass('hidden');
                
                Swal.fire({
                    icon: 'success',
                    title: 'Call Initiated',
                    text: 'Call has been initiated successfully'
                });
            },
            error: function(xhr) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: xhr.responseJSON?.message || 'Failed to initiate call'
                });
            },
            complete: function() {
                $('#initiateCallBtn').prop('disabled', false).html('<i class="fas fa-phone-alt mr-2"></i>Initiate Call');
            }
        });
    });

    $('#endCallBtn').on('click', function() {
        const phoneNumber = $('#callPhoneNumber').val();
        const notes = $('#callNotes').val();
        const duration = Math.round((new Date() - callStartTime) / 1000); // Duration in seconds

        $.ajax({
            url: '/api/communications/end-call',
            method: 'POST',
            data: {
                phone_number: phoneNumber,
                notes: notes,
                duration: duration
            },
            beforeSend: function() {
                $('#endCallBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-2"></i>Ending...');
            },
            success: function(response) {
                callInProgress = false;
                $('#endCallBtn').addClass('hidden');
                $('#initiateCallBtn').removeClass('hidden');
                
                Swal.fire({
                    icon: 'success',
                    title: 'Call Ended',
                    text: 'Call has been ended and logged successfully'
                });
                // Auto-save correspondence
                $('#correspondenceForm').submit();
            },
            error: function(xhr) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: xhr.responseJSON?.message || 'Failed to end call'
                });
            },
            complete: function() {
                $('#endCallBtn').prop('disabled', false).html('<i class="fas fa-phone-slash mr-2"></i>End Call');
            }
        });
    });

    // Handle client selection to populate contact information
    $('#clientSelect').on('change', function() {
        const clientId = $(this).val();
        if (!clientId) return;

        $.ajax({
            url: `/api/clients/${clientId}/contact-info`,
            method: 'GET',
            success: function(response) {
                // Populate contact fields
                $('#phoneNumber, #callPhoneNumber').val(response.phone_number);
                $('#emailAddress').val(response.email);
            },
            error: function(xhr) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Failed to fetch client contact information'
                });
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Initialize client select with search
    $('#clientSelect').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select a client...',
        ajax: {
            url: '/user/api/clients/search',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },
            processResults: function(data, params) {
                params.page = params.page || 1;
                return {
                    results: data.items.map(client => ({
                        id: client.id,
                        text: `${client.name} (${client.client_no})`
                    })),
                    pagination: {
                        more: data.has_more
                    }
                };
            },
            cache: true
        }
    });

    // Load correspondence when client is selected
    $('#clientSelect').on('change', function() {
        const clientId = $(this).val();
        if (clientId) {
            loadCorrespondence(clientId);
        } else {
            clearCorrespondence();
        }
    });

    // Load correspondence for a client
    function loadCorrespondence(clientId) {
        $.ajax({
            url: `/user/api/correspondence/${clientId}`,
            method: 'GET',
            beforeSend: function() {
                $('#correspondenceList ul').html('<div class="flex justify-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>');
            },
            success: function(response) {
                displayCorrespondence(response.correspondence);
            },
            error: function(xhr) {
                showToast('Failed to load correspondence', 'error');
                $('#correspondenceList ul').html('<div class="text-center py-8 text-gray-500">Failed to load correspondence</div>');
            }
        });
    }

    // Display correspondence in timeline view
    function displayCorrespondence(correspondence) {
        if (!correspondence.length) {
            $('#correspondenceList ul').html('<div class="text-center py-8 text-gray-500">No correspondence found</div>');
            return;
        }

        const html = correspondence.map((item, index) => `
            <li>
                <div class="relative pb-8">
                    ${index < correspondence.length - 1 ? '<span class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true"></span>' : ''}
                    <div class="relative flex space-x-3">
                        <div>
                            <span class="h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white bg-${getTypeColor(item.type)}">
                                ${getTypeIcon(item.type)}
                            </span>
                        </div>
                        <div class="flex min-w-0 flex-1 justify-between space-x-4">
                            <div>
                                <p class="text-sm text-gray-700 dark:text-gray-300">${item.content}</p>
                                ${item.attachment ? `
                                    <a href="${item.attachment}" class="inline-flex items-center mt-2 text-sm text-primary hover:text-primary-dark">
                                        <i class="fas fa-paperclip mr-1"></i>
                                        View Attachment
                                    </a>
                                ` : ''}
                            </div>
                            <div class="whitespace-nowrap text-right text-sm text-gray-500">
                                <div>${formatDate(item.created_at)}</div>
                                <div class="text-xs text-gray-400">by ${item.sent_by}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </li>
        `).join('');

        $('#correspondenceList ul').html(html);
    }

    // Clear correspondence list
    function clearCorrespondence() {
        $('#correspondenceList ul').html('<div class="text-center py-8 text-gray-500">Select a client to view correspondence</div>');
    }

    // Helper functions
    function getTypeColor(type) {
        const colors = {
            'sms': 'blue-500',
            'email': 'green-500',
            'call': 'purple-500'
        };
        return colors[type] || 'gray-500';
    }

    function getTypeIcon(type) {
        const icons = {
            'sms': '<i class="fas fa-sms text-white"></i>',
            'email': '<i class="fas fa-envelope text-white"></i>',
            'call': '<i class="fas fa-phone-alt text-white"></i>'
        };
        return icons[type] || '<i class="fas fa-comment text-white"></i>';
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        }).format(date);
    }

    // Show toast message
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 z-50 ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
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
        document.getElementById('newCorrespondenceForm').reset();
    }

    newCorrespondenceBtn.addEventListener('click', openNewCorrespondenceModal);
    closeModalBtn.addEventListener('click', closeNewCorrespondenceModal);

    // Handle new correspondence form submission
    document.getElementById('newCorrespondenceForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const clientId = $('#clientSelect').val();
        if (!clientId) {
            showToast('Please select a client first', 'error');
            return;
        }

        const formData = new FormData(this);
        formData.append('client_id', clientId);

        try {
            const response = await fetch('/user/api/correspondence', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            if (response.ok) {
                showToast('Communication saved successfully');
                closeNewCorrespondenceModal();
                loadCorrespondence(clientId);
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Failed to save communication');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast(error.message, 'error');
        }
    });

    // Initial load
    clearCorrespondence();
});
