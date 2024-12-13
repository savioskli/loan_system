// Handle both direct dependencies and managed field dependencies
class FormDependencyHandler {
    constructor() {
        this.dependencies = new Map();
        this.managedDependencies = new Map();
        this.init();
    }

    async init() {
        // Load managed dependencies from the server
        await this.loadManagedDependencies();
        
        // Set up direct dependencies from data attributes
        this.setupDirectDependencies();
        
        // Initial check of all dependencies
        this.checkAllDependencies();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    async loadManagedDependencies() {
        try {
            const response = await fetch('/api/field-dependencies');
            const deps = await response.json();
            
            deps.forEach(dep => {
                if (!this.managedDependencies.has(dep.parent_field_id)) {
                    this.managedDependencies.set(dep.parent_field_id, []);
                }
                this.managedDependencies.get(dep.parent_field_id).push({
                    dependentId: dep.dependent_field_id,
                    showValues: dep.show_on_values
                });
            });
        } catch (error) {
            console.error('Error loading managed dependencies:', error);
        }
    }

    setupDirectDependencies() {
        // Find all elements with data-depends-on attribute
        document.querySelectorAll('[data-depends-on]').forEach(element => {
            const parentId = element.dataset.dependsOn;
            const requiredValue = element.dataset.dependsValue;
            
            if (!this.dependencies.has(parentId)) {
                this.dependencies.set(parentId, []);
            }
            
            this.dependencies.get(parentId).push({
                element: element,
                requiredValue: requiredValue
            });
        });
    }

    setupEventListeners() {
        // Listen for changes on all form fields that have dependencies
        this.dependencies.forEach((deps, parentId) => {
            const parentElement = document.getElementById(parentId);
            if (parentElement) {
                parentElement.addEventListener('change', () => this.checkDependencies(parentId));
            }
        });

        // Listen for changes on all fields that have managed dependencies
        this.managedDependencies.forEach((deps, parentId) => {
            const parentElement = document.getElementById(parentId);
            if (parentElement) {
                parentElement.addEventListener('change', () => this.checkManagedDependencies(parentId));
            }
        });
    }

    checkAllDependencies() {
        // Check direct dependencies
        this.dependencies.forEach((deps, parentId) => {
            this.checkDependencies(parentId);
        });

        // Check managed dependencies
        this.managedDependencies.forEach((deps, parentId) => {
            this.checkManagedDependencies(parentId);
        });
    }

    checkDependencies(parentId) {
        const parentElement = document.getElementById(parentId);
        if (!parentElement) return;

        const currentValue = parentElement.value;
        const dependencies = this.dependencies.get(parentId) || [];

        dependencies.forEach(dep => {
            const show = dep.requiredValue === currentValue;
            this.toggleElement(dep.element, show);
        });
    }

    checkManagedDependencies(parentId) {
        const parentElement = document.getElementById(parentId);
        if (!parentElement) return;

        const currentValue = parentElement.value;
        const dependencies = this.managedDependencies.get(parentId) || [];

        dependencies.forEach(dep => {
            const dependentElement = document.getElementById(`field-${dep.dependentId}`);
            if (dependentElement) {
                const show = dep.showValues.includes(currentValue);
                this.toggleElement(dependentElement, show);
            }
        });
    }

    toggleElement(element, show) {
        const container = element.closest('.form-group') || element;
        if (show) {
            container.style.display = '';
            element.disabled = false;
        } else {
            container.style.display = 'none';
            element.disabled = true;
        }
    }
}
