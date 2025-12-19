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
            measurementUnits: [],
            serviceGroups: [],
            serviceTypeId: '',
            serviceGroupId: '',
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
                showAddons: false,
                showAddMeasurementUnitBtn: true,
                showManageMeasurementList: true,
                showManageMeasurementUnitForm: false,
                showMUConfirmDelete: false,
                showServiceGroupModal: false,
                showServiceGroupView: false,
            },
            // renamed from `delete` to avoid using the reserved keyword in template expressions
            deleteModal: {
                softText: '',
                strongText: '',
                id: ''
            },
            viewServiceGroup: {
                title: '',
                name: '',
                arabicName: '',
                activeStatus: ''
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
                manageAddOn: {},
                manageMeasurementUnit: {},
                manageServiceGroup: {}
            },
            serviceGroupFormFields: {
                id: null,
                name: '',
                name_arabic: '',
                status: '',
                image_path: null
            },
            serviceFormFields: {
                name: '',
                name_arabic: '',
                servicegroup_id: '',
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
                service_type_id: '',
                measurement_unit_id: ''
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
            measurementUnitFormFields: {
                id: '',
                name: '',
                abbreviation: '',
                is_active: '',
                dataAction: ''
            },
        };
    },
    // Methods for handling service types
    methods: {

        handleServiceGroupBtnClick() {
            this.toggleDivs.showList = false;
            this.toggleDivs.showServiceGroupView = true;
            this.toggleDivs.showServiceGroupModal = false;
        },
        handleAddServiceGroupBtnClick() {
            this.toggleDivs.showList = false;
            this.toggleDivs.showServiceGroupModal = true;
            this.toggleDivs.showServiceGroupView = false;
            this.viewServiceType = {
                title: '',
            };
            this.resetServiceGroup();
            const form = document.getElementById('manage-service-group-form');
            if (form) {
                form.setAttribute('data-action', 'add')
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
        // Handle edit service type button click
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
                this.serviceFormFields.is_active = serviceType.status ? 'active' : 'inactive';

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
        // Delete service type
        removeServiceType(serviceType) {
            const modal = document.getElementById('delete-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.deleteModal.softText = `Are you sure you want to continue with this action? This action will update the status of the service type "${serviceType.name}".`;
                const form = document.getElementById('delete-form');
                if (form) {
                    form.setAttribute('data-delete-property', 'service-type');
                    this.deleteModal.id = serviceType.id || '';

                }
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
                        measurement_unit_id: ''
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
                        measurement_unit_id: productivity.measurement_unit_id || ''
                    }
                }
            }

        },
        //delete productivity
        removeProductivity(productivity) {
            const modal = document.getElementById('delete-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');

                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);

                this.deleteModal.softText = `Are you sure you want to delete the productivity "${productivity.name}"?`;


                // attach delete type
                const form = document.getElementById('delete-form');
                if (form) {
                    form.setAttribute('data-delete-property', 'productivity');
                    this.deleteModal.id = productivity.id || '';
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
                        productivity_id: this.activePtab || (this.productivities && this.productivities[String(this.serviceTypeId ?? '0')] && this.productivities[String(this.serviceTypeId ?? '0')][0] && this.productivities[String(this.serviceTypeId ?? '0')][0].id) || '',
                        service_type_id: this.serviceTypeId || ''
                    }
                }
            }
        },
        // Handle Edit Price Range button click
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
        // Delete price range
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

                const form = document.getElementById('delete-form');
                if (form) {
                    form.setAttribute('data-delete-property', 'price-range');
                    this.deleteModal.id = priceRange.id || '';
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
        handleEditAddonBtnClick(addon) {
            const modal = document.getElementById('manage-addon-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.modalHeading = `Edit ${addon.name}`;
                this.validationErrors['manageAddOn'] = [];
                const form = document.getElementById('manage-addon-form');
                if (form) {
                    form.setAttribute('data-action', 'edit');
                    this.addonFormFields = {
                        id: addon.id || '',
                        item: addon.name || '',
                        category_name: addon.category || '',
                        size: addon.size || '',
                        price: addon.price || '',
                        productivity: addon.productivity || '',
                        service_type_id: this.serviceTypeId || '',
                        status: addon.is_active || false
                    }
                }
            }
        },
        // delete add-on
        removeAddon(addon) {
            const modal = document.getElementById('delete-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.deleteModal.softText = `Are you sure you want to continue with this action? This action will update the status of the add-on "${addon.name}".`;
                // append form with data set of type 'add-on'
                const form = document.getElementById('delete-form');
                if (form) {
                    form.setAttribute('data-delete-property', 'add-on');
                    this.deleteModal.id = addon.id || '';
                }
            }
        },

        // Handle measurement units button click
        handleMeasurementUnitsBtnClick() {
            const modal = document.getElementById('measurement-units-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
            this.measurementUnitFormFields = { id: '', name: '', abbreviation: '', is_active: '' };

            this.toggleDivs.showAddMeasurementUnitBtn = true;
            this.toggleDivs.showManageMeasurementList = true
        },
        // Handle Add Measurement Unit button click
        handleAddManageMeasurementUnitBtnClick() {
            this.toggleDivs.showManageMeasurementUnitForm = true;
            this.toggleDivs.showAddMeasurementUnitBtn = false;
            this.toggleDivs.showManageMeasurementList = false;
            this.validationErrors['manageMeasurementUnit'] = [];
            this.measurementUnitFormFields = { id: '', name: '', abbreviation: '', is_active: '', dataAction: 'add' };
        },
        handleEditMeasurementUnitBtnClick(unit) {
            this.toggleDivs.showManageMeasurementUnitForm = true;
            this.toggleDivs.showAddMeasurementUnitBtn = false;
            this.toggleDivs.showManageMeasurementList = false;
            this.validationErrors['manageMeasurementUnit'] = [];
            this.measurementUnitFormFields = { id: unit.id || '', name: unit.name || '', abbreviation: unit.abbreviation || '', is_active: unit.is_active || false, dataAction: 'edit' };
        },
        // Handle cancel measurement unit button click
        handleCancelManageMeasurementUnitBtnClick() {
            this.toggleDivs.showAddMeasurementUnitBtn = true;
            this.toggleDivs.showManageMeasurementUnitForm = false;
            this.toggleDivs.showManageMeasurementList = true;
            this.validationErrors['manageMeasurementUnit'] = [];
            this.measurementUnitFormFields = { id: '', name: '', abbreviation: '', is_active: true };
        },
        // Delete measurement unit
        removeMeasurementUnit(unit) {
            this.toggleDivs.showMUConfirmDelete = true;
            this.toggleDivs.showAddMeasurementUnitBtn = false;
            this.toggleDivs.showManageMeasurementList = false;
            this.measurementUnitFormFields.id = unit.id || '';
        },
        // Confirm delete measurement unit
        confirmDeleteMeasurementUnit() {
            const payload = { is_active: false };
            this.deleteMeasurementUnit(this.toFormData(payload), this.measurementUnitFormFields.id);
        },
        // Cancel delete measurement unit
        cancelDeleteMeasurementUnit() {
            this.toggleDivs.showMUConfirmDelete = false;
            this.toggleDivs.showAddMeasurementUnitBtn = true;
            this.toggleDivs.showManageMeasurementList = true;
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
        // Set active productivity tab
        setActiveProductivityTab(pid = null) {
            this.activePtab = pid
        },
        // Reset new service form fields
        deleteProperty() {
            const form = document.getElementById('delete-form');
            if (form) {
                const propertyType = form.getAttribute('data-delete-property');
                const id = form.querySelector('input[name="delete_id"]').value;
                if (propertyType === 'service-type') {
                    const payload = {
                        new_service_is_active: "inactive"
                    }
                    this.deleteServiceType(this.toFormData(payload), id);
                    return;
                }
                if (propertyType === 'price-range') {
                    const payload = {
                        status: 0
                    }
                    this.deletePriceRange(this.toFormData(payload), id);
                    return;
                }


                if (propertyType === 'add-on') {
                    const payload = {
                        is_active: 0
                    }
                    this.deleteAddOn(this.toFormData(payload), id);
                    return;
                }
                if (propertyType === 'productivity') {
                    const payload = { status: 0 };
                    this.deleteProductivity(this.toFormData(payload), id);
                    return;
                }
                if (propertyType === 'service-group') {
                    const payload = {
                        new_group_is_active: "inactive"
                    };
                    this.deleteServiceGroup(this.toFormData(payload), id);
                    return;
                }

            }
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

        /* Form submission methods */
        /* Add or update service group */
        submitServiceGroupForm() {
            // Clear previous errors
            this.validationErrors['manageServiceGroup'] = {};

            // Validations
            if (!this.serviceGroupFormFields.name || !this.serviceGroupFormFields.name.trim()) {
                this.validationErrors['manageServiceGroup']['serviceGroupName'] = 'Service name is required.';
            }

            if (!this.serviceGroupFormFields.name_arabic || !this.serviceGroupFormFields.name_arabic.trim()) {
                this.validationErrors['manageServiceGroup']['serviceGroupArabicName'] =
                    'Arabic name is required.';
            } else {
                const arabicRegex = /^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s]+$/;

                if (!arabicRegex.test(this.serviceGroupFormFields.name_arabic)) {
                    this.validationErrors['manageServiceGroup']['serviceGroupArabicName'] =
                        'Arabic name must contain only Arabic characters.';
                }
            }

            if (!this.serviceGroupFormFields.status || this.serviceGroupFormFields.status === '') {
                this.validationErrors['manageServiceGroup']['serviceGroupStatus'] = 'Status is required.';
            }

            // Stop if validation errors exist
            if (Object.keys(this.validationErrors['manageServiceGroup']).length) return;

            // Prepare payload
            const payload = {
                service_name: this.serviceGroupFormFields.name,
                service_name_arabic: this.serviceGroupFormFields.name_arabic || '',
                status: this.serviceGroupFormFields.status,
            };

            if (this.serviceGroupFormFields.image_path) {
                payload.image_path = this.serviceGroupFormFields.image_path;
            }

            // Determine action (add or edit)
            const form = document.getElementById('manage-service-group-form');
            const formAction = form.getAttribute('data-action');

            if (formAction === 'add') {
                this.createServiceGroup(this.toFormData(payload));
            } else {
                const serviceId = form.querySelector('input#editing_service_group_id, input[name="editing_service_group_id"]');
                this.updateServiceGroup(this.toFormData(payload), serviceId.value); // implement this method for editing
            }
        },

        /* Add or update service type */
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
            if (this.serviceFormFields.servicegroup_id === '') {
                this.validationErrors['manageServiceType']['serviceGroup'] = 'Servicegroup is required.';
            }

            if (Object.keys(this.validationErrors['manageServiceType']).length) return;

            // prepare payload for backend (convert boolean to expected value)
            const payload = {
                new_service_name: this.serviceFormFields.name,
                new_service_name_arabic: this.serviceFormFields.name_arabic,
                new_service_group_id: this.serviceFormFields.servicegroup_id,
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

            if (this.categoryFormFields.measurement_unit_id === '') {
                this.validationErrors.manageProductivity.measurementUnit = 'Measurement Unit is required.';
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
                productivity_service_type_id: this.serviceTypeId,
                measurement_unit_id: this.categoryFormFields.measurement_unit_id
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
                if (Number.isNaN(n) || n < 0) {
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
                if (Number.isNaN(n2) || n2 < 0) {
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
        // Submit Add-on form (create or update via API)
        submitAddonForm() {
            this.validationErrors.manageAddOn = {};
            if (!this.addonFormFields.item || !this.addonFormFields.item.trim()) {
                this.validationErrors.manageAddOn.item = 'Item name is required.';
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
            if (!this.addonFormFields.productivity || !String(this.addonFormFields.productivity).trim()) {
                this.validationErrors.manageAddOn.productivity = 'Productivity is required.';
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
        // Submit Measurement Unit form (create or update via API)
        submitMeasurementUnitForm() {
            this.validationErrors.manageMeasurementUnit = {};

            // Validation
            if (!this.measurementUnitFormFields.name || !this.measurementUnitFormFields.name.trim()) {
                this.validationErrors.manageMeasurementUnit.name = 'Name is required.';
            }
            if (!this.measurementUnitFormFields.abbreviation || !this.measurementUnitFormFields.abbreviation.trim()) {
                this.validationErrors.manageMeasurementUnit.abbreviation = 'Abbreviation is required.';
            }
            if (this.measurementUnitFormFields.is_active === '' || this.measurementUnitFormFields.is_active === null) {
                this.validationErrors.manageMeasurementUnit.status = 'Status is required.';
            }

            if (Object.keys(this.validationErrors.manageMeasurementUnit).length > 0) return;

            const payload = {
                name: this.measurementUnitFormFields.name.trim(),
                abbreviation: this.measurementUnitFormFields.abbreviation.trim(),
                is_active: this.measurementUnitFormFields.is_active ? 'active' : 'inactive'
            };

            const form = document.getElementById('manage-measurement-unit-form');
            const formAction = form ? form.getAttribute('data-action') : 'add';

            if (formAction === 'add') {
                this.createMeasurementUnit(this.toFormData(payload));
            } else {
                const id = this.measurementUnitFormFields.id;
                this.updateMeasurementUnit(this.toFormData(payload), id);
            }
        },

        // Fetch service groups from the server
        getServiceGroups() {
            fetch('get-service-groups/')
                .then(response => response.json())
                .then(data => {
                    if (data.service_groups) {
                        this.serviceGroups = data.service_groups.map(g => {
                            return {
                                ...g,
                                avatar: `${this.avatarBaseUrl}?name=${encodeURIComponent(g.service_name)}&background=${this.colorCodes[g.id % this.colorCodes.length]}&color=fff`
                            };
                        });
                    }
                })
                .catch(error => console.error('Error fetching service groups:', error));
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
                    if (data.measurement_units) {
                        this.measurementUnits = data.measurement_units;
                    }

                })
                .catch(error => {
                    console.error('Error fetching service types:', error);
                });
        },
        //create a new service group form
        createServiceGroup(formData) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;

            const url = `${baseUrl}/common/create-service-group/`;

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

                        // Backend returns: error_field + error_message
                        if (data.error_field && data.error_message) {

                            if (data.error_field === 'service_name') {
                                this.validationErrors['manageServiceGroup']['serviceGroupName'] = data.error_message;
                            }

                            if (data.error_field === 'service_name_arabic') {
                                this.validationErrors['manageServiceGroup']['serviceGroupArabicName'] = data.error_message;
                            }

                            if (data.error_field === 'status') {
                                this.validationErrors['manageServiceGroup']['serviceGroupStatus'] = data.error_message;
                            }

                            if (data.error_field === 'imagepath') {
                                this.validationErrors['manageServiceGroup']['serviceGroupImage'] = data.error_message;
                            }
                        }

                    } else {
                        // Success handling
                        this.successMsg = data.service_group
                            ? `Service group "${data.service_group.service_name}" added successfully.`
                            : 'Service group added successfully.';
                        data.service_group.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(data.service_group.service_name)}&background=${this.colorCodes[data.service_group.id % this.colorCodes.length]}&color=fff`;
                        this.serviceGroups.push(data.service_group);
                        // Reset form
                        this.resetServiceGroup();
                        setTimeout(() => { this.successMsg = null; }, 5000);
                    }
                })
                .catch(err => console.error(err));
        },
        // Update an existing service group
        updateServiceGroup(formData, groupId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;

            const url = `${baseUrl}/common/update-service-group/${groupId}/`;

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

                            if (data.error_field === 'service_name') {
                                this.validationErrors['manageServiceGroup']['serviceGroupName'] = data.error_message;
                            }

                            if (data.error_field === 'service_name_arabic') {
                                this.validationErrors['manageServiceGroup']['serviceGroupArabicName'] = data.error_message;
                            }

                            if (data.error_field === 'status') {
                                this.validationErrors['manageServiceGroup']['serviceGroupStatus'] = data.error_message;
                            }

                            // if (data.error_field === 'imagepath') {
                            //     this.validationErrors['manageServiceGroup']['serviceGroupImage'] = data.error_message;
                            // }
                        }

                    } else {

                        this.successMsg = data.service_group
                            ? `Service group "${data.service_group.service_name}" updated successfully.`
                            : 'Service group updated successfully.';

                        // Update avatar (same style as service type)
                        data.service_group.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(data.service_group.service_name)}&background=${this.colorCodes[data.service_group.id % this.colorCodes.length]}&color=fff`;

                        // Update local array
                        const index = this.serviceGroups.findIndex(s => s.id == data.service_group.id);
                        if (index !== -1) {
                            this.serviceGroups.splice(index, 1, data.service_group);
                        }

                        // Reset form
                        this.resetServiceGroup();

                        setTimeout(() => { this.successMsg = null; }, 5000);
                    }
                })
                .catch(err => console.error(err));
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
                            if (data.error_field === 'new_service_group_id') {
                                this.validationErrors['manageServiceType']['serviceGroup'] = data.error_message;
                            }
                            if (data.error_field === 'new_service_is_active') {
                                this.validationErrors['manageServiceType']['serviceTypeIsActive'] = data.error_message;
                            }
                        }
                    } else {
                        console.log("service type", data.service_type);
                        this.successMsg = data.service_type
                            ? `Service type "${data.service_type.name}" added successfully.`
                            : 'Service type added successfully.';
                        data.service_type.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(data.service_type.name)}&background=${this.colorCodes[data.service_type.id % this.colorCodes.length]}&color=fff`;
                        this.serviceTypes.push(data.service_type);
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
                            if (data.error_field === 'edit_service_group_id') {
                                this.validationErrors['manageServiceType']['serviceGroup'] =
                                    data.error_message;
                            }
                            if (data.error_field === 'edit_service_is_active') {
                                this.validationErrors['manageServiceType']['serviceTypeIsActive'] = data.error_message;
                            }
                        }
                    } else {
                        this.successMsg = data.service_type
                            ? `Service type "${data.service_type.name}" updated successfully.`
                            : 'Service type updated successfully.';
                        // update local serviceTypes array
                        const index = this.serviceTypes.findIndex(s => s.id == data.service_type.id);
                        if (index !== -1) {
                            data.service_type.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(data.service_type.name)}&background=${this.colorCodes[data.service_type.id % this.colorCodes.length]}&color=fff`;
                            this.serviceTypes.splice(index, 1, data.service_type);
                        }
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
        // Update an existing productivity category
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
        // Delete productivity category
        deleteProductivity(formData, productivityId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/delete-productivity/${productivityId}/`;

            fetch(url, {
                method: 'DELETE',
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
                    if (data.success) {
                        this.closeModal();

                        // Find key → same as service type wise productivity list
                        const key = String(data.productivity?.service_type_id || this.serviceTypeId || '0');

                        if (!this.serproductivities[key]) this.productivities[key] = [];

                        const updated = data.productivity || data;

                        // update avatar logic if exists
                        if (updated.name && this.avatarBaseUrl) {
                            updated.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(updated.name)}&background=${this.colorCodes[updated.id % this.colorCodes.length]}&color=fff`;
                        }

                        // replace list item
                        const index = this.productivities[key].findIndex(p => String(p.id) === String(updated.id));
                        if (index !== -1) this.productivities[key].splice(index, 1, updated);

                        this.successMsg = updated && updated.name
                            ? `Productivity ${updated.name} deleted successfully.`
                            : 'Productivity deleted successfully.';

                        setTimeout(() => { this.successMsg = ''; }, 5000);
                    }
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.manageProductivity = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        },
        // Update productivity status via JSON PUT (more reliable than FormData on PUT)
        updateProductivityStatus(productivityId, status) {
            const csrftoken = this.getCookie('csrftoken')
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/update-service-productivity/${productivityId}`
            fetch(url, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: status })
            })
                .then(res => {
                    if (!res.ok) throw res;
                    return res.json();
                })
                .then(data => {
                    this.closeModal();
                    const key = String(this.serviceTypeId ?? '0');
                    if (!this.productivities[key]) this.productivities[key] = [];
                    const updated = data.service_productivity || data;
                    const index = this.productivities[key].findIndex(p => p.id === updated.id);
                    if (index !== -1) this.productivities[key].splice(index, 1, updated);
                    this.successMsg = updated && updated.name ? `Category ${updated.name} deleted successfully.` : 'Category deleted successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
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
        createAddOn(formData) {
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
                    const item = data.service_addon || data;
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
        updateAddOn(formData, addonId) {
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
                    if (data.success) {
                        this.closeModal();
                        const key = String(data.service_addon?.service_type_id || this.serviceTypeId || '0');
                        if (!this.serviceAddons[key]) this.serviceAddons[key] = [];
                        const updated = data.service_addon || data;
                        updated.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(updated.name)}&background=${this.colorCodes[updated.id % this.colorCodes.length]}&color=fff`;
                        const index = this.serviceAddons[key].findIndex(p => String(p.id) === String(updated.id));
                        if (index !== -1) this.serviceAddons[key].splice(index, 1, updated);
                        this.successMsg = updated && updated.name ? `Addon ${updated.name} updated successfully.` : 'Addon updated successfully.';
                        setTimeout(() => { this.successMsg = ''; }, 5000);
                    }
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
        // Create a new measurement unit via API
        createMeasurementUnit(formData) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/add-measurement-unit/`;

            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (!data.success) {
                        // Map backend errors if present
                        if (data.error_field && data.error_message) {
                            this.validationErrors.manageMeasurementUnit[data.error_field] = data.error_message;
                        }
                    } else {
                        // Add to local list and reset form
                        if (data.measurement_unit) {
                            this.measurementUnits.push(data.measurement_unit);
                            // this.successMsg = `Measurement unit "${data.measurement_unit.name}" added successfully.`;
                            // setTimeout(() => { this.successMsg = ''; }, 5000);
                        }
                        this.measurementUnitFormFields = { id: '', name: '', abbreviation: '', is_active: '', data_action: '' };
                        this.toggleDivs.showAddMeasurementUnitBtn = true;
                        this.toggleDivs.showManageMeasurementList = true;
                        this.toggleDivs.showManageMeasurementUnitForm = false;
                    }
                })
                .catch(err => {
                    console.error(err);
                });
        },
        updateMeasurementUnit(formData, unitId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/update-measurement-unit/${unitId}`;

            fetch(url, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (!data.success) {
                        // Map backend errors if present
                        if (data.error_field && data.error_message) {
                            this.validationErrors.manageMeasurementUnit[data.error_field] = data.error_message;
                        }
                    } else {
                        // Update local list and reset form
                        if (data.measurement_unit) {
                            const idx = this.measurementUnits.findIndex(u => u.id == data.measurement_unit.id);
                            if (idx !== -1) this.measurementUnits.splice(idx, 1, data.measurement_unit);
                            // this.successMsg = `Measurement unit "${data.measurement_unit.name}" updated successfully.`;
                            // setTimeout(() => { this.successMsg = ''; }, 5000);
                        }
                        this.measurementUnitFormFields = { id: '', name: '', abbreviation: '', is_active: '', data_action: '' };
                        this.toggleDivs.showAddMeasurementUnitBtn = true;
                        this.toggleDivs.showManageMeasurementList = true;
                        this.toggleDivs.showManageMeasurementUnitForm = false;
                    }
                })
                .catch(err => {
                    console.error(err);
                });
        },
        // Delete (deactivate) a service type by delegating to the same update endpoint
        deleteServiceType(formData, serviceId) {
            console.log("object");
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/delete-service-type/${serviceId}/`;
            fetch(url, {
                method: 'DELETE',
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
                    const index = this.serviceTypes.findIndex(s => s.id == serviceId);
                    if (index !== -1) {
                        data.service_type.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(data.service_type.name)}&background=${this.colorCodes[data.service_type.id % this.colorCodes.length]}&color=fff`;
                        this.serviceTypes.splice(index, 1, data.service_type);
                    }
                    this.successMsg = data.service_type ? `Service type "${data.service_type.name}" updated successfully.` : 'Service type updated successfully.';
                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.manageServiceType = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        },

        // Delete (deactivate) a price range by calling the update endpoint and updating local state
        deletePriceRange(formData, priceRangeId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/delete-service-price-range/${priceRangeId}/`;
            fetch(url, {
                method: 'DELETE',
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
                    if (data.success) {
                        this.closeModal();
                        const key = String(data.service_price_range?.service_productivity_id || '0');
                        if (!this.servicePriceRanges[key]) this.servicePriceRanges[key] = [];
                        const updated = data.service_price_range || data;
                        updated.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(updated.name)}&background=${this.colorCodes[updated.id % this.colorCodes.length]}&color=fff`;
                        const index = this.servicePriceRanges[key].findIndex(p => p.id === updated.id);
                        if (index !== -1) this.servicePriceRanges[key].splice(index, 1, updated);
                        this.successMsg = updated && updated.name ? `Price range ${updated.name} updated successfully.` : 'Price range updated successfully.';
                        setTimeout(() => { this.successMsg = ''; }, 5000);
                    }
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

        // Delete (deactivate) an add-on by calling the update endpoint and updating local state
        deleteAddOn(formData, addonId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/delete-service-addons/${addonId}/`;
            fetch(url, {
                method: 'DELETE',
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
                    if (data.success) {
                        this.closeModal();
                        const key = String(data.service_addon?.service_type_id || this.serviceTypeId || '0');
                        if (!this.serviceAddons[key]) this.serviceAddons[key] = [];
                        const updated = data.service_addon || data;
                        updated.avatar = `${this.avatarBaseUrl}?name=${encodeURIComponent(updated.name)}&background=${this.colorCodes[updated.id % this.colorCodes.length]}&color=fff`;
                        const index = this.serviceAddons[key].findIndex(p => String(p.id) === String(updated.id));
                        if (index !== -1) this.serviceAddons[key].splice(index, 1, updated);
                        this.successMsg = updated && updated.name ? `Addon ${updated.name} updated successfully.` : 'Addon updated successfully.';
                        setTimeout(() => { this.successMsg = ''; }, 5000);
                    }
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.manageAddOn = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        },
        // Delete (deactivate) a measurement unit via API
        deleteMeasurementUnit(formData, unitId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;
            const url = `${baseUrl}/common/delete-measurement-unit/${unitId}`;

            fetch(url, {
                method: 'DELETE',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        if (data.measurement_unit) {
                            const idx = this.measurementUnits.findIndex(u => u.id == data.measurement_unit.id);
                            if (idx !== -1) this.measurementUnits.splice(idx, 1, data.measurement_unit);
                            this.toggleDivs.showAddMeasurementUnitBtn = true;
                            this.toggleDivs.showManageMeasurementList = true;
                            this.toggleDivs.showManageMeasurementUnitForm = false;
                            this.toggleDivs.showMUConfirmDelete = false;
                        }
                    } else {
                        // alert(data.error_message || 'Failed to delete measurement unit.');
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('An error occurred while deleting the measurement unit.');
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
        resetServiceGroup() {
            this.serviceGroupFormFields = {
                id: null,
                name: '',
                name_arabic: '',
                status: '',
                image_path: ''

            };
            this.validationErrors['manageServiceGroup'] = {};
        },
        resetNewService() {
            this.serviceFormFields = { name: '', name_arabic: '', servicegroup_id: '', is_active: '' };
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
        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            const day = date.getDate().toString().padStart(2, '0');
            const month = date.toLocaleString('en-US', { month: 'short' });
            const year = date.getFullYear();
            return `${day} ${month}, ${year}`;
        },

        handleImageUpload(event) {
            if (event.target.files && event.target.files[0]) {
                this.serviceGroupFormFields.image_path = event.target.files[0];
            }
        },
        //for submit service group form
        backButtonAction1() {
            this.toggleDivs.showServiceGroupModal = false;
            this.toggleDivs.showServiceGroupView = true;
        },

        handleEditServiceGroupBtnClick(serviceGroup) {

            this.toggleDivs.showServiceGroupView = false;
            this.toggleDivs.showServiceGroupModal = true;

            this.serviceGroupId = serviceGroup.id;

            this.viewServiceGroup = {
                title: `Edit ${serviceGroup.service_name}`,
            };

            const form = document.getElementById('manage-service-group-form');
            if (form) {
                form.setAttribute('data-action', 'edit');

                // FIXED FIELDS
                this.serviceGroupFormFields.name = serviceGroup.service_name || '';
                this.serviceGroupFormFields.name_arabic = serviceGroup.service_name_arabic || '';
                this.serviceGroupFormFields.status = serviceGroup.status ? 'active' : 'inactive';

                const hiddenName = 'editing_service_group_id';
                let hidden = form.querySelector(`input[name="${hiddenName}"]`);

                if (!hidden) {
                    hidden = document.createElement('input');
                    hidden.type = 'hidden';
                    hidden.name = hiddenName;
                    hidden.id = hiddenName;
                    form.appendChild(hidden);
                }

                hidden.value = serviceGroup.id ?? '';
            }
        },
        removeServiceGroup(serviceGroup) {
            const modal = document.getElementById('delete-modal');
            if (modal) {
                modal.classList.add('in', 'show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                this.deleteModal.softText = `Are you sure you want to continue with this action? This action will update the status of the service type "${serviceGroup.service_name}".`;
                const form = document.getElementById('delete-form');
                if (form) {
                    form.setAttribute('data-delete-property', 'service-group');
                    this.deleteModal.id = serviceGroup.id || '';

                }
            }

        },

        deleteServiceGroup(formData, groupId) {
            const csrftoken = this.getCookie('csrftoken');
            const baseUrl = window.location.origin;

            const url = `${baseUrl}/common/delete-service-group/${groupId}/`;

            fetch(url, {
                method: 'DELETE',
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

                    const index = this.serviceGroups.findIndex(g => g.id == groupId);
                    if (index !== -1) {
                        data.service_group.avatar =
                            `${this.avatarBaseUrl}?name=${encodeURIComponent(data.service_group.service_name)}&background=${this.colorCodes[data.service_group.id % this.colorCodes.length]}&color=fff`;

                        this.serviceGroups.splice(index, 1, data.service_group);
                    }

                    this.successMsg = data.service_group
                        ? `Service group "${data.service_group.service_name}" updated successfully.`
                        : 'Service group updated successfully.';

                    setTimeout(() => { this.successMsg = ''; }, 5000);
                })
                .catch(async err => {
                    if (err.json) {
                        const body = await err.json();
                        this.validationErrors.manageServiceGroup = body.errors || {};
                    } else {
                        console.error(err);
                    }
                });
        }
    },
    // Lifecycle hook to fetch service types on mount
    mounted() {
        this.getServiceTypes();
        this.getServiceGroups();
    }
}).mount('#app');