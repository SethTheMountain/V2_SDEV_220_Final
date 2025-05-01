// Helper function to get the CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

// Function to detect and send the user's timezone to the server
function setUserTimezone() {
  if (localStorage.getItem('timezoneSet') === 'true') {
      return;
  }
  if (window.timezoneSet === true) {
      localStorage.setItem('timezoneSet', 'true');
      return;
  }
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (!timezone) {
      console.error('Could not detect user timezone');
      return;
  }
  fetch('/set_timezone/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ timezone: timezone }),
  })
  .then(response => response.json())
  .then(data => {
      if (data.status === 'success') {
          localStorage.setItem('timezoneSet', 'true');
          if (!window.timezoneSet) {
              window.location.reload();
          }
      } else {
          console.error('Failed to set timezone:', data.message);
      }
  })
  .catch(error => console.error('Error setting timezone:', error));
}

// Function to populate positions based on department selection
function populatePositions(departmentSelect, positionSelect, selectedPosition) {
  if (!departmentSelect || !positionSelect) {
      console.error('Department or Position select element not found');
      return;
  }
  const positions = {
      'Front-Desk': ['Cashier', 'Carry-Out', 'Assistant Manager', 'Department Manager', 'General Manager'],
      'Receiving': ['Morning Stock', 'Lumber Yard Associate', 'Receiving Associate', 'Assistant Manager', 'Department Manager'],
      'Electrical': ['Sales Associate', 'Assistant Manager', 'Department Manager'],
      'Plumbing': ['Sales Associate', 'Assistant Manager', 'Department Manager'],
      'Wall Coverings': ['Sales Associate', 'Assistant Manager', 'Department Manager'],
      'Flooring': ['Sales Associate', 'Assistant Manager', 'Department Manager'],
      'Hardware': ['Sales Associate', 'Assistant Manager', 'Department Manager'],
      'Building Materials': ['Sales Associate', 'Assistant Manager', 'Department Manager']
  };
  const selectedDepartment = departmentSelect.value;
  positionSelect.innerHTML = '<option value="" disabled selected>Select Position</option>';
  if (positions[selectedDepartment]) {
      positions[selectedDepartment].forEach(position => {
          const option = document.createElement('option');
          option.value = position;
          option.textContent = position;
          if (position === selectedPosition) {
              option.selected = true;
          }
          positionSelect.appendChild(option);
      });
  }
}

// Utility function to navigate to a URL from a button's data-url attribute
function navigateToUrl(button, buttonName) {
  if (!button) {
      console.error(`${buttonName} button not found`);
      return;
  }
  button.addEventListener('click', function () {
      const url = button.getAttribute('data-url');
      if (url) {
          window.location.href = url;
      } else {
          console.error(`${buttonName} button is missing data-url attribute`);
      }
  });
}

// Utility function to validate form inputs
function validateForm(form) {
  if (!form) {
      console.warn('Form not found for validation');
      return;
  }
  form.addEventListener('submit', function (e) {
      const firstName = document.getElementById('first_name')?.value;
      const lastName = document.getElementById('last_name')?.value;
      const employeeId = document.getElementById('employee_id')?.value;
      const phoneNumber = document.getElementById('phone_number')?.value;
      const hoursInput = document.getElementById('hours_per_week')?.value;
      const salaryInput = document.getElementById('hourly_salary')?.value;

      if (firstName && !/^[A-Za-z]+$/.test(firstName)) {
          e.preventDefault();
          alert('First name must contain only letters.');
          return;
      }
      if (lastName && !/^[A-Za-z]+$/.test(lastName)) {
          e.preventDefault();
          alert('Last name must contain only letters.');
          return;
      }
      if (employeeId && !/^\d+$/.test(employeeId)) {
          e.preventDefault();
          alert('Employee ID must contain only numbers.');
          return;
      }
      if (phoneNumber && !/^\d{3}-\d{3}-\d{4}$/.test(phoneNumber)) {
          e.preventDefault();
          alert('Phone number must be in the format 111-111-1111.');
          return;
      }
      if (hoursInput && (isNaN(hoursInput) || parseFloat(hoursInput) <= 0)) {
          e.preventDefault();
          alert('Hours per week must be a positive number.');
          return;
      }
      if (salaryInput && (isNaN(salaryInput) || parseFloat(salaryInput) <= 0)) {
          e.preventDefault();
          alert('Hourly salary must be a positive number.');
          return;
      }
  });
}

// Confirmation page: Add Another and Exit functions
function addAnother() {
  window.location.href = '/register/';
}

function exitRegistration() {
  window.location.href = '/';
}

// Main event listener for DOM content loaded
document.addEventListener('DOMContentLoaded', function () {
  console.log('scripts.js loaded');

  // Set user timezone
  setUserTimezone();

  // Handle navigation for all buttons with data-url attribute
  const buttons = document.querySelectorAll('[data-url]');
  buttons.forEach(button => {
      const buttonName = button.id || button.textContent.trim() || 'Unnamed';
      navigateToUrl(button, buttonName);
  });

  // Register page: Form validation
  validateForm(document.getElementById('registerForm'));

  // Register/Edit page: Populate positions dropdown
  const departmentSelect = document.getElementById('department');
  const positionSelect = document.getElementById('position');
  if (departmentSelect && positionSelect) {
      const selectedPosition = positionSelect?.dataset?.selected || null;
      populatePositions(departmentSelect, positionSelect, selectedPosition);
      departmentSelect.addEventListener('change', () => {
          populatePositions(departmentSelect, positionSelect, null);
      });
  }
});