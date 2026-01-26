Vue.component('FormSelect', {
  props: {
    label: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      default: () => []
    },
    value: {
      type: [String, Number],
      default: null
    }
  },
  data() {
    return {
      internalValue: this.value
    }
  },
  watch: {
    internalValue(newVal) {
      this.$emit('input', newVal);
    },
    value(newVal) {
      this.internalValue = newVal;
    }
  },
  template: `
    <div class="col-md-4">
      <v-select 
        v-model="internalValue"
        :label="label" 
        :items="items">
      </v-select>
    </div>
  `
});
