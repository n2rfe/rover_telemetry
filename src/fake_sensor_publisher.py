import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
import math
import random
import time

class FakeSensorPublisher(Node):
    def __init__(self):
        super().__init__('fake_sensor_publisher')
        self.imu_pub  = self.create_publisher(Imu,      '/imu',  10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.timer    = self.create_timer(0.1, self.publish)  # 10 Hz
        self.t        = 0.0
        self.get_logger().info('Fake sensor publisher started at 10 Hz')

    def publish(self):
        now = self.get_clock().now().to_msg()
        self.t += 0.1

        # IMU
        imu = Imu()
        imu.header.stamp    = now
        imu.header.frame_id = 'imu_link'
        # Simulate gentle sinusoidal motion + noise
        imu.linear_acceleration.x = math.sin(self.t * 0.5) + random.gauss(0, 0.02)
        imu.linear_acceleration.y = math.cos(self.t * 0.3) + random.gauss(0, 0.02)
        imu.linear_acceleration.z = 9.81              + random.gauss(0, 0.01)
        imu.angular_velocity.x    = random.gauss(0, 0.01)
        imu.angular_velocity.y    = random.gauss(0, 0.01)
        imu.angular_velocity.z    = math.sin(self.t * 0.2) * 0.1
        self.imu_pub.publish(imu)

        # Odometry
        odom = Odometry()
        odom.header.stamp    = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id  = 'base_link'
        odom.pose.pose.position.x = math.sin(self.t * 0.2) * 2.0
        odom.pose.pose.position.y = math.cos(self.t * 0.2) * 2.0
        odom.twist.twist.linear.x  = math.cos(self.t * 0.2) * 0.4
        odom.twist.twist.angular.z = 0.2
        self.odom_pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = FakeSensorPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
