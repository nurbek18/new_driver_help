// Common functions for all pages

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Check if we're on the driver form page
    const driverForm = document.getElementById('driverForm');
    if (driverForm) {
        initDriverForm();
    }

    // Check if we're on the user view page with drivers container
    const driversContainer = document.getElementById('drivers-container');
    if (driversContainer) {
        loadDrivers();
    }
});

// Driver Form Functionality
function initDriverForm() {
    const form = document.getElementById('driverForm');
    
    if (!form) {
        console.error('Driver form not found');
        return;
    }
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            return;
        }
        
        // Collect form data
        const formData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            phone: document.getElementById('phone').value,
            whatsapp: document.getElementById('whatsapp').value
        };
        
        // Submit data to the API
        fetch('/api/drivers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                // Show error in the modal
                const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
                document.getElementById('error-message').textContent = data.error;
                errorModal.show();
            } else {
                // Show success modal with driver code
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                const driverCodeElement = document.getElementById('driver-code');
                if (driverCodeElement) {
                    driverCodeElement.textContent = data.driver_code;
                }
                successModal.show();
                
                // Reset form
                form.reset();
                form.classList.remove('was-validated');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Show error in the modal
            const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
            document.getElementById('error-message').textContent = error.message;
            errorModal.show();
        });
    });
}

// User View Functionality
function loadDrivers() {
    const driversContainer = document.getElementById('drivers-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const noDrivers = document.getElementById('no-drivers');
    const searchInput = document.getElementById('search-input');
    const genderFilter = document.getElementById('gender-filter');
    
    // Show loading indicator
    if (loadingIndicator) {
        loadingIndicator.classList.remove('d-none');
    }
    
    // Hide no drivers message
    if (noDrivers) {
        noDrivers.classList.add('d-none');
    }
    
    // Prepare query parameters
    let queryParams = new URLSearchParams();
    
    if (searchInput && searchInput.value.trim()) {
        queryParams.append('search', searchInput.value.trim());
    }
    
    if (genderFilter && genderFilter.value !== 'all') {
        queryParams.append('gender', genderFilter.value);
    }
    
    // Fetch drivers with filters
    fetch(`/api/drivers?${queryParams.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }
            
            if (!Array.isArray(data)) {
                console.error('Error fetching drivers:', data);
                throw new Error('Invalid data format received from server');
            }
            
            // Clear the drivers container
            driversContainer.innerHTML = '';
            
            // Check if there are no drivers
            if (data.length === 0) {
                if (noDrivers) {
                    noDrivers.classList.remove('d-none');
                }
                return;
            }
            
            // Create driver cards
            const template = document.getElementById('driver-card-template');
            if (!template) {
                console.error('Driver card template not found');
                return;
            }
            
            data.forEach(driver => {
                const driverCard = template.content.cloneNode(true);
                
                // Set card data
                driverCard.querySelector('.driver-name').textContent = driver.name;
                driverCard.querySelector('.driver-code').textContent = driver.driver_code;
                driverCard.querySelector('.driver-age').textContent = driver.age;
                driverCard.querySelector('.driver-gender').textContent = driver.gender;
                driverCard.querySelector('.driver-phone').textContent = driver.phone;
                
                // Set WhatsApp link
                const whatsappBtn = driverCard.querySelector('.whatsapp-btn');
                if (whatsappBtn) {
                    whatsappBtn.href = `https://wa.me/${driver.whatsapp.replace(/\D/g, '')}`;
                }
                
                driversContainer.appendChild(driverCard);
            });
        })
        .catch(error => {
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }
            
            console.error('Error fetching drivers:', error);
            showAlert('danger', `Error loading drivers: ${error.message}`);
        });
}

// Filter drivers functionality
function filterDrivers() {
    const searchInput = document.getElementById('search-input');
    const genderFilter = document.getElementById('gender-filter');
    
    loadDrivers();
}

// Utility function to show alert messages
function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container');
    
    if (!alertContainer) {
        // Create a floating alert if no container exists
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertElement.style.zIndex = "9999";
        alertElement.style.maxWidth = "90%";
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertElement);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alertElement.classList.remove('show');
            setTimeout(() => {
                alertElement.remove();
            }, 500);
        }, 5000);
    } else {
        // Use the existing alert container
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.role = 'alert';
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.appendChild(alertElement);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alertElement.remove();
        }, 5000);
    }
}
