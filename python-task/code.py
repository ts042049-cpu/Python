# First Non-Repeating Character

text = input("Enter a string: ")

frequency = {}

# Count frequency of every character
for char in text:
    if char in frequency:
        frequency[char] += 1
    else:
        frequency[char] = 1

# Find the first character with frequency 1
found = False

for char in text:
    if frequency[char] == 1:
        print("First non-repeating character:", char)
        found = True
        break

if not found:
    print("No non-repeating character found.")