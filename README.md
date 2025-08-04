# 🌿 Plant Diary for Home Assistant

**Plant Diary** is a custom integration and Lovelace card for [Home Assistant](https://www.home-assistant.io/) that helps you manage and monitor your houseplants. Track when each plant was last watered or fertilized, define care intervals, and visualize everything with a custom card.

This work has been inspired by [Plant tracker for Home Assistant](https://github.com/mountwebs/ha-plant-tracker).

## Features

- **Component**
  - Track multiple plants with individual settings
  - Custom watering intervals and postponements
  - Indoor/outdoor plant designation
  - Automatic daily updates for watering days
  - Logbook integration for activity tracking
- **Companion Lovelace Card**
  - Shows days since last watering and fertilizing
  - Supports customizable images for each plant
  - Shows each plant’s watering status with intuitive color codes:
    - 🔵 Blue: watered today
    - 🟢 Green: within watering interval
    - 🔴 Red: past watering interval
    - 🟠 Orange: within postponed watering interval
  - Option to show only plants that currently need watering
  - Quick access to edit plant details via popup dialog

# 🌱 Plant Diary Component

## Installation

### Manual Installation

1. Clone or download this repository.
2. Copy the `plant_diary` folder to your Home Assistant `config/custom_components/` directory: config/custom_components/plant_diary
3. Restart Home Assistant.
4. Go to **Settings > Devices & Services > Devices > Add Device**.
5. Search for **Plant Diary** and add it.

## Plant Data Fields

| Field                | Description                                      |
| -------------------- | ------------------------------------------------ |
| `plant_name`         | Name of the plant                                |
| `last_watered`       | Last watered date (e.g., `2025-07-30`)           |
| `last_fertilized`    | Last fertilized date (optional)                  |
| `watering_interval`  | Days between waterings (default: `14`)           |
| `watering_postponed` | Extra days to postpone watering (default: `0`)   |
| `inside`             | Whether the plant is indoors (`true` or `false`) |
| `image`              | Custom image path or entity picture (optional)   |

## Logbook Integration

Plant Diary logs important events to the Home Assistant logbook. These entries help you keep track of changes made either manually or via automation.

- `Monstera was created.`
- `Monstera was updated.`
- `Monstera was deleted.`

These messages appear in Home Assistant’s **Logbook** panel.

# 🖥️ Lovelace Card

Visualize your plants and their watering status using a custom Lovelace card.

## Preview

### Plant Diary Card

![Plant Diary Card](docs/plant-diary-card.png)

_Overview of multiple plants and their watering status._

### Edit Plant Popup

![Edit Plant](docs/edit-popup.png)

_Popup dialog for editing plant details such as watering schedule and last watered date._

## Installation

1. Download the `plant-diary-card.js` file and place it in your `config/www/plant_diary` directory: config/www//plant_diary/plant-diary-card.js
2. Add the resource to your dashboard via **Settings > Dashboards > Resources**:

```yaml
URL: /local/plant_diary/plant-diary-card.js
```

3. Create a Dashboard using the Sidebar layout
4. Click Add Card, scroll down to Manual and paste the following code

```yaml
type: custom:plant-diary-card
```

## Adding Plant Images

You can add custom images for your plants to enhance the Lovelace card and UI experience.

1. Place your plant images in your Home Assistant `config/www/plant_diary/` directory.
   - The image filename **must** match the plant's name, e.g., `Monstera.jpg` for a plant named "Monstera".
   - Example path:
     `    config/www/plant_diary/Monstera.jpg`
     The Lovelace card and UI will use this image for the corresponding plant.

# 🐛 Issues & Feedback

If you encounter any issues or would like to suggest improvements:

- 📌 Open an issue on GitHub: [https://github.com/xplanes/ha-plant-diary/issues](https://github.com/xplanes/ha-plant-diary/issues)
- 🙌 Pull requests are welcome!

Please include logs or reproduction steps when reporting bugs.

# 🧠 Roadmap

Planned features and improvements for future versions:

- ✅ Create, update, and delete plant entries
- ✅ Daily tracking of days since watering
- ✅ Lovelace card for visualizing plant data
- ✅ Logbook integration
- 🔜 Reminder notifications for watering and fertilizing
- 🔜 Integration with moisture/humidity sensors
- 🔜 Multi-language support

Feel free to contribute to the roadmap or suggest new ideas!

## 📄 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for full license text.

© 2025 [@xplanes](https://github.com/xplanes)
