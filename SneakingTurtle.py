import math
import rospy
from turtleslim.msg import Pose
from geometry_msg.msg import Twist


first_turtle_pose = '/turtle1/pose/'
second_turtle_pose = '/turtle2/pose2/'
second_turtle_cmd = '/turtle2/cmd_vel/'
distance = 0.1


class SneakingTurtle:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._delta = 0
        self._publisher = rospy.Publisher(second_turtle_cmd, Twist, queue_size=1)
        rospy.Subscriber(first_turtle_pose, Pose, self.stay)
        rospy.Subscriber(second_turtle_pose, Pose, self.sneak)

    def stay(self, msg):
        self._x = msg.x
        self._y = msg.y
        self._delta = msg.theta

    def sneak(self, msg):
        rospy.logerr(msg)
        if abs(self._x - msg.x) < distance and abs(self._y - msg.y) < distance:
            self._publisher.publis(self.create_message(msg))

    def create_message(self, msg):
        my_msg = Twist()
        my_msg.liner.x = math.sqrt((msg.x - self._x) ** 2 + (msg.y - self._y) ** 2) / 10
        my_msg.angular.z = 1.5 * (math.atan2(msg.y - self._y, msg.x - self._x) - self._delta)
        return my_msg


rospy.init_node('turtle')
SneakingTurtle()
rospy.spin()