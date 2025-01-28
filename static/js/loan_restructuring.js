// Loan Restructuring JavaScript Module

// Common function to show notifications
function showNotification(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-4 rounded-lg text-white ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} shadow-lg z-50`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Function to populate loan dropdowns
async function populateLoanDropdowns() {
    try {
        const response = await fetch('/user/api/active-loans');
        if (!response.ok) throw new Error('Failed to fetch active loans');
        
        const loans = await response.json();
        const dropdowns = document.querySelectorAll('select[name="loan_id"]');
        
        dropdowns.forEach(dropdown => {
            dropdown.innerHTML = '<option value="">Select a loan</option>' + 
                loans.map(loan => `
                    <option value="${loan.id}" 
                            data-balance="${loan.balance}"
                            data-client="${loan.client_name}">
                        ${loan.loan_number} - ${loan.client_name}
                    </option>
                `).join('');
            
            // Add change event listener to update current balance
            dropdown.addEventListener('change', (e) => {
                const selectedOption = e.target.options[e.target.selectedIndex];
                const balance = selectedOption.dataset.balance;
                const form = e.target.closest('form');
                if (form && balance) {
                    form.querySelector('input[name="current_balance"]').value = balance;
                    // For refinancing, update new total
                    const additionalAmount = form.querySelector('input[name="additional_amount"]');
                    if (additionalAmount) {
                        const newTotal = parseFloat(balance) + (parseFloat(additionalAmount.value) || 0);
                        form.querySelector('input[name="new_total"]').value = newTotal;
                    }
                    // For settlement, update waiver amount
                    const settlementAmount = form.querySelector('input[name="settlement_amount"]');
                    if (settlementAmount) {
                        const waiver = parseFloat(balance) - (parseFloat(settlementAmount.value) || 0);
                        form.querySelector('input[name="waiver_amount"]').value = waiver;
                    }
                }
            });
        });
    } catch (error) {
        console.error('Error fetching loans:', error);
        showNotification('Failed to load active loans', 'error');
    }
}

// Loan Rescheduling Functions
async function createLoanRescheduling(data) {
    try {
        const response = await fetch('/user/api/loan-rescheduling/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to create loan rescheduling request');
        
        const result = await response.json();
        showNotification('Loan rescheduling request created successfully');
        return result;
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

// Loan Refinancing Functions
async function createLoanRefinancing(data) {
    try {
        const response = await fetch('/user/api/refinancing/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to create loan refinancing request');
        
        const result = await response.json();
        showNotification('Loan refinancing request created successfully');
        return result;
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

// Settlement Plan Functions
async function createSettlementPlan(data) {
    try {
        const response = await fetch('/user/api/settlement-plans/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to create settlement plan');
        
        const result = await response.json();
        showNotification('Settlement plan created successfully');
        return result;
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

// Event Listeners for Forms
document.addEventListener('DOMContentLoaded', () => {
    // Populate loan dropdowns
    populateLoanDropdowns();

    // Loan Rescheduling Form
    const reschedulingForm = document.getElementById('reschedulingForm');
    if (reschedulingForm) {
        reschedulingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(reschedulingForm);
            const data = Object.fromEntries(formData.entries());
            try {
                await createLoanRescheduling({
                    ...data,
                    current_balance: parseFloat(data.current_balance),
                    new_tenure: parseInt(data.new_tenure),
                    new_installment: parseFloat(data.new_installment),
                    loan_id: parseInt(data.loan_id)
                });
                closeModal('newReschedulingModal');
                window.location.reload();
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Loan Refinancing Form
    const refinancingForm = document.getElementById('refinancingForm');
    if (refinancingForm) {
        refinancingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(refinancingForm);
            const data = Object.fromEntries(formData.entries());
            try {
                await createLoanRefinancing({
                    ...data,
                    current_balance: parseFloat(data.current_balance),
                    additional_amount: parseFloat(data.additional_amount),
                    new_total: parseFloat(data.new_total),
                    new_tenure: parseInt(data.new_tenure),
                    new_installment: parseFloat(data.new_installment),
                    loan_id: parseInt(data.loan_id)
                });
                closeModal('newRefinancingModal');
                window.location.reload();
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Settlement Plan Form
    const settlementForm = document.getElementById('settlementForm');
    if (settlementForm) {
        settlementForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(settlementForm);
            const data = Object.fromEntries(formData.entries());
            try {
                await createSettlementPlan({
                    ...data,
                    current_balance: parseFloat(data.current_balance),
                    settlement_amount: parseFloat(data.settlement_amount),
                    waiver_amount: parseFloat(data.waiver_amount),
                    loan_id: parseInt(data.loan_id)
                });
                closeModal('newSettlementModal');
                window.location.reload();
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Status Filter Change Handler
    const statusFilter = document.querySelector('select[name="status"]');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            const status = statusFilter.value;
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const statusCell = row.querySelector('td:nth-last-child(2)');
                if (status === 'All' || statusCell.textContent.trim() === status) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Date Range Filter Change Handler
    const dateFilter = document.querySelector('input[type="date"]');
    if (dateFilter) {
        dateFilter.addEventListener('change', () => {
            const selectedDate = new Date(dateFilter.value);
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const dateCell = row.querySelector('td:nth-child(2)');
                const rowDate = new Date(dateCell.dataset.date);
                if (!dateFilter.value || rowDate.toDateString() === selectedDate.toDateString()) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
