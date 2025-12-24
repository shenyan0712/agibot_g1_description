import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, LaunchContext
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch.logging import get_logger  # 导入ROS2 Launch日志器

logger = get_logger('my_robot_launch')
logger.setLevel('DEBUG')  # 强制设置为DEBUG级别

pkg_name = "g1_robot_description"

def generate_launch_description():

    
    if False:
        # 1. 获取Package路径
        pkg_share = get_package_share_directory(pkg_name)
        # 2. 定义URDF文件路径
        urdf_file_path = os.path.join(pkg_share, 'urdf', 'simple_robot.urdf')

        # 3. 读取URDF文件内容，作为参数传递
        with open(urdf_file_path, 'r') as f:
            robot_description_content = f.read()

    else:
        # pkg_share = FindPackageShare(package='urdf_rviz_demo')
        pkg_share = get_package_share_directory(pkg_name)
        # xacro_file_path = PathJoinSubstitution(
        #     [pkg_share, 'urdf', 'simple_robot.xacro']
        # )
        xacro_file_path = os.path.join(pkg_share, 'urdf/robotiq', 'robotiq_85_gripper.xacro')
        logger.debug(xacro_file_path)

        # 2. 构造Xacro解析命令：xacro + 文件路径
        robot_description = Command(
            [FindExecutable(name='xacro'), ' ', xacro_file_path]
        )
        context = LaunchContext()  # 创建Launch上下文
        robot_description_content = robot_description.perform(context)  # 解析为字符串

    # 4. 定义节点
    # 机器人状态发布器节点
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_content,  # 传递URDF内容
            'use_sim_time': False  # 非仿真环境，使用系统时间
        }]
    )

    # 关节状态发布器（GUI版）：提供滑块调节关节
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{
            'use_sim_time': False
        }]
    )

    # RVIZ2节点
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(pkg_share, 'config', 'rviz_config.rviz')]  # 加载RVIZ配置文件
        # 若未编写配置文件，可注释该行，运行时手动配置
    )

    # 5. 组装启动描述
    ld = LaunchDescription()
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_gui_node)
    ld.add_action(rviz2_node)

    return ld