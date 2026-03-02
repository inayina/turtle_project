### 🤖 系统计算图 (Computational Graph)

```mermaid
graph TD
    Client[Client Node] -- "Service: SetGoal (x,y)" --> Nav[Navigation Node]
    Obs[Obstacle Node] -- "Topic: /stop_signal (Bool)" --> Nav
    Nav -- "Topic: /turtle1/cmd_vel (Twist)" --> Sim[Turtlesim]
    Sim -- "Topic: /turtle1/pose (Pose)" --> Nav
    
    style Nav fill:#3498db,stroke:#2980b9,color:#fff
    style Sim fill:#2ecc71,stroke:#27ae60,color:#fff
