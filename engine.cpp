// ============================================================
//  Smart Sports Tournament & Athlete Management System
//  FILE: engine.cpp  —  Complete C++ DSA Backend Engine
//
//  Contains:
//    1. PlayerNode     — Doubly Linked List  (Team Rosters)
//    2. BSTNode        — Binary Search Tree  (Leaderboard)
//    3. QueueNode      — Linked Queue        (Ticket System)
//    4. GraphNode      — Adjacency List      (Match Brackets)
//    5. SportsEngine   — Master controller class
//    6. main()         — Parses input.txt, writes output.txt
//
//  Persistence:
//    - On startup : loads data.dat (replays saved state)
//    - On shutdown: saves current state to data.dat
//
//  Compile:  g++ -o engine engine.cpp
//  Run:      ./engine   (Python calls this automatically)
// ============================================================

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

// ─────────────────────────────────────────────────────────────
//  SECTION 1 — DOUBLY LINKED LIST  (Team Rosters)
// ─────────────────────────────────────────────────────────────

struct PlayerNode {
    std::string playerName;
    int         playerID;
    PlayerNode* next;
    PlayerNode* prev;

    PlayerNode(std::string name, int id)
        : playerName(name), playerID(id), next(nullptr), prev(nullptr) {}
};

struct TeamRoster {
    std::string teamName;
    PlayerNode* head;
    TeamRoster* nextTeam;

    TeamRoster(std::string name)
        : teamName(name), head(nullptr), nextTeam(nullptr) {}
};

// ─────────────────────────────────────────────────────────────
//  SECTION 2 — BINARY SEARCH TREE  (Leaderboard)
// ─────────────────────────────────────────────────────────────

struct BSTNode {
    std::string athleteName;
    int         performanceScore;
    BSTNode*    left;
    BSTNode*    right;

    BSTNode(std::string name, int score)
        : athleteName(name), performanceScore(score),
          left(nullptr), right(nullptr) {}
};

// ─────────────────────────────────────────────────────────────
//  SECTION 3 — LINKED QUEUE  (Ticket System)
// ─────────────────────────────────────────────────────────────

struct QueueNode {
    std::string customerName;
    QueueNode*  next;

    QueueNode(std::string name)
        : customerName(name), next(nullptr) {}
};

// ─────────────────────────────────────────────────────────────
//  SECTION 4 — ADJACENCY LIST GRAPH  (Tournament Brackets)
// ─────────────────────────────────────────────────────────────

struct GraphEdge {
    int        toNode;
    GraphEdge* next;

    GraphEdge(int to) : toNode(to), next(nullptr) {}
};

struct GraphNode {
    std::string matchLabel;
    GraphEdge*  edges;

    GraphNode() : edges(nullptr) {}
};

// Simple integer queue used inside BFS
struct IntQueue {
    int  data[256];
    int  front, rear;

    IntQueue() : front(0), rear(0) {}
    bool empty()     { return front == rear; }
    void push(int v) { data[rear++] = v; }
    int  pop()       { return data[front++]; }
};

// ─────────────────────────────────────────────────────────────
//  SECTION 5 — SPORTS ENGINE  (Master Controller)
// ─────────────────────────────────────────────────────────────

class SportsEngine {
private:
    // --- Team Rosters ---
    TeamRoster* teamsHead;

    // --- Leaderboard (BST) ---
    BSTNode* statsRoot;

    // --- Ticket Queue ---
    QueueNode* queueFront;
    QueueNode* queueRear;
    int        queueSize;

    // --- Tournament Graph ---
    static const int MAX_NODES = 64;
    GraphNode  graph[MAX_NODES];
    int        nodeCount;
    bool       visited[MAX_NODES];

    // ── HELPERS ──────────────────────────────────────────────

    TeamRoster* findTeam(const std::string& name) {
        TeamRoster* cur = teamsHead;
        while (cur) {
            if (cur->teamName == name) return cur;
            cur = cur->nextTeam;
        }
        return nullptr;
    }

    BSTNode* bstInsert(BSTNode* root, const std::string& name, int score) {
        if (!root) return new BSTNode(name, score);
        if (score < root->performanceScore)
            root->left  = bstInsert(root->left,  name, score);
        else
            root->right = bstInsert(root->right, name, score);
        return root;
    }

    void bstInOrder(BSTNode* root, std::ostringstream& out, int& rank) {
        if (!root) return;
        bstInOrder(root->right, out, rank);
        out << rank++ << ". " << root->athleteName
            << " — Score: " << root->performanceScore << "\n";
        bstInOrder(root->left, out, rank);
    }

    // Collect all BST nodes into a vector (for saving)
    void bstCollect(BSTNode* root,
                    std::vector<std::pair<std::string,int>>& vec) {
        if (!root) return;
        vec.push_back({root->athleteName, root->performanceScore});
        bstCollect(root->left,  vec);
        bstCollect(root->right, vec);
    }

    void bstDestroy(BSTNode* root) {
        if (!root) return;
        bstDestroy(root->left);
        bstDestroy(root->right);
        delete root;
    }

    void rosterDestroy(PlayerNode* head) {
        while (head) {
            PlayerNode* tmp = head;
            head = head->next;
            delete tmp;
        }
    }

    void graphDestroyEdges(int node) {
        GraphEdge* e = graph[node].edges;
        while (e) {
            GraphEdge* tmp = e;
            e = e->next;
            delete tmp;
        }
        graph[node].edges = nullptr;
    }

public:
    SportsEngine()
        : teamsHead(nullptr), statsRoot(nullptr),
          queueFront(nullptr), queueRear(nullptr),
          queueSize(0), nodeCount(0) {
        for (int i = 0; i < MAX_NODES; i++) visited[i] = false;
    }

    ~SportsEngine() {
        while (teamsHead) {
            rosterDestroy(teamsHead->head);
            TeamRoster* tmp = teamsHead;
            teamsHead = teamsHead->nextTeam;
            delete tmp;
        }
        bstDestroy(statsRoot);
        while (queueFront) {
            QueueNode* tmp = queueFront;
            queueFront = queueFront->next;
            delete tmp;
        }
        for (int i = 0; i < nodeCount; i++)
            graphDestroyEdges(i);
    }

    // ── FEATURE 1: TEAM ROSTER ────────────────────────────────

    std::string addTeam(const std::string& teamName) {
        if (findTeam(teamName))
            return "ERROR: Team '" + teamName + "' already exists.";
        TeamRoster* t = new TeamRoster(teamName);
        t->nextTeam = teamsHead;
        teamsHead   = t;
        return "Team '" + teamName + "' created successfully.";
    }

    std::string addPlayer(const std::string& teamName,
                          const std::string& playerName, int playerID) {
        TeamRoster* team = findTeam(teamName);
        if (!team) return "ERROR: Team '" + teamName + "' not found.";

        PlayerNode* p = new PlayerNode(playerName, playerID);
        p->next = team->head;
        if (team->head) team->head->prev = p;
        team->head = p;
        return "Player '" + playerName + "' (ID:" + std::to_string(playerID)
               + ") added to " + teamName + ".";
    }

    std::string removePlayer(const std::string& teamName, int playerID) {
        TeamRoster* team = findTeam(teamName);
        if (!team) return "ERROR: Team '" + teamName + "' not found.";

        PlayerNode* cur = team->head;
        while (cur) {
            if (cur->playerID == playerID) {
                if (cur->prev) cur->prev->next = cur->next;
                else           team->head      = cur->next;
                if (cur->next) cur->next->prev = cur->prev;
                std::string name = cur->playerName;
                delete cur;
                return "Player '" + name + "' removed from " + teamName + ".";
            }
            cur = cur->next;
        }
        return "ERROR: Player ID " + std::to_string(playerID) + " not found.";
    }

    std::string listRoster(const std::string& teamName) {
        TeamRoster* team = findTeam(teamName);
        if (!team) return "ERROR: Team '" + teamName + "' not found.";

        PlayerNode* cur = team->head;
        if (!cur) return "Roster for " + teamName + " is empty.";

        std::ostringstream out;
        out << "=== Roster: " << teamName << " ===\n";
        while (cur) {
            out << "  [ID:" << cur->playerID << "] " << cur->playerName << "\n";
            cur = cur->next;
        }
        return out.str();
    }

    // ── FEATURE 2: LEADERBOARD (BST) ─────────────────────────

    std::string insertLeaderboard(const std::string& name, int score) {
        statsRoot = bstInsert(statsRoot, name, score);
        return "Athlete '" + name + "' inserted with score "
               + std::to_string(score) + ".";
    }

    std::string displayLeaderboard() {
        if (!statsRoot) return "Leaderboard is empty.";
        std::ostringstream out;
        out << "=== Leaderboard (Top Performers) ===\n";
        int rank = 1;
        bstInOrder(statsRoot, out, rank);
        return out.str();
    }

    // ── FEATURE 3: TICKET QUEUE ───────────────────────────────

    std::string enqueue(const std::string& customerName) {
        QueueNode* node = new QueueNode(customerName);
        if (!queueRear) {
            queueFront = queueRear = node;
        } else {
            queueRear->next = node;
            queueRear       = node;
        }
        queueSize++;
        return "'" + customerName + "' joined the ticket queue. "
               "Queue size: " + std::to_string(queueSize) + ".";
    }

    std::string dequeue() {
        if (!queueFront) return "ERROR: Ticket queue is empty.";
        std::string name = queueFront->customerName;
        QueueNode*  tmp  = queueFront;
        queueFront       = queueFront->next;
        if (!queueFront) queueRear = nullptr;
        delete tmp;
        queueSize--;
        return "Ticket issued to '" + name + "'. "
               "Remaining in queue: " + std::to_string(queueSize) + ".";
    }

    std::string showQueue() {
        if (!queueFront) return "Ticket queue is empty.";
        std::ostringstream out;
        out << "=== Ticket Queue (" << queueSize << " waiting) ===\n";
        QueueNode* cur = queueFront;
        int pos = 1;
        while (cur) {
            out << "  " << pos++ << ". " << cur->customerName << "\n";
            cur = cur->next;
        }
        return out.str();
    }

    // ── FEATURE 4: TOURNAMENT BRACKETS (Graph + BFS) ─────────

    std::string addMatch(const std::string& label) {
        if (nodeCount >= MAX_NODES)
            return "ERROR: Tournament bracket is full.";
        graph[nodeCount].matchLabel = label;
        nodeCount++;
        return "Match added: [Node " + std::to_string(nodeCount - 1)
               + "] " + label;
    }

    std::string addMatchEdge(int from, int to) {
        if (from < 0 || from >= nodeCount || to < 0 || to >= nodeCount)
            return "ERROR: Invalid node indices.";
        GraphEdge* e      = new GraphEdge(to);
        e->next           = graph[from].edges;
        graph[from].edges = e;
        return "Bracket edge added: Node " + std::to_string(from)
               + " → Node " + std::to_string(to);
    }

    std::string bfsTraversal(int startNode) {
        if (nodeCount == 0) return "No tournament matches added yet.";
        if (startNode < 0 || startNode >= nodeCount)
            return "ERROR: Invalid start node.";

        for (int i = 0; i < MAX_NODES; i++) visited[i] = false;

        std::ostringstream out;
        out << "=== Tournament Bracket (BFS from Node "
            << startNode << ") ===\n";

        IntQueue q;
        visited[startNode] = true;
        q.push(startNode);

        int level = 0;
        while (!q.empty()) {
            int levelSize = q.rear - q.front;
            out << "\n  Round " << level + 1 << ":\n";
            for (int i = 0; i < levelSize; i++) {
                int node = q.pop();
                out << "    [" << node << "] "
                    << graph[node].matchLabel << "\n";
                GraphEdge* e = graph[node].edges;
                while (e) {
                    if (!visited[e->toNode]) {
                        visited[e->toNode] = true;
                        q.push(e->toNode);
                    }
                    e = e->next;
                }
            }
            level++;
        }
        return out.str();
    }

    // ═══════════════════════════════════════════════════════════
    //  PERSISTENCE — saveState() & loadState()
    //
    //  Format of data.dat (plain text, one record per line):
    //
    //  TEAM   <teamName>
    //  PLAYER <teamName> <playerID> <playerName>
    //  SCORE  <athleteName> <score>
    //  QUEUE  <customerName>
    //  MATCH  <nodeIndex> <matchLabel>
    //  EDGE   <fromNode> <toNode>
    //
    //  Teams are written first so players can be re-attached.
    //  Match nodes are written in index order so edge indices
    //  stay consistent on reload.
    // ═══════════════════════════════════════════════════════════

    // ── SAVE ─────────────────────────────────────────────────
    void saveState(const std::string& filename = "data.dat") {
        std::ofstream f(filename);
        if (!f.is_open()) {
            std::cerr << "WARNING: Could not open " << filename
                      << " for saving.\n";
            return;
        }

        f << "# Sports Engine — Saved State\n";

        // 1. Teams & their players
        //    Walk team list in reverse so reload order matches original
        //    (teams were inserted at front, so last team added = teamsHead)
        //    Collect into a vector first so we can reverse easily.
        std::vector<TeamRoster*> teamVec;
        for (TeamRoster* t = teamsHead; t; t = t->nextTeam)
            teamVec.push_back(t);

        // Write in reverse so the first team created is reloaded first
        for (int i = (int)teamVec.size() - 1; i >= 0; i--) {
            TeamRoster* t = teamVec[i];
            f << "TEAM " << t->teamName << "\n";

            // Players were also inserted at front; collect & reverse
            std::vector<PlayerNode*> pVec;
            for (PlayerNode* p = t->head; p; p = p->next)
                pVec.push_back(p);

            for (int j = (int)pVec.size() - 1; j >= 0; j--) {
                PlayerNode* p = pVec[j];
                // Format: PLAYER <team> <id> <name>
                f << "PLAYER " << t->teamName << " "
                  << p->playerID << " " << p->playerName << "\n";
            }
        }

        // 2. Leaderboard (BST pre-order so tree shape is preserved on
        //    rebuild — though scores will re-balance naturally on insert)
        std::vector<std::pair<std::string,int>> scores;
        bstCollect(statsRoot, scores);
        for (auto& s : scores)
            f << "SCORE " << s.first << " " << s.second << "\n";

        // 3. Ticket Queue (front → rear order)
        for (QueueNode* cur = queueFront; cur; cur = cur->next)
            f << "QUEUE " << cur->customerName << "\n";

        // 4. Graph nodes (by index)
        for (int i = 0; i < nodeCount; i++)
            f << "MATCH " << i << " " << graph[i].matchLabel << "\n";

        // 5. Graph edges (adjacency list — each edge stored once)
        for (int i = 0; i < nodeCount; i++) {
            for (GraphEdge* e = graph[i].edges; e; e = e->next)
                f << "EDGE " << i << " " << e->toNode << "\n";
        }

        f.close();
        std::cout << "[Persistence] State saved to '" << filename << "'.\n";
    }

    // ── LOAD ─────────────────────────────────────────────────
    void loadState(const std::string& filename = "data.dat") {
        std::ifstream f(filename);
        if (!f.is_open()) {
            // No saved data yet — that's fine on first run
            std::cout << "[Persistence] No saved state found ('"
                      << filename << "'). Starting fresh.\n";
            return;
        }

        std::string line;
        int matchesLoaded = 0;   // track how many MATCH lines we've seen
                                 // so we can pre-populate nodeCount

        while (std::getline(f, line)) {
            if (line.empty() || line[0] == '#') continue;

            std::istringstream ss(line);
            std::string tag;
            ss >> tag;

            if (tag == "TEAM") {
                std::string name; ss >> name;
                // Silent insert — don't care about return message
                if (!findTeam(name)) {
                    TeamRoster* t = new TeamRoster(name);
                    t->nextTeam = teamsHead;
                    teamsHead   = t;
                }

            } else if (tag == "PLAYER") {
                std::string team, playerName; int id;
                ss >> team >> id >> playerName;
                // addPlayer handles "team not found" gracefully
                addPlayer(team, playerName, id);

            } else if (tag == "SCORE") {
                std::string name; int score;
                ss >> name >> score;
                statsRoot = bstInsert(statsRoot, name, score);

            } else if (tag == "QUEUE") {
                std::string name; ss >> name;
                QueueNode* node = new QueueNode(name);
                if (!queueRear) {
                    queueFront = queueRear = node;
                } else {
                    queueRear->next = node;
                    queueRear       = node;
                }
                queueSize++;

            } else if (tag == "MATCH") {
                // Format: MATCH <index> <label with spaces>
                int idx; ss >> idx;
                std::string label;
                std::getline(ss, label);           // rest of line is the label
                if (!label.empty() && label[0] == ' ')
                    label = label.substr(1);       // strip leading space

                // Ensure we have enough slots
                while (nodeCount <= idx) {
                    graph[nodeCount].matchLabel = "";
                    nodeCount++;
                }
                graph[idx].matchLabel = label;
                matchesLoaded++;

            } else if (tag == "EDGE") {
                int from, to; ss >> from >> to;
                // Silently add edge (bounds were valid when saved)
                if (from >= 0 && from < nodeCount &&
                    to   >= 0 && to   < nodeCount) {
                    GraphEdge* e      = new GraphEdge(to);
                    e->next           = graph[from].edges;
                    graph[from].edges = e;
                }
            }
        }

        f.close();
        std::cout << "[Persistence] State loaded from '" << filename << "'.\n";
    }
};

// ─────────────────────────────────────────────────────────────
//  SECTION 6 — MAIN  (File I/O Bridge)
//  1. Load previous state from data.dat
//  2. Process commands from input.txt → output.txt
//  3. Save updated state back to data.dat
// ─────────────────────────────────────────────────────────────

int main() {
    SportsEngine engine;

    // ── STEP 1: Restore previous session ─────────────────────
    engine.loadState("data.dat");

    // ── STEP 2: Process commands ──────────────────────────────
    std::ifstream inFile("input.txt");
    std::ofstream outFile("output.txt");

    if (!inFile.is_open()) {
        outFile << "ERROR: Could not open input.txt\n";
        // Still save before exit so prior state is not lost
        engine.saveState("data.dat");
        return 1;
    }

    std::string line;
    while (std::getline(inFile, line)) {
        if (line.empty() || line[0] == '#') continue;

        std::istringstream ss(line);
        std::string cmd;
        ss >> cmd;

        // ── Team Roster ───────────────────────────────────────
        if (cmd == "ADD_TEAM") {
            std::string name; ss >> name;
            outFile << engine.addTeam(name) << "\n";

        } else if (cmd == "ADD_PLAYER") {
            std::string team, player; int id;
            ss >> team >> id >> player;
            outFile << engine.addPlayer(team, player, id) << "\n";

        } else if (cmd == "REMOVE_PLAYER") {
            std::string team; int id;
            ss >> team >> id;
            outFile << engine.removePlayer(team, id) << "\n";

        } else if (cmd == "LIST_ROSTER") {
            std::string team; ss >> team;
            outFile << engine.listRoster(team) << "\n";

        // ── Leaderboard ───────────────────────────────────────
        } else if (cmd == "INSERT_SCORE") {
            std::string name; int score;
            ss >> name >> score;
            outFile << engine.insertLeaderboard(name, score) << "\n";

        } else if (cmd == "SHOW_LEADERBOARD") {
            outFile << engine.displayLeaderboard() << "\n";

        // ── Ticket Queue ──────────────────────────────────────
        } else if (cmd == "ENQUEUE") {
            std::string name; ss >> name;
            outFile << engine.enqueue(name) << "\n";

        } else if (cmd == "DEQUEUE") {
            outFile << engine.dequeue() << "\n";

        } else if (cmd == "SHOW_QUEUE") {
            outFile << engine.showQueue() << "\n";

        // ── Tournament Bracket ────────────────────────────────
        } else if (cmd == "ADD_MATCH") {
            std::string label; std::getline(ss, label);
            outFile << engine.addMatch(label) << "\n";

        } else if (cmd == "ADD_EDGE") {
            int from, to; ss >> from >> to;
            outFile << engine.addMatchEdge(from, to) << "\n";

        } else if (cmd == "SHOW_BRACKET") {
            int start; ss >> start;
            outFile << engine.bfsTraversal(start) << "\n";

        } else {
            outFile << "ERROR: Unknown command '" << cmd << "'\n";
        }
    }

    inFile.close();
    outFile.close();

    // ── STEP 3: Save updated state ────────────────────────────
    engine.saveState("data.dat");

    return 0;
}