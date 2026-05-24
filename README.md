# 🏟️ ArenaCore

> A desktop sports management system built in C++ & Python. Features team roster management (Doubly Linked List), athlete leaderboard (BST), ticket queue (FIFO), and tournament bracket traversal (Graph + BFS). All DSA implemented from scratch with raw pointers. Sleek CustomTkinter dark UI.

---

## 📁 Project Structure

```
ArenaCore/
├── engine.cpp       # C++ DSA backend — all data structures & algorithms
├── engine.exe       # Compiled binary (Windows)
├── app.py           # Python UI — CustomTkinter frontend + C++ bridge
├── session.json     # Auto-generated UI session state
├── input.txt        # Auto-generated — commands sent to engine
├── output.txt       # Auto-generated — results from engine
└── README.md        # This file
```

> `input.txt`, `output.txt`, `session.json`, and `data.dat` are **auto-generated at runtime**. You don't write them manually.

---

## ⚙️ Setup & Installation

### Step 1 — Compile the C++ Engine

**Windows**
```bash
g++ -o engine.exe engine.cpp
```

**Mac / Linux**
```bash
g++ -o engine engine.cpp
```

### Step 2 — Install Python Dependency

```bash
pip install customtkinter
```

### Step 3 — Run the App

```bash
python app.py
```

---

## 🧠 Features & Data Structures

### 🏟️ Tab 1 — Team Roster Management
**Data Structure:** Doubly Linked List (raw pointers)

| Operation | Complexity |
|-----------|-----------|
| Add Team | O(1) |
| Add Player | O(1) — insert at head |
| Remove Player | O(n) — traverse to find by ID |
| List Roster | O(n) — full traversal |

- Each team holds a doubly linked list of players
- Players store name and ID
- Teams are linked together in a singly linked team list
- `prev` and `next` pointers updated on every insert/delete

---

### 🏆 Tab 2 — Athlete Leaderboard
**Data Structure:** Binary Search Tree (raw pointers)

| Operation | Complexity |
|-----------|-----------|
| Insert Score | O(log n) average |
| Show Rankings | O(n) — reverse in-order traversal |

- BST keyed by performance score
- In-order traversal (right → root → left) produces descending ranking
- Rankings displayed with position number and score

---

### 🎟️ Tab 3 — Ticket Sales & Queue
**Data Structure:** Singly Linked Queue — FIFO (raw pointers)

| Operation | Complexity |
|-----------|-----------|
| Enqueue (Join Queue) | O(1) |
| Dequeue (Issue Ticket) | O(1) |
| Show Queue | O(n) |

- Maintains `front` and `rear` pointers for O(1) both ends
- Strict FIFO order — no starvation
- Queue size tracked as integer counter

---

### 📊 Tab 4 — Tournament Bracket
**Data Structure:** Adjacency List Graph + BFS (raw pointers)

| Operation | Complexity |
|-----------|-----------|
| Add Match Node | O(1) |
| Add Edge (connection) | O(1) |
| BFS Traversal | O(V + E) |

- Directed graph using adjacency list (linked edges per node)
- Each node = one match with a label (e.g. `QF1: Team A vs Team B`)
- BFS displays the bracket round by round
- Maximum 64 nodes supported

---

## 🔄 How the Bridge Works

```
User clicks button in UI
         │
         ▼
app.py writes commands ──► input.txt
         │
         ▼
app.py runs engine.exe (subprocess)
         │
         ▼
engine.cpp reads input.txt
    → executes DSA logic
    → writes output.txt
         │
         ▼
app.py reads output.txt ──► displays in UI
```

The Python UI and C++ engine communicate entirely through plain text files. This keeps the two layers completely decoupled.

---

## 💾 Persistence

| File | What it stores |
|------|---------------|
| `data.dat` | Full engine state — teams, players, scores, queue, graph |
| `session.json` | UI command history for each tab |

- On **startup**: engine loads `data.dat` and replays saved state
- On **shutdown**: engine saves current state back to `data.dat`
- UI saves its command lists to `session.json` so the interface restores on relaunch

---

## 🛠️ Technical Highlights

- **Zero STL containers** — all lists, trees, queues, and graphs use raw `new`/`delete` C++ pointers
- **File I/O bridge** — Python and C++ communicate through `input.txt` / `output.txt`
- **Session persistence** — both the engine state (`data.dat`) and UI state (`session.json`) survive app restarts
- **PyInstaller-ready** — `resource_path()` and `data_path()` helpers handle frozen `.exe` paths correctly
- **CustomTkinter dark UI** — navy/steel blue theme with a dedicated output panel per tab

---

## 📋 Supported Commands (engine.cpp)

| Command | Description |
|---------|-------------|
| `ADD_TEAM <name>` | Create a new team |
| `ADD_PLAYER <team> <id> <name>` | Add player to team |
| `REMOVE_PLAYER <team> <id>` | Remove player by ID |
| `LIST_ROSTER <team>` | Show all players in team |
| `INSERT_SCORE <name> <score>` | Add athlete to leaderboard |
| `SHOW_LEADERBOARD` | Display ranked leaderboard |
| `ENQUEUE <name>` | Add customer to ticket queue |
| `DEQUEUE` | Issue ticket to front of queue |
| `SHOW_QUEUE` | Display all waiting customers |
| `ADD_MATCH <label>` | Add match node to bracket graph |
| `ADD_EDGE <from> <to>` | Connect two match nodes |
| `SHOW_BRACKET <start>` | BFS traversal from start node |

---

## 🖥️ Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| customtkinter | Latest |
| g++ / MinGW | C++11 or later |

---

## 👤 Author

**Alpha** — CS & Electronics Student, COMSATS University Islamabad  
Built as a DSA course project demonstrating real-world application of data structures in a functional desktop application.

---

## 📄 License

This project is for educational purposes.
