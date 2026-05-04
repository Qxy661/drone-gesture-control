#!/bin/bash
# PX4 + Gazebo Classic 无人机仿真启动脚本 (规范化版)
# 
# 使用方法:
#   bash /root/start_drone_sim.sh          # 启动 PX4 + Gazebo
#   bash /root/start_drone_sim.sh --ros2   # 启动 PX4 + Gazebo + MAVROS (ROS2集成)
#
# 快捷命令 (在 WSL 中):
#   drone-start   - 启动仿真
#   drone-stop    - 停止仿真
#   drone-status  - 查看状态

set -e

PX4_ROOT=/root/PX4-Autopilot
BUILD_PATH=$PX4_ROOT/build/px4_sitl_default
GZ_BUILD=$PX4_ROOT/Tools/simulation/gazebo-classic/sitl_gazebo-classic/build
MODEL=iris
WORLD=empty

# ========== 环境设置 ==========
export DISPLAY=:0
export GAZEBO_PLUGIN_PATH=$GZ_BUILD
export GAZEBO_MODEL_PATH=$PX4_ROOT/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models
export LD_LIBRARY_PATH=$GZ_BUILD:$LD_LIBRARY_PATH
export PX4_SIM_MODEL=gazebo-classic_${MODEL}
export PX4_SIM_WORLD=$WORLD
export PATH=$BUILD_PATH/bin:$BUILD_PATH/rootfs:$PATH

# ========== 杀掉残留进程 ==========
pkill -x gzserver 2>/dev/null || true
pkill -x gzclient 2>/dev/null || true
pkill -x px4 2>/dev/null || true
pkill -f 'gz model' 2>/dev/null || true
pkill -x mavros_node 2>/dev/null || true
sleep 2

echo "=========================================="
echo "  PX4 + Gazebo Classic 无人机仿真"
echo "  模型: ${MODEL}"
echo "  世界: ${WORLD}"
echo "=========================================="
echo ""

# ========== 1. 启动 Gazebo 服务器 ==========
echo "[1/5] 启动 Gazebo 服务器..."
WORLD_PATH=$PX4_ROOT/Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds/${WORLD}.world
gzserver --verbose $WORLD_PATH &
GZ_SERVER_PID=$!

# 等待 gzserver 就绪
echo "  等待 Gazebo 服务器就绪..."
for i in $(seq 1 30); do
    if gz model --info --model-name=nonexistent_test 2>&1 | grep -q "Unable to"; then
        echo "  Gazebo 服务器已就绪！"
        break
    fi
    if ! kill -0 $GZ_SERVER_PID 2>/dev/null; then
        echo "  错误: Gazebo 服务器启动失败！"
        exit 1
    fi
    sleep 1
done

# ========== 2. 生成无人机模型 ==========
echo "[2/5] 生成 ${MODEL} 无人机模型..."
MODEL_PATH=$PX4_ROOT/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models/${MODEL}/${MODEL}.sdf
gz model --spawn-file="$MODEL_PATH" --model-name=${MODEL} -x 0 -y 0 -z 0.3 2>&1

# 验证模型已加载
sleep 2
if gz model --info --model-name=${MODEL} 2>&1 | grep -q "name:"; then
    echo "  无人机模型加载成功！"
else
    echo "  警告: 无人机模型可能未正确加载"
fi

# ========== 3. 启动 Gazebo 客户端 ==========
echo "[3/5] 启动 Gazebo 图形界面..."
gzclient &
GZ_CLIENT_PID=$!
sleep 3

if kill -0 $GZ_CLIENT_PID 2>/dev/null; then
    echo "  Gazebo 图形界面已启动！"
else
    echo "  警告: Gazebo 图形界面启动失败"
fi

# ========== 4. 启动 PX4 ==========
echo "[4/5] 启动 PX4 飞控..."
cd $BUILD_PATH/rootfs
$BUILD_PATH/bin/px4 -s etc/init.d-posix/rcS &
PX4_PID=$!

# 等待 PX4 启动
echo "  等待 PX4 启动..."
sleep 5

# ========== 5. 启动 MAVROS (如果指定 --ros2) ==========
if [ "$1" = "--ros2" ]; then
    echo "[5/5] 启动 MAVROS (ROS2)..."
    source /opt/ros/humble/setup.bash
    source /root/ros2_ws/install/setup.bash
    ros2 launch drone_utils mavros_sitl.launch.py &
    MAVROS_PID=$!
    echo "  MAVROS 已启动"
else
    echo "[5/5] 跳过 MAVROS (使用 --ros2 参数启用)"
fi

echo ""
echo "=========================================="
echo "  仿真已启动！"
echo "  Gazebo 窗口应该在 Windows 桌面弹出"
echo ""
echo "  常用命令:"
echo "    commander takeoff    - 起飞"
echo "    commander land       - 降落"
echo "    commander mode posctl - 位置控制"
echo ""
echo "  ROS2 命令 (如果启用了 MAVROS):"
echo "    ros2 topic list      - 查看话题"
echo "    ros2 topic echo /mavros/state - 查看状态"
echo ""
echo "  按 Ctrl+C 退出"
echo "=========================================="
echo ""

# 等待 PX4 进程结束
wait $PX4_PID 2>/dev/null || true

# ========== 清理 ==========
echo ""
echo "正在清理..."
kill $GZ_CLIENT_PID $GZ_SERVER_PID 2>/dev/null || true
[ -n "$MAVROS_PID" ] && kill $MAVROS_PID 2>/dev/null || true
wait 2>/dev/null
echo "完成！"
