from datetime import datetime, timedelta

# Define the rates as constants for now. Replace these with the values from your table.
DAY_RATES = {'Sunday': 2.00, 'Monday': 10.00, 'Tuesday': 10.00, 'Wednesday': 10.00, 'Thursday': 10.00, 'Friday': 10.00, 'Saturday': 3.00}
NIGHT_RATES = {'Sunday': 5.00, 'Monday': 5.00, 'Tuesday': 5.00, 'Wednesday': 5.00, 'Thursday': 5.00, 'Friday': 5.00, 'Saturday': 5.00}
LATE_NIGHT_FLAT_RATE = 20.00

# Maximum stay hours
MAX_STAY_HOURS = {'Sunday': 8, 'Monday': 2, 'Tuesday': 2, 'Wednesday': 2, 'Thursday': 2, 'Friday': 2, 'Saturday': 4}

# Discounts for frequent parking numbers
EVENING_DISCOUNT = 0.50  # 50% discount for 17:00 - Midnight
OTHER_TIMES_DISCOUNT = 0.10  # 10% discount for other times

def calculate_fee(arrival_time, departure_time, frequent_parker_number=None):
    total_fee = 0
    current_time = arrival_time

    stayed_in_day_hours = 0
    late_night_charged = False
    while current_time < departure_time:
        # Determine the current rate based on the time of day
        if current_time.hour >= 8 and current_time.hour < 17:
            # Apply day rate
            rate = DAY_RATES[current_time.strftime('%A')]
            stayed_in_day_hours += 1

            if stayed_in_day_hours > MAX_STAY_HOURS[current_time.strftime('%A')]:
                rate = rate * 2

        elif current_time.hour >= 17 and current_time.hour < 24:
            # Apply night rate
            rate = NIGHT_RATES[current_time.strftime('%A')]
        else:
            rate = LATE_NIGHT_FLAT_RATE if not frequent_parker_number else LATE_NIGHT_FLAT_RATE * EVENING_DISCOUNT

            if not late_night_charged:
                total_fee += rate
                late_night_charged = True

        # Calculate the fee for the current hour
        hourly_fee = rate if not late_night_charged else 0
        if frequent_parker_number:
            if current_time.hour >= 17 or current_time.hour < 8:
                hourly_fee *= (1 - EVENING_DISCOUNT)
            else:
                hourly_fee *= (1 - OTHER_TIMES_DISCOUNT)

        total_fee += hourly_fee

        print(f"{current_time}: ${hourly_fee:.2f} (rate: ${rate:.2f})")

        # Move to the next hour
        current_time += timedelta(hours=1)

        # reset stayed_in_day_hours if it is a new day
        if current_time.hour == 8:
            stayed_in_day_hours = 0
            late_night_charged = False


    return total_fee
