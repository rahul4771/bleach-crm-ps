new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: {
        activeTabs: {
            activeServiceGroupId: null,
            activeServiceTypeId: null,
            cart: false,
            schedule: false,
            service: true,
        },
        mediaUrl: '',
        serviceGroups: [],
        serviceTypes: [],
        snackbar: false, // Add snackbar property used in template
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
        selectedLocationType: null
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
         * On success, sets this.areaTypes to the returned array.
         * On error, logs the error to the console.
         */
        getAreaTypes() {
            fetch('/customer/ajax/getareatypes')
                .then(response => response.json())
                .then(data => {
                    this.areaTypes = data['area_types'];
                })
                .catch(error => {
                    console.log(error);
                });
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
        }
    }
});