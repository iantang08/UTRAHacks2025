import math

class Stat:
    def __init__(self, name, id, data, heartrate, ideal_data):
        self.name = name
        self.id = id
        self.data = data  # Tuple (x, y, z)
        self.heartrate = heartrate
        self.ideal_data = ideal_data  # Ideal tuple (x, y, z)
        self.heart_rate_history = []  # List to store heart rates over time

    def calculate_consistency(self):
        # Calculate the Euclidean distance between data and ideal_data
        sum = self.data[0] + self.data[1] + self.data[2]
        idealSum = self.ideal_data[0] + self.ideal_data[1] + self.ideal_data[2]
        consistency = 100-(abs(sum-idealSum)/idealSum * 100)
        return consistency

    def add_heart_rate(self, heart_rate):
        # Add a new heart rate to the history
        self.heart_rate_history.append(heart_rate)

        # If there are more than 10 heart rates, pop the oldest one
        if len(self.heart_rate_history) > 10:
            self.heart_rate_history.pop(0)

        # Calculate the average heart rate
        average_heart_rate = sum(self.heart_rate_history) / len(self.heart_rate_history)
        
        # Return the average heart rate
        return average_heart_rate

    def get_heart_rate_data(self):
        # Return the heart rate history
        return self.heart_rate_history
