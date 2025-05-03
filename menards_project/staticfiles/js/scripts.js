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

function setUserTimezone() {
    if (localStorage.getItem('timezoneSet') === 'true' || window.timezoneSet === true) return;
    
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
        body: JSON.stringify({ timezone }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            localStorage.setItem('timezoneSet', 'true');
            if (!window.timezoneSet) window.location.reload();
        } else {
            console.error('Failed to set timezone:', data.message);
        }
    })
    .catch(error => console.error('Error setting timezone:', error));
}

const departmentPositions = {
    'Front-Desk': ['Cashier', 'Carry-Out', 'Assistant Manager', 'Department Manager', 'General Manager'],
    'Receiving': ['Lumber Yard Associate', 'Receiving Associate', 'Morning Stock', 'Assistant Manager', 'Department Manager'],
    'Electrical': ['Department Manager', 'Assistant Manager', 'Sales Associate'],
    'Plumbing': ['Department Manager', 'Assistant Manager', 'Sales Associate'],
    'Wall Coverings': ['Department Manager', 'Assistant Manager', 'Sales Associate'],
    'Flooring': ['Department Manager', 'Assistant Manager', 'Sales Associate'],
    'Hardware': ['Department Manager', 'Assistant Manager', 'Sales Associate'],
    'Building Materials': ['Department Manager', 'Assistant Manager', 'Sales Associate']
};

function populatePositions(departmentSelect, positionSelect, selectedPosition) {
    if (!departmentSelect || !positionSelect) {
        console.error('Department or Position select element not found');
        return;
    }
    const department = departmentSelect.value;
    positionSelect.innerHTML = '<option value="" disabled selected>Select Position</option>';
    const positions = departmentPositions[department] || [];
    positions.forEach(position => {
        const option = document.createElement('option');
        option.value = position;
        option.textContent = position;
        if (position === selectedPosition) option.selected = true;
        positionSelect.appendChild(option);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('scripts.js loaded');

    // Handle clicks on buttons with data-url using event delegation
    document.body.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-url]');
        if (button) {
            const url = button.getAttribute('data-url');
            if (url && url !== '#') {
                window.location.href = url;
            } else {
                console.error('Button has invalid or missing data-url:', button);
            }
        }
    });

    setUserTimezone();
});