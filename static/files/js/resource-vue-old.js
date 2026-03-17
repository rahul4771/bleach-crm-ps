const appCard = new Vue({
  el: "#vueCard",
  delimiters: ["<%", "%>"],
  mounted() {
    console.log("vue app vue card");
    // Initialize workers from Django data
    if (window.workersData) {
      this.workers = window.workersData;
      console.log('Workers loaded:', this.workers);
    }
  },

  data() {
    return {
      workers: [],
      userid: [],
      url: "https://my.bleachkw.com"
    };
  },
  methods: {
    // Button click handlers
    viewSkills(element) {
      console.log("element", element);
      const employeeId = element.dataset.id;
      console.log('View skills for employee ID:', employeeId);
    },
    saveEdit(id) {
      // Collect all checked skill checkboxes
      let selectedServiceTypes = [];

      // Find all checked service type checkboxes for this employee
      const checkboxes = document.querySelectorAll(`input[name="service_type_${id}"]:checked`);
      checkboxes.forEach(checkbox => {
        selectedServiceTypes.push(checkbox.value);
      });

      console.log('Saving skills for employee:', id);
      console.log('Selected service types:', selectedServiceTypes);

      // Get CSRF token
      const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]").value;

      // Send to new endpoint with service type IDs
      fetch('/common/save-employee-skills/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          employee_id: id,
          service_type_ids: selectedServiceTypes
        })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            console.log('✅ Skills saved successfully!');
            console.log('Details:', data.details);

            // Show success message with operation details
            alert(`✅ ${data.message}\nEmployee: ${data.details.employee_name}`);

            // Reload page to reflect changes
            location.reload();
          } else {
            console.error('❌ Failed to save skills:', data.error);
            alert(`❌ Error: ${data.error}`);
          }
        })
        .catch((error) => {
          console.error('❌ Network error while saving skills:', error);
          alert('❌ Network error: ' + error.message);
        });
    },
    getCsrfToken(name = 'csrftoken') {
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
  },
});
