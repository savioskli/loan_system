document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const updateStatusBtn = document.getElementById('updateStatusBtn');
    const statusModal = document.getElementById('statusModal');
    const confirmStatusUpdate = document.getElementById('confirmStatusUpdate');
    const cancelStatusUpdate = document.getElementById('cancelStatusUpdate');
    const exportPdfBtn = document.getElementById('exportPdfBtn');

    // Get guarantor number from URL
    const guarantorNo = window.location.pathname.split('/').pop();

    // Status update modal handling
    updateStatusBtn.addEventListener('click', () => {
        statusModal.classList.remove('hidden');
    });

    cancelStatusUpdate.addEventListener('click', () => {
        statusModal.classList.add('hidden');
        document.getElementById('statusReason').value = '';
    });

    confirmStatusUpdate.addEventListener('click', () => {
        const newStatus = document.getElementById('newStatus').value;
        const reason = document.getElementById('statusReason').value;

        if (!reason.trim()) {
            showNotification('Error', 'Please provide a reason for the status change', 'error');
            return;
        }

        updateGuarantorStatus(newStatus, reason);
    });

    // Update guarantor status
    function updateGuarantorStatus(newStatus, reason) {
        fetch(`/user/api/guarantors/${guarantorNo}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: newStatus,
                reason: reason
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNotification('Success', 'Status updated successfully', 'success');
                statusModal.classList.add('hidden');
                // Reload page to show updated status
                window.location.reload();
            } else {
                showNotification('Error', data.error || 'Failed to update status', 'error');
            }
        })
        .catch(error => {
            console.error('Error updating status:', error);
            showNotification('Error', 'Failed to update status', 'error');
        });
    }

    // Export PDF
    exportPdfBtn.addEventListener('click', () => {
        fetch(`/user/api/guarantors/${guarantorNo}/export`, {
            method: 'GET',
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `guarantor_${guarantorNo}_details.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error exporting PDF:', error);
            showNotification('Error', 'Failed to export PDF', 'error');
        });
    });

    // Show notification
    function showNotification(title, message, type = 'info') {
        // Implement your notification system here
        console.log(`${title}: ${message}`);
    }
});
