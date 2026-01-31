Vue.component('notes-form', {
    props: ['floorIndex', 'buildingIndex', 'apartmentIndex'],
    data() {
        return {
            editingIndex: null,
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
                                    v-model="currentFieldName"
                                    :items="fieldNameOptions" 
                                    label="Field Name">
                                </v-select>
                            </div>

                            <div class="col-md-4">
                                <v-text-field 
                                    v-model="currentValue"
                                    label="Value">
                                </v-text-field>
                            </div>

                            <div class="col-md-2 d-flex align-items-center">
                                <v-btn color="primary" @click="addNote" class="px-5">
                                    {{ editingIndex !== null ? 'Update' : 'Add' }}
                                </v-btn>
                                <v-btn v-if="editingIndex !== null" text color="error" @click="cancelEdit" class="ml-2">
                                    Cancel
                                </v-btn>
                            </div>
                        </div>

                        <!-- Display Added Notes -->
                        <div v-if="notesList.length > 0" class="mt-4">
                            <h6 class="mb-3">Added Notes:</h6>
                            <v-simple-table>
                                <template v-slot:default>
                                    <thead>
                                        <tr>
                                            <th class="text-left">Field Name</th>
                                            <th class="text-left">Value</th>
                                            <th class="text-center">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(note, index) in notesList" :key="index">
                                            <td>{{ note.fieldName }}</td>
                                            <td>{{ note.value }}</td>
                                            <td class="text-center">
                                                <v-btn icon small color="primary" @click="editNote(index)" class="mr-2">
                                                    <v-icon small>mdi-pencil</v-icon>
                                                </v-btn>
                                                <v-btn icon small color="error" @click="removeNote(index)">
                                                    <v-icon small>mdi-delete</v-icon>
                                                </v-btn>
                                            </td>
                                        </tr>
                                    </tbody>
                                </template>
                            </v-simple-table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    computed: {
        notesList() {
            if (this.apartmentIndex) {
                // Apartment-specific notes
                if (!this.$root.floorNotes[this.buildingIndex] || 
                    !this.$root.floorNotes[this.buildingIndex][this.floorIndex] ||
                    !this.$root.floorNotes[this.buildingIndex][this.floorIndex][this.apartmentIndex]) {
                    return [];
                }
                return this.$root.floorNotes[this.buildingIndex][this.floorIndex][this.apartmentIndex];
            } else {
                // Floor-level notes
                if (!this.$root.floorNotes[this.buildingIndex] || !this.$root.floorNotes[this.buildingIndex][this.floorIndex]) {
                    return [];
                }
                return this.$root.floorNotes[this.buildingIndex][this.floorIndex];
            }
        },
        currentFieldName: {
            get() {
                if (this.apartmentIndex) {
                    return this.$root.floorNoteFieldName[this.buildingIndex]?.[this.floorIndex]?.[this.apartmentIndex];
                }
                return this.$root.floorNoteFieldName[this.buildingIndex]?.[this.floorIndex];
            },
            set(value) {
                if (this.apartmentIndex) {
                    this.ensureDataStructure('floorNoteFieldName');
                    this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex][this.floorIndex], this.apartmentIndex, value);
                } else {
                    this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex], this.floorIndex, value);
                }
            }
        },
        currentValue: {
            get() {
                if (this.apartmentIndex) {
                    return this.$root.floorNoteValue[this.buildingIndex]?.[this.floorIndex]?.[this.apartmentIndex];
                }
                return this.$root.floorNoteValue[this.buildingIndex]?.[this.floorIndex];
            },
            set(value) {
                if (this.apartmentIndex) {
                    this.ensureDataStructure('floorNoteValue');
                    this.$root.$set(this.$root.floorNoteValue[this.buildingIndex][this.floorIndex], this.apartmentIndex, value);
                } else {
                    this.$root.$set(this.$root.floorNoteValue[this.buildingIndex], this.floorIndex, value);
                }
            }
        }
    },
    methods: {
        ensureDataStructure(propName) {
            if (!this.$root[propName][this.buildingIndex]) {
                this.$root.$set(this.$root[propName], this.buildingIndex, {});
            }
            if (!this.$root[propName][this.buildingIndex][this.floorIndex]) {
                this.$root.$set(this.$root[propName][this.buildingIndex], this.floorIndex, {});
            }
        },
        addNote() {
            const fieldName = this.apartmentIndex 
                ? this.$root.floorNoteFieldName[this.buildingIndex]?.[this.floorIndex]?.[this.apartmentIndex]
                : this.$root.floorNoteFieldName[this.buildingIndex]?.[this.floorIndex];
            
            const value = this.apartmentIndex
                ? this.$root.floorNoteValue[this.buildingIndex]?.[this.floorIndex]?.[this.apartmentIndex]
                : this.$root.floorNoteValue[this.buildingIndex]?.[this.floorIndex];

            if (!fieldName || !value) {
                alert('Please fill in all fields');
                return;
            }

            // Initialize notes structure
            if (!this.$root.floorNotes[this.buildingIndex]) {
                this.$root.$set(this.$root.floorNotes, this.buildingIndex, {});
            }
            if (!this.$root.floorNotes[this.buildingIndex][this.floorIndex]) {
                this.$root.$set(this.$root.floorNotes[this.buildingIndex], this.floorIndex, this.apartmentIndex ? {} : []);
            }
            
            if (this.apartmentIndex) {
                // Apartment-specific notes
                if (!this.$root.floorNotes[this.buildingIndex][this.floorIndex][this.apartmentIndex]) {
                    this.$root.$set(this.$root.floorNotes[this.buildingIndex][this.floorIndex], this.apartmentIndex, []);
                }
                
                if (this.editingIndex !== null) {
                    // Update existing note
                    this.$root.$set(
                        this.$root.floorNotes[this.buildingIndex][this.floorIndex][this.apartmentIndex],
                        this.editingIndex,
                        { fieldName, value }
                    );
                    this.editingIndex = null;
                } else {
                    // Add new note
                    this.$root.floorNotes[this.buildingIndex][this.floorIndex][this.apartmentIndex].push({ fieldName, value });
                }
                
                // Clear inputs
                this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex][this.floorIndex], this.apartmentIndex, null);
                this.$root.$set(this.$root.floorNoteValue[this.buildingIndex][this.floorIndex], this.apartmentIndex, null);
            } else {
                // Floor-level notes
                if (this.editingIndex !== null) {
                    // Update existing note
                    this.$root.$set(
                        this.$root.floorNotes[this.buildingIndex][this.floorIndex],
                        this.editingIndex,
                        { fieldName, value }
                    );
                    this.editingIndex = null;
                } else {
                    // Add new note
                    this.$root.floorNotes[this.buildingIndex][this.floorIndex].push({ fieldName, value });
                }
                
                // Clear inputs
                this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex], this.floorIndex, null);
                this.$root.$set(this.$root.floorNoteValue[this.buildingIndex], this.floorIndex, null);
            }
        },
        editNote(index) {
            const note = this.notesList[index];
            if (this.apartmentIndex) {
                this.ensureDataStructure('floorNoteFieldName');
                this.ensureDataStructure('floorNoteValue');
                this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex][this.floorIndex], this.apartmentIndex, note.fieldName);
                this.$root.$set(this.$root.floorNoteValue[this.buildingIndex][this.floorIndex], this.apartmentIndex, note.value);
            } else {
                this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex], this.floorIndex, note.fieldName);
                this.$root.$set(this.$root.floorNoteValue[this.buildingIndex], this.floorIndex, note.value);
            }
            this.editingIndex = index;
        },
        cancelEdit() {
            this.editingIndex = null;
            if (this.apartmentIndex) {
                this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex][this.floorIndex], this.apartmentIndex, null);
                this.$root.$set(this.$root.floorNoteValue[this.buildingIndex][this.floorIndex], this.apartmentIndex, null);
            } else {
                this.$root.$set(this.$root.floorNoteFieldName[this.buildingIndex], this.floorIndex, null);
                this.$root.$set(this.$root.floorNoteValue[this.buildingIndex], this.floorIndex, null);
            }
        },
        removeNote(index) {
            if (this.apartmentIndex) {
                this.$root.floorNotes[this.buildingIndex][this.floorIndex][this.apartmentIndex].splice(index, 1);
            } else {
                this.$root.floorNotes[this.buildingIndex][this.floorIndex].splice(index, 1);
            }
        }
    }
});
