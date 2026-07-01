#!/usr/bin/env python

import rospy
import rospkg
from scipy import linalg as lnr
from matplotlib import pyplot as plt
import numpy as np
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from gazebo_msgs.msg import ModelState
import os
import sys


class KalmanFilter(object):
    def __init__(self, mass, C, Sigma_w, Sigma_v, x_0, P_0):
        self.mass = mass
        self.C = C
        self.n = 4
        self.m = 2
        self.Sigma_w = Sigma_w
        self.Sigma_v = Sigma_v
        self.t = 0
        self.x = x_0
        self.P = P_0
        self.u = np.zeros([self.m, 1])

    def _discretization_Func(self, dt):
        Atilde = np.array([
            [1, 0,  0,  0],
            [dt,1,  0,  0],
            [0, 0,  1,  0],
            [0, 0,  dt, 1]
        ])
        Btilde = np.array([
            [dt/self.mass,      0],
            [dt*dt/2/self.mass, 0],
            [0,      dt/self.mass],
            [0, dt*dt/2/self.mass]
        ])
        q1 = self.Sigma_w[0,0]
        q2 = self.Sigma_w[1,1]
        q3 = self.Sigma_w[2,2]
        q4 = self.Sigma_w[3,3]
        Sigma_w_tilde = np.array([
            [dt*q1,         dt*dt/2*q1,                 0,          0],
            [dt*dt/2*q1,    (dt*q2)+(dt*dt*dt/3*q1),    0,          0],
            [0,             0,                          dt*q3,      dt*dt/2*q3],
            [0,             0,                          dt*dt/2*q3, (dt*q4)+(dt*dt*dt/3*q3)],
        ])
        return Atilde, Btilde, Sigma_w_tilde

    def _predict_Step(self, ctrl_time):
        dt = ctrl_time - self.t
        self.t = ctrl_time
        At, Bt, Sigma = self._discretization_Func(dt)
        self.x = np.dot(At, self.x) + np.dot(Bt, self.u)
        self.P = np.dot(np.dot(At, self.P), At.T) + Sigma

    def _correction_Step(self, y):
        correction_B = np.dot(
            np.dot(self.P, self.C.T), 
            np.linalg.inv(np.dot(np.dot(self.C, self.P), self.C.T) + self.Sigma_v)
            )
        self.x = self.x + np.dot(correction_B, y - np.dot(self.C, self.x))
        self.P = self.P - np.dot(np.dot(correction_B, self.C), self.P)

    def control_moment(self, u_new, time_now):
        self._predict_Step(time_now)
        self.u = u_new

    def observe_moment(self, y_new, time_now):
        self._predict_Step(time_now)
        self._correction_Step(y_new)

class Localization(object):
    def __init__(self):
        rospy.Subscriber('/robot/control', Twist, self.callback_control)
        rospy.Subscriber('/robot/observe', LaserScan, self.callback_observe)
        rospy.Subscriber('gazebo/set_model_state', ModelState, self.callback_state)
        self.pub = rospy.Publisher("/robot/esti_model_state", ModelState, queue_size=10)
        rospy.on_shutdown(self.visualization)

        self.kf = KalmanFilter(
            mass = 10, 
            C = np.array([
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ]),
            Sigma_w = np.eye(4)*0.00001,
            Sigma_v = np.array([[0.02**2, 0],[0, 0.02**2]]),
            x_0 = np.zeros([4,1]),
            P_0 = np.eye(4)/1000
            )

        self.x_esti_save = []
        self.x_esti_time = []
        self.x_true_save = []
        self.x_true_time = []
        self.p_obsv_save = []
        self.p_obsv_time = []

    def callback_control(self, twist):
        control_signal = np.array([
            [twist.linear.x], [twist.angular.z]
            ])
        current_time = rospy.get_time()
        self.kf.control_moment(control_signal, current_time)
        self.x_esti_save.append(self.kf.x)
        self.x_esti_time.append(current_time)

    def callback_observe(self, laserscan):
        y = np.array([
            [5 - laserscan.ranges[0]],[5 - laserscan.ranges[1]]
            ]) 
        current_time = rospy.get_time()
        self.kf.observe_moment(y, current_time)
        self.x_esti_save.append(self.kf.x)
        self.x_esti_time.append(current_time)
        self.p_obsv_save.append(y)
        self.p_obsv_time.append(current_time)

        self.sendStateMsg()

    def callback_state(self, state):
        current_time = rospy.get_time()
        x = np.zeros([4,1])
        x[0,0] = state.twist.linear.x
        x[1,0] = state.pose.position.x
        x[2,0] = state.twist.linear.y
        x[3,0] = state.pose.position.y
        self.x_true_save.append(x)
        self.x_true_time.append(current_time)

    def sendStateMsg(self):
        msg = ModelState()
        #msg.model_name = self.name
        msg.pose.position.x = self.kf.x[1]
        msg.pose.position.y = self.kf.x[3]
        msg.twist.linear.x = self.kf.x[0]
        msg.twist.linear.y = self.kf.x[2]
        self.pub.publish(msg)

    def visualization(self):
        print("Visualizing......")
        t_esti = np.array(self.x_esti_time)
        x_esti = np.concatenate(self.x_esti_save, axis=1)
        
        p_obsv = np.concatenate(self.p_obsv_save, axis=1)
        t_obsv = np.array(self.p_obsv_time)

        t_true = np.array(self.x_true_time)
        x_true = np.concatenate(self.x_true_save, axis=1)

        fig_x = plt.figure(figsize=(16,9))
        
        plt.subplot(2,2,1)

        plt.plot(t_esti, x_esti[1,:].T, label = "esti")
        plt.plot(t_true, x_true[1,:].T, label = "true")
        plt.legend(bbox_to_anchor = (0.85,1), loc='upper left')
        plt.title('px')

        plt.subplot(2,2,2)
        plt.plot(t_esti, x_esti[3,:].T, label = "esti")
        plt.plot(t_true, x_true[3,:].T, label = "true")
        plt.legend(bbox_to_anchor = (0.85,1), loc='upper left')
        plt.title('py')

        plt.subplot(2,2,3)
        plt.plot(x_esti[1,:].T, x_esti[3,:].T, label = "esti")
        plt.plot(x_true[1,:].T, x_true[3,:].T, label = "true")
        plt.legend(bbox_to_anchor = (0.1,1), loc='upper left')
        plt.title('trace: esti with truth')

        plt.subplot(2,2,4)
        plt.plot(x_esti[1,:].T, x_esti[3,:].T, label = 'esti')
        plt.plot(p_obsv[0,:].T, p_obsv[1,:].T, label = 'obsv')
        plt.legend(bbox_to_anchor = (0.1,1), loc='upper left')
        plt.title('trace: esti with observation')

        fig_path = rospkg.RosPack().get_path('cylinder_robot')+"/"
        fig_x.savefig(fig_path+'fig_x.png', dpi=120)
        print("Visualization Complete.")


if __name__ == '__main__':
    try:
        rospy.init_node('perception', anonymous=True)
        obs = Localization()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass