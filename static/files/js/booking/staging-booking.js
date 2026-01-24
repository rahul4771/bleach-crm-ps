new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: {
        activeTabs: {
            cart: false,
            schedule: false,
            service: true,
            activeServiceId: null
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
                    if (this.serviceGroups.length > 0) {
                        this.activeTabs.activeServiceId = this.serviceGroups[0].id;
                    }
                })
                .catch(error => {
                    console.error('Error fetching service types:', error);
                    // Optionally show error in snackbar
                    this.snackbar = true;
                });
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
        });
    },
    watch: {
        serviceGroups() {
            this.$nextTick(() => {
                const $carousel = $('#category-carousel');
                if ($carousel.hasClass('owl-loaded')) {
                    $carousel.trigger('destroy.owl.carousel');
                    $carousel.removeClass('owl-loaded owl-hidden');
                    $carousel.find('.owl-stage-outer').children().unwrap();
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
        }
    }
});