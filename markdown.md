# 3x3 Slide Puzzle with XRP Robots

This project involves using three XRP robots to autonomously solve a 3x3 slide puzzle using MQTT communication and a HuskyLens camera. The robots are equipped with April tags and images for position tracking. The HuskyLens camera recognizes the puzzle’s initial state and tracks the positions of the robots as they solve the puzzle. The project demonstrates the application of robotics, image processing, and real-time communication technologies to autonomously solve a traditional puzzle, showcasing collaborative robotics in problem-solving tasks.


## Project Overview

### System Design

The project relies on three main components:

- **XRP Robots**: These robots are the primary agents solving the puzzle. Each robot is equipped with an April tag and image, which is used for position tracking.
  
- **HuskyLens Camera**: The camera is responsible for analyzing the puzzle's initial state and tracking robot movements. It communicates the necessary movement data to the robots via MQTT.

- **MQTT Communication**: This protocol is used to send and receive data between the robots and the HuskyLens camera, enabling the puzzle-solving process.

## Robot Actions and Puzzle Solving

### Initial Setup

The robot starts facing to the right, an orientation known as ‘e’ or east. The robot subscribes to a specific MQTT channel (e.g., `SlidePuzzle/send/1`) to receive its movement commands. 

### Movement and Positioning

1. **Orientation Tracking**: The robot's orientation is key to ensuring the final puzzle image looks correct. If the robot's orientation is not facing east, it will turn to do so.

2. **Movement Command Parsing**: The robot listens for `dx` and `dy` values from the HuskyLens camera. These values determine the robot's movement direction. If the absolute value of `dx` is greater than `dy`, the robot will move along the x-axis; otherwise, it moves along the y-axis.

3. **Turn and Move**: Once the robot receives movement commands, it calculates if it needs to turn. If the robot's orientation isn’t facing east, it will adjust its position accordingly. The robot moves forward until it receives a `dx` or `dy` value that is below a threshold (40), at which point it stops.

4. **Collision Avoidance**: The robots avoid collisions by ensuring they are sufficiently spaced apart during the puzzle-solving process.
   
### Challenges

- **Motor Drift**: One of the challenges faced during the project was motor drift, as not all robots were able to move in a perfectly straight line. This caused slight inaccuracies in positioning, which had to be managed during the puzzle-solving process.


## Future Work and Improvements

While the demo successfully solved the puzzle as expected, there are areas for future improvement. One key limitation was the HuskyLens camera's inability to recognize the orientation of the April tags, which affected the robot's autonomy. In future versions, a more advanced camera capable of recognizing both the position and orientation of the tags would allow for more complex, autonomous code.

Another potential improvement is expanding the puzzle size from 3x3 to a 9x9 puzzle. While the current code could generate the correct moveset for a larger puzzle, the inability to track orientation accurately limits the robots' ability to solve larger puzzles autonomously.


## Project Structure
/SlidePuzzle
/robot_controller.py - Handles movement and communication with the robots.
/husky_lens.py - Integrates the HuskyLens camera for image processing.
/mqtt_server.py - Manages MQTT communication between robots and the camera.
/start_puzzle.py - Main script that starts the puzzle-solving process.
/requirements.txt - Lists dependencies for running the project.

## Conclusion

This project provided valuable experience in robotics, image processing, and communication protocols. Despite some challenges, such as the limitations of the HuskyLens camera, the project successfully demonstrated the potential of collaborative robotics for solving complex problems. Moving forward, incorporating better camera technology and exploring larger puzzle configurations could take the project to the next level, enhancing both the autonomy and scalability of the system.

