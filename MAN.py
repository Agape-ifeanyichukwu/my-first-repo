import csv

students = []

while True:
    print("\n--- New Student Entry ---")

    name = input("Enter your name: ")
    age_entering = int(input("Enter your age: "))

    if age_entering >= 20:
        print("ADMITTANCE REJECTED. PLEASE \nFOLLOW THE STEPS TO RESCHEDULE ADMITTANCE.")
    else:
        print("CONGRATULATIONS! WE LOOK FORWARD TO WALKING WITH YOU.")

    score_entered = float(input("Enter your score: "))

    # Performance evaluation
    if score_entered > 90:
        performance = "EXCELLENT"
    elif 60 <= score_entered <= 89.9:
        performance = "PASS"
    else:
        performance = "FAIL"

    print(f"Performance: {performance}")

    # Enrollment eligibility
    eligible = score_entered >= 60
    print("Enrollment Eligibility:", eligible)

    # Store student data
    student_data = {
        "name": name,
        "age": age_entering,
        "score": score_entered,
        "performance": performance,
        "eligible": eligible
    }

    students.append(student_data)

    # Ask if user wants to continue
    continue_input = input("Do you want to enter another student? (yes/no): ").lower()
    if continue_input != "yes":
        break

# After loop, print all student summaries
print("\n=== Summary of All Students Entered ===")
for s in students:
    print(f"{s['name']} (Age {s['age']}) - Score: {s['score']}, Performance: {s['performance']}, Eligible: {s['eligible']}")

# Save to CSV file
with open("students.csv", "w", newline="") as csvfile:
    fieldnames = ["name", "age", "score", "performance", "eligible"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(students)

print("\nAll student data has been saved to 'students.csv'.")
