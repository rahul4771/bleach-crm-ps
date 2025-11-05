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
            // renamed from `delete` to avoid using the reserved keyword in template expressions
            deleteModal: {
                softText: '',
                strongText: '',
            },
            viewServiceType: {
                title: '',
                name: '',
                arabicName: '',
                activeStatus: ''
            },
            validationErrors: {
                manageServiceType: {},
                manageProductivity: {},
                managePriceRange: {},
                manageAddOn: {}
            },
            serviceFormFields: {
                name: '',
                name_arabic: '',
                is_active: ''
            },
            categoryFormFields: {
                id: '',
                name: '',
                description: '',
                perhour_cleaning: '',
                max_cleaners: '',
                max_hours: '',
                min_cleaners: '',
                min_hours: '',
                is_active: false,
                service_type_id: ''
            },
            priceRangeFormFields: {
                id: '',
                name: '',
                price: '',
                minimum_area: '',
                maximum_area: '',
                unit_price: '',
                status: false,
                productivity_id: '',
                service_type_id: ''
            },
            addonFormFields: {
                id: '',
                item: '',
                category_name: '',
                size: '',
                price: '',
                productivity: '',
                service_type_id: '',
                status: false
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
                hidden.value = serviceType.id ?? '';

            }

        },
        remove(serviceType) {
            if (confirm(`Delete ${serviceType.name}?`)) {
                this.serviceTypes = this.serviceTypes.filter(s => s.id !== serviceType.id);
            }
        },
        // Handle add button clicks
        handleAddServiceBtnClick() {
            this.toggleDivs.showList = false;
            this.toggleDivs.showManageServiceType = true;
            this.validationErrors['manageServiceType'] = [];
            this.viewServiceType = {
                title: '',
            };

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
                    form.setAttribute('data-action', 'add');
                    this.categoryFormFields = {
                        id: '',
                        name: '',
                        description: '',
                        perhour_cleaning: '',
                        max_cleaners: '',
                        max_hours: '',
                        min_cleaners: '',
                        min_hours: '',
                        is_active: '',
                        service_type_id: this.serviceTypeId,
                    }
                }
            }
        },
        // Handle Edit Productivity button click
        handleEditProductivityBtnClick(productivity) {
            const modal = document.getElementById('manage-service-type-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.modalHeading = `Edit ${productivity.name}`;
                this.validationErrors['manageProductivity'] = [];
                const form = document.getElementById('manage-productivity-form');
                if (form) {
                    form.setAttribute('data-action', 'edit');
                    this.categoryFormFields = {
                        id: productivity.id || '',
                        name: productivity.name || '',
                        description: productivity.description || '',
                        perhour_cleaning: productivity.perhour_cleaning || '',
                        max_cleaners: productivity.max_cleaners || '',
                        max_hours: productivity.max_hours || '',
                        min_cleaners: productivity.min_cleaners || '',
                        min_hours: productivity.min_hours || '',
                        is_active: productivity.is_active,
                        service_type_id: this.serviceTypeId,
                    }
                }
            }

        },
        // Handle Add Price Range button click
        handleAddPriceRangeBtnClick() {
            const modal = document.getElementById('manage-price-range-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.modalHeading = 'Add Price Range';
                this.validationErrors['managePriceRange'] = [];
                const form = document.getElementById('manage-price-range-form');
                if (form) {
                    form.setAttribute('data-action', 'add');
                    this.priceRangeFormFields = {
                        id: '',
                        name: '',
                        price: '',
                        minimum_area: '',
                        maximum_area: '',
                        unit_price: '',
                        status: this.priceRangeFormFields.status || false,
                        productivity_id: this.activePtab || this.productivities[String(this.serviceTypeId ?? '0')]?.[0]?.id || '',
                        service_type_id: this.serviceTypeId || ''
                    }
                }
            }
        },
        // Handle Add Add-on (Item) button click
        handleAddAddonBtnClick() {
            const modal = document.getElementById('manage-addon-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.modalHeading = 'Add New Addon';
                this.validationErrors['manageAddOn'] = [];
                const form = document.getElementById('manage-addon-form');
                if (form) {
                    form.setAttribute('data-action', 'add');
                    this.addonFormFields = {
                        id: '',
                        category_name: '',
                        size: '',
                        price: '',
                        productivity: '',
                        service_type_id: this.serviceTypeId || '',
                        status: false
                    }
                }
            }
        },
        
        // Submit Add-on form (create or update via API)
        submitAddonForm() {
            this.validationErrors.manageAddOn = {};
            if (!this.addonFormFields.item || !this.addonFormFields.item.trim()) {
                this.validationErrors.manageAddOn.categoryName = 'Category Name is required.';
            }
            const priceVal = this.addonFormFields.price;
            if (priceVal === '' || priceVal === null || priceVal === undefined) {
                this.validationErrors.manageAddOn.price = 'Price is required.';
            } else {
                const num = Number(priceVal);
                if (Number.isNaN(num) || num < 0) {
                    this.validationErrors.manageAddOn.price = 'Please enter a valid non-negative number for price';
                } else {
                    delete this.validationErrors.manageAddOn.price;
                }
            }

            if (Object.keys(this.validationErrors.manageAddOn).length > 0) return;

            const payload = {
                id: this.addonFormFields.id,
                name: this.addonFormFields.item ? this.addonFormFields.item.trim() : '',
                category: this.addonFormFields.category_name ? this.addonFormFields.category_name.trim() : '',
                size: this.addonFormFields.size,
                price: this.addonFormFields.price,
                productivity: this.addonFormFields.productivity,
                service_type: this.addonFormFields.service_type_id || this.serviceTypeId || '',
                is_active: this.addonFormFields.status ? 1 : 0
            };

            const form = document.getElementById('manage-addon-form');
            const formAction = form ? form.getAttribute('data-action') : 'add';
            if (formAction === 'add') {
                this.createAddOn(this.toFormData(payload), payload);
            } else {
                const id = this.addonFormFields.id;
                this.updateAddOn(this.toFormData(payload), id, payload);
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
            const modal = document.getElementById('manage-price-range-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.modalHeading = `Edit ${priceRange.name}`;
                this.validationErrors['managePriceRange'] = [];
                const form = document.getElementById('manage-price-range-form');
                if (form) {
                    form.setAttribute('data-action', 'edit');
                    this.priceRangeFormFields = {
                        id: priceRange.id,
                        name: priceRange.name,
                        price: priceRange.price,
                        minimum_area: priceRange.minimum_area,
                        maximum_area: priceRange.maximum_area,
                        unit_price: priceRange.unit_price,
                        status: priceRange.is_active,
                        productivity_id: productivityId || '',
                        service_type_id: this.serviceTypeId || ''
                    }
                }
            }
        },
        removePriceRange(priceRange, productivityId) {
            const modal = document.getElementById('delete-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.deleteModal.softText = `Are you sure you want to continue with this action? This action will update the status of the price range "${priceRange.name}".`;

            }
        },
        confirmDelete() {

        },
        // Close modal(s).
        // If an Event is passed (e.g. closeModal($event)) we locate the closest .modal from the event
        // target and close only that modal. If omitted, close all open modals.
        // This keeps modal stacking/backdrop cleanup correct.
        closeModal(event = null) {
            const hideModal = (m) => {
                try {
                    m.classList.remove('in', 'show');
                    m.style.display = 'none';
                    m.setAttribute('aria-hidden', 'true');
                } catch (e) {
                    // ignore
                }
            };

            let targetModal = null;
            if (event && (typeof event === 'object') && (event.target || event.currentTarget)) {
                targetModal = event.target && event.target.closest ? event.target.closest('.modal') : (event.currentTarget && event.currentTarget.closest ? event.currentTarget.closest('.modal') : null);
            }

            if (targetModal) {
                hideModal(targetModal);
            } else {
                const modals = Array.from(document.querySelectorAll('.modal.show, .modal.in.show'));
                modals.forEach(m => hideModal(m));
            }

            // remove all backdrops (there may be multiple)
            const backdrops = Array.from(document.querySelectorAll('.modal-backdrop'));
            backdrops.forEach(b => b.remove());

            const remaining = document.querySelectorAll('.modal.show, .modal.in.show');
            if (!remaining.length) {
                document.body.classList.remove('modal-open');
            }
        },

        /* Form submission methods 
         * Add or update service type 
         */
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
        /* Add or update productivity category */
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
                productivity_name: this.categoryFormFields.name.trim(),
                productivity_description: this.categoryFormFields.description,
                productivity_cleaning_hours: this.categoryFormFields.perhour_cleaning,
                productivity_max_cleaners: this.categoryFormFields.max_cleaners,
                productivity_max_hours: this.categoryFormFields.max_hours,
                productivity_min_cleaners: this.categoryFormFields.min_cleaners,
                productivity_min_hours: this.categoryFormFields.min_hours,
                status: isActive ? 'active' : 'inactive',
                productivity_service_type_id: this.serviceTypeId
            };

            const form = document.getElementById('manage-productivity-form');
            const formAction = form.getAttribute('data-action')
            if (formAction === 'add') {
                this.createProductivityCategory(this.toFormData(payload));
            } else {
                this.updateProductivityCategory(this.toFormData(payload), this.categoryFormFields.id);
            }

        },

        /* Add or update price range */
        submitPriceRangeForm() {
            this.validationErrors.managePriceRange = {};

            // basic validation
            if (!this.priceRangeFormFields.name || !this.priceRangeFormFields.name.trim()) {
                this.validationErrors.managePriceRange.name = 'Item name is required.';
            }

            // price is required and must be a non-negative number
            const priceVal = this.priceRangeFormFields.price;
            if (priceVal === '' || priceVal === null || priceVal === undefined) {
                this.validationErrors.managePriceRange.price = 'Price is required.';
            } else {
                const num = Number(priceVal);
                if (Number.isNaN(num) || num < 0) {
                    this.validationErrors.managePriceRange.price = 'Please enter a valid non-negative number for price';
                } else {
                    delete this.validationErrors.managePriceRange.price;
                }
            }

            // optional integer fields for areas (minimum_area -> minimumArea key in errors)
            const minArea = this.priceRangeFormFields.minimum_area;
            if (minArea !== '' && minArea !== null && minArea !== undefined) {
                const n = Number(minArea);
                if (Number.isNaN(n) || n < 0 || !Number.isInteger(n)) {
                    this.validationErrors.managePriceRange.minimumArea = 'Please enter a valid non-negative integer';
                } else {
                    delete this.validationErrors.managePriceRange.minimumArea;
                }
            } else {
                delete this.validationErrors.managePriceRange.minimumArea;
            }

            const maxArea = this.priceRangeFormFields.maximum_area;
            if (maxArea !== '' && maxArea !== null && maxArea !== undefined) {
                const n2 = Number(maxArea);
                if (Number.isNaN(n2) || n2 < 0 || !Number.isInteger(n2)) {
                    this.validationErrors.managePriceRange.maximumArea = 'Please enter a valid non-negative integer';
                } else {
                    delete this.validationErrors.managePriceRange.maximumArea;
                }
            } else {
                delete this.validationErrors.managePriceRange.maximumArea;
            }

            // optional unit_price (decimal)
            const unitPrice = this.priceRangeFormFields.unit_price;
            if (unitPrice !== '' && unitPrice !== null && unitPrice !== undefined) {
                const up = Number(unitPrice);
                if (Number.isNaN(up) || up < 0) {
                    this.validationErrors.managePriceRange.unitPrice = 'Please enter a valid non-negative number';
                } else {
                    delete this.validationErrors.managePriceRange.unitPrice;
                }
            } else {
                delete this.validationErrors.managePriceRange.unitPrice;
            }

            if (this.priceRangeFormFields.status === '') {
                this.validationErrors.managePriceRange.status = 'Status is required.';
            }

            if (Object.keys(this.validationErrors.managePriceRange).length > 0) return;

            const payload = {
                name: this.priceRangeFormFields.name && this.priceRangeFormFields.name.trim(),
                price: this.priceRangeFormFields.price,
                minimum_area: this.priceRangeFormFields.minimum_area,
                maximum_area: this.priceRangeFormFields.maximum_area,
                unit_price: this.priceRangeFormFields.unit_price,
                productivity_id: this.priceRangeFormFields.productivity_id,
                service_type: this.priceRangeFormFields.service_type_id,
                status: this.priceRangeFormFields.status ? 1 : 0
            };

            const form = document.getElementById('manage-price-range-form');
            const formAction = form ? form.getAttribute('data-action') : 'add';
            if (formAction === 'add') {
                this.createPriceRange(this.toFormData(payload));
            } else {
                const id = this.priceRangeFormFields.id;
                this.updatePriceRange(this.toFormData(payload), id);
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

                    this.closeModal();
                    const key = String(this.serviceTypeId ?? '0');
                    if (!this.productivities[key]) this.productivities[key] = [];
                    this.productivities[key].push(data.service_productivity);
                    this.successMsg = 'Category saved successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);

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
        updateProductivityCategory(formData, productivityId) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/update-service-productivity/${productivityId}`
            fetch(url, {
                method: 'PUT',
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

                    this.closeModal();
                    const key = String(this.serviceTypeId ?? '0');
                    if (!this.productivities[key]) this.productivities[key] = [];
                    const index = this.productivities[key].findIndex(p => p.id === data.service_productivity.id);
                    if (index !== -1) {
                        this.productivities[key].splice(index, 1, data.service_productivity);
                    }
                    this.successMsg = data.service_productivity ? `Category ${data.service_productivity.name} updated successfully.` : 'Category updated successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);

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

        // Create a new price range
        createPriceRange(formData) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/add-service-price-range/`;
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
                    this.closeModal();
                    const key = String(this.priceRangeFormFields.productivity_id ?? this.serviceTypeId ?? '0');
                    if (!this.servicePriceRanges[key]) this.servicePriceRanges[key] = [];
                    // assume backend returns `service_price_range`
                    const item = data.service_price_range || data.service_price_ranges || data;
                    item.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(item.name)}&background=${this.colorCodes[item.id % this.colorCodes.length]}&color=fff`;
                    this.servicePriceRanges[key].push(item);
                    this.successMsg = 'Price range saved successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.managePriceRange = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        },

        // Update an existing price range
        updatePriceRange(formData, priceRangeId) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/update-service-price-range/${priceRangeId}`;
            fetch(url, {
                method: 'PUT',
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
                    this.closeModal();
                    const key = String(this.priceRangeFormFields.productivity_id ?? this.serviceTypeId ?? '0');
                    if (!this.servicePriceRanges[key]) this.servicePriceRanges[key] = [];
                    const updated = data.service_price_range || data;
                    updated.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(updated.name)}&background=${this.colorCodes[updated.id % this.colorCodes.length]}&color=fff`;
                    const index = this.servicePriceRanges[key].findIndex(p => p.id === updated.id);
                    if (index !== -1) this.servicePriceRanges[key].splice(index, 1, updated);
                    this.successMsg = updated && updated.name ? `Price range ${updated.name} updated successfully.` : 'Price range updated successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.managePriceRange = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        },

        // Create a new service add-on via API
        createAddOn(formData, payload) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/add-service-addons/`;
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
                    this.closeModal();
                    const key = String(payload.service_type || this.serviceTypeId || '0');
                    if (!this.serviceAddons[key]) this.serviceAddons[key] = [];
                    const item = {
                        id: data.id,
                        service_type_id: payload.service_type || this.serviceTypeId || '',
                        name: payload.name,
                        category: payload.category,
                        size: payload.size,
                        price: typeof payload.price === 'string' ? Number(payload.price) : payload.price,
                        productivity: payload.productivity,
                        is_active: !!payload.is_active,
                    };
                    item.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(item.name)}&background=${this.colorCodes[item.id % this.colorCodes.length]}&color=fff`;
                    this.serviceAddons[key].push(item);
                    this.successMsg = 'Addon saved successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        // backend often returns error_field + error_message
                        if (body.error_field) {
                            const mapField = f => (f === 'name' ? 'categoryName' : f);
                            this.validationErrors.manageAddOn = this.validationErrors.manageAddOn || {};
                            this.validationErrors.manageAddOn[mapField(body.error_field)] = body.error_message || body.error || 'Invalid input';
                        } else if (body.errors) {
                            this.validationErrors.manageAddOn = body.errors || {};
                        }
                    } else {
                        console.error(err);
                    }
                });
        },

        // Update an existing service add-on via API
        updateAddOn(formData, addonId, payload) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/update-service-addons/${addonId}`;
            fetch(url, {
                method: 'PUT',
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
                    this.closeModal();
                    const key = String(payload.service_type || this.serviceTypeId || '0');
                    if (!this.serviceAddons[key]) this.serviceAddons[key] = [];
                    const updated = {
                        id: Number(addonId),
                        service_type_id: payload.service_type || this.serviceTypeId || '',
                        name: payload.name,
                        category: payload.category,
                        size: payload.size,
                        price: typeof payload.price === 'string' ? Number(payload.price) : payload.price,
                        productivity: payload.productivity,
                        is_active: !!payload.is_active,
                    };
                    updated.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(updated.name)}&background=${this.colorCodes[updated.id % this.colorCodes.length]}&color=fff`;
                    const index = this.serviceAddons[key].findIndex(p => String(p.id) === String(updated.id));
                    if (index !== -1) this.serviceAddons[key].splice(index, 1, updated);
                    this.successMsg = updated && updated.name ? `Addon ${updated.name} updated successfully.` : 'Addon updated successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        if (body.error_field) {
                            const mapField = f => (f === 'name' ? 'categoryName' : f);
                            this.validationErrors.manageAddOn = this.validationErrors.manageAddOn || {};
                            this.validationErrors.manageAddOn[mapField(body.error_field)] = body.error_message || body.error || 'Invalid input';
                        } else if (body.errors) {
                            this.validationErrors.manageAddOn = body.errors || {};
                        }
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