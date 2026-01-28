new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    delimiters: ['[[', ']]'],
    data: {
        snackbar: false, // Add snackbar property used in template
        mediaUrl: '',
        generalNotes: '', // Track general notes
        selectedLocationType: null,
        selectedAreaType: null,
        selectedLocationType: null,
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
        areaTypes: [],
        buildingNumbers: Array.from({ length: 15 }, (_, i) => i + 1),
        floorNumbers: Array.from({ length: 15 }, (_, i) => i + 1),
        serviceGroups: [],
        serviceTypes: [],
        serviceType: null,
        serviceSize: [],
        sizeData: [],
        ropeAccessTypes: [],
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

        // =====================
        // Selection Logic
        // =====================
        selectServiceGroup(groupId) {
            this.activeTabs.activeServiceGroupId = groupId;
        },
        selectServiceType(typeId) {
            this.activeTabs.activeServiceTypeId = typeId;
        },

        // =====================
        // Data Fetching & Initialization
        // =====================
        /**
         * Fetches service types and groups from the server, sets media URL, and selects the first service by default.
         * Also handles error by showing a snackbar notification.
         */
        getServiceTypes() {
            fetch('/common/staging/dynamic/get-service-types/')
                .then(response => response.json())
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
         * Normalizes 'Hourly Cleaning' to 'General Cleaning' before making the request.
         * After fetching, parses the size data and applies appropriate filters based on service type.
         */
        getSize() {
            let service = this.serviceType;
            if (service == 'Hourly Cleaning') {
                service = 'General Cleaning';
            }
            
            fetch(this.mediaUrl + "/customer/ajax/getservicesizeprice?service_type=" + service)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then((data) => {
                    this.serviceSize = data;
                    this.parseSize();
                    
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
                });
        },

        /**
         * Parses the serviceSize data fetched from the server.
         * Can be customized based on the structure of serviceSize.
         */
        parseSize() {
            // Basic implementation - adjust based on your actual data structure
            this.sizeData = this.serviceSize;
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
            // Add window specific filtering logic here
            console.log('Applying window filter');
        },

        // =====================
        // Carousel Logic
        // =====================
        reinitServiceCarousel() {
            this.$nextTick(() => {
                setTimeout(() => {
                    const $carousel = $('#service-carousel');
                    const itemsCount = $carousel.find('.sr-service-card').length;
                    if (itemsCount > 0 && !$carousel.hasClass('owl-loaded')) {
                        $carousel.owlCarousel(this.carouselSettings);
                    }
                }, 100);
            });
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
                'floorNoteFieldName', 'floorNoteValue', 'floorNotes', 'floorGeneralNotes'
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
    },
    mounted() {
        this.getServiceTypes();
        this.getAreaTypes();
        this.$nextTick(() => {
            $('#category-carousel').owlCarousel(this.carouselSettings);
            $('#service-carousel').owlCarousel(this.carouselSettings);
        });
    },
    watch: {
        'activeTabs.activeServiceTypeId'(newVal) {
            if (newVal) {
                // Find the service type name and call getSize
                const serviceType = this.serviceTypes.find(st => st.id === newVal);
                if (serviceType) {
                    this.serviceType = serviceType.name;
                    if (this.mediaUrl) {
                        this.getSize();
                    }
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
                        const $carousel = $('#category-carousel');
                        this.resetOwlCarousel($carousel);
                        $carousel.owlCarousel(this.carouselSettings);
                    });
                }, 50);
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
        }
    }
});