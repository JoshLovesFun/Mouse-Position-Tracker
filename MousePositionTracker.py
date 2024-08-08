# Instructions for Mousepad Friction Testing:

# Change the "Inputs" as needed, lower the mouse DPI, then run the code. Flick
# your mouse, then let go, so it is free-moving. When the mouse stops, repeat
# in the opposite direction. Continue this throughout the total run time.
# Avoid corners of the monitor as calculations may be affected. When testing is
# complete, the code will extract the negative acceleration periods (when your
# hand leaves the mouse) and calculate the average dynamic friction. Graphs of
# the results will appear in the same folder where the code is run from.

from numpy import gradient
from pyautogui import position
from datetime import datetime
import csv
import matplotlib.pyplot as plt

# Inputs
Test_Name = 'Mousepad friction test 1'
Mouse_DPI = 100  # Mouse DPI
Total_Run_Time = 5  # Duration of code execution in seconds
X_Resolution = 1920  # Monitor pixels in the X
Y_Resolution = 1200  # Monitor pixels in the Y
Time_Step = 0.01  # Sample rate

# Results visualization

# If you want the coefficient of friction plot, set to "Y".
# If not testing, turn it off.
Friction_Plot = "N"

# If you want mouse distance, velocity, and acceleration plots, set to "Y".
DVA_Plots = "Y"

# If you want CSV results, set to "Y".
CSV_Results = "Y"

# If you want the mouse position plot, set to "Y".
Position_Plot = "Y"

DECELERATION_INCHES_PER_S2 = -386.08858

# Storage lists defined
T, X, Y, D, P, kF, Px, Py, Ax, Ay = [], [], [], [0], [], [], [], [], [], []

# Initialize time parameters
TimeStart = datetime.now()
Current_Run_Time = datetime.now() - TimeStart
Sample_Time = Current_Run_Time

# Iterate through time
while Current_Run_Time.total_seconds() <= Total_Run_Time:
    Current_Run_Time = datetime.now() - TimeStart

    # If the current time is greater than sample time + time step,
    # get mouse position and append data to T, X, and Y lists.
    if (Sample_Time.total_seconds() + Time_Step
            <= Current_Run_Time.total_seconds()):
        Position = position()
        Sample_Time = datetime.now() - TimeStart
        T.append(Sample_Time.total_seconds())
        X.append(Position[0] / Mouse_DPI)
        Y.append(Y_Resolution / Mouse_DPI - Position[1] / Mouse_DPI)

# Calculate total distance traveled
for i in range(1, len(T)):
    del_D = ((X[i] - X[i - 1]) ** 2 + (Y[i] - Y[i - 1]) ** 2) ** 0.5
    D.append(del_D + D[i - 1])

# Velocity and acceleration calculations
V = gradient(D, T)
A = gradient(V, T)

# Iterate through acceleration data to extract relevant
# deceleration intervals "trials"
Trial_Point = 0
Trial_Number = 0
ii = 0
for i in range(5, len(T) - 2):
    Individual_Trial_Sum = 0
    Individual_Trial_Point = 0

    # Skip operation if deceleration interval was looked at already
    if i <= ii:
        continue

    # If smoothed acceleration is negative, and velocity is substantial, and
    # the mouse is not in corners, extract deceleration.
    if (A[i] < 0 and A[i - 1] < 0 and A[i - 2] < 0 and
            A[i - 3] < 0 and A[i - 4] < 0 and A[i - 5] < 0 and
            V[i] > 5 and V[i + 1] > 5 and
            X[i + 2] <= X_Resolution / Mouse_DPI - 0.2 and
            Y[i + 2] <= Y_Resolution / Mouse_DPI - 0.2 and
            X[i + 2] >= 0.2 and Y[i + 2] >= 0.2):

        # Pull all deceleration data for interval
        Trial_Number += 1
        for ii in range(i, len(T) - 2):

            # Get point and dynamic friction at point
            P.append(Trial_Point)
            kF.append(A[ii] / DECELERATION_INCHES_PER_S2)
            Individual_Trial_Sum += (A[ii] / DECELERATION_INCHES_PER_S2)

            # Get list of relevant acceleration points, so we can graph them
            Ax.append(T[ii])
            Ay.append(A[ii])

            Trial_Point += 1
            Individual_Trial_Point += 1

            # If velocity is small (meaning nearing the end of deceleration) or
            # if the mouse is near the corners, break.
            if (V[ii + 1] <= 2 or
                    X[ii + 2] >= X_Resolution / Mouse_DPI - 0.2 or
                    Y[ii + 2] >= Y_Resolution / Mouse_DPI - 0.2 or
                    X[ii + 2] <= 0.2 or
                    Y[ii + 2] <= 0.2):
                break

        # Individual trial average dynamic friction
        Px.append(Trial_Point - 1)
        Py.append(round(Individual_Trial_Sum / Individual_Trial_Point, 4))
        print('Average Trial ' + str(
            Trial_Number) + ' Dynamic Friction is: ' + str(
            round(Individual_Trial_Sum / Individual_Trial_Point,
                  4)) + '. Over ' + str(Individual_Trial_Point) + ' Points.')

# Total average dynamic friction; if no decelerations, code skips this
try:
    kF_Ave = [round((sum(kF) / len(kF)), 4)] * len(kF)
    print('Average Dynamic Friction is: ' + str(kF_Ave[0]))
except ZeroDivisionError:
    kF_Ave = [0] * len(kF)

# Mouse position plot
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

# Mouse dynamic friction plot
if Friction_Plot == "Y":
    plt.figure(2)
    plt.figure(figsize=(12, 5))
    plt.plot(P, kF, color='black', linestyle='--', linewidth=1, marker='o',
             label='Raw Data')
    plt.plot(P, kF_Ave, color='red', linestyle='--',
             label='Average = ' + str(kF_Ave[0]))
    plt.plot(Px, Py, color='blue', linestyle='', marker='*',
             label='End of Trial Average')
    plt.legend()
    plt.title(Test_Name + ' MousePad Dynamic Friction')
    plt.xlim(0, len(P) - 1)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Point (#)')
    plt.ylabel('Dynamic Friction')
    plt.savefig(Test_Name + " MousePad Dynamic Friction.png")

if DVA_Plots == "Y":
    # Mouse distance plot
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

    # Mouse velocity plot
    plt.subplot(3, 1, 2)
    plt.plot(T, V, color='red', linewidth=1)
    plt.title(Test_Name + ' Mouse Velocity vs Time')
    plt.xlim(0, Total_Run_Time)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (in/s)')

    # Mouse acceleration plot
    plt.subplot(3, 1, 3)
    plt.plot(T, A, color='red', linewidth=1)
    plt.plot(Ax, Ay, color='blue', linewidth=1, linestyle='', marker='o',
             markersize=2)
    plt.title(Test_Name + ' Mouse Acceleration vs Time')
    plt.xlabel('Time (s)')
    plt.xlim(0, Total_Run_Time)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.ylabel('Acceleration (in/s^2)')
    plt.savefig(Test_Name + " Mouse Plotting.png")

# CSV data writing
if CSV_Results == "Y":
    with open(Test_Name + ' MousePosition.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            ["T (sec)", "X (in)", "Y (in)", "D (in)", "V (in/s)",
             "A (in/s^2)"])
        for i in range(0, len(T)):
            csvwriter.writerow([T[i], X[i], Y[i], D[i], V[i], A[i]])
