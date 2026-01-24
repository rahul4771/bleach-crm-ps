new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: {
        activeTabs: {
            cart: false,
            schedule: false,
            service: true,
        },
        serviceGroups: [],
        serviceTypes: [],
        snackbar: false // Add snackbar property used in template
    },

    methods: {
        getServiceTypes() {
            fetch('/staging/dynamic/get-service-types/')
                .then(response => response.json())
                .then(data => {
                    this.serviceGroups = data.service_groups ?? [];
                    this.serviceTypes = data.service_types ?? [];
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
    }
});