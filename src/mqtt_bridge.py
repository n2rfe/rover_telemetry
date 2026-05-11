import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
import paho.mqtt.client as mqtt
import json
import time

BROKER_HOST = 'localhost'   #
BROKER_PORT = 1883

class MQTTBridge(Node):
    def __init__(self):
        super().__init__('mqtt_bridge')

        # MQTT client setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect    = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        self.client.loop_start()

        # ROS2 subscriptions
        self.create_subscription(Imu,      '/imu',  self.imu_cb,  10)
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        self.get_logger().info(f'MQTT bridge ready -> {BROKER_HOST}:{BROKER_PORT}')

    def on_connect(self, client, userdata, flags, rc, properties=None):
        status = 'connected' if rc == 0 else f'failed (rc={rc})'
        self.get_logger().info(f'Broker {status}')

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        self.get_logger().warn('Broker disconnected')

    def publish(self, topic, payload: dict):
        payload['ts'] = time.time()          # timestamp for latency calc
        self.client.publish(topic, json.dumps(payload), qos=0)

    def imu_cb(self, msg: Imu):
        self.publish('rover/imu', {
            'acc':  { 'x': round(msg.linear_acceleration.x, 4),
                      'y': round(msg.linear_acceleration.y, 4),
                      'z': round(msg.linear_acceleration.z, 4) },
            'gyro': { 'x': round(msg.angular_velocity.x, 4),
                      'y': round(msg.angular_velocity.y, 4),
                      'z': round(msg.angular_velocity.z, 4) },
        })

    def odom_cb(self, msg: Odometry):
        self.publish('rover/odom', {
            'pos': { 'x': round(msg.pose.pose.position.x, 4),
                     'y': round(msg.pose.pose.position.y, 4) },
            'vel': { 'linear':  round(msg.twist.twist.linear.x,  4),
                     'angular': round(msg.twist.twist.angular.z, 4) },
        })

    def destroy_node(self):
        self.client.loop_stop()
        self.client.disconnect()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = MQTTBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
