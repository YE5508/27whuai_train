#!/usr/bin/env python3
"""控制小海龟从重置位置完成一圈边长为 3 的等边三角形运动。

运行前先启动：ros2 run turtlesim turtlesim_node
运行本程序会调用 /reset；请一次只运行一个巡逻节点。
"""

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.msg import Pose


def normalize_angle(angle):
    """把角度差限制到 [-pi, pi]。"""
    return math.atan2(math.sin(angle), math.cos(angle))


class TrianglePatrol(Node):
    """通过位姿反馈依次转向、走边，最后恢复起始朝向。"""

    def __init__(self):
        super().__init__('triangle_patrol')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.reset_client = self.create_client(Empty, '/reset')
        self.pose = None
        self.reset_future = None
        self.waypoints = []
        self.index = 0
        self.start_heading = 0.0
        self.stage = 'wait_service'
        self.done = False
        self.timer = self.create_timer(0.02, self.on_timer)
        self.get_logger().info('等待 turtlesim 的 /reset 服务……')

    def on_pose(self, pose):
        self.pose = pose

    def stop(self):
        self.publisher.publish(Twist())

    def finish(self):
        self.stop()
        self.timer.cancel()
        self.done = True
        self.get_logger().info('三角形巡逻完成，已回到起点并停止。')

    def make_waypoints(self):
        # 以重置后实际收到的位置及朝向为基准，生成闭合轨迹。
        x, y, heading = self.pose.x, self.pose.y, self.pose.theta
        self.start_heading = heading
        local_points = [(3.0, 0.0), (1.5, 1.5 * math.sqrt(3.0)), (0.0, 0.0)]
        self.waypoints = [
            (x + dx * math.cos(heading) - dy * math.sin(heading),
             y + dx * math.sin(heading) + dy * math.cos(heading))
            for dx, dy in local_points
        ]
        self.get_logger().info(
            f'从 ({x:.3f}, {y:.3f}) 开始三角形巡逻。')

    def on_timer(self):
        if self.stage == 'wait_service':
            if self.reset_client.service_is_ready():
                self.reset_future = self.reset_client.call_async(Empty.Request())
                self.stage = 'wait_reset'
            return

        if self.stage == 'wait_reset':
            if self.reset_future.done():
                self.reset_future.result()
                # 丢弃重置前缓存，等待下一帧位姿。
                self.pose = None
                self.stage = 'wait_pose'
            return

        if self.stage == 'wait_pose':
            if self.pose is not None and self.publisher.get_subscription_count() > 0:
                self.make_waypoints()
                self.stage = 'turn'
            return

        cmd = Twist()
        if self.stage == 'final_turn':
            error = normalize_angle(self.start_heading - self.pose.theta)
            if abs(error) <= 0.015:
                self.finish()
                return
            cmd.angular.z = max(-2.0, min(2.0, 4.0 * error))
        else:
            target_x, target_y = self.waypoints[self.index]
            dx, dy = target_x - self.pose.x, target_y - self.pose.y
            distance = math.hypot(dx, dy)
            if distance <= 0.025:
                self.stop()
                self.index += 1
                self.get_logger().info(
                    f'完成第 {self.index}/{len(self.waypoints)} 条边。')
                self.stage = (
                    'final_turn' if self.index == len(self.waypoints) else 'turn')
                return

            error = normalize_angle(math.atan2(dy, dx) - self.pose.theta)
            if self.stage == 'turn':
                if abs(error) <= 0.015:
                    self.stage = 'drive'
                else:
                    cmd.angular.z = max(-2.0, min(2.0, 4.0 * error))
            else:
                cmd.linear.x = min(2.0, 2.5 * distance)
                cmd.angular.z = max(-2.0, min(2.0, 4.0 * error))
        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = TrianglePatrol()
    while not node.done:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

