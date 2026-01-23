new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: {
        activeTabs: {
            cart: false,
            schedule: false,
            service: true,
        },
        serviceTypes: [],
        snackbar: false // Add snackbar property used in template
    },

    methods: {
        getServiceTypes() {
            fetch('/customer/booking/dynamic/get-service-types/')
                .then(response => response.json())
                .then(data => {
                    // console.log("data", data.service_types)
                    this.serviceTypes = data.service_types;
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