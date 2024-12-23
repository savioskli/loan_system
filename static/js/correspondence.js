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
