#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
import rospy
from std_msgs.msg import String
def callback(data):
    rospy.loginfo(rospy.get_caller_id() \
        + "I heard %s", data.data)
    
def listener():
    rospy.init_node('listener', anonymous=True)
    # 订阅来自名为chatter的rostopic上的String类型的信息，当收到信息后，执行回调函数callback
    rospy.Subscriber("chatter", String, callback)
    # 阻塞程序结束，使节点保持运行状态
    rospy.spin()
if __name__ == '__main__':
    listener()