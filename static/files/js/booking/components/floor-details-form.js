Vue.component('FloorDetailsForm', {
  props: {
    floorIndex: {
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
  template: `
    <div class="row">
      <form-select label="Size" :items="sizeOptions"></form-select>
      <form-select label="Wall type" :items="wallTypeOptions"></form-select>
      <form-select label="Floor type" :items="floorTypeOptions"></form-select>
      <form-select label="Ceiling type" :items="ceilingTypeOptions"></form-select>
      <form-select label="No of rooms" :items="roomOptions"></form-select>
      <form-select label="No of bathrooms" :items="bathroomOptions"></form-select>
      <form-select label="No of windows" :items="windowOptions"></form-select>
    </div>
  `
});
