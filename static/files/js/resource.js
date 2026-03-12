
const app = new Vue({
  el: "#appResource",
  delimiters: ["<%", "%>"],
  mounted() {
    console.log("vue app");
    // Initialize date input with today's date if not already set
    const dateInput = document.getElementById('working_calendar_date');
    if (dateInput && !dateInput.value) {
      dateInput.value = moment().format('YYYY-MM-DD');
    }
    this.set_params_go();
  },

  data() {
    return {
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
      ]
    };
  },
  methods: {
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
    selectSolt(soltNo) {
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
        const startingIdInput = document.getElementById("starting_id");
        const endingIdInput = document.getElementById("ending_id");

        if (selected.length == 1) {
          startingIdInput.value = selected[0].start_time;
          endingIdInput.value = selected[0].end_time;
        } else {
          startingIdInput.value = selected[0].start_time;
          endingIdInput.value = selected[selected.length - 1].end_time;
        }
      }
      this.set_params_go();
    },
    set_params_go(args = {}) {
      var url = '{% url "common_items:resource-management" %}';
      var params = {
        workers_calendar_date: $('#working_calendar_date').val(), search: $('#search-bar').val(), staff_type: $('#staff_type_filter_id').val(), service_type: $('#service_type_filter_id').val(), starting_time: $('#starting_id').val(), ending_time: $('#ending_id').val()
      };
      for (key in args)
        if (args.hasOwnProperty(key))
          params[key] = args[key];
      var query = '';
      for (key in params)
        if (params[key])
          query += '&' + key + '=' + params[key].toString();
      query = query.replace('&', '?');
      // window.location.href = url + query;
      fetch('/common/resources-management/' + query).then(res => res.json().then(data => {
        // Update the appCard Vue component with fetched data
        appCard.workers = data.workers || [];
        appCard.workers_date = data.workers_date || '';
        appCard.serviceTypes = data.service_types || [];
        appCard.initializeWorkerData();
      })).catch(err => {
        console.error('Error fetching resource management data:', err);
      });
    }
  },
});

const appCard = new Vue({
  el: "#vueCard",
  delimiters: ["<%", "%>"],
  data() {
    return {
      workers: [],
      workers_date: '',
      serviceTypes: [],
      workerSkills: {},
      existingSkills: {},
      editingWorkers: {},
      flippingWorkers: {},
      workerBusySlots: {},
      selectedDate: new Date(),
      searchQuery: '',
      staffTypeFilter: '',
      serviceTypeFilter: '',
      startingTime: '',
      endingTime: '',
      loadingSkills: false,
      alert: {
        show: false,
        message: '',
        type: 'success'
      },
      userid: [],
      url: "https://my.bleachkw.com"
    };
  },
  computed: {
    filteredWorkers() {
      return this.workers;
    }
  },
  mounted() {
    console.log("Resource Vue app mounted");

    // Initialize workers from data attribute instead of global variable
    const workersData = this.$el.dataset.workers;
    if (workersData) {
      try {
        this.workers = JSON.parse(workersData);
        this.initializeWorkerData();
      } catch (error) {
        console.error('Error parsing workers data:', error);
      }
    }
  },
  methods: {
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
      console.log('Opening edit mode for employee:', workerId);

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
      const existingSkillIds = new Set(existingSkills.map(skill => skill.id));

      // Check appropriate checkboxes
      this.$nextTick(() => {
        existingSkillIds.forEach(skillId => {
          const checkbox = document.getElementById(`service_${workerId}_${skillId}`);
          if (checkbox) {
            checkbox.checked = true;
          }
        });
      });
    },

    /**
     * Save edited skills for employee
     */
    saveEdit(workerId) {
      let selectedServiceTypes = [];

      document.querySelectorAll(`#id_skill_edit_list_${workerId} input[type="checkbox"]:checked`)
        .forEach(cb => {
          selectedServiceTypes.push(cb.value);
        });


      fetch('/common/save-employee-skills/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken('csrftoken')
        },
        body: JSON.stringify({
          employee_id: workerId,
          service_type_ids: selectedServiceTypes
        })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {

            // Show styled success alert
            showStyledAlert('Skills updated Successfully!', 'success');


            document.getElementById("id_done_" + workerId).style.display = "none";
            document.getElementById("id_skill_edit_list_" + workerId).style.display = "none";
            document.getElementById("id_skill_list_" + workerId).style.display = "block";

            // Small delay before refreshing view
            setTimeout(() => {
              viewSkills({ getAttribute: () => workerId });
            }, 500);
          } else {
            showStyledAlert('Error: ' + (data.error || 'Failed to save skills'), 'error');
          }
        })
        .catch(err => {
          showStyledAlert('Network error: ' + err.message, 'error');
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
            console.error('❌ Failed to fetch skills. Error:', data.error);
            this.showAlert('Error fetching skills: ' + (data.error || 'Unknown error'), 'error');
          }
        })
        .catch(err => {
          console.error('❌ Network error while fetching skills:', err);
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
     * Set parameters and navigate
     */
    setParamsGo(args = {}) {
      const params = {
        workers_calendar_date: document.getElementById('working_calendar_date')?.value || '',
        search: document.getElementById('search-bar')?.value || '',
        staff_type: document.getElementById('staff_type_filter_id')?.value || '',
        service_type: document.getElementById('service_type_filter_id')?.value || '',
        starting_time: document.getElementById('starting_id')?.value || '',
        ending_time: document.getElementById('ending_id')?.value || '',
        ...args
      };

      const queryParams = new URLSearchParams();
      Object.keys(params).forEach(key => {
        if (params[key]) {
          queryParams.append(key, params[key]);
        }
      });

      const url = '{% url "common_items:resource-management" %}';
      window.location.href = url + '?' + queryParams.toString();
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
    }
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
