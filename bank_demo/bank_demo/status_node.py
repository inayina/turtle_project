#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Bool

class StatusNode(Node):
    def __init__(self):
        super().__init__('status_node')
        
        # 1. 订阅位姿和停止信号
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.stop_sub = self.create_subscription(Bool, '/stop', self.stop_callback, 10)
        
        # 2. 内部变量
        self.current_x = 0.0
        self.current_y = 0.0
        self.is_stopped = False
        
        # 3. 定时器：每 1.0 秒打印一次日志 (防止 62Hz 刷屏)
        self.timer = self.create_timer(1.0, self.timer_callback)
        
        self.get_logger().info('🖥️  仪表盘监控节点已启动，正在监听系统状态...')

    def pose_callback(self, msg):
        """实时更新坐标，但不在此处打印"""
        self.current_x = msg.x
        self.current_y = msg.y

    def stop_callback(self, msg):
        """实时更新避障状态"""
        self.is_stopped = msg.data

    def timer_callback(self):
        """定时汇总并输出状态到终端"""
        # 使用 Emoji 让状态一眼就能看清
        status_icon = "🔴 [ 遇障暂停 ]" if self.is_stopped else "🟢 [ 正常航行 ]"
        
        # 格式化输出，确保数据对齐美观
        log_msg = (
            f"\n"
            f"----------------------------------------\n"
            f"📍 当前位置 | X: {self.current_x:>5.2f}  Y: {self.current_y:>5.2f}\n"
            f"🚦 运行状态 | {status_icon}\n"
            f"----------------------------------------"
        )
        self.get_logger().info(log_msg)

def main(args=None):
    rclpy.init(args=args)
    node = StatusNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()