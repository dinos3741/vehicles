# defines the vehicle class
from PVector import *
from math import *
from random import *
from tkinter import *
from sklearn.cluster import KMeans
import numpy as np

class Vehicle:
    # Initialize the vehicle. max speed is the maximum speed the vehicle can move. Provide mass, color, size and
    # initial location
    def __init__(self, canvas, width, height, max_speed, mass, image):
        self.canvas = canvas
        # the parameters of the environment: dimensions of the top window:
        self.width = width
        self.height = height
        # define the initial position, velocity and acceleration of the vehicle:
        self.position = PVector(randrange(0, self.width), randrange(0, self.height))  # random starting position
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

        # check if vehicle hits a window edge:
        #self.boundaries()
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
        point = PVector(0, 0)

        if self.position.x < DISTANCE_FROM_BORDER:  # close to left wall
            point = PVector(0, self.position.y)

        elif self.position.x > self.width - DISTANCE_FROM_BORDER:  # close to right wall
            point = PVector(self.width, self.position.y)

        elif self.position.y < DISTANCE_FROM_BORDER:  # close to ceiling
            point = PVector(self.position.x, 0)

        elif self.position.y > self.height - DISTANCE_FROM_BORDER:  # close to floor
            point = PVector(self.position.x, self.height)

        else:
            point = PVector(self.width, self.height/2)

        self.avoid_point(point, DISTANCE_FROM_BORDER)

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
    # avoid a PVector point
    def avoid_point(self, point, safe_distance):
        # safe_distance represents how close to the point before activating fleeing
        distance = self.position.distance(point)  # calculate the distance between vehicle and the point

        if distance < safe_distance:  # point is getting too close
            # create a vector to point away from the point:
            diff = self.position.Sub(point)
            diff.Normalize()
            diff.Mult(self.max_speed)

            # Subtract the desired from the current vectors to create the steering force vector:
            steer = diff.Sub(self.velocity)

            # Limit the steering force depending on the vehicle mass:
            max_force = 10 / self.mass  # maximum force is inversely proportional to the vehicle mass
            steer.Limit(max_force)
            # Finally apply the steering force:
            self.apply_force(steer)

    # ------------------------------------------------------------------
    # method to create a wandering path for the vehicle. Result is to calculate a target vector
    def wandering(self, radius, distance):
        wanderR = radius  # Radius for our "wander circle"
        wander_theta = 0  # angle of circle
        wanderD = distance  # Distance from current location to the center of the "wander circle"
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
    def separate(self, butterflies):
        SAFE_DISTANCE = 70  # minimum distance before activating fleeing
        for butterfly in butterflies:
            # calculate the distance between this vehicle and all other vehicles:
            dist = self.position.distance(butterfly.position)
            if dist > 0 and dist < SAFE_DISTANCE:
                self.avoid_point(butterfly.position, SAFE_DISTANCE)  # avoid this vehicle

    # ------------------------------------------------------------------
    def chase_butterflies(self, butterflies):
        distance = []  # create a list of distances from wasp to all butterflies
        for butterfly in butterflies:
            dist = self.position.distance(butterfly.position)
            distance.append(dist)

        # find the nearest butterfly: sort the distance list. sorted gives a new sorted list, enumerate gives
        # a tuple with first item the index and second the value, we sort by the value, and create a new list
        # with the first, ie the index. Then we chose the first item, so the minimum.
        if len(distance) > 0:  # seeks butterflies while they exist:
            min_index = [i[0] for i in sorted(enumerate(distance), key=lambda x: x[1])][0]
            self.seek(butterflies[min_index].position)

    # ------------------------------------------------------------------
    # each butterfly tries to classify wasp behaviour based on ts speed and if it killed another. If wasp is
    # classified as enemy, butterfly runs faster
    def recognize_enemy(self, butterflies, wasp):
    # if length of butterflies is getting smaller, this indicates that wasp is enemy. An unsupervised learning
    # algorithm (k-means) with inputs speed and length of butterlfy list, should classify the output as enemy or friend.
    # if butterfly detects that wasp is enemy, it must raise a flag to increase the speed
        pass

    # ------------------------------------------------------------------
    # I want to detect mouse movements and classify them as friendly or violent. A k-means algorithm was used but
    # was very slow because I needed to run the model at each data frame.
    # I need to get and store mouse movements and speed for a specific period of time, and classify it, and do that
    # repeatedly. Its easier with a perceptron model of two inputs and one output to raise the flag of attack.

    def mouse_attack(self, data_frame):
        global is_aggressor  # aggression flag
        AGGRESSIVE_THRESHOLD = 600

        # Declaring k-means unsupervised Model with one cluster
        #model = KMeans(n_clusters=1)
        # Fitting Model
        #model.fit(data_frame)
        #level = sqrt(model.cluster_centers_[0][0] ** 2 + model.cluster_centers_[0][1] **2)

        # simpler way: if the average of all magnitudes of samples within the dataframe is larger than 500,
        # the behaviour is classified as aggressive and flag is raised
        sum_list = []
        for i in range(data_frame.shape[0]):  # for each sample in the data frame (row in the np array):
            sum_list.append(sqrt(data_frame[i, 0] ** 2 + data_frame[i, 1] ** 2)) # magnitude of the two elements

        average = sum(sum_list)/len(sum_list)
        sum_list.clear()

        if average > AGGRESSIVE_THRESHOLD:  # aggressive behaviour
            is_aggressor = True
        else:
            is_aggressor = False

        return is_aggressor
