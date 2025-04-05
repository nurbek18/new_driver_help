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
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
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
    const emptyState = document.getElementById('empty-state');
    
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
    
    if (emptyState) {
        emptyState.classList.add('d-none');
    }
    
    // Access translations from the global scope
    const t = window.translations || {
        contact_whatsapp: "Contact via WhatsApp",
        available: "Available",
        unavailable: "Unavailable",
        age: "Age",
        gender: "Gender",
        phone_number: "Phone Number"
    };
    
    fetch('/api/drivers')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            
            if (!Array.isArray(data)) {
                console.error('Received data is not an array:', data);
                throw new Error('Invalid data format received from server');
            }
            
            if (data.length === 0) {
                if (emptyState) {
                    emptyState.classList.remove('d-none');
                } else {
                    driversList.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No drivers available at this time.</p></div>';
                }
                return;
            }
            
            driversList.innerHTML = '';
            data.forEach(driver => {
                const availabilityStatus = driver.available ? 
                    `<span class="status-indicator available"></span>${t.available}` : 
                    `<span class="status-indicator unavailable"></span>${t.unavailable}`;
                
                const driverCard = `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="card driver-card ${driver.available ? 'border-success' : 'border-danger'}">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="card-title mb-0">${driver.name}</h5>
                                <span class="badge ${driver.available ? 'bg-success' : 'bg-danger'}">${availabilityStatus}</span>
                            </div>
                            <div class="card-body">
                                <p class="driver-code"><strong>ID:</strong> ${driver.driver_code || 'N/A'}</p>
                                <p class="card-text"><strong>${t.age}:</strong> ${driver.age}</p>
                                <p class="card-text"><strong>${t.gender}:</strong> ${driver.gender}</p>
                                <p class="card-text"><strong>${t.phone_number}:</strong> ${driver.phone}</p>
                                <a href="https://wa.me/${driver.whatsapp.replace(/\D/g, '')}" target="_blank" class="btn btn-success w-100">
                                    <i class="fab fa-whatsapp me-2"></i>${t.contact_whatsapp}
                                </a>
                            </div>
                        </div>
                    </div>
                `;
                driversList.innerHTML += driverCard;
            });
            
            // Apply any active filters
            filterDrivers();
        })
        .catch(error => {
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            console.error('Error fetching drivers:', error);
            driversList.innerHTML = `<div class="col-12 text-center"><p class="alert alert-danger">Error loading drivers: ${error.message}</p></div>`;
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
        
        const driverCards = document.querySelectorAll('.driver-card');
        let visibleCount = 0;
        
        driverCards.forEach(card => {
            const parent = card.closest('.col-md-6');
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
                const genderElement = card.querySelector('.card-text:nth-child(3)');
                if (genderElement) {
                    const genderText = genderElement.textContent;
                    if (!genderText.toLowerCase().includes(filterOptions.gender.toLowerCase())) {
                        show = false;
                    }
                }
            }
            
            // Show or hide based on filters
            if (parent) {
                parent.style.display = show ? 'block' : 'none';
                if (show) visibleCount++;
            }
        });
        
        // Show empty state if no drivers match filters
        const emptyState = document.getElementById('empty-state');
        if (emptyState) {
            if (visibleCount === 0) {
                emptyState.classList.remove('d-none');
            } else {
                emptyState.classList.add('d-none');
            }
        }
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
