Vue.component('FloorDetailsForm', {
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
      sizeOptions: ['Small', 'Medium', 'Large'],
      wallTypeOptions: ['Concrete', 'Drywall', 'Painted', 'Tiled'],
      floorTypeOptions: ['Marble', 'Ceramic', 'Wooden', 'Carpet', 'Concrete'],
      ceilingTypeOptions: ['Gypsum', 'False Ceiling', 'Painted', 'Suspended'],
      roomOptions: Array.from({length: 20}, (_, i) => i + 1),
      bathroomOptions: Array.from({length: 10}, (_, i) => i + 1),
      windowOptions: Array.from({length: 15}, (_, i) => i + 1)
    }
  },
  computed: {
    getCurrentSize() {
      const data = this.$root.floorSize;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentWallType() {
      const data = this.$root.floorWallType;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentFloorType() {
      const data = this.$root.floorFloorType;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentCeilingType() {
      const data = this.$root.floorCeilingType;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentRooms() {
      const data = this.$root.floorRooms;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentBathrooms() {
      const data = this.$root.floorBathrooms;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentWindows() {
      const data = this.$root.floorWindows;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex 
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    }
  },
  methods: {
    ensureDataStructure(propName) {
      const data = this.$root[propName];
      if (!data[this.buildingIndex]) {
        this.$root.$set(data, this.buildingIndex, {});
      }
      if (!data[this.buildingIndex][this.floorIndex]) {
        this.$root.$set(data[this.buildingIndex], this.floorIndex, this.apartmentIndex ? {} : null);
      }
    },
    updateValue(propName, value) {
      this.ensureDataStructure(propName);
      const data = this.$root[propName];
      if (this.apartmentIndex) {
        this.$root.$set(data[this.buildingIndex][this.floorIndex], this.apartmentIndex, value);
      } else {
        this.$root.$set(data[this.buildingIndex], this.floorIndex, value);
      }
    }
  },
  template: `
    <div class="row">
      <form-select label="Size" :items="sizeOptions" 
        :value="getCurrentSize"
        @input="updateValue('floorSize', $event)"></form-select>
      <form-select label="Wall type" :items="wallTypeOptions"
        :value="getCurrentWallType"
        @input="updateValue('floorWallType', $event)"></form-select>
      <form-select label="Floor type" :items="floorTypeOptions"
        :value="getCurrentFloorType"
        @input="updateValue('floorFloorType', $event)"></form-select>
      <form-select label="Ceiling type" :items="ceilingTypeOptions"
        :value="getCurrentCeilingType"
        @input="updateValue('floorCeilingType', $event)"></form-select>
      <form-select label="No of rooms" :items="roomOptions"
        :value="getCurrentRooms"
        @input="updateValue('floorRooms', $event)"></form-select>
      <form-select label="No of bathrooms" :items="bathroomOptions"
        :value="getCurrentBathrooms"
        @input="updateValue('floorBathrooms', $event)"></form-select>
      <form-select label="No of windows" :items="windowOptions"
        :value="getCurrentWindows"
        @input="updateValue('floorWindows', $event)"></form-select>
      <kitchen-preference-form :floor-index="floorIndex" :building-index="buildingIndex"></kitchen-preference-form> 
      <div class="col-md-12" v-if="$root.floorKitchenPreference[buildingIndex] && $root.floorKitchenPreference[buildingIndex][floorIndex] === true">
        <h5 class="pt-4">Kitchen Details</h5>
        <div class="col-md-12">
          <kitchen-details-form :floor-index="floorIndex" :apartment-index="apartmentIndex" :building-index="buildingIndex"></kitchen-details-form>
        </div>
      </div>    
      <notes-form :floor-index="floorIndex" :building-index="buildingIndex"></notes-form>
    </div>
  `
});
