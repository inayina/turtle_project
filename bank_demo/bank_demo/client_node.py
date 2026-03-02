#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from bank_demo_interfaces.srv import SetGoal
import time

class ClientNode(Node):
    """
    智能任务调度客户端
    功能：按顺序下达目标，等待导航节点反馈 'Reached' 信号后再下达下一个。
    """

    def __init__(self):
        super().__init__('client_node')

        # 1. 声明服务客户端
        self.cli = self.create_client(SetGoal, 'set_goal')
        
        # 2. 订阅导航节点的到达信号
        self.reached_sub = self.create_subscription(
            Bool, 
            '/goal_reached', 
            self.reached_callback, 
            10)

        # 3. 预定义目标序列
        # 注意：第一个点 (1.1, 1.1) 是测试避障逻辑的关键
        self.goals = [
            (1.1, 1.1),
            (8.0, 8.0),
            (9.0, 9.0),
            (2.0, 2.0)
        ]
        self.current_goal_idx = 0
        self.waiting_for_arrival = False
        
        # 4. 启动冗余计时（给系统 3 秒准备时间）
        self.startup_wait_count = 3 

        # 5. 定时检查器 (1Hz)
        self.timer = self.create_timer(1.0, self.check_and_send)
        
        self.get_logger().info('🚀 智能客户端已启动，准备开始任务序列...')

    def reached_callback(self, msg):
        """监听到导航节点发来的到达信号"""
        if msg.data and self.waiting_for_arrival:
            goal = self.goals[self.current_goal_idx]
            self.get_logger().warn(f'✨ [反馈] 目标点 {self.current_goal_idx+1} ({goal[0]}, {goal[1]}) 已成功到达！')
            
            # 索引推进，解除等待锁定
            self.current_goal_idx += 1
            self.waiting_for_arrival = False

    def check_and_send(self):
        """核心调度逻辑"""
        
        # A. 初始启动等待（防止系统未就绪就抢跑）
        if self.startup_wait_count > 0:
            self.get_logger().info(f'⏳ 系统热身中... 剩余 {self.startup_wait_count} 秒')
            self.startup_wait_count -= 1
            return

        # B. 检查是否所有任务已完成
        if self.current_goal_idx >= len(self.goals):
            if self.current_goal_idx == len(self.goals):
                self.get_logger().info('🎉 所有目标点已全部完成！任务结束。')
                self.current_goal_idx += 1 # 防止重复打印
            return

        # C. 如果正在等待上一个点到达，则静默
        if self.waiting_for_arrival:
            return

        # D. 确保服务端已挂载
        if not self.cli.service_is_ready():
            self.get_logger().info('等待 SetGoal 服务就绪...')
            return

        # E. 发送新目标
        self.send_next_goal()

    def send_next_goal(self):
        x, y = self.goals[self.current_goal_idx]
        req = SetGoal.Request()
        req.x = float(x)
        req.y = float(y)
        
        self.get_logger().info(f'📡 [指令] 正在向导航节点发送点 {self.current_goal_idx+1}: ({x}, {y})')
        
        # 异步调用服务
        future = self.cli.call_async(req)
        self.waiting_for_arrival = True

def main(args=None):
    rclpy.init(args=args)
    node = ClientNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()