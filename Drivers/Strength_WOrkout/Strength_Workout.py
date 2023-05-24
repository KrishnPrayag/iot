#!/usr/bin/env python3
#! bin/bash
#! bin/sh
import sys
import time
import os
from mqtt_client import MQTTClient
from StrengthWorkout_class import StrengthWorkout
from dotenv import load_dotenv, set_key

MAX_WORKOUT_DURATION = 20  # Maximum duration of the workout in minutes

def perform_actions(resistence_level):
    mqtt_client.publish(f"bike/000001/resistance/control", resistence_level)


def perform_strength_workout(strength_workout_object):
    print("Starting strength workout in 5 seconds...")
    time.sleep(5)

    resistance_level = -1  # Initial value to enter the loop

    while resistance_level < 0 or resistance_level > 100:
        resistance_level = int(input("Enter the resistance percentage (0-100%): "))
        
        if resistance_level < 0 or resistance_level > 100:
            print("Invalid resistance percentage. Please enter a value between 0 and 100.")


    start_time = time.time()    
    
    try:
        while True:
            current_time = time.time() - start_time
            if current_time >= (strength_workout_object.duration * 60) or current_time >= (MAX_WORKOUT_DURATION * 60):
                break

            # Store the resistance level in the strength workout object
            strength_workout_object.resistance_data.append(resistance_level)

            # Perform the strength workout action based on the resistance level
            perform_actions(resistance_level)

            if current_time % 120 == 0 and resistance_level < 100:
                resistance_level += 5

            time.sleep(1)

    except KeyboardInterrupt:
        print("Workout stopped")
        print("Count of data points given: " + str(len(strength_workout_object.resistance_data)))

def set_workout_duration(strength_workout_object):
    # Read the command line argument for setting the duration of the workout
    if len(sys.argv) > 1:
        strength_workout_object.duration = int(sys.argv[1])
        if strength_workout_object.duration > MAX_WORKOUT_DURATION:
            strength_workout_object.duration = MAX_WORKOUT_DURATION
            print("Duration exceeds maximum limit of 20 minutes. Setting duration to 20 minutes.")
        print("Duration set to " + str(strength_workout_object.duration) + " minutes")
    else:
        # Default duration is 20 minutes (no argument given)
        strength_workout_object.duration = 20
        print("Duration not specified, defaulting to 20 minutes")

def main():
    try:
        # Load environment variables from the .env file
        env_path = '/home/pi/.env'
        load_dotenv(env_path)

        # Instantiate StrengthWorkout object and initialize duration to user-set parameter
        strength_workout_object = StrengthWorkout()
        strength_workout_object.__init__()

        global mqtt_client
        global deviceId

        set_workout_duration(strength_workout_object)

        # Initialize MQTT client and subscribe to resistance topic
        mqtt_client = MQTTClient(os.getenv('MQTT_HOSTNAME'), os.getenv('MQTT_USERNAME'), os.getenv('MQTT_PASSWORD'))
        deviceId = os.getenv('DEVICE_ID')
        topic = f'bike/{deviceId}/resistance'
        print(deviceId)
        print(topic)
        mqtt_client.setup_mqtt_client()
        mqtt_client.subscribe(topic)
        mqtt_client.get_client().on_message = strength_workout_object.read_remote_data

        mqtt_client.get_client().loop_start()

        # Start the strength workout
        print("Starting the strength workout...")
        perform_strength_workout(strength_workout_object)
        print("Workout complete.")

    except KeyboardInterrupt:
        pass
    mqtt_client.get_client().loop_stop()

if __name__ == "__main__":
    main()
