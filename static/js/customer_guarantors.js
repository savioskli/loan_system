document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const addGuarantorBtn = document.getElementById('addGuarantorBtn');
    const guarantorModal = document.getElementById('guarantorModal');
    const guarantorForm = document.getElementById('guarantorForm');
    const exportListBtn = document.getElementById('exportListBtn');
    
    // Get customer ID from URL
    const customerId = window.location.pathname.split('/').slice(-2)[0];
    let editingGuarantorNo = null;

    // Add Guarantor button click
    addGuarantorBtn.addEventListener('click', () => {
        editingGuarantorNo = null;
        document.getElementById('modalTitle').textContent = 'Add New Guarantor';
        guarantorForm.reset();
        guarantorModal.classList.remove('hidden');
    });

    // Form submission
    guarantorForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(guarantorForm);
        const guarantorData = Object.fromEntries(formData.entries());
        
        // Add customer_id to the data
        guarantorData.customer_id = customerId;

        const url = editingGuarantorNo 
            ? `/user/api/guarantors/${editingGuarantorNo}`
            : '/user/api/guarantors';

        fetch(url, {
            method: editingGuarantorNo ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(guarantorData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNotification('Success', `Guarantor ${editingGuarantorNo ? 'updated' : 'added'} successfully`, 'success');
                closeModal();
                window.location.reload();
            } else {
                showNotification('Error', data.error || 'Failed to save guarantor', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving guarantor:', error);
            showNotification('Error', 'Failed to save guarantor', 'error');
        });
    });

    // Edit guarantor
    window.editGuarantor = function(guarantorNo) {
        editingGuarantorNo = guarantorNo;
        document.getElementById('modalTitle').textContent = 'Edit Guarantor';
        
        // Fetch guarantor data
        fetch(`/user/api/guarantors/${guarantorNo}`)
            .then(response => response.json())
            .then(data => {
                // Populate form fields
                Object.keys(data).forEach(key => {
                    const element = document.getElementById(key);
                    if (element) {
                        element.value = data[key];
                    }
                });
                guarantorModal.classList.remove('hidden');
            })
            .catch(error => {
                console.error('Error fetching guarantor:', error);
                showNotification('Error', 'Failed to fetch guarantor details', 'error');
            });
    };

    // View guarantor details
    window.viewGuarantor = function(guarantorNo) {
        window.location.href = `/user/guarantors/${guarantorNo}`;
    };

    // Close modal
    window.closeModal = function() {
        guarantorModal.classList.add('hidden');
        guarantorForm.reset();
        editingGuarantorNo = null;
    };

    // Export list
    exportListBtn.addEventListener('click', () => {
        fetch(`/user/api/customers/${customerId}/guarantors/export`, {
            method: 'GET',
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `customer_${customerId}_guarantors.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error exporting list:', error);
            showNotification('Error', 'Failed to export list', 'error');
        });
    });

    // Show notification
    function showNotification(title, message, type = 'info') {
        // Implement your notification system here
        console.log(`${title}: ${message}`);
    }
});
