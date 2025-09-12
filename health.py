Number_of_cups_of_water_drunk = int(input("How Many Cup(s) Of Water , Have You Drunk?:"))
#sleep deficiency
Time_active = int(input("How Many Hours Did You Spend working?:"))
Hours_slept= int(input("How Many Hours Did You Sleep?:"))

if Hours_slept <Number_of_cups_of_water_drunk :
    print("Deficiency")
elif Number_of_cups_of_water_drunk>Time_active :
    print("Excess")
else:
    print("Normal")
