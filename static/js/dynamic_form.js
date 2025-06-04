// Debug: Log all styles for an element
function debugStyles(elementId) {
    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`Element with ID '${elementId}' not found`);
        return;
    }
    
    const styles = window.getComputedStyle(el);
    const styleMap = {};
    
    // Convert CSSStyleDeclaration to a plain object
    for (let i = 0; i < styles.length; i++) {
        const prop = styles[i];
        styleMap[prop] = styles.getPropertyValue(prop);
    }
    
    console.group(`Styles for #${elementId}:`);
    console.table(styleMap);
    console.groupEnd();
}

// Global variables for form state
let form, prevBtn, nextBtn, submitBtn, sections, totalSections, currentSection = 0;

// Navigation handlers
function handlePrevClick() {
    if (currentSection > 0) {
        goToSection(currentSection - 1);
    }
}

function handleNextClick() {
    if (validateCurrentSection()) {
        if (currentSection < totalSections - 1) {
            goToSection(currentSection + 1);
        }
    }
}

// Function to navigate to a specific section
function goToSection(index) {
    console.log(`Navigating to section ${index}`);
    
    // Hide current section
    if (sections[currentSection]) {
        sections[currentSection].classList.add('hidden');
    }
    
    // Show new section
    if (sections[index]) {
        sections[index].classList.remove('hidden');
        currentSection = index;
        
        // Update URL hash
        const sectionId = sections[index].id || `section-${index}`;
        window.location.hash = sectionId;
        
        // Update button states
        updateButtonStates();
        
        // Scroll to top of section
        sections[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        console.log(`Now on section ${currentSection + 1} of ${totalSections}`);
    } else {
        console.error(`Section ${index} not found`);
    }
}

// Update button states based on current section
function updateButtonStates() {
    console.log('Updating button states, current section:', currentSection);
    
    // Update Previous button
    if (prevBtn) {
        if (currentSection === 0) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'inline-flex';
        }
    }
    
    // Update Next/Submit button
    if (nextBtn) {
        if (currentSection === totalSections - 1) {
            nextBtn.style.display = 'none';
            if (submitBtn) submitBtn.style.display = 'inline-flex';
        } else {
            nextBtn.style.display = 'inline-flex';
            if (submitBtn) submitBtn.style.display = 'none';
        }
    }
    
    // Debug: Log button states
    console.log('Button states updated:', {
        prevBtn: prevBtn ? prevBtn.style.display : 'N/A',
        nextBtn: nextBtn ? nextBtn.style.display : 'N/A',
        submitBtn: submitBtn ? submitBtn.style.display : 'N/A',
        currentSection,
        totalSections
    });
}

// Validate current section
function validateCurrentSection() {
    console.log('Validating section', currentSection);
    let isValid = true;
    
    // Get all required fields in current section
    const requiredFields = sections[currentSection].querySelectorAll('[required]');
    console.log(`Found ${requiredFields.length} required fields in section ${currentSection}`);
    
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

// Initialize form
function initForm() {
    console.log('Initializing form with', totalSections, 'sections');
    
    // Show first section and hide others
    goToSection(0);
    
    // Add click handlers for navigation buttons
    if (prevBtn) {
        prevBtn.removeEventListener('click', handlePrevClick);
        prevBtn.addEventListener('click', handlePrevClick);
    }
    
    if (nextBtn) {
        nextBtn.removeEventListener('click', handleNextClick);
        nextBtn.addEventListener('click', handleNextClick);
    }
    
    // Initialize system reference fields after a short delay
    setTimeout(initializeSystemReferenceFields, 100);
}

// Track which fields have been initialized to prevent duplicates
const initializedFields = new Set();

// Function to log system field information
function logSystemFieldInfo(field, referenceId, index) {
    const fieldInfo = {
        id: field.id || 'none',
        name: field.name || 'none',
        type: field.type || field.tagName,
        referenceId: referenceId,
        index: index + 1,
        parentId: field.parentElement ? field.parentElement.id : 'none',
        hasForm: !!field.form
    };
    
    console.group(`🔍 System Field #${fieldInfo.index}: ${fieldInfo.id || fieldInfo.name}`);
    console.log('📋 Field Info:', fieldInfo);
    console.groupEnd();
    
    return fieldInfo;
}

// Function to handle system reference fields
function handleSystemReferenceFields() {
    console.log('🚀 Initializing system reference fields');
    
    // Debug: Log all elements with data-reference-id
    const allRefFields = document.querySelectorAll('[data-reference-id]');
    console.log('All elements with data-reference-id:', allRefFields);
    
    // Find all potential system reference fields in the document
    const potentialFields = Array.from(document.querySelectorAll('select[data-reference-id]'));
    
    console.log(`🔍 Found ${potentialFields.length} potential system reference fields in document`);
    
    // Debug: Log all potential fields
    potentialFields.forEach((field, index) => {
        const fieldInfo = {
            id: field.id || 'none',
            name: field.name || 'none',
            tagName: field.tagName,
            referenceId: field.getAttribute('data-reference-id'),
            referenceCode: field.getAttribute('data-reference-code'),
            fieldType: field.getAttribute('data-field-type'),
            parentElement: field.parentElement ? field.parentElement.tagName : 'none',
            form: field.form ? 'has form' : 'no form',
            isVisible: field.getAttribute('data-visible') !== 'false',
            isSystemField: field.hasAttribute('data-is-system-field'),
            formGroup: field.closest('.form-group') ? 'found' : 'not found',
            options: field.tagName === 'SELECT' ? 
                Array.from(field.options).map(opt => ({
                    value: opt.value,
                    text: opt.text,
                    selected: opt.selected
                })) : 'N/A',
            currentValue: field.value || 'empty',
            attributes: {}
        };

        // Get all data attributes
        Array.from(field.attributes).forEach(attr => {
            if (attr.name.startsWith('data-')) {
                fieldInfo.attributes[attr.name] = attr.value;
            }
        });
        
        console.group(`Field ${index + 1}:`);
        console.log('Field Info:', fieldInfo);
        console.groupEnd();
    });

    // Process fields that need initialization
    potentialFields.forEach(field => {
        const id = field.id || field.name;
        const refId = field.getAttribute('data-reference-id');
        
        if (!id || !refId) {
            console.warn('Skipping field - missing ID or reference ID:', { id, refId });
            return;
        }
        
        // Skip if already initialized
        if (initializedFields.has(id)) {
            console.log(`Field ${id} already initialized, skipping`);
            return;
        }
        
        // Mark as initialized
        initializedFields.add(id);
        
        // Initialize the field
        initializeSystemReferenceField(field, refId);
    });
}

// Initialize system reference fields
function initializeSystemReferenceFields() {
    'use strict'; // Help the linter parse this function correctly
    const form = document.getElementById('dynamicForm');
    if (!form) {
        console.error('Form element not found for system reference fields');
        return;
    }

    console.log('🚀 Initializing system reference fields...');
    
    try {
        // Handle system reference fields
        handleSystemReferenceFields();
        console.log('✅ System reference fields updated successfully');
        
        // Debug: Log all system reference fields
        const systemFields = document.querySelectorAll('[data-system-reference]');
        console.log(`🔍 Found ${systemFields.length} system reference fields in the DOM`);
        systemFields.forEach((field, index) => {
            console.log(`Field ${index + 1}:`, {
                id: field.id,
                name: field.name,
                tagName: field.tagName,
                referenceId: field.getAttribute('data-reference-id'),
                isSystemField: field.hasAttribute('data-is-system-field'),
                value: field.value
            });
        });
    } catch (error) {
        console.error('❌ Error updating system reference fields:', error);
    }

    // Set up MutationObserver to detect dynamic changes
    const observer = new MutationObserver((mutations) => {
        const shouldUpdate = mutations.some(mutation => 
            mutation.addedNodes && mutation.addedNodes.length > 0 ||
            (mutation.type === 'attributes' && 
             mutation.target.hasAttribute('data-system-reference'))
        );
        
        if (shouldUpdate) {
            console.log('🔄 DOM changes detected, updating system reference fields...');
            handleSystemReferenceFields();
        }
    });

    // Start observing the form for changes
    observer.observe(form, { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['data-system-reference', 'data-reference-id']
    });

    // Handle changes to system reference fields
    form.addEventListener('change', (event) => {
        const field = event.target;
        if (field.hasAttribute('data-reference-id')) {
            const referenceId = field.getAttribute('data-reference-id');
            const isChecked = field.type === 'checkbox' ? field.checked : true;
            
            console.log('System reference field changed:', {
                field: field,
                referenceId: referenceId,
                value: field.value,
                isChecked: isChecked
            });
            
            // Update visibility of related fields
            document.querySelectorAll(`[data-reference-id="${referenceId}"]`).forEach(targetField => {
                const targetGroup = targetField.closest('.field-group') || targetField.closest('.form-group');
                if (targetGroup) {
                    targetGroup.style.display = isChecked ? 'block' : 'none';
                    console.log('Updated visibility for field group:', targetGroup);
                }
            });
        }
    });

    console.log('✅ System reference field initialization complete');
}

// Initialize system reference fields after a short delay to ensure all elements are in the DOM
function initializeForm() {
    console.log('Initializing form...');
    
    // Initialize the main form first
    initForm();
    
    // Then initialize system reference fields
    console.log('Initializing system reference fields...');
    initializeSystemReferenceFields();
    
    // One more check after a short delay to catch any dynamically added fields
    setTimeout(() => {
        console.log('Running final check for system reference fields...');
        handleSystemReferenceFields();
    }, 500);
    
    // System reference fields are initialized above
    
    // Debug: Log initial state
    console.log('Form initialized');
    console.log('Current section:', currentSection);
    console.log('Total sections:', totalSections);
}

// Initialize when DOM is ready
function initializeApp() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initializeForm();
        });
    } else {
        // DOMContentLoaded has already fired
        setTimeout(initializeForm, 0);
    }
}

// Start the application
initializeApp();
