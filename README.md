# Slide-Puzzle-Robot
ME134 Final project

1. Download full project as a folder
2. Make and run a virtual environment:

On macOS/Linux

python3 -m venv venv

source venv/bin/activate

On Windows

python -m venv venv

venv\Scripts\activate



# Running the Slide Puzzle project

1. Retrieve 3 robots, and install the entire Working Code Robots folder to each robot
2. Run a ROBOTXWORKING.py to each robot. i.e. robot 1 gets ROBOT1WORKING, robot 2 gets ROBOT2WORKING, etc.
3. When a robot says that it is connected and shows the mqtt server number, remove robot from computer
4. Repeat for each robot
5. Close that folder on computer, and open the folder for the eye in the sky camera
6. Connect camera to laptop with the serial connection, make sure the serial connection number in the main2edited script is correct.
7. Place robots with correct april tags on top in the desired starting board position
8. Make sure camera is on Tag Recognition mode, and that it can see every april tag
9. Make sure mqtt server is on
10. Run main2edited.py script, and watch the robots move!
