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
            this.activeTabs.activeServiceGroupId = groupId;
        },
        reinitServiceCarousel() {
            
            // Wait for Vue to mount the new carousel element
            this.$nextTick(() => {
                setTimeout(() => {
                    const $carousel = $('#service-carousel');
                    const itemsCount = $carousel.find('.sr-service-card').length;
                    
                    if (itemsCount > 0 && !$carousel.hasClass('owl-loaded')) {
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
                    }
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
            setTimeout(() => {
                this.$nextTick(() => {
                    const $carousel = $('#category-carousel');
                    if ($carousel.hasClass('owl-loaded')) {
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
                });
            }, 50);
        },
        'activeTabs.service'(newVal) {
            if (newVal) {
                setTimeout(() => {
                    this.$nextTick(() => {
                        const $carousel = $('#category-carousel');
                        if ($carousel.hasClass('owl-loaded')) {
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
                    const match = t.service_group_id === this.activeTabs.activeServiceGroupId;
                    if (match) console.log('Filtered - Service Type:', t.name, 'Group ID:', t.service_group_id);
                    return match;
                })
                .filter(t => {
                    if (seen.has(t.name)) {
                        return false;
                    }
                    seen.add(t.name);
                    return true;
                });
            
            return result;
        }
    }
});