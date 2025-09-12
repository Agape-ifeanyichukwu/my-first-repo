digits = ['zero', 'one', 'two', 'three', 'four',
          'five', 'six', 'seven', 'eight', 'nine']

# Read the phone number as a string
phone_number = input("Enter the phone number: ")

# Iterate over each character in the string
for char in phone_number:
    # Convert the character to integer index
    index = int(char)
    # Print the corresponding digit name
    print(digits[index])
