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
    },
  },
});

const app2 = new Vue({
  el: "#appResource2",
  delimiters: ["<%", "%>"],
  mounted() {
    console.log("vue app");
  },

  data: {
    solt2: [
      { solt2: 1, check: false, start_time: "12:00 AM", end_time: "02:00 AM" },
      { solt2: 2, check: false, start_time: "02:00 AM", end_time: "04:00 AM" },
      { solt2: 3, check: false, start_time: "04:00 AM", end_time: "06:00 AM" },
      { solt2: 4, check: false, start_time: "06:00 AM", end_time: "08:00 AM" },
      { solt2: 5, check: false, start_time: "08:00 AM", end_time: "10:00 AM" },
      { solt2: 6, check: false, start_time: "10:00 AM", end_time: "12:00 PM" },
      { solt2: 7, check: false, start_time: "12:00 PM", end_time: "02:00 PM" },
      { solt2: 8, check: false, start_time: "02:00 PM", end_time: "04:00 PM" },
      { solt2: 9, check: false, start_time: "04:00 PM", end_time: "06:00 PM" },
      { solt2: 10, check: false, start_time: "06:00 PM", end_time: "08:00 PM" },
      { solt2: 11, check: false, start_time: "08:00 PM", end_time: "10:00 PM" },
      { solt2: 12, check: false, start_time: "10:00 PM", end_time: "12:00 AM" },
    ],
  },
  methods: {
    selectsolt2(solt2No) {
      var pos, prevPos;
      if (solt2No == 1) {
        pos = 0;
        prevPos = null;
      } else {
        pos = solt2No - 1;
        prevPos = solt2No - 2;
      }
      var firstFlag = true;
      for (var i = 0; i < this.solt2.length; i++) {
        if (this.solt2[i].check) {
          firstFlag = false;
          break;
        }
      }
      if (!this.solt2[pos].check) {
        if (firstFlag) {
          this.solt2[pos].check = true;
        } else {
          if (prevPos != null) {
            if (this.solt2[prevPos].check || this.solt2[solt2No].check) {
              this.solt2[pos].check = true;
            }
          } else {
            if (this.solt2[solt2No].check) {
              this.solt2[pos].check = true;
            }
          }
        }
      } else {
        for (var j = pos; j < this.solt2.length; j++) {
          this.solt2[j].check = false;
        }
      }
      var selected2 = [];
      for (var i = 0; i < this.solt2.length; i++) {
        if (this.solt2[i].check) {
          selected2.push(this.solt2[i]);
        }
      }

      if (selected2.length > 0) {
        if (selected2.length == 1) {
          $("#filter_starting_id").val(selected2[0].start_time);
          $("#filter_ending_id").val(selected2[0].end_time);
        } else {
          $("#filter_starting_id").val(selected2[0].start_time);
          $("#filter_ending_id").val(selected2[selected2.length - 1].end_time);
        }
      }

      console.log(
        "fliter",
        $("#filter_starting_id").val(),
        $("#filter_ending_id").val()
      );
    },
  },
});
