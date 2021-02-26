# Introduction

This was a project in my master's degree at University of Washington. The objective was to automate the calibration process of an eye tracker (Tobii). Eye-trackers have their own calibration routine where humans are asked to gaze at certain points on the screen (see https://www.youtube.com/watch?v=Zms0YpbV_mg). The idea was to replace the human with artificial robotic eyes and fool the eye-tracker into thinking that it's working with a human. My contribution was to design a methodology so that the setup works with the eye-tracker.


# Setup
A Screen, The eye tracker (paired to the screen), a Camera (facing the screen), and a servo-controlled mechanism which mimicked human eyes and on which a laser and artificial robotic eyes could be mounted

![](images/setup.PNG)


# Procedure

By pointing the laser on the screen at regular intervals, pixel co-ordinates and its corresponding servo command angles were recorded and stored as a grid. Image processing algorithms were used to detect laser position on the screen. Once a map/grid was formed, regression methods were used to interpolate between the grid points and generate servo commands to point the laser at the desired point on the screen. The Camera was used for visual feedback of the laser position. Once calibrated, the laser was replaced by artificial robotic eyes to fool the eye tracker.


# Organization

main.py contains the main calibration routine  
control.py contains functions which mainly interface with the servo  
mapping.py contains functions which are related to generating pixel-servo map  
perception.py contains function used by the camera to detect laser, calibration points, screen warping, etc
