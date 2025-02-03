# 🕊️ Flappy Bird AI - Reinforcement Learning & Multiplayer

This project is a **Flappy Bird AI** implementation using **Deep Reinforcement Learning (PPO)** along with **Multiplayer Flask Server** and **Dynamic Difficulty Adjustment using Neural Networks**.

---

## 📌 Features
✔️ **AI-powered gameplay** using PPO (Proximal Policy Optimization).  
✔️ **Multiplayer support** with Flask & Socket.IO.  
✔️ **SQLite Database** for storing high scores.  
✔️ **Neural Network** for adjusting game difficulty dynamically.  
✔️ **Power-ups and moving pipes** for enhanced gameplay experience.  

---

## 🛠 Installation & Setup

### 1️⃣ Clone the repository:
```bash
git clone https://github.com/vedant713/flappy-bird-ai.git
cd flappy-bird-ai
```

### 2️⃣ Install dependencies:
```bash
pip install pygame numpy opencv-python flask flask-socketio stable-baselines3 tensorflow gym sqlite3
```

### 3️⃣ Run the game:
```bash
python flappy_ai.py
```

This will start the game **AND** the multiplayer server.

---

## 🎮 Game Modes

### 🤖 AI Mode
- AI trains using **PPO (Proximal Policy Optimization)** to learn how to play Flappy Bird.

### 🏆 Multiplayer Mode
- **Flask & Socket.IO** enable multiplayer where players' scores sync in real time.

### 📊 Dynamic Difficulty
- A **neural network adjusts** pipe speed based on score to make the game progressively harder.

---

## 🚀 Deployment (Optional)
For continuous running, deploy on a server:
- **Using PythonAnywhere**
- **Using AWS Lambda**
- **Using Docker**

---

## 🔍 Technical Details

### 📡 Multiplayer API
- Flask Server running on port `5050`.
- WebSocket events for **real-time score updates**.

### 🧠 AI Training
- PPO algorithm from **Stable-Baselines3**.
- CNN-based policy network for processing game screen pixels.

### 📜 Database
- SQLite stores **top 10 high scores**.

---

## 📜 License
This project is **open-source** and available under the MIT License.

---

## ✨ Credits
- Developed by **Vedant**  
- **Pygame** for rendering game visuals  
- **Stable-Baselines3** for reinforcement learning  
- **Flask & Socket.IO** for multiplayer  

---

📬 For any issues, open an **[Issue](https://github.com/your-repo/flappy-bird-ai/issues)** in the repository!
