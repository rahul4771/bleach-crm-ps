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
      type: [String, Number, Array],
      default: null
    },
    multiple: {
      type: Boolean,
      default: false
    },
    chips: {
      type: Boolean,
      default: false
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
    <div class="col-md-4 col-sm-6 col-12">
      <v-select 
        v-model="internalValue"
        :label="label" 
        :items="items"
        :multiple="multiple"
        :chips="chips"
        :class="{'multi-select-field': multiple}"
        class="chips-overflow-hidden">
        <template v-slot:prepend-item>
          <slot name="prepend-item"></slot>
        </template>
        <template v-slot:selection="data">
          <slot name="selection" v-bind="data">
            <v-chip v-if="multiple" v-bind="data.attrs" :input-value="data.selected" close @click="data.select" small>
              {{ data.item }}
            </v-chip>
            <span v-else>{{ data.item }}</span>
          </slot>
        </template>
        <template v-slot:item="data">
          <slot name="item" v-bind="data">
            <v-list-item-content>
              <v-list-item-title>{{ data.item }}</v-list-item-title>
            </v-list-item-content>
          </slot>
        </template>
      </v-select>
    </div>
  `
});
