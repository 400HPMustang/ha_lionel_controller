# Lionel Train Controller

A Home Assistant custom integration for controlling Lionel LionChief Bluetooth locomotives.

This fork adds current Home Assistant Bluetooth handling, non-blocking connection monitoring, multi-train support, model-specific announcement labels, diagnostics, and a custom Lovelace card.

## Features

- Throttle control from 0-100%
- Forward, reverse, and stop controls
- Horn, bell, lights, and announcement controls
- Master, horn, bell, speech, and engine volume controls
- Bluetooth connection status and diagnostics
- Automatic reconnection when a locomotive becomes available
- Home Assistant Bluetooth discovery, including compatible Bluetooth proxies
- Multiple Lionel locomotives in one Home Assistant instance
- Model-specific announcement labels for supported train models
- Optional custom Lovelace control card

## Installation

### HACS

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/400HPMustang/ha_lionel_controller` as an **Integration** repository.
4. Install **Lionel Train Controller**.
5. Restart Home Assistant.

### Manual

Copy `custom_components/lionel_controller` into your Home Assistant `custom_components` directory and restart Home Assistant.

## Configuration

### Bluetooth discovery

1. Power on the LionChief locomotive near a Home Assistant Bluetooth adapter or compatible Bluetooth proxy.
2. Home Assistant should discover the locomotive automatically when the LionChief service UUID is advertised.
3. Open **Settings → Devices & services** and configure the discovered train.
4. Select the train model. The model choice controls the announcement button labels; choose **Generic** when the train is not listed.

### Manual setup

1. Open **Settings → Devices & services → Add integration**.
2. Search for **Lionel Train Controller**.
3. Choose **Enter MAC address manually**.
4. Enter the locomotive Bluetooth MAC address and a friendly name.
5. Select the train model.

The locomotive must be powered on and visible to Home Assistant Bluetooth during manual validation. The integration uses Home Assistant's Bluetooth stack rather than starting its own scanner, so devices reachable through supported Bluetooth proxies can be used as well.

Example MAC address: `FC:1F:C3:9F:A5:4A`.

## Entities

### Numbers

- Throttle
- Master Volume
- Horn Volume
- Bell Volume
- Speech Volume
- Engine Volume

### Switches

- Lights
- Auto Reconnect

### Buttons

- Connect
- Disconnect
- Stop
- Forward
- Reverse
- Horn
- Bell
- Announcement buttons

### Sensors

- Connection
- Status
- Train Model
- Direction
- Diagnostics

## Service actions

The integration also exposes `lionel_controller.*` service actions for advanced automations. When more than one Lionel train is configured, select the **Train** field so the action targets the correct configuration entry. Old service calls without a target remain compatible when exactly one Lionel train is loaded.

Available actions include:

- `lionel_controller.set_speed`
- `lionel_controller.set_direction`
- `lionel_controller.stop`
- `lionel_controller.horn`
- `lionel_controller.bell`
- `lionel_controller.lights_on`
- `lionel_controller.lights_off`
- `lionel_controller.play_announcement`
- `lionel_controller.connect`
- `lionel_controller.disconnect`

For normal dashboard and automation use, the number, switch, and button entities are usually simpler than calling these actions directly.

## Bluetooth protocol

Known LionChief UUIDs used by the integration:

- LionChief service: `e20a39f4-73f5-4bc4-a12f-17d1ad07a961`
- Write characteristic: `08590f7e-db05-467e-8757-72f6faeb13d4`
- Notify characteristic: `08590f7e-db05-467e-8757-72f6faeb14d3`

Basic commands use the LionChief-compatible structure implemented by the integration and are sent directly over BLE.

## Connection behavior

Home Assistant startup is not blocked waiting for a powered-off train. Each configured locomotive starts an availability monitor as a background task. When the train is detected, the integration connects in the background. If a connected train drops offline, automatic reconnect attempts are made and the integration falls back to availability monitoring if the finite reconnect loop is exhausted.

The **Auto Reconnect** switch can disable that behavior for an individual locomotive.

## Custom Lovelace card

The integration includes `lionel-train-card.js`.

Add the resource under **Settings → Dashboards → Resources**:

- URL: `/lionel_controller/lionel-train-card.js`
- Type: **JavaScript Module**

Then add the Lionel Train Controller custom card to a dashboard and select the train throttle entity.

## Troubleshooting

If a train will not connect:

- Confirm the locomotive is powered on.
- Confirm Home Assistant Bluetooth can currently see the train.
- If using an ESPHome Bluetooth proxy, verify that proxy is online.
- Check the train's **Connection** and **Diagnostics** entities.
- Use the **Connect** button to force a fresh connection attempt.

For setup problems, enable debug logging for the integration and include the relevant Home Assistant Core log when opening an issue.

## Compatibility

- Designed for current Home Assistant releases using the modern Bluetooth APIs.
- HACS metadata declares Home Assistant `2025.7.0` or newer.
- Tested protocol behavior is based on Lionel LionChief Bluetooth locomotives; individual models may expose different sounds or capabilities.

## Credits

- Protocol reverse engineering by [Property404](https://github.com/Property404/lionchief-controller)
- ESPHome reference implementation by [@iamjoshk](https://github.com/iamjoshk/home-assistant-collection/tree/main/ESPHome/LionelController)
- Additional protocol details from [pedasmith's BluetoothDeviceController](https://github.com/pedasmith/BluetoothDeviceController/blob/main/BluetoothProtocolsDevices/Lionel_LionChief.cs)
- Earlier Home Assistant integration work by [BlackandBlue1908](https://github.com/BlackandBlue1908/ha_lionel_controller)
