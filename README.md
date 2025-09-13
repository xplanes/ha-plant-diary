# 🌿 Plant Diary Integration for Home Assistant

**Plant Diary** is a custom integration for [Home Assistant](https://www.home-assistant.io/) that helps you manage and monitor your houseplants. Track when each plant was last watered or fertilized, define care intervals, and visualize everything with a custom card [Plant Diary Card](https://github.com/xplanes/ha-plant-diary-card).

This work has been inspired by [Plant tracker for Home Assistant](https://github.com/mountwebs/ha-plant-tracker).

# Features

- Track multiple plants with individual settings
- Custom watering intervals and postponements
- Indoor/outdoor plant designation
- Automatic daily updates for watering days
- Logbook integration for activity tracking

# Installation

You can install this component in two ways: via [HACS](https://github.com/hacs/integration) or manually.

## Option A: Installing via HACS

### Plant Diary integration

1. Go to the HACS Integration Tab
2. Search the `Plant Diary` component and click on it.
3. Click Download button at the bottom of the page. A pop up will be shown informing you that the component will be installed in the folder `/config/custom_components/plant_diary`. Click Download.

### Plant Diary Card

1. Go to the HACS Integration Tab
2. Search the `Plant Diary Card` component and click on it.
3. Click Download button at the bottom of the page. A pop up will be shown informing you that the component will be installed in the folder `/config/www/community/ha-plant-diary-card`. Click Download. The JavaScript module will be automatically added to the Dashboard Resources (/hacsfiles/ha-plant-diary-card/ha-plant-diary-card.js).

## Option B: Manual Installation

### Plant Diary integration

1. Clone or download the GitHub repository: [ha-plant-diary](https://github.com/xplanes/ha-plant-diary)
2. Copy the `custom_components/plant_diary` folder to your Home Assistant `config/custom_components/` directory: config/custom_components/plant_diary
3. Restart Home Assistant.

### Plant Diary Card

1. Clone or download the GitHub repository: [ha-plant-diary-card](https://github.com/xplanes/ha-plant-diary-card)
1. Place the file `ha-plant-diary-card.js` in your `config/www/plant_diary` directory: config/www/plant_diary/ha-plant-diary-card.js
1. Add the resource to your dashboard via **Settings > Dashboards > Resources**:

```yaml
URL: /local/plant_diary/ha-plant-diary-card.js
```

# Configuration

### Plant Diary integration

1. Go to **Settings > Devices & Services > Devices > Add Device**.
2. Search for **Plant Diary** and add it.

### Plant Diary Card

1. Create a Dashboard using the Sidebar layout
2. Click Add Card and search for `Plant Diary Card`

# Plant Data Fields

| Field                | Description                                      |
| -------------------- | ------------------------------------------------ |
| `plant_name`         | Name of the plant                                |
| `last_watered`       | Last watered date (e.g., `2025-07-30`)           |
| `last_fertilized`    | Last fertilized date (optional)                  |
| `watering_interval`  | Days between waterings (default: `14`)           |
| `watering_postponed` | Extra days to postpone watering (default: `0`)   |
| `inside`             | Whether the plant is indoors (`true` or `false`) |
| `image`              | Custom image path or entity picture (optional)   |

# Logbook Integration

Plant Diary logs important events to the Home Assistant logbook. These entries help you keep track of changes made either manually or via automation.

- `Monstera was created.`
- `Monstera was updated.`
- `Monstera was deleted.`

These messages appear in Home Assistant’s **Logbook** panel.

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

# 📄 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for full license text.

© 2025 [@xplanes](https://github.com/xplanes)
