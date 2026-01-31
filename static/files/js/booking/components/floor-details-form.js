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
      wallTypeOptions: ["Bricks", "Glass", "Concrete", "Ceramic", "Gypsum", "Fabric", "Rubber", "Stone", "Terrazo", "Stainless", "Vinyl", "Wooden", "Others"],
      floorTypeOptions: ["Marble", "Glass", "Stone", "Ceramic", "Concrete", "Bricks", "Wooden", "Terrazo", "Others"],
      ceilingTypeOptions: ["Wooden", "Glass", "Concrete", "Ceramic", "Gypsum", "Foam", "Plastic", "Fabric", "Rubber", "Stainless", "Vinyl", "Others"],
      materials: ["Polyester", "Natural Fiber", "Synthetic", "Leather", "Olefin", "Polypropylene", "Nylon"],
      colors: ["Green", "Silver", "Violet", "White", "Black", "Beige", "Blue", "Grey", "Red", "Cream", "Multi", "Off White", "Meroon", "Orange", "Pink", "Gold", "Brown", "Yellow", "Royal Blue", "Lilac", "Others"],
      roomOptions: Array.from({ length: 20 }, (_, i) => i + 1),
      bathroomOptions: Array.from({ length: 10 }, (_, i) => i + 1),
      windowOptions: Array.from({ length: 15 }, (_, i) => i + 1)
    }
  },
  computed: {
    sizeOptions() {
      // Directly access and format windowSize from root
      if (this.$root.windowSize && this.$root.windowSize.length > 0) {
        return this.$root.windowSize.map(size => size.combinedSize || size.name || size);
      }
    },
    getCurrentSize() {
      const data = this.$root.floorSize;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return null;
      return this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
    },
    getCurrentWallType() {
      const data = this.$root.floorWallType;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return [];
      const value = this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
      return Array.isArray(value) ? value : [];
    },
    getCurrentFloorType() {
      const data = this.$root.floorFloorType;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return [];
      const value = this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
      return Array.isArray(value) ? value : [];
    },
    getCurrentCeilingType() {
      const data = this.$root.floorCeilingType;
      if (!data || !data[this.buildingIndex] || !data[this.buildingIndex][this.floorIndex]) return [];
      const value = this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
      return Array.isArray(value) ? value : [];
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
    },
    toggle(propName) {
      const data = this.$root[propName];
      const currentValue = this.apartmentIndex
        ? (data[this.buildingIndex][this.floorIndex][this.apartmentIndex] || [])
        : (data[this.buildingIndex][this.floorIndex] || []);
      
      let newValue;
      if (propName === 'floorWallType') {
        newValue = currentValue.length === this.wallTypeOptions.length ? [] : [...this.wallTypeOptions];
      } else if (propName === 'floorFloorType') {
        newValue = currentValue.length === this.floorTypeOptions.length ? [] : [...this.floorTypeOptions];
      } else if (propName === 'floorCeilingType') {
        newValue = currentValue.length === this.ceilingTypeOptions.length ? [] : [...this.ceilingTypeOptions];
      }
      
      this.updateValue(propName, newValue);
    },
    removeWallType(item) {
      const data = this.$root.floorWallType;
      const currentValue = this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
      
      const newValue = currentValue.filter(v => v !== item);
      this.updateValue('floorWallType', newValue);
    },
    removeFloorType(item) {
      const data = this.$root.floorFloorType;
      const currentValue = this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
      
      const newValue = currentValue.filter(v => v !== item);
      this.updateValue('floorFloorType', newValue);
    },
    removeCeilingType(item) {
      const data = this.$root.floorCeilingType;
      const currentValue = this.apartmentIndex
        ? data[this.buildingIndex][this.floorIndex][this.apartmentIndex]
        : data[this.buildingIndex][this.floorIndex];
      
      const newValue = currentValue.filter(v => v !== item);
      this.updateValue('floorCeilingType', newValue);
    },
    toggleItem(propName, item) {
      const data = this.$root[propName];
      const currentValue = this.apartmentIndex
        ? (data[this.buildingIndex][this.floorIndex][this.apartmentIndex] || [])
        : (data[this.buildingIndex][this.floorIndex] || []);
      
      let newValue;
      if (currentValue.includes(item)) {
        newValue = currentValue.filter(v => v !== item);
      } else {
        newValue = [...currentValue, item];
      }
      
      this.updateValue(propName, newValue);
    }
  },
  template: `
    <div class="row">
      <form-select label="Size" :items="sizeOptions" 
        :value="getCurrentSize"
        @input="updateValue('floorSize', $event)"></form-select>
      <form-select label="Wall type" :items="wallTypeOptions"
        :value="getCurrentWallType"
        @input="updateValue('floorWallType', $event)"
        multiple
        chips>
        <template v-slot:prepend-item>
          <v-list-item ripple @click="toggle('floorWallType')">
            <v-list-item-action>
              <v-checkbox :input-value="allWallTypeSelected"></v-checkbox>
            </v-list-item-action>
            <v-list-item-title>Select All</v-list-item-title>
          </v-list-item>
          <v-divider class="mt-2"></v-divider>
        </template>
        <template v-slot:selection="data">
          <v-chip v-bind="data.attrs" :input-value="data.selected" close @click="data.select" @click:close="removeWallType(data.item)">
            {{ data.item }}
          </v-chip>
        </template>
        <template v-slot:item="data">
          <v-list-item @click="toggleItem('floorWallType', data.item)" ripple>
            <v-list-item-action>
              <v-checkbox :input-value="getCurrentWallType.includes(data.item)"></v-checkbox>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>{{ data.item }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
      </form-select>
      <form-select label="Floor type" :items="floorTypeOptions"
        :value="getCurrentFloorType"
        @input="updateValue('floorFloorType', $event)"
        multiple
        chips>
        <template v-slot:prepend-item>
          <v-list-item ripple @click="toggle('floorFloorType')">
            <v-list-item-action>
              <v-checkbox :input-value="allFloorTypeSelected"></v-checkbox>
            </v-list-item-action>
            <v-list-item-title>Select All</v-list-item-title>
          </v-list-item>
          <v-divider class="mt-2"></v-divider>
        </template>
        <template v-slot:selection="data">
          <v-chip v-bind="data.attrs" :input-value="data.selected" close @click="data.select" @click:close="removeFloorType(data.item)">
            {{ data.item }}
          </v-chip>
        </template>
        <template v-slot:item="data">
          <v-list-item @click="toggleItem('floorFloorType', data.item)" ripple>
            <v-list-item-action>
              <v-checkbox :input-value="getCurrentFloorType.includes(data.item)"></v-checkbox>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>{{ data.item }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
      </form-select>
      <form-select label="Ceiling type" :items="ceilingTypeOptions"
        :value="getCurrentCeilingType"
        @input="updateValue('floorCeilingType', $event)"
        multiple
        chips>
        <template v-slot:prepend-item>
          <v-list-item ripple @click="toggle('floorCeilingType')">
            <v-list-item-action>
              <v-checkbox :input-value="allCeilingTypeSelected"></v-checkbox>
            </v-list-item-action>
            <v-list-item-title>Select All</v-list-item-title>
          </v-list-item>
          <v-divider class="mt-2"></v-divider>
        </template>
        <template v-slot:selection="data">
          <v-chip v-bind="data.attrs" :input-value="data.selected" close @click="data.select" @click:close="removeCeilingType(data.item)">
            {{ data.item }}
          </v-chip>
        </template>
        <template v-slot:item="data">
          <v-list-item @click="toggleItem('floorCeilingType', data.item)" ripple>
            <v-list-item-action>
              <v-checkbox :input-value="getCurrentCeilingType.includes(data.item)"></v-checkbox>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>{{ data.item }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
      </form-select>
      <div class="col-md-4 col-sm-6 col-12">
        <v-text-field 
          label="No of rooms"
          :value="getCurrentRooms"
          @input="updateValue('floorRooms', $event)"
          type="number"
          min="0"></v-text-field>
      </div>
      <div class="col-md-4 col-sm-6 col-12">
        <v-text-field 
          label="No of bathrooms"
          :value="getCurrentBathrooms"
          @input="updateValue('floorBathrooms', $event)"
          type="number"
          min="0"></v-text-field>
      </div>
      <div class="col-md-4 col-sm-6 col-12">
        <v-text-field 
          label="No of windows"
          :value="getCurrentWindows"
          @input="updateValue('floorWindows', $event)"
          type="number"
          min="0"></v-text-field>
      </div>
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
