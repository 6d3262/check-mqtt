# Zigbee MQTT Message Reception Monitor

This script is designed to monitor the message reception of Zigbee Router/Repeater devices via the MQTT protocol using the Zigbee2MQTT utility, and send notifications via Telegram. The script can operate in either **'check'** or **'debug'** mode.

- In **'check'** mode, the script listens for MQTT messages from the specified devices for a fixed amount of time. If no messages are received in this period, a notification is sent via Telegram.
- In **'debug'** mode, the script will print out diagnostic information regarding its connection to the MQTT broker and incoming messages.

## Setup and Configuration

You need to have an MQTT broker running and accessible to the script. This is where Zigbee2MQTT will send its messages. The script also requires access to a Telegram bot for sending notifications.

The MQTT broker credentials, Telegram bot token, chat ID, and the list of device topics that you want to monitor are specified in a configuration file (config.ini). An example configuration is provided, which you can modify:

```ini
[MQTT]
USER = MQTT_USERNAME
PASS = MQTT_PASSWORD
BROKER = IP_OR_HOSTNAME_OF_YOU_MQTT_BROKER

[TELEGRAM]
BOT_TOKEN = YOUR_BOT_TOKEN
CHAT_ID = YOUR_CHAT_ID

[DEVICES]
TOPICS = TOPIC/DEVICENAME_1, TOPIC/DEVICENAME_2, TOPIC/DEVICENAME_3
```

The `TOPICS` field under `DEVICES` is a comma-separated list of the MQTT topics of the devices you want to monitor. The script will automatically split this list into individual topics.

Running the Script

The script can be run manually or set up as a cron job to periodically check the MQTT message reception of your devices. Here is an example of how to run the script:

```bash
/usr/bin/python3 /path/to/your/script.py -c -t 120
```

In this example, the script is run in **'check'** mode (`-c`), and will listen for messages for 120 seconds (`-t 120`).

You can also run the script in **'debug'** mode using the `-d` argument instead of `-c`.

## Dependencies

This script depends on the following Python libraries:

- paho-mqtt: MQTT client library
- requests: For sending HTTP requests (used for sending Telegram notifications)

You can install these dependencies using pip:

```shell
pip install paho-mqtt requests
```

## Running the script

Make sure you have Python 3 installed on your system. You can check this by running:

```sh
python3 --version
```

If Python 3 is installed, it should display the version. If it's not installed, you will need to install it. The process to do this depends on your operating system.

You also need to have the `paho-mqtt` and `requests` Python packages installed. If you don't have them installed, you can do so using pip, which is a package manager for Python. Run the following command to install the necessary dependencies:

```sh
pip install paho-mqtt requests
```

Or if you are using a system where Python 3 is not the default version:

```sh
pip3 install paho-mqtt requests
```

Once you have Python 3 and the necessary packages installed, you can run the script using the command shown in the Usage section.

## Notifications

This script sends notifications via Telegram when it doesn't receive MQTT messages from the specified devices within the listening period.

You need to replace the placeholder `BOT_TOKEN` and `CHAT_ID` in the `config.ini` file with your actual Telegram bot token and the chat ID where you want to receive notifications.

To generate a new bot token, you can use the BotFather bot on Telegram. To find the chat ID, you can use the `getUpdates` API of your bot.

Ensure you have the correct permissions to send messages to the chat. You might need to add your bot to the chat or start a conversation with the bot first.

## Error handling

The script includes error handling for connecting to the MQTT broker and sending Telegram messages. If an error occurs while connecting to the MQTT broker, the script will terminate and send a notification via Telegram. If an error occurs while sending a Telegram message, an error message will be printed to the console.

## Contributing

If you encounter any issues while using this script or have suggestions for improvements, feel free to open an issue or submit a pull request. All contributions are welcome.

## License

This script is provided under the MIT License. You are free to use, modify, and distribute it as you see fit. However, it comes with no warranty of any kind.
