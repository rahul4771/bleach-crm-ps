const { createApp } = Vue;

createApp({
    // Application data
    data() {
        return {
            avatarBaseUrl: 'https://ui-avatars.com/api/',
            activePtab: null,
            successMsg: '',
            modalHeading: '',
            serviceTypes: [],
            productivities: [],
            serviceAddons: [],
            servicePriceRanges: [],
            serviceTypeId: '',
            colorCodes: [
                "6366f1",
                "10b981",
                "f59e0b",
                "ef4444",
                "8b5cf6",
                "06b6d4",
                "ec4899",
                "f97316",
                "84cc16",
                "0891b2"
            ],
            toggleDivs: {
                showList: true,
                showView: false,
                showManageServiceType: false,
                showProductivity: false,
                showAddons: false
            },
            viewServiceType: {
                title: '',
                name: '',
                arabicName: '',
                activeStatus: ''
            },
            validationErrors: {
                manageServiceType: {},
                manageProductivity: {}
            },
            serviceFormFields: {
                name: '',
                name_arabic: '',
                is_active: ''
            },
            categoryFormFields: {
                name: '',
                description: '',
                perhour_cleaning: '',
                max_cleaners: '',
                max_hours: '',
                min_cleaners: '',
                min_hours: '',
                is_active: ''
            },

        };
    },
    // Methods for handling service types
    methods: {
        // Handle view, edit, remove actions
        handleServiceViewBtnClick(serviceType) {
            this.toggleDivs.showList = false;
            this.toggleDivs.showView = true;
            this.toggleDivs.showProductivity = true;
            this.toggleDivs.showAddons = true;
            this.viewServiceType = {
                title: serviceType.name,
                name: serviceType.name,
                arabicName: serviceType.name_arabic,
                activeStatus: serviceType.is_active ? 'Active' : 'Inactive'
            }
            this.serviceTypeId = serviceType.id
        },
        handleEditServiceBtnClick(serviceType) {
            this.toggleDivs.showList = false;
            this.toggleDivs.showManageServiceType = true;
            this.toggleDivs.showProductivity = true;
            this.toggleDivs.showAddons = true;
            this.serviceTypeId = serviceType.id
            this.viewServiceType = {
                title: `Edit ${serviceType.name}`,
            };
            const form = document.getElementById('manage-service-form');
            if (form) {
                form.setAttribute('data-action', 'edit')

                this.serviceFormFields.name = serviceType.name || '';
                this.serviceFormFields.name_arabic = serviceType.name_arabic || '';
                this.serviceFormFields.is_active = serviceType.is_active ? 'active' : 'inactive';

                const hiddenName = 'editing_service_type_id';
                let hidden = form.querySelector(`input[name="${hiddenName}"]`);
                if (!hidden) {
                    hidden = document.createElement('input');
                    hidden.type = 'hidden';
                    hidden.name = hiddenName;
                    hidden.id = hiddenName;
                    form.appendChild(hidden);
                }
                hidden.value = serviceType.id || '';

            }

        },
        remove(student) {
            if (confirm(`Delete ${student.name}?`)) {
                this.students = this.students.filter(s => s.id !== student.id);
            }
        },
        // Handle add button clicks
        handleAddServiceBtnClick() {
            this.toggleDivs.showList = false;
            this.toggleDivs.showManageServiceType = true;
            this.validationErrors['manageServiceType'] = [];

            const form = document.getElementById('manage-service-form');
            if (form) {
                form.setAttribute('data-action', 'add')
            }
        },
        // Handle Add Category button click
        handleAddCategoryBtnClick() {
            const modal = document.getElementById('manage-service-type-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.modalHeading = 'Add Category';
                this.validationErrors['manageProductivity'] = [];
                const form = document.getElementById('manage-productivity-form');
                if (form) {
                    form.setAttribute('data-action', 'add')
                }
            }
        },
        // Handle back button action
        backButtonAction(view) {
            Object.keys(this.toggleDivs).forEach(key => {
                this.toggleDivs[key] = (key === view);
            });
            // this.
            this.setActiveProductivityTab(null);
            this.resetNewService();
        },
        setActiveProductivityTab(pid = null) {
            this.activePtab = pid
        },
        handleEditPriceRangeBtnClick(priceRange, productivityId) {
            // Logic to handle editing a price range
            alert(`Edit Price Range: ${priceRange.name} under Productivity ID: ${productivityId}`);
        },
        removePriceRange(priceRange, productivityId) {
            // Logic to handle removing a price range
            if (confirm(`Delete Price Range: ${priceRange.name}?`)) {
                if (this.servicePriceRanges[productivityId]) {
                    this.servicePriceRanges[productivityId] = this.servicePriceRanges[productivityId].filter(item => item.id !== priceRange.id);
                }
            }
        },
        // Close modal
        closeModal() {
            const modal = document.getElementsByClassName('modal');
            if (modal.length) {
                modal[0].classList.remove('in', 'show');
                modal[0].style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.getElementsByClassName('modal-backdrop');
                if (backdrop.length) {
                    backdrop[0].remove();
                }
            }
        },

        // Add or update service type
        submitServiceTypeForm() {
            this.validationErrors['manageServiceType'] = {};
            if (!this.serviceFormFields.name || !this.serviceFormFields.name.trim()) {
                this.validationErrors['manageServiceType']['serviceTypeName'] = 'Service name is required.';
            }
            if (!this.serviceFormFields.name_arabic || !this.serviceFormFields.name_arabic.trim()) {
                this.validationErrors['manageServiceType']['serviceTypeArabicName'] = 'Arabic name is required.';
            }
            const arabicRegex = /^[\u0600-\u06FF\s]+$/;
            if (this.serviceFormFields.name_arabic.trim().length > 0 && !arabicRegex.test(this.serviceFormFields.name_arabic)) {
                this.validationErrors['manageServiceType']['serviceTypeArabicName'] = 'Service name (Arabic) must contain only Arabic characters.';
            }
            if (this.serviceFormFields.is_active === '') {
                this.validationErrors['manageServiceType']['serviceTypeIsActive'] = 'Status is required.';
            }

            if (Object.keys(this.validationErrors['manageServiceType']).length) return;

            // prepare payload for backend (convert boolean to expected value)
            const payload = {
                new_service_name: this.serviceFormFields.name,
                new_service_name_arabic: this.serviceFormFields.name_arabic,
                new_service_is_active: this.serviceFormFields.is_active
            };

            const form = document.getElementById('manage-service-form');
            const formAction = form.getAttribute('data-action')
            if (formAction === 'add') {
                this.createServiceType(this.toFormData(payload));
            } else {
                const serviceId = form.querySelector('input#editing_service_type_id, input[name="editing_service_type_id"]');
                this.updateServiceType(this.toFormData(payload), serviceId.value);
            }

        },
        // Add or update productivity category
        submitProductivityForm() {
            this.validationErrors.manageProductivity = {};

            // client-side validation
            if (!this.categoryFormFields.name || !this.categoryFormFields.name.trim()) {
                this.validationErrors.manageProductivity.categoryName = 'Category Name is required.';
            }

            if (this.categoryFormFields.is_active === '') {
                this.validationErrors.manageProductivity.status = 'Status is required.';
            }

            this.validateNumberInput(this.categoryFormFields.perhour_cleaning, false, "Please enter a valid non-negative number", 'perhour_cleaning');
            this.validateNumberInput(this.categoryFormFields.max_cleaners, true, "Please enter a valid non-negative integer", 'max_cleaners');
            this.validateNumberInput(this.categoryFormFields.max_hours, false, "Please enter a valid non-negative number", 'max_hours');
            this.validateNumberInput(this.categoryFormFields.min_cleaners, true, "Please enter a valid non-negative integer", 'min_cleaners');
            this.validateNumberInput(this.categoryFormFields.min_hours, false, "Please enter a valid non-negative number", 'min_hours');


            if (Object.keys(this.validationErrors.manageProductivity).length > 0) {
                return;
            }

            // normalize is_active to boolean (select uses :value true/false, fallback handles string)
            const rawStatus = this.categoryFormFields.is_active;
            let isActive = null;
            if (rawStatus === true || rawStatus === 'true') isActive = true;
            else if (rawStatus === false || rawStatus === 'false') isActive = false;

            const payload = {
                name: this.categoryFormFields.name.trim(),
                description: this.categoryFormFields.description,
                perhour_cleaning: this.categoryFormFields.perhour_cleaning,
                max_cleaners: this.categoryFormFields.max_cleaners,
                max_hours: this.categoryFormFields.max_hours,
                min_cleaners: this.categoryFormFields.min_cleaners,
                min_hours: this.categoryFormFields.min_hours,
                is_active: isActive
            };

            const form = document.getElementById('manage-productivity-form');
            const formAction = form.getAttribute('data-action')
            this.createProductivityCategory(this.toFormData(payload));
            if (formAction === 'add') {
                this.createProductivityCategory(this.toFormData(payload));
            } else {

            }

        },
        // Fetch service types from the server
        getServiceTypes() {
            fetch('get-service-types/')
                .then(response => response.json())
                .then(data => {
                    if (data.service_types) {
                        this.serviceTypes = data.service_types.map(serviceType => {
                            return {
                                ...serviceType,
                                avatar: `${this.avatarBaseUrl}?name=${encodeURIComponent(serviceType.name)}&background=${this.colorCodes[serviceType.id % this.colorCodes.length]}&color=fff`
                            };
                        });
                    }
                    if (data.service_productivities) {
                        const grouped = {};
                        data.service_productivities.forEach(p => {
                            const key = String(p.service_type_id ?? '0');
                            if (!grouped[key]) grouped[key] = [];
                            grouped[key].push(p);
                        });
                        this.productivities = grouped;
                    }
                    if (data.service_addons) {
                        const grouped = {};
                        data.service_addons.forEach(p => {
                            const key = String(p.service_type_id ?? '0');
                            if (!grouped[key]) grouped[key] = [];
                            p.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(p.name)}&background=${this.colorCodes[p.id % this.colorCodes.length]}&color=fff`;
                            grouped[key].push(p);
                        });
                        this.serviceAddons = grouped;
                    }
                    if (data.service_price_ranges) {
                        const grouped = {};
                        data.service_price_ranges.forEach(p => {
                            const key = String(p.service_productivity_id ?? '0');
                            if (!grouped[key]) grouped[key] = [];
                            p.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(p.name)}&background=${this.colorCodes[p.id % this.colorCodes.length]}&color=fff`;
                            grouped[key].push(p);
                        });
                        this.servicePriceRanges = grouped;
                    }

                })
                .catch(error => {
                    console.error('Error fetching service types:', error);
                });
        },
        // Create a new service type
        createServiceType(formData) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;

            const url = `${baseUrl}/common/add-service-type/`
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                },
                body: formData
            })
                .then(r => r.json())
                .then(data => {
                    if (!data.success) {
                        if (data.error_field && data.error_message) {
                            if (data.error_field === 'new_service_name') {
                                this.validationErrors['manageServiceType']['serviceTypeName'] = data.error_message;
                            }
                            if (data.error_field === 'new_service_name_arabic') {
                                this.validationErrors['manageServiceType']['serviceTypeArabicName'] = data.error_message;
                            }
                            if (data.error_field === 'new_service_is_active') {
                                this.validationErrors['manageServiceType']['serviceTypeIsActive'] = data.error_message;
                            }
                        }
                    } else {
                        this.successMsg = data.service_type
                            ? `Service type "${data.service_type}" added successfully.`
                            : 'Service type added successfully.';
                        this.resetNewService();
                        setTimeout(() => { this.successMsg = ''; }, 5000);

                    }
                }).catch(err => console.error(err));

        },
        // Update an existing service type
        updateServiceType(formData, serviceId) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;

            const url = `${baseUrl}/common/update-service-type/${serviceId}/`
            fetch(url, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                },
                body: formData
            })
                .then(r => r.json())
                .then(data => {
                    if (!data.success) {
                        if (data.error_field && data.error_message) {
                            if (data.error_field === 'edit_service_name') {
                                this.validationErrors['manageServiceType']['serviceTypeName'] = data.error_message;
                            }
                            if (data.error_field === 'edit_service_name_arabic') {
                                this.validationErrors['manageServiceType']['serviceTypeArabicName'] = data.error_message;
                            }
                            if (data.error_field === 'edit_service_is_active') {
                                this.validationErrors['manageServiceType']['serviceTypeIsActive'] = data.error_message;
                            }
                        }
                    } else {
                        this.successMsg = data.service_type
                            ? `Service type "${data.service_type}" updated successfully.`
                            : 'Service type updated successfully.';
                        this.resetNewService();
                        setTimeout(() => { this.successMsg = ''; }, 5000);

                    }
                }).catch(err => console.error(err));

        },
        // Create a new productivity category
        createProductivityCategory(formData) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/add-service-productivity/`
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                },
                body: formData
            })
                .then(res => {
                    if (!res.ok) throw res;
                    return res.json();
                })
                .then(data => {
                    this.successMsg = 'Category saved successfully.';
                    this.closeModal();
                    // refresh list or update local state
                    this.loadProductivitiesForServiceType(this.serviceTypeId);
                })
                .catch(async err => {
                    // map server validation errors if present
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.manageProductivity = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        },

        // utility functions
        getCookie(name) {
            const v = document.cookie.split('; ').find(row => row.startsWith(name + '='));
            return v ? decodeURIComponent(v.split('=')[1]) : null;
        },
        toFormData(payload) {
            const fd = new FormData();
            for (const k in payload) fd.append(k, payload[k]);
            return fd;
        },
        resetNewService() {
            this.newService = { name: '', name_arabic: '', is_active: '' };
            this.validationErrors['manageServiceType'] = {};
        },
        formatCurrency(value) {
            if (value == null || value === '') return '--';
            const n = Number(value);
            if (Number.isNaN(n)) return value;
            const formatted = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 3,
                maximumFractionDigits: 3
            }).format(n);
            return `${formatted} KD`;
        },
        validateNumberInput(value, mustBeInteger = false, errorMessage = 'Invalid number', fieldKey = null) {
            // treat empty/null/undefined as valid (field optional)
            if (value === '' || value === null || value === undefined) {
                if (fieldKey) delete this.validationErrors.manageProductivity[fieldKey];
                return true;
            }
            const num = Number(value);
            if (Number.isNaN(num) || num < 0) {
                if (fieldKey) this.validationErrors.manageProductivity[fieldKey] = errorMessage;
                return false;
            }
            if (mustBeInteger && !Number.isInteger(num)) {
                if (fieldKey) this.validationErrors.manageProductivity[fieldKey] = errorMessage;
                return false;
            }
            if (fieldKey) delete this.validationErrors.manageProductivity[fieldKey];
            return true;
        },


    },
    // Lifecycle hook to fetch service types on mount
    mounted() {
        this.getServiceTypes();
    }
}).mount('#app');