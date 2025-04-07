# PV Microinverter Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacs-shield]][hacs]

_Home Assistant integration to get data from PV Microinverter systems._

## Overview

This integration allows you to monitor your solar PV microinverter system in Home Assistant. It periodically fetches data from the microinverter API and provides sensor entities for:

- Current power generation
- Today's energy production
- Lifetime energy production

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Go to HACS > Integrations.
3. Click on the "+ Explore & Download Repositories" button.
4. Search for "PV Microinverter".
5. Click on it and select "Download".
6. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/pv_microinverter` directory from this repository to the `custom_components` directory in your Home Assistant configuration directory.
2. Restart Home Assistant.

## Configuration

1. Go to Settings > Devices & Services.
2. Click on the "+ Add Integration" button.
3. Search for "PV Microinverter".
4. Follow the configuration steps, providing:
   - API Key: Your PV Microinverter API key
   - System ID: Your system ID
   - Update Interval: How often to refresh data (in seconds, default is 300)

## Usage

After configuration, the integration will create several sensors:

- `sensor.pv_microinverter_current_power`: Shows the current power generation in watts.
- `sensor.pv_microinverter_today_energy`: Shows today's energy production in kilowatt-hours.
- `sensor.pv_microinverter_lifetime_energy`: Shows the lifetime energy production in kilowatt-hours.

These sensors can be used in automations, dashboards, energy monitoring, and more.

## Example Lovelace UI

```yaml
type: entities
entities:
  - entity: sensor.pv_microinverter_current_power
  - entity: sensor.pv_microinverter_today_energy
  - entity: sensor.pv_microinverter_lifetime_energy
title: Solar Production
```

## Troubleshooting

- **No data or errors**: Check your API credentials and system ID.
- **Delayed updates**: Adjust the update interval to refresh more frequently.
- **API rate limiting**: If you experience API rate limiting, increase the update interval.

## Contributing

If you want to contribute to this integration, please read the [Contributing Guidelines](CONTRIBUTING.md).

## License

This integration is licensed under the MIT License.

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/your-github-username/pv_microinverter.svg
[commits]: https://github.com/your-github-username/pv_microinverter/commits/main
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs]: https://github.com/hacs/integration
[license-shield]: https://img.shields.io/github/license/your-github-username/pv_microinverter.svg
[releases-shield]: https://img.shields.io/github/release/your-github-username/pv_microinverter.svg
[releases]: https://github.com/your-github-username/pv_microinverter/releases
