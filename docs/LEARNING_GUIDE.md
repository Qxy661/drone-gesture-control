# Drone Autonomy Suite — 学习指南

> 本指南基于你已有的三个 ROS2 项目，从代码出发学习无人机自主飞行的核心技术。
> 每个阶段都有明确的目标和产出，不是泛泛而谈。

---

## 你的起点

- 大一/大二，自动化专业
- C++ 熟练，Python 会用
- 控制理论零基础
- 有 Jetson Nano + V5+ + A8Mini 硬件（没飞过）
- 已完成三个 ROS2 包：手势识别、自主导航、视觉跟踪

## 学习原则

1. **代码先行** — 先读代码理解"做了什么"，再学理论理解"为什么这样做"
2. **每个概念都要跑通** — 不要只看不练，每个算法都要亲手跑一遍
3. **记笔记** — 每读完一个模块，写 3 句话总结：输入/输出/核心思想
4. **带着问题学** — 不要从第一页开始看教材，而是遇到不懂的概念再去查

---

## 阶段1：读懂代码（第1-2周）

### 目标
能画出三个包的节点关系图，能解释每个模块的输入输出。

### 任务清单

#### Week 1: 手势识别 + 控制

| 天 | 读什么 | 要回答的问题 | 产出 |
|----|--------|-------------|------|
| D1 | `gesture_definitions.py` | MediaPipe 21个关键点分别在哪？怎么判断手指伸直/弯曲？ | 手画手部关键点图 |
| D2 | `gesture_recognizer.py` | 订阅什么？发布什么？debounce 是怎么实现的？ | 画数据流图 |
| D3 | `gesture_commander.py` | 状态机有哪些状态？转换条件是什么？MAVROS 的 topic/service 怎么用？ | 画状态机图 |
| D4 | `gesture_velocity_controller.py` | 低通滤波的公式？死区的作用？sigmoid 映射的直觉？ | 写伪代码 |
| D5 | `safety_monitor.py` + `diagnostics.py` | 安全机制有哪些？怎么实现自动紧急降落？ | 列安全检查清单 |

#### Week 2: 导航 + 视觉

| 天 | 读什么 | 要回答的问题 | 产出 |
|----|--------|-------------|------|
| D6 | `coordinate_utils.py` | ENU/NED/Body 的区别？MAVROS 用哪个坐标系？ | 画三个坐标系的关系图 |
| D7 | `path_planner.py` | A* 的 f=g+h 含义？RRT 怎么扩展节点？RRT* 怎么优化？ | 手写 A* 在 5x5 网格上的执行过程 |
| D8 | `dwa_planner.py` | 动态窗口怎么算？评价函数三个权重的含义？ | 画 DWA 流程图 |
| D9 | `camera_model.py` | 像素坐标→3D射线的推导？焦距的物理含义？ | 手算一个投影例子 |
| D10 | `kalman_tracker.py` | 预测步和更新步的公式？卡尔曼增益 K 的含义？ | 写出5个公式 |

### 每日笔记模板

```markdown
## [日期] [文件名]

**输入**: (这个模块接收什么数据)
**输出**: (这个模块输出什么数据)
**核心思想**: (用一句话概括)
**我不懂的**: (记录疑问，后面解决)
```

---

## 阶段2：跑通仿真（第3-4周）

### 目标
在 PX4 SITL 中用 MAVROS 控制仿真无人机，建立控制直觉。

### 前置准备

```bash
# 1. 安装 PX4 Autopilot
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash Tools/setup/ubuntu.sh  # 安装依赖
make px4_sitl_default gazebo  # 首次编译

# 2. 安装 MAVROS (如果还没装)
sudo apt install ros-humble-mavros ros-humble-mavros-msgs
pip install pymavlink
```

### 任务清单

#### Week 3: 基础操控

| 任务 | 做什么 | 学到什么 |
|------|--------|---------|
| T1 | 启动 SITL + MAVROS，用 `rostopic echo /mavros/state` 看状态 | MAVROS 通信机制 |
| T2 | 用 Python 脚本发 `/mavros/cmd/arming` 解锁无人机 | MAVLink 服务调用 |
| T3 | 切 GUIDED 模式，发 `/mavros/setpoint_position/local` 起飞到 5m | 位置控制 |
| T4 | 发速度命令 `/mavros/setpoint_velocity/cmd_vel` 让无人机前进 | 速度控制 |
| T5 | 切 LAND 模式降落，观察降落过程 | 模式切换 |

#### Week 4: 高级操作

| 任务 | 做什么 | 学到什么 |
|------|--------|---------|
| T6 | 用航点列表让无人机按航线飞行 | 航点协议 |
| T7 | 在 Gazebo 中加障碍物，测试 DWA 避障 | 避障实际效果 |
| T8 | 调 PID 参数：把 P 调大/调小，观察振荡/响应慢 | PID 直觉 |
| T9 | 测试手势控制闭环：做手势 → 仿真无人机动作 | 端到端流程 |
| T10 | 断开 MAVROS，观察安全监控是否触发紧急降落 | 安全机制验证 |

### 关键命令速查

```bash
# 启动 PX4 SITL
cd ~/PX4-Autopilot && make px4_sitl_default gazebo

# 启动 MAVROS (连接 SITL)
ros2 launch mavros px4.launch.py fcu_url:=udp://14540@14556

# 查看话题
ros2 topic list
ros2 topic echo /mavros/state

# 手动解锁
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

# 切 GUIDED 模式
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'GUIDED'}"
```

---

## 阶段3：深入算法（第5-8周）

### 目标
面试时能手推公式，能解释算法原理，能讨论优缺点。

### 学习路线

#### Week 5: PID 控制

**学什么:**
- P (比例): 反应强度，越大响应越快但会振荡
- I (积分): 消除稳态误差，但会导致超调
- D (微分): 抑制振荡，但对噪声敏感
- 串联 PID: 角速度环(内环) → 角度环(外环) → 位置环(最外)

**实践:**
```
在 SITL 中做实验:
1. 只用 P 控制，观察振荡
2. 加 D，观察振荡减弱
3. 加 I，观察稳态误差消除
4. 记录每组参数的响应曲线
```

**资源:**
- B站: 「DR_CAN_PID教程」(中文，直觉好)
- 书: 《自动控制原理》胡寿松 第1-3章

#### Week 6: 卡尔曼滤波

**要手推的5个公式:**
```
预测:
  x̂⁻ = F * x̂ + B * u        (状态预测)
  P⁻ = F * P * Fᵀ + Q        (协方差预测)

更新:
  K = P⁻ * Hᵀ * (H * P⁻ * Hᵀ + R)⁻¹  (卡尔曼增益)
  x̂ = x̂⁻ + K * (z - H * x̂⁻)          (状态更新)
  P = (I - K * H) * P⁻                   (协方差更新)
```

**直觉理解:**
- K 大 → 更相信观测
- K 小 → 更相信预测
- Q 大 → 预测不确定 → K 大 → 更依赖观测
- R 大 → 观测不确定 → K 小 → 更依赖预测

**实践:**
```python
# 读 kalman_tracker.py，对照公式理解每行代码
# 然后做实验：加不同程度的噪声，观察滤波效果
```

**资源:**
- YouTube: 3Blue1Brown 「But what is a Kalman filter?」
- B站: 「DR_CAN_卡尔曼滤波」

#### Week 7: 路径规划

**要理解的:**
- A*: f(n) = g(n) + h(n)，时间复杂度 O(b^d)
- RRT: 概率完备但不最优
- RRT*: 渐近最优，rewire 操作
- DWA: 局部规划，直接输出控制命令

**面试常见问题:**
1. A* 和 Dijkstra 的区别？→ A* 有启发函数
2. RRT 和 RRT* 的区别？→ RRT* 有 rewire 优化
3. 全局规划和局部规划的区别？→ 全局不考虑动态障碍物
4. DWA 的评价函数怎么设计？→ heading + dist + velocity

**实践:**
```
1. 在 test_path_planner.py 中添加新的测试场景
2. 对比 A* 和 RRT 在同一地图上的路径质量
3. 可视化 DWA 的速度空间采样
```

#### Week 8: 相机模型与视觉

**要理解的:**
- 针孔模型: u = fx * X/Z + cx
- 畸变: 径向畸变 k1, k2
- 像素→射线: 从 2D 恢复 3D 方向
- 视觉伺服: IBVS vs PBVS

**实践:**
```
1. 手算: 给定相机内参，把像素 (320, 240) 投影到 3D
2. 读 camera_model.py，理解代码与公式的对应
3. 用 OpenCV 标定自己的摄像头，得到内参
```

---

## 阶段4：项目打磨（第9-12周）

### 目标
做出可以写进简历、可以演示的完整项目。

### 产出清单

| 产出 | 内容 | 用途 |
|------|------|------|
| 演示视频 | 3 个项目各 2 分钟运行录屏 | 面试展示 |
| 技术文档 | 架构图 + 算法原理 + 设计决策 | GitHub README |
| 简历描述 | 3-5 行精炼项目描述 | 简历 |
| 面试准备 | 每个项目准备 5 个可能被问的问题 | 面试 |

### 简历项目描述模板

```
无人机自主飞行系统 (ROS2 + MAVROS + MediaPipe)
- 设计并实现了手势识别控制系统，基于 MediaPipe Hands 实现 4 种手势的实时识别，
  通过 MAVROS 协议控制 ArduCopter 飞控，支持离散命令和连续速度两种控制模式
- 实现了 A*/RRT/RRT* 全局路径规划和 DWA 局部避障算法，支持 2D 栅格地图的
  实时路径搜索和动态障碍物规避
- 开发了基于 YOLOv8 和卡尔曼滤波的视觉目标跟踪系统，支持多目标跟踪和
  PID 视觉伺服控制，实现无人机自主跟随地面目标
```

### 面试准备问题

**项目相关:**
1. 你的手势识别系统怎么处理误触发？→ debounce + 置信度阈值 + 安全监控
2. DWA 和 A* 的区别？什么时候用哪个？→ 全局 vs 局部
3. 卡尔曼滤波的预测和更新分别做了什么？→ 手推公式
4. 你的安全机制有哪些？→ 电量/连接/心跳/自动降落
5. 为什么选择 MediaPipe 而不是 YOLO？→ 手部关键点 vs 目标检测，不同任务

**基础知识:**
6. ROS2 的 Topic/Service/Action 区别？
7. MAVLink 协议的基本结构？
8. PID 参数怎么调？
9. 坐标系变换怎么表示？→ 旋转矩阵/四元数
10. 什么是 SLAM？你了解哪些 SLAM 算法？

---

## 推荐资源

### 视频课程

| 资源 | 内容 | 平台 |
|------|------|------|
| DR_CAN 系列 | PID、卡尔曼、状态空间 | B站 |
| 3Blue1Brown | 卡尔曼滤波直觉 | YouTube |
| 古月居 ROS2 教程 | ROS2 从入门到实战 | B站 |
| MIT 16.06 | 自动控制原理 | OCW |

### 书籍

| 书名 | 用途 | 难度 |
|------|------|------|
| 《自动控制原理》胡寿松 | PID、状态空间 | 入门 |
| 《概率机器人》 | 卡尔曼滤波、SLAM | 进阶 |
| 《多旋翼飞行器设计与控制》高飞 | 飞控算法全景 | 进阶 |
| 《Multiple View Geometry》 | 相机模型、多视图几何 | 高级 |

### 开源项目

| 项目 | 星标 | 学什么 |
|------|------|--------|
| ArduPilot | 15k | 飞控固件、PID 调参、EKF |
| PX4-Autopilot | 11.6k | 模块化架构、uORB |
| ZJU ego-planner | 2.4k | 轨迹优化 |
| HKUST VINS-Fusion | 4.5k | VIO、传感器融合 |
| open_vins | 2.9k | 模块化 VIO |

---

## 每周自检

每周日花 30 分钟回答：

1. 这周学了什么新概念？能用一句话解释吗？
2. 这周写了多少行代码？跑了几个实验？
3. 有什么不懂的？记录下来下周解决。
4. 离 3 个月目标还有多远？需要调整计划吗？

---

> 学习不是线性的。遇到不懂的很正常，记下来，继续往前走。
> 很多概念会在不同地方反复出现，每次都会理解更深一点。
