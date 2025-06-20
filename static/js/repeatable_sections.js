/**
 * RepeatableSections - Handles adding and removing repeatable form section entries
 * For corporate client management (Officials, Signatories, Attachments, Services)
 */
class RepeatableSections {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        // Add entry button click handler
        document.querySelectorAll('.add-entry-btn').forEach(button => {
            button.addEventListener('click', (e) => this.addEntry(e));
        });

        // Remove entry button click handler (delegated)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-entry-btn')) {
                this.removeEntry(e);
            }
        });
    }

    addEntry(e) {
        const button = e.target;
        const section = button.closest('.repeatable-section');
        const entriesContainer = section.querySelector('.repeatable-entries');
        const entryTemplate = section.querySelector('.entry-template').content.cloneNode(true);
        const newEntry = entryTemplate.querySelector('.repeatable-entry');
        
        // Get current number of entries
        const currentEntries = entriesContainer.querySelectorAll('.repeatable-entry').length;
        
        // Check if we've reached the maximum entries
        const maxEntries = parseInt(section.dataset.maxEntries) || 0;
        if (maxEntries > 0 && currentEntries >= maxEntries) {
            alert(`Maximum of ${maxEntries} entries allowed`);
            return;
        }
        
        // Update indices in field names and IDs
        newEntry.querySelectorAll('input, select, textarea').forEach(field => {
            const name = field.getAttribute('name');
            const id = field.getAttribute('id');
            
            if (name) {
                field.setAttribute('name', name.replace(/\[\d+\]/, `[${currentEntries}]`));
            }
            
            if (id) {
                const newId = id.replace(/\d+$/, currentEntries);
                field.setAttribute('id', newId);
                
                // Update associated label if exists
                const label = newEntry.querySelector(`label[for="${id}"]`);
                if (label) {
                    label.setAttribute('for', newId);
                }
            }
            
            // Clear values
            if (field.tagName === 'SELECT') {
                field.selectedIndex = 0;
            } else {
                field.value = '';
            }
        });
        
        // Add the new entry to the container
        entriesContainer.appendChild(newEntry);
        
        // Initialize any special fields in the new entry
        this.initializeSpecialFields(newEntry);
        
        // Show/hide add button based on max entries
        if (maxEntries > 0 && entriesContainer.querySelectorAll('.repeatable-entry').length >= maxEntries) {
            button.style.display = 'none';
        }
    }

    removeEntry(e) {
        const button = e.target;
        const entry = button.closest('.repeatable-entry');
        const section = button.closest('.repeatable-section');
        const entriesContainer = section.querySelector('.repeatable-entries');
        
        // Get minimum required entries
        const minEntries = parseInt(section.dataset.minEntries) || 0;
        
        // Check if we can remove more entries
        if (entriesContainer.querySelectorAll('.repeatable-entry').length <= minEntries) {
            alert(`Minimum of ${minEntries} entries required`);
            return;
        }
        
        // Remove the entry
        entry.remove();
        
        // Reindex remaining entries
        this.reindexEntries(entriesContainer);
        
        // Show add button if it was hidden
        const maxEntries = parseInt(section.dataset.maxEntries) || 0;
        if (maxEntries > 0) {
            section.querySelector('.add-entry-btn').style.display = 'block';
        }
    }

    reindexEntries(container) {
        const entries = container.querySelectorAll('.repeatable-entry');
        
        entries.forEach((entry, index) => {
            entry.querySelectorAll('input, select, textarea').forEach(field => {
                const name = field.getAttribute('name');
                if (name) {
                    field.setAttribute('name', name.replace(/\[\d+\]/, `[${index}]`));
                }
                
                const id = field.getAttribute('id');
                if (id) {
                    const newId = id.replace(/\d+$/, index);
                    field.setAttribute('id', newId);
                    
                    // Update associated label if exists
                    const label = entry.querySelector(`label[for="${id}"]`);
                    if (label) {
                        label.setAttribute('for', newId);
                    }
                }
            });
        });
    }

    initializeSpecialFields(entry) {
        // Initialize any special fields like date pickers, select2, etc.
        // This would depend on what other libraries you're using
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RepeatableSections();
});
