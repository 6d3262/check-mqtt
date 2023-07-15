"""
This script is designed to monitor the message reception of Zigbee Router/Repeater devices via the MQTT protocol 
using Zigbee2MQTT. The script can operate in either 'check' or 'debug' mode, specified as command line arguments. 

- In 'check' mode, the script listens for MQTT messages from the specified devices for a fixed amount of time. 
  If no messages are received in this period, a notification is sent via Telegram.
- In 'debug' mode, the script will print out diagnostic information regarding its connection to the MQTT broker and
  incoming messages and sends a telegram notification regarding the result.

The script fetches the following configuration from a config.ini file:
- MQTT_USER: The username for the MQTT broker.
- MQTT_PASS: The password for the MQTT broker.
- MQTT_BROKER: The URL of the MQTT broker.
- TELEGRAM_BOT_TOKEN: The bot token for the Telegram bot that will be used to send notifications.
- CHAT_ID: The ID of the chat where the Telegram bot will send notifications.
- DEVICES: A list of MQTT topics corresponding to the devices the script should listen to.

Run this script via cron. For example:
*/15 * * * * /usr/bin/python3 /path/to/your/script.py -c -t 120
"""

from configparser import ConfigParser
import argparse
import configparser
import paho.mqtt.client as mqtt
import requests
import sys
import time

try:
    # Fetching credentials from the config.ini file
    config = ConfigParser()
    config.read('config.ini')

    # Fetching MQTT credentials from the config file
    MQTT_USER = config.get('MQTT', 'USER')
    MQTT_PASS = config.get('MQTT', 'PASS')
    MQTT_BROKER = config.get('MQTT', 'BROKER')

    # Fetching MQTT topics for devices to monitor from the config file
    DEVICES = config.get('DEVICES', 'TOPICS').split(', ')

    # Fetching Telegram Bot Token and Chat ID from the config file
    TELEGRAM_BOT_TOKEN = config.get('TELEGRAM', 'BOT_TOKEN')
    CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')
except (configparser.NoSectionError, configparser.NoOptionError) as e:
    print(f"Error occurred while reading config.ini file: {e}")
    sys.exit(1)  # Exit program if there's an error reading the config file

# This function is responsible for sending the telegram notification
def send_telegram_notification(message, success=False):
    # Determine whether to send notification
    send_notification = args.check or args.debug or success
    if not send_notification:
        return

    # If success flag is True, print the success message
    if success:
        print(f"Successful check: {message}")

    # Prepare and send the Telegram notification
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except requests.exceptions.RequestException as e: 
        print(f"Error occurred while sending Telegram notification: {e}")

# This function is called when MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
    # Initialize a dictionary in userdata to False for all devices
    if args.debug:
        print(f"Connected to MQTT broker")

# This function is called when an MQTT message is received
def on_message(client, userdata, msg):
    device = msg.topic  # Get the device topic
    # Set flag to True when a message is received
    userdata['message_received'][device] = True  
    if args.debug:
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

# This function creates and returns an MQTT client
def create_mqtt_client(user, passw, broker):
    client = mqtt.Client(userdata={'message_received': {device: False for device in DEVICES}})
    client.username_pw_set(user, passw)
    try:
        client.connect(broker, 1883, 60)
    except Exception as e:
        print(f"Error occurred while connecting to MQTT broker: {e}")
        return None  # Return None if connection fails
    return client

# This function subscribes the MQTT client to all devices
def subscribe_to_devices(client, devices):
    for device in devices:
        client.subscribe(device)

# This function starts the MQTT client's network loop
def start_client_loop(client):
    client.loop_start()

# This function stops the MQTT client's network loop
def stop_client_loop(client):
    client.loop_stop()

# This function checks periodically whether any device has sent a message
def listen_for_messages(client, listen_time):
    start_time = time.time()
    any_device_message_received = False
    devices_reported_back = set()
    while time.time() - start_time < listen_time:
        if any(client._userdata['message_received'].values()):  # Check if any device has sent a message
            any_device_message_received = True
            for device, message_received in client._userdata['message_received'].items():
                if message_received:
                    devices_reported_back.add(device)  # Use a set to eliminate duplicates
        time.sleep(1)  # Sleep for 1 second before checking again
    return any_device_message_received

# Main function of the script that handles the main logic
def main():
    # Create MQTT client
    client = create_mqtt_client(MQTT_USER, MQTT_PASS, MQTT_BROKER)
    
    # If client creation failed (i.e., could not connect to MQTT broker)
    if client is None:
        send_telegram_notification("Could not connect to MQTT broker. Please check your MQTT settings.")
        return  # Stop execution if MQTT connection failed
    
    # Set up MQTT client callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Subscribe MQTT client to the device topics
    subscribe_to_devices(client, DEVICES)

    # Start MQTT client's network loop
    start_client_loop(client)

    # Listen for messages from devices for a specified time period
    any_device_message_received = listen_for_messages(client, args.time)

    # Stop MQTT client's network loop
    stop_client_loop(client)

    # Send notification based on the operation mode and whether any message was received
    if args.check:
        if not any_device_message_received:
            send_telegram_notification('No MQTT message was received from any device. Please check.')
    else:
        if any_device_message_received:
            send_telegram_notification('At least one device has sent an MQTT message. Your Zigbee Router/Repeater is working properly.')
        else:
            send_telegram_notification('No MQTT message was received from any device. Your Zigbee Router/Repeater may not be functioning properly. Please check.')

# Main entry point of the script
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description='Check Zigbee Router/Repeater MQTT message reception and send Telegram notifications.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--check', action='store_true', help='Check for normal operation')
    group.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-t', '--time', type=int, required=True, help='Amount of time in seconds to listen for an MQTT message')

    args = parser.parse_args()

    main()