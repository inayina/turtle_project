#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Bool

class ObstacleNode(Node):
    def __init__(self):
        super().__init__('obstacle_node')
        
        # 订阅乌龟位置
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        # 发布停止指令
        self.stop_pub = self.create_publisher(Bool, '/stop', 10)
        
        # 定义障碍区域（矩形）
        self.obstacle_x_min = 5.2
        self.obstacle_x_max = 5.8
        self.obstacle_y_min = 5.2
        self.obstacle_y_max = 5.8
        
        self.get_logger().info('避障节点已启动，障碍区域: x(5.2-5.8), y(5.2-5.8)')

    def pose_callback(self, msg):
        """检测是否进入障碍区"""
        in_obstacle = (self.obstacle_x_min < msg.x < self.obstacle_x_max and 
                       self.obstacle_y_min < msg.y < self.obstacle_y_max)
        
        # 发布停止指令
        stop_msg = Bool()
        stop_msg.data = in_obstacle
        self.stop_pub.publish(stop_msg)
        
        if in_obstacle:
            self.get_logger().warn(f'进入障碍区! 位置: ({msg.x:.2f}, {msg.y:.2f})')

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()