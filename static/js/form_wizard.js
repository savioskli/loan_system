/**
 * Form Wizard for Dynamic Forms
 * Converts a multi-section form into a step-by-step wizard
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the form wizard
    initFormWizard();
});

function initFormWizard() {
    const form = document.getElementById('dynamicForm');
    if (!form) return;
    
    // Get all sections
    const sections = document.querySelectorAll('.section-container');
    if (sections.length <= 1) return; // No need for wizard if only one section
    
    // Create wizard navigation
    createWizardNavigation(sections);
    
    // Hide all sections except the first one
    sections.forEach((section, index) => {
        if (index > 0) {
            section.classList.add('hidden');
        } else {
            section.classList.add('active-section');
            updateProgressIndicator(0, sections.length);
        }
    });
    
    // Create navigation buttons
    createNavigationButtons(sections);
    
    // Hide the default submit button and create our own
    const originalSubmitBtn = document.querySelector('#dynamicForm button[type="submit"]');
    if (originalSubmitBtn) {
        originalSubmitBtn.classList.add('hidden');
    }
}

function createWizardNavigation(sections) {
    // Create progress container
    const progressContainer = document.createElement('div');
    progressContainer.className = 'wizard-progress-container mb-6';
    
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'wizard-progress-bar bg-gray-200 rounded-full h-2.5';
    
    // Create progress indicator
    const progressIndicator = document.createElement('div');
    progressIndicator.className = 'wizard-progress-indicator bg-blue-600 h-2.5 rounded-full';
    progressIndicator.style.width = '0%';
    
    // Create step indicators
    const stepsContainer = document.createElement('div');
    stepsContainer.className = 'wizard-steps-container flex justify-between mt-2';
    
    sections.forEach((section, index) => {
        // Get section title
        const sectionTitle = section.querySelector('.section-header h3')?.textContent || `Step ${index + 1}`;
        
        // Create step indicator
        const stepIndicator = document.createElement('div');
        stepIndicator.className = 'wizard-step-indicator';
        stepIndicator.dataset.step = index;
        
        // Create step number
        const stepNumber = document.createElement('div');
        stepNumber.className = `wizard-step-number flex items-center justify-center w-8 h-8 rounded-full ${index === 0 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`;
        stepNumber.textContent = index + 1;
        
        // Create step label
        const stepLabel = document.createElement('div');
        stepLabel.className = 'wizard-step-label text-xs mt-1 text-center';
        stepLabel.textContent = sectionTitle;
        
        // Append to step indicator
        stepIndicator.appendChild(stepNumber);
        stepIndicator.appendChild(stepLabel);
        
        // Append to steps container
        stepsContainer.appendChild(stepIndicator);
    });
    
    // Append progress bar to container
    progressBar.appendChild(progressIndicator);
    progressContainer.appendChild(progressBar);
    progressContainer.appendChild(stepsContainer);
    
    // Insert at the beginning of the form
    const form = document.getElementById('dynamicForm');
    form.insertBefore(progressContainer, form.firstChild);
}

function createNavigationButtons(sections) {
    sections.forEach((section, index) => {
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'wizard-buttons-container flex justify-between mt-6';
        
        // Previous button (except for first section)
        if (index > 0) {
            const prevButton = document.createElement('button');
            prevButton.type = 'button';
            prevButton.className = 'wizard-prev-btn px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300';
            prevButton.innerHTML = '<i class="fas fa-arrow-left mr-1"></i> Previous';
            prevButton.addEventListener('click', () => navigateToSection(index - 1, sections));
            buttonsContainer.appendChild(prevButton);
        } else {
            // Empty div for spacing
            const spacer = document.createElement('div');
            buttonsContainer.appendChild(spacer);
        }
        
        // Next button or Submit for last section
        if (index < sections.length - 1) {
            const nextButton = document.createElement('button');
            nextButton.type = 'button';
            nextButton.className = 'wizard-next-btn px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700';
            nextButton.innerHTML = 'Next <i class="fas fa-arrow-right ml-1"></i>';
            nextButton.addEventListener('click', () => {
                if (validateSection(section)) {
                    navigateToSection(index + 1, sections);
                }
            });
            buttonsContainer.appendChild(nextButton);
        } else {
            // Submit button for last section
            const submitButton = document.createElement('button');
            submitButton.type = 'button';
            submitButton.className = 'wizard-submit-btn px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700';
            submitButton.innerHTML = 'Submit <i class="fas fa-check ml-1"></i>';
            submitButton.addEventListener('click', () => {
                if (validateSection(section)) {
                    document.getElementById('dynamicForm').submit();
                }
            });
            buttonsContainer.appendChild(submitButton);
        }
        
        section.appendChild(buttonsContainer);
    });
}

function navigateToSection(index, sections) {
    // Hide all sections
    sections.forEach(section => {
        section.classList.remove('active-section');
        section.classList.add('hidden');
    });
    
    // Show the target section
    sections[index].classList.remove('hidden');
    sections[index].classList.add('active-section');
    
    // Update progress indicator
    updateProgressIndicator(index, sections.length);
    
    // Update step indicators
    updateStepIndicators(index);
    
    // Scroll to top of the form
    document.getElementById('dynamicForm').scrollIntoView({ behavior: 'smooth' });
}

function updateProgressIndicator(currentStep, totalSteps) {
    const progressPercentage = (currentStep / (totalSteps - 1)) * 100;
    const progressIndicator = document.querySelector('.wizard-progress-indicator');
    if (progressIndicator) {
        progressIndicator.style.width = `${progressPercentage}%`;
    }
}

function updateStepIndicators(currentStep) {
    const stepIndicators = document.querySelectorAll('.wizard-step-number');
    stepIndicators.forEach((indicator, index) => {
        if (index < currentStep) {
            // Completed steps
            indicator.className = 'wizard-step-number flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white';
            indicator.innerHTML = '<i class="fas fa-check"></i>';
        } else if (index === currentStep) {
            // Current step
            indicator.className = 'wizard-step-number flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white';
            indicator.textContent = index + 1;
        } else {
            // Future steps
            indicator.className = 'wizard-step-number flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 text-gray-700';
            indicator.textContent = index + 1;
        }
    });
}

function validateSection(section) {
    // Get all required inputs in the current section
    const requiredInputs = section.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    // Check each required input
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-red-500');
            
            // Add error message if it doesn't exist
            let errorMsg = input.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('p');
                errorMsg.className = 'error-message text-red-500 text-sm mt-1';
                errorMsg.textContent = 'This field is required';
                input.parentNode.appendChild(errorMsg);
            }
        } else {
            input.classList.remove('border-red-500');
            const errorMsg = input.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
    
    return isValid;
}

/**
 * Initialize the form wizard UI
 */
function initFormWizard() {
    // Get all form sections
    const sections = document.querySelectorAll('.section-container');
    if (!sections.length) return;
    
    // Hide all sections except the first one
    sections.forEach((section, index) => {
        if (index > 0) {
            section.classList.add('hidden');
        } else {
            section.classList.add('active-section');
        }
    });
    
    // Create progress bar container
    const progressContainer = document.createElement('div');
    progressContainer.className = 'wizard-progress-container';
    
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'wizard-progress-bar';
    
    const progressIndicator = document.createElement('div');
    progressIndicator.className = 'wizard-progress-indicator';
    progressIndicator.style.width = `${(1 / sections.length) * 100}%`;
    
    progressBar.appendChild(progressIndicator);
    progressContainer.appendChild(progressBar);
    
    // Create step indicators
    const stepsContainer = document.createElement('div');
    stepsContainer.className = 'wizard-steps-container';
    
    // Add step indicators for each section
    sections.forEach((section, index) => {
        const stepIndicator = document.createElement('div');
        stepIndicator.className = 'wizard-step-indicator';
        
        const stepNumber = document.createElement('div');
        stepNumber.className = 'wizard-step-number';
        stepNumber.style.backgroundColor = index === 0 ? '#2563eb' : '#e5e7eb';
        stepNumber.style.color = index === 0 ? 'white' : '#4b5563';
        stepNumber.textContent = index + 1;
        
        const stepLabel = document.createElement('div');
        stepLabel.className = 'wizard-step-label';
        
        // Get section title from the header
        const sectionHeader = section.querySelector('.section-header h3');
        stepLabel.textContent = sectionHeader ? sectionHeader.textContent : `Step ${index + 1}`;
        
        stepIndicator.appendChild(stepNumber);
        stepIndicator.appendChild(stepLabel);
        stepsContainer.appendChild(stepIndicator);
    });
    
    progressContainer.appendChild(stepsContainer);
    
    // Insert progress container before the form
    const form = document.querySelector('#dynamicForm');
    form.parentNode.insertBefore(progressContainer, form);
    
    // Create navigation buttons container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'wizard-buttons-container';
    
    // Create previous button
    const prevButton = document.createElement('button');
    prevButton.type = 'button';
    prevButton.className = 'wizard-prev-btn';
    prevButton.textContent = 'Previous';
    prevButton.style.display = 'none'; // Hide on first step
    prevButton.addEventListener('click', () => navigateStep('prev'));
    
    // Create next button
    const nextButton = document.createElement('button');
    nextButton.type = 'button';
    nextButton.className = 'wizard-next-btn';
    nextButton.textContent = 'Next';
    nextButton.addEventListener('click', () => navigateStep('next'));
    
    // Create submit button
    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.className = 'wizard-submit-btn';
    submitButton.textContent = 'Submit';
    submitButton.style.display = 'none'; // Hide until last step
    
    // Add buttons to container
    buttonsContainer.appendChild(prevButton);
    const rightButtonsContainer = document.createElement('div');
    rightButtonsContainer.appendChild(nextButton);
    rightButtonsContainer.appendChild(submitButton);
    buttonsContainer.appendChild(rightButtonsContainer);
    
    // Add buttons container to the end of each section
    sections.forEach(section => {
        const buttonsCopy = buttonsContainer.cloneNode(true);
        section.appendChild(buttonsCopy);
        
        // Add event listeners to the cloned buttons
        buttonsCopy.querySelector('.wizard-prev-btn').addEventListener('click', () => navigateStep('prev'));
        buttonsCopy.querySelector('.wizard-next-btn').addEventListener('click', () => navigateStep('next'));
    });
    
    // Hide the original submit button
    const originalSubmitBtn = document.querySelector('#dynamicForm button[type="submit"]');
    if (originalSubmitBtn) {
        originalSubmitBtn.classList.add('hidden');
    }
    
    // Initialize current step
    window.currentStep = 0;
    updateWizardUI();
}

/**
 * Navigate between wizard steps
 * @param {string} direction - 'next' or 'prev'
 */
function navigateStep(direction) {
    const sections = document.querySelectorAll('.section-container');
    if (!sections.length) return;
    
    // Get current and next/prev step
    const currentSection = sections[window.currentStep];
    
    if (direction === 'next') {
        // Validate current section before proceeding
        if (!validateSection(currentSection)) {
            return; // Don't proceed if validation fails
        }
        
        // Move to next step if not on last step
        if (window.currentStep < sections.length - 1) {
            window.currentStep++;
        }
    } else if (direction === 'prev') {
        // Move to previous step if not on first step
        if (window.currentStep > 0) {
            window.currentStep--;
        }
    }
    
    // Update UI to reflect current step
    updateWizardUI();
}

/**
 * Update the wizard UI based on current step
 */
function updateWizardUI() {
    const sections = document.querySelectorAll('.section-container');
    if (!sections.length) return;
    
    // Show only current section
    sections.forEach((section, index) => {
        if (index === window.currentStep) {
            section.classList.remove('hidden');
            section.classList.add('active-section');
        } else {
            section.classList.add('hidden');
            section.classList.remove('active-section');
        }
    });
    
    // Update progress bar
    const progressIndicator = document.querySelector('.wizard-progress-indicator');
    if (progressIndicator) {
        progressIndicator.style.width = `${((window.currentStep + 1) / sections.length) * 100}%`;
    }
    
    // Update step indicators
    const stepNumbers = document.querySelectorAll('.wizard-step-number');
    stepNumbers.forEach((step, index) => {
        if (index <= window.currentStep) {
            step.style.backgroundColor = '#2563eb';
            step.style.color = 'white';
        } else {
            step.style.backgroundColor = '#e5e7eb';
            step.style.color = '#4b5563';
        }
    });
    
    // Update navigation buttons
    const prevButtons = document.querySelectorAll('.wizard-prev-btn');
    const nextButtons = document.querySelectorAll('.wizard-next-btn');
    const submitButtons = document.querySelectorAll('.wizard-submit-btn');
    
    prevButtons.forEach(btn => {
        btn.style.display = window.currentStep > 0 ? 'block' : 'none';
    });
    
    nextButtons.forEach(btn => {
        btn.style.display = window.currentStep < sections.length - 1 ? 'block' : 'none';
    });
    
    submitButtons.forEach(btn => {
        btn.style.display = window.currentStep === sections.length - 1 ? 'block' : 'none';
    });
}

/**
 * Validate a form section
 * @param {HTMLElement} section - The section to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function validateSection(section) {
    // Get all required inputs in the current section
    const requiredInputs = section.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    // Check each required input
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-red-500');
            
            // Add error message if it doesn't exist
            let errorMsg = input.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('p');
                errorMsg.className = 'error-message text-red-500 text-sm mt-1';
                errorMsg.textContent = 'This field is required';
                input.parentNode.appendChild(errorMsg);
            }
        } else {
            input.classList.remove('border-red-500');
            const errorMsg = input.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
    
    return isValid;
}

/**
 * Disable the form wizard and restore the normal form view
 */
function disableFormWizard() {
    // Remove wizard navigation
    const progressContainer = document.querySelector('.wizard-progress-container');
    if (progressContainer) {
        progressContainer.remove();
    }
    
    // Show all sections
    const sections = document.querySelectorAll('.section-container');
    sections.forEach(section => {
        section.classList.remove('hidden');
        section.classList.remove('active-section');
    });
    
    // Remove navigation buttons
    const navButtons = document.querySelectorAll('.wizard-buttons-container');
    navButtons.forEach(container => {
        container.remove();
    });
    
    // Show the original submit button
    const originalSubmitBtn = document.querySelector('#dynamicForm button[type="submit"]');
    if (originalSubmitBtn) {
        originalSubmitBtn.classList.remove('hidden');
    }
}
