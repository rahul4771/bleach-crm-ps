
const app = new Vue({
  el: "#appResource",
  delimiters: ["<%", "%>"],
  mounted() {
    console.log("vue app");
  },

  data: {
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
        if (selected.length == 1) {
          $("#starting_id").val(selected[0].start_time);
          $("#ending_id").val(selected[0].end_time);
        } else {
          $("#starting_id").val(selected[0].start_time);
          $("#ending_id").val(selected[selected.length - 1].end_time);
        }
      }
      console.log($("#starting_id").val(), $("#ending_id").val());
      set_params_go();
    },
  },
});

const appCard = new Vue({
  el: "#vueCard",
  delimiters: ["<%", "%>"],
  mounted() {
    console.log("vue app vue card");
  },

  data: {
    userid: [],
    //url:"http://localhost:8000/"
    url: "https://my.bleachkw.com"
    //url : 'http://127.0.0.1:8000'

  },
  methods: {
    // Button click handlers
    viewSkills(element){
      const employeeId = element.dataset.id;
      console.log('View skills for employee ID:', employeeId);
    },
    saveEdit(id) {
      // Collect all checked skill checkboxes
      let selectedServiceTypes = [];

      // Find all checked service type checkboxes for this employee
      $(`input[name="service_type_${id}"]:checked`).each(function () {
        selectedServiceTypes.push($(this).val());
      });

      console.log('Saving skills for employee:', id);
      console.log('Selected service types:', selectedServiceTypes);

      // Send to new endpoint with service type IDs
      fetch('/common/save-employee-skills/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
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
  },
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
