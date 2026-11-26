# Collaborative Multi-Robot SLAM & Map Merging

A ROS 2 Jazzy workspace for spawning multiple TurtleBot3 robots (`burger` and `waffle`) in Gazebo Sim, running per-robot SLAM with `slam_toolbox`, and merging their individual occupancy grids into a unified global map.

---

## Workspace Structure

```text
second_evaluvation/
├── floor1.{data,pgm,posegraph,yaml}   # Saved SLAM maps & posegraphs
├── floor2.{data,pgm,posegraph,yaml}
└── src/
    ├── collaborative_slam/            # Multi-robot spawning, SLAM, Nav2, exploration & map merging
    │   ├── collaborative_slam/
    │   │   ├── multirobo_map_merge.py # OpenCV-based multi-robot map merger node (mergemap)
    │   │   ├── explore.py             # Namespaced frontier explorer node (explore)
    │   │   ├── explore_2.py           # Global /map frontier explorer node (exp)
    │   │   └── elevator_controller.py # JointTrajectory elevator controller (elevator)
    │   ├── config/
    │   │   ├── robots.yaml            # Multi-robot spawn configuration & initial poses
    │   │   ├── slam_toolbox_params_*.yaml
    │   │   ├── navigation_*.yaml / amcl*.yaml
    │   │   └── *.rviz                 # RViz2 configs (burger, waffle, multirobot_map_BW)
    │   ├── launch/
    │   │   ├── display.launch.py      # Gazebo Sim hospital world + robot spawning + ros_gz_bridge + RViz2
    │   │   ├── multiple_roboto.launch.py # Config-driven multi-robot spawner (reads robots.yaml)
    │   │   ├── slam_burger.launch.py  # Online async SLAM for burger
    │   │   ├── slam_waffle.launch.py  # Online sync SLAM for waffle
    │   │   ├── merge_map_launch.py    # Launches mergemap node + multi-robot RViz2
    │   │   └── nav2_*.launch.py / bringup.launch.py / navigation.launch.py
    │   └── urdf/                      # TurtleBot3 Burger, Waffle, and Waffle Pi URDFs
    ├── aws_robomaker_hospital_world/  # Two-floor hospital Gazebo world & models
    └── multifloor_map/                # Multi-floor SLAM, AMCL, and task management
```

---

## Prerequisites

- **ROS 2**: Jazzy (`/opt/ros/jazzy`)
- **Simulation & ROS 2 Packages**:
  - `ros_gz_sim`, `ros_gz_bridge` (Gazebo Sim)
  - `slam_toolbox`
  - `nav2_bringup`
  - `robot_state_publisher`, `xacro`, `rviz2`, `tf2_ros`
- **Python Dependencies** (for `multirobo_map_merge.py` and exploration):
  - `numpy`
  - `opencv-python` (`cv2`)
  - `shapely`
  - `tf_transformations`
  - `PyYAML`

---

## Build

```bash
cd ~/second_evaluvation
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

## Usage

Source the workspace in each new terminal before running launch files:

```bash
source /opt/ros/jazzy/setup.bash
source ~/second_evaluvation/install/setup.bash
```

### 1. Launch Simulation & Spawn Robots

Start Gazebo Sim with the hospital world, `ros_gz_bridge`, `robot_state_publisher`, and RViz2:

```bash
ros2 launch collaborative_slam display.launch.py
```

> **Note:** In `display.launch.py`, `waffle` (`robot_state_publisher_node2`, `spawn_entity2`, `rviz2`) is commented out by default; uncomment those entries if you want to spawn both `burger` and `waffle` from `display.launch.py`. Alternatively, `multiple_roboto.launch.py` spawns all enabled robots listed in `config/robots.yaml`.

### 2. Run SLAM for Each Robot

In separate terminals, start `slam_toolbox` for each robot namespace:

```bash
# Terminal 2 - Burger SLAM (online async)
ros2 launch collaborative_slam slam_burger.launch.py
```

```bash
# Terminal 3 - Waffle SLAM (online sync)
ros2 launch collaborative_slam slam_waffle.launch.py
```

Each robot publishes its own occupancy grid on `/burger/map` and `/waffle/map`.

### 3. Run Map Merging & Visualization

Launch the map merger node (`mergemap`) and the multi-robot RViz2 view (`multirobot_map_BW.rviz`):

```bash
ros2 launch collaborative_slam merge_map_launch.py
```

`MultiRobotMapMerger` subscribes to `/burger/map` and `/waffle/map`, aligns and merges the maps using OpenCV preprocessing (CLAHE contrast enhancement, Gaussian blur, wall dilation, and ORB feature matching), and publishes the combined `OccupancyGrid` on `/map` (frame `world`).

### 4. Teleoperation / Autonomous Exploration (Optional)

Drive the robots manually via `/burger/cmd_vel` and `/waffle/cmd_vel`:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/burger/cmd_vel
```

Or run the frontier exploration nodes (requires Nav2 `navigate_to_pose` action servers):

```bash
ros2 run collaborative_slam explore
# or for global /map exploration:
ros2 run collaborative_slam exp
```

---

## Configuration

- **`src/collaborative_slam/config/robots.yaml`**: Defines robot names (`burger`, `burger_2`, `burger_3`, `waffle`, `waffle_2`, `waffle_3`), initial `(x_pose, y_pose, z_pose)`, and `enabled` flags for `multiple_roboto.launch.py`.
- **`mergemap` node parameters** (in `merge_map_launch.py` / `multirobo_map_merge.py`):
  - `tf_publish_frequency` (default: `20.0`)
  - `map_publish_frequency` (default: `1.0`, set to `0.5` in `merge_map_launch.py`)
  - `visualize` (default: `True` — opens an OpenCV `"Map merger"` preview window)
  - `match_confidence_threshold` (default: `0.035`)
  - `min_map_size` (default: `60000`)

