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
    const driverForm = document.getElementById('driver-registration-form');
    if (driverForm) {
        initDriverForm();
    }

    // Check if we're on the user view page
    const driversList = document.getElementById('drivers-list');
    if (driversList) {
        loadDrivers();
    }
});

// Driver Form Functionality
function initDriverForm() {
    const form = document.getElementById('driver-registration-form');
    
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
            whatsapp: document.getElementById('whatsapp').value,
            available: document.getElementById('available').checked
        };
        
        // Submit data to the API
        fetch('/api/drivers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert('danger', 'Error: ' + data.error);
            } else {
                showAlert('success', 'Driver information saved successfully!');
                form.reset();
                form.classList.remove('was-validated');
            }
        })
        .catch(error => {
            showAlert('danger', 'Error submitting form: ' + error.message);
            console.error('Error:', error);
        });
    });
}

// User View Functionality
function loadDrivers() {
    const driversList = document.getElementById('drivers-list');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
    
    fetch('/api/drivers')
        .then(response => response.json())
        .then(drivers => {
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            
            if (drivers.length === 0) {
                driversList.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No drivers available at this time.</p></div>';
                return;
            }
            
            driversList.innerHTML = '';
            drivers.forEach(driver => {
                const availabilityStatus = driver.available ? 
                    '<span class="status-indicator available"></span>Available' : 
                    '<span class="status-indicator unavailable"></span>Unavailable';
                
                const driverCard = `
                    <div class="col-md-6 col-lg-4">
                        <div class="card driver-card ${driver.available ? 'border-success' : 'border-danger'}">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="card-title mb-0">${driver.name}</h5>
                                <span class="badge ${driver.available ? 'bg-success' : 'bg-danger'}">${availabilityStatus}</span>
                            </div>
                            <div class="card-body">
                                <p class="card-text"><strong>Age:</strong> ${driver.age}</p>
                                <p class="card-text"><strong>Gender:</strong> ${driver.gender}</p>
                                <p class="card-text"><strong>Phone:</strong> ${driver.phone}</p>
                                <a href="https://wa.me/${driver.whatsapp.replace(/\D/g, '')}" target="_blank" class="btn btn-success w-100">
                                    <i class="fab fa-whatsapp me-2"></i>Contact via WhatsApp
                                </a>
                            </div>
                        </div>
                    </div>
                `;
                driversList.innerHTML += driverCard;
            });
        })
        .catch(error => {
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            driversList.innerHTML = `<div class="col-12 text-center"><p class="alert alert-danger">Error loading drivers: ${error.message}</p></div>`;
            console.error('Error fetching drivers:', error);
        });
}

// Filter drivers functionality (for user_view page)
function filterDrivers() {
    const availabilityFilter = document.getElementById('filter-availability');
    const genderFilter = document.getElementById('filter-gender');
    
    if (availabilityFilter && genderFilter) {
        const filterOptions = {
            availability: availabilityFilter.value,
            gender: genderFilter.value
        };
        
        const cards = document.querySelectorAll('.driver-card');
        
        cards.forEach(card => {
            const parent = card.parentElement;
            let show = true;
            
            // Check availability filter
            if (filterOptions.availability !== 'all') {
                const isAvailable = card.classList.contains('border-success');
                if ((filterOptions.availability === 'available' && !isAvailable) || 
                    (filterOptions.availability === 'unavailable' && isAvailable)) {
                    show = false;
                }
            }
            
            // Check gender filter
            if (filterOptions.gender !== 'all' && show) {
                const genderText = card.querySelector('.card-text:nth-child(2)').textContent;
                if (!genderText.includes(filterOptions.gender)) {
                    show = false;
                }
            }
            
            // Show or hide based on filters
            parent.style.display = show ? 'block' : 'none';
        });
    }
}

// Utility function to show alert messages
function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container');
    
    if (alertContainer) {
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
