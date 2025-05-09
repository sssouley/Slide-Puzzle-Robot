# Slide-Puzzle-Robot
ME134 Final project

Link

1. Download full project as a folder
2. Make and run a virtual environment:

On macOS/Linux

python3 -m venv venv

source venv/bin/activate

On Windows

python -m venv venv

venv\Scripts\activate

Link to demonstration video:
https://youtube.com/shorts/AeRlkZi26ls?si=vw8UeUBsXHKFo4c7


# Instructions On Running the Slide Puzzle project

1. Retrieve 3 robots, and install the entire Working Code Robots folder to each robot
2. You will probably need to run a virtual environment due to all the libraries
3. Run a ROBOTXWORKING.py to each robot. i.e. robot 1 gets ROBOT1WORKING, robot 2 gets ROBOT2WORKING, etc.
4. When a robot says that it is connected and shows the mqtt server number, remove robot from computer
5. Repeat for each robot
6. Close that folder on computer, and open the folder for the eye in the sky camera
7. Connect camera to laptop with the serial connection, make sure the serial connection number in the main2edited script is correct.
8. Place robots with correct april tags on top in the desired starting board position
9. Make sure camera is on Tag Recognition mode, and that it can see every april tag
10. Make sure mqtt server is on
11. Run main2edited.py script, and watch the robots move!
