class SectionDraftHandler {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.init();
    }

    getSectionData(sectionNumber) {
        const section = this.form.querySelector(`[data-section="${sectionNumber}"]`);
        if (!section) return null;

        const formData = new FormData();
        
        // Add all inputs from the section
        section.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.type === 'file') {
                // For file inputs, only add if there's a file selected
                if (input.files.length > 0) {
                    formData.append(input.name, input.files[0]);
                }
            } else {
                formData.append(input.name, input.value);
            }
        });

        // Add CSRF token
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        formData.append('csrf_token', csrfToken);
        formData.append('section_number', sectionNumber);
        formData.append('is_draft', 'true');

        return formData;
    }

    async saveSectionDraft(sectionNumber) {
        const formData = this.getSectionData(sectionNumber);
        if (!formData) return;

        try {
            const moduleId = new URLSearchParams(window.location.search).get('module_id');
            const response = await fetch(`/user/save_section_draft/${moduleId}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to save draft');
            }

            // Show success message
            const button = this.form.querySelector(`button[data-section="${sectionNumber}"]`);
            const originalText = button.textContent;
            button.textContent = 'Saved!';
            button.classList.remove('bg-amber-100', 'hover:bg-amber-200', 'text-amber-700');
            button.classList.add('bg-green-100', 'text-green-700');

            // Revert button text after 2 seconds
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('bg-green-100', 'text-green-700');
                button.classList.add('bg-amber-100', 'hover:bg-amber-200', 'text-amber-700');
            }, 2000);

        } catch (error) {
            console.error('Error saving section draft:', error);
            // Show error message
            alert('Failed to save draft. Please try again.');
        }
    }

    init() {
        // Add click handlers for save draft buttons
        this.form.querySelectorAll('.save-section-draft').forEach(button => {
            button.addEventListener('click', () => {
                const sectionNumber = button.dataset.section;
                this.saveSectionDraft(sectionNumber);
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SectionDraftHandler('dynamicForm');
});
