
/**
 * Consolidated Resource Management Vue Application
 * Manages time slot selection, worker display, and skill management
 */
const app = new Vue({
  el: "#resourceApp",
  delimiters: ["<%", "%>"],

  data() {
    return {
      dailyOccupencyCount: 12,
      // Slot management
      solt: [
        { solt: 1, check: false, start_time: "12:00 AM", end_time: "02:00 AM" },
        { solt: 2, check: false, start_time: "02:00 AM", end_time: "04:00 AM" },
        { solt: 3, check: false, start_time: "04:00 AM", end_time: "06:00 AM" },
        { solt: 4, check: false, start_time: "06:00 AM", end_time: "08:00 AM" },
        { solt: 5, check: false, start_time: "08:00 AM", end_time: "10:00 AM" },
        { solt: 6, check: false, start_time: "10:00 AM", end_time: "12:00 PM" },
        { solt: 7, check: false, start_time: "12:00 PM", end_time: "02:00 PM" },
        { solt: 8, check: false, start_time: "02:00 PM", end_time: "04:00 PM" },
        { solt: 9, check: false, start_time: "04:00 PM", end_time: "06:00 PM" },
        { solt: 10, check: false, start_time: "06:00 PM", end_time: "08:00 PM" },
        { solt: 11, check: false, start_time: "08:00 PM", end_time: "10:00 PM" },
        { solt: 12, check: false, start_time: "10:00 PM", end_time: "12:00 AM" },
      ],
      startingTime: '',
      endingTime: '',

      // Filter controls
      workersCalendarDate: '',
      search: '',
      staffTypeFilter: '',
      serviceTypeFilter: '',
      staff_type: '',
      selected_service_type_id: '',

      // Worker display
      workers: [],
      workers_date: '',
      serviceTypes: [],
      service_types: [],
      workerSkills: {},
      existingSkills: {},
      selectedSkills: {},
      editingWorkers: {},
      flippingWorkers: {},
      workerBusySlots: {},

      // UI state
      loadingSkills: false,
      showAvailabilityFilter: false,
      alert: {
        show: false,
        message: '',
        type: 'success'
      },
      url: "https://my.bleachkw.com"
    };
  },

  computed: {
    filteredWorkers() {
      return this.workers;
    }
  },

  mounted() {
    console.log("Resource Management App mounted");

    // Initialize date input with today's date if not set
    const dateInput = document.getElementById('working_calendar_date');
    if (dateInput) {
      if (!dateInput.value) {
        const todayDate = moment().format('DD-MM-YYYY');
        dateInput.value = todayDate;
        this.workersCalendarDate = todayDate;
      } else {
        // Sync existing value with Vue data
        this.workersCalendarDate = dateInput.value;
      }

      // Listen to manual input changes
      dateInput.addEventListener('input', (e) => {
        this.onDateChange(e);
      });

      // Listen to datepicker change event
      $(dateInput).on('change.datetimepicker', (e) => {
        if (e.target.value) {
          this.workersCalendarDate = e.target.value;
          this.setParamsGo();
        }
      });
    }

    // Initialize datepicker
    this.initializeDatepicker();

    // Load initial data
    this.setParamsGo();
  },

  methods: {
    /**
     * Set slot time range
     */
    setSolt(s, e) {
      var sPos, ePos;
      for (var i = 0; i < this.solt.length; i++) {
        if (this.solt[i].start_time == s) {
          sPos = i;
        }
        if (this.solt[i].end_time == e) {
          ePos = i;
        }
      }
      for (var j = sPos; j <= ePos; j++) {
        this.solt[j].check = true;
      }
    },

    /**
     * Toggle slot selection
     */
    selectSolt(soltNo) {
      console.log("soltNoselected :", soltNo);
      var pos, prevPos;
      if (soltNo == 1) {
        pos = 0;
        prevPos = null;
      } else {
        pos = soltNo - 1;
        prevPos = soltNo - 2;
      }
      var firstFlag = true;
      for (var i = 0; i < this.solt.length; i++) {
        if (this.solt[i].check) {
          firstFlag = false;
          break;
        }
      }
      if (!this.solt[pos].check) {
        if (firstFlag) {
          this.solt[pos].check = true;
        } else {
          if (prevPos != null) {
            if (this.solt[prevPos].check || this.solt[soltNo].check) {
              this.solt[pos].check = true;
            }
          } else {
            if (this.solt[soltNo].check) {
              this.solt[pos].check = true;
            }
          }
        }
      } else {
        for (var j = pos; j < this.solt.length; j++) {
          this.solt[j].check = false;
        }
      }

      var selected = [];
      for (var i = 0; i < this.solt.length; i++) {
        if (this.solt[i].check) {
          selected.push(this.solt[i]);
        }
      }

      if (selected.length > 0) {
        if (selected.length == 1) {
          this.startingTime = selected[0].start_time;
          this.endingTime = selected[0].end_time;
        } else {
          this.startingTime = selected[0].start_time;
          this.endingTime = selected[selected.length - 1].end_time;
        }
      }
      this.setParamsGo();
    },

    /**
     * Fetch and update worker data based on filter parameters
     */
    setParamsGo(args = {}) {
      const dateInput = document.getElementById('working_calendar_date');
      const dateValue = dateInput ? dateInput.value : '';

      var params = {
        workers_calendar_date: dateValue || this.workersCalendarDate || '',
        search: this.search || document.getElementById('search-bar')?.value || '',
        staff_type: this.staffTypeFilter || document.getElementById('staff_type_filter_id')?.value || '',
        service_type: this.serviceTypeFilter || document.getElementById('service_type_filter_id')?.value || '',
        starting_time: this.startingTime || document.getElementById('starting_id')?.value || '',
        ending_time: this.endingTime || document.getElementById('ending_id')?.value || ''
      };

      for (key in args)
        if (args.hasOwnProperty(key))
          params[key] = args[key];

      var query = '';
      for (key in params)
        if (params[key])
          query += '&' + key + '=' + params[key].toString();
      query = query.replace('&', '?');

      fetch('/common/resources-management/' + query)
        .then(res => res.json())
        .then(data => {
          this.workers = data.workers || [];
          this.workers_date = data.workers_date || '';
          this.serviceTypes = data.service_types || [];
          this.service_types = data.service_types || [];
          this.initializeWorkerData();
        })
        .catch(err => {
          console.error('Error fetching resource management data:', err);
        });
    },
    /**
     * Initialize worker data - calculate busy slots and attendance
     */
    initializeWorkerData() {
      this.workers.forEach(worker => {
        this.calculateBusySlots(worker);
        this.updateAttendanceStatus(worker);
      });
    },

    /**
     * Edit skill mode - fetch service types and existing skills
     */
    editShow(workerId) {

      // Show the edit form immediately
      this.$set(this.editingWorkers, workerId, true);
      this.loadingSkills = true;

      // Fetch both service types and existing skills
      Promise.all([
        fetch('/common/get-service-types/').then(res => res.json()),
        fetch(`/common/get-employee-skills/?employee_id=${workerId}`).then(res => res.json())
      ])
        .then(([serviceTypesData, skillsData]) => {

          if (serviceTypesData.success && skillsData.success) {
            this.serviceTypes = serviceTypesData.service_types;
            this.service_types = serviceTypesData.service_types;
            this.existingSkills[workerId] = skillsData.skills;

            // Update the skill selection state
            this.$nextTick(() => {
              this.initializeSkillCheckboxes(workerId, skillsData.skills);
            });
          } else {
            console.error('Failed to fetch data');
            console.error('Service Types Success:', serviceTypesData.success, 'Error:', serviceTypesData.error);
            console.error('Skills Success:', skillsData.success, 'Error:', skillsData.error);

            if (serviceTypesData.success) {
              this.serviceTypes = serviceTypesData.service_types || [];
              this.service_types = serviceTypesData.service_types || [];
            }
            if (skillsData.success) {
              this.existingSkills[workerId] = skillsData.skills || [];
            }

            if (!serviceTypesData.success) {
              this.showAlert('Error loading service types: ' + (serviceTypesData.error || 'Unknown error'), 'error');
            }
            if (!skillsData.success) {
              this.showAlert('Error loading existing skills: ' + (skillsData.error || 'Unknown error'), 'error');
            }
          }
          this.loadingSkills = false;
        })
        .catch(err => {
          console.error('Network error:', err);
          this.showAlert('Network error: ' + err.message, 'error');
          this.loadingSkills = false;
        });
    },

    /**
     * Initialize skill checkboxes based on existing skills
     */
    initializeSkillCheckboxes(workerId, existingSkills) {
      // Initialize the array for this worker
      const selectedIds = existingSkills && existingSkills.length > 0
        ? existingSkills.map(skill => skill.id.toString())
        : [];

      // Use $set for proper reactivity
      this.$set(this.selectedSkills, workerId, selectedIds);
    },

    /**
     * Save edited skills for employee
     */
    saveEdit(workerId) {
      // Get selected skills from Vue data instead of DOM
      let selectedServiceTypes = this.selectedSkills[workerId] || [];


      fetch('/common/save-employee-skills/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken('csrftoken')
        },
        body: JSON.stringify({
          employee_id: workerId,
          service_type_ids: selectedServiceTypes
        })
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            this.showStyledAlert('Error: ' + (data.error || 'Failed to save skills'), 'error');
            return;
          }
          this.showStyledAlert('Skills updated Successfully!', 'success');
          // Use Vue reactivity instead of DOM manipulation
          this.$set(this.editingWorkers, workerId, false);
          // Fetch updated skills
          setTimeout(() => {
            this.viewSkills(workerId);
          }, 500);

        })
        .catch(err => {
          this.showStyledAlert('Network error: ' + err.message, 'error');
        });
    },

    /**
     * View skills for employee - flip card and fetch skills
     */
    viewSkills(workerId) {

      this.$set(this.flippingWorkers, workerId, true);

      fetch(`/common/get-employee-skills/?employee_id=${workerId}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {

            if (data.skills && data.skills.length > 0) {
              this.$set(this.workerSkills, workerId, data.skills);
            } else {
              this.$set(this.workerSkills, workerId, []);
            }
          } else {
            console.error('Failed to fetch skills. Error:', data.error);
            this.showAlert('Error fetching skills: ' + (data.error || 'Unknown error'), 'error');
          }
        })
        .catch(err => {
          console.error('Network error while fetching skills:', err);
          this.showAlert('Network error: ' + err.message, 'error');
        });
    },

    /**
     * Toggle flip view for worker card
     */
    flip(workerId) {
      this.$set(this.flippingWorkers, workerId, !this.flippingWorkers[workerId]);
    },

    /**
     * Display styled alert message
     */
    showStyledAlert(message, type = 'success') {
      this.alert.message = message;
      this.alert.type = type;
      this.alert.show = true;

      // Auto-hide alert after 5 seconds
      setTimeout(() => {
        this.alert.show = false;
      }, 5000);
    },

    /**
     * Calculate busy slots for a worker
     */
    calculateBusySlots(worker) {
      const busySlotDetails = {};
      const slotArray = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11], [12, 13], [14, 15], [16, 17], [18, 19], [20, 21], [22, 23]];

      if (worker.cleaning_member_details && worker.cleaning_member_details.length > 0) {
        worker.cleaning_member_details.forEach(cleaningDetail => {
          const startHour = parseInt(cleaningDetail.start_at_hour) || 0;
          const endHour = parseInt(cleaningDetail.end_at_hour) || 0;
          const cleaningPolicy = cleaningDetail.cleaning_policy || 'UNKNOWN';
          const busySlots = [];

          for (let i = 0; i < slotArray.length; i++) {
            if (startHour > endHour) {
              // Overnight shift
              if ((startHour <= slotArray[i][0] && 24 > slotArray[i][0]) ||
                (startHour <= slotArray[i][1] && 24 > slotArray[i][1])) {
                busySlots.push(i + 1);
              }
            } else {
              // Regular shift
              if ((startHour <= slotArray[i][0] && endHour > slotArray[i][0]) ||
                (startHour <= slotArray[i][1] && endHour > slotArray[i][1])) {
                busySlots.push(i + 1);
              }
            }
          }

          if (!busySlotDetails[cleaningPolicy]) {
            busySlotDetails[cleaningPolicy] = [];
          }
          busySlotDetails[cleaningPolicy] = [...busySlotDetails[cleaningPolicy], ...busySlots];
        });
      }

      this.$set(this.workerBusySlots, worker.id, busySlotDetails);
    },

    /**
     * Update attendance status for worker
     */
    updateAttendanceStatus(worker) {
      if (!worker.cleaning_member_details || worker.cleaning_member_details.length === 0) {
        // No cleaning details - worker is unavailable
        worker.attendanceClass = 'dot-gray';
      } else if (worker.leave === 1) {
        worker.attendanceClass = 'dot-red';
      } else {
        worker.attendanceClass = 'dot-green';
      }
    },

    /**
     * Get slot class based on busy slots
     */
    getSlotClass(workerId, slotNo) {
      const busySlots = this.workerBusySlots[workerId] || {};
      let classes = 'resource-card-solt-1';

      if (busySlots['ONE TIME SERVICE'] && busySlots['ONE TIME SERVICE'].includes(slotNo)) {
        classes += ' resource-card-solt-2';
      }
      if (busySlots['SUBSCRIPTION'] && busySlots['SUBSCRIPTION'].includes(slotNo)) {
        classes += ' resource-card-solt-3';
      }

      return classes;
    },

    /**
     * Get CSRF token from cookies
     */
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
    },

    /**
     * Format date for display - Parse as UTC and convert to AST (UTC+3) for Kuwait timezone
     */
    formatDate(dateString) {
      if (!dateString) return '';
      // Parse as UTC time and convert to AST (Kuwait timezone, UTC+3)
      return moment.utc(dateString).utcOffset('+0300').format('MMMM D, YYYY, h a.');
    },

    /**
     * Show alert notification
     */
    showAlert(message, type = 'success') {
      this.alert = {
        show: true,
        message: message,
        type: type
      };

      // Auto-hide after 4 seconds
      setTimeout(() => {
        this.alert.show = false;
      }, 4000);
    },

    /**
     * Close alert
     */
    closeAlert() {
      this.alert.show = false;
    },

    /**
     * Toggle availability filter visibility
     */
    toggleAvailability() {
      this.showAvailabilityFilter = !this.showAvailabilityFilter;
      const filterMenu = document.querySelector('.menu-filter-left');
      if (filterMenu) {
        filterMenu.style.display = this.showAvailabilityFilter ? 'block' : 'none';
      }
    },

    /**
     * Get display date with formatting
     */
    getDisplayDate() {
      const dateInput = document.getElementById('working_calendar_date');
      return dateInput ? dateInput.value : moment().format('DD-MM-YYYY');
    },

    /**
     * Initialize datepicker plugin
     */
    initializeDatepicker() {
      const dateInput = document.getElementById('working_calendar_date');
      if (dateInput && $.fn.datetimepicker) {
        // Initialize with moment.js and custom format
        try {
          $(dateInput).datetimepicker({
            format: 'DD-MM-YYYY',
            useCurrent: false,
            allowInputToggle: true
          });
        } catch (e) {
          console.log('Datepicker initialization note:', e.message);
        }
      }
    },

    /**
     * Handle date change from calendar picker or manual input
     */
    onDateChange(event) {
      const dateValue = event.target.value;
      if (dateValue) {
        this.workersCalendarDate = dateValue;
        this.setParamsGo();
      }
    },
  },
  watch: {
    // Watch for changes if needed
  }
});


var mainurl = window.location.href;
if (mainurl.includes("starting_time")) {
  var urlSplit = mainurl.split("&")
  var s = urlSplit[1].split("=")[1]
  var e = urlSplit[2].split("=")[1]
  var starting_time = s.replace("%20", " ")
  var ending_time = e.replace("%20", " ")
  app.setSolt(starting_time, ending_time)
}
