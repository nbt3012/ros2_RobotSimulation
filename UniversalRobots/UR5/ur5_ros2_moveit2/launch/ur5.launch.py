#!/usr/bin/python3

# ===================================== COPYRIGHT ===================================== #
#                                                                                       #
#  IFRA (Intelligent Flexible Robotics and Assembly) Group, CRANFIELD UNIVERSITY        #
#  Created on behalf of the IFRA Group at Cranfield University, United Kingdom          #
#  E-mail: IFRA@cranfield.ac.uk                                                         #
#                                                                                       #
#  Licensed under the Apache-2.0 License.                                               #
#  You may not use this file except in compliance with the License.                     #
#  You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0  #
#                                                                                       #
#  Unless required by applicable law or agreed to in writing, software distributed      #
#  under the License is distributed on an "as-is" basis, without warranties or          #
#  conditions of any kind, either express or implied. See the License for the specific  #
#  language governing permissions and limitations under the License.                    #
#                                                                                       #
#  IFRA Group - Cranfield University                                                    #
#  AUTHORS: Mikel Bueno Viso - Mikel.Bueno-Viso@cranfield.ac.uk                         #
#           Seemal Asif      - s.asif@cranfield.ac.uk                                   #
#           Phil Webb        - p.f.webb@cranfield.ac.uk                                 #
#                                                                                       #
#  Date: September, 2022.                                                               #
#                                                                                       #
# ===================================== COPYRIGHT ===================================== #

# ======= CITE OUR WORK ======= #
# You can cite our work with the following statement:
# IFRA (2022) ROS2.0 ROBOT SIMULATION. URL: https://github.com/IFRA-Cranfield/ros2_RobotSimulation.

# ur5.launch.py:
# Launch file for the UR5 ROBOT GAZEBO + MoveIt!2 SIMULATION in ROS2 Foxy:

# Import libraries:
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro
import yaml

# LOAD FILE:
def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        # parent of IOError, OSError *and* WindowsError where available.
        return None
# LOAD YAML:
def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        # parent of IOError, OSError *and* WindowsError where available.
        return None

# ========== **GENERATE LAUNCH DESCRIPTION** ========== #
def generate_launch_description():


    # *********************** Gazebo *********************** # 
    
    # DECLARE Gazebo WORLD file:
    ur5_ros2_gazebo = os.path.join(
        get_package_share_directory('ur5_ros2_gazebo'),
        'worlds',
        'ur5.world')
    # DECLARE Gazebo LAUNCH file:
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch'), 'gz_sim.launch.py']),
                launch_arguments={'world': ur5_ros2_gazebo}.items(),
             )

    # ========== COMMAND LINE ARGUMENTS ========== #
    print("")
    print(" --- Cranfield University --- ")
    print("        (c) IFRA Group        ")
    print("")

    print("ros2_RobotSimulation --> UR5 ROBOT")
    print("Launch file -> ur5.launch.py")

    print("")
    print("Robot configuration:")
    print("")

    # Cell Layout:
    print("- Cell layout:")
    error = True
    while (error == True):
        print("     + Option N1: UR5 ROBOT alone.")
        print("     + Option N2: UR5 ROBOT on top of a pedestal.")
        cell_layout = input ("  Please select: ")
        if (cell_layout == "1"):
            error = False
            cell_layout_1 = "true"
            cell_layout_2 = "false"
        elif (cell_layout == "2"):
            error = False
            cell_layout_1 = "false"
            cell_layout_2 = "true"
        else:
            print ("  Please select a valid option!")
    print("")

    # End-Effector:
    print("- End-effector:")
    print("     + No EE variants for this robot.")
    EE_no = "true"
    
    # error = True
    # while (error == True):
    #     print("     + Option N1: No end-effector.")
    #     print("     + Option N2: ***.")
    #     end_effector = input ("  Please select: ")
    #     if (end_effector == "1"):
    #         error = False
    #         EE_no = "true"
    #         EE_*** = "false"
    #     elif (end_effector == "2"):
    #         error = False
    #         EE_no = "false"
    #         EE_*** = "true"
    #     else:
    #         print ("  Please select a valid option!")
    print("")

    # ***** ROBOT DESCRIPTION ***** #
    # UR5 ROBOT Description file package:
    ur5_description_path = os.path.join(
        get_package_share_directory('ur5_ros2_gazebo'))
    # UR5 ROBOT urdf file path:
    xacro_file = os.path.join(ur5_description_path,
                              'urdf',
                              'ur5.urdf.xacro')
    # Generate ROBOT_DESCRIPTION for UR5 ROBOT:
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc, mappings={
        "cell_layout_1": cell_layout_1,
        "cell_layout_2": cell_layout_2,
        "EE_no": EE_no,
        # "EE_**": EE_**,
        })
    robot_description_config = doc.toxml()
    robot_description = {'robot_description': robot_description_config}

    # SPAWN ROBOT TO GAZEBO:
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'ur5'],
                        output='screen')

    # ***** STATIC TRANSFORM ***** #
    # NODE -> Static TF:
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "base_link"],
    )
    # Publish TF:
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    # ***** ROS2_CONTROL -> LOAD CONTROLLERS ***** #

    load_controllers = []
    for controller in [
        "ur5_controller",
        "joint_state_controller",
    ]:
        load_controllers += [
            ExecuteProcess(
                cmd=["ros2 run controller_manager spawner.py {}".format(controller)],
                shell=True,
                output="screen",
            )
        ]


    # *********************** MoveIt!2 *********************** #   
    
    # Command-line argument: RVIZ file?
    rviz_arg = DeclareLaunchArgument(
        "rviz_file", default_value="False", description="Load RVIZ file."
    )

    # *** PLANNING CONTEXT *** #
    # Robot description, SRDF:
    robot_description_semantic_config = load_file("ur5_ros2_moveit2", "config/ur5.srdf")
    robot_description_semantic = {"robot_description_semantic": robot_description_semantic_config }
    
    # Kinematics.yaml file:
    kinematics_yaml = load_yaml("ur5_ros2_moveit2", "config/kinematics.yaml")
    robot_description_kinematics = {"robot_description_kinematics": kinematics_yaml}

    # Move group: OMPL Planning.
    ompl_planning_pipeline_config = {
        "move_group": {
            "planning_plugin": "ompl_interface/OMPLPlanner",
            "request_adapters": """default_planner_request_adapters/AddTimeOptimalParameterization default_planner_request_adapters/FixWorkspaceBounds default_planner_request_adapters/FixStartStateBounds default_planner_request_adapters/FixStartStateCollision default_planner_request_adapters/FixStartStatePathConstraints""",
            "start_state_max_bounds_error": 0.1,
        }
    }
    ompl_planning_yaml = load_yaml("ur5_ros2_moveit2", "config/ompl_planning.yaml")
    ompl_planning_pipeline_config["move_group"].update(ompl_planning_yaml)

    # MoveIt!2 Controllers:
    moveit_simple_controllers_yaml = load_yaml("ur5_ros2_moveit2", "config/ur5_controllers.yaml")
    moveit_controllers = {
        "moveit_simple_controller_manager": moveit_simple_controllers_yaml,
        "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }
    trajectory_execution = {
        "moveit_manage_controllers": True,
        "trajectory_execution.allowed_execution_duration_scaling": 1.2,
        "trajectory_execution.allowed_goal_duration_margin": 0.5,
        "trajectory_execution.allowed_start_tolerance": 0.01,
    }
    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }

    # START NODE -> MOVE GROUP:
    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            ompl_planning_pipeline_config,
            trajectory_execution,
            moveit_controllers,
            planning_scene_monitor_parameters,
        ],
    )

    # RVIZ:
    load_RVIZfile = LaunchConfiguration("rviz_file")
    rviz_base = os.path.join(get_package_share_directory("ur5_ros2_moveit2"), "config")
    rviz_full_config = os.path.join(rviz_base, "ur5_moveit2.rviz")
    rviz_node_full = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_full_config],
        parameters=[
            robot_description,
            robot_description_semantic,
            ompl_planning_pipeline_config,
            kinematics_yaml,
        ],
        condition=UnlessCondition(load_RVIZfile),
    )

    return LaunchDescription(
        [
            # Gazebo nodes:
            gazebo, 
            spawn_entity,
            # ROS2_CONTROL:
            static_tf,
            robot_state_publisher,
            
            RegisterEventHandler(
                OnProcessExit(
                    target_action = spawn_entity,
                    on_exit = [

                        # MoveIt!2:
                        TimerAction(
                            period=5.0,
                            actions=[
                                rviz_arg,
                                rviz_node_full,
                                run_move_group_node
                            ]
                        ),

                    ]
                )
            )
        ]
        + load_controllers
    )