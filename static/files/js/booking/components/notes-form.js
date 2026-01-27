Vue.component('notes-form', {
    props: ['floorIndex'],
    data() {
        return {
            fieldNameOptions: [
                'Wall Condition',
                'Floor Condition',
                'Ceiling Condition',
                'Special Request',
                'Additional Notes',
                'Other'
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
                                    v-model="$root.floorNoteFieldName[floorIndex]"
                                    :items="fieldNameOptions" 
                                    label="Field Name">
                                </v-select>
                            </div>

                            <div class="col-md-4">
                                <v-text-field 
                                    v-model="$root.floorNoteValue[floorIndex]"
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
            if (!this.$root.floorNoteFieldName[this.floorIndex] || !this.$root.floorNoteValue[this.floorIndex]) {
                alert('Please fill in all fields');
                return;
            }
            
            // Initialize notes array if doesn't exist
            if (!this.$root.floorNotes[this.floorIndex]) {
                this.$root.$set(this.$root.floorNotes, this.floorIndex, []);
            }
            
            // Add note to array
            this.$root.floorNotes[this.floorIndex].push({
                fieldName: this.$root.floorNoteFieldName[this.floorIndex],
                value: this.$root.floorNoteValue[this.floorIndex]
            });
            
            // Clear inputs
            this.$root.$set(this.$root.floorNoteFieldName, this.floorIndex, null);
            this.$root.$set(this.$root.floorNoteValue, this.floorIndex, null);
        }
    }
});
