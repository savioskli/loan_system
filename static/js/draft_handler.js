class DraftHandler {
    constructor() {
        this.initializeHandlers();
    }

    initializeHandlers() {
        // Find all save draft buttons
        const saveDraftButtons = document.querySelectorAll('.save-draft-btn');
        
        // Add click handler to each button
        saveDraftButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleSaveDraft(e));
        });
    }

    handleSaveDraft(event) {
        const button = event.currentTarget;
        const sectionId = button.dataset.sectionId;
        const section = button.closest('.section-container');
        
        // Disable button and show loading state
        button.disabled = true;
        const originalText = button.textContent;
        button.textContent = 'Saving...';
        
        // Collect form data for this section
        const formData = this.collectSectionData(section);
        
        // Send to server
        fetch('/user/save_draft', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                section_id: sectionId,
                form_data: formData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                button.textContent = 'Saved!';
                setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 2000);
                
                // Show toast notification
                this.showToast('Section saved as draft successfully!', 'success');
            } else {
                throw new Error(data.message || 'Failed to save draft');
            }
        })
        .catch(error => {
            console.error('Error saving draft:', error);
            button.textContent = originalText;
            button.disabled = false;
            this.showToast('Failed to save draft. Please try again.', 'error');
        });
    }

    collectSectionData(section) {
        const formData = {};
        
        // Get all form fields in this section
        const fields = section.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            // Skip fields that are hidden due to client type restrictions
            if (field.closest('.form-group').style.display === 'none') {
                return;
            }
            
            if (field.type === 'file') {
                // For file fields, just store the current filename if any
                formData[field.name] = field.dataset.currentFile || '';
            } else {
                formData[field.name] = field.value;
            }
        });
        
        return formData;
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg text-white ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DraftHandler();
});
