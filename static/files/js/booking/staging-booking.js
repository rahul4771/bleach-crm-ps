$(document).ready(function () {
});

function selectService(item, itempt) {
    // Remove active icon from all service cards
    $('#service-carousel').find('.sr-service-card').each(function () {
        $(this).find('.active-icon').removeClass('active-icon').addClass('inactive-icon').removeClass('fa-check-circle').addClass('fa-circle');
    });

    // Add active icon to clicked service card
    $(itempt).find('.inactive-icon').removeClass('inactive-icon').addClass('active-icon').removeClass('fa-circle').addClass('fa-check-circle');

    if (typeof app !== 'undefined') {
        app.selectService({ name: item })
    }
}

function selectServiceOnly(service) {
    if (typeof app !== 'undefined') {
        app.selectService({ name: service })
    }

    // Remove active icon from all service cards
    $('#service-carousel').find('.sr-service-card').each(function () {
        $(this).find('.active-icon').removeClass('active-icon').addClass('inactive-icon').removeClass('fa-check-circle').addClass('fa-circle');
    });
}

// Global component: AddonCarousel
Vue.component('addon-carousel', {
    template: `
        <div class="col-md-12 mt-2" v-if="addons.length > 0">
            <div class="more-services">
                <div class="service-content-heading">{{ heading }}</div>
                <div style="padding-left: 32px; padding-right: 32px;">
                    <div class="owl-carousel other-service-carousel" :id="carouselId">
                        <addon-card 
                            v-for="(addon, index) in addons" 
                            :key="index"
                            :addon="addon" 
                            :index="index"
                            @select="$emit('select', $event)"
                            @reduce="$emit('reduce', $event)"
                            @increase="$emit('increase', $event)"
                            @update-quantity="$emit('update-quantity', $event)"
                            @choose-size="$emit('choose-size', $event)">
                        </addon-card>
                    </div>
                </div>
            </div>
        </div>
    `,
    props: {
        addons: {
            type: Array,
            required: true,
            default: () => []
        },
        carouselId: {
            type: String,
            required: true
        },
        heading: {
            type: String,
            default: 'Add-ons'
        }
    },
    watch: {
        addons: {
            handler() {
                this.reinitializeCarousel();
            },
            deep: true
        }
    },
    mounted() {
        this.reinitializeCarousel();
    },
    methods: {
        reinitializeCarousel() {
            const self = this;
            setTimeout(() => {
                self.$nextTick(() => {
                    const selector = `#${self.carouselId}`;
                    const $carousel = $(selector);

                    if ($carousel.length === 0) return;

                    $carousel.css({ 'opacity': '0', 'transition': 'opacity 0.1s' });

                    if ($carousel.hasClass('owl-loaded')) {
                        $carousel.trigger('destroy.owl.carousel').removeClass('owl-loaded owl-drag owl-carousel');
                        $carousel.find('.owl-stage-outer, .owl-stage, .owl-item, .owl-nav, .owl-dots').remove();
                    }

                    const finalItemsCount = $carousel.children().length;

                    if (finalItemsCount > 0) {
                        $carousel.addClass('owl-carousel').owlCarousel({
                            items: 4,
                            loop: false,
                            margin: 10,
                            nav: true,
                            dots: false,
                            responsive: {
                                0: { items: 1 },
                                600: { items: 2 },
                                1000: { items: 4 }
                            }
                        });

                        setTimeout(() => {
                            $carousel.css('opacity', '1');
                        }, 50);
                    }
                });
            }, 150);
        }
    }
});

const app = new Vue({
    el: '#app',
    delimiters: ['<%', '%>'],
    vuetify: new Vuetify({
        theme: {
            themes: {
                light: {
                    primary: '#2e4e85', // #E53935
                    secondary: '#FFCDD2', // #FFCDD2
                    accent: '#3F51B5', // #3F51B5
                },
            },
        }
    }),
    components: {

    },
    data: {
        hourly_options: [{
            text: '1 - 2 Hours',
            value: 2
        },
        {
            text: '3 - 4 Hours',
            value: 4
        }
        ],
        is_hourly: false,
        currentSlotDay: 1,
        cleaning_set: [],
        max_cleaners: [],
        min_cleaners: [],
        max_hours: [],
        min_hours: [],
        out_of_shift: false,
        kitchen_max_cleaners: null,
        new_kitchen_cabinet_productivity: null,
        old_kitchen_cabinet_productivity: null,
        new_kitchen_nocabinet_productivity: null,
        old_kitchen_nocabinet_productivity: null,
        absolute_cost: 0,
        added_cost: 0,
        addon_size: [],
        add_new_kitchen: true,
        addons_parsed: [],
        submit_loader: false,
        billingDataIndex: null,
        slot_msg: false,
        keynote_content: [
            'BEDROOMS', 'BATHROOMS', 'MAID ROOM', 'STORAGE ROOM', 'LIVING ROOM', 'DRESSING ROOM', 'CABINETS (Inside)', 'CABINETS (Outside)', 'DRIVER ROOM', 'LAUNDRY ROOM', 'MECHANICAL ROOM', 'ELECTRICAL ROOM', 'ENTERTAINMENT ROOM', 'DINING ROOM', 'ENTRANCE AREA', 'STAIR CASE', 'HAND WASH AREA', 'WINDOWS', 'WALL GLASS', 'BALCONY', 'SWIMMING POOL', 'FAÇADE', 'DUSTING', 'GATES & FENCE', 'HALL WAY', 'AC VENTS', 'COVE LIGHTS', 'SWITCH BOARDS', 'CHANDELIERS', 'WALL LIGHTS', 'CEILING LIGHTS', 'DOOR', 'ROOF TOP', 'FENCE', 'PARKING AREA'
        ],
        customDateSelected: [],
        customDialog: false,
        cleaningPolicy: '',
        altweekStat: false,
        subStat: '',
        altdaysStat: false,
        currentPageTitle: 'Booking',
        custBookStat: false,
        scheduleStat: true,
        serviceChange: true,
        cat_counter: 0,
        ser_counter: 0,
        bookingMultiData: {},
        serviceImages: new FormData(),
        activePayment: 'debit',
        imageUrl: '',
        images: [],
        contact_platform: [],
        serviceDetails: {
            total_cost: 0,
            estimated_cost: 0,
            service_details: {},
            shift_availability_check: true

        },
        tempCost: 0,
        scale: 80,
        quality: 80,
        area_type: '',
        location_type: '',
        evaluator_note: '',
        multiServicesBill: [],
        refresh: 0,
        floorCompleted: false,
        detailedCleaningServices: [],
        specialCareServices: [],
        buildingCount: 1,
        kitchenCleaningServices: [],
        infectionControlServices: [],
        valid: [],
        validApartment: true,
        validKitchen: true,
        validKitchenDialog: true,

        validOtherService: true,
        validOtherServiceDialog: true,
        hallway_check: false,
        window_check: false,
        scheduleGroup: {},

        selectedCategory: '',
        name: '',
        rules: {
            required: v => !!v || 'this field is required',
        },
        // url:'',
        // url:'https://my.bleachkw.com',
        url: 'http://127.0.0.1:8000',
        slot_loader: false,
        lastLoadedServiceType: '',  // Track last loaded service to prevent duplicate addon calls
        kitchenData: {
            wall_type: '',
            floor_type: '',
            size: null,
            ceiling_type: '',
            condition: '',
            type: 'old',
            residue: false,
            is_cabinet: false
        },
        mob_number: "",
        customerDetails: {},
        selectedAddress: {},
        today: "",
        otpStat: false,
        verifyStat: false,
        errorStat: false,
        errorVerifyStat: false,
        verificationStat: false,
        mob_otp: "",
        activeTab: "Services",
        selectedService: {
            name: 'General Cleaning'
        },
        serviceSize: {},
        cartItems: [],
        selectedSlot: [],
        categories: [],
        area_types: [],
        location_types: [
            "Post Construction",
            "Post Renovation",
            "Fully Furnished",
            "Empty Area",
        ],
        mediaUrl: '',
        services: [],
        buildingsCompleted: false,
        date: null,
        menu: false,
        ImageDetails: {
            url: "",
            file: "",
            service: ""
        },
        dateSelected: "",
        userStat: true,
        images: [],
        duration: [],
        totalCost: 0,
        billingData: [],
        dialogStat: "",
        sizeData: [],
        currentItem: null,
        service: "test",
        dialog: false,
        dialogmsg: "",
        otherServices: [],
        otherService: {
            material: "",

            color: "",
            size: null,
            keynote_data: [],
            type: "",
            age: "",
            stain: false,
            stain_reason: "",
            wall_type: "",
            floor_type: "",
            ceiling_type: "",
            residue: false,
            hallway_size: "",
            sides: "",
            stain_age: "",
            height: "",
            is_cabinet: false,
            addons: [],
            section_net_cost: null,
            section_cost: null
        },
        color: ["Blue", "Yellow", "Orange", "Red", "Black", "White"],
        material: ["Material 1", "Material 2", "Material 3", "Material 4"],
        upholsteryType: ["SOFA", "CURTAIN"],
        upholsterySize1: ["Small", "Medium", "Large", "Xtra Large"],
        upholsterySize2: ["Small", "Medium", "Large"],
        upholsterySize3: ["Small", "Medium", "Large"],
        tab: "tab1",
        serviceType: "",
        serviceTypes: [],
        apartment: [],
        no_of_apartments: [],

        e: {
            building: [],
        },
        no_of_building: 0,
        temp_no_of_building: 0,
        building: [],
        no_of_floors: [],
        buildings: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", '11', "12", "13", "14", "15"],
        serviceSection: {
            service_type: "",
            area_type: "",
            location_type: "",
            sections: {},
        },
        area_types: [],


        location_types: [
            "Post Construction",
            "Post Renovation",
            "Fully Furnished",
            "Empty Area",
        ],
        location_types2: [
            "Fully Furnished",
            "Empty Area"
        ],
        splitData: ["8"],
        selectedDuration: {},
        size: ["SMALL", "MEDIUM", "LARGE"],
        cause_of_stain: ['INK MARK', 'HARD DUST', 'COFFEE & TEA SPILL', 'OIL',
            'GREASE', 'PAINT', 'URINE', 'MILK SPILL', 'NO STAIN', 'OTHERS'],
        walltypes: ["BRICKS", "GLASS", "CONCRETE", "CERAMIC", "GYPSUM", "FABRIC", "RUBBER", "STONE", "TERRAZO", "STAINLESS", "VINYL", "WOODEN", "OTHERS"],
        ceilingtypes: ["WOODEN", "GLASS", "CONCRETE", "CERAMIC", "GYPSUM", "FOAM", "PLASTIC", "FABRIC", "RUBBER", "STAINLESS", "VENYL", "OTHERS"],
        floortypes: ["MARBLE", "GLASS", "STONE", "CERAMIC", "CONCRETE", "BRICKS", "WOODEN", "TERRAZO", "OTHERS"],
        materials: ["POLYESTER", "NATURAL FIBER", "SYNTHETIC", "LEATHER", "OLEFIN", "POLYPROPYLENE", "NYLON"],
        colors: ["GREEN", "SILVER", "VIOLET", "WHITE", "BLACK", "BEIGE", "BLUE", "GREY", "RED", "CREAM", "MULTI", "OFF WHITE", "MEROON", "ORANGE", "PINK", "GOLD", "BROWN", "YELLOW", "ROYAL BLUE", "LILAC", "OTHERS"],

        imageData: [],
        dob: '',
        serviceData: {
            service_details: {
                service_type: "",
                location_type: "",
                area_type: "",
                evaluator_note: "",
                estimated_cost: 0,
                total_cost: 0,
                number_of_cleaners: 0,
                cleaning_hours: 0,
            },
            sections: {},
            customer_id: "",
            customer_details: {
                name: "",
                gender: "",
                email: "",
                mobile_number: "",
                dob: "",
                date_day: "",
                date_month: "",
                date_year: "",
                nationality: "",
                sms_preference: "",
                contact_platform: [],
            },
            address_id: "",
            address_details: {
                governorate: "",
                area: "",
                block: "",
                avenue: "",
                building: "",
                street: "",
                floor: "",
                apartment: "",
            },
        },
        sections: {
            section_name: "",
            size: "",
            wall_type: "",
            ceiling_type: "",
            cement_residue: false,
            section_cost: "",
            section_net_cost: "",
            keynotes: {},
        },
        upholsterySize: [],
        total_size: 0,
        slotDate: "",
        timeSlots: {},
        renderComponent: true,
        time_slot: {},
        slotCounter: 0,
        sizeFilteredData: [],
        kitchendialog: false,
        kitchenType: '',
        currentBuilding: '',
        currentFloor: '',
        currentKitchen: '',
        kitchendialogStat: false,
        kitchenSize: {},
        kitchenSizeData: [],
        facadeSize: [],
        windowSize: [],
        ropeAccessSize: [],
        durationData: {},
        billSample: {
            name: '',
            section: {},
            section_name: '',
            serviceNo: 1,
        },
        totalmanhour: 0,
        maxCleaners: [],
        n: 0,
        serviceCount: 1,
        errMsg: '',

        kitchen_size: 0,
        sofa_size: 0,
        chair_size: 0,
        caret_size: 0,

        new_kitchen_cabinet_size: 0,
        old_kitchen_cabinet_size: 0,
        new_kitchen_nocabinet_size: 0,
        old_kitchen_nocabinet_size: 0,
        high_facade: 0,
        low_facade: 0,
        serviceTypesData: [],
        gateway_eval: '',
        gateway_price: 0,
        cust_governorates: [],
        cust_areas: [],
        udf3: '',
        multiServiceImages: [],
        phase2Result: {},
        ip_address: '',
        prefDay: [],
        scheduleDialog: false,
        scheduleDate: '',
        double_slots: [],
        slotStat: {
            available_slotes: [],
            busy_slotes: []
        },
        selected_double_slots: [],
        visits: [],
        visitDateTime: [],
        no_of_visits: null,
        monthly_starting_date: '',
        menu2: false,
        monthlyDialog: false,
        week1: ['01', '02', '03', '04', '05', '06', '07'],
        week2: ['08', '09', '10', '11', '12', '13', '14'],
        week3: ['15', '16', '17', '18', '19', '20', '21'],
        week4: ['22', '23', '24', '25', '26', '27', '28'],
        week5: ['29', '30', '31'],
        autofixStat: false,
        selected_monthly_date: [],
        reselectDialog: false,
        reselectSlot: [],
        reselectDate: {},
        reselectDateIndex: null,
        scheduleFormat: {
            allSchedule: {},
            individual: {}
        },

        schedule_serviceTypes: [],
        schedule_serviceTypes_selected: [],
        slotFormat: {
            "1": {
                start_time: '12:00 AM',
                end_time: '02:00 AM'
            },
            "2": {
                start_time: '02:00 AM',
                end_time: '04:00 AM'
            },
            "3": {
                start_time: '04:00 AM',
                end_time: '06:00 AM'
            },
            "4": {
                start_time: '06:00 AM',
                end_time: '08:00 AM'
            },
            "5": {
                start_time: '08:00 AM',
                end_time: '10:00 AM'
            },
            "6": {
                start_time: '10:00 AM',
                end_time: '12:00 PM'
            },
            "7": {
                start_time: '12:00 PM',
                end_time: '02:00 PM'
            },
            "8": {
                start_time: '02:00 PM',
                end_time: '04:00 PM'
            },
            "9": {
                start_time: '04:00 PM',
                end_time: '06:00 PM'
            },
            "10": {
                start_time: '06:00 PM',
                end_time: '08:00 PM'
            },
            "11": {
                start_time: '08:00 PM',
                end_time: '10:00 PM'
            },
            "12": {
                start_time: '10:00 PM',
                end_time: '12:00 AM'
            }
        },
        fixedSlots: {},
        keynote_list: [],
        keynote_data: {
            name: '',
            value: ''
        },
        keynote_name: '',
        keynote_value: '',
        keynote_err_msg: false,
        scheduleDateSat: false,
        confirmation_dialog: false,
        schedule_err_msg: false,
        onetime_dialog: false,
        oneTimeDateSelected: '',
        one_time_slots: {},
        onetimerender: true,
        selected_onetime_slots: {},
        oneTimeSelectionStat: false,
        onetime_scheduled: {},
        togetherStat: false,
        del_confirmation_dialog: false,
        service_index: null,
        editScheduleData: {},
        editScheduleStat: false,
        reconfirmation_dialog: false,
        userid: '',
        snackbar: false,
        responseText: '',
        parsedTimeSlots: [],
        scheduleStatus: false,
        floor_msg: false,
        apartment_stat_err: false,
        building_msg: false,
        others_keynotes: [],
        reset_building: false,
        reset_floor: false,
        building_warning: false,
        available_slotes: [],
        date_group: {},
        addons: [],
        last_image_stat: false,
        hourly_cleaning: {
            duration: null,
            hourly_duration: null,
            cleaners: null
        },
        hourly_slots: true,
        current_service: '',
        ropeAccessTypes: '',
        kitchenTypes: '',
        kitchenSize: '',


    },
    computed: {
        filteredServices() {
            // Find the selected category ID
            const selectedCat = this.categories.find(cat => cat.service_name === this.selectedCategory);
            if (!selectedCat) {
                return [];
            }
            // Filter services by the selected category ID
            return this.services.filter(service => service.service_group_id === selectedCat.id);
        }
    },
    watch: {
        filteredServices() {
            // Reinitialize service carousel when services change
            this.reinitServiceCarousel();
        },
        categories() {
            // Reinitialize category carousel when categories change
            this.reinitCategoryCarousel();
        },
        // addons_parsed watcher - addon-carousel component handles re-initialization automatically
        serviceType(newVal) {
            // Whenever the selected service type changes, fetch associated addons
            // Only call if the service type is different from the last loaded one (prevents duplicate calls)
            if (newVal && newVal !== this.lastLoadedServiceType) {
                this.lastLoadedServiceType = newVal;  // Update the last loaded service
                this.getAddons();
                // addon-carousel component will automatically re-initialize when addons_parsed updates
            }
        }
    },
    methods: {


        /* ================================================================
            METHODS ORGANIZATION INDEX
            ================================================================
            
            This file contains 150+ methods organized into 17 major categories.
            Use Ctrl+F to search for section markers below.

            1. UTILITY & VALIDATION METHODS (Line ~625)
            2. PRICING & COST CALCULATION (Line ~650)
            3. BUILDING/PROPERTY MANAGEMENT (Line ~760)
            4. SERVICE SELECTION & CONFIGURATION (Line ~3120)
            5. KITCHEN MANAGEMENT (Line ~2254-2510)
            6. SLOT MANAGEMENT (Line ~2661-2895)
            7. SCHEDULING & VISIT MANAGEMENT (Line ~1050-1900)
            8. SCHEDULE UI & DATE HANDLING (Line ~800-1050)
            9. CHECKOUT & CART MANAGEMENT (Line ~4500-5200)
            10. BOOKING & PAYMENT (Line ~3460-3700)
            11. IMAGE MANAGEMENT (Line ~3970-4100)
            12. API/SERVER CALLS (Line ~1750-1850)
            13. OTHER SERVICES & ADD-ONS (Line ~3340-4080)
            14. KEYNOTES & ANNOTATIONS (Line ~950-1000)
            15. TAB NAVIGATION (Line ~4420-4500)
            16. DURATION & HOUR CALCULATIONS (Line ~4730-6050)
            17. CUSTOMER DETAILS & OTP (Line ~2600-2660)

         ================================================================= */

        /* ================================================================
            1. UTILITY & VALIDATION METHODS
            ================================================================ */

        /**
         * Check if all slots have been selected
         * @returns {boolean} True if current slot day exceeds cleaning set length
         */
        isSlotsSelected() {
            return this.currentSlotDay > this.cleaning_set.length;
        },

        /**
         * Get visit number based on index
         * @param {number} index - Index of the visit
         * @returns {number} Visit number (1-indexed)
         */
        getVisitNumber(index) {
            return index + 1;
        },

        /**
         * Check if a datetime is in available slots
         * @param {string} dateTime - DateTime string
         * @returns {boolean} True if datetime is available
         */
        isDateTimeAvailable(dateTime) {
            return this.slotStat &&
                Array.isArray(this.slotStat.available_slotes) &&
                this.slotStat.available_slotes.includes(dateTime);
        },

        /**
         * Get the number of required slots for the current day
         * @returns {number} Number of slots required based on hours
         */
        getRequiredSlots() {
            if (!this.cleaning_set || this.currentSlotDay < 1) {
                return 0;
            }
            const hours = this.cleaning_set[this.currentSlotDay - 1]?.[0] || 0;
            return Math.ceil(hours / 2);
        },

        /* ================================================================
            2. PRICING & COST CALCULATION METHODS
            ================================================================
            Methods for calculating costs, pricing, and totals
        ================================================================ */

        /**
         * Calculate total cost of selected add-ons
         * @returns {number} Total add-on cost
         */
        findAddonCost() {
            let addonCost = 0;
            for (const addon of this.addons_parsed) {
                if (addon.selected) {
                    const price = addon.details.category ? addon.selected_size.price : addon.details.price;
                    addonCost += price * addon.quantity;
                }
            }
            return addonCost;
        },
        /**
         * Calculate absolute cost including service and add-ons
         * @returns {number} Total absolute cost
         */
        findAbsoluteCost() {
            let addonCost = 0;
            for (const addon of this.addons_parsed) {
                if (addon.selected) {
                    const price = addon.details.category ? addon.selected_size.price : addon.details.price;
                    addonCost += (price || 0) * addon.quantity;
                }
            }

            let totalCost = (this.otherService.size?.cost || 0) + addonCost;
            if (this.edit_item) {
                totalCost -= this.billingData[this.currentItem].section_cost;
            }
            return totalCost || 0;
        },
        /**
         * Wrapper method to calculate total booking amount
         * @returns {number} Total amount for the booking
         */
        calculateTotalAmount() {
            return this.findFullAmount();
        },
        /**
         * Close the edit dialog and reset other service data
         */
        closeEditDialog() {
            this.edit_item = false;
            this.otherService = {
                material: '',
                addons: [],
                color: '',
                size: null,
                type: '',
                age: '',
                stain: false,
                stain_reason: '',
                wall_type: '',
                floor_type: '',
                ceiling_type: '',
                residue: false,
                is_cabinet: false,
                hallway_size: '',
                sides: '',
                stain_age: '',
                height: '',
                keynote_data: [],
                section_cost: 0,
                sectiononly_cost: 0
            };
            this.dialog = false;
        },
        /**
         * Calculate total cost from all billing data items
         * @returns {number} Total cost of added items
         */
        findAddedCost() {
            let totalCost = 0;
            for (const item of this.billingData) {
                totalCost += item.section_cost;
            }
            return totalCost || 0;
        },
        /**
         * Check if hourly cleaning service is NOT included
         * @returns {boolean} True if no hourly cleaning service found
         */
        checkHourly() {
            return !this.multiServicesBill.some(service => service.service === 'Hourly Cleaning');
        },
        /**
         * Calculate total amount including service multiplier for subscriptions
         * @returns {number} Full amount including schedule multiplier for subscriptions
         */
        findFullAmount() {
            let fullAmount = 0;

            for (const service of this.multiServicesBill) {
                // Calculate total section cost for this service
                const sectionCost = service.bill?.reduce((sum, item) => sum + (item.section_cost || 0), 0) || 0;

                if (service.cleaning_policy === 'SUBSCRIPTION' && service.schedule_details) {
                    // Multiply by schedule count for subscription services
                    const scheduleCount = Object.keys(service.schedule_details).length;
                    fullAmount += scheduleCount > 0 ? sectionCost * scheduleCount : sectionCost;
                } else {
                    fullAmount += sectionCost;
                }
            }

            return fullAmount;
        },

        /* ================================================================
            3. BUILDING/PROPERTY MANAGEMENT METHODS
            ================================================================
            Hierarchical property structure: Building → Floor → Apartment
        ================================================================ */

        /**
         * Reset all building and floor data structures
         * Reinitializes arrays for buildings, floors, and validation
         */
        resetAllData() {
            this.reset_building = false;
            this.building_warning = false;
            this.no_of_building = this.temp_no_of_building;
            this.valid = [];
            this.building = [];
            this.e.building = [];
            this.no_of_floors = [];
            this.reset_floor = false;

            // Initialize building structures for each building
            for (let i = 0; i < this.no_of_building; i++) {
                this.building.push({
                    floors: [],
                    completed: false
                });
                this.e.building.push({
                    floors: [],
                    e: 1
                });
                this.no_of_floors.push('');
                this.valid.push({ floors: [] });
            }

            this.reset_floor = true;
            this.reset_building = true;
        },
        /**
         * Cancel building reset and close warning dialog
         */
        cancelResetData() {
            this.temp_no_of_building = this.no_of_building;
            this.building_warning = false;
        },
        /**
         * Open schedule editor for a specific service
         * @param {Object} service - The service to edit
         * @param {number} index - The service index
         */
        viewEditSchedule(service, index) {
            this.schedule_serviceTypes_selected = [];
            this.editScheduleData = service;
            this.editScheduleStat = true;
            this.schedule_serviceTypes_selected.push(index);
            this.goToSchedule();
        },
        /**
         * Open confirmation dialog before removing service
         * @param {number} index - The service index to delete
         */
        openDelConfirm(index) {
            this.service_index = index;
            this.del_confirmation_dialog = true;
        },
        /**
         * Remove service from bill and reset schedule selection
         */
        removeService() {
            this.multiServicesBill.splice(this.service_index, 1);
            this.del_confirmation_dialog = false;
            this.checkIsHourly();
            this.schedule_serviceTypes_selected = [];
        },

        /* ================================================================
            4. SCHEDULE & DATE HANDLING METHODS
            ================================================================
            One-time bookings, scheduling logic, date/time management
        ================================================================ */

        /**
         * Handle date selection change for one-time bookings
         * Fetches available slots for the selected date
         */
        oneTimeDateChange() {
            if (!this.one_time_slots[this.oneTimeDateSelected]) {
                this.one_time_slots[this.oneTimeDateSelected] = { slots: [] };
            }

            const [yr, mt, dy] = this.oneTimeDateSelected.split('-');
            this.slotDate = `${dy}-${mt}-${yr}`;
            this.getMultipleSlots();
        },
        /**
         * Reset and handle new date selection for one-time bookings
         * Clears previous slot selections and fetches slots for new date
         */
        oneTimeNewDateChange() {

            this.one_time_slots = {};
            this.one_time_slots[this.oneTimeDateSelected] = { slots: [] };

            const [yr, mt, dy] = this.oneTimeDateSelected.split('-');
            this.slotDate = `${dy}-${mt}-${yr}`;
            this.getMultipleSlots();
        },
        /**
         * Clear all service schedules and reset scheduler
         * Used when reconfirming scheduling for all services
         */
        reconfirmScheduler() {
            this.reconfirmation_dialog = false;
            for (const service of this.multiServicesBill) {
                service.schedule_details = {};
            }
            this.resetScheduler();
        },
        /**
         * Schedule services together
         * Handles subscription vs one-time scheduling and reconfirmation
         */
        scheduleTogether() {
            if (this.current_service == 'Hourly Cleaning') {
                this.cleaningPolicy = 'Subscription'
            }
            if (this.checkScheduleAvail()) {
                this.reconfirmation_dialog = true
            }
            else {
                this.goToSchedule()
            }
        },
        /**
         * Check if any service has schedule details configured
         * @returns {boolean} True if at least one service has schedule details
         */
        checkScheduleAvail() {
            return this.multiServicesBill.some(service => Object.keys(service.schedule_details).length > 0);
        },
        /**
         * Check if a slot index is within out-of-shift time window
         * @param {number} index - The slot index to check
         * @returns {boolean} True if out-of-shift or within specific time window (4-10)
         */
        outofshiftCheck(index) {
            return this.out_of_shift || (index > 3 && index < 11);
        },
        /**
         * Clear out-of-shift slot selections
         * Removes out-of-shift slots (1-3 and 12) from selected double slots
         */
        clearOutOfShift() {
            if (!this.out_of_shift) {
                // Remove early morning slots (1-3)
                for (let i = 0; i <= 2; i++) {
                    const slotNumber = i + 1;
                    const index = this.selected_double_slots.indexOf(slotNumber);
                    if (index > -1) {
                        this.selected_double_slots.splice(index, 1);
                    }
                }

                // Remove late night slot (12)
                const nightIndex = this.selected_double_slots.indexOf(12);
                if (nightIndex > -1) {
                    this.selected_double_slots.splice(nightIndex, 1);
                }
            }
        },
        resetScheduler() {
            this.hourly_cleaning = {
                cleaners: '',
                duration: '',
                hourly_duration: ''
            }
            this.currentSlotDay = 1
            this.out_of_shift = false
            this.cleaningPolicy = ''
            this.subStat = ''
            this.visits = []
            this.fixedSlots = {}
            this.altdaysStat = false
            this.altweekStat = false
            this.selected_double_slots = []
            this.selected_monthly_date = []
            this.autofixStat = false
            this.selected_monthly_date = []
            this.reselectDialog = false
            this.reselectSlot = []
            this.reselectDate = {}
            this.reselectDateIndex = null

            // this.one_time_slots={},
            if (this.cleaning_set.length > 0) {
                this.selectedDuration = {
                    cleaners: this.cleaning_set[0][1],
                    hours: this.cleaning_set[0][0],
                    slots: (this.cleaning_set[0][0]) / 2
                }
            }
            this.scheduleFormat = {
                allSchedule: {},
                individual: {}
            },
                this.no_of_visits = '',
                this.scheduleDateSat = false
            this.confirmation_dialog = false
            this.monthly_starting_date = ''
            this.customDateSelected = []
            this.schedule_err_msg = false
            if (this.editScheduleStat) {
                this.editScheduleStat = false
                this.editScheduleData.schedule_details = {}
            }
            else {
                this.editScheduleData = {}
            }
            this.oneTimeDateSelected = moment().format().split("T")[0];
            this.one_time_slots[this.oneTimeDateSelected] = {
                slots: []
            }
            this.selected_onetime_slots = {}

        },

        /* ================================================================
            5. KEYNOTES & ANNOTATIONS METHODS
            ================================================================
            Custom notes and annotations for properties and services
        ================================================================ */

        /**
         * Add a keynote to a floor in a building
         * @param {number} building - Building index
         * @param {number} floor - Floor index
         */
        addKeynote(building, floor) {
            // Get the form ref (may be array in v-for)
            let formRef = this.$refs[`keynoteForm-${building}-${floor}`];
            if (Array.isArray(formRef)) formRef = formRef[0];

            // Validate the form before adding
            if (formRef && formRef.validate()) {
                this.building[building].floors[floor].keynote_data.push({
                    name: this.keynote_name,
                    value: this.keynote_value
                });
                this.keynote_name = '';
                this.keynote_value = '';
                // Reset form validation
                this.$nextTick(() => {
                    formRef.resetValidation();
                });
            }
        },
        /**
         * Add a keynote to other services
         */
        addOthersKeynote() {
            // Get the form ref (may be array)
            let formRef = this.$refs.keynoteOthersForm;
            if (Array.isArray(formRef)) formRef = formRef[0];

            // Validate the form before adding
            if (formRef && formRef.validate()) {
                this.otherService.keynote_data.push({
                    name: this.keynote_name,
                    value: this.keynote_value
                });
                this.keynote_name = '';
                this.keynote_value = '';
                // Reset form validation
                this.$nextTick(() => {
                    formRef.resetValidation();
                });
            }
        },
        /**
         * Remove a keynote from other services
         * @param {number} keynote - Keynote index to remove
         */
        removeOthersKeynote(keynote) {
            this.otherService.keynote_data.splice(keynote, 1);
        },
        /**
         * Remove a keynote from a floor
         * @param {number} building - Building index
         * @param {number} floor - Floor index
         * @param {number} keynote - Keynote index to remove
         */
        removeKeynote(building, floor, keynote) {
            this.building[building].floors[floor].keynote_data.splice(keynote, 1);
        },
        /**
         * Add a keynote to a specific apartment
         * @param {number} building - Building index
         * @param {number} floor - Floor index
         * @param {number} apartment - Apartment index
         */
        addApartmentKeynote(building, floor, apartment) {
            // Get the form ref (may be array in v-for)
            let formRef = this.$refs[`keynoteApartmentForm-${building}-${floor}-${apartment}`];
            if (Array.isArray(formRef)) formRef = formRef[0];

            // Validate the form before adding
            if (formRef && formRef.validate()) {
                this.building[building].floors[floor].apartments[apartment].keynote_data.push({
                    name: this.keynote_name,
                    value: this.keynote_value
                });
                this.keynote_name = '';
                this.keynote_value = '';
                // Reset form validation
                this.$nextTick(() => {
                    formRef.resetValidation();
                });
            }
        },
        /**
         * Remove a keynote from an apartment
         * @param {number} building - Building index
         * @param {number} floor - Floor index
         * @param {number} apartment - Apartment index
         * @param {number} keynote - Keynote index to remove
         */
        removeApartmentKeynote(building, floor, apartment, keynote) {
            if (this.building[building] && this.building[building].floors[floor] && this.building[building].floors[floor].apartments[apartment] && this.building[building].floors[floor].apartments[apartment].keynote_data) {
                this.building[building].floors[floor].apartments[apartment].keynote_data.splice(keynote, 1);
            }
        },
        /**
         * Calculate and populate service types for selected services
         * Maps selected indices to their service names
         */
        calcSelectedServices() {
            this.schedule_serviceTypes = this.schedule_serviceTypes_selected.map(
                index => this.multiServicesBill[index].service
            );
        },
        /**
         * Check if any selected service includes kitchen cleaning
         * @returns {boolean} True if kitchen cleaning is included
         */
        checkKitchen() {
            return this.schedule_serviceTypes_selected.some(index => {
                const bills = this.multiServicesBill[index]?.bill || [];
                return bills.some(bill => bill.section?.kitchen);
            });
        },
        addScheduledService(service, index) {
            this.schedule_serviceTypes_selected[index] = {
                service: service
            }
        },
        addOneTimeToSchedule() {

            if (this.scheduleStat) {
                this.scheduleStatus = true
            }
            else {
                this.scheduleStatus = false
            }

            for (let j = 0; j < this.schedule_serviceTypes_selected.length; j++) {
                this.onetime_scheduled[this.schedule_serviceTypes_selected[j]] = {
                    slot: this.selected_onetime_slots
                }
            }

            for (let j = 0; j < this.schedule_serviceTypes_selected.length; j++) {
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaning_policy = 'ONE TIME SERVICE'
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details = {}
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaners = this.selectedDuration.cleaners

                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].shift_availability_check = !this.out_of_shift
                if (Object.keys(this.selected_onetime_slots).length > 1) {
                    this.findContDate()
                    let count = 0
                    for (const i in this.date_group) {
                        let cleaning_hr = 0
                        let dates = this.date_group[i]
                        if (dates.length > 0) {
                            let min = dates[0]
                            cleaning_hr = this.selected_onetime_slots[dates[0]].slots.length * 2
                            for (let m = 1; m < dates.length; m++) {
                                if (moment(dates[m], 'YYYY-MM-DD').isBefore(moment(min, 'YYYY-MM-DD'))) {

                                    min = dates[m]
                                }

                                cleaning_hr = cleaning_hr + (this.selected_onetime_slots[dates[m]].slots.length * 2)
                            }

                            /** add to schedule details */
                            let yr = min.split('-')[0]
                            let month = min.split('-')[1]
                            let day = min.split('-')[2]
                            let date = day + '-' + month + '-' + yr
                            let min_slot = Math.min(...this.selected_onetime_slots[min].slots)
                            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[count + 1] = {

                                "date": date,
                                "time": this.slotFormat[parseInt(min_slot)].start_time,
                                "no_of_cleaners": this.selectedDuration.cleaners,
                                "cleaning_hours": cleaning_hr,
                                "hourly_cleaning_duration": null
                            }

                            count = count + 1
                        }
                    }
                }
                else {

                    let count = 0
                    for (const k in this.selected_onetime_slots) {

                        const yr = k.split('-')[0]
                        const month = k.split('-')[1]
                        const day = k.split('-')[2]
                        const date = day + '-' + month + '-' + yr
                        const min_slot = Math.min(...this.selected_onetime_slots[k].slots)
                        this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[count + 1] = {

                            "date": date,
                            "time": this.slotFormat[parseInt(min_slot)].start_time,
                            "no_of_cleaners": this.selectedDuration.cleaners,
                            "cleaning_hours": this.selected_onetime_slots[k].slots.length * 2,
                            "hourly_cleaning_duration": null
                        }

                        count = count + 1
                    }
                }

                //Find continous dates
                //   var removedDates=[]
                //   var contDates=[]

                //   for(var m in this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details){
                //   if (Object.keys(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details).length>1 && Object.keys(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details).length!=m){

                //     if(moment(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[m].date,'DD-MM-YYYY').add(1,'days').format('DD-MM-YYYY') == this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[(parseInt(m)+1)].date){
                //       if(contDates.includes())
                //       contDates.push(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[m].date,this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[(parseInt(m)+1)].date)

                //     }
                //     else{
                //       console.log("yes i exited")
                //     }
                //   }
                // }
            }
            for (let k = 0; k < this.schedule_serviceTypes_selected.length; k++) {
                for (const sch in this.scheduleGroup) {
                    // if(Array.isArray(this.scheduleGroup[sch])){
                    if (this.scheduleGroup[sch].includes(this.schedule_serviceTypes_selected[k])) {
                        let index = this.scheduleGroup[sch].indexOf(this.schedule_serviceTypes_selected[k])
                        this.scheduleGroup[sch].splice(index, 1)
                    }
                    // }
                }
            }
            let groundid = Object.keys(this.scheduleGroup).length
            this.scheduleGroup[groundid] = [...this.schedule_serviceTypes_selected]
            this.selected_onetime_slots = {}
            this.currentSlotDay = 1
            this.onetime_scheduled = {}
            this.oneTimeSelectionStat = false
            this.schedule_serviceTypes_selected = []
            this.oneTimeDateSelected = this.today
            this.dateSelected = this.today
            this.formatDate()
            this.one_time_slots = {}
            this.activeTab = 'Cart'
        },
        findContDate() {

            const dates = Object.keys(this.selected_onetime_slots)
            let count = 0;
            let found = false
            this.date_group[count] = []
            for (let i = 0; i < dates.length; i++) {
                found = false
                if (dates.includes(moment(dates[i], 'YYYY-MM-DD').add(1, 'days').format('YYYY-MM-DD'))) {

                    for (const g in this.date_group) {
                        if (this.date_group[g].includes(dates[i])) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {

                        if (this.selected_onetime_slots[dates[i]].slots.includes("12") && this.selected_onetime_slots[moment(dates[i], 'YYYY-MM-DD').add(1, 'days').format('YYYY-MM-DD')].slots.includes("1")) {
                            if (this.date_group[count].length > 0) {
                                if ((this.date_group[count].includes(this.selected_onetime_slots[moment(dates[i], 'YYYY-MM-DD').add(1, 'days').format('YYYY-MM-DD')])) || (this.date_group[count].includes(this.selected_onetime_slots[moment(dates[i], 'YYYY-MM-DD').subtract(1, 'days').format('YYYY-MM-DD')]))) {

                                    this.date_group[count].push(dates[i])
                                }
                                else {
                                    count = count + 1
                                    this.date_group[count].push(dates[i])
                                }

                            }
                            else {
                                this.date_group[count].push(dates[i])
                            }
                            for (const g in this.date_group) {
                                if (this.date_group[g].includes(moment(dates[i], 'YYYY-MM-DD').add(1, 'days').format('YYYY-MM-DD'))) {
                                    found = true;
                                    break;
                                }
                            }
                            if (!found) {

                                this.date_group[count].push(moment(dates[i], 'YYYY-MM-DD').add(1, 'days').format('YYYY-MM-DD'))
                            }

                        }
                        else {
                            found = false
                            count = count + 1

                            this.date_group[count] = []
                            for (const g in this.date_group) {
                                if (this.date_group[g].includes(dates[i])) {
                                    found = true;
                                    break;
                                }
                            }
                            if (!found) {

                                this.date_group[count].push(dates[i])
                            }
                        }
                    }

                }
                else {
                    found = false
                    count = count + 1

                    this.date_group[count] = []
                    for (const g in this.date_group) {
                        if (this.date_group[g].includes(dates[i])) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {

                        this.date_group[count].push(dates[i])
                    }
                }

            }
        },
        addAllServiceTypes() {
            this.schedule_serviceTypes_selected = []
            if (this.scheduleStat) {
                this.schedule_serviceTypes_selected = this.multiServicesBill.map((_, i) => i)
            }
            else {
                this.schedule_serviceTypes_selected = []
            }
            this.calcSelectedServices()
        },
        addToSchedule() {

            if (this.scheduleStat) {
                this.scheduleStatus = true
            }
            else {
                this.scheduleStatus = false
            }
            for (let i = 0; i < this.schedule_serviceTypes_selected.length; i++) {

                this.scheduleFormat.individual[this.schedule_serviceTypes_selected[i]] = {
                    starting_date: this.visits[0].dateTime,
                    visits: this.visits
                }

            }
            let cleaners = this.selectedDuration.cleaners
            for (let j = 0; j < this.schedule_serviceTypes_selected.length; j++) {
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaning_policy = 'SUBSCRIPTION'
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details = {}
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaners = cleaners
                for (let k = 0; k < this.visits.length; k++) {
                    let min_slot = Math.min(...this.visits[k].slots)

                    this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[k + 1] = {

                        "date": this.visits[k].date,
                        "time": this.slotFormat[min_slot].start_time,
                        "no_of_cleaners": this.selectedDuration.cleaners,
                        "cleaning_hours": this.selectedDuration.hours,
                        "hourly_cleaning_duration": parseInt(this.hourly_cleaning.hourly_duration) || null
                    }
                }
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].shift_availability_check = !this.out_of_shift
            }
            for (let k = 0; k < this.schedule_serviceTypes_selected.length; k++) {
                for (const sch in this.scheduleGroup) {
                    // if(Array.isArray(this.scheduleGroup[sch])){
                    if (this.scheduleGroup[sch].includes(this.schedule_serviceTypes_selected[k])) {
                        let index = this.scheduleGroup[sch].indexOf(this.schedule_serviceTypes_selected[k])
                        this.scheduleGroup[sch].splice(1, index)
                    }
                    // }
                }
            }
            let groundid = Object.keys(this.scheduleGroup).length
            this.scheduleGroup[groundid] = [...this.schedule_serviceTypes_selected]

            this.visits = []
            this.selected_double_slots = []
            this.selectedDuration = {
                cleaners: '',
                hours: '',
                slots: ''
            }
            this.fixedSlots = {}
            this.reselectDateIndex = null
            this.reselectDate = {}
            this.subStat = '',
                cleaningPolicy = '',
                no_of_visits = '',
                this.visits = []
            this.schedule_serviceTypes_selected = []
            this.scheduleDateSat = false
            this.activeTab = 'Cart'
        },
        changeVisitDate() {
            this.slot_msg = false
            if (this.selected_double_slots.length == Math.ceil(this.selectedDuration.hours / 2)) {
                const day = moment(this.dateSelected, 'YYYY-MM-DD')
                const dayname = day.format('ddd')
                const startSlot = Math.min(...this.selected_double_slots)
                const dateTime = day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                this.visits[this.reselectDateIndex] = {
                    date: day.format('DD-MM-YYYY'),
                    slots: this.selected_double_slots,
                    day: dayname,
                    dateTime: day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                }
                this.visitDateTime = []
                this.visitDateTime.push(dateTime)
                this.fixedSlots = {}
                this.checkAvailablility()
                this.reselectDialog = false
                this.slot_msg = false
            }
            else {
                this.slot_msg = true
            }
        },
        reselectVisitDate(slot, index) {
            this.reselectDate = slot
            this.reselectDateIndex = index
            this.reselectDialog = true
            this.selected_double_slots = []
        },
        selectMonthlyDate(date) {
            if (this.selected_monthly_date.includes(date)) {
                let index = this.selected_monthly_date.indexOf(date)
                this.selected_monthly_date.splice(index, 1)
            }
            else {
                this.selected_monthly_date.push(date)
            }


        },
        checkFixedSlots(slot, index) {
            const duration = this.visits[index].slots.length * 2
            let startTime = ''
            let end = ''
            let endTime = ''
            let totalTime = ''
            if (this.fixedSlots[slot] != 'Not Available' && this.fixedSlots[slot]) {
                // console.log("found the slot")
                this.visits[index].slots = []
                const start = this.fixedSlots[slot]
                startTime = moment(start, 'DD-MM-YYYY hh:mm A').format('hh:mm A')
                end = moment(start, 'DD-MM-YYYY hh:mm A').add(duration, 'hours')
                endTime = moment(end).format('hh:mm A')
                totalTime = startTime + ' - ' + endTime

                this.visits[index].status = 'fixed'
                this.visits[index].dateTime = slot.split(' ')[0] + ' ' + startTime

                let counter = startTime
                let limit = endTime
                while (moment(counter, 'hh:mm A').isBefore(moment(limit, 'hh:mm A'))) {
                    for (const i in this.slotFormat) {
                        if (this.slotFormat[i].start_time == counter) {
                            this.visits[index].slots.push(parseInt(i))
                        }
                    }
                    counter = moment(counter, 'hh:mm A').add(2, 'hours').format('hh:mm A')

                }
                return totalTime
            }
            else {
                return false
            }

        },
        getCombinedSlot(slots) {
            const min = Math.min(...slots)
            const max = Math.max(...slots)
            const combined = this.slotFormat[String(min)].start_time + ' - ' + this.slotFormat[String(max)].end_time
            return combined
        },
        getCombinedOnetimeSlot(slots) {
            const min = Math.min(...slots)
            const max = Math.max(...slots)
            const combined = this.slotFormat[parseInt(min)].start_time + ' - ' + this.slotFormat[parseInt(max)].end_time
            return combined
        },
        findCustomVisits() {
            if (this.current_service == 'Hourly Cleaning') {
                this.findHourlyCost()
            }
            if (this.selected_double_slots.length == Math.ceil(this.selectedDuration.hours / 2)) {


                if (this.customDateSelected.length > 0 && this.selected_double_slots.length > 0) {
                    for (let i = 0; i < this.customDateSelected.length; i++) {
                        const day = moment(this.customDateSelected[i], 'YYYY-MM-DD')
                        const dayname = day.format('ddd')
                        const startSlot = Math.min(...this.selected_double_slots)
                        const dateTime = day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                        this.visits.push({
                            date: day.format('DD-MM-YYYY'),
                            slots: this.selected_double_slots,
                            day: dayname,
                            dateTime: day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                        })

                        this.visitDateTime.push(dateTime)
                    }
                    this.checkAvailablility()
                    this.customDialog = false
                    this.scheduleDateSat = true
                    this.schedule_err_msg = false
                }
                else {
                    this.schedule_err_msg = true
                }
                this.slot_msg = false
            }
            else {
                this.slot_msg = true
            }


        },
        findVisits() {
            if (this.current_service == 'Hourly Cleaning') {
                this.findHourlyCost()
            }
            if (this.selected_double_slots.length == Math.ceil(this.selectedDuration.hours / 2)) {
                if (this.selected_double_slots.length > 0 && this.dateSelected) {
                    this.scheduleDialog = false

                    /* Weekly Cleaning calculator */
                    if (this.subStat == 'Weekly') {
                        let count = 0
                        let visitcount = 0

                        while (count < 999) {

                            const day = moment(this.dateSelected, 'YYYY-MM-DD').add(count, "days")

                            const dayname = day.format('ddd')
                            const startSlot = Math.min(...this.selected_double_slots)
                            const dateTime = day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                            if (this.prefDay.includes(dayname)) {
                                this.visits.push({
                                    date: day.format('DD-MM-YYYY'),
                                    slots: this.selected_double_slots,
                                    day: dayname,
                                    dateTime: day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                                })

                                this.visitDateTime.push(dateTime)
                                visitcount++

                            }
                            if (visitcount == parseInt(this.no_of_visits)) {
                                this.checkAvailablility()
                                break;
                            }
                            if (this.altweekStat && dayname == 'Sat') {
                                count = count + 8
                            }
                            else {
                                count++
                            }
                        }
                    }
                    /* Daily Cleaning calculator */
                    else if (this.subStat == 'Daily') {
                        let count = 0
                        let visitcount = 0
                        while (count < 999) {

                            const day = moment(this.dateSelected, 'YYYY-MM-DD').add(count, "days")


                            const startSlot = Math.min(...this.selected_double_slots)
                            const dateTime = day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time

                            this.visits.push({
                                date: day.format('DD-MM-YYYY'),
                                slots: this.selected_double_slots,

                                dateTime: day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                            })

                            this.visitDateTime.push(dateTime)
                            visitcount++


                            if (visitcount == parseInt(this.no_of_visits)) {
                                this.checkAvailablility()
                                break;
                            }
                            if (this.altdaysStat) {
                                count = count + 2
                            }
                            else {
                                count++
                            }
                        }
                    }
                    this.scheduleDateSat = true
                }
                else {
                    this.schedule_err_msg = true
                }
                this.slot_msg = false
            }
            else {
                this.slot_msg = true
            }
        },
        findHourlyCost() {
            if (this.hourly_cleaning.hourly_duration <= 2) {
                let total_cost = 15 * parseInt(this.hourly_cleaning.cleaners)
            }
            else {
                let total_cost = 25 * parseInt(this.hourly_cleaning.cleaners)
            }
            let section_length = this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill.length
            for (let i = 0; i < section_length; i++) {
                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill[i].section_net_cost = total_cost / section_length
                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill[i].section_cost = total_cost / section_length
                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill[i].section.section_net_cost = total_cost / section_length
                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill[i].section.section_cost = total_cost / section_length
                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill[i].sectiononly_cost = total_cost / section_length
                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].bill[i].sectiononly_net_cost = total_cost / section_length

                this.multiServicesBill[this.schedule_serviceTypes_selected[0]].total_cost = total_cost
            }


        },
        findMonthlyVisits() {
            if (this.current_service == 'Hourly Cleaning') {
                this.findHourlyCost()
            }
            if (this.selected_double_slots.length == Math.ceil(this.selectedDuration.hours / 2)) {
                if (this.selected_monthly_date.length > 0 && this.selected_double_slots.length > 0) {

                    let count = 0
                    let visitcount = 0
                    while (count < 999) {

                        const day = moment(this.monthly_starting_date, 'YYYY-MM-DD').add(count, "days")

                        const dayNo = day.format('DD')
                        if (dayNo != undefined) {
                            if (this.selected_monthly_date.includes(String(dayNo))) {

                                const startSlot = Math.min(...this.selected_double_slots)
                                const dateTime = day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time

                                this.visits.push({
                                    date: day.format('DD-MM-YYYY'),
                                    slots: this.selected_double_slots,

                                    dateTime: day.format('DD-MM-YYYY') + ' ' + this.slotFormat[startSlot].start_time
                                })

                                this.visitDateTime.push(dateTime)
                                visitcount++
                            }
                        }



                        if (visitcount == parseInt(this.no_of_visits)) {
                            this.checkAvailablility()
                            break;
                        }



                        count++

                    }
                    this.monthlyDialog = false
                    this.scheduleDateSat = true
                }
                else {
                    this.schedule_err_msg = true
                }
                this.slot_msg = false
            }
            else {
                this.slot_msg = true
            }
        },
        checkAvailablility() {
            const schedule_serviceTypes = this.schedule_serviceTypes
            if (this.current_service == 'Hourly Cleaning') {
                schedule_serviceTypes = []
                schedule_serviceTypes.push('General Cleaning')
            }
            fetch(this.url + '/customer/ajax/multipleservice/multipledates/cleaningslotes/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    number_of_cleaners: this.selectedDuration.cleaners,
                    cleaning_hours: this.selectedDuration.hours,
                    service_types: schedule_serviceTypes,
                    shift_availability_check: !this.out_of_shift,
                    cleaning_datetimes: this.visitDateTime
                })
            }).then(response => response.json()).then(slotStat => {
                this.slotStat = slotStat
                for (let i = 0; i < this.visits.length; i++) {
                    if (this.slotStat.available_slotes.includes(this.visits[i].dateTime)) {
                        this.visits[i].status = 'fixed'
                    }
                }
                if (this.slotStat.busy_slotes.length > 0) {
                    this.autofixStat = false
                }
                else {
                    this.autofixStat = true
                }

            })


        },
        autoFix() {
            this.fixedSlots = {}
            fetch(this.url + '/customer/ajax/multipleservice/multipledates/cleaningslotes/autofix/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    number_of_cleaners: this.selectedDuration.cleaners,
                    cleaning_hours: this.selectedDuration.hours,
                    service_types: this.schedule_serviceTypes,
                    shift_availability_check: !this.out_of_shift,
                    cleaning_datetimes: this.slotStat.busy_slotes
                })
            }).then(response => response.json()).then(slotData => {
                this.fixedSlots = slotData.slote_details
                this.autofixStat = true


            })


        },
        checkFixStatus() {
            let flag = false
            for (let i = 0; i < this.visits.length; i++) {
                if (this.visits[i].status) {
                    if (this.visits[i].status == 'fixed') {
                        flag = true
                    }
                    else {
                        flag = false
                        break
                    }
                }
                else {
                    flag = false
                    break
                }
            }
            return flag
        },
        calcSlots() {
            this.double_slots = []
            this.selected_double_slots = []
            const slot = {
                "0": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "2": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "4": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "6": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "8": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "10": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "12": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "14": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "16": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "18": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "20": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                "22": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]

            }
            for (const i in slot) {
                if (slot[i].includes(2)) {
                    const slotNo = (parseInt(i) + 2) / 2

                    this.double_slots.push(this.slotFormat[String(slotNo)])


                }
            }
        },
        selectPrefDay(day) {
            if (!this.prefDay.includes(day)) {
                this.prefDay.push(day)
            }
            else {
                const prefIndex = this.prefDay.indexOf(day);
                this.prefDay.splice(prefIndex, 1)
            }
        },
        getIp() {
            fetch('https://www.cloudflare.com/cdn-cgi/trace')
                .then(response => response.text())
                .then((data) => {
                    const response = {}
                    data.trim().split('\n').forEach(pair => {
                        const [key, value] = pair.split('=')
                        response[key] = value
                    })
                    this.ip_address = response.ip
                })
        },
        uploadFile() {
            this.$refs.item - image.input.click()
        },
        getServiceTypes() {
            fetch('/common/staging/dynamic/get-service-types/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.mediaUrl = data.MEDIA_URL;
                    this.categories = data.service_groups ?? [];
                    this.services = data.service_types ?? [];

                    // Initialize with first category and service
                    if (this.categories.length > 0) {
                        const firstCategory = this.categories[0];
                        this.selectedCategory = firstCategory.service_name;

                        // Wait for Vue reactivity, then directly get first matching service
                        this.$nextTick(() => {
                            const matchingServices = this.services.filter(
                                service => service.service_group_id === firstCategory.id
                            );

                            if (matchingServices.length > 0) {
                                const firstService = matchingServices[0];
                                this.selectedService = firstService;
                                this.serviceType = firstService.name;

                                // Now fetch size data
                                this.$nextTick(() => {
                                    this.getSize();
                                    // also fetch addons for initial service
                                    this.getAddons();
                                });
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching service types:', error);
                    // Silently fail on page load - don't show popup to user
                });
        },

        /* ================================================================
            11. PAYMENT & CHECKOUT METHODS
            ================================================================
            Payment gateway integration, payment selection, booking completion
        ================================================================ */

        goToPayment() {
            if (this.activePayment == 'debit') {
                this.$refs.gateway_submit.click()
            }
            if (this.activePayment == 'credit') {
                window.location.href = "https://testpay.bleach-kw.com/creditcard/payment_form.php?merchant_defined_data1=" + this.bookingMultiData.order_details.order_no + "&reference_number=" + this.bookingMultiData.order_details.order_no + "&merchant_defined_data2=prepaid&amount=" + this.bookingMultiData.order_details.total_amount + "&currency=KWD&transaction_type=sale&bill_to_forename=" + this.bookingMultiData.customer_details.customer.name.split(' ')[1] + "&bill_to_surname=" + this.bookingMultiData.customer_details.customer.name.split(' ')[2] + "&bill_to_phone=mobile" + this.bookingMultiData.customer_details.customer.mobile_number + "&bill_to_email=" + this.bookingMultiData.customer_details.customer.email + "&bill_to_address_country=" + this.bookingMultiData.customer_details.customer.nationality + "&bill_to_address_city=" + this.bookingMultiData.cleaning_details[0].address.area.name + "&bill_to_address_line1=" + this.bookingMultiData.cleaning_details[0].address.governorate.name + "&merchant_defined_data4=" + this.bookingMultiData.customer_details.payment_method + "&merchant_defined_data5=NO&merchant_defined_data7=1&merchant_defined_data20=NO&customer_ip_address=" + this.ip_address
            }
        },
        selectPayment(pay) {
            this.activePayment = pay
        },
        getFiles(obj) {
            this.scale = 60
            this.quality = 60
            this.imageObj = obj

            if (obj.compressed) {
                this.images.push(obj)
                this.imageURL = URL.createObjectURL(obj.compressed.file)
            }

        },

        /* ================================================================
            8. API & SERVER CALL METHODS
            ================================================================
            fetch HTTP requests for backend communication
        ================================================================ */

        getServices() {
            fetch(this.url + "/customer/ajax/getservicetypes")
                .then(response => response.json())
                .then((data) => {
                    this.serviceTypesData = data.service_types
                })
        },
        getGovernorate() {
            fetch(this.url + "/customer/ajax/getgovernorates")
                .then(response => response.json())
                .then((data) => {
                    this.cust_governorates = data.governorates
                })
        },
        getAreas() {
            const governorate = this.serviceDetails.address_details.governorate
            fetch(this.url + "/customer/ajax/getareas?governorate_id=" + governorate)
                .then(response => response.json())
                .then((data) => {
                    this.cust_areas = data.areas
                })
        },
        getServiceId(service) {
            const serviceData = this.serviceTypesData.find(s => s.name === service)
            return serviceData?.id
        },
        scheduleBooking() {
            this.activeTab = 'Address'
            let count = 0
            for (const dateKey in this.time_slot) {
                for (const slot of this.time_slot[dateKey].selectedSlot) {
                    let selectedTime = this.formatSlotTime(slot)
                    count = count + 1
                    this.serviceDetails.schedule_details[count] = {
                        date: dateKey,
                        time: selectedTime,
                        cleaning_hours: this.selectedDuration.hours,
                        no_of_cleaners: this.selectedDuration.cleaners
                    }
                }
            }
        },

        formatSlotTime(slot) {
            if (slot === 0) return '12:00 am'
            if (slot < 12) return `${slot}:00 am`
            if (slot > 12) return `${slot - 12}:00 pm`
            return '12:00 pm'
        },

        checkScheduleStatus() {
            return this.multiServicesBill.every(service => Object.keys(service.schedule_details).length > 0)
        },
        arrangeData() {
            for (const [i, service] of this.multiServicesBill.entries()) {

                const service_id = this.getServiceId(service.service)
                this.serviceDetails.service_details[i] = {
                    "service_type": service_id,
                    "cleaning_policy": this.multiServicesBill[i].cleaning_policy,
                    "schedule_details": this.multiServicesBill[i].schedule_details,
                    "location_type": this.multiServicesBill[i].location_type,
                    "area_type": this.multiServicesBill[i].area_type,
                    "evaluator_note": this.multiServicesBill[i].evaluator_note,
                    "estimated_cost": this.multiServicesBill[i].total_cost,
                    "total_cost": this.multiServicesBill[i].total_cost,
                    "number_of_cleaners": this.multiServicesBill[i].cleaners,

                    "cleaning_hours": parseInt(this.selectedDuration.hours),
                    sections: {}
                }

                if (this.serviceDetails.service_details[i].cleaning_policy == 'SUBSCRIPTION') {
                    const visits = Object.keys(this.multiServicesBill[i].schedule_details).length
                    this.serviceDetails.service_details[i].total_cost = parseFloat(this.serviceDetails.service_details[i].total_cost) * parseInt(visits)
                    this.serviceDetails.service_details[i].estimated_cost = parseFloat(this.serviceDetails.service_details[i].total_cost)
                }
                for (const [j, bill] of this.multiServicesBill[i].bill.entries()) {
                    this.serviceDetails.service_details[i].sections[j] = {
                        "section_name": bill.section_name,
                        "size": bill.section.size.name,
                        "wall_type": "",
                        "floor_type": '',
                        "ceiling_type": '',
                        "cement_residue": bill.section.cement_residue,
                        "oil_residue": bill.section.residue,
                        "section_cost": bill.section_cost,
                        "sectiononly_cost": bill.sectiononly_cost,
                        "sectiononly_net_cost": bill.sectiononly_cost,
                        "section_net_cost": bill.section_net_cost,
                        "keynotes": {},
                        "addons": {},
                        "new_kitchen": false,
                        "is_cabinet": false,
                        "is_highprice_facade": false,
                        "is_highprice_window": false,
                        "colour": '',
                        "material": '',
                        "cause_of_stain": '',
                        "upholstery_type": '',
                        "age": '',
                        "age_of_stain": ''

                    }
                    if (this.serviceDetails.service_details[i].cleaning_policy == 'SUBSCRIPTION') {
                        this.serviceDetails.service_details[i].sections[j].sectiononly_net_cost = this.serviceDetails.service_details[i].sections[j].sectiononly_net_cost * parseInt(this.visits)
                        this.serviceDetails.service_details[i].sections[j].section_net_cost = this.serviceDetails.service_details[i].sections[j].section_net_cost * parseInt(this.visits)
                    }
                    if (this.multiServicesBill[i].bill[j].section.size.is_highprice_facade) {
                        this.serviceDetails.service_details[i].sections[j].is_highprice_facade = true
                    }

                    if (this.multiServicesBill[i].bill[j].section.size.is_highprice_window) {
                        this.serviceDetails.service_details[i].sections[j].is_highprice_window = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.size.is_newkitchen) {
                        this.serviceDetails.service_details[i].sections[j].new_kitchen = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.is_cabinet) {
                        this.serviceDetails.service_details[i].sections[j].is_cabinet = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.stain_age) {
                        this.serviceDetails.service_details[i].sections[j].age_of_stain = this.multiServicesBill[i].bill[j].section.stain_age
                    }
                    if (this.multiServicesBill[i].bill[j].section.color) {
                        this.serviceDetails.service_details[i].sections[j].colour = this.multiServicesBill[i].bill[j].section.color.join()
                    }
                    if (this.multiServicesBill[i].bill[j].section.material) {
                        this.serviceDetails.service_details[i].sections[j].material = this.multiServicesBill[i].bill[j].section.material.join()
                    }
                    if (this.multiServicesBill[i].bill[j].section.stain_reason) {
                        this.serviceDetails.service_details[i].sections[j].cause_of_stain = this.multiServicesBill[i].bill[j].section.stain_reason
                    }
                    if (this.multiServicesBill[i].bill[j].section.type == 'SOFA' || this.multiServicesBill[i].bill[j].section.type == 'CURTAIN') {
                        this.serviceDetails.service_details[i].sections[j].upholstery_type = this.multiServicesBill[i].bill[j].section.type

                    }
                    if (this.multiServicesBill[i].bill[j].section.wall_type) {
                        this.serviceDetails.service_details[i].sections[j].wall_type = this.multiServicesBill[i].bill[j].section.wall_type.join()

                    }
                    if (this.multiServicesBill[i].bill[j].section.ceiling_type) {
                        this.serviceDetails.service_details[i].sections[j].ceiling_type = this.multiServicesBill[i].bill[j].section.ceiling_type.join()

                    }
                    if (this.multiServicesBill[i].bill[j].section.floor_type) {
                        this.serviceDetails.service_details[i].sections[j].floor_type = this.multiServicesBill[i].bill[j].section.floor_type.join()

                    }
                    if (this.multiServicesBill[i].bill[j].section.age) {
                        this.serviceDetails.service_details[i].sections[j].age = this.multiServicesBill[i].bill[j].section.age

                    }

                    var keynotecounter = 1
                    if (this.multiServicesBill[i].bill[j].section.no_of_bathrooms) {
                        this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                            "sub_area": "bathroom",
                            "quantity": this.multiServicesBill[i].bill[j].section.no_of_bathrooms

                        }
                        keynotecounter = keynotecounter + 1
                    }
                    if (this.multiServicesBill[i].bill[j].section.no_of_rooms) {
                        this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                            "sub_area": "rooms",
                            "quantity": this.multiServicesBill[i].bill[j].section.no_of_rooms

                        }
                        keynotecounter = keynotecounter + 1
                    }
                    if (this.multiServicesBill[i].bill[j].section.no_of_windows) {
                        this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                            "sub_area": "windows",
                            "quantity": this.multiServicesBill[i].bill[j].section.no_of_windows

                        }
                        keynotecounter = keynotecounter + 1
                    }

                    if (this.multiServicesBill[i].bill[j].section.keynote_data.length > 0) {
                        for (const keynote of this.multiServicesBill[i].bill[j].section.keynote_data) {
                            this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                                "sub_area": keynote.name,
                                "quantity": keynote.value

                            }
                            keynotecounter = keynotecounter + 1
                        }

                    }
                    var addoncounter = 0
                    if (this.multiServicesBill[i].bill[j].section.addons) {
                        for (const addon of this.multiServicesBill[i].bill[j].section.addons) {
                            if (addon.selected) {
                                addoncounter = addoncounter + 1
                                // Handle both old structure (addon.details.name) and new structure (addon.name)
                                const addonName = addon.name || addon.details?.name || 'Addon';
                                const addonPrice = addon.unit_price || addon.details?.price || 0;
                                const addonQuantity = addon.quantity || 1;
                                
                                this.serviceDetails.service_details[i].sections[j].addons[addoncounter] = {
                                    name: addonName,
                                    addon_cost: addonPrice,
                                    addon_net_cost: addonPrice * addonQuantity,
                                    quantity: addonQuantity,
                                    size: '',
                                    other_details: ''
                                }
                                
                                // Check if addon has size information
                                const selectedSize = addon.selected_size || addon.details?.category;
                                if (selectedSize) {
                                    const sizeValue = addon.selected_size?.size || selectedSize;
                                    this.serviceDetails.service_details[i].sections[j].addons[addoncounter].size = sizeValue;
                                }
                            }
                        }
                    }
                    if (this.multiServicesBill[i].bill[j].section.kitchen) {
                        let newindex = Object.keys(this.serviceDetails.service_details[i].sections[j].addons).length
                        for (const kitchen of this.multiServicesBill[i].bill[j].section.kitchens) {
                            newindex = newindex + 1
                            this.serviceDetails.service_details[i].sections[j].addons[newindex] = {
                                name: "kitchen",
                                addon_cost: kitchen.size ? kitchen.size.cost : 0,
                                addon_net_cost: kitchen.size ? kitchen.size.cost : 0,
                                quantity: 1,
                                size: kitchen.size.name,
                                other_details: JSON.stringify({
                                    size: kitchen.size.name,
                                    max_size: kitchen.size.max_size,
                                    type: kitchen.type,
                                    residue: kitchen.residue,
                                    is_cabinet: kitchen.is_cabinet
                                })
                            }
                        }

                    }

                }
            }
            this.serviceDetails.shift_availability_check = this.multiServicesBill[0].shift_availability_check
            let tc = 0
            for (const sr in this.serviceDetails.service_details) {
                tc = tc + parseInt(this.serviceDetails.service_details[sr].total_cost)
            }
            this.serviceDetails.total_cost = tc
            this.serviceDetails.estimated_cost = tc

            this.bookMultipleService()
        },
        arrangeCustData() {
            for (let i = 0; i < this.multiServicesBill.length; i++) {

                const service_id = this.getServiceId(this.multiServicesBill[i].service)
                this.serviceDetails.service_details[i] = {
                    "service_type": service_id,
                    "location_type": this.multiServicesBill[i].location_type,
                    "area_type": this.multiServicesBill[i].area_type,
                    "evaluator_note": this.multiServicesBill[i].evaluator_note,
                    "estimated_cost": this.multiServicesBill[i].total_cost,
                    "total_cost": this.multiServicesBill[i].total_cost,
                    sections: {}
                }
                for (let j = 0; j < this.multiServicesBill[i].bill.length; j++) {
                    this.serviceDetails.service_details[i].sections[j] = {
                        "section_name": this.multiServicesBill[i].bill[j].section_name,

                        "size": this.multiServicesBill[i].bill[j].section.size.name,
                        "wall_type": "",
                        "floor_type": '',
                        "ceiling_type": '',
                        "cement_residue": this.multiServicesBill[i].bill[j].section.cement_residue,
                        "oil_residue": this.multiServicesBill[i].bill[j].section.residue,
                        "section_cost": this.multiServicesBill[i].bill[j].section_net_cost,
                        "sectiononly_cost": this.multiServicesBill[i].bill[j].sectiononly_cost,
                        "sectiononly_net_cost": this.multiServicesBill[i].bill[j].sectiononly_cost,
                        "section_net_cost": this.multiServicesBill[i].bill[j].section_net_cost,
                        "keynotes": {},
                        "addons": {},
                        "new_kitchen": false,
                        "is_cabinet": false,
                        "is_highprice_facade": false,
                        "is_highprice_window": false,
                        "colour": '',
                        "material": '',
                        "cause_of_stain": '',
                        "upholstery_type": '',
                        "age": ''

                    }

                    if (this.multiServicesBill[i].bill[j].section.size.is_highprice_facade) {
                        this.serviceDetails.service_details[i].sections[j].is_highprice_facade = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.size.is_highprice_window) {
                        this.serviceDetails.service_details[i].sections[j].is_highprice_window = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.size.is_newkitchen) {
                        this.serviceDetails.service_details[i].sections[j].new_kitchen = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.is_cabinet) {
                        this.serviceDetails.service_details[i].sections[j].is_cabinet = true
                    }
                    if (this.multiServicesBill[i].bill[j].section.stain_age) {
                        this.serviceDetails.service_details[i].sections[j].age_of_stain = this.multiServicesBill[i].bill[j].section.stain_age
                    }
                    if (this.multiServicesBill[i].bill[j].section.color) {
                        this.serviceDetails.service_details[i].sections[j].colour = this.multiServicesBill[i].bill[j].section.color.join()
                    }
                    if (this.multiServicesBill[i].bill[j].section.material) {
                        this.serviceDetails.service_details[i].sections[j].material = this.multiServicesBill[i].bill[j].section.material.join()
                    }
                    if (this.multiServicesBill[i].bill[j].section.stain_reason) {
                        this.serviceDetails.service_details[i].sections[j].cause_of_stain = this.multiServicesBill[i].bill[j].section.stain_reason
                    }
                    if (this.multiServicesBill[i].bill[j].section.type == 'SOFA' || this.multiServicesBill[i].bill[j].section.type == 'CURTAIN') {
                        this.serviceDetails.service_details[i].sections[j].upholstery_type = this.multiServicesBill[i].bill[j].section.type

                    }
                    if (this.multiServicesBill[i].bill[j].section.wall_type) {
                        this.serviceDetails.service_details[i].sections[j].wall_type = this.multiServicesBill[i].bill[j].section.wall_type.join()

                    }
                    if (this.multiServicesBill[i].bill[j].section.ceiling_type) {
                        this.serviceDetails.service_details[i].sections[j].ceiling_type = this.multiServicesBill[i].bill[j].section.ceiling_type.join()

                    }
                    if (this.multiServicesBill[i].bill[j].section.floor_type) {
                        this.serviceDetails.service_details[i].sections[j].floor_type = this.multiServicesBill[i].bill[j].section.floor_type.join()

                    }
                    if (this.multiServicesBill[i].bill[j].section.age) {
                        this.serviceDetails.service_details[i].sections[j].age = this.multiServicesBill[i].bill[j].section.age

                    }

                    var keynotecounter = 1
                    if (this.multiServicesBill[i].bill[j].section.no_of_bathrooms) {
                        this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                            "sub_area": "bathroom",
                            "quantity": this.multiServicesBill[i].bill[j].section.no_of_bathrooms

                        }
                        keynotecounter = keynotecounter + 1
                    }
                    if (this.multiServicesBill[i].bill[j].section.no_of_rooms) {
                        this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                            "sub_area": "rooms",
                            "quantity": this.multiServicesBill[i].bill[j].section.no_of_rooms

                        }
                        keynotecounter = keynotecounter + 1
                    }
                    if (this.multiServicesBill[i].bill[j].section.no_of_windows) {
                        this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                            "sub_area": "windows",
                            "quantity": this.multiServicesBill[i].bill[j].section.no_of_windows

                        }
                        keynotecounter = keynotecounter + 1
                    }
                    if (this.multiServicesBill[i].bill[j].section.keynote_data.length > 0) {
                        for (const keynote of this.multiServicesBill[i].bill[j].section.keynote_data) {
                            this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter] = {
                                "sub_area": keynote.name,
                                "quantity": keynote.value

                            }
                            keynotecounter = keynotecounter + 1
                        }

                    }
                    var addoncounter = 0
                    if (this.multiServicesBill[i].bill[j].section.addons) {
                        for (const addon of this.multiServicesBill[i].bill[j].section.addons) {
                            if (addon.selected) {
                                addoncounter = addoncounter + 1
                                // Handle both old structure (addon.details.name) and new structure (addon.name)
                                const addonName = addon.name || addon.details?.name || 'Addon';
                                const addonPrice = addon.unit_price || addon.details?.price || 0;
                                const addonQuantity = addon.quantity || 1;
                                
                                this.serviceDetails.service_details[i].sections[j].addons[addoncounter] = {
                                    name: addonName,
                                    addon_cost: addonPrice,
                                    addon_net_cost: addonPrice * addonQuantity,
                                    quantity: addonQuantity
                                }
                                
                                // Check if addon has size information
                                const selectedSize = addon.selected_size || addon.details?.category;
                                if (selectedSize) {
                                    const sizeValue = addon.selected_size?.size || selectedSize;
                                    this.serviceDetails.service_details[i].sections[j].addons[addoncounter].size = sizeValue;
                                }
                            }
                        }
                    }
                    if (this.multiServicesBill[i].bill[j].section.kitchen) {
                        let newindex = Object.keys(this.serviceDetails.service_details[i].sections[j].addons).length
                        for (const kitchen of this.multiServicesBill[i].bill[j].section.kitchens) {
                            newindex = newindex + 1
                            this.serviceDetails.service_details[i].sections[j].addons[newindex] = {
                                name: "kitchen",
                                addon_cost: kitchen.size ? kitchen.size.cost : 0,
                                addon_net_cost: kitchen.size ? kitchen.size.cost : 0,
                                quantity: 1,
                                size: kitchen.size.name,
                                other_details: JSON.stringify({
                                    size: kitchen.size.name,
                                    max_size: kitchen.size.max_size,
                                    type: kitchen.type,
                                    residue: kitchen.residue,
                                    is_cabinet: kitchen.is_cabinet

                                })
                            }
                        }

                    }
                }
            }

            this.serviceDetails.total_cost = this.totalCost
            this.serviceDetails.estimated_cost = this.totalCost

            this.bookCustService()
        },
        openFloor(index, floor) {
            this.e.building[index - 1].e = floor
            this.building[index - 1].completed = false
        },
        openApartment(index, floor, apindex) {
            this.e.building[index - 1].floors[floor - 1].e = apindex + 1
            this.building[index - 1].floors[floor - 1].completed = false
        },

        /* ================================================================
            9. KITCHEN MANAGEMENT METHODS
            ================================================================
            Add, edit, update, delete kitchen details for properties
        ================================================================ */

        addKitchen(building, floor) {

            if (this.$refs['kitchenFloor-building-' + (building) + 'floor-' + (floor)][0].validate()) {
                this.building[building].floors[floor].kitchens.push(this.kitchenData)
                this.forceRerender();
                this.kitchenData = {
                    wall_type: '',
                    floor_type: '',
                    size: null,
                    ceiling_type: '',
                    condition: '',
                    is_cabinet: false,
                    type: 'old',
                    residue: false
                }
                this.changeNewKitchen()
                this.recalcPrice(building, floor)
            }

        },
        addApartmentKitchen(building, floor, apartment) {


            this.building[building].floors[floor].apartments[apartment].kitchens.push(this.kitchenData)
            this.forceRerender();
            this.kitchenData = {
                wall_type: '',
                floor_type: '',
                size: null,
                ceiling_type: '',
                condition: '',
                is_cabinet: false,
                type: 'old',
                residue: false
            }
            this.changeNewKitchen()
            this.recalcApartmentPrice(building, floor, apartment)


        },
        addMoreKitchen(building, floor) {

            if (this.$refs['KitchenForm-building-' + building + 'floor' - floor].validate()) {
                const temp = { ...this.kitchenData }
                this.building[building].floors[floor].kitchens.push(temp)
                this.forceRerender();
                this.kitchenData = {
                    wall_type: '',
                    floor_type: '',
                    size: null,
                    ceiling_type: '',
                    condition: '',
                    type: 'old',
                    is_cabinet: false,
                    residue: false
                }
                this.changeNewKitchen()
                this.kitchendialog = false
                this.recalcPrice(building, floor)

            }
        },
        changeFloorKitchenStat(building, floor) {
            if (!this.building[building].floors[floor].kitchen) {
                this.building[building].floors[floor].kitchens = []
            }
            this.recalcPrice(building, floor)
        },
        changeApartmentKitchenStat(building, floor, apartment) {
            if (!this.building[building].floors[floor].apartments[apartment].kitchen) {
                this.building[building].floors[floor].apartments[apartment].kitchens = []
            }
            this.recalcApartmentPrice(building, floor, apartment)
        },
        addMoreKitchenApartment(building, floor, apartment) {


            const temp = { ...this.kitchenData }
            this.building[building].floors[floor].apartments[apartment].kitchens.push(temp)
            this.forceRerender();
            this.kitchenData = {
                wall_type: '',
                floor_type: '',
                size: null,
                ceiling_type: '',
                condition: '',
                is_cabinet: false,
                residue: false,
                type: 'old'
            }
            this.changeNewKitchen()
            this.kitchendialog = false
            this.recalcApartmentPrice(building, floor, apartment)

        },
        addNewKitchen(building, floor) {

            this.kitchenType = 'floor'
            this.currentBuilding = building
            this.currentFloor = floor
            this.kitchendialog = true
            this.kitchendialogStat = true
            this.kitchenData = {
                wall_type: '',
                floor_type: '',
                size: '',
                ceiling_type: '',
                condition: '',
                type: 'old',
                is_cabinet: false,
                residue: false
            }
            this.changeNewKitchen()



        },
        addNewKitchenWithAddon() {
            this.otherService = {
                material: "",
                color: "",
                size: "",
                type: "old",
                age: "",
                stain: false,
                stain_reason: "",
                wall_type: "",
                floor_type: "",
                ceiling_type: "",
                residue: false,
                hallway_size: "",
                sides: "",
                stain_age: "",
                height: "",
                keynote_data: [],
                addons: []
            }
            this.add_new_kitchen = true
            this.currentItem = null
            this.parseAddons()
        },
        addNewApartmentKitchen(building, floor, apartment) {

            this.kitchenType = 'apartment'
            this.currentBuilding = building
            this.currentFloor = floor
            this.currentApartment = apartment
            this.kitchendialog = true
            this.kitchendialogStat = true
            this.kitchenData = {
                wall_type: '',
                floor_type: '',
                size: '',
                ceiling_type: '',
                condition: '',
                type: 'old',
                is_cabinet: false,
                residue: false
            }
            this.changeNewKitchen()

        },
        editNewKitchen(building, floor, serv) {

            this.kitchenType = 'floor'
            this.currentBuilding = building
            this.currentFloor = floor
            this.currentKitchen = serv
            this.kitchendialog = true
            this.kitchendialogStat = false
            this.kitchenData.wall_type = this.building[building].floors[floor].kitchens[serv].wall_type
            this.kitchenData.floor_type = this.building[building].floors[floor].kitchens[serv].floor_type
            this.kitchenData.size = this.building[building].floors[floor].kitchens[serv].size
            this.kitchenData.ceiling_type = this.building[building].floors[floor].kitchens[serv].ceiling_type
            this.kitchenData.condition = this.building[building].floors[floor].kitchens[serv].condition
            this.kitchenData.type = this.building[building].floors[floor].kitchens[serv].type
            this.kitchenData.residue = this.building[building].floors[floor].kitchens[serv].residue



        },
        editNewApartmentKitchen(building, floor, apartment, serv) {

            this.kitchenType = 'apartment'
            this.currentBuilding = building
            this.currentFloor = floor
            this.currentKitchen = serv
            this.currentApartment = apartment
            this.kitchendialog = true
            this.kitchendialogStat = false
            this.kitchenData.wall_type = this.building[building].floors[floor].apartments[apartment].kitchens[serv].wall_type
            this.kitchenData.floor_type = this.building[building].floors[floor].apartments[apartment].kitchens[serv].floor_type
            this.kitchenData.size = this.building[building].floors[floor].apartments[apartment].kitchens[serv].size
            this.kitchenData.ceiling_type = this.building[building].floors[floor].apartments[apartment].kitchens[serv].ceiling_type
            this.kitchenData.condition = this.building[building].floors[floor].apartments[apartment].kitchens[serv].condition
            this.kitchenData.type = this.building[building].floors[floor].apartments[apartment].kitchens[serv].type
            this.kitchenData.residue = this.building[building].floors[floor].apartments[apartment].kitchens[serv].residue


        },
        updateKitchen() {
            this.building[this.currentBuilding].floors[this.currentFloor].kitchens[this.currentKitchen] = this.kitchenData
            this.kitchendialog = false
            this.forceRerender()
            this.kitchenData = {
                wall_type: '',
                floor_type: '',
                size: null,
                ceiling_type: '',
                condition: '',
                is_cabinet: false,
                type: '',
                residue: false
            }
            this.changeNewKitchen()
            this.recalcPrice(this.currentBuilding, this.currentFloor)
        },
        updateKitchenApartment() {
            this.building[this.currentBuilding].floors[this.currentFloor].apartments[this.currentApartment].kitchens[this.currentKitchen] = this.kitchenData
            this.kitchendialog = false
            this.forceRerender()
            this.kitchenData = {
                wall_type: '',
                floor_type: '',
                size: null,
                ceiling_type: '',
                condition: '',
                type: 'old',
                residue: false,
                is_cabinet: false,
            }
            this.changeNewKitchen()
            this.recalcApartmentPrice(this.currentBuilding, this.currentFloor, this.currentApartment)
        },
        deleteKitchen(building, floor, service) {
            this.building[building].floors[floor].kitchens.splice(service, 1)
            this.forceRerender();
            this.recalcPrice(building, floor);
        },
        deleteApartmentKitchen(building, floor, apartment, service) {
            this.building[building].floors[floor].apartments[apartment].kitchens.splice(service, 1)
            this.forceRerender();
            this.recalcApartmentPrice(building, floor, apartment);
        },
        changeKitchen() {


            this.sizeFilteredData = [];
            this.otherService.size = ""
            this.parseAddons()
            this.kitchenTypeFilter();
            // $('.more-services').hide()
            // if (this.otherService.type == "new") {
            //     if (this.otherService.is_cabinet) {
            //         this.sizeFilteredData = this.sizeData.filter(size => size.is_newkitchen && size.is_cabinet)
            //     }
            //     else {
            //         this.sizeFilteredData = this.sizeData.filter(size => size.is_newkitchen && !size.is_cabinet)
            //     }
            // }
            // if (this.otherService.type == "old") {
            //     $('.more-services').show()
            //     if (this.otherService.is_cabinet) {
            //         this.sizeFilteredData = this.sizeData.filter(size => !size.is_newkitchen && size.is_cabinet)
            //     }
            //     else {
            //         this.sizeFilteredData = this.sizeData.filter(size => !size.is_newkitchen && !size.is_cabinet)
            //     }
            // }
        },
        changeNewKitchen() {
            this.kitchenData.size = ''
            fetch(this.url + "/customer/ajax/getservicesizeprice?service_type=Kitchen Cleaning")
                .then(response => response.json())
                .then((kitchenSize) => {
                    this.kitchenSize = kitchenSize;
                    this.kitchenSizeData = [];
                    // Ensure kitchenSize is an array
                    const kitchenArray = Array.isArray(kitchenSize) ? kitchenSize : (kitchenSize.data || []);
                    for (const kitchen of kitchenArray) {
                        kitchen["combinedSize"] =
                            kitchen.name +
                            " ( " +
                            kitchen.min_size +
                            " sq. m - " +
                            kitchen.max_size +
                            " sq. m )";
                        this.kitchenSizeData.push(kitchen);
                    }
                    this.serviceSize = {};
                    if (this.kitchenData.type == "new") {
                        $('.more-services').hide()
                        this.parseAddons()
                        if (this.kitchenData.is_cabinet) {
                            for (var i = 0; i < this.kitchenSizeData.length; i++) {
                                if (this.kitchenSizeData[i].is_newkitchen && this.kitchenSizeData[i].is_cabinet) {
                                    this.sizeFilteredData.push(this.kitchenSizeData[i]);
                                }
                            }
                        }
                        else {
                            for (var i = 0; i < this.kitchenSizeData.length; i++) {
                                if (this.kitchenSizeData[i].is_newkitchen && !this.kitchenSizeData[i].is_cabinet) {
                                    this.sizeFilteredData.push(this.kitchenSizeData[i]);
                                }
                            }
                        }
                    }
                    if (this.kitchenData.type == "old") {
                        $('.more-services').show()
                        if (this.kitchenData.is_cabinet) {
                            for (var i = 0; i < this.kitchenSizeData.length; i++) {
                                if (!this.kitchenSizeData[i].is_newkitchen && this.kitchenSizeData[i].is_cabinet) {
                                    this.sizeFilteredData.push(this.kitchenSizeData[i]);
                                }
                            }
                        }
                        else {
                            for (var i = 0; i < this.kitchenSizeData.length; i++) {
                                if (!this.kitchenSizeData[i].is_newkitchen && !this.kitchenSizeData[i].is_cabinet) {
                                    this.sizeFilteredData.push(this.kitchenSizeData[i]);
                                }
                            }
                        }
                    }
                })
                .catch((error) => {
                });
            this.sizeFilteredData = [];

        },

        /* ================================================================
            6. CUSTOMER & OTP VERIFICATION METHODS
            ================================================================
            OTP sending, verification, and customer authentication
        ================================================================ */

        /**
         * Send OTP to customer's mobile number
         * Sets otpStat on success, errorStat on failure
         */
        sendOtp() {
            fetch(`${this.url}/customer/ajax/addressotpsend?mobile_number=${this.mob_number}`)
                .then(response => response.json())
                .then((data) => {
                    this.otpStat = !data.success;
                    this.errorStat = !this.otpStat;
                })
                .catch((error) => {
                    console.error('OTP Send Error:', error);
                    this.errorStat = true;
                    this.otpStat = false;
                });
        },
        /**
         * Verify OTP entered by customer
         * On success, retrieves customer details and sets first address as selected
         */
        verifyOtp() {
            fetch(`${this.url}/customer/ajax/addressotpverify?address_otp=${this.mob_otp}`)
                .then(response => response.json())
                .then((data) => {
                    if (data.success) {
                        this.verificationStat = true;
                        this.customerDetails = data;
                        this.selectedAddress = this.customerDetails.customer_addresses?.[0] || null;
                        this.verifyStat = true;
                        this.errorVerifyStat = false;
                    } else {
                        this.verifyStat = true;
                        this.errorVerifyStat = true;
                    }
                })
                .catch((error) => {
                    console.error('OTP Verification Error:', error);
                    this.verifyStat = false;
                    this.errorVerifyStat = true;
                });
        },
        /**
         * Verify OTP using test mode (mobile number based)
         * Used for testing without actual OTP delivery
         */
        verifyTest() {
            fetch(`${this.url}/customer/ajax/addressotpverifytest?mobile_number=${this.mob_number}`)
                .then(response => response.json())
                .then((data) => {
                    if (data.success) {
                        this.verificationStat = true;
                        this.customerDetails = data;
                        this.selectedAddress = this.customerDetails.customer_addresses?.[0] || null;
                        this.verifyStat = true;
                        this.errorVerifyStat = false;
                    } else {
                        this.verifyStat = true;
                        this.errorVerifyStat = true;
                    }
                })
                .catch((error) => {
                    console.error('Test Verification Error:', error);
                    this.verifyStat = false;
                    this.errorVerifyStat = true;
                });
        },

        /* ================================================================
            7. SLOT MANAGEMENT METHODS
            ================================================================
            Time slot selection, validation, and management
        ================================================================ */

        /**
         * Check if a slot can be selected based on availability and rules
         * Adjacent slots must be within 3 positions of each other
         * @param {string|number} slot - The slot number to check
         * @returns {boolean} True if slot selection is allowed
         */
        checkSlot(slot) {
            const selectedSlots = this.time_slot[this.slotDate]?.selectedSlot || [];
            const maxSlots = this.selectedDuration?.slots || 0;

            // Check if within slot limit and max 4 slots allowed
            if (this.slotCounter >= maxSlots || selectedSlots.length >= 4) {
                return false;
            }

            // If no slots selected yet, allow first selection
            if (selectedSlots.length === 0) {
                return true;
            }

            // Check if slot is adjacent (±3 positions) to already selected slots
            const slotNum = parseInt(slot, 10);
            return selectedSlots.some(existingSlot => {
                const diff = Math.abs(slotNum - parseInt(existingSlot, 10));
                return diff === 3;
            });
        },
        /**
         * Force re-render of component by removing and re-adding it
         */
        forceRerender() {
            this.renderComponent = false;
            this.$nextTick(() => {
                this.renderComponent = true;
            });
        },
        /**
         * Add a double slot to selected slots
         * @param {string} start - Start time
         * @param {string} end - End time
         * @param {number} slot - Slot number
         */
        addDoubleSlot(start, end, slot) {
            this.selected_double_slots.push(slot);
        },
        /**
         * Add a one-time slot for the selected date
         * @param {string} start - Start time
         * @param {string} end - End time
         * @param {number} slot - Slot number
         */
        addOneTimeSlot(start, end, slot) {
            this.onetimerender = false;

            // Find slot format index by start time
            const slotIndex = Object.keys(this.slotFormat).find(
                i => this.slotFormat[i].start_time === start
            );

            if (slotIndex !== undefined) {
                this.one_time_slots[this.oneTimeDateSelected].slots.push(slotIndex);
            }

            this.onetimerender = true;
        },

        /**
         * Reset all one-time slot selections and related data
         */
        resetOneTime() {
            this.onetimerender = false;
            this.one_time_slots = {};
            this.date_group = {};
            this.one_time_slots[this.oneTimeDateSelected] = { slots: [] };
            this.selected_onetime_slots = {};
            this.currentSlotDay = 1;
            this.onetimerender = true;
        },
        /**
         * Check if any one-time slots have been selected
         * @returns {boolean} True if at least one slot is selected
         */
        checkSlotSelection() {
            return Object.values(this.selected_onetime_slots).some(
                dateSlot => (dateSlot.slots?.length || 0) > 0
            );
        },
        /**
         * Check if a specific start time slot is already selected
         * @param {string} start - Start time
         * @param {string} end - End time
         * @param {number} slot - Slot number to check
         * @returns {boolean} True if slot is already selected
         */
        checkOneTimeSlot(start, end, slot) {
            // Find slot format index by start time
            const slotIndex = Object.keys(this.slotFormat).find(
                i => this.slotFormat[i].start_time === start
            );

            if (slotIndex === undefined) {
                return false;
            }

            return this.one_time_slots[this.oneTimeDateSelected].slots.includes(slotIndex);
        },
        /**
         * Remove a one-time slot from selection
         * Adjusts slot numbers if needed (removes higher slots when adjacent slots remain)
         * @param {number} slot - The slot to remove
         */
        removeOneTimeSlot(slot) {
            this.onetimerender = false;
            const slots = this.one_time_slots[this.oneTimeDateSelected].slots;
            const index = slots.indexOf(slot);

            if (index > -1) {
                slots.splice(index, 1);
            }

            // If both adjacent slots exist, remove all higher slots
            const prevSlot = parseInt(slot, 10) - 1;
            const nextSlot = parseInt(slot, 10) + 1;

            if (slots.includes(nextSlot) && slots.includes(prevSlot)) {
                const filteredSlots = slots.filter(s => s <= slot);
                this.one_time_slots[this.oneTimeDateSelected].slots = filteredSlots;
            }

            this.onetimerender = true;
        },

        /**
         * Remove a double slot from selection
         * Adjusts slot numbers if needed (removes higher slots when adjacent slots remain)
         * @param {number} slot - The slot to remove
         */
        removeDoubleSlot(slot) {
            const index = this.selected_double_slots.indexOf(slot);

            if (index > -1) {
                this.selected_double_slots.splice(index, 1);
            }

            // If both adjacent slots exist, remove all higher slots
            const prevSlot = parseInt(slot, 10) - 1;
            const nextSlot = parseInt(slot, 10) + 1;

            if (this.selected_double_slots.includes(nextSlot) && this.selected_double_slots.includes(prevSlot)) {
                const filteredSlots = this.selected_double_slots.filter(s => s <= slot);
                this.selected_double_slots = filteredSlots;
            }
        },
        /**
         * Check if a double slot can be selected
         * @param {number} slot - Slot number to check
         * @returns {boolean} True if slot can be selected
         */
        checkSlotStat(slot) {
            const maxSlots = this.selectedDuration?.slots || 0;
            const hasSlots = this.selected_double_slots.length > 0;

            // Cannot select if already at max slots
            if (this.selected_double_slots.length >= maxSlots) {
                return false;
            }

            // First slot can always be selected if under limit
            if (!hasSlots) {
                return true;
            }

            const slotNum = parseInt(slot, 10);
            const prevSlot = slotNum - 1;
            const nextSlot = slotNum + 1;

            // Check adjacency based on slot position
            if (slotNum === 1) {
                return this.selected_double_slots.includes(nextSlot);
            } else if (slotNum === 12) {
                return this.selected_double_slots.includes(prevSlot);
            } else {
                return this.selected_double_slots.includes(prevSlot) || this.selected_double_slots.includes(nextSlot);
            }
        },
        /**
         * Check if the current date has been selected for one-time slots
         * @returns {boolean} True if current date exists in selected slots
         */
        checkSelectedDate() {
            return this.oneTimeDateSelected in this.selected_onetime_slots;
        },

        /**
         * Check if a one-time slot can be selected
         * @param {string} start - Start time
         * @param {string} end - End time
         * @param {number} slot - Slot position (1-12)
         * @returns {boolean} True if slot can be selected
         */
        checkOneTimeSlotStat(start, end, slot) {
            // Find slot format index by start time
            const currSlotIndex = Object.keys(this.slotFormat).find(
                i => this.slotFormat[i].start_time === start
            );

            if (currSlotIndex === undefined) {
                return false;
            }

            // Count total slots across all dates
            const totalSlots = Object.values(this.one_time_slots).reduce(
                (sum, dateSlot) => sum + (dateSlot.slots?.length || 0), 0
            );

            const maxSlotsRequired = Math.ceil((this.cleaning_set[this.currentSlotDay - 1]?.[0] || 0) / 2);

            // Cannot select if max slots reached
            if (totalSlots >= maxSlotsRequired) {
                return false;
            }

            // First slot for this date can always be selected
            const currentDateSlots = this.one_time_slots[this.oneTimeDateSelected].slots;
            if (!currentDateSlots || currentDateSlots.length === 0) {
                return true;
            }

            // Check adjacency for subsequent slots
            const slotNum = parseInt(currSlotIndex, 10);
            const prevSlot = slotNum - 1;
            const nextSlot = slotNum + 1;

            if (slot === 1) {
                return currentDateSlots.includes(String(nextSlot));
            } else if (slot === 12) {
                return currentDateSlots.includes(String(prevSlot));
            } else {
                return currentDateSlots.includes(String(prevSlot)) || currentDateSlots.includes(String(nextSlot));
            }
        },
        /**
         * Count total one-time slots selected across all dates
         * @returns {number} Total number of slots selected
         */
        oneTimeSlotCounter() {
            return Object.values(this.one_time_slots).reduce(
                (sum, dateSlot) => sum + (dateSlot.slots?.length || 0), 0
            );
        },
        /**
         * Submit selected one-time slots and close dialog
         * Validates that correct number of slots has been selected
         */
        submitOneTimeSlots() {
            this.slot_msg = false;
            const slotsCount = this.oneTimeSlotCounter();
            const slotsRequired = Math.ceil(this.selectedDuration.hours / 2);

            if (slotsCount === slotsRequired) {
                this.selected_onetime_slots = {};

                // Build selected slots object from one_time_slots
                for (const dateKey in this.one_time_slots) {
                    if (this.one_time_slots[dateKey].slots.length > 0) {
                        this.selected_onetime_slots[dateKey] = {
                            slots: this.one_time_slots[dateKey].slots
                        };
                    }
                }

                this.onetime_dialog = false;
                this.oneTimeSelectionStat = true;
            } else {
                this.slot_msg = true;
            }
        },
        /**
         * Move to next day in slot selection process
         * Saves current slots and moves to next day or closes dialog
         */
        nextSlotSelection() {
            this.slot_msg = false;
            const slotsCount = this.oneTimeSlotCounter();
            const slotsRequired = Math.ceil(this.selectedDuration.hours / 2);

            if (slotsCount !== slotsRequired) {
                this.slot_msg = true;
                return;
            }

            // Save current slots
            for (const dateKey in this.one_time_slots) {
                if (this.one_time_slots[dateKey].slots.length > 0) {
                    this.selected_onetime_slots[dateKey] = {
                        slots: this.one_time_slots[dateKey].slots,
                        day_count: this.currentSlotDay
                    };
                }
            }

            // Check if we've gone through all required days
            if (this.currentSlotDay > this.cleaning_set.length) {
                this.onetime_dialog = false;
                this.oneTimeSelectionStat = true;
            } else {
                // Move to next day
                this.currentSlotDay++;
                if (this.currentSlotDay <= this.cleaning_set.length) {
                    this.oneTimeDateSelected = moment(this.oneTimeDateSelected, 'YYYY-MM-DD')
                        .add(1, 'days')
                        .format('YYYY-MM-DD');
                    this.oneTimeNewDateChange();
                }
            }
        },

        addSlot(slot) {
            if (this.time_slot[this.slotDate].selectedSlot.length == 0) {
                this.time_slot[this.slotDate].selectedSlot.push(slot);
                this.forceRerender();
                this.countSlots();
            } else {
                const nextSlot = slot + 3;
                if (this.time_slot[this.slotDate].selectedSlot.includes(nextSlot)) {
                    if (this.timeSlots[slot].includes(6)) {
                        this.time_slot[this.slotDate].selectedSlot.push(slot);
                        this.forceRerender();
                        this.countSlots();
                    } else {
                    }
                } else {
                    if (slot > 0) {
                        const prevSlot = slot - 3;
                        if (this.timeSlots[prevSlot].includes(6)) {
                            this.time_slot[this.slotDate].selectedSlot.push(slot);
                            this.forceRerender();
                            this.countSlots();
                        } else {
                        }
                    }
                }
            }
        },
        countSlots() {
            this.slotCounter = 0;
            for (var slot in this.time_slot) {
                this.slotCounter =
                    parseInt(this.slotCounter) +
                    parseInt(this.time_slot[slot].selectedSlot.length);
            }
        },
        removeSlot(slot) {
            this.time_slot[this.slotDate].selectedSlot.splice(
                this.time_slot[this.slotDate].selectedSlot.indexOf(slot),
                this.time_slot[this.slotDate].selectedSlot.length
            );
            this.countSlots();
            this.forceRerender();
        },
        updateSize() {
            this.upholsterySize = this.sizeData.filter(size => size.upholstery_type === this.otherService.type)
        },
        findSelectedTotalSize() {
            this.total_size = 0
            this.sofa_size = 0
            this.chair_size = 0
            this.new_kitchen_nocabinet_size = 0
            this.new_kitchen_cabinet_size = 0
            this.old_kitchen_cabinet_size = 0
            this.old_kitchen_nocabinet_size = 0


            for (const j of this.schedule_serviceTypes_selected) {
                const serIndex = j

                if (this.multiServicesBill[serIndex].service == 'Upholstery Cleaning') {
                    for (const bill of this.multiServicesBill[serIndex].bill) {
                        if (bill.section.type == 'SOFA') {
                            this.sofa_size = this.sofa_size + parseInt(bill.section.size.max_size)
                        }
                        if (bill.section.type == 'CURTAIN') {
                            this.chair_size = this.chair_size + parseInt(bill.section.size.max_size)
                        }
                    }
                }
                else if (this.multiServicesBill[serIndex].service == 'Kitchen Cleaning') {
                    for (const bill of this.multiServicesBill[serIndex].bill) {
                        if (bill.section.type == 'old') {
                            if (bill.section.is_cabinet) {
                                this.old_kitchen_cabinet_size = this.old_kitchen_cabinet_size + parseInt(bill.section.size.max_size)
                            }
                            else {
                                this.old_kitchen_nocabinet_size = this.old_kitchen_nocabinet_size + parseInt(bill.section.size.max_size)
                            }
                        }
                        if (bill.section.type == 'new') {
                            if (bill.section.is_cabinet) {
                                this.new_kitchen_cabinet_size = this.new_kitchen_cabinet_size + parseInt(bill.section.size.max_size)
                            }
                            else {
                                this.new_kitchen_nocabinet_size = this.new_kitchen_nocabinet_size + parseInt(bill.section.size.max_size)
                            }
                        }
                    }
                }
                else if (this.multiServicesBill[serIndex].service == 'Kitchen Appliances') {

                }
                else {

                    for (var i = 0; i < this.multiServicesBill[serIndex].bill.length; i++) {
                        this.total_size = 0
                        if (this.multiServicesBill[serIndex].bill[i].section.size) {
                            this.total_size = this.total_size + parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size);
                        }
                    }
                }
            }
        },
        findTotalSize() {
            this.total_size = 0
            this.sofa_size = 0
            this.chair_size = 0
            for (const service of this.multiServicesBill) {
                if (service.service === 'Upholstery Cleaning') {
                    for (const bill of service.bill) {
                        if (bill.section.type === 'SOFA') {
                            this.sofa_size = this.sofa_size + parseInt(bill.section.size.max_size)
                        }
                        if (bill.section.type === 'CURTAIN') {
                            this.chair_size = this.chair_size + parseInt(bill.section.size.max_size)
                        }
                    }
                }
                else if (service.service === 'Kitchen Cleaning') {
                    for (const bill of service.bill) {
                        if (bill.section.type === 'old') {
                            if (bill.is_cabinet) {
                                this.old_kitchen_cabinet_size = this.old_kitchen_cabinet_size + parseInt(bill.section.size.max_size)
                            }
                            else {
                                this.old_kitchen_nocabinet_size = this.old_kitchen_nocabinet_size + parseInt(bill.section.size.max_size)
                            }

                        }
                        if (bill.section.type === 'new') {
                            if (bill.is_cabinet) {
                                this.new_kitchen_cabinet_size = this.new_kitchen_cabinet_size + parseInt(bill.section.size.max_size)
                            }
                            else {
                                this.new_kitchen_nocabinet_size = this.new_kitchen_nocabinet_size + parseInt(bill.section.size.max_size)
                            }
                        }
                    }
                }
                else {
                    for (const bill of service.bill) {
                        this.total_size = this.total_size + parseInt(bill.section.size.max_size)
                    }
                }
            }
            // console.log("total size is "+this.total_size)
        },

        /* ================================================================
            10. SERVICE SELECTION & CATEGORY METHODS
            ================================================================
            Service type selection, categories, sizes, and filtering
        ================================================================ */

        selectService(service) {
            this.serviceChange = false
            this.selectedService = service;
            this.serviceType = service.name;
            this.location_type = ''
            this.area_type = ''
            this.otherServices = [];
            this.billingData = [];
            this.building = [];
            this.no_of_building = 0;
            this.temp_no_of_building = 0;
            this.no_of_floors = [];
            this.no_of_apartments = [];
            this.buildingsCompleted = false
            this.getSize();
            // Watcher on serviceType will call getAddons() automatically

            if (this.selectedService.name == 'Kitchen Cleaning') {
                this.otherService.type = 'old'
            }

            this.serviceChange = true
        },
        getHourly() {

            return (
                ` <div class="sr-service-card m-2 p-2 "   onclick="selectService('Hourly Cleaning',this)">
  <i class="far fa-circle inactive-icon"></i>
  <img src="/static/files/icons/hourly_cleaning.png" class="service-icon"> 
  <div class="text-center pt-2 service-title">
 Hourly Cleaning
</div></div>`)

        },
        selectCategory(item) {
            this.ser_counter++
            this.refresh++
            this.detailedCleaningServices = []
            this.specialCareServices = []
            this.kitchenCleaningServices = []
            this.infectionControlServices = []
            this.selectedCategory = item.service_name

            this.$nextTick(() => {
                const filteredServices = this.services.filter(service => service.service_group_id === item.id);

                if (filteredServices && filteredServices.length > 0) {
                    const firstService = filteredServices[0];
                    this.selectedService = firstService;
                    this.serviceType = firstService.name;
                    this.selectService(firstService);
                    // Watcher will handle getAddons() and getSize() via serviceType change
                }
            });
        },

        selectServiceType(service) {
            
            if (!service || !service.name) {
                console.error("Invalid service object");
                return;
            }

            this.selectedService = service;
            this.serviceType = service.name;
            this.serviceCount++;

            try {
                this.serviceChange = false
                this.selectedService = service;
                this.serviceType = service.name;
                this.location_type = ''
                this.area_type = ''
                this.otherServices = [];
                this.billingData = [];
                this.building = [];
                this.no_of_building = 0;
                this.temp_no_of_building = 0;
                this.no_of_floors = [];
                this.no_of_apartments = [];
                this.buildingsCompleted = false
                this.getSize();
                // Watcher on serviceType will call getAddons() automatically

            } catch (error) {
                console.error("Error getting service size:", error);
            }
        },

        /**
         * Reinitialize the service carousel after content changes
         * This is necessary when switching categories as filteredServices changes
         */
        reinitServiceCarousel() {
            const $carousel = $('#service-carousel');

            // Hide carousel to prevent visual flicker during transition
            $carousel.css({ 'opacity': '0', 'transition': 'opacity 0.1s' });

            // Destroy old carousel instance if it exists
            if ($carousel.hasClass('owl-loaded')) {
                $carousel.trigger('destroy.owl.carousel').removeClass('owl-loaded owl-drag owl-carousel');
                $carousel.find('.owl-stage-outer, .owl-stage, .owl-item, .owl-nav, .owl-dots').remove();
            }

            // Wait for Vue to render new items, then reinitialize
            setTimeout(() => {
                this.$nextTick(() => {
                    const finalItemsCount = $carousel.find('.sr-service-card').length;

                    // Re-initialize carousel if we have items
                    if (finalItemsCount > 0) {
                        $carousel.addClass('owl-carousel').owlCarousel({
                            items: 4,
                            loop: false,
                            margin: 10,
                            nav: true,
                            dots: false,
                            responsive: {
                                0: { items: 1 },
                                600: { items: 2 },
                                1000: { items: 4 }
                            }
                        });

                        // Show carousel again with smooth fade-in
                        setTimeout(() => {
                            $carousel.css('opacity', '1');
                        }, 50);
                    }
                });
            }, 150);
        },

        /**
         * Reinitialize the category carousel after content changes
         */
        reinitCategoryCarousel() {
            const $carousel = $('#category-carousel');

            // Hide carousel to prevent visual flicker during transition
            $carousel.css({ 'opacity': '0', 'transition': 'opacity 0.1s' });

            if ($carousel.hasClass('owl-loaded')) {
                $carousel.trigger('destroy.owl.carousel').removeClass('owl-loaded owl-drag owl-carousel');
                $carousel.find('.owl-stage-outer, .owl-stage, .owl-item, .owl-nav, .owl-dots').remove();
            }

            setTimeout(() => {
                this.$nextTick(() => {
                    const finalItemsCount = $carousel.find('.sr-service-card').length;

                    if (finalItemsCount > 0) {
                        $carousel.addClass('owl-carousel').owlCarousel({
                            items: 4,
                            loop: false,
                            margin: 10,
                            nav: true,
                            dots: false,
                            responsive: {
                                0: { items: 1 },
                                600: { items: 2 },
                                1000: { items: 4 }
                            }
                        });

                        // Show carousel again with smooth fade-in
                        setTimeout(() => {
                            $carousel.css('opacity', '1');
                        }, 50);
                    }
                });
            }, 150);
        },



        /* ================================================================
            12. BOOKING EXECUTION METHODS  
            ================================================================
            Primary booking operations: single, multiple, scheduling
        ================================================================ */

        bookMultipleService() {
            this.submit_loader = true
            const urlSearchParams = new URLSearchParams(window.location.search);
            const params = Object.fromEntries(urlSearchParams.entries());
            this.userid = window.location.href.split('/')[6] // Index 6 correctly extracts user ID from URL in common/staging/booking context
            let posturl = ''
            if (this.scheduleStatus) {
                posturl = '/customer/evaluatorbookingmultiplephase2/together/'

                fetch(this.url + posturl + this.userid + '/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.serviceDetails)
                })
                    .then(response => response.json())
                    .then((data) => {
                        this.submit_loader = false
                        // console.log("booking details is "+response)
                        this.phase2Result = data
                        if (data.success) {
                            this.responseText = 'Booking Successful'
                            this.snackbar = true
                            // this.getBookingDetails(data.booking_id)
                            this.last_image_stat = true
                            this.uploadImages()
                            //window.location.href='/common/makequatation/phase1/'+params.enquiry_id+'/'+params.evaluation_id

                        }
                        else {
                            this.responseText = response.data.Error
                            this.snackbar = true
                        }
                    })
                    .catch((error) => {
                        this.responseText = error
                    });
            }
            else {
                this.seperateMultiBook()
            }
        },
        async seperateMultiBook() {
            const urlSearchParams = new URLSearchParams(window.location.search);
            const params = Object.fromEntries(urlSearchParams.entries());
            this.userid = window.location.href.split('/')[6]
            let posturl = '/customer/evaluatorbookingmultiplephase2/together/'

            for (const sch in this.scheduleGroup) {
                this.submit_loader = true
                let totalCost = 0
                let estimatedCost = 0
                let groupData = {}
                for (let i = 0; i < this.scheduleGroup[sch].length; i++) {
                    const data = this.scheduleGroup[sch]
                    // console.log("service details is"+JSON.stringify(this.serviceDetails))
                    groupData[i] = { ...this.serviceDetails.service_details[data[i]] }
                    totalCost = totalCost + this.serviceDetails.service_details[data[i]].total_cost
                }
                // var res=await this.seperateBookRequest(posturl,totalCost,groupData)
                const res = await fetch(this.url + posturl + this.userid + '/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        estimated_cost: totalCost,
                        total_cost: totalCost,
                        service_details: groupData,
                        shift_availability_check: this.serviceDetails.service_details[0].shift_availability_check
                    })
                })
                    .then(response => response.json())
                    .then((data) => {
                        this.submit_loader = false
                        //  console.log("booking details is "+response)
                        this.phase2Result = data
                        groupData = {}
                        if (data.success) {
                            this.responseText = 'Booking Successful'
                            this.snackbar = true

                            //  console.log("got response")
                            const schedule_keys = Object.keys(this.scheduleGroup)
                            if (sch == this.scheduleGroup[schedule_keys[schedule_keys.length - 1]]) {
                                this.last_image_stat = true
                            }
                            else {
                                this.last_image_stat = false
                            }
                            this.uploadImages()
                            return data

                        }
                        else {
                            this.responseText = data.Error
                            this.snackbar = true
                        }


                    })
                    .catch((error) => {
                        this.responseText = error
                        return error
                    });


            }
        },

        /* This function is deprecated -> keeping it for future purpose*/
        async seperateBookRequest(posturl, totalCost, groupData) {
            fetch(this.url + posturl + this.userid + '/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    estimated_cost: totalCost,
                    total_cost: totalCost,
                    service_details: groupData
                })
            })
                .then(response => response.json())
                .then((data) => {
                    this.submit_loader = false
                    this.phase2Result = response.data
                    groupData = {}
                    if (response.data.success) {
                        this.responseText = 'Booking Successful'
                        this.snackbar = true

                        // console.log("got response")

                        this.uploadImages()
                        return response

                    }
                    else {
                        this.responseText = response.data.Error
                        this.snackbar = true
                    }


                })
                .catch((error) => {
                    this.responseText = error
                    return error
                });
        },
        /* Deprecated function ends here */

        bookCustService() {
            this.userid = window.location.href.split('/')[6]
            const urlSearchParams = new URLSearchParams(window.location.search);
            const params = Object.fromEntries(urlSearchParams.entries());


            fetch(this.url + '/customer/evaluatorbookingmultiplephase2/customer/' + this.userid + '/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.serviceDetails)
            })
                .then(response => response.json())
                .then((data) => {

                    this.phase2Result = data
                    if (data.success) {
                        this.responseText = 'Booking Successful'
                        this.snackbar = true
                        this.last_image_stat = true

                        this.uploadImages()
                    }
                })
                .catch((error) => {
                    this.responseText = error
                });
        },
        async uploadImages() {
            const urlSearchParams = new URLSearchParams(window.location.search);
            const params = Object.fromEntries(urlSearchParams.entries());
            for (const [i, serviceImages] of this.multiServiceImages.entries()) {
                this.submit_loader = true
                const image = new FormData()
                image.append('evaluation_book_id', Object.keys(this.phase2Result.evaluation_book_ids)[i])
                for (const imageData of serviceImages.images) {
                    image.append('media', imageData.file)
                }
                await fetch(this.url + "/customer/bookingmediasave", {
                    method: 'POST',
                    body: image
                })
                    .then(response => response.json())
                    .then((data) => {
                        // this.submit_loader=false

                        if (this.last_image_stat) {
                            window.location.href = '/common/makequatation/phase1/' + params.enquiry_id + '/' + params.evaluation_id
                        }


                    })
                    .catch((error) => {
                        if (this.last_image_stat) {
                            window.location.href = '/common/makequatation/phase1/' + params.enquiry_id + '/' + params.evaluation_id
                        }
                    });

            }

        },
        getBookingDetails(bkid) {
            fetch(this.url + "/customer/bookingphase3?booking_id=" + bkid)
                .then(response => response.json())
                .then((data) => {
                    this.bookingMultiData = data
                    this.udf3 = data.order_details.order_status
                    const order_no = data.order_details.order_no
                    this.gateway_eval = order_no.substring(3, order_no.length) + data.encryption_key
                    this.gateway_price = data.order_details.total_amount


                })
                .catch((error) => {
                });
        },
        async getAddons() {
            this.addons = []
            fetch(this.url + '/customer/ajax/getserviceaddons?service_type=' + this.serviceType)
                .then(response => response.json())
                .then(data => {
                    this.addons = data.service_addons
                    this.parseAddons()
                })
                .catch((error) => {
                })
        },
        findAddons(addon) {

            for (let i = 0; i < this.addons_parsed.length; i++) {
                if (this.addons_parsed[i].details.name == addon) {
                    return i
                }
            }
            return 'not found'
        },
        async parseAddons() {
            this.addons_parsed = []
            for (let i = 0; i < this.addons.length; i++) {
                if (this.addons[i].category) {

                    const add_on_stat = this.findAddons(this.addons[i].name)

                    if (add_on_stat != 'not found') {
                        this.addons_parsed[add_on_stat].size.push({
                            size: this.addons[i].category,
                            max_size: this.addons[i].size,
                            price: this.addons[i].price
                        })
                    }
                    else {


                        this.addons_parsed.push({
                            details: this.addons[i],
                            selected: false,
                            quantity: 0,
                            size: [{
                                size: this.addons[i].category,
                                max_size: this.addons[i].size,
                                price: this.addons[i].price
                            }],
                            selected_size: {}
                        })

                    }
                }
                else {
                    this.addons_parsed.push({
                        details: this.addons[i],
                        selected: false,
                        quantity: 0,

                        size: [],
                        selected_size: {}
                    })
                }


            }


        },
        selectAddons(index) {
            this.addons_parsed[index].selected = true
            this.addons_parsed[index].quantity = 1
        },
        increaseQty(index) {
            this.addons_parsed[index].quantity++
        },
        reduceQty(index) {
            this.addons_parsed[index].quantity--
            if (this.addons_parsed[index].quantity == 0) {
                this.addons_parsed[index].selected = false
            }
        },
        getMultipleSlots() {
            this.slot_loader = true

            // Build service types array from multiServicesBill if schedule_serviceTypes is empty
            let schedule_services = [];

            if (this.schedule_serviceTypes && this.schedule_serviceTypes.length > 0) {
                schedule_services = [...this.schedule_serviceTypes];
            } else {
                // If schedule_serviceTypes is not populated, build from multiServicesBill
                for (const service of this.multiServicesBill) {
                    if (service.service && !schedule_services.includes(service.service)) {
                        schedule_services.push(service.service);
                    }
                }
            }
            if (schedule_services.length === 0) return; // No services to fetch slots for, exit early

            fetch(this.url + "/customer/ajax/getmultipleservicecleaningslotes", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service_types: schedule_services, cleaning_date: this.slotDate, number_of_cleaners: this.selectedDuration.cleaners })
            })
                .then(response => response.json())
                .then((data) => {
                    this.slot_loader = false
                    this.timeSlots = data.slotes;
                    this.parseOneTimeSlots()
                    if (data.Error) {
                        this.errMsg = data['Error']
                    }
                    else {
                        this.errMsg = ''
                    }
                    if (!this.time_slot.hasOwnProperty(this.slotDate)) {
                        this.time_slot[this.slotDate] = {
                            selectedSlot: [],
                        };
                    }

                    this.parseSize();
                })
                .catch((error) => {
                });
        },
        parseOneTimeSlots() {
            this.parsedTimeSlots = []
            this.available_slotes = []
            for (var i in this.timeSlots) {
                if (this.timeSlots[i].includes(2)) {
                    const slotNo = (parseInt(i) + 2) / 2
                    this.available_slotes.push(slotNo)
                    this.parsedTimeSlots.push(this.slotFormat[String(slotNo)])


                }
            }
        },
        getTimeSlots() {
            this.timeSlots = {};
            fetch(this.url + "/customer/ajax/getcleaningslotes?service_type=" +
                this.serviceType +
                "&number_of_cleaners=" +
                this.selectedDuration.cleaners +
                "&cleaning_date=" +
                this.slotDate)
                .then(response => response.json())
                .then((data) => {
                    this.timeSlots = data.slotes;
                    if (!this.time_slot.hasOwnProperty(this.slotDate)) {
                        this.time_slot[this.slotDate] = {
                            selectedSlot: [],
                        };
                    }

                    this.parseSize();
                })
                .catch((error) => {
                });
        },
        getAreaTypes() {
            fetch(this.url + "/customer/ajax/getareatypes")
                .then(response => response.json())
                .then((data) => {
                    this.area_types = data['area_types'];

                })
                .catch((error) => {
                });
        },
        getSize() {
            let service = this.serviceType
            if (service == 'Hourly Cleaning') {
                service = 'General Cleaning'
            }
            fetch(this.url + "/customer/ajax/getservicesizeprice?service_type=" + service)
                .then(response => {
                    if (!response.ok) {
                        console.error('API error:', response.status, response.statusText);
                        throw new Error('API returned status ' + response.status);
                    }
                    return response.json();
                })
                .then((data) => {
                    if (!data || Object.keys(data).length === 0) {
                        this.serviceSize = {};
                    } else {
                        this.serviceSize = data;
                    }
                    this.parseSize();
                    if (this.serviceType == 'Kitchen Cleaning') {
                        this.kitchenTypes = [...new Set(this.sizeData.map(size => size.kitchen_type))];
                        this.otherService.type = this.kitchenTypes[0]
                        this.kitchenTypeFilter();
                    }
                    if (this.serviceType == 'Rope Access') {
                        this.ropeAccessTypes = [...new Set(this.sizeData.map(size => size.rope_access_type))];
                        this.ropeAccessFilter();
                        return;
                    }
                    this.facadeFilter();
                    this.windowFilter();
                })
                .catch((error) => {
                    console.error('Error fetching size data:', error);
                    this.snackbar = true;
                    this.responseText = 'Error loading size options. Please try again.';
                });
        },
        setDuration(hours, cleaners) {

            this.duration.push({
                hours: hours,
                cleaners: cleaners,
            });
        },
        sortDuration() {
            if (this.duration[0].hours < this.duration[1].hours) {
                this.selectDuration(this.duration[0])
            }
            else {
                const temp = this.duration[0]
                this.duration[0] = this.duration[1]
                this.duration[1] = temp
                this.selectDuration(this.duration[0])
            }
        },
        parseSize() {
            this.sizeData = [];
            for (var i in this.serviceSize) {
                this.serviceSize[i]["combinedSize"] =
                    this.serviceSize[i].name +
                    " ( " +
                    this.serviceSize[i].min_size +
                    " sq. m - " +
                    this.serviceSize[i].max_size +
                    " sq. m )";
                this.sizeData.push(this.serviceSize[i]);
            }
            this.serviceSize = {};
        },
        save(date) {
            this.$refs.menu.save(date);
        },

        /* ================================================================
            13. IMAGE MANAGEMENT METHODS
            ================================================================
            Image upload, storage, deletion, and batch processing
        ================================================================ */

        async onImageFileChanged(event) {

            this.ImageDetails.service = this.selectedService.name;
            const file = event.target.files[0]

            const options = {
                maxSizeMB: 1,
                maxWidthOrHeight: 1920,
                useWebWorker: true,
                onProgress: Function(2)
            }
            try {
                const compressedFile = await imageCompression(event.target.files[0], options);


                await this.uploadImgToArray(compressedFile, event.target.files[0].name); // write your own logic
            } catch (error) {
            }


        },
        uploadImgToArray(file, fileName) {
            file.lastModifiedDate = Date.now();

            const converted_file = new File([file], fileName, { lastModified: Date.now() });
            this.ImageDetails.url = URL.createObjectURL(converted_file);
            this.ImageDetails.file = converted_file;
            this.imageData.push(this.ImageDetails);
            this.ImageDetails = {
                file: "",
                url: "",
                service: ""

            };
        },
        deleteImage(imageindex) {
            this.imageData.splice(imageindex, 1);
        },

        /* ================================================================
            15. OTHER SERVICES & ADD-ONS MANAGEMENT
            ================================================================
            Upholstery, Facade, Window, Rope Access configurations
        ================================================================ */

        addNew() {
            this.otherService = {
                material: "",
                color: "",
                size: null,
                type: "",
                age: "",
                stain: false,
                is_cabinet: false,
                stain_reason: "",
                wall_type: "",
                floor_type: "",
                ceiling_type: "",
                residue: false,
                hallway_size: "",
                sides: "",
                stain_age: "",
                height: "",
                keynote_data: [],
                addons: []
            };
            this.parseAddons()
            // if (this.selectedService.name == 'Kitchen Cleaning') {
            //     this.otherService.type = "old"
            //     this.changeKitchen()
            // }

            this.dialog = true;
            this.dialogmsg = "Add New";
            this.dialogStat = true;
            this.building = [];
        },
        facadeFilter() {
            this.facadeSize = []
            if (this.hallway_check) {
                for (let i = 0; i < this.sizeData.length; i++) {
                    if (this.sizeData[i].is_highprice_facade) {
                        this.facadeSize.push(this.sizeData[i])
                    }
                }
            }
            else {

                for (let i = 0; i < this.sizeData.length; i++) {
                    if (!this.sizeData[i].is_highprice_facade) {
                        this.facadeSize.push(this.sizeData[i])
                    }
                }

            }
        },
        windowFilter() {
            this.windowSize = []
            this.otherService.size = {}
            if (this.window_check) {
                for (var i = 0; i < this.sizeData.length; i++) {
                    if (this.sizeData[i].is_highprice_window) {
                        this.windowSize.push(this.sizeData[i])
                    }
                }
            }
            else {

                for (var i = 0; i < this.sizeData.length; i++) {
                    if (!this.sizeData[i].is_highprice_window) {
                        this.windowSize.push(this.sizeData[i])
                    }
                }

            }
        },
        ropeAccessFilter(index = null, floor = null) {

            if (index !== null && floor !== null && this.building[index] && this.building[index].floors[floor]) {
                selectedType = this.building[index].floors[floor].rope_access_type || this.ropeAccessTypes[0];
            } else {
                selectedType = this.ropeAccessTypes[0];
            }
            this.ropeAccessSize = this.sizeData.filter(size => size.rope_access_type === selectedType);
            this.otherService.size = {}
        },
        kitchenTypeFilter() {
            this.sizeFilteredData = this.sizeData.filter(size => size.kitchen_type === this.otherService.type);
            this.otherService.size = {}
        },
        editItem(a, b) {
            this.edit_item = true
            this.add_new_kitchen = false
            this.addons_parsed = [...a.addons]

            this.dialog = true;
            this.dialogmsg = "Edit";
            this.dialogStat = false;


            (this.otherService = {
                material: a.material,
                keynote_data: a.keynote_data,
                color: a.color,
                size: a.size,
                type: a.type,
                age: a.age,
                stain: a.stain,
                stain_reason: a.stain_reason.split(','),
                wall_type: a.wall_type,
                floor_type: a.floor_type,
                ceiling_type: a.ceiling_type,
                residue: a.residue,
                hallway_size: a.hallway_size,
                sides: a.sides,
                stain_age: a.stain_age,
                section_cost: a.section_cost,
                height: a.height,
                addons: a.addons,
                is_cabinet: a.is_cabinet

            }),

                this.currentItem = b;
        },
        async saveChanges() {
            this.edit_item = false
            await this.calcSize()

            if (this.otherService.stain_reason.length > 0) {
                this.otherService.stain_reason = this.otherService.stain_reason.join()
            }
            this.otherService.sectiononly_cost = this.otherService.size ? this.otherService.size.cost : 0
            this.otherService.section_cost = (this.otherService.size ? this.otherService.size.cost : 0) + this.findAddonCost()
            this.otherServices[this.currentItem] = { ...this.otherService };
            this.billingData[this.currentItem].section_cost = this.otherService.section_cost
            this.billingData[this.currentItem].section_net_cost = this.otherService.section_cost
            this.billingData[this.currentItem].sectiononly_cost = this.otherService.sectiononly_cost
            this.billingData[this.currentItem].sectiononly_net_cost = this.otherService.sectiononly_cost
            this.billingData[this.currentItem].section = { ...this.otherService }
            this.dialog = false;
            this.otherService = {
                material: "",
                addons: [],
                color: "",
                size: {},
                type: "",
                age: "",
                stain: false,
                stain_reason: "",
                wall_type: "",
                floor_type: "",
                ceiling_type: "",
                residue: false,
                is_cabinet: false,
                hallway_size: "",
                sides: "",
                stain_age: "",
                height: "",
                keynote_data: [],
                section_cost: 0,
                sectiononly_cost: 0
            },
                this.recalcCost();
        },
        calcSize() {
            let sizeFound = false
            let max_size_data = []
            let max_size_val = []
            if (this.serviceType == "Upholstery Cleaning") {

                if (this.otherService.type == "SOFA") {
                    for (let item = 0; item < this.sizeData.length; item++) {
                        if (this.sizeData[item].upholstery_type == "SOFA") {
                            for (let item = 0; item < this.sizeData.length; item++) {

                                if (this.sizeData[item].upholstery_type == "SOFA") {
                                    max_size_data.push(this.sizeData[item].max_size)
                                    max_size_val.push(this.sizeData[item])
                                    if (
                                        this.otherService.size >= this.sizeData[item].min_size &&
                                        this.otherService.size <= this.sizeData[item].max_size
                                    ) {
                                        this.otherService.size = {
                                            name: this.otherService.size + ' Seater',
                                            cost: this.sizeData[item].cost,
                                            combinedSize: this.otherService.size + ' Seater',
                                            upholstery_type: "SOFA",
                                            min_size: this.otherService.size,
                                            max_size: this.otherService.size
                                        };
                                        sizeFound = true
                                    }
                                }
                            }
                            const max_val = Math.max(...max_size_data)
                            let left_size = 0
                            if (!sizeFound && this.otherService.size > 0) {
                                left_size = this.otherService.size - max_val

                                for (let j = 0; j < max_size_val.length; j++) {
                                    if (max_size_val[j].max_size == max_val) {
                                        const new_cost = this.otherService.size * max_size_val[j].unit_price
                                        const current_cost = max_size_val[j].cost + new_cost
                                        const size = this.otherService.size
                                        this.otherService.size = {
                                            name: size + ' Seater',
                                            cost: new_cost,
                                            max_size: size,
                                            min_size: size,
                                            upholstery_type: "SOFA",
                                            combinedSize: size + ' Seater'

                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                if (this.otherService.type == "CURTAIN") {
                    for (let item = 0; item < this.sizeData.length; item++) {
                        if (this.sizeData[item].upholstery_type == "CURTAIN") {
                            if (
                                this.otherService.size >= this.sizeData[item].min_size &&
                                this.otherService.size <= this.sizeData[item].max_size
                            ) {
                                this.otherService.size = this.sizeData[item];
                            }
                        }
                    }
                }
            }
        },
        async addOtherService() {
            if (this.$refs.otherServiceForm.validate()) {

                await this.calcSize();
                this.otherService.section_cost = (this.otherService.size ? this.otherService.size.cost : 0) + this.findAddonCost()
                this.otherService.sectiononly_cost = this.otherService.size ? this.otherService.size.cost : 0
                if (this.otherService.stain_reason.length > 0) {
                    this.otherService.stain_reason = this.otherService.stain_reason.join()
                }

                // Format addons with proper name and price fields
                if (this.addons_parsed && this.addons_parsed.length > 0) {
                    const formattedAddons = [];
                    for (const addon of this.addons_parsed) {
                        if (addon.selected) {
                            let addonPrice = 0;
                            let selectedSize = addon.selected_size || {};

                            if (selectedSize && selectedSize.price) {
                                addonPrice = parseFloat(selectedSize.price);
                            } else if (addon.size && addon.size.length > 0 && addon.size[0].price) {
                                addonPrice = parseFloat(addon.size[0].price) || 0;
                                selectedSize = addon.size[0];
                            } else if (addon.details && addon.details.price) {
                                addonPrice = parseFloat(addon.details.price);
                            }

                            if (addonPrice > 0 && addon.quantity > 0) {
                                formattedAddons.push({
                                    id: addon.details?.id || null,
                                    name: addon.details?.name || 'Addon',
                                    quantity: addon.quantity || 1,
                                    unit_price: addonPrice,
                                    total_price: (addonPrice * (addon.quantity || 1)),
                                    selected: true
                                });
                            }
                        }
                    }
                    this.otherService.addons = formattedAddons;
                }

                this.otherServices.push(this.otherService);
                if (this.serviceType == 'Upholstery Cleaning') {
                    this.billingData.push({
                        name: this.serviceType + " - " + this.otherService.type,
                        section_name: this.serviceType + " - " + this.otherService.type,
                        section: this.otherService,
                        section_cost: this.otherService.section_cost,
                        section_net_cost: this.otherService.section_cost,

                        sectiononly_cost: this.otherService.sectiononly_cost,
                        sectiononly_net_cost: this.otherService.sectiononly_cost
                    });
                }
                else {
                    this.billingData.push({
                        name: this.serviceType,
                        section_name: this.serviceType,
                        section: this.otherService,
                        section_cost: this.otherService.section_cost,
                        section_net_cost: this.otherService.section_cost,
                        sectiononly_cost: this.otherService.sectiononly_cost,
                        sectiononly_net_cost: this.otherService.sectiononly_cost
                    });
                }

                this.otherService = {
                    material: "",
                    color: "",
                    size: "",
                    type: "old",
                    is_cabinet: false,
                    age: "",
                    stain: false,
                    stain_reason: "",
                    keynote_data: [],
                    wall_type: "",
                    floor_type: "",
                    ceiling_type: "",
                    residue: false,
                    hallway_size: "",
                    sides: "",
                    stain_age: "",
                    section_cost: null,
                    sectiononly_cost: null,
                    addons: []
                };
                this.parseAddons()
                this.dialog = false;
            }
            this.findTempcost()
        },
        async addOtherServiceDialog() {
            if (this.$refs.otherServiceDialogForm.validate()) {

                await this.calcSize();
                this.otherService.section_cost = (this.otherService.size ? this.otherService.size.cost : 0) + this.findAddonCost()
                this.otherService.sectiononly_cost = this.otherService.size ? this.otherService.size.cost : 0
                if (this.otherService.stain_reason.length > 0) {
                    this.otherService.stain_reason = this.otherService.stain_reason.join()
                }

                // Format addons with proper name and price fields
                if (this.addons_parsed && this.addons_parsed.length > 0) {
                    const formattedAddons = [];
                    for (const addon of this.addons_parsed) {
                        if (addon.selected) {
                            let addonPrice = 0;
                            let selectedSize = addon.selected_size || {};

                            if (selectedSize && selectedSize.price) {
                                addonPrice = parseFloat(selectedSize.price);
                            } else if (addon.size && addon.size.length > 0 && addon.size[0].price) {
                                addonPrice = parseFloat(addon.size[0].price) || 0;
                                selectedSize = addon.size[0];
                            } else if (addon.details && addon.details.price) {
                                addonPrice = parseFloat(addon.details.price);
                            }

                            if (addonPrice > 0 && addon.quantity > 0) {
                                formattedAddons.push({
                                    id: addon.details?.id || null,
                                    name: addon.details?.name || 'Addon',
                                    quantity: addon.quantity || 1,
                                    unit_price: addonPrice,
                                    total_price: (addonPrice * (addon.quantity || 1)),
                                    selected: true
                                });
                            }
                        }
                    }
                    this.otherService.addons = formattedAddons;
                }

                this.otherServices.push(this.otherService);
                if (this.serviceType == 'Upholstery Cleaning') {
                    this.billingData.push({
                        name: this.serviceType + " - " + this.otherService.type,
                        section_name: this.serviceType + " - " + this.otherService.type,
                        section: this.otherService,
                        sectiononly_cost: this.otherService.sectiononly_cost,
                        sectiononly_net_cost: this.otherService.sectiononly_cost,
                        section_cost: this.otherService.section_cost,
                        section_net_cost: this.otherService.section_cost
                    });
                }
                else {
                    this.billingData.push({
                        name: this.serviceType,
                        section_name: this.serviceType,
                        section: this.otherService,
                        sectiononly_cost: this.otherService.sectiononly_cost,
                        section_cost: this.otherService.section_cost,
                        section_net_cost: this.otherService.section_cost
                    });
                }


                this.otherService = {
                    material: "",
                    color: "",
                    size: "",
                    type: "",
                    age: "",
                    stain: false,
                    stain_reason: "",
                    wall_type: "",
                    floor_type: "",
                    ceiling_type: "",
                    is_cabinet: false,
                    residue: false,
                    hallway_size: "",
                    sides: "",
                    stain_age: "",
                    section_cost: null,
                    section_net_cost: null,
                    sectiononly_cost: null,
                    sectiononly_net_cost: null,
                    keynote_data: []
                };
                this.dialog = false;
            }
            this.findTempcost()
        },
        recalcCost() {
            this.totalCost = 0;
            for (var i = 0; i < this.billingData.length; i++) {
                this.totalCost = this.totalCost + this.billingData[i].section.section_cost
            }
        },
        findServiceCost() {

            for (var i = 0; i < this.multiServicesBill.length; i++) {
                let servcost = 0;
                for (var j = 0; j < this.multiServicesBill[i].bill.length; j++) {
                    let itemCost = parseFloat(this.multiServicesBill[i].bill[j].section_cost) || 0;
                    servcost = servcost + itemCost;
                }
                this.multiServicesBill[i]['total_cost'] = servcost;
            }

        },

        deleteItem(a) {
            this.otherServices.splice(a, 1);
            this.billingData.splice(a, 1)
            this.recalcCost()
        },

        /* ================================================================
            14. TAB NAVIGATION & UI METHODS
            ================================================================
            Navigate between tabs: Services, Schedule, Cart, Payment
        ================================================================ */

        goToServices() {


            this.activeTab = 'Services'

            // Show carousel navigation arrows
            $('.owl-nav').show();

            setTimeout(function () {

                app.reinitCat()
                app.selectCategory('Detailed Cleaning')
            }, 500);


            $('#tab-1').click()

        },
        /**
         * Navigate to Schedule tab and prepare scheduling interface
         * Initializes scheduler if needed and calculates service types
         */
        goToSchedule() {
            // Set current service if hourly cleaning is selected
            this.current_service = this.is_hourly
                ? this.multiServicesBill[this.schedule_serviceTypes_selected[0]].service
                : '';

            if (!this.editScheduleStat) {
                this.resetScheduler();
            }

            this.activeTab = 'Schedule';
            this.currentPageTitle = 'Schedule';

            // Hide carousel navigation arrows in Schedule tab
            $('.owl-nav').hide();

            // Always populate schedule_serviceTypes from multiServicesBill
            // This ensures Kitchen Cleaning and other services get duration options
            if (!this.editScheduleStat) {
                this.schedule_serviceTypes_selected = this.multiServicesBill.map((_, i) => i)
            }

            this.findSelectedTotalSize();
            this.calcSelectedServices();
            this.newdurationcalculation();

            // Set subscription policy for hourly cleaning
            if (this.current_service === 'Hourly Cleaning') {
                this.cleaningPolicy = 'Subscription';
            }
        },
        /**
         * Check if schedule edit is allowed
         * @returns {boolean} True if edit is allowed (no schedule details or data empty)
         */
        checkEditSchedule() {
            if (Object.keys(this.editScheduleData).length === 0) {
                return true;
            }
            return Object.keys(this.editScheduleData.schedule_details).length === 0;
        },
        /**
         * Navigate to Payment/Billing tab
         */
        goToBilling() {
            this.activeTab = 'Payment Method';

            // Hide carousel navigation arrows in Payment Method tab
            $('.owl-nav').hide();

            this.arrangeData();
        },
        /**
         * Add more services and navigate back to Services tab
         */
        addMoreService() {
            reinit();
            this.serviceCount++;
            this.activeTab = 'Services';

            // Show carousel navigation arrows
            $('.owl-nav').show();
        },
        /**
         * Prepare billing entry for Kitchen Appliances (addon-only service).
         * Has no size/area cost — pricing is purely from selected addons.
         * Call this before goToCart() when serviceType is 'Kitchen Appliances'.
         */
        prepareBilling() {
            const addonCost = this.findAddonCost()
            
            // Format addons same way as addOtherService()
            const formattedAddons = [];
            for (const addon of this.addons_parsed) {
                if (addon.selected) {
                    let addonPrice = 0;
                    let selectedSize = addon.selected_size || {};

                    if (selectedSize && selectedSize.price) {
                        addonPrice = parseFloat(selectedSize.price);
                    } else if (addon.size && addon.size.length > 0 && addon.size[0].price) {
                        addonPrice = parseFloat(addon.size[0].price) || 0;
                        selectedSize = addon.size[0];
                    } else if (addon.details && addon.details.price) {
                        addonPrice = parseFloat(addon.details.price);
                    }

                    if (addonPrice > 0 && addon.quantity > 0) {
                        formattedAddons.push({
                            id: addon.details?.id || null,
                            name: addon.details?.name || 'Addon',
                            quantity: addon.quantity || 1,
                            unit_price: addonPrice,
                            total_price: (addonPrice * (addon.quantity || 1)),
                            selected: true
                        });
                    }
                }
            }
            
            const otherService = {
                material: "",
                addons: formattedAddons,
                color: "",
                size: {},
                section_cost: addonCost,
                sectiononly_cost: 0,
                type: "",
                age: "",
                stain: false,
                stain_reason: "",
                wall_type: "",
                floor_type: "",
                ceiling_type: "",
                residue: false,
                is_cabinet: false,
                hallway_size: "",
                sides: "",
                stain_age: "",
                height: "",
                keynote_data: []
            }
            this.billingData.push({
                name: this.serviceType,
                section_name: this.serviceType,
                section: otherService,
                section_cost: addonCost,
                section_net_cost: addonCost,
                sectiononly_cost: 0,
                sectiononly_net_cost: 0
            })
            // 
        },
        /**
         * Zero out all billing costs for Hourly Cleaning.
         * Pricing for hourly is handled separately at the scheduling level.
         * Call this before goToCart() when serviceType is 'Hourly Cleaning'.
         */
        prepareHourlyCleaningBilling() {
            for (var b = 0; b < this.billingData.length; b++) {
                this.billingData[b].section_net_cost = 0
                this.billingData[b].section_cost = 0
                this.billingData[b].sectiononly_net_cost = 0
                this.billingData[b].sectiononly_cost = 0
            }
        },
        /**
         * Entry point for cart navigation.
         * Calls the appropriate billing preparation method for special service types
         * before delegating to goToCart().
         */
        handleGoToCart() {
            if (this.serviceType === 'Hourly Cleaning') {
                this.prepareHourlyCleaningBilling()
            } else {
                this.prepareBilling()
            }
            this.goToCart()
        },
        goToCart() {
            var sampleServicesBill = {
                service: this.serviceType,
                bill: [],
                serviceNo: this.serviceCount,
                area_type: this.area_type,
                location_type: this.location_type,
                evaluator_note: this.evaluator_note,
                schedule_details: {},
                cleaners: null,
                shift_availability_check: true
            }

            this.serviceTypes.push(this.serviceType)

            this.multiServiceImages.push({ service: this.selectedService.name, images: this.imageData })
            this.imageData = []
            sampleServicesBill.bill = [...this.billingData];

            this.multiServicesBill.push(sampleServicesBill)
            this.activeTab = 'Cart'
            window.scrollTo(0, 0);
            sampleServicesBill = {
                service: '',
                bill: [],
                serviceNo: '',
                area_type: '',
                location_type: '',
                evaluator_note: ''
            }
            this.area_type = ''
            this.location_type = ''
            this.evaluator_note = ''
            this.billingData = []
            this.otherServices = []
            this.otherService = {
                material: "",
                addons: [],
                color: "",
                size: {},
                section_cost: 0,
                sectiononly_cost: 0,
                type: "",
                age: "",
                stain: false,
                stain_reason: "",
                wall_type: "",
                floor_type: "",
                ceiling_type: "",
                residue: false,
                is_cabinet: false,
                hallway_size: "",
                sides: "",
                stain_age: "",
                height: "",
                keynote_data: []
            },
                this.building = []
            this.no_of_apartments = [];

            this.buildingsCompleted = false
            this.serviceData.service_details.location_type = ''
            this.serviceData.service_details.area_type = ''
            this.e = { building: [] }
            this.no_of_building = 0
            this.temp_no_of_building = 0
            this.no_of_floors = []
            this.calcTotal()
            //this.findTotalSize()
            this.findSelectedTotalSize()
            this.findServiceCost()
            this.tempCost = 0
            this.schedule_serviceTypes_selected = []
            this.schedule_serviceTypes = []
            //  this.durationcalculation();
            if (this.checkIsHourly()) {
                this.scheduleStat = false
            }
            else {
                this.scheduleStat = true
            }
            // this.parseAddons();

        },
        hourlySelection() {
            if (this.is_hourly) {
                const latest_cleaning = this.schedule_serviceTypes_selected[this.schedule_serviceTypes_selected.length - 1]

                this.schedule_serviceTypes_selected = []
                if (latest_cleaning != undefined) {
                    this.schedule_serviceTypes_selected.push(latest_cleaning)
                }
            }
        },
        selectServ(elem) {
            this.billingData = [];
            this.tempCost = 0
            this.serviceType = elem;
            this.serviceSection.service_type = this.serviceType;
            this.otherServices = [];
            this.no_of_apartments = [];
            this.no_of_floors = [];
            this.no_of_building = 0;
            this.temp_no_of_building = 0
            this.otherService = {
                material: "",
                color: "",
                size: "",
                type: "",
                age: "",
                stain: false,
                is_cabinet: false,
                addons: [],
                stain_reason: "",
                wall_type: "",
                floor_type: "",
                ceiling_type: "",
                residue: false,
                keynote_data: [],
                hallway_size: "",
                sides: "",

            };
            this.e = {
                building: [],
            };
        },
        addSectionFloor(section) {
            this.serviceSection.sections[section] = {
                size: "",
            };
        },

        /* ================================================================
            16. PROPERTY STRUCTURE SETUP METHODS
            ================================================================
            Initialize and configure Buildings, Floors, Apartments hierarchy
        ================================================================ */

        setBuilding() {

            if (this.no_of_floors.length > 0) {

                this.building_warning = true
            }
            else {
                this.no_of_building = this.temp_no_of_building

                this.valid = []
                this.building = []
                this.e.building = []
                this.no_of_floors = []
                this.reset_floor = false
                this.reset_building = false
                for (var i = 0; i < this.no_of_building; i++) {
                    this.building.push({
                        floors: [],
                        completed: false
                    });
                    this.e.building.push({
                        floors: [],
                        e: 1,
                    });
                    this.no_of_floors.push("")
                    this.valid.push({ floors: [] })
                }

                this.reset_floor = true
                this.reset_building = true
            }

        },
        setFloors(building) {
            this.building[building - 1].floors = [];
            this.valid[building - 1].floors = [];
            this.e.building[building - 1].e = 1;
            for (var i = 0; i < this.no_of_floors[building - 1]; i++) {
                this.building[building - 1].floors.push({
                    section_name: "",
                    size: null,
                    floor_type: '',
                    wall_type: "",
                    ceiling_type: "",
                    cement_residue: false,
                    section_cost: "",
                    section_net_cost: "",
                    keynotes: {},
                    apartment: false,
                    apartments: [],
                    kitchen: false,
                    kitchens: [],
                    keynote_data: [],
                    completed: false,
                    paint_residue: false,
                    upholsteries: ["Sofa", ""],
                    rope_access_type: null,
                    sides: null


                });
                if (this.serviceType === 'Rope Access') {
                    this.building[building - 1].floors[i].rope_access_type = "Skyline";
                }
                this.e.building[building - 1].floors.push({
                    floors: [],
                    e: 1,
                });
                this.valid[building - 1].floors.push(false)
            }
        },
        setApartments(building, floor) {
            this.building[building - 1].floors[floor - 1].apartments = [];
            this.e.building[building - 1].floors[floor - 1].e = 1;
            for (
                let i = 0;
                i < this.building[building - 1].floors[floor - 1].no_of_apartments;
                i++
            ) {
                this.building[building - 1].floors[floor - 1].apartments.push({
                    section_name: "",
                    size: null,
                    completed: false,
                    wall_type: "",
                    floor_type: "",
                    ceiling_type: "",
                    cement_residue: false,
                    paint_residue: false,
                    section_cost: "",
                    section_net_cost: "",
                    no_of_rooms: "",
                    no_of_bathrooms: "",
                    no_of_windows: "",
                    keynote_data: [],
                    kitchen: false,
                    kitchens: [],
                    keynotes: {},
                    rope_access_type: null,
                    sides: null
                });
            }
        },
        hourlyCleaningChange() {
            this.hourly_slots = false
            this.hourly_cleaning.hourly_duration = parseInt(this.hourly_cleaning.hourly_duration)
            this.selectedDuration.cleaners = parseInt(this.hourly_cleaning.cleaners)
            if ((parseInt(this.hourly_cleaning.hourly_duration) % 2) != 0) {
                this.selectedDuration.hours = parseInt(this.hourly_cleaning.hourly_duration) + 1
                this.hourly_cleaning.duration = parseInt(this.hourly_cleaning.hourly_duration) + 1
            }
            else {
                this.selectedDuration.hours = parseInt(this.hourly_cleaning.hourly_duration)
                this.hourly_cleaning.duration = parseInt(this.hourly_cleaning.hourly_duration)
            }
            this.selectedDuration.slots = parseInt(this.selectedDuration.hours) / 2

            this.hourly_slots = false
            this.calcSlots()
            this.hourly_slots = true
        },
        selectDuration(duration) {
            duration.slots = duration.hours / 2;
            this.selectedDuration = duration;
            this.resetOneTime()
            this.calcSlots()
            this.getMultipleSlots();
        },
        /**
         * Format selected date from YYYY-MM-DD to DD-MM-YYYY format
         * Fetches slots if all required fields are selected
         */
        formatDate() {
            const [year, month, day] = this.dateSelected.split('-');
            this.slotDate = `${day}-${month}-${year}`;

            // Call getMultipleSlots when we have date and cleaners
            // Works for both single and multiple service scheduling
            if (this.selectedDuration.cleaners && this.slotDate) {
                this.getMultipleSlots();
            }
        },
        /**
         * Check if all buildings are marked as completed
         * @returns {boolean} True if all buildings have completed status
         */
        buildingCompleteChecker() {
            return this.building.every(bldg => bldg.completed);
        },
        /**
         * Check if all floors in a building are marked as completed
         * @param {number} building - Building index
         * @returns {boolean} True if all floors are completed
         */
        floorCompleteChecker(building) {
            return this.building[building].floors.every(floor => floor.completed);
        },
        /**
         * Check if all apartments in a floor are marked as completed
         * @param {number} building - Building index
         * @param {number} floor - Floor index
         * @returns {boolean} True if all apartments are completed
         */
        apartmentCompleteChecker(building, floor) {
            return this.building[building].floors[floor].apartments.every(apt => apt.completed);
        },
        /**
         * Navigate to next tab in building structure with validation
         * @param {number} build - Building number (1-indexed)
         */
        nextTab(build) {
            this.floor_msg = false;
            this.building_msg = false;

            // Check if all floors in current building are completed
            if (!this.floorCompleteChecker(build - 1)) {
                this.floor_msg = true;
                return;
            }

            this.cat_counter = this.cat_counter + 1;

            // Check if this is the last building
            if (build == this.no_of_building) {
                if (this.buildingCompleteChecker()) {
                    this.buildingsCompleted = true;
                } else {
                    this.building_msg = true;
                }
            } else {
                // Move to next tab
                document.querySelector(`#tab${build + 1}`)?.click();
            }
        },

        /**
         * Distribute hours across multiple days in split view
         * Adjusts hours per day based on fixed/variable days
         * @param {number} index - Day index being modified
         */
        changeDuration(index) {
            let currentTotal = 0;
            let balCounter = 0;
            let lastDay = 0;
            this.splitData[index].fixed = true;
            for (let i = 0; i < this.splitData.length; i++) {
                currentTotal = currentTotal + parseInt(this.splitData[i].hours);
            }

            let balance = parseInt(this.selectedDuration) - currentTotal;
            if (balance > 0) {
                for (let j = 0; j < this.splitData.length; j++) {
                    if (!this.splitData[j].fixed) {
                        for (let k = 0; k < balance; k++) {
                            if (parseInt(this.splitData[j].hours) < 10) {
                                this.splitData[j].hours = parseInt(this.splitData[j].hours) + 1;

                                if (this.splitData[j].hours >= 10) {
                                    this.splitData[j].maxVal = 12;
                                } else {
                                    this.splitData[j].maxVal = 12;
                                }
                                balCounter = balCounter + 1;
                                break;
                            }
                        }
                    }
                }

                let balanceamount = balance - balCounter;
                if (balanceamount > 0) {
                    let fullDays = 0;
                    let lastDayHour = 0;
                    let days = 0;
                    lastDay = this.splitData.length;
                    if (balanceamount > 10) {
                        days = balanceamount / 10;
                        fullDays = Math.floor(days);
                        lastDayHour = days.toString().split(".")[1];
                        for (let i = 0; i < fullDays; i++) {
                            this.splitData.push({
                                name: "Day " + (lastDay + 1),
                                hours: "10",
                                maxVal: "12",
                                fixed: false,
                            });
                            lastDay = lastDay + 1;
                        }
                        if (lastDayHour > 0) {
                            this.splitData.push({
                                name: "Day " + lastDay,
                                hours: lastDayHour,
                                maxVal: "12",
                                fixed: false,
                            });
                        }
                    } else {
                        this.splitData.push({
                            name: "Day " + lastDay,
                            hours: balanceamount,
                            maxVal: "12",
                            fixed: false,
                        });
                    }
                }
            } else {
                if (balance < 0) {
                    let negBalCounter = 0;
                    for (let j = 0; j < this.splitData.length; j++) {
                        if (!this.splitData[j].fixed) {
                            for (let k = 0; k < -1 * balance; k++) {
                                if (parseInt(this.splitData[j].hours) > 0) {
                                    this.splitData[j].hours =
                                        parseInt(this.splitData[j].hours) - 1;
                                    if (this.splitData[j].hours >= 10) {
                                        this.splitData[j].maxVal = 12;
                                    } else {
                                        this.splitData[j].maxVal = 12;
                                    }
                                    negBalCounter = negBalCounter + 1;
                                }
                            }
                        }
                        if (negBalCounter == -1 * balance) {
                            break;
                        } else {
                            if (negBalCounter == 0 && -1 * balance != 0) {
                                for (let m = 0; m < -1 * balance; m++) {
                                    if (parseInt(this.splitData[j].hours) > 0 && j != index) {
                                        this.splitData[j].hours =
                                            parseInt(this.splitData[j].hours) - 1;
                                        if (this.splitData[j].hours >= 10) {
                                            this.splitData[j].maxVal = 12;
                                        } else {
                                            this.splitData[j].maxVal = 12;
                                        }
                                        negBalCounter = negBalCounter + 1;
                                    }
                                }
                            }
                        }
                    }
                    if (balance < 0) {
                        for (let i = 0; i < this.splitData.length; i++) {
                            if (parseInt(this.splitData[i].hours) == 0) {
                                this.splitData.splice(i, 1);
                            }
                        }
                    }
                }
            }
        },
        parseSize() {
            this.sizeData = [];
            for (var i in this.serviceSize) {
                if (this.serviceType == 'Upholstery Cleaning') {
                    this.serviceSize[i]["combinedSize"] =
                        this.serviceSize[i].name +
                        "( " +
                        this.serviceSize[i].min_size +
                        " Seater - " +
                        this.serviceSize[i].max_size +
                        " Seater )";
                    this.sizeData.push(this.serviceSize[i]);

                }
                else {
                    this.serviceSize[i]["combinedSize"] =
                        this.serviceSize[i].name +
                        "( " +
                        this.serviceSize[i].min_size +
                        " sq. m - " +
                        this.serviceSize[i].max_size +
                        " sq. m )";
                    this.sizeData.push(this.serviceSize[i]);
                }
            }
        },
        checkBillingData(building, floor) {
            this.billingDataIndex = null
            let itemFound = false;
            for (let i = 0; i < this.billingData.length; i++) {
                if (
                    this.billingData[i].name ==
                    "Building " +
                    building +
                    " Floor " +
                    floor
                ) {
                    itemFound = true;
                    this.billingDataIndex = i
                    break
                }
            }
            return itemFound
        },
        findBillingDataIndex(building, floor) {
            this.billingDataIndex = null
            let itemFound = false;
            for (let i = 0; i < this.billingData.length; i++) {
                if (
                    this.billingData[i].name ==
                    "Building " +
                    building +
                    " Floor " +
                    floor
                ) {
                    itemFound = true;
                    return i
                }
            }

        },
        checkBillingApartmentData(building, floor, apartment) {
            this.billingDataIndex = null
            let itemFound = false;
            for (let i = 0; i < this.billingData.length; i++) {
                if (
                    this.billingData[i].name ==
                    "Building " +
                    building +
                    " Floor " +
                    floor +
                    " Apartment " +
                    (apartment + 1)
                ) {
                    itemFound = true;
                    this.billingDataIndex = i
                    break
                }
            }
            return itemFound
        },
        findBillingApartmentDataIndex(building, floor, apartment) {
            this.billingDataIndex = null
            let itemFound = false;
            for (let i = 0; i < this.billingData.length; i++) {
                if (
                    this.billingData[i].name ==
                    "Building " +
                    building +
                    " Floor " +
                    floor +
                    " Apartment " +
                    (apartment + 1)
                ) {
                    itemFound = true;
                    return i
                }
            }

        },
        nextApartment(building, floor, apartment) {
            //this.$refs.apartmentForm[0].validate()
            if (this.$refs['building-' + building + 'floor-' + floor + 'apartment-' + apartment][0].validate()) {


                this.building[building].floors[floor].apartments[apartment].section_cost = 0
                this.e.building[building].floors[floor].e = apartment + 2;
                this.building[building].floors[floor].apartments[
                    apartment
                ].completed = true;
                let itemFound = false;
                for (let i = 0; i < this.billingData.length; i++) {
                    if (
                        this.billingData[i].name ==
                        "Building " +
                        (building + 1) +
                        " Floor " +
                        (floor + 1) +
                        " Apartment " +
                        (apartment + 1)
                    ) {
                        itemFound = true;
                        this.billingData[i].section = this.building[building].floors[
                            floor
                        ].apartments[apartment];
                    }
                }
                if (!itemFound) {
                    this.building[building].floors[floor].apartments[apartment].section_cost = this.building[building].floors[floor].apartments[apartment].size ? this.building[building].floors[floor].apartments[apartment].size.cost : 0
                    this.building[building].floors[floor].apartments[apartment].section_net_cost = this.building[building].floors[floor].apartments[apartment].section_cost
                    if (this.building[building].floors[floor].apartments[apartment].kitchen) {

                        for (let k = 0; k < this.building[building].floors[floor].apartments[apartment].kitchens.length; k++) {
                            if (this.building[building].floors[floor].apartments[apartment].kitchens[k].type == 'old') {
                                this.building[building].floors[floor].apartments[apartment].section_net_cost = this.building[building].floors[floor].apartments[apartment].section_net_cost + (this.building[building].floors[floor].apartments[apartment].kitchens[k].size ? this.building[building].floors[floor].apartments[apartment].kitchens[k].size.cost : 0)
                            }
                            if (this.building[building].floors[floor].apartments[apartment].kitchens[k].type == 'new' && this.serviceType != 'General Cleaning') {
                                this.building[building].floors[floor].apartments[apartment].section_net_cost = this.building[building].floors[floor].apartments[apartment].section_net_cost + (this.building[building].floors[floor].apartments[apartment].kitchens[k].size ? this.building[building].floors[floor].apartments[apartment].kitchens[k].size.cost : 0)
                            }


                        }
                    }

                    this.billingData.push({
                        name:
                            "Building " +
                            (building + 1) +
                            " Floor " +
                            (floor + 1) +
                            " Apartment " +
                            (apartment + 1),
                        section_name: "Building " +
                            (building + 1) +
                            " Floor " +
                            (floor + 1) +
                            " Apartment " +
                            (apartment + 1),
                        section: this.building[building].floors[floor].apartments[apartment],
                        section_cost: this.building[building].floors[floor].apartments[apartment].section_net_cost,
                        section_net_cost: this.building[building].floors[floor].apartments[apartment].section_net_cost,
                        sectiononly_cost: this.building[building].floors[floor].apartments[apartment].size ? this.building[building].floors[floor].apartments[apartment].size.cost : 0,
                        sectiononly_net_cost: this.building[building].floors[floor].apartments[apartment].size ? this.building[building].floors[floor].apartments[apartment].size.cost : 0,
                    });
                }
                if (apartment == (parseInt(this.building[building].floors[floor].no_of_apartments) - 1)) {
                    this.building[building].floors[floor].completed = true
                }


                this.recalcApartmentPrice(building, floor, apartment);
                this.findTempcost()
            }

        },
        findTempcost() {
            this.tempCost = 0
            for (var i = 0; i < this.billingData.length; i++) {
                this.tempCost = this.tempCost + this.billingData[i].section.section_cost
            }
        },
        checkBuildingStats(index) {
            if (index > 0) {

                if (!this.floorCompleteChecker(index - 1)) {
                    document.querySelector("#tab" + (index - 1)).click();
                }
            }
        },
        nextFloor(building, floor) {
            this.apartment_stat_err = false
            this.building_msg = false
            if (this.building[building].floors[floor - 1].apartment && !this.apartmentCompleteChecker(building, floor - 1)) {
                this.apartment_stat_err = true
            }
            else {
                this.floor_msg = false
                if (this.$refs['building-' + building + 'floor-' + (floor - 1)][0].validate()) {
                    this.building[building].floors[floor - 1].section_cost = this.building[building].floors[floor - 1].size ? this.building[building].floors[floor - 1].size.cost : 0
                    this.e.building[building].e = floor + 1;
                    this.building[building].floors[floor - 1].completed = true;
                    let floorFound = false;



                    for (var i = 0; i < this.billingData.length; i++) {
                        if (
                            this.billingData[i].name ==
                            "Building " + (building + 1) + " Floor " + floor
                        ) {
                            floorFound = true;
                            this.billingData[i].section = this.building[building].floors[
                                floor - 1
                            ];
                        }
                    }



                    if (!floorFound) {
                        if (!this.building[building].floors[floor - 1].apartment) {
                            this.building[building].floors[floor - 1].section_cost = this.building[building].floors[floor - 1].size ? this.building[building].floors[floor - 1].size.cost : 0
                            this.building[building].floors[floor - 1].section_net_cost = this.building[building].floors[floor - 1].section_cost
                            if (this.building[building].floors[floor - 1].kitchen) {

                                for (var k = 0; k < this.building[building].floors[floor - 1].kitchens.length; k++) {

                                    if (this.building[building].floors[floor - 1].kitchens[k].type == 'old') {
                                        this.building[building].floors[floor - 1].section_net_cost = this.building[building].floors[floor - 1].section_net_cost + (this.building[building].floors[floor - 1].kitchens[k].size ? this.building[building].floors[floor - 1].kitchens[k].size.cost : 0)
                                    }
                                    if (this.building[building].floors[floor - 1].kitchens[k].type == 'new' && this.serviceType != 'General Cleaning') {
                                        this.building[building].floors[floor - 1].section_net_cost = this.building[building].floors[floor - 1].section_net_cost + (this.building[building].floors[floor - 1].kitchens[k].size ? this.building[building].floors[floor - 1].kitchens[k].size.cost : 0)
                                    }

                                }
                            }
                            // this.building[building].floors[floor - 1].section_cost=
                            this.billSample.sectiononly_cost = this.building[building].floors[floor - 1].size ? this.building[building].floors[floor - 1].size.cost : 0
                            this.billSample.sectiononly_net_cost = this.building[building].floors[floor - 1].size ? this.building[building].floors[floor - 1].size.cost : 0
                            this.billSample.section_cost = this.building[building].floors[floor - 1].section_net_cost
                            this.billSample.section_net_cost = this.building[building].floors[floor - 1].section_net_cost
                            this.billSample.name = "Building " + (building + 1) + " Floor " + floor
                            this.billSample.section_name = "Building " + (building + 1) + " Floor " + floor
                            this.billSample.serviceNo = this.serviceCount
                            Object.assign(this.billSample.section, this.building[building].floors[floor - 1]);

                            this.billingData.push(this.billSample);
                            this.billSample = {
                                section_name: '',
                                name: '',
                                section: {},
                                section_cost: "",
                                section_net_cost: "",
                                sectiononly_cost: "",
                                sectiononly_net_cost: "",
                                serviceNo: this.serviceCount,
                            }

                        }


                    }
                    if (floor == this.building[building].floors.length) {
                        this.building[building].completed = true;
                        this.floorCompleted = true;
                    }
                    else {
                        this.building[building].completed = false;

                    }
                    this.recalcPrice(building, floor - 1);
                }
                this.findTempcost()
            }
        },
        recalcPrice(building, floor) {


            if (this.building[building].floors[floor].kitchen) {
                this.building[building].floors[floor].section_cost = this.building[building].floors[floor].size.cost
                for (var k = 0; k < this.building[building].floors[floor].kitchens.length; k++) {
                    this.building[building].floors[floor].section_cost = this.building[building].floors[floor].section_cost + this.building[building].floors[floor].kitchens[k].size.cost
                }
            }

            for (var i = 0; i < this.billingData.length; i++) {
                if (
                    this.billingData[i].name ==
                    "Building " + (building + 1) + " Floor " + floor
                ) {

                    this.billingData[i].section = this.building[building].floors[
                        floor - 1
                    ];
                }
            }
            this.findTempcost()
            this.calcTotal()

        },
        calcTotal() {
            this.totalCost = 0;

            for (var i = 0; i < this.multiServicesBill.length; i++) {
                for (var j = 0; j < this.multiServicesBill[i].bill.length; j++) {
                    /*if(!this.multiServicesBill[i].bill[j].section.kitchen)
                    {
                                  this.multiServicesBill[i].bill[j].section.section_cost=this.multiServicesBill[i].bill[j].section.size.cost
                                  this.multiServicesBill[i].bill[j].section.section_net_cost=this.multiServicesBill[i].bill[j].section.size.cost
                    }*/
                    this.totalCost = this.totalCost + this.multiServicesBill[i].bill[j].section_net_cost;
                }
            }
        },
        recalcApartmentPrice(building, floor, apartment) {
            /*this.totalCost = 0;
            for (var i = 0; i < this.billingData.length; i++) {
              this.totalCost = this.totalCost + this.billingData[i].section.size.cost;
            }*/
            if (this.building[building].floors[floor].apartments[apartment].kitchen) {
                this.building[building].floors[floor].apartments[apartment].section_cost = this.building[building].floors[floor].apartments[apartment].size.cost
                for (let k = 0; k < this.building[building].floors[floor].apartments[apartment].kitchens.length; k++) {
                    this.building[building].floors[floor].apartments[apartment].section_cost = this.building[building].floors[floor].apartments[apartment].section_cost + this.building[building].floors[floor].apartments[apartment].kitchens[k].size.cost
                }
            }
            let apartmentFound = false;
            for (let i = 0; i < this.billingData.length; i++) {
                if (
                    this.billingData[i].name ==
                    "Building " + (building + 1) + " Floor " + (floor + 1) + " Apartment " + (apartment + 1)
                ) {
                    apartmentFound = true;

                    this.billingData[i].section = this.building[building].floors[
                        floor
                    ].apartments[apartment];

                }
            }

            this.calcTotal()
            this.findTempcost()
        },
        setCost(building, floor, apartment) {
            this.building[building].floors[floor].apartments[apartment].cost = "";
        },
        getServiceProductivity() {
            if (!this.serviceType) return;
            fetch(`${this.url}/customer/ajax/getserviceproductivity?service_type=${this.serviceType}`)
                .then(response => response.json())
                .then(data => {
                    this.new_kitchen_cabinet_productivity = data.newkitchenwithcabinet_perhour_cleaning
                    this.new_kitchen_nocabinet_productivity = data.newkitchenwithout_perhour_cleaning
                    this.old_kitchen_cabinet_productivity = data.oldkitchenwithcabinet_perhour_cleaning
                    this.old_kitchen_nocabinet_productivity = data.oldkitchenwithoutcabinet_perhour_cleaning
                })
        },
        checkIsHourly() {
            const hourly_services = this.multiServicesBill.filter(a => a.service == 'Hourly Cleaning')
            if (hourly_services.length > 0) {

                this.is_hourly = true
                return true
            }
            else {
                this.is_hourly = false
                return false
            }
        },
        /**
         * Calculate addon manhour from bill items
         * @param {Array} billItems - Array of bill items containing addons
         * @returns {number} Total addon manhour
         */
        calculateAddonManhour(billItems) {
            return billItems
                .flatMap(item => item.section?.addons || [])
                .filter(addon => addon?.selected)
                .reduce((total, addon) => {
                    // Validate required properties
                    if (!addon?.details?.productivity || !addon?.quantity) {
                        return total;
                    }

                    const quantity = addon.quantity;
                    const productivity = addon.details.productivity;

                    if (addon.details.category && addon.selected_size?.max_size) {
                        const maxSize = parseInt(addon.selected_size.max_size);
                        if (productivity > 0) {
                            return total + (quantity * (maxSize / productivity));
                        }
                    } else if (productivity > 0) {
                        return total + (productivity * quantity);
                    }
                    
                    return total;
                }, 0);
        },
        doSomethingAsync(k) {
            return new Promise((resolve) => {
                let service_to_select = '';

                if (this.schedule_serviceTypes[k] == 'Kitchen Appliances') {
                    service_to_select = 'Kitchen Cleaning'
                }
                else if (this.schedule_serviceTypes[k] == 'Hourly Cleaning') {
                    service_to_select = 'General Cleaning'
                }
                else {
                    service_to_select = this.schedule_serviceTypes[k]
                }

                fetch(`${this.url}/customer/ajax/getserviceproductivity?service_type=${service_to_select}`)
                    .then(response => response.json())
                    .then((data) => {
                        let total_estimated_size = 0
                        let total_highpricewindow_size = 0;
                        let total_lowpricewindow_size = 0;
                        let total_highpricefacade_size = 0;
                        let total_lowpricefacade_size = 0;
                        let selected_service = ''
                        let responseData = '';

                        if (service_to_select === 'Rope Access') {

                            const firstRopeAccess = this.multiServicesBill[k].bill.find(bill => bill.section.rope_access_type)?.section.rope_access_type;
                            if (firstRopeAccess) {

                                if (data[firstRopeAccess]) {
                                    responseData = data[firstRopeAccess]
                                    this.max_cleaners.push(data[firstRopeAccess].max_cleaners)
                                    this.min_cleaners.push(data[firstRopeAccess].min_cleaners)
                                    this.max_hours.push(data[firstRopeAccess].max_hours)
                                    this.min_hours.push(data[firstRopeAccess].min_hours)
                                    selected_service = this.schedule_serviceTypes[k]
                                    this.durationData[this.schedule_serviceTypes[k]] = data[firstRopeAccess]
                                }
                            }
                        } else {
                            responseData = data
                            this.max_cleaners.push(data.max_cleaners)
                            this.min_cleaners.push(data.min_cleaners)
                            this.max_hours.push(data.max_hours)
                            this.min_hours.push(data.min_hours)
                            selected_service = this.schedule_serviceTypes[k]
                            this.durationData[this.schedule_serviceTypes[k]] = data
                        }

                        /*   Calculation begins */


                        //to find total size and manhour
                        if (selected_service == "Upholstery Cleaning") {
                            const total_sofa_size = this.sofa_size;
                            const total_chair_size = this.chair_size;
                            // var total_curtain_size = 750;
                            let manhour =
                                parseInt(total_sofa_size / responseData["sofa_perhour_cleaning"]) +
                                parseInt(total_chair_size / responseData["chair_perhour_cleaning"]);
                        } else if (selected_service == "Facade Cleaning") {
                            for (let b = 0; b < this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length; b++) {
                                if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.is_highprice_facade) {
                                    total_highpricefacade_size = total_highpricefacade_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
                                }
                                else {
                                    total_lowpricefacade_size = total_lowpricefacade_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
                                }
                            }
                            var manhour =
                                parseInt(
                                    total_highpricefacade_size /
                                    data["highpricefacade_perhour_cleaning"]
                                ) +
                                parseInt(
                                    total_lowpricefacade_size /
                                    data["lowpricefacade_perhour_cleaning"]
                                );
                        } else if (selected_service == "Kitchen Cleaning") {

                            var manhour =
                                parseInt(
                                    this.new_kitchen_cabinet_size / data["newkitchenwithcabinet_perhour_cleaning"]
                                ) +
                                parseInt(
                                    this.new_kitchen_nocabinet_size / data["newkitchenwithout_perhour_cleaning"]
                                ) +
                                parseInt(
                                    this.old_kitchen_cabinet_size / data["oldkitchenwithcabinet_perhour_cleaning"]
                                ) +
                                parseInt(
                                    this.old_kitchen_nocabinet_size / data["oldkitchenwithoutcabinet_perhour_cleaning"]
                                )
                            //To find addons man hour 
                            const billItems = this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill;
                            const addon_manhour = this.calculateAddonManhour(billItems);
                            manhour = parseInt(manhour) + parseInt(addon_manhour)
                        }
                        else if (selected_service == 'Kitchen Appliances') {
                            const billItems = this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill;
                            const addon_manhour = this.calculateAddonManhour(billItems);
                            var manhour = parseInt(addon_manhour);
                        }

                        else if (selected_service == "Window Cleaning") {
                            for (var b = 0; b < this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length; b++) {
                                if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.is_highprice_window) {
                                    total_highpricewindow_size = total_highpricewindow_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
                                }
                                else {
                                    total_lowpricewindow_size = total_lowpricewindow_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
                                }
                            }

                            var manhour =
                                parseInt(
                                    total_highpricewindow_size /
                                    data["highpricewindow_perhour_cleaning"]
                                ) +
                                parseInt(
                                    total_lowpricewindow_size /
                                    data["lowpricewindow_perhour_cleaning"]
                                );
                        } else if (selected_service == "Rope Access") {
                            let total_highprice_ropeaccess_size = 0;
                            let total_lowprice_ropeaccess_size = 0;

                            for (var b = 0; b < this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length; b++) {
                                if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.is_highprice_ropeaccess) {
                                    total_highprice_ropeaccess_size = total_highprice_ropeaccess_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
                                }
                                else {
                                    total_lowprice_ropeaccess_size = total_lowprice_ropeaccess_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
                                }
                            }

                            var manhour =
                                parseInt(
                                    total_highprice_ropeaccess_size /
                                    data["highprice_ropeaccess_perhour_cleaning"]
                                ) +
                                parseInt(
                                    total_lowprice_ropeaccess_size /
                                    data["lowprice_ropeaccess_perhour_cleaning"]
                                );
                        }
                        else {
                            //var total_estimated_size = this.total_size;
                            for (var ose = 0; ose < this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length; ose++) {
                                if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ose].section.size) {
                                    total_estimated_size = total_estimated_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ose].section.size.max_size
                                }
                            }
                            let productivity = data["perhour_cleaning"];
                            let manhour = parseInt(total_estimated_size / productivity);
                            let new_kit_cab_size = 0
                            let new_kit_nocab_size = 0
                            let old_kit_cab_size = 0
                            let old_kit_nocab_size = 0
                            let kit_manhour = 0
                            for (var b = 0; b < this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length; b++) {
                                if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchen) {
                                    for (var kit = 0; kit < this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens.length; kit++) {
                                        if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].is_newkitchen) {
                                            if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].is_cabinet) {
                                                new_kit_cab_size = new_kit_cab_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                                            }
                                            else {
                                                new_kit_nocab_size = new_kit_nocab_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                                            }

                                        } else {
                                            if (this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].is_cabinet) {
                                                old_kit_cab_size = old_kit_cab_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                                            }
                                            else {
                                                old_kit_nocab_size = old_kit_nocab_size + this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                                            }
                                        }
                                    }
                                }
                            }
                            kit_manhour = parseInt(new_kit_cab_size / this.new_kitchen_cabinet_productivity) + parseInt(old_kit_cab_size / this.old_kitchen_cabinet_productivity)
                                + parseInt(old_kit_nocab_size / this.old_kitchen_nocabinet_productivity) + parseInt(new_kit_nocab_size / this.new_kitchen_nocabinet_productivity)
                            manhour = manhour + kit_manhour
                        }
                        if (manhour < 2) {
                            manhour = 2
                        }

                        //optimal finding
                        this.totalmanhour = this.totalmanhour + manhour
                        let r = 2 ** (this.totalmanhour.toString().length + 1);
                        let mod = this.totalmanhour % r;

                        if (mod > parseInt(r / 4)) {
                            this.n = this.totalmanhour + (r - mod);
                        } else {
                            this.n = this.totalmanhour - mod;
                        }

                        this.max_cleaners.push(data.max_cleaners)
                        resolve("done")


                    }).catch((error) => {
                        console.error("doSomethingAsync failed for service:", service_to_select, error.message || error, error.stack)
                        resolve("done")
                    })
            });
        },

        /* ================================================================
            17. COMPLEX DURATION & MANHOUR CALCULATIONS
            ================================================================
             Advanced productivity algorithms for schedule optimization
        ================================================================ */

        newdurationcalculation() {
            this.subStat = ''
            this.max_cleaners = []
            this.min_cleaners = []
            this.max_hours = []
            this.min_hours = []
            this.duration = []
            this.totalmanhour = 0
            let promises = [];
            var count = 0;


            for (var k = 0; k < this.schedule_serviceTypes.length; k++) {
                promises.push(
                    this.doSomethingAsync(k)
                )
            }

            /** Loop ends here  */
            Promise.all(promises)
                .then(responses => {
                    var manhour = this.totalmanhour

                    // var n=this.n
                    if (this.cleaningPolicy == 'Subscription') {
                        this.subscriptionHourCalculation(manhour)
                    }
                    else {
                        this.newHourCalculation(manhour)
                    }


                    // Fallback: If no duration was calculated but we have services, call getMultipleSlots directly
                    if (this.duration.length === 0 && this.schedule_serviceTypes.length > 0) {
                        // Set a default duration as fallback
                        this.selectedDuration = {
                            cleaners: 1,
                            hours: 2,
                            slots: 1
                        };
                        // Try to get slots after a short delay to ensure data is ready
                        setTimeout(() => {
                            if (this.slotDate) {
                                this.getMultipleSlots();
                            }
                        }, 500);
                    }
                })
        },
        oldHourCalculation(n) {
            let manhour = n
            let pair = [];
            for (var i = 1; i < parseInt(n ** (1 / 2)) + 1; i++) {
                if (n % i == 0) {
                    pair = [i, n / i];
                }
            }
            //pair convert to 3's multiple
            let convertion_r = 2;
            let convertion_mod = pair[1] % convertion_r;
            var highest_cleaner = Math.max(...this.maxCleaners)
            var lowest_cleaner = Math.min(...this.maxCleaners)

            if (convertion_mod > parseInt(convertion_r / 2)) {

                pair = [
                    Math.round(manhour / (pair[1] + (convertion_r - convertion_mod))),
                    pair[1] + (convertion_r - convertion_mod),
                ];
            } else {


                if (pair[1] - convertion_mod == 0) {
                    pair = [Math.round(manhour / 2), 2];
                } else {
                    pair = [
                        Math.round(manhour / (pair[1] - convertion_mod)),
                        pair[1] - convertion_mod,
                    ];
                }
            }


            //var max_cleaners = data["max_cleaners"];
            //max_cleaners=10;
            var duration_list = [];
            var lower_loop = 0;
            var upper_loop = 0;
            var middle_element = pair[0];
            var middle_hours = pair[1];

            if (middle_element <= lowest_cleaner && middle_element > 0) {
                duration_list.push(pair);

                //first
                if (
                    Math.round(manhour / (middle_hours - 2)) > 0 &&
                    Math.round(manhour / (middle_hours - 2)) <= lowest_cleaner
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours - 2)),
                        middle_hours - 2,
                    ]);
                    lower_loop = 1;
                }
                if (
                    Math.round(manhour / (middle_hours + 2)) > 0 &&
                    Math.round(manhour / (middle_hours + 2)) <= lowest_cleaner
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours + 2)),
                        middle_hours + 2,
                    ]);
                    upper_loop = 1;
                }

                //check
                if (
                    Math.round(manhour / (middle_hours - 4)) > 0 &&
                    Math.round(manhour / (middle_hours - 4)) <= lowest_cleaner &&
                    upper_loop == 0
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours - 4)),
                        middle_hours - 4,
                    ]);
                    lower_loop = 1;
                }
                if (
                    Math.round(manhour / (middle_hours + 4)) > 0 &&
                    Math.round(manhour / (middle_hours + 4)) <= lowest_cleaner &&
                    lower_loop == 0
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours + 4)),
                        middle_hours + 4,
                    ]);
                    upper_loop = 1;
                }
            } else if (middle_element == 0 && lowest_cleaner > 0) {
                //1st
                duration_list.push([1, middle_hours]);

                //2nd
                if (
                    Math.round(manhour / (middle_hours + 2)) > 0 &&
                    Math.round(manhour / (middle_hours + 2)) <= lowest_cleaner
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours + 2)),
                        middle_hours + 2,
                    ]);
                } else {
                    duration_list.push([1, middle_hours + 2]);
                }

                //3rd
                if (
                    Math.round(manhour / (middle_hours + 4)) > 0 &&
                    Math.round(manhour / (middle_hours + 4)) <= lowest_cleaner
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours + 4)),
                        middle_hours + 4,
                    ]);
                } else {
                    duration_list.push([1, middle_hours + 4]);
                }
            } else {
                middle_element = lowest_cleaner;
                middle_hours =
                    Math.round(manhour / middle_element) -
                    (Math.round(manhour / middle_element) % 2);
                if (middle_hours == 0) {
                    middle_hours = 2;
                }

                //1st
                duration_list.push([middle_element, middle_hours]);

                //2nd
                if (
                    Math.round(manhour / (middle_hours + 2)) > 0 &&
                    Math.round(manhour / (middle_hours + 2)) <= lowest_cleaner
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours + 2)),
                        middle_hours + 2,
                    ]);
                } else {
                    duration_list.push([middle_element, middle_hours + 2]);
                }

                //3rd
                if (
                    Math.round(manhour / (middle_hours + 4)) > 0 &&
                    Math.round(manhour / (middle_hours + 2)) <= highest_cleaner
                ) {
                    duration_list.push([
                        Math.round(manhour / (middle_hours + 4)),
                        middle_hours + 4,
                    ]);
                } else {
                    duration_list.push([middle_element, middle_hours + 4]);
                }
            }

            for (i = 0; i < duration_list.length; i++) {
                var total_duration = duration_list[i][1];
                //show to users
                var total_minutes = (total_duration.toFixed(2) * 60).toFixed(0);
                var converted_hours = Math.floor(total_minutes / 60);
                var converted_minutes = total_minutes % 60;
                var total_cleaners = duration_list[i][0];

                this.setDuration(converted_hours, total_cleaners);
            }
            this.sortDuration()

        },
        newHourCalculation(n) {
            if (n % 2 == 1) {
                n = n + 1
            }
            var minman = Math.max(...this.min_cleaners)
            var maxman = Math.max(...this.max_cleaners)
            var minhr = Math.max(...this.min_hours)
            var maxhr = Math.max(...this.max_hours)



            //allowed calculation
            var allowed = []
            for (var i = minhr; i <= maxhr; i++) {
                if (i % 2 == 0 && i != 8) {
                    allowed.push(i)
                }
            }
            //initialization




            var maxn = maxman * maxhr
            var minn = minman * minhr

            var rem = n % (maxn)

            var cleaningset = []

            //Append Each Days Pair
            var days = parseInt((n - rem) / maxn)
            for (var i = 0; i < days; i++) {
                cleaningset.push([maxhr, maxman])
            }


            //Append Remining Low Pair
            if (rem != 0) {
                var lowpair = [allowed[0], Math.round(rem / allowed[0])]
                for (var i = 0; i < allowed.length; i++) {
                    if (lowpair[0] + lowpair[1] > (allowed[i] + Math.round(rem / allowed[i]))) {
                        lowpair = [allowed[i], Math.round(rem / allowed[i])]
                    }
                }
                if (lowpair[1] != 0 && lowpair[1] < minman) {
                    cleaningset.push([minhr, minman])
                }
                else if (lowpair[1] != 0 && lowpair[1] > maxman) {
                    for (var i = 0; i < allowed.reverse(); i++) {
                        var rev = allowed.reverse()
                        if (round(rem / rev[i]) <= maxman) {
                            cleaningset.push(rev[i], round(rem / rev[i]))
                            break
                        }
                    }
                }
                else if (lowpair[1] != 0 && lowpair[1] >= minman && lowpair[1] <= maxman) {
                    cleaningset.push(lowpair)
                }



            }
            if (cleaningset.length == 0 && n != 0) {
                cleaningset = [minhr, minman]
            }
            //cleaning set smoothening for 2-D array
            if ((cleaningset.length > 1) && !Number.isInteger(cleaningset[0])) {
                last_set_length = cleaningset.length
                last_set = cleaningset[last_set_length - 1]



                try {
                    fixed_hour = cleaningset[0][0]
                    variable_cleaner = cleaningset[0][1]
                }
                catch {
                    fixed_hour = cleaningset[0]
                    variable_cleaner = cleaningset[1]
                }
                for (var i = 1; i <= variable_cleaner; i++) {
                    if ((last_set_length * fixed_hour * i) >= n && i >= minman) {
                        cleaningset = []
                        for (var j = 0; j < last_set_length; j++) {
                            cleaningset.push([fixed_hour, i])
                        }


                        break
                    }
                }
            }

            //1D array to 2D array
            if (cleaningset.length > 0)
                if (Number.isInteger(cleaningset[0])) {
                    cleaningset = [cleaningset]
                }

            this.cleaning_set = cleaningset
            this.selectedDuration = {
                cleaners: this.cleaning_set[0][1],
                hours: this.cleaning_set[0][0],
                slots: Math.ceil(this.cleaning_set[0][0] / 2)
            }
            this.calcSlots()
            this.getMultipleSlots()


        },
        subscriptionHourCalculation(n) {



            if (n % 2 == 1) {
                n = n + 1
            }
            var minman = Math.max(...this.min_cleaners)
            var maxman = Math.max(...this.max_cleaners)
            var minhr = Math.max(...this.min_hours)
            var maxhr = Math.max(...this.max_hours)



            //allowed calculation
            var allowed = []
            for (var i = minhr; i <= maxhr; i++) {
                if (i % 2 == 0 && i != 8) {
                    allowed.push(i)
                }
            }
            //initialization




            var maxn = maxman * maxhr
            var minn = minman * minhr

            var rem = n % (maxn)

            var cleaningset = []

            //Append Each Days Pair
            var days = parseInt((n - rem) / maxn)
            for (var i = 0; i < days; i++) {
                cleaningset.push([maxhr, maxman])
            }


            //Append Remining Low Pair
            if (rem != 0) {
                var lowpair = [allowed[0], Math.round(rem / allowed[0])]
                for (var i = 0; i < allowed.length; i++) {
                    if (lowpair[0] + lowpair[1] > (allowed[i] + Math.round(rem / allowed[i]))) {
                        lowpair = [allowed[i], Math.round(rem / allowed[i])]
                    }
                }
                if (lowpair[1] != 0 && lowpair[1] < minman) {
                    cleaningset.push([minhr, minman])
                }
                else if (lowpair[1] != 0 && lowpair[1] > maxman) {
                    for (var i = 0; i < allowed.reverse(); i++) {
                        var rev = allowed.reverse()
                        if (round(rem / rev[i]) <= maxman) {
                            cleaningset.push(rev[i], round(rem / rev[i]))
                            break
                        }
                    }
                }
                else if (lowpair[1] != 0 && lowpair[1] >= minman && lowpair[1] <= maxman) {
                    cleaningset.push(lowpair)
                }



            }
            if (cleaningset.length == 0 && n != 0) {
                cleaningset = [minhr, minman]
            }
            //cleaning set smoothening for 2-D array
            if ((cleaningset.length > 1) && !Number.isInteger(cleaningset[0])) {
                last_set_length = cleaningset.length
                last_set = cleaningset[last_set_length - 1]



                try {
                    fixed_hour = cleaningset[0][0]
                    variable_cleaner = cleaningset[0][1]
                }
                catch {
                    fixed_hour = cleaningset[0]
                    variable_cleaner = cleaningset[1]
                }
                for (var i = 1; i <= variable_cleaner; i++) {
                    if ((last_set_length * fixed_hour * i) >= n && i >= minman) {
                        cleaningset = []
                        for (var j = 0; j < last_set_length; j++) {
                            cleaningset.push([fixed_hour, i])
                        }


                        break
                    }
                }
            }

            //1D array to 2D array
            if (cleaningset.length > 0)
                if (Number.isInteger(cleaningset[0])) {
                    cleaningset = [cleaningset]
                }

            this.cleaning_set = cleaningset
            var sub_cleaners = 0
            for (var cs = 0; cs < this.cleaning_set.length; cs++) {
                sub_cleaners = sub_cleaners + this.cleaning_set[cs][1]
            }
            this.selectedDuration = {
                cleaners: sub_cleaners,
                hours: this.cleaning_set[0][0],
                slots: Math.ceil(this.cleaning_set[0][0] / 2)
            }
            this.calcSlots()
            this.getMultipleSlots()


        },
        getFirstWord(text) {
            if (text) {
                return text.split(' ')[0];
            }
            return '';
        },
        getKitchenCount() {
            if (this.otherServices) {
                var count = 0;
                for (var i = 0; i < this.otherServices.length; i++) {
                    if (this.otherServices[i].type === 'old') {
                        count++;
                    }
                }
                return count;
            }
            return 0;
        },
        getSizeWithoutUnit(sizeString) {
            if (!sizeString) {
                return '';
            }
            // Remove common size units like SQM, sqm, Sqm, etc.
            return sizeString.replace(/\s*(SQM|sqm|Sqm|sq\.m|sq m|m²)/gi, '').trim();
        }
    },
    mounted() {
        this.url = api;
        this.getServiceTypes();
        this.getServices();
        this.getServiceProductivity();
        this.getAreaTypes();
        this.getIp();
        this.getGovernorate();

        // Ensure addons are loaded for initial serviceType if already set
        if (this.serviceType) {
            this.getAddons();
        }

        this.dateSelected = moment().format().split('T')[0];
        this.today = moment().format().split('T')[0];
        this.oneTimeDateSelected = moment().format().split('T')[0];
        this.one_time_slots[this.oneTimeDateSelected] = {
            slots: []
        };
        this.formatDate();
        this.getMultipleSlots();

        // this.changeNewKitchen();

        // Initialize owl carousels after Vue has finished rendering
        this.$nextTick(() => {
            // Initialize category carousel
            $('#category-carousel').owlCarousel({
                items: 4,
                loop: false,
                margin: 10,
                nav: true,
                dots: false,
                responsive: {
                    0: { items: 1 },
                    600: { items: 2 },
                    1000: { items: 4 }
                }
            });

            // Initialize service carousel
            $('#service-carousel').owlCarousel({
                items: 4,
                loop: false,
                margin: 10,
                nav: true,
                dots: false,
                responsive: {
                    0: { items: 1 },
                    600: { items: 2 },
                    1000: { items: 4 }
                }
            });
        });
    },
    beforeDestroy() {
    }
});
