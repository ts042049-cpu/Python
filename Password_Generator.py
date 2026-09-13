import random
import string

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


print("================================")
print("       PASSWORD GENERATOR")
print("================================")

while True:
    try:
        length = int(input("Enter password length: "))

        if length < 4:
            print("Password length should be at least 4.")
            continue

        password = generate_password(length)

        print("\nGenerated Password:")
        print(password)

        again = input("\nGenerate another password? (yes/no): ").lower()

        if again != "yes":
            print("Thank you for using Password Generator!")
            break

    except ValueError:
        print("Please enter a valid number.")