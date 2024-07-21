# INSTRUCTIONS FOR MOUSEPAD FRICTION TESTING:
# ENTER "INPUTS", LOWER MOUSE DPI, THEN RUN CODE, FLICK YOUR MOUSE THEN LET GO OF MOUSE SO IT IS FREE MOVING
# WHEN MOUSE STOPS, THEN REPEAT IN THE OPPOSITE DIRECTION, KEEP DOING THIS THROUGHOUT THE TOTAL RUN TIME
# TRY TO AVOID THE CORNERS OF THE MONITOR CAUSE CALCULATIONS MAY GET MESSED UP A BIT
# WHEN TESTING IS COMPLETE, CODE WILL EXTRACT THE NEGATIVE ACCELERATION PERIODS (WHEN YOUR HAND LEAVES YOUR MOUSE)
# BASED ON THESE NEGATIVE ACCELERATION PERIODS, CODE WILL CALCULATE AVERAGE DYNAMIC FRICTION
# GRAPHS OF RESULTS WILL APPEAR IN THE SAME FOLDER CODE IS RAN FROM

# IMPORTS
import numpy as np
import pyautogui
import datetime
import csv
import matplotlib.pyplot as plt

# INPUTS
Test_Name = 'Mousepad friction test 1'
Mouse_DPI = 100  # Mouse DPI
Total_Run_Time = 25  # How Many Seconds Code Runs For
X_Resolution = 1920  # Monitor Pixels in the X
Y_Resolution = 1080  # Monitor Pixels in the Y
Time_Step = 0.01  # SAMPLE RATE

# RESULTS VISUALIZATION
Friction_Plot = "Y"  # IF YOU WANT THE COEFFICIENT OF FRICTION PLOT = "Y". IF YOU ARE NOT TESTING THIS TURN IT OFF
DVA_Plots = "Y"  # IF YOU WANT MOUSE DISTANCE VELOCITY AND ACCELERATION PLOT = "Y"
CSV_Results = "N"  # IF YOU WANT CSV RESULTS = "Y"
Position_Plot = "N"  # IF YOU WANT MOUSE POSITION PLOT = "Y"

# STORAGE LISTS DEFINED
T, X, Y, D, P, kF, Px, Py, Ax, Ay = [], [], [], [0], [], [], [], [], [], []

# INITIALIZE TIME PARAMETERS
TimeStart = datetime.datetime.now()
Current_Run_Time = datetime.datetime.now() - TimeStart
Sample_Time = Current_Run_Time

# ITERATE THOUGH TIME
while Current_Run_Time.total_seconds() <= Total_Run_Time:
    Current_Run_Time = datetime.datetime.now() - TimeStart

    # IF CURRENT TIME IS GREATER THAN Sample Time + Time Step, GET MOUSE POSITION AND APPEND DATA TO T X AND Y LISTS
    if Sample_Time.total_seconds() + Time_Step <= Current_Run_Time.total_seconds():
        Position = pyautogui.position()
        Sample_Time = datetime.datetime.now() - TimeStart
        T.append(Sample_Time.total_seconds())
        X.append(Position[0]/ Mouse_DPI)
        Y.append(Y_Resolution / Mouse_DPI - Position[1] / Mouse_DPI)

# CALCULATE TOTAL DISTANCE TRAVELED
for i in range(1, len(T)):
    del_D = ((X[i] - X[i - 1]) ** 2 + (Y[i] - Y[i - 1]) ** 2) ** 0.5
    D.append(del_D + D[i - 1])

# VELOCITY AND ACCELERATION CALCULATIONS
V = np.gradient(D, T)
A = np.gradient(V, T)

# ITERATE THROUGH ACCELERATION DATA TO EXTRACT RELEVANT DECELERATION INTERVALS "Trials"
Trial_Point = 0
Trial_Number = 0
ii = 0
for i in range(5, len(T) - 2):
    Individual_Trial_Sum = 0
    Individual_Trial_Point = 0

    # SKIP OPERATION IF DECELERATION INTERVAL WAS LOOKED AT ALREADY
    if i <= ii:
        continue

    # IF SMOOTHED ACCELERATION IS NEGATIVE AND SUBSTANTIAL VELOCITY AND MOUSE IS NOT IN CORNERS, EXTRACT DECELERATION
    if A[i] < 0 and A[i - 1] < 0 and A[i - 2] < 0 and A[i - 3] < 0 and A[i - 4] < 0 and A[i - 5] < 0 and \
            V[i] > 5 and V[i + 1] > 5 and \
            X[i + 2] <= X_Resolution / Mouse_DPI - 0.2 and Y[i + 2] <= Y_Resolution / Mouse_DPI - 0.2 and X[i + 2] >= 0.2 and Y[i + 2] >= 0.2:

        # PULL ALL DECELERATION DATA FOR INTERVAL
        Trial_Number += 1
        for ii in range(i, len(T) - 2):

            # GET POINT AND DYNAMIC FRICTION AT POINT
            P.append(Trial_Point)
            kF.append(A[ii] / -386.1)
            Individual_Trial_Sum += (A[ii] / -386.1)

            # GET LIST OF RELEVANT ACCELERATION POINTS SO WE CAN GRAPH THEM
            Ax.append(T[ii])
            Ay.append(A[ii])

            Trial_Point += 1
            Individual_Trial_Point += 1

            # IF VELOCITY IS SMALL (MEANING NEARING END OF DECELERATION) BREAK OR IF MOUSE IS NEAR CORNERS BREAK
            if V[ii + 1] <= 2 or X[ii + 2] >= X_Resolution / Mouse_DPI - 0.2 or Y[ii + 2] >= Y_Resolution / Mouse_DPI - 0.2 or X[ii + 2] <= 0.2 or Y[ii + 2] <= 0.2:
                break

        # INDIVIDUAL TRIAL AVERAGE DYNAMIC FRICTION
        Px.append(Trial_Point - 1)
        Py.append(round(Individual_Trial_Sum / Individual_Trial_Point, 4))
        print('Average Trial ' + str(Trial_Number) + ' Dynamic Friction is: ' + str(round(Individual_Trial_Sum / Individual_Trial_Point, 4)) + '. Over ' + str(Individual_Trial_Point) + ' Points.')

# TOTAL AVERAGE DYNAMIC FRICTION, IF NO DECELERATIONS CODE SKIPS THIS
try:
    kF_Ave = [round((sum(kF) / len(kF)), 4)] * len(kF)
    print('Average Dynamic Friction is: ' + str(kF_Ave[0]))
except:
    kF_Ave = [0] * len(kF)

# MOUSE POSITION PLOT
if Position_Plot == "Y":
    plt.figure(1)
    plt.plot(X, Y, color='black')
    plt.title(Test_Name + 'Mouse Position')
    plt.xlim(0, None)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('X Position (in)')
    plt.ylabel('Y Position (in)')
    plt.savefig(Test_Name + "Mouse Position.png")

# MOUSE DYNAMIC FRICTION PLOT
if Friction_Plot == "Y":
    plt.figure(2)
    plt.figure(figsize=(12, 5))
    plt.plot(P, kF, color='black', linestyle='--', linewidth=1, marker='o', label='Raw Data')
    plt.plot(P, kF_Ave, color='red', linestyle='--', label='Average = ' + str(kF_Ave[0]))
    plt.plot(Px, Py, color='blue', linestyle='', marker='*', label='End of Trial Average')
    plt.legend()
    plt.title(Test_Name + ' MousePad Dynamic Friction')
    plt.xlim(0, len(P)-1)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Point (#)')
    plt.ylabel('Dynamic Friction')
    plt.savefig(Test_Name + " MousePad Dynamic Friction.png")

if DVA_Plots == "Y":
    # MOUSE DISTANCE PLOT
    plt.figure(3)
    plt.figure(figsize=(8, 15))
    plt.subplot(3, 1, 1)
    plt.plot(T, D, color='red')
    plt.title(Test_Name + ' Mouse Distance vs Time')
    plt.xlim(0, Total_Run_Time)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Distance (in)')

    # MOUSE VELOCITY PLOT
    plt.subplot(3, 1, 2)
    plt.plot(T, V, color='red', linewidth=1)
    plt.title(Test_Name + ' Mouse Velocity vs Time')
    plt.xlim(0, Total_Run_Time)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (in/s)')

    # MOUSE ACCELERATION PLOT
    plt.subplot(3, 1, 3)
    plt.plot(T, A, color='red', linewidth=1)
    plt.plot(Ax, Ay, color='blue', linewidth=1, linestyle='', marker='o', markersize=2)
    plt.title(Test_Name + ' Mouse Acceleration vs Time')
    plt.xlabel('Time (s)')
    plt.xlim(0, Total_Run_Time)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.ylabel('Acceleration (in/s^2)')
    plt.savefig(Test_Name + " Mouse Plotting.png")

# CSV DATA WRITING
if CSV_Results == "Y":
    with open(Test_Name + ' MousePosition.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["T (sec)", "X (in)", "Y (in)", "D (in)", "V (in/s)", "A (in/s^2)"])
        for i in range(0, len(T)):
            csvwriter.writerow([T[i], X[i], Y[i], D[i], V[i], A[i]])
