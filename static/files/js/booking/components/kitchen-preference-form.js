Vue.component('kitchen-preference-form', {
    props: ['floorIndex'],
    template: `
        <div class="col-md-6">
            <div class="d-flex">
                <div style="margin-top: 16px; padding-top: 4px;">
                    Do you want to clean your Kitchen ? 
                    <span style="color:red">*</span>
                </div>
                <v-radio-group row v-model="$root.floorKitchenPreference[floorIndex]">
                    <v-radio :value="true" class="ml-2">
                        <template v-slot:label>
                            <div>
                                Yes<strong class="success--text"></strong>
                            </div>
                        </template>
                    </v-radio>
                    <v-radio :value="false">
                        <template v-slot:label>
                            <div>
                                No
                                <strong class="primary--text"></strong>
                            </div>
                        </template>
                    </v-radio>
                </v-radio-group>
            </div>
        </div>
    `
});
