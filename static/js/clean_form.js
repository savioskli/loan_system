// Global variables for form state
let form, prevBtn, nextBtn, saveDraftBtn, submitBtn, sections, totalSections, currentSection = 0;
const initializedFields = new Set();

// Navigation handlers
function handlePrevClick() {
    if (currentSection > 0) {
        goToSection(currentSection - 1);
    }
}

function handleNextClick() {
    if (validateCurrentSection() && currentSection < totalSections - 1) {
        goToSection(currentSection + 1);
    }
}

function handleSubmit(e) {
    e.preventDefault();
    if (validateCurrentSection()) {
        form.submit();
    }
}

// Function to navigate to a specific section
function goToSection(index) {
    if (index < 0 || index >= totalSections) {
        console.error('Invalid section index:', index);
        return false;
    }

    // Hide current section
    sections[currentSection].classList.add('hidden');
    
    // Show the target section
    const targetSection = sections[index];
    if (targetSection) {
        targetSection.classList.remove('hidden');
        currentSection = index;
        updateButtonStates();
        
        // Scroll to top of the section
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        
        console.log('Successfully navigated to section', index);
        return true;
    }
    
    console.error('Target section not found for index:', index);
    return false;
}

// Update button states based on current section
function updateButtonStates() {
    console.log('\n--- Updating button states for section:', currentSection, 'of', totalSections - 1);
    
    // Previous button
    if (prevBtn) {
        const showPrev = currentSection > 0;
        prevBtn.style.setProperty('display', showPrev ? 'inline-flex' : 'none', 'important');
        prevBtn.style.setProperty('visibility', showPrev ? 'visible' : 'hidden', 'important');
        console.log('Previous button:', showPrev ? 'SHOWN' : 'HIDDEN');
    }
    
    // Next button
    if (nextBtn) {
        const showNext = currentSection < totalSections - 1;
        nextBtn.style.setProperty('display', showNext ? 'inline-flex' : 'none', 'important');
        nextBtn.style.setProperty('visibility', showNext ? 'visible' : 'hidden', 'important');
        console.log('Next button:    ', showNext ? 'SHOWN' : 'HIDDEN');
    }
    
    // Submit button
    if (submitBtn) {
        const showSubmit = currentSection === totalSections - 1;
        submitBtn.style.setProperty('display', showSubmit ? 'inline-flex' : 'none', 'important');
        submitBtn.style.setProperty('visibility', showSubmit ? 'visible' : 'hidden', 'important');
        console.log('Submit button:  ', showSubmit ? 'SHOWN' : 'HIDDEN');
    }
    
    // Save Draft button - always visible
    if (saveDraftBtn) {
        saveDraftBtn.style.setProperty('display', 'inline-flex', 'important');
        saveDraftBtn.style.setProperty('visibility', 'visible', 'important');
        console.log('Save button:    ALWAYS VISIBLE');
    }
    
    // Update step indicator
    const currentStepElement = document.getElementById('current-step');
    if (currentStepElement) {
        currentStepElement.textContent = currentSection + 1;
    }
}

// Validate current section
function validateCurrentSection() {
    const currentSectionElement = sections[currentSection];
    const requiredFields = currentSectionElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');
            // Add error message if not already present
            if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
                const errorMsg = document.createElement('p');
                errorMsg.className = 'mt-1 text-sm text-red-600 error-message';
                errorMsg.textContent = 'This field is required';
                field.parentNode.insertBefore(errorMsg, field.nextSibling);
            }
        } else {
            field.classList.remove('border-red-500');
            // Remove error message if exists
            const errorMsg = field.nextElementSibling;
            if (errorMsg && errorMsg.classList.contains('error-message')) {
                errorMsg.remove();
            }
        }
    });
    
    return isValid;
}

// Initialize system reference fields
function initializeSystemReferenceFields() {
    const systemRefFields = document.querySelectorAll('[data-reference-id]');
    systemRefFields.forEach(field => {
        if (field.id && !initializedFields.has(field.id)) {
            initializedFields.add(field.id);
            const refId = field.getAttribute('data-reference-id');
            initializeSystemReferenceField(field, refId);
        }
    });
}

// Initialize a single system reference field
function initializeSystemReferenceField(field, refId) {
    if (!refId) return;
    
    const apiUrl = `/api/system-references/by-id/${refId}`;
    const selectElement = field.tagName === 'SELECT' ? field : field.querySelector('select');
    
    if (!selectElement) return;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!Array.isArray(data)) {
                throw new Error('Invalid data format received from API');
            }
            
            // Clear existing options except the first one (which is usually the default/placeholder)
            while (selectElement.options.length > 1) {
                selectElement.remove(1);
            }
            
            // Add new options
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.value;
                option.textContent = item.label;
                selectElement.appendChild(option);
            });
            
            // Trigger change event in case other scripts are listening
            const event = new Event('change');
            selectElement.dispatchEvent(event);
            
        })
        .catch(error => {
            console.error('Error loading system reference options:', error);
            // Show error message to user
            const errorMsg = document.createElement('div');
            errorMsg.className = 'mt-1 text-sm text-red-600';
            errorMsg.textContent = 'Failed to load options. Please try again.';
            selectElement.parentNode.insertBefore(errorMsg, selectElement.nextSibling);
        });
}

// Initialize form
function initializeForm() {
    console.log('Initializing form...');
    
    // Initialize form elements
    form = document.getElementById('dynamicForm');
    prevBtn = document.getElementById('prevBtn');
    nextBtn = document.getElementById('nextBtn');
    saveDraftBtn = document.getElementById('saveDraftBtn');
    submitBtn = document.getElementById('submitBtn');
    sections = document.querySelectorAll('.form-section');
    totalSections = sections.length;
    
    // Set up event listeners
    if (prevBtn) prevBtn.addEventListener('click', handlePrevClick);
    if (nextBtn) nextBtn.addEventListener('click', handleNextClick);
    if (submitBtn) submitBtn.addEventListener('click', handleSubmit);
    
    // Set up save draft functionality
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                const formData = new FormData(form);
                const response = await fetch(`/user/save_draft/${MODULE_ID}`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name="csrf_token"]').value
                    }
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('Draft saved successfully!');
                } else {
                    alert('Failed to save draft: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error saving draft:', error);
                alert('Error saving draft. Please try again.');
            }
        });
    }
    
    // Show first section and hide others
    sections.forEach((section, index) => {
        if (index !== 0) {
            section.classList.add('hidden');
        } else {
            section.classList.remove('hidden');
        }
    });
    
    // Update button states
    updateButtonStates();
    
    // Initialize system reference fields after a short delay
    setTimeout(initializeSystemReferenceFields, 500);
    
    console.log('Form initialization complete');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeForm);
} else {
    initializeForm();
}
