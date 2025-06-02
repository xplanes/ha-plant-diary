class PlantTrackerCard extends HTMLElement {

    config;
    content;
    imageCache = new Map(); // 🔐 store cached image availability

    // required
    setConfig(config) {
        this.config = config;
    }

    set hass(hass) {
        this._hass = hass;

        // done once
        if (!this.innerHTML) {
            // Create the card
            this.innerHTML = `
                <ha-card header="Plant Tracker">` +
                this.getStyles() +
                `   <div class="card-actions">
                        <mwc-button id="addPlantButton" label="Add Plant"></mwc-button>
                    </div>
                    <div id="plantsOutside" class="card-content"></div>
                    <div id="plantsInside" class="card-content"></div>
                    <div id="modalEditPlant" class="modal">
                        <div id="modalEditPlantBody" class="modal-content"></div>
                    </div>
                </ha-card>
            `;
            this.addPlantButton = this.querySelector('#addPlantButton');
            this.contentPlantsOutside = this.querySelector('#plantsOutside');
            this.contentPlantsInside = this.querySelector('#plantsInside');
            this.modalEditPlant = this.querySelector('#modalEditPlant');
            this.modalEditPlantBody = this.querySelector('#modalEditPlantBody');

            // Add event listener to the add plant button
            this.addPlantButton.onclick = () => {
                this.showPlantEditModal("");
            };

            // Call the service to update the days since watered
            this._hass.callService('plant_tracker', 'update_days_since_watered');
        }

        // Set the inner HTML of the content div to the generated HTML
        this.contentPlantsOutside.innerHTML = this.generatePlantCardContentHTML(false);
        this.contentPlantsInside.innerHTML = this.generatePlantCardContentHTML(true);

        // Show modal for adding or editing a plant
        this.showPlantEditModal = (entityId) => {

            // Create a new plant if entityId is empty
            if (entityId === "") {
                const attributes = {
                    plant_name: 'New Plant',
                    last_watered: 'Unknown',
                    last_fertilized: 'Unknown',
                    watering_interval: '14',
                    watering_postponed: '0',
                    inside: false
                };

                // Set the modal content
                this.modalEditPlantBody.innerHTML =
                    this.generateModalEditPlantBodyHTML("", attributes);

                // On OK call create_plant
                const okButton = this.modalEditPlantBody.querySelector('#ok_button');
                okButton.onclick = () => {
                    const plantNameInput = this.modalEditPlantBody.querySelector('#plant_name').value;
                    const normalizedNewName = this.normalizeName(plantNameInput);

                    // Verificar si ya existe un nombre de planta con ese valor
                    const existingNames = Object.values(this._hass.states)
                        .filter(entity => entity.entity_id.startsWith("sensor.plant_tracker"))
                        .map(entity => entity.attributes.plant_name?.toLowerCase());
                    const normalizedExisting = existingNames.map(n => this.normalizeName(n));

                    if (normalizedExisting.includes(normalizedNewName)) {
                        const errorMessageDiv = this.modalEditPlantBody.querySelector('#error_message');
                        errorMessageDiv.innerText = "A plant with this name already exists.";
                        errorMessageDiv.style.display = "block";
                        return;
                    }

                    // Call the service to add a new plant
                    this._hass.callService('plant_tracker', 'create_plant', {
                        plant_name: plantNameInput,
                        last_watered: this.modalEditPlantBody.querySelector('#last_watered').value,
                        last_fertilized: this.modalEditPlantBody.querySelector('#last_fertilized').value,
                        watering_interval: this.modalEditPlantBody.querySelector('#watering_days').value,
                        watering_postponed: this.modalEditPlantBody.querySelector('#watering_postponed').value,
                        inside: this.modalEditPlantBody.querySelector('#inside').checked
                    });
                    // Close the modal
                    this.modalEditPlant.style.display = "none";
                };

            }
            else {
                const state = hass.states[entityId];
                const stateStr = state ? state.state : 'unavailable';
                const attributes = state ? state.attributes : {};

                // Set the modal content
                this.modalEditPlantBody.innerHTML =
                    this.generateModalEditPlantBodyHTML(entityId, attributes);

                // On OK call updateAttributes
                const okButton = this.modalEditPlantBody.querySelector('#ok_button');
                okButton.onclick = () => {
                    this.updateAttributes(entityId);
                };

                // Add event listeners to the delete button
                const deleteButton = this.modalEditPlantBody.querySelector('.deletePlantButton');
                deleteButton.onclick = () => {
                    const name = attributes.plant_name || 'Unknown';
                    if (confirm(`Are you sure you want to delete ${name}?`)) {
                        this._hass.callService('plant_tracker', 'delete_plant', {
                            plant_id: name
                        });
                        this.modalEditPlant.style.display = "none"; // Close the modal after deletion
                    }
                };
            }

            // Close the modal when the user clicks on <span> (x)
            const modalEditPlantCloseButton = this.modalEditPlantBody.querySelector('#EditPlantClose');
            modalEditPlantCloseButton.onclick = () => {
                this.modalEditPlant.style.display = "none";
            };

            // On Cancel close the modal
            const cancelButton = this.modalEditPlantBody.querySelector('#cancel_button');
            cancelButton.onclick = () => {
                this.modalEditPlant.style.display = "none";
            };

            // Update attributes
            this.modalEditPlantBody.querySelector('#last_watered_btn')
                .addEventListener('click', () => this.modalEditPlantBody.querySelector('#last_watered').value = this.getTodayDate());
            this.modalEditPlantBody.querySelector('#last_fertilized_btn')
                .addEventListener('click', () => this.modalEditPlantBody.querySelector('#last_fertilized').value = this.getTodayDate());
            this.modalEditPlantBody.querySelector('#watering_postponed_btn')
                .addEventListener('click', () => this.modalEditPlantBody.querySelector('#watering_postponed').value++);

            this.modalEditPlant.style.display = "block";
        };

        // Update attributes when the user clicks on OK
        this.updateAttributes = (entityId) => {
            const form = this.modalEditPlantBody.querySelector('#editForm');
            if (!form) {
                console.error("Form not found");
                return;
            }

            const plantId = this._hass.states[entityId]?.attributes?.plant_name;

            // Call the service to update the attributes
            this._hass.callService('plant_tracker', 'update_plant', {
                plant_id: plantId,
                plant_name: plantId,
                last_watered: form.last_watered.value,
                last_fertilized: form.last_fertilized.value,
                watering_interval: form.watering_days.value,
                watering_postponed: form.watering_postponed.value,
                inside: form.inside.checked
            });

            // Close the modal
            this.modalEditPlant.style.display = "none";
        };

        // Attach the showPlantEditModal and updateAttributes functions to the window object to make them accessible
        window.showPlantEditModal = this.showPlantEditModal;
        window.updateAttributes = this.updateAttributes;
    }

    // Helper function to get today's date in "YYYY-MM-DD" format
    getTodayDate() {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0]; // "YYYY-MM-DD"
        return formattedDate;
    }

    getBackgroundColor(state) {
        switch (state) {
            case '3':
                return 'rgba(30,144,255,0.25)'; // DodgerBlue
            case '2':
                return 'rgba(0, 128, 0, 0.25)'; // Green
            case '1':
                return 'rgba(255,165,0,0.25)'; // Orange
            case '0':
                return 'rgba(255, 0, 0,0.25)'; // Red
            default:
                return 'rgba(0, 0, 0, 0.25)'; // Default
        }
    }

    // Function to get the image URL for a plant
    getImageUrl(entityId) {
        const state = this._hass.states[entityId];
        const attributes = state ? state.attributes : {};
        const imageUrl = `/local/plant_tracker/${attributes.image || 'default_image'}.jpg`;
        return imageUrl;
    }

    // Function to check if an image exists in the cache or fetch it
    checkImageExists(url) {
        if (this.imageCache.has(url)) return this.imageCache.get(url);

        return fetch(url)
            .then(res => {
                const exists = res.ok;
                this.imageCache.set(url, exists);
                return exists;
            })
            .catch(() => {
                this.imageCache.set(url, false);
                return false;
            });
    }

    // Function to normalize the plant name
    normalizeName(name) {
        return String(name)
            .toLowerCase()
            .normalize("NFD")               // separa los acentos
            .replace(/[\u0300-\u036f]/g, "") // elimina los acentos
            .replace(/\s+/g, " ")           // quita espacios múltiples
            .trim();
    }

    // Function to generate the plant image container HTML
    generatePlantImageContainerHTML(entityId) {
        const localPath = this.getImageUrl(entityId);
        const fullUrl = `${location.origin}${localPath}`;
        const imageExists = this.checkImageExists(fullUrl);

        let htmlContent = `<div class="plant-image-container">`
        if (imageExists) {
            htmlContent += `<img src="${localPath}" alt="Plant Image" class="plant-image">`;
        }
        else {
            htmlContent += `<ha-icon icon="mdi:flower" class="plant-image fallback-icon"></ha-icon>`;
        }
        htmlContent += `</div>`
        return htmlContent;
    }

    // Function to generate the modal content for adding or editing a plant
    generateModalEditPlantBodyHTML(entityId, attributes) {

        const isInside = attributes.inside === true ? 'checked' : '';
        let title = "";
        if (entityId === "") title = "Add New Plant";
        else title = `${attributes.plant_name || 'Unknown'} `;

        // Add the title for the modal
        let content = `
            <div class="modal-header">
                <h2 class="modal-title">` + title + `</h2>
                <span id="EditPlantClose" class="close">&times;</span>
            </div>
        `;

        // Add an error message div
        content += `<div id="error_message" class="error-message"></div>`;

        // Add the content for the modal
        content += '<div class="plant-tracker-entity-modal-content">';

        // Add the plant image
        content += this.generatePlantImageContainerHTML(entityId);

        // Add the plant attributes form
        content += `<form id="editForm" class ="editForm">`;

        // If entityId is empty, we are adding a new plant, so we show the name input
        if (entityId === "") {
            content += `
            <div class="modal-attribute">
                <label for="name">Name:</label>
                <input type="text" id="plant_name" name="plant_name" value="${attributes.plant_name || 'Unknown'}"><br>
            </div>
            `;
        }

        // Add the attributes to the form
        content += `
                <div class="modal-attribute">
                    <label for="last_watered">Last Watered:</label>
                    <input type="text" id="last_watered" name="last_watered" value="${attributes.last_watered || 'Unknown'}"><br>
                    <button type="button" id="last_watered_btn">
                        <ha-icon icon="mdi:water"></ha-icon>
                    </button>
                </div>
                <div class="modal-attribute">
                    <label for="last_fertilized">Last Fertilized:</label>
                    <input type="text" id="last_fertilized" name="last_fertilized" value="${attributes.last_fertilized || 'Unknown'}"><br>
                    <button type="button" id="last_fertilized_btn">
                        <ha-icon icon="mdi:food-fork-drink"></ha-icon>
                    </button>
                </div>
                <div class="modal-attribute">
                    <label for="watering_postponed">Watering Postponed:</label>
                    <input type="text" id="watering_postponed" name="watering_postponed" value="${attributes.watering_postponed || 'Unknown'}"><br>
                    <button type="button" id="watering_postponed_btn">
                        <ha-icon icon="mdi:sleep"></ha-icon>
                    </button>
                </div>
                <div class="modal-attribute">
                    <label for="watering_days">Watering days:</label>
                    <input type="text" id="watering_days" name="watering_days" value="${(attributes.watering_interval) || 'Unknown'}"><br>
                </div>
                <div class="modal-attribute">
                    <label for="inside">Inside:</label>
                    <input type="checkbox" id="inside" name="inside" ${isInside}></input>
                </div>
            </form>
            `
        content += `
            <div class="modal-buttons">
                <mwc-button id="cancel_button" label="Cancel"></mwc-button>
                `
        if (entityId !== "") {
            content += `
                <ha-icon icon="mdi:delete" class="deletePlantButton" title="Delete planta"></ha-icon>`;
        }

        content += `
                <mwc-button id="ok_button" label="OK"></mwc-button>
            </div>
        </div>`

        return content;
    }

    generatePlantCardContentHTML(isInside) {

        // generate the plant tracker card content
        let htmlContent = '';

        if (isInside) {
            htmlContent += `<ha-markdown-element><h1>Indoor Plants</h1></ha-markdown-element>`;
        } else {
            htmlContent += `<ha-markdown-element><h1>Outdoor Plants</h1></ha-markdown-element>`;
        }
        for (const entityId in this._hass.states) {
            // Check if the entity ID starts with 'plant_tracker.'
            if (entityId.startsWith('sensor.plant_tracker')) {
                const state = this._hass.states[entityId];
                const stateStr = state ? state.state : 'unavailable';
                const attributes = state ? state.attributes : {};

                if (isInside === attributes.inside) {

                    const backgroundColor = this.getBackgroundColor(stateStr);

                    // Create the HTML content for each entity
                    // Use the entity ID as the key to access the state and attributes
                    htmlContent += `
                        <div class="plant-tracker-entity" style="background-color: ${backgroundColor};" onclick="showPlantEditModal('${entityId}')">
                    `;
                    htmlContent += this.generatePlantImageContainerHTML(entityId);
                    htmlContent += `
                        <p class="name">${attributes.plant_name || 'Unknown'}</p>
                        <p class="last_watered">Last Watered: ${attributes.last_watered || 'Unknown'}</p>
                        <p class="last_fertilized">Last Fertilized: ${attributes.last_fertilized || 'Unknown'}</p>
                        <p class="due">Due: ${(parseFloat(attributes.watering_interval) - parseFloat(attributes.days_since_watered))} / ${Math.round(parseFloat(attributes.watering_interval)) || 'Unknown'} days</p>
                        <p class="watering_postponed">Watering Postponed: ${attributes.watering_postponed || 'Unknown'}</p>
                    </div>
                    `;
                }
            }
        }
        return htmlContent;
    }

    // Function to get the styles for the card
    getStyles() {
        return `
          <style>
            ha-card {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            .card-actions {
                display: flex;
                justify-content: flex-end;
                margin: 4px;
                margin-bottom: 12px;
            }
            .card-content {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .plant-tracker-entity {
                display: grid;
                grid-template-areas:
                    "i n delete_btn"
                    "i last_watered last_watered"
                    "i last_fertilized last_fertilized"
                    "i due due"
                    "i watering_postponed watering_postponed"
                    "i . .";
                grid-template-columns: min-content 4fr auto;
                grid-template-rows:
                    1fr
                    min-content
                    min-content
                    min-content
                    min-content
                    1fr;
                border-radius: 8px;
                padding: 5px;
                margin-bottom: 16px;
                width: 100%;
                height: 140px;
                box-sizing: border-box;
                cursor: pointer;
            }
            .plant-tracker-entity .plant-image-container {
                grid-area: i;
                display: flex;
                align-items: center;        /* vertical */
                justify-content: center;    /* optional: horizontal */
                max-width: 100px;
				min-width: 100px;
                height: 100%;               /* let it take up the full grid row height */
                border-radius: 8px;
                margin: 0px 0px;
            }
            .plant-tracker-entity .plant-image {
                max-height: 100px;          /* Set a max height */
                max-width: 100%;            /* Prevent overflow */
                height: auto;               /* Maintain aspect ratio */
                width: auto;                /* Let the image scale naturally */
                margin: 0px;               /* Center within flex container */
                display: block;
                border-radius: 8px;
            }
            .plant-tracker-entity .name {
                grid-area: n;
                font-size: 120%;
                margin: 0px 0px 5px 10px;
                justify-self: start;
            }
            .plant-tracker-entity .last_watered,
            .plant-tracker-entity .due,
            .plant-tracker-entity .watering_postponed,
            .plant-tracker-entity .last_fertilized {
                font-size: 90%;
                margin: 0px 0px 0px 10px;
                line-height: 1.2;
            }
            .plant-tracker-entity .last_watered {
                grid-area: last_watered;
            }
            .plant-tracker-entity .due {
                grid-area: due;
            }
            .plant-tracker-entity .watering_postponed {
                grid-area: watering_postponed;
            }
            .plant-tracker-entity .last_fertilized {
                grid-area: last_fertilized;
            }

            .modal {
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.4);
                padding-top: 60px;
            }
            .modal-content {
                background-color: rgb(0,0,0);
                margin: 5% auto;
                padding: 10px;
                border: 1px solid #888;
                width: 90%;
                max-width: 350px;
                max-height: 90vh;
                box-sizing: border-box;
                overflow-x: auto;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            .modal-header {
                position: relative;
                text-align: center;
                margin-bottom: 10px;
            }
            .modal-title {
                font-size: 140%;
                font-weight: bold;
                margin: 0;
                color: var(--primary-text-color, #fff);
            }
            .close {
                position: absolute;
                top: 50%;
                right: 0;
                transform: translateY(-50%);
                font-size: 28px;
                font-weight: bold;
                color: #aaa;
                cursor: pointer;
                line-height: 1;
                padding: 0;
            }
            .modal-buttons {
                margin-top: 10px;
                display: flex;
                justify-content: space-between;
            }
            .deletePlantButton {
                grid-area: delete_btn;
                justify-self: end;
                cursor: pointer;
                color: rgba(255, 1, 1, 0.5);
                --mdc-icon-size: 30px;
            }
            .deletePlantButton:hover {
                color: red;
                transform: scale(1.2);
            }
            .modal-attribute {
                display: flex;
                align-items: center; /* Aligns all children vertically centered */
                gap: 0px; /* Optional: adds space between elements */
                margin: 5px 0;
                min-height: 30px;
            }
            .modal-attribute label {
                width: 150px;
                text-align: left;
            }
            .modal-attribute input {
                width: 50px;
            }
            .modal-attribute input[type="text"],
            .modal-attribute input[type="number"],
            .modal-attribute select {
                flex: 1;
                text-align: right;
                width: 50px;
            }
            .modal-attribute input[type="checkbox"] {
                margin-left: auto;
            }
            .modal-attribute button {
                background: none;
                border: none;
                cursor: pointer;
            }
            .modal-attribute ha-icon {
                --mdc-icon-size: 36px;
                color: var(--primary-color);
            }
            .fallback-icon {
                font-size: 64px;
                --mdc-icon-size: 64px;
                color: #888;
            }
            .error-message {
                color: red;
                font-weight: bold;
                display: none;
                margin-bottom: 10px;
                text-align: center;
            }

            .plant-tracker-entity-modal-content {
                grid-area: content;
                display: grid;
                grid-template-areas:
                    "i"
                    "plant_name"
                    "last_watered"
                    "watering_days"
                    "watering_postponed"
                    "last_fertilized"
                    "inside";
                grid-template-columns: 1fr;
                grid-template-rows:
                    min-content
                    min-content
                    min-content
                    min-content
                    min-content
                    min-content
                    min-content;
                padding: 0px;
                width: 100%;
                height: 100%;
                box-sizing: border-box;
                flex-grow: 2;
            }
            .plant-tracker-entity-modal-content .plant-image-container {
                grid-area: i;
                max-width: 200px;
                max-height: 200px;
                border-radius: 8px;
                margin-top: 10px;
                justify-self: center;
            }
            .plant-tracker-entity-modal-content .plant-image {
                width: 100%;
                height: 100%;
                display: block;
                border-radius: 8px;
            }
            .plant-tracker-entity-modal-content .editForm {
                padding: 10px 10px 0px 10px;
            }
            .plant-tracker-entity-modal-content .plant_name {
                grid-area: plant_name;
            }
            .plant-tracker-entity-modal-content .last_watered {
                grid-area: last_watered;
            }
            .plant-tracker-entity-modal-content .watering_days {
                grid-area: watering_days;
            }
            .plant-tracker-entity-modal-content .watering_postponed {
                grid-area: watering_postponed;
            }
            .plant-tracker-entity-modal-content .last_fertilized {
                grid-area: last_fertilized;
            }
            .plant-tracker-entity-modal-content .inside {
                grid-area: inside;
                justify-self: center;
            }
          </style>`;
    }
}

customElements.define('plant-tracker-card', PlantTrackerCard);