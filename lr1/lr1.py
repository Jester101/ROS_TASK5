import rospy
import math
from sensor_msgs.msg import LaserScan

DEFAULT_STEP = 3
MAX_FLOAT = 10000.0
RESOLUTION = 0.1
MAX_DIST = 0.1 * RESOLUTION
OLD_PUBLISHER = rospy.Publisher('/base_scan', LaserScan, queue_size=10)
FIXED_PUBLISHER = rospy.Publisher('/fixed_scan', LaserScan, queue_size=10)


def process_msg(msg, old=OLD_PUBLISHER, new=FIXED_PUBLISHER):
    old.publish(msg)
    msg = laser_fixing(msg, msg.angle_min, msg.angle_increment)
    new.publish(msg)


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def get_point(range, theta):
    return range * math.cos(theta), range * math.sin(theta)


def get_angle(angle, angle_increment, position):
    return angle + angle_increment * position


def laser_fixing(msg, angle, increment):
    data = []
    ranges = msg.ranges

    for i in range(DEFAULT_STEP, len(ranges) - DEFAULT_STEP):
        prev_step_point = get_point(ranges[i - DEFAULT_STEP], get_angle(angle, increment, i - DEFAULT_STEP))
        current_point = get_point(ranges[i], get_angle(angle, increment, i))
        next_step_point = get_point(ranges[i + DEFAULT_STEP], get_angle(angle, increment, i + DEFAULT_STEP))

        if distance(prev_step_point, current_point) > MAX_DIST or distance(next_step_point, current_point) > MAX_DIST:
            data.append(MAX_FLOAT)
        else:
            data.append(data[i])

    msg.ranges = [MAX_FLOAT] * DEFAULT_STEP + data + [MAX_FLOAT] * DEFAULT_STEP
    return msg


rospy.init_node('lr1')
rospy.Subscriber('base_scan', LaserScan, process_msg)
r = rospy.Rate(0.5)

while not (rospy.is_shutdown()):
    r.sleep()
