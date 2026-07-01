#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity
import rospy
from std_msgs.msg import String
def talker():
    # 向名为chatter的rostopic发送String类型的消息，发布者在队列中保留的待发布消息的最大数量为10
    pub = rospy.Publisher('chatter',\
        String, queue_size=10)
    # 创建一个名为talker的节点，anonymous=True时，会在节点名后添加一个唯一的标识符，保证节点的唯一性
    rospy.init_node('talker', anonymous=True)
    # 频率设置为10Hz
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        hello_str = "hello world %s"%rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        # 控制循环频率，保证按照指定频率执行
        rate.sleep()
# 作为主程序运行时，执行if内代码
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass