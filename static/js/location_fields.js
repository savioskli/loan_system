// Location fields handling
document.addEventListener('DOMContentLoaded', function() {
    const countySelect = document.getElementById('county');
    const subCountySelect = document.getElementById('sub_county');
    const postalTownSelect = document.getElementById('postal_town');
    
    // Function to update sub-counties based on selected county
    function updateSubCounties() {
        const selectedCounty = countySelect.value;
        if (selectedCounty) {
            fetch(`/user/get_sub_counties/${selectedCounty}`)
                .then(response => response.json())
                .then(data => {
                    // Clear current options
                    subCountySelect.innerHTML = '<option value="">Select Sub-County</option>';
                    
                    // Add new options
                    if (data.success && data.data) {
                        data.data.forEach(subCounty => {
                            const option = document.createElement('option');
                            option.value = subCounty;
                            option.textContent = subCounty;
                            subCountySelect.appendChild(option);
                        });
                    }
                    
                    // Enable sub-county select
                    subCountySelect.disabled = false;
                })
                .catch(error => {
                    console.error('Error fetching sub-counties:', error);
                    subCountySelect.innerHTML = '<option value="">Error loading sub-counties</option>';
                });
        } else {
            // Reset and disable sub-county select
            subCountySelect.innerHTML = '<option value="">Select Sub-County</option>';
            subCountySelect.disabled = true;
        }
    }
    
    // Event listeners
    if (countySelect) {
        countySelect.addEventListener('change', updateSubCounties);
    }
    
    // Initialize states
    if (subCountySelect) {
        subCountySelect.disabled = !countySelect.value;
    }
    
    // If county is already selected on page load, update dependent fields
    if (countySelect && countySelect.value) {
        updateSubCounties();
    }
    
    // Initialize postal town select
    if (postalTownSelect) {
        postalTownSelect.disabled = false;
    }
});
