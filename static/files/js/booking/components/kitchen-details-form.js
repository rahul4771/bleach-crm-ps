Vue.component('KitchenDetailsForm', {
  props: {
    floorIndex: {
      type: Number,
      required: true
    },
    apartmentIndex: {
      type: Number,
      required: false,
      default: null
    },
    buildingIndex: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      sizeOptions: ['Small', 'Medium', 'Large']
    }
  },
  template: `
    <div class="row kitchen-box p-4">

      <div class="col-md-12 d-flex">
        <div style="margin-top: 16px; padding-top: 4px;">Do you want to clean the Cabinet ?
          <span style="color:red">*</span>
        </div>
        <v-radio-group class="p-2" row v-model="$root.floorCabinetCleaning[buildingIndex][floorIndex]">
          <v-radio :value="true">
            <template v-slot:label>
              <div>Yes<strong class="success--text"></strong></div>
            </template>
          </v-radio>
          <v-radio :value="false">
            <template v-slot:label>
              <div>No <strong class="primary--text"></strong></div>
            </template>
          </v-radio>
        </v-radio-group>
      </div>

      <div class="col-md-12 d-flex">
        <v-radio-group row required v-model="$root.floorKitchenCondition[buildingIndex][floorIndex]">
          <v-radio label="Used Kitchen" value="old"></v-radio>
          <v-radio label="New Kitchen" value="new"></v-radio>
        </v-radio-group>
      </div>

      <div class="col-md-6">
        <v-select v-model="$root.floorKitchenSize[buildingIndex][floorIndex]" :items="sizeOptions" label="Size"></v-select>
      </div>

      <div class="col-md-6">
        <div class="d-flex">
          <div style="margin-top: 16px; padding-top: 4px;">Oil Residue? <span style="color:red">*</span></div>
          <v-radio-group class="p-2" row v-model="$root.floorOilResidue[buildingIndex][floorIndex]">
            <v-radio :value="true">
              <template v-slot:label>
                <div>Yes<strong class="success--text"></strong></div>
              </template>
            </v-radio>
            <v-radio :value="false">
              <template v-slot:label>
                <div>No <strong class="primary--text"></strong></div>
              </template>
            </v-radio>
          </v-radio-group>
        </div>
      </div>
    </div>
  `
});
