#!/usr/bin/env python
# -*- coding: utf-8 -*-


import rospy
import sys
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import math
from gazebo_msgs.msg import ModelState
from sensor_msgs.msg import LaserScan


class PID_Controller:
    def __init__(self,kp,ki,kd,output_min,output_max):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error = 0
        self.last_error = 0
        self.error_sum = 0
        self.error_diff = 0
        self.output_min = output_min
        self.output_max = output_max
        self.output = 0

    def constrain(self, output):
        if output > self.output_max:
            output = self.output_max
        elif output < self.output_min:
            output = self.output_min
        else:
            output = output
        return output

    def get_output(self, error):
        self.error = error
        self.error_sum += self.error
        self.error_diff = self.error - self.last_error
        self.last_error = self.error
        self.output = self.kp * self.error + self.kd * self.error_diff + self.ki * self.error_sum
        self.output = self.constrain(self.output)
        return self.output


class estimation:
    def __init__(self, data, counts):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.data = data
        self.count = counts
        self.pub = rospy.Publisher('/robot/control', Twist, queue_size = 10)
        self.sub = rospy.Subscriber('/robot/esti_model_state', ModelState, self.callback_state)
    
    def callback_state(self, state):
        current_time = rospy.get_time()
        self.vx = state.twist.linear.x
        self.x = state.pose.position.x
        self.vy = state.twist.linear.y
        self.y = state.pose.position.y
    
    def track_trajectory(self):
        rate = rospy.Rate(10)
        threshold = 0.001
        x_controller = PID_Controller(1.3, 0, 0.1, -0.6, 0.6)
        y_controller = PID_Controller(1.3, 0, 0.1, -0.6, 0.6)
        vx_controller = PID_Controller(3, 0, 0.3, -1.8, 1.8)
        vy_controller = PID_Controller(3, 0, 0.3, -1.8, 1.8)
        target_index = 0
        while target_index < self.count:
            twist = Twist()
            while (self.data[target_index][0] - self.x) ** 2 + (self.data[target_index][1] - self.y) ** 2 > threshold:
                vx = x_controller.get_output(self.data[target_index][0] - self.x)
                vy = y_controller.get_output(self.data[target_index][1] - self.y)
                twist.linear.x = vx_controller.get_output(vx - self.vx)
                twist.angular.z = vy_controller.get_output(vy - self.vy)
                self.pub.publish(twist)         
            x_controller = PID_Controller(1.3, 0, 0.1, -0.6, 0.6)
            y_controller = PID_Controller(1.3, 0, 0.1, -0.6, 0.6)
            vx_controller = PID_Controller(3, 0, 0.3, -1.8, 1.8)
            vy_controller = PID_Controller(3, 0, 0.3, -1.8, 1.8)
            target_index = target_index + 1
            rate.sleep()
        sys.exit(0)


if __name__ == '__main__':
    try:
        rospy.init_node('talker',anonymous=True)
        trajectory_name = '/home/headless/catkin_ws/src/cylinder_robot/script/picachu.txt'
        with open(trajectory_name, 'r') as file:
            lines = file.readlines() 
        data = [[float(num_str) for num_str in item.split()] for item in lines]
        counts = len(lines)
        obs = estimation(data, counts)
        obs.track_trajectory()
    except rospy.ROSInterruptException:
        pass