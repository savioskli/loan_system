// Function to open the generate report modal
function openGenerateModal() {
    document.getElementById('generate-modal').classList.remove('hidden');
}

// Function to close the generate report modal
function closeGenerateModal() {
    document.getElementById('generate-modal').classList.add('hidden');
    document.getElementById('national-id').value = '';
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

// Function to generate a new CRB report
async function generateReport() {
    const nationalId = document.getElementById('national-id').value.trim();
    
    if (!nationalId) {
        alert('Please enter a National ID');
        return;
    }
    
    try {
        const response = await fetch('/user/crb-reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ national_id: nationalId })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate report');
        }
        
        const data = await response.json();
        closeGenerateModal();
        loadReports(); // Refresh the reports list
        
        if (data.status === 'completed') {
            alert('Report generated successfully!');
        } else {
            alert('Report generation initiated. Please wait while we process your request.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate report. Please try again.');
    }
}

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
