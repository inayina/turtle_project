# ROS 2 Turtlesim 闭环导航控制项目

本项目基于 **Ubuntu 24.04** 与 **ROS 2 Jazzy** 开发，实现了一个完整的机器人自主导航任务链路。通过自定义 Service 与 Topic 通信，演示了从目标下发到闭环执行的标准 ROS 2 开发流程。

---

## 🎥 项目演示 (Project Demo)

> **[➔ 点击此处直接查看：演示动画 (GIF)](./turtle_demo.gif)**
>
> **[➔ 点击此处查看：1080P 高清演示视频 (MP4)](./turtle_navigation_demo.mp4)**
> 
> *注：由于 GitHub 预览限制，若动图加载失败，请点击上方链接跳转查看。*

---

## 🏗️ 系统架构 (System Architecture)

本项目采用解耦的节点设计，确保了任务调度、运动控制与环境反馈的逻辑清晰。

### 1. 节点通信计算图 (Computational Graph)

```mermaid
graph LR
    User[Client Node] -- "Service: SetGoal" --> Nav[Navigation Node]
    Obs[Obstacle Node] -- "Topic: /stop_signal" --> Nav
    Nav -- "Topic: /turtle1/cmd_vel" --> Sim[Turtlesim]
    Sim -- "Topic: /turtle1/pose" --> Nav

    style Nav fill:#3498db,stroke:#2980b9,color:#fff
    style Sim fill:#2ecc71,stroke:#27ae60,color:#fff
    style Obs fill:#f1c40f,stroke:#f39c12,color:#333
