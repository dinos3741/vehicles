# defines the vehicle class
from PVector import *
from math import *
from random import *
from tkinter import *

class Vehicle:
    # Initialize the vehicle. max speed is the maximum speed the vehicle can move. Provide mass, color, size and
    # initial location:
    def __init__(self, canvas, width, height, max_speed, mass, image):
        self.canvas = canvas
        # the parameters of the environment: dimensions of the top window:
        self.width = width
        self.height = height
        # define the initial position, velocity and acceleration of the vehicle:
        self.position = PVector(self.width/2, self.height/2)
        self.velocity = PVector(0, 0)
        self.acceleration = PVector(0, 0)
        self.max_speed = max_speed
        self.mass = mass
        self.image = image

        # create the vehicle shape:
        #self.id = canvas.create_oval(self.position.x, self.position.y, self.position.x + self.size, self.position.y + self.size, fill=self.color)
        self.id = canvas.create_image(self.position.x, self.position.y, anchor=CENTER, image=self.image)

    # ------------------------------------------------------------------
    # the draw method updates the location based on the velocity by adding the two vectors, and moves the vehicle
    def draw(self):
        self.velocity.Add(self.acceleration)
        self.position.Add(self.velocity)

        # now we zero the acceleration at the end of each frame
        self.acceleration.Mult(0)

        # moves the shape with the specific id by the pixels specified:
        self.canvas.move(self.id, self.velocity.x, self.velocity.y)
        self.canvas.after(10, self.draw)  # redraw after 10 milliseconds

        # start wandering in the world:
        self.wandering()

        # check if vehicle hits a window edge:
        self.boundaries()
        self.bounce()

    # ------------------------------------------------------------------
    # apply a force to the vehicle:
    def apply_force(self, force):
        f = PVector(0, 0)
        force.Copy(f)  # copy force to temporary f
        f = force.Div(self.mass)
        self.acceleration.Add(f)

    # ------------------------------------------------------------------
    # methods to avoid the window boundaries: boundaries() and bounce()
    def boundaries(self):
        DISTANCE_FROM_BORDER = 100  # the distance from the borders where it starts to change direction

        desired = PVector(0, 0)  # initialize the desired velocity vector

        if self.velocity.x < 0 and self.position.x < DISTANCE_FROM_BORDER:  # approaching and close to left wall
            desired.x = self.max_speed; desired.y = self.velocity.y

        elif self.position.x > self.width - DISTANCE_FROM_BORDER:  # close to right wall
            desired.x = -self.max_speed; desired.y = self.velocity.y

        if self.position.y < DISTANCE_FROM_BORDER:  # close to ceiling
            desired.x = self.velocity.x; desired.y = self.max_speed

        elif self.position.y > self.height - DISTANCE_FROM_BORDER:  # close to floor
            desired.x = self.velocity.x; desired.y = -self.max_speed

        #  calculate the steering vector based on the desired:
        if desired.get_Magnitude() != 0:
            desired.Normalize()
            desired.Mult(self.max_speed)
            steer = desired.Sub(self.velocity)
            max_force = 10.0 / self.mass
            steer.Limit(max_force)
            self.apply_force(steer)

    # ------------------------------------------------------------------
    # a simple bounce off the edges method (velocity reversal)
    def bounce(self):
        if self.position.x > self.width or self.position.x < 0:
            self.velocity.x *= -1
        if self.position.y > self.height or self.position.y < 0:
            self.velocity.y *= -1

    # ------------------------------------------------------------------
    # Method to calculate and apply a steering force towards a target. It receives a target point and calculates
    # a steering force towards that target point
    def seek(self, target):
        CLOSE_ENOUGH = 130  # distance from target in order to detect arriving and stop

        # subtract the current location from the target location vector to find the desired direction vector:
        desired = target.Sub(self.position)  # desired vector = target position - current position

        dist = desired.get_Magnitude()  # this is how far the target is
        desired.Normalize()  # get the unit vector in the direction of the desired direction vector

        if dist < CLOSE_ENOUGH:  # if we arrive close to the target
            # limit with the max speed of the vehicle (if instead -max_speed, we have fleeing behaviour)
            desired.Mult(self.max_speed * dist / CLOSE_ENOUGH)
        else:
            desired.Mult(self.max_speed)

        # Subtract the desired from the current velocity to create the steering force vector:
        steer = desired.Sub(self.velocity)  # steer = desired - current velocity

        # finally limit the steering force depending on the vehicle mass:
        max_force = 10.0/self.mass  # maximum force is inversely proportional to the vehicle mass
        steer.Limit(max_force)

        # finally we apply the steering force:
        self.apply_force(steer)

    # ------------------------------------------------------------------
    # method to create a wandering path for the vehicle. Result is to calculate a target vector
    def wandering(self):
        wanderR = 100  # Radius for our "wander circle"
        wander_theta = 0  # angle of circle
        wanderD = 200  # Distance from current location to the center of the "wander circle"
        change = pi  # we randomly chose an angle from -π to π
        wander_theta = random() * 2.0 * change - change   # Randomly change wander theta from -change to change

        # Now we have to calculate the new location to steer towards on the wander circle:
        circleloc = PVector(0, 0)  # initialize circleloc: this is the center of the circle
        self.velocity.Copy(circleloc)  # copy velocity to circleloc
        circleloc.Normalize()  # unit vector in direction of current velocity
        circleloc.Mult(wanderD)  # Multiply by distance
        circleloc.Add(self.position)  # now circleloc is the center of the circle, in the perimeter of which we move next
        heading = self.velocity.heading2D()  # We need to know the heading to offset wander_theta
        circleOffSet = PVector(wanderR * cos(wander_theta + heading), wanderR * sin(wander_theta + heading))
        circleloc.Add(circleOffSet)  # this is the target to feed the seek method
        # and now seek the new target:
        self.seek(circleloc)

    # ------------------------------------------------------------------
    # when wasp comes closer than 200 pixels, creates an avoiding force to get away from it
    def avoid_wasp(self, wasp):
        SAFE_DISTANCE = 200  # how close to the wasp before activating fleeing
        distance = self.position.distance(wasp.position)  # calculate the distance between him and the wasp
        if distance < SAFE_DISTANCE:
            # create a vector to point away from the wasp:
            diff = PVector(0, 0)
            diff = self.position.Sub(wasp.position)
            diff.Normalize()
            diff.Mult(self.max_speed)

            # Subtract the desired from the current vectors to create the steering force vector:
            steer = diff.Sub(self.velocity)

            # finally limit the steering force depending on the vehicle mass:
            max_force = 10.0 / self.mass  # maximum force is inversely proportional to the vehicle mass
            steer.Limit(max_force)
            # and now apply the steering force:
            self.apply_force(steer)

    # ------------------------------------------------------------------
    def separate(self, batterflies):
        desired_separation = 50  # how close to the other vehicles before activating fleeing
        for i in batterflies:
            # calculate the distance between this vehicle and all other vehicles:
            dist = self.position.distance(batterflies[i].position)
            if dist > 0 and dist < desired_separation:
                # execute code to deal with fleeing from that vehicle
                pass