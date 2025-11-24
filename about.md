So basically this is a WI-FI speed tester.
I don't know how long it will take but i will take you through this process.


STEP 1:

[//]: # (DOWNLOAD THIS MODULES)
# For the core speed test functionality
pip install speedtest-cli

# For the modern GUI
pip install customtkinter

STEP 2:

We need the logic
+the speed test takes time ---------> so we will use threading to avoid freezing the GUI.
   also we will Write a Python function that uses the speedtest-cli module to calculate :
=>the download speed, 
=>upload speed, and 
=>ping time.

i may face some challenges:
   =>function may take time to execute
    =>GUI may freeze during the speed test
    =>i will use threading to run the speed test in a separate thread.


STEP 3:
  THE UI:
+i will use customtkinter to create a modern GUI.

STEP 4:
Define tiers for speed results:
: => Slow: < 25 Mbps
: => Average: 25-100 Mbps
: => Fast: > 100 Mbps   

STEP 5:
Polishing and Testing: