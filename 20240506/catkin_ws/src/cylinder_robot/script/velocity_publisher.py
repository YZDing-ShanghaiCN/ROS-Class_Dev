#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 该例程将发布turtle1/cmd_vel话题，消息类型geometry_msgs::Twist
import rospy
from geometry_msgs.msg import Twist
import math
def velocity_publisher():
    # ROS节点初始化
    rospy.init_node('velocity_publisher', anonymous=True)
    # 创建一个Publisher，发布名为/turtle1/cmd_vel的topic，消息类型为geometry_msgs::Twist，队列长度10
    turtle_vel_pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    #设置循环的频率
    rate = rospy.Rate(2)
    while not rospy.is_shutdown():
        #stage1:walk forward
        # 初始化geometry_msgs::Twist类型的消息
        vel_msg = Twist()
        vel_msg.linear.x = 4
        vel_msg.angular.z = 0
        # 发布消息
        turtle_vel_pub.publish(vel_msg)
        rospy.loginfo("Publsh turtle velocity command[%0.2f m/s, %0.2f rad/s]",
                vel_msg.linear.x, vel_msg.angular.z)
        # 按照循环频率延时
        rate.sleep()

        #stage2:turn left
        # 初始化geometry_msgs::Twist类型的消息
        vel_msg = Twist()
        vel_msg.linear.x = 0
        vel_msg.angular.z = math.pi
        # 发布消息
        turtle_vel_pub.publish(vel_msg)
        rospy.loginfo("Publsh turtle velocity command[%0.2f m/s, %0.2f rad/s]",
                vel_msg.linear.x, vel_msg.angular.z)
        # 按照循环频率延时
        rate.sleep()
if __name__ == '__main__':
    try:
        velocity_publisher()
    except rospy.ROSInterruptException:
        pass