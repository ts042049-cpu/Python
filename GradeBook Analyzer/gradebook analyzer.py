# Name: Tushar Saini

# Title: GradeBook Analyzer (Simple Version)

def give_grade(score):
    """Return grade based on score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def main():
    print("=== GradeBook Analyzer ===")
    marks = {}

    # Enter marks for 3 students
    for i in range(3):
        name = input(f"\nEnter student {i+1} name: ")
        while True:
            try:
                mark = int(input(f"Enter marks for {name} (0–100): "))
                if 0 <= mark <= 100:
                    marks[name] = mark
                    break
                else:
                    print("Marks must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number.")

    # Calculate grades
    grades = {name: give_grade(score) for name, score in marks.items()}

    # Show Report
    print("\n--- Report Card ---")
    print(f"{'Name':<15}{'Marks':<10}{'Grade'}")
    print("----------------------------")
    for name in marks:
        print(f"{name:<15}{marks[name]:<10}{grades[name]}")

    # Stats
    scores = list(marks.values())
    avg = sum(scores) / len(scores)
    highest = max(scores)
    lowest = min(scores)

    print("\n--- Class Stats ---")
    print("Average Marks :", round(avg, 2))
    print("Highest Marks :", highest)
    print("Lowest Marks  :", lowest)

    # Pass / Fail
    passed = [n for n, m in marks.items() if m >= 40]
    failed = [n for n, m in marks.items() if m < 40]

    print("\nPassed Students :", ", ".join(passed) if passed else "None")
    print("Failed Students :", ", ".join(failed) if failed else "None")

    print("\n--- End of Report ---")

if __name__ == "__main__":
    main()