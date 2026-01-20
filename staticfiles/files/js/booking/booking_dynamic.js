new Vue({
    el: '#app',

    data: {
        serviceTypes: []
    },

    methods: {
        getServiceTypes() {
            fetch('/customer/booking/dynamic/get-service-types/')
                .then(response => response.json())
                .then(data => {
                    this.serviceTypes = data.service_types;
                })
                .catch(error => {
                    console.error('Error fetching service types:', error);
                });
        }
    },

    mounted() {
        this.getServiceTypes();
    }
});
