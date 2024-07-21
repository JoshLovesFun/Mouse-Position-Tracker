# IMPORTS
import numpy as np
import pyautogui
import datetime
import csv
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# INPUTS
Run_Time = 25  # How Many Seconds Code Runs For
Time_Sample = 0.01  # How Many Samples per second
X_Resolution = 1920  # Monitor Pixels in the X
Y_Resolution = 1080  # Monitor Pixels in the Y
Mouse_DPI = 200   # Mouse DPI
Test_Name = 'Hyper X & Gwolves Dots'
Smooth_V = 21  # Increase sampling factor for smoother velocity curve
Smooth_A = 21  # Increase sampling factor for smoother acceleration curve

# MAIN STORAGE ARRAY HEADERS
MainArray = [["T (sec)", "X (in)", "Y (in)", "D (in)", "V (in/s)", "A (in/s^2)", "Vs (in/s)", "As (in/s^2)", "Avs (in/s^2)"]]
T = []
X = []
Y = []
D = []
Af = []
P = []
Fk = []
Pyend = []
Pxend = []

# ITERATE THROUGH EACH TIME INTERVAL
TimeStart = datetime.datetime.now()
TimeDelta = datetime.datetime.now()-TimeStart
TimeDeltaa = TimeDelta

# ITERATE THOUGH ALL TIME INTERVALS
while TimeDelta.total_seconds() < Run_Time:
    TimeDelta = datetime.datetime.now() - TimeStart

    # IF TIME IS GREATER THAN NEXT T STEP
    if TimeDeltaa.total_seconds() + Time_Sample <= TimeDelta.total_seconds():
        Position = pyautogui.position()
        TimeDeltaa = datetime.datetime.now() - TimeStart
        New_Row = [TimeDeltaa.total_seconds(), Position[0]/Mouse_DPI, Y_Resolution/Mouse_DPI - Position[1]/Mouse_DPI, 0, 0, 0, 0, 0, 0]
        MainArray.append(New_Row)

# CALCULATE TOTAL DISTANCE
for i in range(2, len(MainArray)):
    Del_D = (((float(MainArray[i][1]) - float(MainArray[i - 1][1])) ** 2 + (float(MainArray[i][2]) - float(MainArray[i - 1][2])) ** 2) ** 0.5)

    # TOTAL DISTANCE
    MainArray[i][3] = Del_D + float(MainArray[i - 1][3])

    # APPEND
    T.append(MainArray[i][0])
    X.append(MainArray[i][1])
    Y.append(MainArray[i][2])
    D.append(MainArray[i][3])

# GRADIENTS
V = np.gradient(D, T)
A = np.gradient(V, T)

# SMOOTHED VELOCITY
V_s = savgol_filter(V, Smooth_V, 3)

# ACCELERATION BASED ON SMOOTH VELOCITY
A_s = np.gradient(V_s, T)

# SMOOTHED ACCELERATION
A_vs = savgol_filter(A_s, Smooth_A, 3)

# PRINT DATA TO MAIN ARRAY
for i in range(2, len(MainArray)):
    MainArray[i][4] = V[i - 2]
    MainArray[i][5] = A[i - 2]
    MainArray[i][6] = V_s[i-2]
    MainArray[i][7] = A_s[i-2]
    MainArray[i][8] = A_vs[i-2]

# CSV DATA WRITING
with open(Test_Name + ' MousePosition.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    for row in MainArray:
        csvwriter.writerow(row)


Count = 0
Trial = 0
ii = 0
# ITERATE THROUGH MAIN ARRAY
for i in range(1, len(MainArray) - 12):
    Trial_T = 0
    P_in_T_Count = 0

    # SKIP OPERATION IF OPERATION WAS ALREADY DONE
    if i <= ii:
        continue

    # IF SMOOTHED ACCELERATION IS NEGATIVE AND MOTION IS TO THE LEFT AND SUBSTANTIAL VELOCITY NAD MOUSE IS NOT IN CORNERS
    if A_vs[i] < 0 and V[i] > 5 and V[i + 1] > 5 and X[i+2] <= X_Resolution/Mouse_DPI - 0.2 and Y[i+2] <= Y_Resolution/Mouse_DPI - 0.2 and X[i+2] >= 0.2 and Y[i+2] >= 0.2:
        Trial = Trial + 1

        # START INNER LOOP
        for ii in range(i, len(MainArray) - 3):
            P.append(Count)
            Fk.append(A[ii] / -386.1)
            Trial_T = Trial_T + (A[ii] / -386.1)
            Count = Count + 1
            P_in_T_Count = P_in_T_Count + 1

            # IF VELOCITY IS SMALL BREAK OR IF MOUSE IS NEAR CORNERS BREAK
            if V[ii + 1] <= 2 or X[ii+2] >= X_Resolution/Mouse_DPI - 0.2 or Y[ii+2] >= Y_Resolution/Mouse_DPI - 0.2 or X[ii+2] <= 0.2 or Y[ii+2] <= 0.2:
                break

        # INDIVIDUAL TRIAL RESULTS
        Pxend.append(Count-1)
        Pyend.append(round(Trial_T / P_in_T_Count, 4))
        print('Average Trial ' + str(Trial) + ' Dynamic Friction is: ' + str(round(Trial_T / P_in_T_Count, 4)) + '. Over ' + str(P_in_T_Count) + ' Points.' )

# SOME FINAL CALCS
Fka = round((sum(Fk) / len(Fk)), 4)
print('Average Dynamic Friction is: ' + str(Fka))
Fkaa = [Fka]*len(P)

# MOUSE POSITION PLOT
plt.figure(1)
plt.plot(X, Y, color='black')
plt.title('Mouse Position')
plt.xlim(0, None)
plt.ylim(0, None)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.xlabel('X Position (in)')
plt.ylabel('Y Position (in)')
# plt.savefig("Mouse Position.png")

# MOUSE DYNAMIC FRICTION PLOT
plt.figure(2)
plt.figure(figsize=(12, 5))
plt.plot(P, Fk, color='black', linestyle='--', linewidth=1, marker='o', label='Raw Data')
plt.plot(P, Fkaa, color='red', linestyle='--', label='Average = ' + str(Fka))
plt.plot(Pxend, Pyend, color='blue', linestyle='', marker='*', label='End of Trial Average')
plt.legend()
plt.title(Test_Name + ' MousePad Dynamic Friction')
plt.xlim(0, len(P)-1)
plt.ylim(0, None)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.xlabel('Point (#)')
plt.ylabel('Dynamic Friction')
plt.savefig(Test_Name + " MousePad Dynamic Friction.png")

# MOUSE DISTANCE PLOT
plt.figure(3)
plt.figure(figsize=(8, 15))
plt.subplot(3, 1, 1)
plt.plot(T, D, color='black')
plt.title(Test_Name + ' Mouse Distance vs Time')
plt.xlim(0, Run_Time)
plt.ylim(0, None)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.xlabel('Time (s)')
plt.ylabel('Distance (in)')

# MOUSE VELOCITY PLOT
plt.subplot(3, 1, 2)
plt.plot(T, V, color='black', linewidth=1, label='V')
plt.plot(T, V_s, color='red', linestyle='--', label='V Smooth')
plt.legend()
plt.title(Test_Name + ' Mouse Velocity vs Time')
plt.xlim(0, Run_Time)
plt.ylim(0, None)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (in/s)')

# Mouse Acceleration PLOT
plt.subplot(3, 1, 3)
plt.plot(T, A, color='black', linewidth=1, label='A')
plt.plot(T, A_s, color='red', linestyle='--', label='A Smooth')
plt.plot(T, A_vs, color='blue', linestyle='--', label='A Very Smooth')
plt.legend()
plt.title(Test_Name + ' Mouse Acceleration vs Time')
plt.xlabel('Time (s)')
plt.xlim(0, Run_Time)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.ylabel('Acceleration (in/s^2)')
plt.savefig(Test_Name + " Mouse Plotting.png")
