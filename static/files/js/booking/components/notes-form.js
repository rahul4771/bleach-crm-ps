Vue.component('notes-form', {
    props: ['floorIndex', 'buildingIndex'],
    data() {
        return {
            fieldNameOptions: [
                'Bedrooms',
                'Bathrooms',
                'Maid Room', 
                'Storage Room', 
                'Living Room', 
                'Dressing Room', 
                'Cabinets (Inside)', 
                'Cabinets (Outside)', 
                'Driver Room', 
                'Laundry Room', 
                'Mechanical Room', 
                'Electrical Room', 
                'Entertainment Room', 
                'Dining Room', 
                'Entrance Area', 
                'Stair Case', 
                'Hand Wash Area', 
                'Windows', 
                'Wall Glass', 
                'Balcony', 
                'Swimming Pool', 
                'Façade', 
                'Dusting', 
                'Gates & Fence', 
                'Hall Way', 
                'AC Vents', 
                'Cove Lights', 
                'Switch Boards', 
                'Chandeliers', 
                'Wall Lights', 
                'Ceiling Lights', 
                'Door', 
                'Roof Top', 
                'Fence', 
                'Parking Area'
            ]
        }
    },
    template: `
        <div class="col-md-12">
            <div class="d-flex">
                <div class="row">
                    <div class="col-md-12">
                        <h5 class="pt-4">Add Notes</h5>
                        <div class="row g-4">
                            <div class="col-md-4">
                                <v-select 
                                    v-model="$root.floorNoteFieldName[buildingIndex][floorIndex]"
                                    :items="fieldNameOptions" 
                                    label="Field Name">
                                </v-select>
                            </div>

                            <div class="col-md-4">
                                <v-text-field 
                                    v-model="$root.floorNoteValue[buildingIndex][floorIndex]"
                                    label="Value">
                                </v-text-field>
                            </div>

                            <div class="text-center mt-4">
                                <button class="btn btn-primary px-5" @click="addNote">Add</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
        addNote() {
            if (!this.$root.floorNoteFieldName[this.buildingIndex][this.floorIndex] || !this.$root.floorNoteValue[this.buildingIndex][this.floorIndex]) {
                alert('Please fill in all fields');
                return;
            }

            // Initialize notes array if doesn't exist
            if (!this.$root.floorNotes[this.buildingIndex][this.floorIndex]) {
                this.$root.$set(this.$root.floorNotes[this.buildingIndex], this.floorIndex, []);
            }

            // Add note to array
            this.$root.floorNotes[this.buildingIndex][this.floorIndex].push({
                fieldName: this.$root.floorNoteFieldName[this.buildingIndex][this.floorIndex],
                value: this.$root.floorNoteValue[this.buildingIndex][this.floorIndex]
            });

            // Clear inputs
            this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex], this.floorIndex, null);
            this.$root.$set(this.$root.floorNoteValue[this.buildingIndex], this.floorIndex, null);
        }
    }
});
