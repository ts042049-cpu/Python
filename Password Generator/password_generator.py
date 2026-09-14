import random
import string
import math

def generate_password(length=16, include_uppercase=True, include_lowercase=True, 
                      include_digits=True, include_symbols=True, exclude_similar=False):
    """
    Generates a secure random password based on user specifications.
    """
    uppercase_chars = string.ascii_uppercase
    lowercase_chars = string.ascii_lowercase
    digit_chars = string.digits
    symbol_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if exclude_similar:
        similar_chars = "iI1lLo0O"
        uppercase_chars = ''.join(c for c in uppercase_chars if c not in similar_chars)
        lowercase_chars = ''.join(c for c in lowercase_chars if c not in similar_chars)
        digit_chars = ''.join(c for c in digit_chars if c not in similar_chars)
        symbol_chars = ''.join(c for c in symbol_chars if c not in similar_chars)

    character_pool = ""
    guaranteed_chars = []

    if include_uppercase:
        character_pool += uppercase_chars
        guaranteed_chars.append(random.choice(uppercase_chars))
    if include_lowercase:
        character_pool += lowercase_chars
        guaranteed_chars.append(random.choice(lowercase_chars))
    if include_digits:
        character_pool += digit_chars
        guaranteed_chars.append(random.choice(digit_chars))
    if include_symbols:
        character_pool += symbol_chars
        guaranteed_chars.append(random.choice(symbol_chars))

    if not character_pool:
        raise ValueError("At least one character type must be selected!")

    if length < len(guaranteed_chars):
        length = len(guaranteed_chars)

    # Fill remaining password length from character pool
    remaining_length = length - len(guaranteed_chars)
    remaining_chars = [random.choice(character_pool) for _ in range(remaining_length)]

    # Combine guaranteed characters and remaining characters, then shuffle
    password_list = guaranteed_chars + remaining_chars
    random.shuffle(password_list)

    return "".join(password_list)


def evaluate_strength(password):
    """
    Evaluates the strength of a password based on character entropy and length.
    """
    pool_size = 0
    if any(c in string.ascii_lowercase for c in password):
        pool_size += 26
    if any(c in string.ascii_uppercase for c in password):
        pool_size += 26
    if any(c in string.digits for c in password):
        pool_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        pool_size += 32

    if pool_size == 0 or len(password) == 0:
        return 0, "Empty / Invalid"

    entropy = len(password) * math.log2(pool_size)

    if entropy < 36:
        rating = "Weak (Low Entropy)"
    elif entropy < 60:
        rating = "Moderate"
    elif entropy < 80:
        rating = "Strong"
    else:
        rating = "Very Strong"

    return round(entropy, 2), rating


def main():
    print("==========================================")
    print("        Random Password Generator         ")
    print("==========================================")

    while True:
        print("\nMenu:")
        print("1. Generate Password")
        print("2. Generate Multiple Passwords")
        print("3. Check Password Strength")
        print("4. Exit")

        choice = input("Select an option (1-4): ").strip()

        if choice == '1':
            try:
                length = int(input("Enter password length (default 16): ") or "16")
                inc_upper = input("Include uppercase letters? (y/n, default y): ").strip().lower() != 'n'
                inc_lower = input("Include lowercase letters? (y/n, default y): ").strip().lower() != 'n'
                inc_digits = input("Include numbers? (y/n, default y): ").strip().lower() != 'n'
                inc_symbols = input("Include special symbols? (y/n, default y): ").strip().lower() != 'n'
                exc_similar = input("Exclude ambiguous characters (i, I, 1, l, L, o, 0, O)? (y/n, default n): ").strip().lower() == 'y'

                password = generate_password(
                    length=length,
                    include_uppercase=inc_upper,
                    include_lowercase=inc_lower,
                    include_digits=inc_digits,
                    include_symbols=inc_symbols,
                    exclude_similar=exc_similar
                )
                entropy, rating = evaluate_strength(password)

                print("\n------------------------------------------")
                print(f"Generated Password : {password}")
                print(f"Strength Rating    : {rating} (Entropy: {entropy} bits)")
                print("------------------------------------------")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '2':
            try:
                count = int(input("How many passwords to generate? ") or "5")
                length = int(input("Password length (default 12): ") or "12")
                print("\nGenerated Passwords:")
                print("------------------------------------------")
                for i in range(1, count + 1):
                    pwd = generate_password(length=length)
                    _, rating = evaluate_strength(pwd)
                    print(f"{i}. {pwd} [{rating}]")
                print("------------------------------------------")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '3':
            user_pwd = input("Enter password to test: ")
            entropy, rating = evaluate_strength(user_pwd)
            print("\n------------------------------------------")
            print(f"Password Strength : {rating}")
            print(f"Entropy Rating   : {entropy} bits")
            print("------------------------------------------")

        elif choice == '4':
            print("Goodbye! Stay secure.")
            break
        else:
            print("Invalid option! Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
