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

            fetch(`/customer/ajax/getservicesizeprice?service_type=${service}`)
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

                    // this.facadeFilter();
                    this.windowFilter();
                })
                .catch((error) => {
                    console.error('Error fetching size data:', error);
                    this.snackbar = true;
                });
        },

        /**
         * Parses the serviceSize data fetched from the server.
         * Creates a combinedSize property for each size item that includes name and size range.
         */
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
        }
    }
});