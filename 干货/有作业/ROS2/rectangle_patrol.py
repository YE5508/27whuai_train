#!/usr/bin/env python3
"""控制小海龟从重置位置完成一圈 3×2 矩形运动。

运行前先启动：ros2 run turtlesim turtlesim_node
运行本程序会调用 /reset；请一次只运行一个巡逻节点。
"""

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.msg import Pose


def normalize_angle(angle):
    """把角度差限制到 [-pi, pi]。"""
    return math.atan2(math.sin(angle), math.cos(angle))


class RectanglePatrol(Node):
    """通过位姿反馈依次转向、走边，最后恢复起始朝向。"""

    def __init__(self):
        super().__init__('rectangle_patrol')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.reset_client = self.create_client(Empty, '/reset')
        self.pose = None
        self.pose_time = None
        self.reset_future = None
        self.waypoints = []
        self.index = 0
        self.start_heading = 0.0
        self.stage = 'wait_service'
        self.started = time.monotonic()
        self.done = False
        self.failed = False
        self.timer = self.create_timer(0.02, self.on_timer)
        self.get_logger().info('等待 turtlesim 的 /reset 服务……')

    def on_pose(self, pose):
        self.pose = pose
        self.pose_time = time.monotonic()

    def stop(self):
        self.publisher.publish(Twist())

    def finish(self, error=None):
        self.stop()
        self.timer.cancel()
        self.done = True
        self.failed = error is not None
        if error:
            self.get_logger().error(error)
        else:
            self.get_logger().info('矩形巡逻完成，已回到起点并停止。')

    def make_waypoints(self):
        # 以重置后实际收到的位置及朝向为基准，生成闭合轨迹。
        x, y, heading = self.pose.x, self.pose.y, self.pose.theta
        self.start_heading = heading
        local_points = [(3.0, 0.0), (3.0, 2.0), (0.0, 2.0), (0.0, 0.0)]
        self.waypoints = [
            (x + dx * math.cos(heading) - dy * math.sin(heading),
             y + dx * math.sin(heading) + dy * math.cos(heading))
            for dx, dy in local_points
        ]
        self.get_logger().info(
            f'从 ({x:.3f}, {y:.3f}) 开始矩形巡逻。')

    def on_timer(self):
        now = time.monotonic()
        if now - self.started > 90.0:
            self.finish('巡逻超时，请检查 turtlesim 与话题通信。')
            return

        if self.stage == 'wait_service':
            if self.reset_client.service_is_ready():
                self.reset_future = self.reset_client.call_async(Empty.Request())
                self.stage = 'wait_reset'
            elif now - self.started > 15.0:
                self.finish('未发现 /reset 服务，请先启动 turtlesim。')
            return

        if self.stage == 'wait_reset':
            if self.reset_future.done():
                try:
                    self.reset_future.result()
                except Exception as exc:
                    self.finish(f'重置失败：{exc}')
                    return
                # 丢弃重置前缓存，等待下一帧位姿。
                self.pose = None
                self.pose_time = None
                self.stage = 'wait_pose'
                self.pose_wait_started = now
            elif now - self.started > 20.0:
                self.finish('/reset 服务响应超时。')
            return

        if self.stage == 'wait_pose':
            if self.pose is not None:
                # 等待速度订阅端被发现，避免首条控制指令丢失。
                if self.publisher.get_subscription_count() > 0:
                    self.make_waypoints()
                    self.stage = 'turn'
            if self.stage == 'wait_pose' and now - self.pose_wait_started > 10.0:
                self.finish('未收到位姿或未发现速度订阅端，请检查通信。')
            return

        if self.pose_time is None or now - self.pose_time > 2.0:
            self.finish('位姿反馈中断，已发送停止指令。')
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
                # 大角度偏差时先停下转向，防止偏离轨迹。
                if abs(error) > 0.15:
                    self.stage = 'turn'
                else:
                    cmd.linear.x = min(2.0, 2.5 * distance)
                    cmd.angular.z = max(-2.0, min(2.0, 4.0 * error))
        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = None
    exit_code = 0
    try:
        node = RectanglePatrol()
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
        if node.failed:
            exit_code = 1
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.timer.cancel()
            if rclpy.ok():
                node.stop()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())

