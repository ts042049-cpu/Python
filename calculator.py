def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error! Division by zero."
    return a / b


print("🔢 Simple Python Calculator")
print("Operations:")
print("1. Add (+)")
print("2. Subtract (-)")
print("3. Multiply (*)")
print("4. Divide (/)")

while True:
    choice = input("\nEnter choice (1/2/3/4) or 'q' to quit: ")

    if choice == 'q':
        print("Calculator closed.")
        break

    if choice in ['1', '2', '3', '4']:
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))

            if choice == '1':
                print("Result:", add(num1, num2))

            elif choice == '2':
                print("Result:", subtract(num1, num2))

            elif choice == '3':
                print("Result:", multiply(num1, num2))

            elif choice == '4':
                print("Result:", divide(num1, num2))

        except ValueError:
            print("Invalid input! Please enter numbers.")
    else:
        print("Invalid choice! Try again.")