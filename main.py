import json
import re
from datetime import datetime

# Constants
PARKING_RATE_PER_HOUR = 5
DATA_FILE = "data.json"


class Park:
    def __init__(self, identity, arrival_time, frequent_parking_number):
        self.identity = identity
        self.arrival_time = arrival_time
        self.frequent_parking_number = frequent_parking_number


# Utility Functions
def validate_car_identity(identity):
    pattern = r"^\d{2}[A-Z]-\d{5}$"

    if re.match(pattern, identity):
        return True
    else:
        return False


# valid number: 73278
def validate_frequent_parking_number(number):
    if len(number) != 5 or not number.isdigit():
        return False

    digits = [int(digit) for digit in number]
    check_digit = digits.pop()

    calculated_check_digit = sum(digits) % 11

    return calculated_check_digit == check_digit


def calculate_parking_fee(arrival_time, departure_time):
    duration = departure_time - arrival_time
    hours = duration.total_seconds() / 3600
    return round(hours * PARKING_RATE_PER_HOUR, 2)


def read_data_from_file(file_name):
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File {file_name} not found. Creating a new file.")
        with open(file_name, "w") as file:
            json.dump({}, file)  # Create an empty JSON object
        return {}
    except json.JSONDecodeError:
        print(f"File {file_name} is empty or corrupted. Returning empty data.")
        return {}


def write_data_to_file(file_name, data):
    with open(file_name, "w") as file:
        json.dump(data, file)


def write_history_to_file(file_name, data):
    with open(file_name, "w") as file:
        file.write(f"Total Payments: {data['total_payments']}\n")
        file.write(f"Available Credits: {data['available_credits']}\n")
        file.write(f"Parked Dates:\n")
        for parked_date in data["parked_dates"]:
            file.write(f"{parked_date}\n")

def read_history_from_file(file_name):
    try:
        with open(file_name, "r") as file:
            data = file.readlines()
            # Read the first two lines
            total_payments = float(data[0].split(":")[1].strip())
            available_credits = float(data[1].split(":")[1].strip())
            
            parked_dates = []
            for line in data[3:]:
                parked_dates.append(line.strip())
            return {
                "total_payments": total_payments,
                "available_credits": available_credits,
                "parked_dates": parked_dates,
            }
    except FileNotFoundError:
        return False

def validate_arrival_time(time):
    try:
        parsed_time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        return True, parsed_time
    except ValueError:
        print("Invalid time format. Please use YYYY-MM-DD HH:MM format.")
        return False, None


# Main Menu
def main_menu():
    while True:
        print("\nCar Parking System")
        print("1. Park")
        print("2. Pick Up")
        print("3. History")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            park_car()
        elif choice == "2":
            pick_up_car()
        elif choice == "3":
            view_history()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


# Park Car
def park_car():
    print("\nParking a Car")
    car_identity = input("Car identity:")
    arrival_time = input("Arrival time:")
    frequent_parking_number = input("Frequent Parking Number:")

    is_valid_car_identity = validate_car_identity(car_identity)
    is_valid_arrival_time = validate_arrival_time(arrival_time)
    is_valid_frequent_parking_number = validate_frequent_parking_number(frequent_parking_number) if frequent_parking_number.isdigit() else True

    if is_valid_car_identity and is_valid_arrival_time and is_valid_frequent_parking_number:
        data = read_data_from_file(DATA_FILE)
        data[car_identity] = {
            "arrival_time": arrival_time,
            "frequent_parking_number": frequent_parking_number,
        }

        write_data_to_file(DATA_FILE, data)
        print("Car parked")
    else:
        if not is_valid_car_identity:
            print("Invalid car identity")
        if not is_valid_arrival_time:
            print("Invalid arrival time")
        if not is_valid_frequent_parking_number:
            print("Invalid frequent parking number")

        print("Invalid data")


# Pick Up Car
def pick_up_car():
    print("\nPicking Up a Car")
    car_identity = input("Enter car identity: ")
    data = read_data_from_file(DATA_FILE)
    if car_identity in data:
        arrival_time = datetime.strptime(
            data[car_identity]["arrival_time"], "%Y-%m-%d %H:%M"
        )
        departure_time = datetime.now()
        fee = calculate_parking_fee(arrival_time, departure_time)
        print(f"Total parking fee: ${fee:.2f}")
        
        while True:
            try:
                payment = float(input("Enter payment amount: "))
                if payment < fee:
                    print("Insufficient payment. Please pay the full amount.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value.")

        excess_payment = payment - fee
        print(f"Payment successful. Excess amount: ${excess_payment:.2f}")

        history_data = read_history_from_file(f"{car_identity}.txt")
        total_payments = history_data.get("total_payments", 0) + payment
        available_credits = history_data.get("available_credits", 0) + excess_payment

        updated_history = {
            "total_payments": total_payments,
            "available_credits": available_credits,
            "parked_dates": history_data.get("parked_dates", []) + [f"{data[car_identity]['arrival_time']} - {departure_time.strftime("%Y-%m-%d %H:%M")} ${fee:.2f}"]
        }

        write_history_to_file(f"{car_identity}.txt", updated_history)

        # Remove entry from main data file
        del data[car_identity]
        write_data_to_file(DATA_FILE, data)
    else:
        print("Car identity not found.")


# View History
def view_history():
    print("\nExporting Parking History")
    car_identity = input("Enter car identity: ")
    data = read_data_from_file(DATA_FILE)
    if car_identity in data:
        history_file_name = f"{car_identity}.txt"
        history_data = read_history_from_file(history_file_name)
        total_payments = history_data.get("total_payments", 0) if history_data != False else 0
        available_credits = history_data.get("available_credits", 0) if history_data != False else 0
        parked_dates = history_data.get("parked_dates", []) if history_data != False else []
        with open(history_file_name, "w") as file:
            file.write(f"Total Payments: {total_payments}\n")
            file.write(f"Available Credits: {available_credits}\n")
            file.write(f"Parked Dates:\n")
            for parked_date in parked_dates:
                file.write(f"{parked_date}\n")

            file.write(
                f"{data[car_identity]['arrival_time']} - Stay Time ...\n"
            )
        print(f"History written to {history_file_name}")
    else:
        print("Car identity not found.")


if __name__ == "__main__":
    main_menu()