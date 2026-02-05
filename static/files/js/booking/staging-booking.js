new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    delimiters: ['[[', ']]'],
    data: {
        // Constants
        MAX_VISIT_ITERATIONS: 999,
        ALTERNATE_WEEK_SKIP_DAYS: 8,
        ALTERNATE_DAY_SKIP_DAYS: 2,
        HOURLY_CLEANING_LOW_RATE: 15,
        HOURLY_CLEANING_HIGH_RATE: 25,
        HOURLY_CLEANING_THRESHOLD: 2,

        // UI State
        snackbar: false,
        mediaUrl: '',
        generalNotes: '',

        // Location Selection
        selectedLocationType: null,
        selectedAreaType: null,
        selectedNoOfBuildings: null,
        selectedNoOfFloors: {}, // Track floors per building
        tab: null,
        floorApartments: {}, // Track apartment selection for each floor
        floorApartmentCounts: {}, // Track number of apartments per floor
        floorSize: {}, // Track floor size per building-floor
        floorWallType: {}, // Track wall type per building-floor
        floorFloorType: {}, // Track floor type per building-floor
        floorCeilingType: {}, // Track ceiling type per building-floor
        floorRooms: {}, // Track number of rooms per building-floor
        floorBathrooms: {}, // Track number of bathrooms per building-floor
        floorWindows: {}, // Track number of windows per building-floor
        floorKitchenPreference: {}, // Track kitchen cleaning preference
        floorCabinetCleaning: {}, // Track cabinet cleaning preference
        floorKitchenCondition: {}, // Track kitchen condition (old/new)
        floorKitchenSize: {}, // Track kitchen size
        floorOilResidue: {}, // Track oil residue preference
        floorNoteFieldName: {}, // Track notes field name per floor
        floorNoteValue: {}, // Track notes value per floor
        floorNotes: {}, // Track all notes per floor
        floorGeneralNotes: {}, // Track general notes per floor
        floorSectionCost: {}, // Track calculated section cost per floor
        completedFloors: {}, // Track completed floors per building
        activeFloor: {}, // Track currently active floor per building
        completedApartments: {}, // Track completed apartments per building/floor
        activeApartment: {}, // Track currently active apartment per building/floor
        cartItems: [], // Track items added to cart
        cartItemIdCounter: 0, // Counter for generating unique IDs
        noteIdCounter: 0, // Counter for generating unique note IDs
        scheduleTogether: false, // Track schedule together toggle
        cleaningPolicy: null, // Track selected cleaning policy
        dateMenu: false, // Date picker menu state
        availableSlots: [ // Available time slots
            { id: 1, start_time: '08:00', end_time: '10:00' },
            { id: 2, start_time: '10:00', end_time: '12:00' },
            { id: 3, start_time: '12:00', end_time: '14:00' },
            { id: 4, start_time: '14:00', end_time: '16:00' },
            { id: 5, start_time: '16:00', end_time: '18:00' },
            { id: 6, start_time: '18:00', end_time: '20:00' },
            { id: 7, start_time: '20:00', end_time: '22:00' }
        ],
        // Scheduling data
        visits: [], // Array of visit dates and slots
        visitDateTime: [], // Array of formatted datetime strings
        dateSelected: moment().format('YYYY-MM-DD'), // Selected start date (default to today)
        selectedDoubleSlots: [], // Selected time slots
        selectedDuration: { hours: 0, cleaners: 1 }, // Duration and cleaners
        subStat: null, // Subscription status: 'Weekly', 'Daily', or null for one-time
        prefDay: [], // Preferred days for weekly cleaning
        altweekStat: false, // Alternate week status
        altdaysStat: false, // Alternate days status
        noOfVisits: 0, // Number of visits for subscription
        customDateSelected: [], // Array of custom selected dates for Custom subscription
        scheduleDialog: false,
        oneTimeSlotDialog: false, // Dialog for one-time service slot selection
        scheduleDateSat: false,
        scheduleErrMsg: false,
        slotMsg: false,
        slotStat: { availableSlotes: [], busySlotes: [] },
        autofixStat: false,
        outOfShift: false,
        editScheduleStat: false, // Flag to track if schedule is being edited
        
        // One-Time Slot Properties
        oneTimeDateSelected: null, // Selected date for one-time slot booking (YYYY-MM-DD format)
        oneTimeRender: true, // Flag to control rendering of one-time slots
        oneTimeSlots: {}, // Object storing selected slots keyed by date
        availableSlotes: [], // Array of available slot numbers for current date
        currentSlotDay: 1, // Current day being selected in multi-day one-time booking
        cleaningSet: [], // Array of cleaning hour requirements per day
        today: moment().format('YYYY-MM-DD'), // Today's date in YYYY-MM-DD format
        
        slotFormat: {
            "1": {
                startTime: '12:00 AM',
                endTime: '02:00 AM'
            },
            "2": {
                startTime: '02:00 AM',
                endTime: '04:00 AM'
            },
            "3": {
                startTime: '04:00 AM',
                endTime: '06:00 AM'
            },
            "4": {
                startTime: '06:00 AM',
                endTime: '08:00 AM'
            },
            "5": {
                startTime: '08:00 AM',
                endTime: '10:00 AM'
            },
            "6": {
                startTime: '10:00 AM',
                endTime: '12:00 PM'
            },
            "7": {
                startTime: '12:00 PM',
                endTime: '02:00 PM'
            },
            "8": {
                startTime: '02:00 PM',
                endTime: '04:00 PM'
            },
            "9": {
                startTime: '04:00 PM',
                endTime: '06:00 PM'
            },
            "10": {
                startTime: '06:00 PM',
                endTime: '08:00 PM'
            },
            "11": {
                startTime: '08:00 PM',
                endTime: '10:00 PM'
            },
            "12": {
                startTime: '10:00 PM',
                endTime: '12:00 AM'
            }
        },
        scheduleServiceTypesSelected: [],
        scheduleServiceTypes: [],
        currentService: '',
        hourlyCleaning: { hourlyDuration: 0, cleaners: 1 },
        multiServicesBill: {},
        url: '', // Base URL for API calls
        areaTypes: [],
        buildingNumbers: Array.from({ length: 15 }, (_, i) => i + 1),
        floorNumbers: Array.from({ length: 15 }, (_, i) => i + 1),
        serviceGroups: [],
        serviceTypes: [],
        serviceType: null,
        serviceSize: [],
        sizeData: [],
        ropeAccessTypes: [],
        windowSize: [],
        window_check: false,
        otherService: {
            size: {}
        },
        // Define location types
        primaryLocationTypes: [
            { value: 'Post Construction', text: 'Post Construction' },
            { value: 'Post Renovation', text: 'Post Renovation' },
            { value: 'Fully Furnished', text: 'Fully Furnished' },
            { value: 'Empty Area', text: 'Empty Area' }
        ],
        secondaryLocationTypes: [
            { value: 'Fully Furnished', text: 'Fully Furnished' },
            { value: 'Empty Area', text: 'Empty Area' }
        ],
        activeTabs: {
            activeServiceGroupId: null,
            activeServiceTypeId: null,
            cart: false,
            schedule: false,
            service: true,
        },
        // Map service type to location type set (by name; adjust as needed)
        serviceLocationTypeMap: {
            'Deep Cleaning': 'primary',
            'Window Cleaning': 'primary',
            'Rope Access': 'primary',
            'Kitchen Cleaning': 'primary',
            'Sterilization': 'primary',
            'General Cleaning': 'secondary',
            'Upholstery Cleaning': 'secondary',
            'Mattress Cleaning': 'secondary',
            'Carpet Cleaning': 'secondary',
            'Pest Control': 'secondary'
        },
        // Reusable carousel settings
        carouselSettings: {
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
        },
    },
    methods: {

        // =================================================
        // 1. API CALLS & SERVER COMMUNICATION
        // =================================================

        /**
         * Fetches service types and groups from the server, sets media URL, and selects the first service by default.
         * Also handles error by showing a snackbar notification.
         */
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
                    this.serviceGroups = data.service_groups ?? [];
                    this.serviceTypes = data.service_types ?? [];

                    // Select first service by default
                    if (this.serviceTypes.length > 0) {
                        this.activeTabs.activeServiceTypeId = this.serviceTypes[0].id;
                    }
                    if (this.serviceGroups.length > 0) {
                        this.activeTabs.activeServiceGroupId = this.serviceGroups[0].id;
                    }
                })
                .catch(error => {
                    console.error('Error fetching service types:', error);
                    this.snackbar = true;
                });
        },

        /**
         * Fetches area types from the backend and updates the areaTypes property.
         * Uses the Fetch API to make a GET request to /customer/ajax/getareatypes.
         * Transforms the response to match v-select format: { value, text }
         * On success, sets this.area_types to the formatted array.
         * On error, logs the error to the console.
         */
        getAreaTypes() {
            fetch('/customer/ajax/getareatypes')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Transform API response to v-select format
                    if (data.area_types && Array.isArray(data.area_types)) {
                        this.areaTypes = data.area_types.map(item => ({
                            value: item.id,
                            text: item.name
                        }));
                    }
                })
                .catch(error => {
                    console.error('Error fetching area types:', error);
                });
        },

        /**
         * Fetches service size and price data based on the current service type.
         */
        getSize() {
            let service = this.serviceType;
            if (service === 'Hourly Cleaning') {
                service = 'General Cleaning';
            }

            fetch(`/customer/ajax/getservicesizeprice?service_type=${service}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.serviceSize = data;
                    this.parseSize();

                    if (this.serviceType === 'Rope Access') {
                        this.ropeAccessTypes = [...new Set(this.sizeData.map(size => size.rope_access_type))];
                        this.ropeAccessFilter();
                        return;
                    }

                    this.windowFilter();
                })
                .catch(error => {
                    console.error('Error fetching size data:', error);
                    this.snackbar = true;
                });
        },

        /**
         * Checks availability of cleaning slots for selected dates and times.
         */
        checkAvailablility() {
            let serviceTypes = this.scheduleServiceTypes;

            if (this.current_service === 'Hourly Cleaning') {
                serviceTypes = ['General Cleaning'];
            }

            fetch('/customer/ajax/multipleservice/multipledates/cleaningslotes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    number_of_cleaners: this.selectedDuration.cleaners,
                    cleaning_hours: this.selectedDuration.hours,
                    service_types: serviceTypes,
                    shift_availability_check: !this.out_of_shift,
                    cleaning_datetimes: this.visitDateTime
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.slotStat = data;

                    // Mark available visits as 'fixed'
                    this.visits.forEach(visit => {
                        if (this.slotStat.available_slotes.includes(visit.dateTime)) {
                            visit.status = 'fixed';
                        }
                    });

                    // Set autofix status based on busy slots
                    this.autofixStat = this.slotStat.busy_slotes.length === 0;
                })
                .catch(error => {
                    console.error('Error checking availability:', error);
                    this.snackbar = true;
                });
        },

        /**
         * Fetches available time slots for multiple services.
         */
        getMultipleSlots() {
            this.slotLoader = true;
            let scheduleServices = this.scheduleServiceTypes;

            if (this.checkKitchen()) {
                scheduleServices.push('Kitchen Cleaning');
            }

            fetch(this.url + "/customer/ajax/getmultipleservicecleaningslotes", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    service_types: scheduleServices,
                    cleaning_date: this.slotDate,
                    number_of_cleaners: this.selectedDuration.cleaners
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.slotLoader = false;
                    this.timeSlots = data.slotes;
                    this.parseOneTimeSlots();

                    if (data.Error) {
                        this.errMsg = data['Error'];
                    } else {
                        this.errMsg = '';
                    }

                    if (!this.timeSlot.hasOwnProperty(this.slotDate)) {
                        this.timeSlot[this.slotDate] = {
                            selectedSlot: []
                        };
                    }

                    this.parseSize();
                })
                .catch(error => {
                    console.error('Error fetching multiple slots:', error);
                    this.slotLoader = false;
                });
        },

        // =================================================
        // 2. SCHEDULING & VISIT CALCULATION
        // =================================================

        /**
         * Main visit calculation entry point.
         */
        findVisits() {
            if (this.current_service === 'Hourly Cleaning') {
                this.findHourlyCost();
            }

            const requiredSlots = Math.ceil(this.selectedDuration.hours / 2);
            if (this.selectedDoubleSlots.length !== requiredSlots) {
                this.slotMsg = true;
                return;
            }

            this.slotMsg = false;

            if (this.selectedDoubleSlots.length === 0 || !this.dateSelected) {
                this.scheduleErrMsg = true;
                return;
            }

            this.scheduleDialog = false;
            const startSlot = Math.min(...this.selectedDoubleSlots);

            if (this.subStat === 'Weekly') {
                this.calculateWeeklyVisits(startSlot);
            } else if (this.subStat === 'Daily') {
                this.calculateDailyVisits(startSlot);
            }

            this.scheduleDateSat = true;
        },

        calculateWeeklyVisits(startSlot) {
            let dayCount = 0;
            let visitCount = 0;
            const targetVisits = parseInt(this.no_of_visits);

            while (dayCount < this.MAX_VISIT_ITERATIONS && visitCount < targetVisits) {
                const day = moment(this.dateSelected, 'YYYY-MM-DD').add(dayCount, 'days');
                const dayName = day.format('ddd');

                if (this.prefDay.includes(dayName)) {
                    const formattedDate = day.format('DD-MM-YYYY');
                    const dateTime = `${formattedDate} ${this.slotFormat[startSlot].startTime}`;

                    this.visits.push({
                        date: formattedDate,
                        slots: this.selectedDoubleSlots,
                        day: dayName,
                        dateTime: dateTime
                    });
                    this.visitDateTime.push(dateTime);
                    visitCount++;
                }

                // Handle alternate week scheduling
                if (this.altweekStat && dayName === 'Sat') {
                    dayCount += this.ALTERNATE_WEEK_SKIP_DAYS;
                } else {
                    dayCount++;
                }
            }

            if (visitCount > 0) {
                this.checkAvailablility();
            }
        },

        calculateDailyVisits(startSlot) {
            let dayCount = 0;
            let visitCount = 0;
            const targetVisits = parseInt(this.no_of_visits);

            while (dayCount < this.MAX_VISIT_ITERATIONS && visitCount < targetVisits) {
                const day = moment(this.dateSelected, 'YYYY-MM-DD').add(dayCount, 'days');
                const formattedDate = day.format('DD-MM-YYYY');
                const dateTime = `${formattedDate} ${this.slotFormat[startSlot].startTime}`;

                this.visits.push({
                    date: formattedDate,
                    slots: this.selectedDoubleSlots,
                    dateTime: dateTime
                });
                this.visitDateTime.push(dateTime);
                visitCount++;

                // Handle alternate day scheduling
                dayCount += this.altdaysStat ? this.ALTERNATE_DAY_SKIP_DAYS : 1;
            }

            if (visitCount > 0) {
                this.checkAvailablility();
            }
        },

        findMonthlyVisits() {
            if (this.current_service === 'Hourly Cleaning') {
                this.findHourlyCost();
            }

            const requiredSlots = Math.ceil(this.selectedDuration.hours / 2);
            if (this.selectedDoubleSlots.length !== requiredSlots) {
                this.slotMsg = true;
                return;
            }

            this.slotMsg = false;

            if (this.selectedMonthlyDate.length === 0 || this.selectedDoubleSlots.length === 0) {
                this.scheduleErrMsg = true;
                return;
            }

            let dayCount = 0;
            let visitCount = 0;
            const targetVisits = parseInt(this.noOfVisits);
            const startSlot = Math.min(...this.selectedDoubleSlots);

            while (dayCount < this.MAX_VISIT_ITERATIONS && visitCount < targetVisits) {
                const day = moment(this.monthlyStartingDate, 'YYYY-MM-DD').add(dayCount, 'days');
                const dayNumber = day.format('DD');

                if (dayNumber && this.selectedMonthlyDate.includes(String(dayNumber))) {
                    const formattedDate = day.format('DD-MM-YYYY');
                    const dateTime = `${formattedDate} ${this.slotFormat[startSlot].startTime}`;

                    this.visits.push({
                        date: formattedDate,
                        slots: this.selectedDoubleSlots,
                        dateTime: dateTime
                    });

                    this.visitDateTime.push(dateTime);
                    visitCount++;
                }

                dayCount++;
            }

            if (visitCount > 0) {
                this.checkAvailablility();
            }

            this.monthlyDialog = false;
            this.scheduleDateSat = true;
        },

        findCustomVisits() {
            if (this.current_service === 'Hourly Cleaning') {
                this.findHourlyCost();
            }

            const requiredSlots = Math.ceil(this.selectedDuration.hours / 2);
            if (this.selectedDoubleSlots.length !== requiredSlots) {
                this.slotMsg = true;
                return;
            }

            this.slotMsg = false;

            if (this.customDateSelected.length === 0 || this.selectedDoubleSlots.length === 0) {
                this.scheduleErrMsg = true;
                return;
            }

            const startSlot = Math.min(...this.selectedDoubleSlots);

            this.customDateSelected.forEach(selectedDate => {
                const day = moment(selectedDate, 'YYYY-MM-DD');
                const dayName = day.format('ddd');
                const formattedDate = day.format('DD-MM-YYYY');
                const dateTime = `${formattedDate} ${this.slotFormat[startSlot].startTime}`;

                this.visits.push({
                    date: formattedDate,
                    slots: this.selectedDoubleSlots,
                    day: dayName,
                    dateTime: dateTime
                });

                this.visitDateTime.push(dateTime);
            });

            this.checkAvailablility();
            this.customDialog = false;
            this.scheduleDateSat = true;
            this.scheduleErrMsg = false;
        },

        findHourlyCost() {
            const rate = this.hourlyCleaning.hourlyDuration <= this.HOURLY_CLEANING_THRESHOLD
                ? this.HOURLY_CLEANING_LOW_RATE
                : this.HOURLY_CLEANING_HIGH_RATE;
            const totalCost = rate * parseInt(this.hourlyCleaning.cleaners);

            const serviceKey = this.scheduleServiceTypesSelected[0];
            const billItems = this.multiServicesBill[serviceKey].bill;
            const sectionLength = billItems.length;
            const costPerSection = totalCost / sectionLength;

            for (let i = 0; i < sectionLength; i++) {
                const billItem = billItems[i];
                billItem.section_net_cost = costPerSection;
                billItem.section_cost = costPerSection;
                billItem.section.section_net_cost = costPerSection;
                billItem.section.section_cost = costPerSection;
                billItem.sectiononly_cost = costPerSection;
                billItem.sectiononly_net_cost = costPerSection;
            }

            this.multiServicesBill[serviceKey].total_cost = totalCost;
        },

        addToSchedule() {
            // Set schedule status
            this.scheduleStatus = this.scheduleStat;

            // Configure schedule format for selected service types
            this.scheduleServiceTypesSelected.forEach(serviceType => {
                this.scheduleFormat.individual[serviceType] = {
                    starting_date: this.visits[0].dateTime,
                    visits: this.visits
                };
            });

            const cleanersCount = this.selectedDuration.cleaners;

            // Update billing information for each selected service type
            this.scheduleServiceTypesSelected.forEach(serviceType => {
                const billDetails = this.multiServicesBill[serviceType];
                billDetails.cleaningPolicy = 'SUBSCRIPTION';
                billDetails.scheduleDetails = {};
                billDetails.cleaners = cleanersCount;

                // Add schedule details for each visit
                this.visits.forEach((visit, index) => {
                    const minSlot = Math.min(...visit.slots);
                    billDetails.scheduleDetails[index + 1] = {
                        date: visit.date,
                        time: this.slotFormat[minSlot].startTime,
                        noOfCleaners: this.selectedDuration.cleaners,
                        cleaningHours: this.selectedDuration.hours,
                        hourlyCleaningDuration: parseInt(this.hourlyCleaning.hourlyDuration) || null
                    };
                });

                billDetails.shiftAvailabilityCheck = !this.outOfShift;
            });

            // Remove selected service types from existing schedule groups
            this.scheduleServiceTypesSelected.forEach(selectedService => {
                for (const groupKey in this.scheduleGroup) {
                    if (this.scheduleGroup[groupKey].includes(selectedService)) {
                        const serviceIndex = this.scheduleGroup[groupKey].indexOf(selectedService);
                        if (serviceIndex > -1) {
                            this.scheduleGroup[groupKey].splice(serviceIndex, 1);
                        }
                    }
                }
            });

            // Create new schedule group with selected services
            const newGroupId = Object.keys(this.scheduleGroup).length;
            this.scheduleGroup[newGroupId] = [...this.scheduleServiceTypesSelected];

            // Reset state
            this.visits = [];
            this.selectedDoubleSlots = [];
            this.selectedDuration = {
                cleaners: '',
                hours: '',
                slots: ''
            };
            this.fixedSlots = {};
            this.reselectDateIndex = null;
            this.reselectDate = {};
            this.subStat = '';
            this.cleaningPolicy = '';
            this.noOfVisits = '';
            this.scheduleServiceTypesSelected = [];
            this.scheduleDateSat = false;
            this.activeTab = 'Cart';
        },

        addOneTimeToSchedule() {
            // Set schedule status
            this.scheduleStatus = this.scheduleStat;

            // Configure one-time scheduling for selected service types
            this.scheduleServiceTypesSelected.forEach(serviceType => {
                this.oneTimeScheduled[serviceType] = {
                    slot: this.selectedOnetimeSlots
                };
            });

            // Update billing information for each selected service type
            this.scheduleServiceTypesSelected.forEach(serviceType => {
                const billDetails = this.multiServicesBill[serviceType];
                billDetails.cleaningPolicy = 'ONE TIME SERVICE';
                billDetails.scheduleDetails = {};
                billDetails.cleaners = this.selectedDuration.cleaners;
                billDetails.shift_availability_check = !this.out_of_shift;

                // Handle multiple dates with continuous date grouping
                if (Object.keys(this.selectedOnetimeSlots).length > 1) {
                    this.findContDate();
                    let scheduleCount = 0;

                    for (const groupKey in this.dateGroup) {
                        const dates = this.dateGroup[groupKey];

                        if (dates.length > 0) {
                            // Find earliest date and calculate total cleaning hours
                            let minDate = dates[0];
                            let totalCleaningHours = this.selectedOnetimeSlots[dates[0]].slots.length * 2;

                            for (let i = 1; i < dates.length; i++) {
                                const currentDate = dates[i];
                                if (moment(currentDate, 'YYYY-MM-DD').isBefore(moment(minDate, 'YYYY-MM-DD'))) {
                                    minDate = currentDate;
                                }
                                totalCleaningHours += this.selectedOnetimeSlots[currentDate].slots.length * 2;
                            }

                            // Format date and add to schedule details
                            const [year, month, day] = minDate.split('-');
                            const formattedDate = `${day}-${month}-${year}`;
                            const minSlot = Math.min(...this.selectedOnetimeSlots[minDate].slots);

                            billDetails.scheduleDetails[scheduleCount + 1] = {
                                date: formattedDate,
                                time: this.slotFormat[parseInt(minSlot)].startTime,
                                noOfCleaners: this.selectedDuration.cleaners,
                                cleaningHours: totalCleaningHours,
                                hourlyCleaningDuration: null
                            };

                            scheduleCount++;
                        }
                    }
                } else {
                    // Handle single date or non-continuous dates
                    let scheduleCount = 0;

                    for (const dateKey in this.selectedOnetimeSlots) {
                        const [year, month, day] = dateKey.split('-');
                        const formattedDate = `${day}-${month}-${year}`;
                        const minSlot = Math.min(...this.selectedOnetimeSlots[dateKey].slots);
                        const cleaningHours = this.selectedOnetimeSlots[dateKey].slots.length * 2;

                        billDetails.scheduleDetails[scheduleCount + 1] = {
                            date: formattedDate,
                            time: this.slotFormat[parseInt(minSlot)].startTime,
                            noOfCleaners: this.selectedDuration.cleaners,
                            cleaningHours: cleaningHours,
                            hourlyCleaningDuration: null
                        };

                        scheduleCount++;
                    }
                }
            });

            // Remove selected service types from existing schedule groups
            this.scheduleServiceTypesSelected.forEach(selectedService => {
                for (const groupKey in this.scheduleGroup) {
                    if (this.scheduleGroup[groupKey].includes(selectedService)) {
                        const serviceIndex = this.scheduleGroup[groupKey].indexOf(selectedService);
                        if (serviceIndex > -1) {
                            this.scheduleGroup[groupKey].splice(serviceIndex, 1);
                        }
                    }
                }
            });

            // Create new schedule group with selected services
            const newGroupId = Object.keys(this.scheduleGroup).length;
            this.scheduleGroup[newGroupId] = [...this.scheduleServiceTypesSelected];

            // Reset state
            this.selectedOnetimeSlots = {};
            this.currentSlotDay = 1;
            this.oneTimeScheduled = {};
            this.oneTimeSelectionStat = false;
            this.scheduleServiceTypesSelected = [];
            this.oneTimeDateSelected = this.today;
            this.dateSelected = this.today;
            this.formatDate();
            this.oneTimeSlots = {};
            this.activeTab = 'Cart';
        },

        // =================================================
        // 3. SLOT MANAGEMENT
        // =================================================

        /**
         * Parses one-time service slots from the server response.
         * Converts slot data into available slots array and formatted time slots.
         */
        parseOneTimeSlots() {
            this.parsedTimeSlots = [];
            this.availableSlotes = [];

            for (const slotIndex in this.timeSlots) {
                if (this.timeSlots[slotIndex].includes(2)) {
                    const slotNo = (parseInt(slotIndex) + 2) / 2;
                    this.availableSlotes.push(slotNo);
                    this.parsedTimeSlots.push(this.slotFormat[String(slotNo)]);
                }
            }
        },

        /**
         * Checks if a one-time slot is already selected for the current date.
         * @param {string} start - Start time of the slot (HH:MM format)
         * @param {string} end - End time of the slot (HH:MM format)
         * @param {string|number} slot - Slot identifier
         * @returns {boolean} True if slot is selected, false otherwise
         */
        checkOneTimeSlot(start, end, slot) {
            let currSlot = '';

            // Find the slot number that matches the start time
            for (const slotKey in this.slotFormat) {
                if (this.slotFormat[slotKey].startTime === start) {
                    currSlot = slotKey;
                    break;
                }
            }

            // Check if current slot is in the selected slots for this date
            if (this.oneTimeSlots[this.oneTimeDateSelected] &&
                this.oneTimeSlots[this.oneTimeDateSelected].slots.includes(currSlot)) {
                return true;
            }

            return false;
        },

        /**
         * Checks the status of a one-time slot considering adjacency and capacity constraints.
         * Validates whether a slot can be selected based on:
         * - Total slots selected vs required slots
         * - Slot adjacency to already selected slots
         * - Special handling for edge slots (1 and 12)
         * @param {string} start - Start time of the slot (HH:MM format)
         * @param {string} end - End time of the slot (HH:MM format)
         * @param {number} slot - Slot number (1-12)
         * @returns {boolean} True if slot can be selected, false otherwise
         */
        checkOneTimeSlotStat(start, end, slot) {
            let currSlot = '';

            // Find the slot number that matches the start time
            for (const slotKey in this.slotFormat) {
                if (this.slotFormat[slotKey].startTime === start) {
                    currSlot = slotKey;
                    break;
                }
            }

            const prevSlot = parseInt(currSlot) - 1;
            const nextSlot = parseInt(currSlot) + 1;

            // Count total slots already selected across all dates
            let totalSlotsSelected = 0;
            for (const dateKey in this.oneTimeSlots) {
                totalSlotsSelected += this.oneTimeSlots[dateKey].slots.length;
            }

            // Get required slots for current day - safely check if cleaningSet is initialized
            if (!this.cleaningSet || !this.cleaningSet[this.currentSlotDay - 1] || !this.cleaningSet[this.currentSlotDay - 1][0]) {
                return true; // Allow selection if cleaningSet not yet populated
            }
            
            const requiredSlots = Math.ceil((this.cleaningSet[this.currentSlotDay - 1][0]) / 2);

            // Check if we haven't exceeded the required number of slots
            if (totalSlotsSelected >= requiredSlots) {
                return false;
            }

            // Get selected slots for current date
            const selectedSlotsForDate = this.oneTimeSlots[this.oneTimeDateSelected];

            // If no slots are selected yet for this date, allow selection
            if (!selectedSlotsForDate || selectedSlotsForDate.slots.length === 0) {
                return true;
            }

            // Check adjacency based on slot position
            return this.isSlotAdjacent(slot, prevSlot, nextSlot, selectedSlotsForDate);
        },

        /**
         * Checks if a slot is adjacent to already selected slots.
         * Enforces continuous slot selection rule.
         * @param {number} slot - Slot number (1-12)
         * @param {number} prevSlot - Previous slot number
         * @param {number} nextSlot - Next slot number
         * @param {object} selectedSlotsForDate - Object containing selected slots for the date
         * @returns {boolean} True if slot is adjacent or can be selected, false otherwise
         */
        isSlotAdjacent(slot, prevSlot, nextSlot, selectedSlotsForDate) {
            const selectedSlots = selectedSlotsForDate.slots;

            // First slot - check if next slot is selected
            if (slot === 1) {
                return selectedSlots.includes(String(nextSlot));
            }

            // Last slot - check if previous slot is selected
            if (slot === 12) {
                return selectedSlots.includes(String(prevSlot));
            }

            // Middle slots - check if either adjacent slot is selected
            return selectedSlots.includes(String(prevSlot)) ||
                selectedSlots.includes(String(nextSlot));
        },

        /**
         * Removes a one-time slot and enforces contiguous slot selection.
         * If both adjacent slots exist, removes all slots above the removed slot.
         * @param {number|string} slot - The slot number to remove
         */
        removeOneTimeSlot(slot) {
            this.oneTimeRender = false;

            // Safety check for valid data structure
            if (!this.oneTimeSlots || !this.oneTimeSlots[this.oneTimeDateSelected]) {
                this.oneTimeRender = true;
                return;
            }

            const slots = this.oneTimeSlots[this.oneTimeDateSelected].slots;
            const slotNum = parseInt(slot);
            const prevSlot = slotNum - 1;
            const nextSlot = slotNum + 1;

            // Remove the selected slot
            const index = slots.indexOf(slot);
            if (index > -1) {
                slots.splice(index, 1);
            }

            // If both adjacent slots exist, enforce contiguous selection
            // by removing all slots above the removed slot
            if (slots.includes(String(nextSlot)) && slots.includes(String(prevSlot))) {
                this.oneTimeSlots[this.oneTimeDateSelected].slots = slots.filter(
                    s => parseInt(s) <= slotNum
                );
            }

            this.oneTimeRender = true;
        },

        /**
         * Toggles selection of a time slot.
         */
        toggleSlot(slotId) {
            const index = this.selectedDoubleSlots.indexOf(slotId);
            if (index > -1) {
                this.selectedDoubleSlots.splice(index, 1);
            } else {
                this.selectedDoubleSlots.push(slotId);
            }
        },

        /**
         * Sets the selected duration and recalculates slots.
         */
        selectDuration(duration) {
            duration.slots = duration.hours / 2;
            this.selectedDuration = duration;
            this.resetOneTime();
            this.calcSlots();
            this.getMultipleSlots();
        },

        /**
         * Calculates available time slots based on duration.
         */
        calcSlots() {
            this.doubleSlots = [];
            this.selectedDoubleSlots = [];

            // Slot configuration: maps hour increments to available durations
            const SLOT_DURATIONS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24];
            const HOUR_INCREMENTS = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22];

            // Calculate available double slots based on 2-hour increments
            HOUR_INCREMENTS.forEach(hourIncrement => {
                if (SLOT_DURATIONS.includes(2)) {
                    const slotNumber = (parseInt(hourIncrement) + 2) / 2;
                    const slotKey = String(slotNumber);

                    if (this.slotFormat[slotKey]) {
                        this.doubleSlots.push(this.slotFormat[slotKey]);
                    }
                }
            });
        },

        /**
         * Resets one-time slot selection state.
         */
        resetOneTime() {
            this.oneTimeRender = false;
            this.oneTimeSlots = {};
            this.dateGroup = {};
            this.oneTimeSlots[this.oneTimeDateSelected] = {
                slots: []
            };
            this.selectedOnetimeSlots = {};
            this.currentSlotDay = 1;
            this.oneTimeRender = true;
        },

        /**
         * Combines multiple slot IDs into a time range string.
         */
        getCombinedSlot(slots) {
            const minSlot = Math.min(...slots);
            const maxSlot = Math.max(...slots);
            const startTime = this.slotFormat[String(minSlot)].startTime;
            const endTime = this.slotFormat[String(maxSlot)].endTime;
            return `${startTime} - ${endTime}`;
        },

        /**
         * Toggles selection of a preferred day for weekly scheduling.
         */
        selectPrefDay(day) {
            const dayIndex = this.prefDay.indexOf(day);

            if (dayIndex === -1) {
                // Day not selected, add it
                this.prefDay.push(day);
            } else {
                // Day already selected, remove it
                this.prefDay.splice(dayIndex, 1);
            }
        },

        /**
         * Toggles selection of a date for monthly scheduling.
         */
        selectMonthlyDate(date) {
            const dateIndex = this.selectedMonthlyDate.indexOf(date);

            if (dateIndex === -1) {
                // Date not selected, add it
                this.selectedMonthlyDate.push(date);
            } else {
                // Date already selected, remove it
                this.selectedMonthlyDate.splice(dateIndex, 1);
            }
        },

        /**
         * Checks if a slot is currently selected.
         */
        isSlotSelected(slotId) {
            return this.selectedDoubleSlots.includes(slotId);
        },

        /**
         * Formats time from 24-hour to 12-hour format with AM/PM.
         */
        formatSlotTime(time) {
            const [hours, minutes] = time.split(':');
            const hour = parseInt(hours);
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
            return `${hour12.toString().padStart(2, '0')}:${minutes} ${ampm}`;
        },

        /**
         * Gets the current date in YYYY-MM-DD format.
         * @returns {string} Current date formatted as YYYY-MM-DD
         */
        getCurrentDate() {
            return moment().format('YYYY-MM-DD');
        },

        /**
         * Counts total number of one-time slots selected across all dates.
         * @returns {number} Total count of selected slots
         */
        oneTimeSlotCounter() {
            let counter = 0;
            for (const dateKey in this.oneTimeSlots) {
                counter += this.oneTimeSlots[dateKey].slots.length;
            }
            return counter;
        },

        /**
         * Submits selected one-time slots after validation.
         * Checks that the total selected slots match the required slots based on cleaning duration.
         * Populates selectedOnetimeSlots with valid slots and closes the dialog on success.
         */
        submitOneTimeSlots() {
            this.slotMsg = false;
            const slotCount = this.oneTimeSlotCounter();
            
            // Calculate required slots - if no duration set, don't validate slot count
            const slotsRequired = this.selectedDuration.hours > 0 
                ? Math.ceil(this.selectedDuration.hours / 2) 
                : slotCount; // Allow any number of slots if duration not set

            if (slotCount === slotsRequired && slotCount > 0) {
                this.selectedOnetimeSlots = {};

                for (const dateKey in this.oneTimeSlots) {
                    if (this.oneTimeSlots[dateKey].slots.length > 0) {
                        this.selectedOnetimeSlots[dateKey] = {
                            slots: this.oneTimeSlots[dateKey].slots
                        };
                    }
                }

                this.oneTimeSlotDialog = false;
                this.oneTimeSelectionStat = true;
            } else if (slotCount === 0) {
                this.slotMsg = true; // Show error if no slots selected
                alert('Please select at least one time slot');
            } else {
                this.slotMsg = true;
            }
        },

        /**
         * Processes next slot selection in multi-day one-time slot booking flow.
         * Validates selected slots for current day, stores them with day count,
         * and advances to next day if more days remain, or completes selection.
         */
        nextSlotSelection() {
            this.slotMsg = false;
            const slotCount = this.oneTimeSlotCounter();
            const slotsRequired = Math.ceil(this.selectedDuration.hours / 2);

            if (slotCount === slotsRequired) {
                for (const dateKey in this.oneTimeSlots) {
                    if (this.oneTimeSlots[dateKey].slots.length > 0) {
                        this.selectedOnetimeSlots[dateKey] = {
                            slots: this.oneTimeSlots[dateKey].slots,
                            dayCount: this.currentSlotDay
                        };
                    }
                }

                if (this.currentSlotDay > this.cleaningSet.length) {
                    this.oneTimeSlotDialog = false;
                    this.oneTimeSelectionStat = true;
                } else {
                    this.currentSlotDay++;
                    if (this.currentSlotDay <= this.cleaningSet.length) {
                        this.oneTimeDateSelected = moment(this.oneTimeDateSelected, 'YYYY-MM-DD')
                            .add(1, 'days')
                            .format('YYYY-MM-DD');
                        this.oneTimeNewDateChange();
                    }
                }
            } else {
                this.slotMsg = true;
            }
        },

        /**
         * Handles date change for one-time slot selection.
         * Resets slots for the newly selected date and fetches available slots from server.
         * Converts date format from YYYY-MM-DD to DD-MM-YYYY for API calls.
         */
        oneTimeNewDateChange() {
            this.oneTimeSlots = {};
            this.oneTimeSlots[this.oneTimeDateSelected] = {
                slots: []
            };

            const dateParts = this.oneTimeDateSelected.split('-');
            const year = dateParts[0];
            const month = dateParts[1];
            const day = dateParts[2];
            this.slotDate = `${day}-${month}-${year}`;
            
            // Load available slots for the selected date
            this.loadAvailableSlots();
        },

        /**
         * Loads available time slots for the currently selected date.
         * Populates availableSlotes array with all 12 slot numbers (1-12).
         */
        loadAvailableSlots() {
            // Populate available slots (1-12 represent 2-hour time slots)
            this.availableSlotes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
            
            // Populate slot format with time mappings for each slot
            const slotTimes = [
                { startTime: '12:00 AM', endTime: '02:00 AM' },
                { startTime: '02:00 AM', endTime: '04:00 AM' },
                { startTime: '04:00 AM', endTime: '06:00 AM' },
                { startTime: '06:00 AM', endTime: '08:00 AM' },
                { startTime: '08:00 AM', endTime: '10:00 AM' },
                { startTime: '10:00 AM', endTime: '12:00 PM' },
                { startTime: '12:00 PM', endTime: '02:00 PM' },
                { startTime: '02:00 PM', endTime: '04:00 PM' },
                { startTime: '04:00 PM', endTime: '06:00 PM' },
                { startTime: '06:00 PM', endTime: '08:00 PM' },
                { startTime: '08:00 PM', endTime: '10:00 PM' },
                { startTime: '10:00 PM', endTime: '12:00 AM' }
            ];
            
            this.availableSlotes.forEach((slotNo, index) => {
                this.slotFormat[String(slotNo)] = slotTimes[index];
            });
            
            this.oneTimeRender = true;
        },

        /**
         * Adds a one-time slot to the current date selection.
         * Checks if slot can be added based on adjacency and capacity constraints.
         * @param {string} start - Start time (HH:MM AM/PM format)
         * @param {string} end - End time (HH:MM AM/PM format)
         * @param {number} slot - Slot number (1-12)
         */
        addOneTimeSlot(start, end, slot) {
            // Check if slot can be added
            if (!this.checkOneTimeSlotStat(start, end, slot)) {
                return;
            }

            // Initialize slots array for this date if it doesn't exist
            if (!this.oneTimeSlots[this.oneTimeDateSelected]) {
                this.oneTimeSlots[this.oneTimeDateSelected] = {
                    slots: []
                };
            }

            const slots = this.oneTimeSlots[this.oneTimeDateSelected].slots;
            const slotStr = String(slot);

            // Add slot if not already selected
            if (!slots.includes(slotStr)) {
                slots.push(slotStr);
                // Sort slots numerically
                slots.sort((a, b) => parseInt(a) - parseInt(b));
            }

            this.oneTimeRender = true;
        },

        /**
         * Calculates total number of slots across all selected dates.
         * @returns {number} Total number of slots
         */
        calculateTotalSlots() {
            let total = 0;
            for (const date in this.selectedOnetimeSlots) {
                total += this.selectedOnetimeSlots[date].slots.length;
            }
            return total;
        },

        /**
         * Gets the earliest date from selected one-time slots.
         * @returns {string} Formatted date (DD-MM-YYYY)
         */
        getEarliestDate() {
            const dates = Object.keys(this.selectedOnetimeSlots);
            if (dates.length === 0) return '';
            
            let earliest = dates[0];
            for (const date of dates) {
                if (moment(date, 'YYYY-MM-DD').isBefore(moment(earliest, 'YYYY-MM-DD'))) {
                    earliest = date;
                }
            }
            
            return this.formatDateForDisplay(earliest);
        },

        /**
         * Formats date from YYYY-MM-DD to DD-MM-YYYY format.
         * @param {string} date - Date in YYYY-MM-DD format
         * @returns {string} Formatted date in DD-MM-YYYY format
         */
        formatDateForDisplay(date) {
            const [year, month, day] = date.split('-');
            return `${day}-${month}-${year}`;
        },

        /**
         * Gets the visit number for a given date.
         * @param {string} date - Date in YYYY-MM-DD format
         * @returns {number} Visit number
         */
        getVisitNumber(date) {
            const dates = Object.keys(this.selectedOnetimeSlots).sort();
            return dates.indexOf(date) + 1;
        },

        /**
         * Gets combined slot time range for a date.
         * @param {array} slots - Array of slot numbers
         * @returns {string} Time range string
         */
        getCombinedSlotTime(slots) {
            if (!slots || slots.length === 0) return '';
            
            const minSlot = Math.min(...slots.map(s => parseInt(s)));
            const maxSlot = Math.max(...slots.map(s => parseInt(s)));
            
            const startTime = this.slotFormat[String(minSlot)].startTime;
            const endTime = this.slotFormat[String(maxSlot)].endTime;
            
            return `${startTime} - ${endTime}`;
        },

        /**
         * Resets the schedule selection and shows the slot selection dialog again.
         */
        resetScheduleSelection() {
            this.selectedOnetimeSlots = {};
            this.oneTimeSlots = {};
            this.oneTimeDateSelected = this.getCurrentDate();
            this.currentSlotDay = 1;
            this.oneTimeSlotDialog = true;
            this.loadAvailableSlots();
        },

        /**
         * Proceeds with one-time booking after reviewing schedule.
         */
        proceedWithOneTimeBooking() {
            // Trigger the add to schedule logic
            this.addOneTimeToSchedule();
        },

        // =================================================
        // 4. COST CALCULATION & BILLING
        // ================================================= 

        /**
         * Calculates cost for hourly cleaning services.
         */
        findHourlyCost() {
            // Populate service details from multi-service bill
            this.multiServicesBill.forEach((bill, serviceIndex) => {
                const serviceId = this.getServiceId(bill.service);
                const visitCount = Object.keys(bill.schedule_details).length;

                // Initialize service detail entry
                this.serviceDetails.service_details[serviceIndex] = {
                    service_type: serviceId,
                    cleaning_policy: bill.cleaning_policy,
                    schedule_details: bill.schedule_details,
                    location_type: bill.location_type,
                    area_type: bill.area_type,
                    evaluator_note: bill.evaluator_note,
                    estimated_cost: bill.total_cost,
                    total_cost: bill.total_cost,
                    number_of_cleaners: bill.cleaners,
                    cleaning_hours: parseInt(this.selectedDuration.hours),
                    sections: {}
                };

                // Adjust costs for subscription services
                const normalizedPolicy = bill.cleaning_policy;
                if (normalizedPolicy === 'SUBSCRIPTION') {
                    const totalCost = parseFloat(bill.total_cost) * parseInt(visitCount);
                    this.serviceDetails.service_details[serviceIndex].total_cost = totalCost;
                    this.serviceDetails.service_details[serviceIndex].estimated_cost = totalCost;
                }

                // Process each section in the bill
                bill.bill.forEach((billItem, sectionIndex) => {
                    const section = billItem.section;

                    // Initialize section data
                    this.serviceDetails.service_details[serviceIndex].sections[sectionIndex] = {
                        section_name: billItem.section_name,
                        size: section.size.name,
                        wall_type: '',
                        floor_type: '',
                        ceiling_type: '',
                        cement_residue: section.cement_residue,
                        oil_residue: section.residue,
                        section_cost: billItem.section_cost,
                        sectiononly_cost: billItem.sectiononly_cost,
                        sectiononly_net_cost: billItem.sectiononly_cost,
                        section_net_cost: billItem.section_net_cost,
                        keynotes: {},
                        addons: {},
                        new_kitchen: false,
                        is_cabinet: false,
                        is_highprice_facade: false,
                        is_highprice_window: false,
                        colour: '',
                        material: '',
                        cause_of_stain: '',
                        upholstery_type: '',
                        age: '',
                        age_of_stain: ''
                    };

                    const sectionDetail = this.serviceDetails.service_details[serviceIndex].sections[sectionIndex];

                    // Adjust section costs for subscription
                    const servicePolicyNormalized = this.serviceDetails.service_details[serviceIndex].cleaning_policy;
                    if (servicePolicyNormalized === 'SUBSCRIPTION') {
                        sectionDetail.sectiononly_net_cost *= parseInt(visitCount);
                        sectionDetail.section_net_cost *= parseInt(visitCount);
                    }

                    // Set boolean flags
                    if (section.size.is_highprice_facade) sectionDetail.is_highprice_facade = true;
                    if (section.size.is_highprice_window) sectionDetail.is_highprice_window = true;
                    if (section.size.is_newkitchen) sectionDetail.new_kitchen = true;
                    if (section.is_cabinet) sectionDetail.is_cabinet = true;

                    // Set optional properties
                    if (section.stain_age) sectionDetail.age_of_stain = section.stain_age;
                    if (section.color) sectionDetail.colour = section.color.join();
                    if (section.material) sectionDetail.material = section.material.join();
                    if (section.stain_reason) sectionDetail.cause_of_stain = section.stain_reason;
                    if (section.type === 'SOFA' || section.type === 'CURTAIN') {
                        sectionDetail.upholstery_type = section.type;
                    }
                    if (section.wall_type) sectionDetail.wall_type = section.wall_type.join();
                    if (section.ceiling_type) sectionDetail.ceiling_type = section.ceiling_type.join();
                    if (section.floor_type) sectionDetail.floor_type = section.floor_type.join();
                    if (section.age) sectionDetail.age = section.age;

                    // Process keynotes
                    let keynoteCounter = 1;

                    if (section.no_of_bathrooms) {
                        sectionDetail.keynotes[keynoteCounter++] = {
                            sub_area: 'bathroom',
                            quantity: section.no_of_bathrooms
                        };
                    }

                    if (section.no_of_rooms) {
                        sectionDetail.keynotes[keynoteCounter++] = {
                            sub_area: 'rooms',
                            quantity: section.no_of_rooms
                        };
                    }

                    if (section.no_of_windows) {
                        sectionDetail.keynotes[keynoteCounter++] = {
                            sub_area: 'windows',
                            quantity: section.no_of_windows
                        };
                    }

                    // Process custom keynote data
                    if (section.keynote_data && section.keynote_data.length > 0) {
                        section.keynote_data.forEach(keynote => {
                            sectionDetail.keynotes[keynoteCounter++] = {
                                sub_area: keynote.name,
                                quantity: keynote.value
                            };
                        });
                    }

                    // Process addons
                    let addonCounter = 0;

                    if (section.addons) {
                        section.addons.forEach(addon => {
                            if (addon.selected) {
                                addonCounter++;
                                sectionDetail.addons[addonCounter] = {
                                    name: addon.details.name,
                                    addon_cost: addon.details.price,
                                    addon_net_cost: addon.details.price * addon.quantity,
                                    quantity: addon.quantity,
                                    size: '',
                                    other_details: ''
                                };

                                if (addon.details.category && addon.selected_size) {
                                    sectionDetail.addons[addonCounter].size = addon.selected_size.size;
                                }
                            }
                        });
                    }

                    // Process kitchen as addon
                    if (section.kitchen && section.kitchens) {
                        let newIndex = Object.keys(sectionDetail.addons).length;

                        section.kitchens.forEach(kitchen => {
                            newIndex++;
                            sectionDetail.addons[newIndex] = {
                                name: 'kitchen',
                                addon_cost: kitchen.size.cost,
                                addon_net_cost: kitchen.size.cost,
                                quantity: 1,
                                size: kitchen.size.name,
                                other_details: JSON.stringify({
                                    size: kitchen.size.name,
                                    max_size: kitchen.size.max_size,
                                    type: kitchen.type,
                                    residue: kitchen.residue,
                                    is_cabinet: kitchen.is_cabinet
                                })
                            };
                        });
                    }
                });
            });

            // Set shift availability check
            this.serviceDetails.shift_availability_check = this.multiServicesBill[0].shift_availability_check;

            // Calculate total cost
            let totalCost = 0;
            for (const serviceKey in this.serviceDetails.service_details) {
                totalCost += parseInt(this.serviceDetails.service_details[serviceKey].total_cost);
            }

            this.serviceDetails.total_cost = totalCost;
            this.serviceDetails.estimated_cost = totalCost;

            this.bookMultipleService();
        },

        // =====================
        // Selection Logic
        // =====================
        selectServiceGroup(groupId) {
            this.activeTabs.activeServiceGroupId = groupId;
        },
        selectServiceType(typeId) {
            this.activeTabs.activeServiceTypeId = typeId;
        },



        /**
         * Parses the serviceSize data fetched from the server.
         * Creates a combinedSize property for each size item that includes name and size range.
         */
        parseSize() {
            this.sizeData = [];
            for (const key in this.serviceSize) {
                if (this.serviceSize.hasOwnProperty(key)) {
                    const size = this.serviceSize[key];
                    size.combinedSize = `${size.name} ( ${size.min_size} sq. m - ${size.max_size} sq. m )`;
                    this.sizeData.push(size);
                }
            }
            this.serviceSize = {};
        },

        /**
         * Filters size data for rope access type services.
         * Implement filtering logic based on rope access requirements.
         */
        ropeAccessFilter() {
            // Add rope access specific filtering logic here
            console.log('Applying rope access filter');
        },

        /**
         * Filters size data for facade cleaning services.
         * Implement filtering logic based on facade requirements.
         */
        facadeFilter() {
            // Add facade specific filtering logic here
            console.log('Applying facade filter');
        },

        /**
         * Filters size data for window cleaning services.
         * Implement filtering logic based on window requirements.
         */
        windowFilter() {
            this.windowSize = [];
            this.otherService.size = {};

            const filterCondition = this.window_check
                ? size => size.is_highprice_window
                : size => !size.is_highprice_window;

            this.windowSize = this.sizeData.filter(filterCondition);
        },

        /**
         * Calculates the total cost for a specific floor or apartment including base size cost and kitchen costs.
         * @param {number} buildingIndex - The building index (1-based)
         * @param {number} floorIndex - The floor index (1-based)
         * @param {number} apartmentIndex - Optional apartment index (1-based)
         */
        calculateFloorCost(buildingIndex, floorIndex, apartmentIndex = null) {
            // Initialize cost structure if needed
            if (!this.floorSectionCost[buildingIndex]) {
                this.$set(this.floorSectionCost, buildingIndex, {});
            }
            if (!this.floorSectionCost[buildingIndex][floorIndex]) {
                this.$set(this.floorSectionCost[buildingIndex], floorIndex, apartmentIndex ? {} : 0);
            }

            // Get the floor/apartment size object from windowSize data
            let selectedSizeName;
            if (apartmentIndex) {
                selectedSizeName = this.floorSize[buildingIndex] &&
                    this.floorSize[buildingIndex][floorIndex] &&
                    this.floorSize[buildingIndex][floorIndex][apartmentIndex];
            } else {
                selectedSizeName = this.floorSize[buildingIndex] && this.floorSize[buildingIndex][floorIndex];
            }

            const sizeObject = this.windowSize.find(size =>
                size.combinedSize === selectedSizeName || size.name === selectedSizeName
            );

            // Base cost from size
            let sectionCost = 0;
            if (sizeObject && sizeObject.cost) {
                sectionCost = parseFloat(sizeObject.cost) || 0;
            }

            // Add kitchen cost if kitchen cleaning is selected
            if (this.floorKitchenPreference[buildingIndex] &&
                this.floorKitchenPreference[buildingIndex][floorIndex]) {

                const kitchenSizeName = this.floorKitchenSize[buildingIndex] &&
                    this.floorKitchenSize[buildingIndex][floorIndex];

                // Find kitchen size cost from windowSize data
                const kitchenSizeObject = this.windowSize.find(size =>
                    size.combinedSize === kitchenSizeName || size.name === kitchenSizeName
                );

                if (kitchenSizeObject && kitchenSizeObject.cost) {
                    sectionCost += parseFloat(kitchenSizeObject.cost) || 0;
                }
            }

            // Store the calculated cost
            if (apartmentIndex) {
                if (typeof this.floorSectionCost[buildingIndex][floorIndex] !== 'object') {
                    this.$set(this.floorSectionCost[buildingIndex], floorIndex, {});
                }
                this.$set(this.floorSectionCost[buildingIndex][floorIndex], apartmentIndex, sectionCost);
            } else {
                this.$set(this.floorSectionCost[buildingIndex], floorIndex, sectionCost);
            }

            // Mark floor/apartment as completed
            if (apartmentIndex) {
                // Mark apartment as completed
                if (!this.completedApartments[buildingIndex]) {
                    this.$set(this.completedApartments, buildingIndex, {});
                }
                if (!this.completedApartments[buildingIndex][floorIndex]) {
                    this.$set(this.completedApartments[buildingIndex], floorIndex, {});
                }
                this.$set(this.completedApartments[buildingIndex][floorIndex], apartmentIndex, true);

                // Clear active apartment
                if (this.activeApartment[buildingIndex] &&
                    this.activeApartment[buildingIndex][floorIndex]) {
                    this.$set(this.activeApartment[buildingIndex][floorIndex], apartmentIndex, false);
                }
            } else {
                // Mark floor as completed
                if (!this.completedFloors[buildingIndex]) {
                    this.$set(this.completedFloors, buildingIndex, {});
                }
                this.$set(this.completedFloors[buildingIndex], floorIndex, true);

                // Clear active floor
                if (this.activeFloor[buildingIndex]) {
                    this.$set(this.activeFloor[buildingIndex], floorIndex, false);
                }
            }

            console.log(`Floor ${floorIndex} in Building ${buildingIndex} - Total Cost: ${sectionCost}`);

            // Add to cart
            this.addToCart(buildingIndex, floorIndex, apartmentIndex, sectionCost);

            return sectionCost;
        },

        /**
         * Add completed floor/apartment to cart
         */
        addToCart(buildingIndex, floorIndex, apartmentIndex, cost) {
            // Get service type name
            const serviceType = this.serviceTypes.find(st => st.id === this.activeTabs.activeServiceTypeId);
            const serviceName = serviceType ? serviceType.name : 'Service';

            // Get size name
            let selectedSizeName;
            if (apartmentIndex) {
                selectedSizeName = this.floorSize[buildingIndex]?.[floorIndex]?.[apartmentIndex];
            } else {
                selectedSizeName = this.floorSize[buildingIndex]?.[floorIndex];
            }

            // Create location string
            let location = `Building ${buildingIndex} Floor ${floorIndex}`;
            if (apartmentIndex) {
                location += ` Apartment ${apartmentIndex}`;
            }

            // Extract just the size name without the range
            let sizeName = selectedSizeName;
            if (selectedSizeName) {
                const match = selectedSizeName.match(/^([^(]+)/);
                if (match) {
                    sizeName = match[1].trim();
                }
            }

            // Add to cart
            this.cartItems.push({
                id: ++this.cartItemIdCounter, // Unique ID for each cart item
                serviceName: serviceName,
                location: location,
                sizeName: sizeName || 'N/A',
                cost: cost,
                buildingIndex: buildingIndex,
                floorIndex: floorIndex,
                apartmentIndex: apartmentIndex
            });
        },

        /**
         * Remove item from cart
         */
        removeCartItem(id) {
            const index = this.cartItems.findIndex(item => item.id === id);
            if (index !== -1) {
                this.cartItems.splice(index, 1);
            }
        },

        /**
         * Edit a completed floor - reopens the floor for editing
         */
        editFloor(buildingIndex, floorIndex) {
            if (!this.activeFloor[buildingIndex]) {
                this.$set(this.activeFloor, buildingIndex, {});
            }
            this.$set(this.activeFloor[buildingIndex], floorIndex, true);
        },

        /**
         * Check if a floor is completed
         */
        isFloorCompleted(buildingIndex, floorIndex) {
            return this.completedFloors[buildingIndex] && this.completedFloors[buildingIndex][floorIndex];
        },

        /**
         * Check if a floor is active/being edited
         */
        isFloorActive(buildingIndex, floorIndex) {
            if (this.activeFloor[buildingIndex] && this.activeFloor[buildingIndex][floorIndex]) {
                return true;
            }
            // If not explicitly set, show if not completed
            return !this.isFloorCompleted(buildingIndex, floorIndex);
        },

        /**
         * Check if an apartment is completed
         */
        isApartmentCompleted(buildingIndex, floorIndex, apartmentIndex) {
            return this.completedApartments[buildingIndex] &&
                this.completedApartments[buildingIndex][floorIndex] &&
                this.completedApartments[buildingIndex][floorIndex][apartmentIndex];
        },

        /**
         * Check if an apartment is active/being edited
         */
        isApartmentActive(buildingIndex, floorIndex, apartmentIndex) {
            if (this.activeApartment[buildingIndex] &&
                this.activeApartment[buildingIndex][floorIndex] &&
                this.activeApartment[buildingIndex][floorIndex][apartmentIndex]) {
                return true;
            }
            // If not explicitly set, show if not completed
            return !this.isApartmentCompleted(buildingIndex, floorIndex, apartmentIndex);
        },

        /**
         * Edit a completed apartment - reopens the apartment for editing
         */
        editApartment(buildingIndex, floorIndex, apartmentIndex) {
            if (!this.activeApartment[buildingIndex]) {
                this.$set(this.activeApartment, buildingIndex, {});
            }
            if (!this.activeApartment[buildingIndex][floorIndex]) {
                this.$set(this.activeApartment[buildingIndex], floorIndex, {});
            }
            this.$set(this.activeApartment[buildingIndex][floorIndex], apartmentIndex, true);
        },

        allApartmentsCompleted(buildingIndex, floorIndex) {
            const apartmentCount = this.floorApartmentCounts[buildingIndex] && this.floorApartmentCounts[buildingIndex][floorIndex];
            if (!apartmentCount) return false;

            for (let i = 1; i <= apartmentCount; i++) {
                if (!this.isApartmentCompleted(buildingIndex, floorIndex, i)) {
                    return false;
                }
            }
            return true;
        },
        resetOwlCarousel($carousel) {
            if ($carousel.hasClass('owl-loaded')) {
                $carousel.trigger('destroy.owl.carousel');
                $carousel.removeData('owl.carousel');
                $carousel.removeClass('owl-loaded owl-hidden');
                $carousel.find('.owl-stage-outer').children().unwrap();
                $carousel.find('.owl-stage-outer').unwrap();
                $carousel.find('.owl-nav, .owl-dots, .owl-next, .owl-prev').remove();
            }
        },

        reinitServiceCarousel() {
            setTimeout(() => {
                this.$nextTick(() => {
                    const $carousel = $('#service-carousel');
                    this.resetOwlCarousel($carousel);
                    const itemsCount = this.filteredServiceTypes.length;
                    if (itemsCount > 0 && !$carousel.hasClass('owl-loaded')) {
                        $carousel.owlCarousel(this.carouselSettings);
                    }
                });
            }, 100);
        },

        // =====================
        // Data Initialization Helpers
        // =====================
        initializeBuildingData(buildingIndex) {
            // Array of property names to initialize
            const properties = [
                'floorApartments', 'floorApartmentCounts', 'floorSize', 'floorWallType',
                'floorFloorType', 'floorCeilingType', 'floorRooms', 'floorBathrooms',
                'floorWindows', 'floorKitchenPreference', 'floorCabinetCleaning',
                'floorKitchenCondition', 'floorKitchenSize', 'floorOilResidue',
                'floorNoteFieldName', 'floorNoteValue', 'floorNotes', 'floorGeneralNotes',
                'floorSectionCost', 'completedFloors', 'activeFloor', 'completedApartments', 'activeApartment'
            ];

            // Initialize each property for the building if not already initialized
            properties.forEach(prop => {
                if (!this[prop][buildingIndex]) {
                    this.$set(this[prop], buildingIndex, {});
                }
            });
        },

        initializeFloorData(buildingIndex, floorIndex, apartmentCount) {
            // Define default values for each property
            const floorDefaults = {
                floorApartments: false,
                floorApartmentCounts: null,
                floorSize: null,
                floorWallType: [],
                floorFloorType: [],
                floorCeilingType: [],
                floorRooms: null,
                floorBathrooms: null,
                floorWindows: null,
                floorKitchenPreference: false,
                floorCabinetCleaning: false,
                floorKitchenCondition: null,
                floorKitchenSize: null,
                floorOilResidue: false,
                floorNoteFieldName: null,
                floorNoteValue: null,
                floorNotes: [],
                floorGeneralNotes: null
            };

            // Properties that should be indexed by apartment when apartments exist
            const apartmentLevelProperties = [
                'floorSize', 'floorWallType', 'floorFloorType', 'floorCeilingType',
                'floorRooms', 'floorBathrooms', 'floorWindows'
            ];

            // Set default values for each floor property
            Object.keys(floorDefaults).forEach(prop => {
                if (this[prop][buildingIndex][floorIndex] === undefined) {
                    // If apartments exist and this is an apartment-level property, create object for apartments
                    if (apartmentCount && apartmentLevelProperties.includes(prop)) {
                        const apartmentData = {};
                        for (let i = 1; i <= apartmentCount; i++) {
                            apartmentData[i] = Array.isArray(floorDefaults[prop]) ? [] : floorDefaults[prop];
                        }
                        this.$set(this[prop][buildingIndex], floorIndex, apartmentData);
                    } else {
                        this.$set(this[prop][buildingIndex], floorIndex, floorDefaults[prop]);
                    }
                }
            });

            // If apartments exist and were not set before, initialize them now
            if (apartmentCount) {
                const apartmentLevelProperties = [
                    'floorSize', 'floorWallType', 'floorFloorType', 'floorCeilingType',
                    'floorRooms', 'floorBathrooms', 'floorWindows'
                ];

                apartmentLevelProperties.forEach(prop => {
                    if (!Array.isArray(this[prop][buildingIndex][floorIndex]) && typeof this[prop][buildingIndex][floorIndex] !== 'object') {
                        const apartmentData = {};
                        for (let i = 1; i <= apartmentCount; i++) {
                            apartmentData[i] = floorDefaults[prop];
                        }
                        this.$set(this[prop][buildingIndex], floorIndex, apartmentData);
                    }
                });
            }
        },

        // =====================
        // Slot Selection Dialog Methods
        // =====================
        isSlotSelected(slotId) {
            return this.selectedDoubleSlots.includes(slotId);
        },

        formatSlotTime(time) {
            // Convert 24-hour format to 12-hour format with AM/PM
            const [hours, minutes] = time.split(':');
            const hour = parseInt(hours);
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
            return `${hour12.toString().padStart(2, '0')}:${minutes} ${ampm}`;
        },

        onDateChange(date) {
            this.dateSelected = date;
        },

        cancelSlotSelection() {
            this.scheduleDialog = false;
            this.selectedDoubleSlots = [];
            this.dateSelected = null;
        },

        confirmSlotSelection() {
            // Validate slot selection
            if (this.selectedDoubleSlots.length === 0) {
                alert('Please select at least one time slot');
                return;
            }

            // Validate date selection
            if (!this.dateSelected) {
                alert('Please select a date');
                return;
            }

            // Close dialog and process selection
            this.scheduleDialog = false;
            this.findVisits();
        },

        confirmOneTimeSlotSelection() {
            // Validate slot selection
            if (this.oneTimeSlotCounter() === 0) {
                alert('Please select at least one time slot');
                return;
            }

            // Validate date selection - check if date exists and is not empty/null
            if (!this.oneTimeDateSelected || this.oneTimeDateSelected.trim() === '') {
                alert('Please select a date');
                return;
            }

            // Additional check: ensure date is in valid format
            const selectedDate = moment(this.oneTimeDateSelected);
            if (!selectedDate.isValid()) {
                alert('Please select a valid date');
                return;
            }

            // Close dialog and proceed with one-time booking
            this.oneTimeSlotDialog = false;
            // Process one-time slot selection
            this.submitOneTimeSlots();
        }
    },
    mounted() {
        this.getServiceTypes();
        this.getAreaTypes();

        // Initialize one-time slot dialog with current date
        this.oneTimeDateSelected = this.getCurrentDate();
        this.loadAvailableSlots();

        // Initialize slot format mapping
        this.availableSlots.forEach(slot => {
            this.slotFormat[slot.id] = {
                start_time: slot.start_time,
                end_time: slot.end_time
            };
        });

        this.$nextTick(() => {
            $('#category-carousel').owlCarousel(this.carouselSettings);
            $('#service-carousel').owlCarousel(this.carouselSettings);
            this.highlightTodayInDatePicker();
        });
    },

    /**
     * Highlights today's date in the v-date-picker component
     */
    highlightTodayInDatePicker() {
        this.$nextTick(() => {
            // Get all date buttons in the calendar
            const dateButtons = document.querySelectorAll('.v-date-picker-table .v-btn');
            
            if (dateButtons.length === 0) {
                console.warn('No date buttons found in calendar');
                return;
            }
            
            const today = new Date();
            const todayDay = today.getDate().toString();
            const todayMonth = today.getMonth();
            const todayYear = today.getFullYear();
            
            // Get the calendar header to verify we're viewing the correct month/year
            const headerElement = document.querySelector('.v-date-picker-header__value');
            
            let isCurrentMonth = true;
            if (headerElement) {
                const headerText = headerElement.textContent.trim();
                const months = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December'];
                const currentMonth = months[todayMonth];
                const currentYear = todayYear.toString();
                isCurrentMonth = headerText.includes(currentMonth) && headerText.includes(currentYear);
            }
            
            // Process all date buttons
            dateButtons.forEach(button => {
                const buttonText = button.textContent.trim();
                
                // Check if button text matches today's day number and we're in current month
                if (buttonText === todayDay && isCurrentMonth) {
                    // Set the data attribute
                    button.setAttribute('data-today', 'true');
                    
                    // Apply inline styles to ensure they work
                    button.style.backgroundColor = '#E3F2FD';
                    button.style.color = '#4A6CB5';
                    button.style.border = '2px solid #4A6CB5';
                    button.style.fontWeight = '600';
                    button.style.boxShadow = '0 2px 4px rgba(74, 108, 181, 0.2)';
                    button.style.borderRadius = '4px';
                } else {
                    // Remove today attribute from other buttons
                    button.removeAttribute('data-today');
                }
            });
        });
    },
    watch: {
        oneTimeSlotDialog(newVal) {
            if (newVal) {
                // Initialize when dialog opens - use current date, not cached date
                const todayDate = moment().format('YYYY-MM-DD');
                this.oneTimeDateSelected = todayDate;
                this.currentSlotDay = 1;
                this.oneTimeSlots = {};
                this.oneTimeSlots[todayDate] = { slots: [] };
                
                // Initialize cleaningSet with default values if not set
                if (!this.cleaningSet || this.cleaningSet.length === 0) {
                    this.cleaningSet = [[4]]; // Default: 4 hours (2 slots) for first day
                }

                // Load available slots first
                this.loadAvailableSlots();

                // Highlight today's date with multiple timing attempts to ensure it works
                this.$nextTick(() => {
                    setTimeout(() => {
                        this.highlightTodayInDatePicker();
                    }, 150);
                });
                
                // Also try again after a longer delay
                setTimeout(() => {
                    this.highlightTodayInDatePicker();
                }, 300);
            }
        },
        'activeTabs.activeServiceTypeId'(newVal) {
            if (!newVal) return;

            // Find the service type name and call getSize
            const serviceType = this.serviceTypes.find(st => st.id === newVal);
            if (serviceType) {
                this.serviceType = serviceType.name;
                if (this.mediaUrl) {
                    this.getSize();
                }
            }
        },
        serviceGroups() {
            setTimeout(() => {
                this.$nextTick(() => {
                    const $carousel = $('#category-carousel');
                    this.resetOwlCarousel($carousel);
                    $carousel.owlCarousel(this.carouselSettings);
                });
            }, 50);
        },
        'activeTabs.service'(newVal) {
            if (newVal) {
                setTimeout(() => {
                    this.$nextTick(() => {
                        const $categoryCarousel = $('#category-carousel');
                        const $serviceCarousel = $('#service-carousel');

                        this.resetOwlCarousel($categoryCarousel);
                        $categoryCarousel.owlCarousel(this.carouselSettings);

                        this.resetOwlCarousel($serviceCarousel);
                        if (this.filteredServiceTypes.length > 0) {
                            $serviceCarousel.owlCarousel(this.carouselSettings);
                        }
                    });
                }, 100);
            }
        },
        filteredServiceTypes(newVal) {
            // Set the first filtered service type as active
            if (newVal.length > 0) {
                this.activeTabs.activeServiceTypeId = newVal[0].id;
            } else {
                this.activeTabs.activeServiceTypeId = null;
            }
            this.reinitServiceCarousel();
        },
        selectedNoOfFloors: {
            deep: true,
            handler(newVal) {
                if (!newVal || Object.keys(newVal).length === 0) return;

                // Initialize data for all floors in all buildings
                for (let buildingIndex in newVal) {
                    const floorCount = newVal[buildingIndex];
                    if (!floorCount) continue;

                    // Initialize building-level data structures
                    this.initializeBuildingData(buildingIndex);

                    // Initialize floor-level data
                    for (let i = 1; i <= floorCount; i++) {
                        const apartmentCount = this.floorApartmentCounts[buildingIndex] && this.floorApartmentCounts[buildingIndex][i];
                        this.initializeFloorData(buildingIndex, i, apartmentCount);
                    }
                }
            }
        },
        floorApartmentCounts: {
            deep: true,
            handler(newVal) {
                if (!newVal) return;

                // When apartment count changes, reinitialize floor data with new apartment count
                for (let buildingIndex in newVal) {
                    for (let floorIndex in newVal[buildingIndex]) {
                        const apartmentCount = newVal[buildingIndex][floorIndex];
                        if (apartmentCount) {
                            this.initializeFloorData(buildingIndex, parseInt(floorIndex), apartmentCount);
                        }
                    }
                }
            }
        },
        oneTimeDateSelected(newVal) {
            // Highlight today's date whenever the selected date changes
            setTimeout(() => {
                this.$nextTick(() => {
                    this.highlightTodayInDatePicker();
                });
            }, 50);
        }
    },
    computed: {
        filteredServiceTypes() {
            const seen = new Set();
            // Filter service types by the selected service group and remove duplicates
            const result = this.serviceTypes
                .filter(t => {
                    return t.service_group_id === this.activeTabs.activeServiceGroupId;
                })
                .filter(t => {
                    if (seen.has(t.name)) {
                        return false;
                    }
                    seen.add(t.name);
                    return true;
                });
            return result;
        },
        // Computed property for allowed location types for the selected service
        allowedLocationTypes() {
            const activeType = this.serviceTypes.find(
                t => t.id === this.activeTabs.activeServiceTypeId
            );
            if (!activeType) {
                return [];
            }
            const mapKey = activeType.name ? activeType.name.trim() : '';
            const typeSet = this.serviceLocationTypeMap[mapKey];
            if (!typeSet) {
                return [];
            }
            if (typeSet === 'primary') return this.primaryLocationTypes;
            if (typeSet === 'secondary') return this.secondaryLocationTypes;
            return [];
        },
        // Computed property to determine if location type dropdown should be shown
        showLocationTypeDropdown() {
            return this.allowedLocationTypes.length > 0;
        },
        // Computed property for building tabs
        buildingTabs() {
            if (!this.selectedNoOfBuildings) return [];
            const count = parseInt(this.selectedNoOfBuildings);
            return Array.from({ length: count }, (_, i) => `Building ${i + 1}`);
        },
        // Computed property for total section cost across all completed floors
        totalSectionCost() {
            let total = 0;
            for (let buildingIndex in this.floorSectionCost) {
                for (let floorIndex in this.floorSectionCost[buildingIndex]) {
                    const cost = this.floorSectionCost[buildingIndex][floorIndex];
                    if (typeof cost === 'number') {
                        // Floor-level cost (no apartments)
                        total += cost;
                    } else if (typeof cost === 'object') {
                        // Apartment-level costs
                        for (let apartmentIndex in cost) {
                            const apartmentCost = cost[apartmentIndex];
                            if (apartmentCost && typeof apartmentCost === 'number') {
                                total += apartmentCost;
                            }
                        }
                    }
                }
            }
            return total;
        },
        canSchedule() {
            // Basic validation
            if (!this.cleaningPolicy || !this.dateSelected) {
                return false;
            }

            // Validate slot selection matches required duration
            const requiredSlots = Math.ceil(this.selectedDuration.hours / 2);
            if (this.selectedDoubleSlots.length !== requiredSlots) {
                return false;
            }

            // Additional validation for subscription services
            if (this.normalizedCleaningPolicy === 'SUBSCRIPTION') {
                if (!this.subStat) return false;
                if (!this.no_of_visits || this.no_of_visits < 1) return false;
                if (this.subStat === 'Weekly' && this.prefDay.length === 0) return false;
            }

            return true;
        },
        selectedDateFormatted() {
            if (!this.dateSelected) return '';
            const date = new Date(this.dateSelected);
            const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return `${days[date.getDay()]}, ${months[date.getMonth()]} ${date.getDate()}`;
        },
        selectedYear() {
            if (!this.dateSelected) return new Date().getFullYear();
            return new Date(this.dateSelected).getFullYear();
        },
        selectedDays() {
            // For now, return an array with one day. You can expand this for multi-day selection
            return this.dateSelected ? [this.dateSelected] : [];
        },
        normalizedCleaningPolicy() {
            // Normalize user-friendly values to backend format
            if (this.cleaningPolicy === 'Subscription') return 'SUBSCRIPTION';
            if (this.cleaningPolicy === 'One Time Service') return 'ONE TIME SERVICE';
            return this.cleaningPolicy;
        }
    }
});