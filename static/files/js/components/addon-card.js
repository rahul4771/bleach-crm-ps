Vue.component('addon-card', {
  props: {
    addon: null,
    index: null,
    addonMediaPath: String
  },
  template: `
      <div class="more-service-card">
        <div class="text-center">{{ addon.details.name }}</div>
        
        <div class="text-center mt-2">
          <img v-if="hasImagePath" :src="getAddonIconPath(addon.details.image_path)" class="service-icon" />
        </div>

        <div class="mt-2 text-center primary-text">
          <span v-if="hasSelectedSize"><b>{{ addon.selected_size.price + ' KD' }}</b></span>
          <span v-else><b>{{ addon.details.price + ' KD' }}</b></span>
        </div>

        <v-select v-if="addon.details.category"
                  dense
                  :items="addon.size"
                  item-text="size"
                  :value="addon.selected_size"
                  return-object
                  label="Size"
                  class="mt-2"
                  @input="onSizeChange"></v-select>

        <div class="text-center mb-2">
          <v-btn class="mt-4 mb-2" color="primary" small outlined @click="onSelect" v-if="!addon.selected">
            <v-icon left>mdi-cart</v-icon>
            Add
          </v-btn>

          <div v-else>
            <div class="d-flex justify-center mt-2">
              <div class="reduce-addon-qty" @click="onReduce">
                <i class="fas fa-minus-square primary-text"></i>
              </div>
              <div class="input-addon-qty">
                <input type="number" :min="0" class="input-addon" :value="addon.quantity" @input="onQtyChange($event.target.value)" />
              </div>
              <div class="add-addon-qty" @click="onIncrease">
                <i class="fas fa-plus-square primary-text"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    `,
  computed: {
    hasSelectedSize() {
      return this.addon && this.addon.selected_size && Object.keys(this.addon.selected_size || {}).length > 0;
    },
    hasImagePath() {
      return this.addon && this.addon.details && this.addon.details.image_path && this.addon.details.image_path.length > 0;
    }
  },
  methods: {
    getAddonIconPath(imagePath) {
      if (!imagePath) return '';
      return `http://127.0.0.1:8000${imagePath}`;
    },
    onSelect() { this.$emit('select', this.index); },
    onReduce() { this.$emit('reduce', this.index); },
    onIncrease() { this.$emit('increase', this.index); },
    onQtyChange(val) { const v = Number(val); this.$emit('update-quantity', { index: this.index, quantity: isNaN(v) ? 0 : v }); },
    onSizeChange(obj) { this.$emit('choose-size', { index: this.index, size: obj }); }
  }
});
