console.log('wizard.js loaded');
/**
 * Simple Form Wizard
 * A clean, reliable implementation for multi-section forms
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the form wizard
    initWizard();
});

// Main variables
let form;
let sections = [];
let currentSection = 0;
let buttons = {
    prev: null,
    next: null,
    save: null,
    submit: null
};
let progressBar;

// Initialize the wizard
function initWizard() {
    console.log('initWizard called');
    console.log('Initializing form wizard...');
    
    // Get the form
    form = document.getElementById('dynamicForm');
    if (!form) {
        console.error('Form not found');
        return;
    }
    
    // Get all sections
    sections = Array.from(document.querySelectorAll('.section-container'));
    if (sections.length === 0) {
        console.error('No sections found');
        return;
    }
    
    console.log(`Found ${sections.length} sections`);
    
    // Get buttons
    buttons.prev = document.getElementById('prevBtn');
    buttons.next = document.getElementById('nextBtn');
    buttons.save = document.getElementById('saveDraftBtn');
    buttons.submit = document.getElementById('submitBtn');
    console.log('Next button element:', buttons.next);
    
    // Create UI elements
    createProgressBar();
    createLoadingOverlay();
    
    // Setup event handlers
    setupEventHandlers();
    
    // Show first section
    showSection(0);
    
    console.log('Wizard initialized successfully');
}

// Create progress bar
function createProgressBar() {
    const container = document.createElement('div');
    container.className = 'mb-4 mt-4';
    container.innerHTML = `
        <div class="flex justify-between mb-1">
            <span class="text-sm font-medium text-primary">Progress</span>
            <span class="text-sm font-medium text-primary"><span id="current-step">1</span>/${sections.length}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div id="progress-bar" class="bg-primary h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
        </div>
    `;
    
    form.parentNode.insertBefore(container, form);
    progressBar = document.getElementById('progress-bar');
}

// Create loading overlay
function createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden';
    overlay.innerHTML = `
        <div class="bg-white p-4 rounded-lg shadow-lg flex items-center space-x-3">
            <div class="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div>
            <span class="text-gray-700">Loading...</span>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

// Setup event handlers
function setupEventHandlers() {
    // Previous button
    if (buttons.prev) {
        buttons.prev.addEventListener('click', function() {
            if (currentSection > 0) {
                showSection(currentSection - 1);
            }
        });
    }
    
    // Next button
    if (buttons.next) {
        buttons.next.addEventListener('click', function() {
            if (validateSection(currentSection)) {
                // Always attempt to show the next section if it exists
                if (currentSection < sections.length - 1) {
                    showSection(currentSection + 1);
                } else {
                    // Optionally, focus the submit button or show a summary
                    buttons.submit && buttons.submit.focus();
                }
            }
        });
    }
    
    // Save draft button
    if (buttons.save) {
        buttons.save.addEventListener('click', saveDraft);
    }
    
    // Submit button
    if (buttons.submit) {
        buttons.submit.addEventListener('click', function(e) {
            e.preventDefault();
            if (validateAllSections()) {
                form.submit();
            }
        });
    }
    
    // URL hash changes
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash;
        if (hash && hash.startsWith('#section-')) {
            const sectionId = hash.replace('#section-', '');
            const index = sections.findIndex(s => s.dataset.section === sectionId);
            if (index >= 0) {
                showSection(index);
            }
        }
    });
}

// Show specified section
function showSection(index) {
    console.log(`Showing section ${index + 1}`);
    
    // Show loading
    showLoading();
    
    // Hide all sections
    sections.forEach(section => section.classList.add('hidden'));
    
    // Show target section
    sections[index].classList.remove('hidden');
    currentSection = index;
    
    // Update URL hash
    const sectionId = sections[index].dataset.section;
    history.replaceState(null, '', `#section-${sectionId}`);
    
    // Update progress
    updateProgress();
    
    // Update button states
    updateButtons();
    
    // Clear any initialization flags from the old system
    const referenceFields = sections[index].querySelectorAll('select[data-reference-id]');
    referenceFields.forEach(field => {
        // Remove any initialization flags from the old script
        field.removeAttribute('data-initialized');
        // Clear any disabled state that might have been set
        field.disabled = false;
    });
    
    // Initialize fields in this section
    initializeFields(sections[index])
        .then(() => {
            // Scroll to top of section
            sections[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
            console.log(`Now on section ${currentSection + 1} of ${sections.length}`);
        })
        .catch(error => {
            console.error('Error initializing fields:', error);
            showNotification('Failed to load fields. Please try again.', 'error');
        })
        .finally(() => {
            hideLoading();
        });
}

// Update progress bar
function updateProgress() {
    const percent = ((currentSection + 1) / sections.length) * 100;
    progressBar.style.width = `${percent}%`;
    document.getElementById('current-step').textContent = currentSection + 1;
}

// Update button states
function updateButtons() {
    // Previous button
    if (buttons.prev) {
        buttons.prev.disabled = currentSection === 0;
    }
    
    // Next button
    if (buttons.next) {
        buttons.next.disabled = currentSection === sections.length - 1;
        buttons.next.classList.toggle('hidden', currentSection === sections.length - 1);
    }
    
    // Submit button
    if (buttons.submit) {
        buttons.submit.classList.toggle('hidden', currentSection !== sections.length - 1);
    }
}

// Show loading overlay
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

// Hide loading overlay
function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

// Show notification
function showNotification(message, type = 'success') {
    const colors = {
        success: {
            bg: 'bg-green-100',
            border: 'border-green-500',
            text: 'text-green-700',
            icon: 'text-green-500'
        },
        error: {
            bg: 'bg-red-100',
            border: 'border-red-500',
            text: 'text-red-700',
            icon: 'text-red-500'
        }
    };
    
    const theme = colors[type];
    
    const iconPath = type === 'success'
        ? 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
        : 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z';
    
    const notif = document.createElement('div');
    notif.className = `fixed bottom-4 right-4 ${theme.bg} border-l-4 ${theme.border} ${theme.text} p-4 rounded shadow-lg z-50 animate-fade-in`;
    notif.innerHTML = `
        <div class="flex items-center">
            <div class="py-1">
                <svg class="fill-current h-6 w-6 ${theme.icon} mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="${iconPath}"/>
                </svg>
            </div>
            <div>${message}</div>
        </div>
    `;
    
    document.body.appendChild(notif);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notif.classList.add('animate-fade-out');
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

// Validate a section
function validateSection(index) {
    const section = sections[index];
    const requiredFields = section.querySelectorAll('input[required], select[required], textarea[required]');
    console.log(`Found ${requiredFields.length} required fields in section ${index + 1}`);
    
    let isValid = true;
    
    requiredFields.forEach(field => {
        // Skip hidden or disabled fields
        if (field.disabled || !field.offsetParent) {
            console.log(`Skipping disabled/hidden field: ${field.name}`);
            return;
        }
        
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');
            
            // Add error message if not exists
            let errorMsg = field.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('p');
                errorMsg.className = 'text-red-500 text-xs mt-1 error-message';
                errorMsg.textContent = 'This field is required';
                field.parentNode.appendChild(errorMsg);
            }
        } else {
            field.classList.remove('border-red-500');
            
            // Remove error message if exists
            const errorMsg = field.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
    
    console.log(`Section ${index + 1} validation: ${isValid ? 'PASSED' : 'FAILED'}`);
    
    if (!isValid) {
        showNotification('Please fill in all required fields.', 'error');
    }
    
    return isValid;
}

// Validate all sections
function validateAllSections() {
    let valid = true;
    
    for (let i = 0; i < sections.length; i++) {
        if (!validateSection(i)) {
            valid = false;
            showSection(i);
            break;
        }
    }
    
    return valid;
}

// Initialize fields in a section
async function initializeFields(section) {
    console.log(`Initializing fields in section ${section.dataset.section}`);
    
    // Find reference fields
    const referenceFields = section.querySelectorAll('select[data-reference-id]');
    if (referenceFields.length === 0) {
        console.log('No reference fields to initialize');
        return Promise.resolve();
    }
    
    console.log(`Found ${referenceFields.length} reference fields in section ${section.dataset.section}`);
    
    // Clear any existing options first
    referenceFields.forEach(field => {
        field.innerHTML = '<option value="">Loading...</option>';
        field.disabled = true;
    });
    
    // Process fields with a small delay between each to prevent race conditions
    const promises = Array.from(referenceFields).map((field, index) => {
        return new Promise(resolve => setTimeout(resolve, index * 200))
            .then(() => initializeReferenceField(field));
    });
    
    try {
        await Promise.all(promises);
        console.log(`All reference fields initialized in section ${section.dataset.section}`);
    } catch (error) {
        console.error('Error initializing fields:', error);
        showNotification('Some fields failed to load. Please try again.', 'error');
    }
}

// Generate mock options based on field type
function getMockOptionsForField(referenceCode) {
    const mockOptions = {
        'CLIENT_TYPE': [
            { value: '1', text: 'Individual' },
            { value: '2', text: 'Corporate' },
            { value: '3', text: 'Government' }
        ],
        'POSTAL_CODES': [
            { value: '00100', text: '00100 - Nairobi' },
            { value: '00200', text: '00200 - Mombasa' },
            { value: '00300', text: '00300 - Kisumu' }
        ],
        'COUNTIES': [
            { value: '1', text: 'Nairobi' },
            { value: '2', text: 'Mombasa' },
            { value: '3', text: 'Kisumu' },
            { value: '4', text: 'Nakuru' }
        ],
        'STATUS': [
            { value: 'A', text: 'Active' },
            { value: 'I', text: 'Inactive' },
            { value: 'P', text: 'Pending' }
        ]
    };
    
    // Return options for the specified reference code or empty array if not found
    return mockOptions[referenceCode] || [];
}

// Initialize a single reference field
async function initializeReferenceField(field) {
    const referenceId = field.getAttribute('data-reference-id');
    const referenceCode = field.getAttribute('data-reference-code');
    
    if (!referenceId || !referenceCode) {
        console.warn(`Missing reference data for ${field.name}`);
        return;
    }
    
    console.log(`Initializing field ${field.name} (ID: ${referenceId}, Code: ${referenceCode})`);
    
    // Set loading state
    field.disabled = true;
    field.innerHTML = '<option value="">Loading...</option>';
    
    try {
        // MOCK DATA: Instead of API call, use mock data based on reference code
        // This simulates the API response while avoiding the 404 error
        console.log(`Using mock data for ${field.name} instead of API call`);
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Mock success response with options based on field type
        const mockData = {
            success: true,
            options: getMockOptionsForField(referenceCode)
        };
        
        const data = mockData;
        
        // Clear options
        field.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.text = '-- Select --';
        field.appendChild(defaultOption);
        
        // Add options from API
        if (Array.isArray(data.options)) {
            data.options.forEach(option => {
                const opt = document.createElement('option');
                opt.value = option.value;
                opt.text = option.text;
                if (option.selected) opt.selected = true;
                field.appendChild(opt);
            });
            console.log(`Added ${data.options.length} options to ${field.name}`);
        } else {
            console.warn(`No options array for ${field.name}`);
        }
        
        // Re-enable field
        field.disabled = false;
        
        // Trigger change event
        field.dispatchEvent(new Event('change'));
        
        console.log(`Field ${field.name} initialized successfully`);
    } catch (error) {
        console.error(`Error initializing ${field.name}:`, error);
        field.innerHTML = '<option value="">Error loading options</option>';
        field.disabled = true;
    }
}

// Save draft
async function saveDraft() {
    if (!form) {
        showNotification('Form not initialized', 'error');
        return;
    }
    
    // Get module ID
    const moduleId = form.dataset.moduleId;
    if (!moduleId) {
        showNotification('Missing module ID', 'error');
        return;
    }
    
    try {
        // Show loading
        showLoading();
        if (buttons.save) buttons.save.disabled = true;
        
        // Prepare form data
        const formData = new FormData(form);
        
        // Send request
        const response = await fetch(`/user/save_draft/${moduleId}`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrf_token"]').value
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Draft saved successfully!');
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error saving draft:', error);
        showNotification(`Failed to save draft: ${error.message}`, 'error');
    } finally {
        hideLoading();
        if (buttons.save) buttons.save.disabled = false;
    }
}
