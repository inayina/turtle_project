#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from bank_demo_interfaces.srv import SetGoal
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Bool
import math

class NavigationNode(Node):
    def __init__(self):
        super().__init__('navigation_node')
        
        # 1. 初始化坐标（就绪检查关键：设为-1.0）
        self.current_x = -1.0
        self.current_y = -1.0
        self.current_theta = 0.0

        # 2. 目标点与任务状态
        self.target_x = 0.0
        self.target_y = 0.0
        self.goal_received = False

        # 3. 避障状态机变量
        self.stop_flag = False      # 外部障碍信号
        self.stop_start_time = None # 开始被堵住的时间
        self.escape_mode = False    # 是否处于逃脱动作中
        self.escape_start_time = 0.0

        # 4. 发布者与订阅者
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.reached_pub = self.create_publisher(Bool, '/goal_reached', 10)
       
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.stop_sub = self.create_subscription(Bool, '/stop', self.stop_callback, 10)

        # 5. 服务：接收目标点
        self.srv = self.create_service(SetGoal, 'set_goal', self.goal_callback)

        # 6. 控制定时器：10Hz
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('✅ 导航节点已启动，状态机就绪')

    # ---------------- 服务回调 ----------------
    def goal_callback(self, request, response):
        """接收新目标，并重置到达判定"""
        self.target_x = request.x
        self.target_y = request.y
        self.goal_received = True
        
        self.get_logger().warn(f'📢 收到新任务！目标点设置为: ({self.target_x:.2f}, {self.target_y:.2f})')
        
        response.success = True
        response.message = f"目标已更新"
        return response

    # ---------------- 订阅回调 ----------------
    def pose_callback(self, msg):
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta

    def stop_callback(self, msg):
        """更新停止标志，如果是从停止变为移动，重置计时器"""
        old_flag = self.stop_flag
        self.stop_flag = msg.data
        if old_flag and not self.stop_flag:
            self.stop_start_time = None

    # ---------------- 核心控制循环 ----------------
    def control_loop(self):
        # [检查1]：坐标未就绪不干活
        if self.current_x == -1.0:
            return

        now = self.get_clock().now().nanoseconds / 1e9

        # [状态1]：逃脱模式（最高优先级）
        if self.escape_mode:
            elapsed = now - self.escape_start_time
            if elapsed < 2.0:
                # 阶段1：强制后退，拉开与障碍的距离
                self.publish_velocity(-1.5, 0.0)
            elif elapsed < 3.5:
                # 阶段2：大角度转向，寻找新出路
                self.publish_velocity(0.0, 2.5)
            else:
                self.get_logger().info('✨ 逃脱完成，尝试继续导航')
                self.escape_mode = False
                self.stop_start_time = None
            return # 逃脱中不执行后续导航

        # [状态2]：遇障暂停计时
        if self.stop_flag:
            self.publish_velocity(0.0, 0.0)
            if self.stop_start_time is None:
                self.stop_start_time = now
            
            # 停止超过2秒，判定为死锁，进入逃脱模式
            if now - self.stop_start_time > 2.0:
                self.get_logger().error('⚠️ 检测到长时间死锁，启动逃脱程序！')
                self.escape_mode = True
                self.escape_start_time = now
            return

        # [状态3]：正常导航（强行推进）
        if self.goal_received:
            dx = self.target_x - self.current_x
            dy = self.target_y - self.current_y
            distance = math.sqrt(dx**2 + dy**2)

            # --- A. 到达判断 ---
            if distance < 0.3: # 适当放宽判定阈值增加成功率
                self.publish_velocity(0.0, 0.0)
                self.goal_received = False
                self.get_logger().warn(f'🏆 成功到达目标点: ({self.target_x:.2f}, {self.target_y:.2f})')

                # 发布到达信号
                msg = Bool()
                msg.data = True
                self.reached_pub.publish(msg)
                return

            # --- B. 计算角度偏差 ---
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - self.current_theta

            # 角度归一化 (-pi to pi)
            while angle_diff > math.pi: angle_diff -= 2.0 * math.pi
            while angle_diff < -math.pi: angle_diff += 2.0 * math.pi

            # --- C. 【强行推进逻辑】 ---
            # 不设置 angle_diff 阈值，强制给线速度 linear_speed
            # 这能让乌龟划出弧线切入目标点，避开 2.30 这种尴尬的停滞位
            linear_speed = 1.0 
            angular_speed = angle_diff * 3.0
            
            # 限速保护：防止 turtlesim 窗口中乌龟因旋转过快失控
            angular_speed = max(min(angular_speed, 1.8), -1.8)

            self.publish_velocity(linear_speed, angular_speed)

    # ---------------- 辅助函数 ----------------
    def publish_velocity(self, linear, angular):
        twist = Twist()
        twist.linear.x = float(linear)
        twist.angular.z = float(angular)
        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()