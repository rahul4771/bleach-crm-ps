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
        snackbar: false // Add snackbar property used in template
    },

    methods: {
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
                    // Optionally show error in snackbar
                    this.snackbar = true;
                });
        },
        selectServiceGroup(groupId) {
            console.log('=== selectServiceGroup called ===');
            console.log('Previous activeServiceGroupId:', this.activeTabs.activeServiceGroupId);
            console.log('New groupId:', groupId);
            this.activeTabs.activeServiceGroupId = groupId;
            console.log('activeServiceGroupId updated to:', this.activeTabs.activeServiceGroupId);
        },
        reinitServiceCarousel() {
            console.log('=== START reinitServiceCarousel ===');
            console.log('Current activeServiceGroupId:', this.activeTabs.activeServiceGroupId);
            console.log('Current filteredServiceTypes count:', this.filteredServiceTypes.length);
            
            // Wait for Vue to mount the new carousel element
            this.$nextTick(() => {
                setTimeout(() => {
                    const $carousel = $('#service-carousel');
                    const itemsCount = $carousel.find('.sr-service-card').length;
                    console.log('Items in DOM:', itemsCount);
                    
                    if (itemsCount > 0 && !$carousel.hasClass('owl-loaded')) {
                        console.log('Initializing carousel with', itemsCount, 'items');
                        $carousel.owlCarousel({
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
                        console.log('Carousel initialized successfully');
                    } else if ($carousel.hasClass('owl-loaded')) {
                        console.log('Carousel already loaded, skipping init');
                    } else {
                        console.log('No items found, skipping carousel init');
                    }
                    console.log('=== END reinitServiceCarousel ===');
                }, 100);
            });
        },
        // select service type
        selectServiceType(typeId) {
            this.activeTabs.activeServiceTypeId = typeId;
        }
    },

    mounted() {
        this.getServiceTypes();
        this.$nextTick(() => {
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
    watch: {
        serviceGroups() {
            console.log('=== serviceGroups Watcher ===');
            console.log('serviceGroups changed, count:', this.serviceGroups.length);
            setTimeout(() => {
                this.$nextTick(() => {
                    const $carousel = $('#category-carousel');
                    if ($carousel.hasClass('owl-loaded')) {
                        console.log('Destroying category carousel...');
                        $carousel.trigger('destroy.owl.carousel');
                        $carousel.removeData('owl.carousel');
                        $carousel.removeClass('owl-loaded owl-hidden');
                        // Unwrap the owl-stage structure
                        $carousel.find('.owl-stage-outer').children().unwrap();
                        $carousel.find('.owl-stage-outer').unwrap();
                        $carousel.find('.owl-nav, .owl-dots, .owl-next, .owl-prev').remove();
                    }
                    $carousel.owlCarousel({
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
                    console.log('Category carousel re-initialized');
                });
            }, 50);
        },
        'activeTabs.service'(newVal) {
            console.log('=== activeTabs.service Watcher ===');
            console.log('activeTabs.service changed to:', newVal);
            if (newVal) {
                setTimeout(() => {
                    this.$nextTick(() => {
                        const $carousel = $('#category-carousel');
                        if ($carousel.hasClass('owl-loaded')) {
                            console.log('Destroying category carousel...');
                            $carousel.trigger('destroy.owl.carousel');
                            $carousel.removeData('owl.carousel');
                            $carousel.removeClass('owl-loaded owl-hidden');
                            // Unwrap the owl-stage structure
                            $carousel.find('.owl-stage-outer').children().unwrap();
                            $carousel.find('.owl-stage-outer').unwrap();
                            $carousel.find('.owl-nav, .owl-dots, .owl-next, .owl-prev').remove();
                        }
                        $carousel.owlCarousel({
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
                        console.log('Category carousel re-initialized');
                    });
                }, 50);
            }
        },
        filteredServiceTypes(newVal) {
            console.log('=== START filteredServiceTypes Watcher ===');
            console.log('Old activeServiceTypeId:', this.activeTabs.activeServiceTypeId);
            console.log('Filtered Service Types count:', newVal.length);
            console.log('Filtered Service Types:', newVal);
            
            // Set the first filtered service type as active
            if (newVal.length > 0) {
                this.activeTabs.activeServiceTypeId = newVal[0].id;
                console.log('Set activeServiceTypeId to:', newVal[0].id);
            } else {
                this.activeTabs.activeServiceTypeId = null;
                console.log('No service types, set activeServiceTypeId to null');
            }
            
            console.log('Calling reinitServiceCarousel...');
            this.reinitServiceCarousel();
            console.log('=== END filteredServiceTypes Watcher ===');
        }
    },
    computed: {
        filteredServiceTypes() {
            const seen = new Set();
            // Filter service types by the selected service group and remove duplicates
            const result = this.serviceTypes
                .filter(t => {
                    const match = t.service_group_id === this.activeTabs.activeServiceGroupId;
                    if (match) console.log('Filtered - Service Type:', t.name, 'Group ID:', t.service_group_id);
                    return match;
                })
                .filter(t => {
                    if (seen.has(t.name)) {
                        console.log('Duplicate found:', t.name, '- skipping');
                        return false;
                    }
                    seen.add(t.name);
                    return true;
                });
            
            console.log('Computed filteredServiceTypes result count:', result.length);
            return result;
        }
    }
});