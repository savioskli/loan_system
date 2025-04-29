// Initialize Select2 for customer dropdown
// Global variable to store selected customer data
let selectedCustomerData = null;

$(document).ready(function() {
    // Modal handling
    const modal = document.getElementById('generate-modal');

    function openGenerateModal() {
        modal.classList.remove('hidden');
        initializeSelect2();
    }

    function closeGenerateModal() {
        modal.classList.add('hidden');
        resetForm();
    }

    // Make modal functions available globally
    window.openGenerateModal = openGenerateModal;
    window.closeGenerateModal = closeGenerateModal;

    // Close modal when clicking outside
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeGenerateModal();
        }
    });

    function initializeSelect2() {
        // Remove any existing select2 containers first
        $('.select2-container').remove();

        // Destroy and reinitialize Select2
        if ($('#customer').data('select2')) {
            $('#customer').select2('destroy');
        }

        // Initialize customer select
        $('#customer').select2({
            theme: 'bootstrap-5',
            placeholder: 'Search for a customer...',
            allowClear: true,
            width: '100%',
            dropdownParent: $('#generate-modal'),
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
                    console.log('Customer data received:', data);
                    
                    if (!data || !Array.isArray(data.items)) {
                        console.error('Invalid customer data format:', data);
                        return { results: [] };
                    }
                    
                    return {
                        results: data.items,
                        pagination: {
                            more: data.has_more || false
                        }
                    };
                },
                cache: true
            },
            minimumInputLength: 0,
            templateResult: formatCustomerResult,
            templateSelection: formatCustomerSelection,
            escapeMarkup: function(markup) {
                return markup;
            }
        }).on('select2:select', function(e) {
            const customer = e.params.data;
            updateCustomerDetails(customer);
        }).on('select2:clear', function() {
            $('#customer-details').addClass('hidden');
        });

        // Focus the search box after initialization
        setTimeout(function() {
            $('.select2-search__field').focus();
        }, 100);
    }

    function resetForm() {
        $('#generate-report-form')[0].reset();
        $('#customer').val(null).trigger('change');
        $('#customer-details').addClass('hidden');
    }

    // Form submission is now handled by the validateReportForm function
});

// Function to format customer result
function formatCustomerResult(customer) {
    if (customer.loading) {
        return '<div class="text-gray-500">Loading...</div>';
    }

    // Get the first loan for loan details
    const loan = customer.loans && customer.loans[0] || {};
    const missedPayments = loan.DaysInArrears ? Math.ceil(loan.DaysInArrears / 30) : 0;
    const outstandingAmount = loan.OutstandingBalance || 0;
    const installmentAmount = loan.InstallmentAmount || outstandingAmount;

    return `
        <div class="flex items-center py-1">
            <div class="flex-1">
                <div class="font-medium">${customer.text}</div>
                <div class="text-sm text-gray-500">
                    ${customer.NationalID ? `National ID: ${customer.NationalID}` : ''}
                    ${customer.PhoneNumber ? ` • ${customer.PhoneNumber}` : ''}
                </div>
                ${customer.loans ? `
                    <div class="text-sm text-gray-500">
                        ${customer.loans.length} loan(s) • Outstanding: ${outstandingAmount.toLocaleString('en-US', {style: 'currency', currency: 'KES'})}
                        ${missedPayments > 0 ? ` • ${missedPayments} missed payment(s)` : ''}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Function to format selected customer
function formatCustomerSelection(customer) {
    return customer.text;
}

// Function to update customer details section
function updateCustomerDetails(customer) {
    // Store the selected customer data in the global variable
    selectedCustomerData = customer;
    
    // Get customer details directly from customer object
    $('#customer-name').text(customer.text || '-');
    $('#customer-id').text(customer.NationalID || '-');
    $('#customer-phone').text(customer.PhoneNumber || '-');
    $('#customer-email').text(customer.Email || '-');

    // Get the first loan for loan details
    const loan = customer.loans && customer.loans[0] || {};

    // Calculate missed payments
    const missedPayments = loan.DaysInArrears ? Math.ceil(loan.DaysInArrears / 30) : 0;
    const outstandingAmount = loan.OutstandingBalance || 0;
    const installmentAmount = loan.InstallmentAmount || outstandingAmount;

    // Add loan details
    $('#customer-loan-amount').text(loan.LoanAmount ? loan.LoanAmount.toLocaleString('en-US', {style: 'currency', currency: 'KES'}) : '-');
    $('#customer-outstanding').text(outstandingAmount.toLocaleString('en-US', {style: 'currency', currency: 'KES'}));
    $('#customer-installment').text(installmentAmount.toLocaleString('en-US', {style: 'currency', currency: 'KES'}));
    $('#customer-missed-payments').text(missedPayments || '-');
    
    $('#customer-details').removeClass('hidden');
}

// Function to open the generate report modal
function openGenerateModal() {
    document.getElementById('generate-modal').classList.remove('hidden');
}

// Function to close the generate report modal
function closeGenerateModal() {
    document.getElementById('generate-modal').classList.add('hidden');
    $('#customer').val(null).trigger('change');
    $('#customer-details').addClass('hidden');
    $('#consent').prop('checked', false);
}

// Function to open the view report modal
function openViewModal() {
    document.getElementById('view-modal').classList.remove('hidden');
}

// Function to close the view report modal
function closeViewModal() {
    document.getElementById('view-modal').classList.add('hidden');
    document.getElementById('report-content').innerHTML = '';
}

// Function to validate the CRB report form
function validateReportForm() {
    const customerId = $('#customer').val();
    const bureauId = $('#bureau').val();
    const consent = $('#consent').is(':checked');
    
    if (!customerId || !bureauId || !consent) {
        Swal.fire({
            icon: 'error',
            title: 'Validation Error',
            text: !customerId ? 'Please select a customer' : 
                  !bureauId ? 'Please select a credit bureau' : 
                  'Please confirm customer consent'
        });
        return false;
    }
    
    // Add hidden fields with customer details to the form
    const customerData = selectedCustomerData;
    if (customerData) {
        // Add customer name
        let customerName = '';
        if (customerData.FirstName) customerName += customerData.FirstName + ' ';
        if (customerData.LastName) customerName += customerData.LastName;
        $('<input>').attr({
            type: 'hidden',
            name: 'customer_name',
            value: customerName.trim()
        }).appendTo('#generate-report-form');
        
        // Add national ID
        $('<input>').attr({
            type: 'hidden',
            name: 'national_id',
            value: customerData.NationalID || ''
        }).appendTo('#generate-report-form');
        
        // Add phone number
        $('<input>').attr({
            type: 'hidden',
            name: 'phone_number',
            value: customerData.PhoneNumber || ''
        }).appendTo('#generate-report-form');
        
        // Add email
        $('<input>').attr({
            type: 'hidden',
            name: 'email',
            value: customerData.Email || ''
        }).appendTo('#generate-report-form');
    }
    
    // Show loading state
    const submitBtn = $('#generate-report-form button[type="submit"]');
    submitBtn.html('<i class="fas fa-spinner fa-spin mr-2"></i>Generating...').prop('disabled', true);
    
    // If all validations pass, return true to allow form submission
    return true;
}

// Initialize form submission
$(document).ready(function() {
    $('#generate-report-form').on('submit', function(e) {
        if (!validateReportForm()) {
            e.preventDefault();
            return false;
        }
        // Form will submit normally if validation passes
        return true;
    });
});

// Function to view a CRB report
async function viewReport(reportId) {
    try {
        const response = await fetch(`/user/crb-reports/${reportId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch report');
        }
        
        const report = await response.json();
        
        // Format and display the report
        const content = formatReportContent(report);
        document.getElementById('report-content').innerHTML = content;
        openViewModal();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load report. Please try again.');
    }
}

// Function to format the report content
function formatReportContent(report) {
    return `
        <div class="space-y-4">
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold">Basic Information</h4>
                <dl class="mt-2 grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">National ID</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">${report.national_id}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Credit Score</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">${report.credit_score || 'N/A'}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Report Reference</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">${report.report_reference || 'N/A'}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Generated On</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">${new Date(report.created_at).toLocaleString()}</dd>
                    </div>
                </dl>
            </div>
            
            ${report.report_data ? formatDetailedReport(report.report_data) : ''}
        </div>
    `;
}

// Function to format detailed report data
function formatDetailedReport(reportData) {
    // Format the detailed report data based on the Metropol API response structure
    // This is a placeholder - adjust according to actual API response structure
    return `
        <div class="space-y-4">
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold">Credit Summary</h4>
                <!-- Add credit summary details -->
            </div>
            
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold">Account Information</h4>
                <!-- Add account information -->
            </div>
            
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold">Payment History</h4>
                <!-- Add payment history -->
            </div>
        </div>
    `;
}

// Function to load reports
async function loadReports(page = 1) {
    try {
        const response = await fetch(`/user/crb-reports/list?page=${page}`);
        if (!response.ok) {
            throw new Error('Failed to fetch reports');
        }
        
        const data = await response.json();
        updateReportsTable(data.reports);
        updateStats(data.stats);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load reports. Please try again.');
    }
}

// Function to update the reports table
function updateReportsTable(reports) {
    const tbody = document.getElementById('reports-table-body');
    tbody.innerHTML = reports.map(report => `
        <tr>
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900 dark:text-gray-100">${report.national_id}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-300">${report.credit_score || 'N/A'}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm">
                <span class="inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${getStatusClass(report.status)}">
                    ${report.status}
                </span>
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-300">
                ${new Date(report.created_at).toLocaleString()}
            </td>
            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                ${report.status === 'completed' ? 
                    `<button onclick="viewReport(${report.id})" class="text-primary hover:text-primary-dark">View Report</button>` :
                    ''}
            </td>
        </tr>
    `).join('');
}

// Function to get status CSS classes
function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'completed':
            return 'bg-green-100 text-green-800';
        case 'pending':
            return 'bg-yellow-100 text-yellow-800';
        case 'failed':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

// Function to update statistics
function updateStats(stats) {
    document.getElementById('negative-count').textContent = stats.negative_count;
    document.getElementById('positive-count').textContent = stats.positive_count;
    document.getElementById('pending-count').textContent = stats.pending_count;
}

// Load reports when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadReports();
});
