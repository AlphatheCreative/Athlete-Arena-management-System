# ============================================================
#  Smart Sports Tournament & Athlete Management System
#  FILE: app.py  —  Premium UI + C++ Bridge
#
#  Requirements:  pip install customtkinter
#  Run:           python app.py
#  Build:         run build.bat
# ============================================================

import customtkinter as ctk
import subprocess
import os
import sys
import time
import json

# ─────────────────────────────────────────────────────────────
#  PATH RESOLUTION
#  When frozen by PyInstaller (inside .exe), bundled files
#  live in sys._MEIPASS (temp, read-only).
#  Writable data files (session.json, input.txt, output.txt)
#  always sit next to the .exe so they survive across runs.
# ─────────────────────────────────────────────────────────────

def resource_path(filename):
    """Bundled read-only file (engine.exe lives here when frozen)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def data_path(filename):
    """Writable file — always beside the .exe (or beside app.py in dev)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


# ─────────────────────────────────────────────────────────────
#  SECTION 1 — C++ BRIDGE
# ─────────────────────────────────────────────────────────────

ENGINE     = resource_path("engine.exe")
STATE_FILE = data_path("session.json")
INPUT_TXT  = data_path("input.txt")
OUTPUT_TXT = data_path("output.txt")

def run_engine(commands):
    try:
        with open(INPUT_TXT, "w") as f:
            for cmd in commands:
                f.write(cmd.strip() + "\n")

        result = subprocess.run(
            [ENGINE],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(INPUT_TXT),  # engine reads/writes here
        )

        if result.returncode != 0:
            return f"[Engine Error]\n{result.stderr}"
        if not os.path.exists(OUTPUT_TXT):
            return "[Error] output.txt was not created."
        with open(OUTPUT_TXT, "r") as f:
            return f.read().strip()

    except FileNotFoundError:
        return "[Error] Engine binary not found.\nRun build.bat to compile."
    except subprocess.TimeoutExpired:
        return "[Error] Engine timed out."
    except Exception as e:
        return f"[Unexpected Error] {e}"


# ─────────────────────────────────────────────────────────────
#  PERSISTENCE
# ─────────────────────────────────────────────────────────────

def save_session(roster_cmds, lb_cmds, q_cmds, bracket_cmds):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({
                "roster_cmds":  roster_cmds,
                "lb_cmds":      lb_cmds,
                "q_cmds":       q_cmds,
                "bracket_cmds": bracket_cmds,
            }, f, indent=2)
    except Exception as e:
        print(f"[Warning] Could not save session: {e}")

def load_session():
    if not os.path.exists(STATE_FILE):
        return [], [], [], []
    try:
        with open(STATE_FILE, "r") as f:
            s = json.load(f)
        return (s.get("roster_cmds",[]), s.get("lb_cmds",[]),
                s.get("q_cmds",[]),      s.get("bracket_cmds",[]))
    except Exception as e:
        print(f"[Warning] Could not load session: {e}")
        return [], [], [], []


# ─────────────────────────────────────────────────────────────
#  SECTION 2 — THEME
# ─────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_ROOT    = "#080e17"
BG_PANEL   = "#0d1520"
BG_CARD    = "#111c2d"
BG_INPUT   = "#0a1220"
C_NAVY     = "#1B3A6B"
C_STEEL    = "#2E75B6"
C_ACCENT   = "#4A9FD4"
C_GLOW     = "#5AB4E8"
C_SUCCESS  = "#27AE60"
C_ERROR    = "#C0392B"
C_TEXT     = "#E8EDF5"
C_MUTED    = "#6B7E99"
C_DIVIDER  = "#1a2a40"
C_BADGE_BG = "#0f2040"
C_BORDER   = "#1e3050"


# ─────────────────────────────────────────────────────────────
#  SECTION 3 — WIDGET HELPERS
# ─────────────────────────────────────────────────────────────

def section_card(parent, icon, title, sub, row):
    f = ctk.CTkFrame(parent, fg_color=C_BADGE_BG, corner_radius=10,
                     border_width=1, border_color=C_BORDER)
    f.grid(row=row, column=0, sticky="ew", padx=12, pady=(0,8))
    f.grid_columnconfigure(1, weight=1)
    badge = ctk.CTkFrame(f, fg_color=C_NAVY, corner_radius=8, width=40, height=40)
    badge.grid(row=0, column=0, rowspan=2, padx=(10,8), pady=8)
    badge.grid_propagate(False)
    ctk.CTkLabel(badge, text=icon, font=ctk.CTkFont(size=18)).place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(f, text=title,
                 font=ctk.CTkFont(family="Trebuchet MS", size=13, weight="bold"),
                 text_color=C_TEXT).grid(row=0, column=1, sticky="sw", pady=(8,0))
    ctk.CTkLabel(f, text=sub,
                 font=ctk.CTkFont(family="Trebuchet MS", size=9),
                 text_color=C_MUTED).grid(row=1, column=1, sticky="nw", pady=(0,8))

def field_lbl(parent, text, row):
    ctk.CTkLabel(parent, text=text.upper(),
                 font=ctk.CTkFont(family="Trebuchet MS", size=9, weight="bold"),
                 text_color=C_MUTED).grid(row=row, column=0, sticky="w", padx=16, pady=(8,1))

def mk_entry(parent, ph, row):
    e = ctk.CTkEntry(parent, placeholder_text=ph,
                     fg_color=BG_INPUT, border_color=C_BORDER, border_width=1,
                     text_color=C_TEXT, placeholder_text_color=C_MUTED,
                     font=ctk.CTkFont(family="Trebuchet MS", size=12),
                     corner_radius=8, height=38)
    e.grid(row=row, column=0, sticky="ew", padx=16, pady=(0,4))
    return e

def mk_btn(parent, text, cmd, row, color=C_STEEL):
    b = ctk.CTkButton(parent, text=text, command=cmd,
                      fg_color=color, hover_color=C_GLOW, text_color=C_TEXT,
                      font=ctk.CTkFont(family="Trebuchet MS", size=12, weight="bold"),
                      corner_radius=8, height=40)
    b.grid(row=row, column=0, sticky="ew", padx=16, pady=(2,8))
    return b

def mk_divider(parent, row):
    ctk.CTkFrame(parent, fg_color=C_DIVIDER, height=1).grid(
        row=row, column=0, sticky="ew", padx=10, pady=6)


# ─────────────────────────────────────────────────────────────
#  SECTION 4 — MAIN APP
# ─────────────────────────────────────────────────────────────

class SportsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Sports Tournament & Athlete Management System")
        self.geometry("1150x780")
        self.minsize(900, 620)
        self.configure(fg_color=BG_ROOT)

        # Custom icon
        icon = resource_path("icon.ico")
        if os.path.exists(icon):
            self.iconbitmap(icon)

        # Restore previous session
        self._roster_cmds, self._lb_cmds, \
        self._q_cmds, self._bracket_cmds = load_session()

        self._build_header()
        self._build_layout()
        self._build_statusbar()
        self._switch("rosters")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        save_session(self._roster_cmds, self._lb_cmds,
                     self._q_cmds, self._bracket_cmds)
        self.destroy()

    # ── HEADER ──────────────────────────────────────────────

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=C_NAVY, corner_radius=0, height=66)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        logo = ctk.CTkFrame(hdr, fg_color="#162e58", corner_radius=0, width=58)
        logo.pack(side="left", fill="y")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="⚽", font=ctk.CTkFont(size=28)
                     ).place(relx=0.5, rely=0.5, anchor="center")
        titl = ctk.CTkFrame(hdr, fg_color="transparent")
        titl.pack(side="left", padx=16, pady=8)
        ctk.CTkLabel(titl, text="SMART SPORTS SYSTEM",
                     font=ctk.CTkFont(family="Trebuchet MS", size=18, weight="bold"),
                     text_color=C_TEXT).pack(anchor="w")
        ctk.CTkLabel(titl, text="Tournament & Athlete Management  •  C++ DSA Engine  •  Python UI",
                     font=ctk.CTkFont(family="Trebuchet MS", size=10),
                     text_color=C_ACCENT).pack(anchor="w")
        badges = ctk.CTkFrame(hdr, fg_color="transparent")
        badges.pack(side="right", padx=20)
        for lbl, col in [("C++ Backend","#1B4A8A"),("Python UI","#1a5c3a"),("DSA Engine","#4a2080")]:
            p = ctk.CTkFrame(badges, fg_color=col, corner_radius=20, height=26)
            p.pack(side="left", padx=3)
            ctk.CTkLabel(p, text=lbl,
                         font=ctk.CTkFont(family="Trebuchet MS", size=10, weight="bold"),
                         text_color=C_TEXT).pack(padx=10, pady=4)
        ctk.CTkFrame(self, fg_color=C_STEEL, corner_radius=0, height=2).pack(fill="x")

    # ── LAYOUT ──────────────────────────────────────────────

    def _build_layout(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True)
        wrap.grid_columnconfigure(1, weight=1)
        wrap.grid_rowconfigure(0, weight=1)

        self._sidebar = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=0, width=210)
        self._sidebar.grid(row=0, column=0, sticky="ns")
        self._sidebar.grid_propagate(False)
        ctk.CTkLabel(self._sidebar, text="NAVIGATION",
                     font=ctk.CTkFont(family="Trebuchet MS", size=9, weight="bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=16, pady=(18,8))

        self._nav_btns = {}
        for key, icon, title, sub in [
            ("rosters","🏟","Team Rosters","Doubly Linked List"),
            ("leader", "🏆","Leaderboard", "Binary Search Tree"),
            ("tickets","🎟","Ticket Queue","FIFO Linked Queue"),
            ("bracket","📊","Tournament Bracket","Graph + BFS"),
        ]:
            self._nav_btns[key] = self._make_nav(key, icon, title, sub)

        ctk.CTkFrame(self._sidebar, fg_color=C_DIVIDER, height=1).pack(fill="x", padx=12, pady=12)
        eng_card = ctk.CTkFrame(self._sidebar, fg_color=C_BADGE_BG, corner_radius=10,
                                border_width=1, border_color=C_BORDER)
        eng_card.pack(fill="x", padx=10, pady=(0,16))
        ctk.CTkLabel(eng_card, text="⚙  ENGINE STATUS",
                     font=ctk.CTkFont(family="Trebuchet MS", size=9, weight="bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=10, pady=(10,2))
        self._eng_lbl = ctk.CTkLabel(eng_card, text="● Ready",
                                     font=ctk.CTkFont(family="Trebuchet MS", size=12, weight="bold"),
                                     text_color=C_SUCCESS)
        self._eng_lbl.pack(anchor="w", padx=10, pady=(0,10))

        self._body = ctk.CTkFrame(wrap, fg_color=BG_ROOT, corner_radius=0)
        self._body.grid(row=0, column=1, sticky="nsew")

    def _make_nav(self, key, icon, title, sub):
        f = ctk.CTkFrame(self._sidebar, fg_color="transparent", cursor="hand2")
        f.pack(fill="x", padx=8, pady=2)
        f.grid_columnconfigure(1, weight=1)
        ibadge = ctk.CTkFrame(f, fg_color=C_NAVY, corner_radius=8, width=38, height=38)
        ibadge.grid(row=0, column=0, rowspan=2, padx=(6,8), pady=6)
        ibadge.grid_propagate(False)
        ctk.CTkLabel(ibadge, text=icon, font=ctk.CTkFont(size=16)
                     ).place(relx=0.5, rely=0.5, anchor="center")
        tl = ctk.CTkLabel(f, text=title,
                          font=ctk.CTkFont(family="Trebuchet MS", size=12, weight="bold"),
                          text_color=C_TEXT)
        tl.grid(row=0, column=1, sticky="sw")
        sl = ctk.CTkLabel(f, text=sub,
                          font=ctk.CTkFont(family="Trebuchet MS", size=9),
                          text_color=C_MUTED)
        sl.grid(row=1, column=1, sticky="nw")
        bar = ctk.CTkFrame(f, fg_color="transparent", width=4, corner_radius=2)
        bar.grid(row=0, column=2, rowspan=2, sticky="ns", padx=(4,0))
        f._bar = bar; f._ibadge = ibadge
        for w in [f, ibadge, tl, sl, bar]:
            w.bind("<Button-1>", lambda e, k=key: self._switch(k))
        return f

    def _switch(self, key):
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color=C_BADGE_BG)
                btn._bar.configure(fg_color=C_ACCENT, width=4)
                btn._ibadge.configure(fg_color=C_STEEL)
            else:
                btn.configure(fg_color="transparent")
                btn._bar.configure(fg_color="transparent")
                btn._ibadge.configure(fg_color=C_NAVY)
        for w in self._body.winfo_children():
            w.destroy()
        {"rosters":self._build_rosters,"leader":self._build_leader,
         "tickets":self._build_tickets,"bracket":self._build_bracket}[key]()

    # ── STATUS BAR ──────────────────────────────────────────

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        ctk.CTkFrame(bar, fg_color=C_STEEL, height=1).pack(fill="x", side="top")
        self._stat_lbl = ctk.CTkLabel(bar, text="System ready  •  All modules loaded",
                                      font=ctk.CTkFont(family="Trebuchet MS", size=9),
                                      text_color=C_MUTED)
        self._stat_lbl.pack(side="left", padx=14)
        ctk.CTkLabel(bar, text="C++ DSA Engine v1.0",
                     font=ctk.CTkFont(family="Trebuchet MS", size=9),
                     text_color=C_MUTED).pack(side="right", padx=14)

    def _set_status(self, msg, color=C_MUTED):
        self._stat_lbl.configure(text=msg, text_color=color)

    def _flash(self, ok=True):
        self._eng_lbl.configure(text="● Running...", text_color=C_ACCENT)
        self.after(700, lambda: self._eng_lbl.configure(text="● Ready", text_color=C_SUCCESS))

    def _show(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        is_err = text.startswith("ERROR") or text.startswith("[Error")
        box.tag_config("err",  foreground=C_ERROR)
        box.tag_config("head", foreground=C_ACCENT)
        box.tag_config("num",  foreground=C_GLOW)
        box.tag_config("ok",   foreground=C_TEXT)
        for line in text.split("\n"):
            if is_err:             box.insert("end", line+"\n","err")
            elif line.startswith("==="): box.insert("end", line+"\n","head")
            elif line.strip() and line.strip()[0].isdigit(): box.insert("end",line+"\n","num")
            else:                  box.insert("end", line+"\n","ok")
        box.configure(state="disabled")
        self._flash(not is_err)
        self._set_status(f"{'Error' if is_err else 'Success'}  •  {time.strftime('%H:%M:%S')}",
                         C_ERROR if is_err else C_SUCCESS)

    def _tab_title(self, icon, title, sub):
        f = ctk.CTkFrame(self._body, fg_color=C_NAVY, corner_radius=0, height=58)
        f.pack(fill="x"); f.pack_propagate(False); f.grid_columnconfigure(1, weight=1)
        badge = ctk.CTkFrame(f, fg_color=C_STEEL, corner_radius=10, width=40, height=40)
        badge.grid(row=0, column=0, padx=(14,10), pady=9); badge.grid_propagate(False)
        ctk.CTkLabel(badge, text=icon, font=ctk.CTkFont(size=18)).place(relx=0.5,rely=0.5,anchor="center")
        ctk.CTkLabel(f, text=title,
                     font=ctk.CTkFont(family="Trebuchet MS",size=16,weight="bold"),
                     text_color=C_TEXT).grid(row=0,column=1,sticky="w")
        ctk.CTkLabel(f, text=sub,
                     font=ctk.CTkFont(family="Trebuchet MS",size=10),
                     text_color=C_ACCENT).grid(row=0,column=2,sticky="e",padx=16)

    def _ctrl_scroll(self):
        outer = ctk.CTkFrame(self._body, fg_color=BG_CARD, corner_radius=0, width=288)
        outer.pack(side="left", fill="y"); outer.pack_propagate(False)
        sc = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                    scrollbar_button_color=C_BORDER,
                                    scrollbar_button_hover_color=C_STEEL)
        sc.pack(fill="both", expand=True); sc.grid_columnconfigure(0, weight=1)
        return sc

    def _out_panel(self):
        wrap = ctk.CTkFrame(self._body, fg_color=BG_PANEL, corner_radius=12,
                            border_width=1, border_color=C_BORDER)
        wrap.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        wrap.grid_rowconfigure(1, weight=1); wrap.grid_columnconfigure(0, weight=1)
        hdr = ctk.CTkFrame(wrap, fg_color=C_NAVY, corner_radius=0, height=40)
        hdr.grid(row=0, column=0, sticky="ew"); hdr.grid_columnconfigure(0, weight=1); hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="◉  ENGINE OUTPUT",
                     font=ctk.CTkFont(family="Trebuchet MS",size=10,weight="bold"),
                     text_color=C_ACCENT).grid(row=0,column=0,sticky="w",padx=14)
        ctk.CTkLabel(hdr, text="C++ RESULT",
                     font=ctk.CTkFont(family="Trebuchet MS",size=9),
                     text_color=C_MUTED).grid(row=0,column=1,sticky="e",padx=14)
        box = ctk.CTkTextbox(wrap, font=ctk.CTkFont(family="Consolas",size=13),
                             fg_color=BG_PANEL, text_color=C_TEXT,
                             corner_radius=0, border_width=0, wrap="word")
        box.grid(row=1, column=0, sticky="nsew"); box.configure(state="disabled")
        return box

    # ── TAB 1: ROSTERS ──────────────────────────────────────

    def _build_rosters(self):
        self._tab_title("🏟","Team Rosters","Doubly Linked List — O(1) insert, pointer-based traversal")
        ctrl = self._ctrl_scroll(); self.t_out = self._out_panel()
        section_card(ctrl,"➕","Create Team","Add new team to the league",0)
        field_lbl(ctrl,"Team Name",1); self.t_team = mk_entry(ctrl,"e.g. Warriors",2)
        mk_btn(ctrl,"🏟  Create Team",self._create_team,3,C_STEEL); mk_divider(ctrl,4)
        section_card(ctrl,"👤","Add Player","Insert node into doubly linked list",5)
        field_lbl(ctrl,"Team Name",6);  self.t_r_team = mk_entry(ctrl,"e.g. Warriors",7)
        field_lbl(ctrl,"Player Name",8); self.t_p_name = mk_entry(ctrl,"e.g. Ali Hassan",9)
        field_lbl(ctrl,"Player ID",10);  self.t_p_id   = mk_entry(ctrl,"e.g. 101",11)
        mk_btn(ctrl,"➕  Add Player",self._add_player,12,C_STEEL); mk_divider(ctrl,13)
        section_card(ctrl,"🗑","Remove Player","Delete node, update prev/next pointers",14)
        field_lbl(ctrl,"Team Name",15); self.t_rm_team = mk_entry(ctrl,"Team name",16)
        field_lbl(ctrl,"Player ID",17); self.t_rm_id   = mk_entry(ctrl,"Player ID",18)
        mk_btn(ctrl,"🗑  Remove Player",self._rem_player,19,"#8B2020"); mk_divider(ctrl,20)
        section_card(ctrl,"📋","View Roster","Traverse linked list, print all nodes",21)
        field_lbl(ctrl,"Team Name",22); self.t_lt_team = mk_entry(ctrl,"Team name",23)
        mk_btn(ctrl,"📋  Show Roster",self._list_roster,24,"#1a5c3a")
        if self._roster_cmds:
            self._show(self.t_out, run_engine(self._roster_cmds))

    def _create_team(self):
        n = self.t_team.get().strip()
        if not n: return
        self._roster_cmds.append(f"ADD_TEAM {n}")
        self._show(self.t_out, run_engine(self._roster_cmds))

    def _add_player(self):
        team=self.t_r_team.get().strip(); name=self.t_p_name.get().strip(); pid=self.t_p_id.get().strip()
        if not (team and name and pid): return
        self._roster_cmds += [f"ADD_TEAM {team}", f"ADD_PLAYER {team} {pid} {name}"]
        self._show(self.t_out, run_engine(self._roster_cmds))

    def _rem_player(self):
        team=self.t_rm_team.get().strip(); pid=self.t_rm_id.get().strip()
        if not (team and pid): return
        self._roster_cmds.append(f"REMOVE_PLAYER {team} {pid}")
        self._show(self.t_out, run_engine(self._roster_cmds))

    def _list_roster(self):
        team=self.t_lt_team.get().strip()
        if not team: return
        self._show(self.t_out, run_engine(self._roster_cmds + [f"LIST_ROSTER {team}"]))

    # ── TAB 2: LEADERBOARD ──────────────────────────────────

    def _build_leader(self):
        self._tab_title("🏆","Leaderboard","Binary Search Tree — O(log n) lookup, In-Order traversal ranking")
        ctrl = self._ctrl_scroll(); self.lb_out = self._out_panel()
        section_card(ctrl,"📥","Insert Athlete","Add to BST keyed by score",0)
        field_lbl(ctrl,"Athlete Name",1);      self.lb_name  = mk_entry(ctrl,"e.g. Ahmed Raza",2)
        field_lbl(ctrl,"Performance Score",3); self.lb_score = mk_entry(ctrl,"e.g. 950",4)
        mk_btn(ctrl,"📥  Insert Score",self._lb_insert,5,C_STEEL); mk_divider(ctrl,6)
        section_card(ctrl,"🏆","Rankings","In-Order BST traversal — highest first",7)
        mk_btn(ctrl,"🏆  Show Leaderboard",self._lb_show,8,"#4a2080")
        if self._lb_cmds:
            self._show(self.lb_out, run_engine(self._lb_cmds + ["SHOW_LEADERBOARD"]))

    def _lb_insert(self):
        name=self.lb_name.get().strip(); score=self.lb_score.get().strip()
        if not (name and score): return
        self._lb_cmds.append(f"INSERT_SCORE {name} {score}")
        self._show(self.lb_out, run_engine(self._lb_cmds + ["SHOW_LEADERBOARD"]))

    def _lb_show(self):
        if not self._lb_cmds: self._show(self.lb_out,"No athletes inserted yet."); return
        self._show(self.lb_out, run_engine(self._lb_cmds + ["SHOW_LEADERBOARD"]))

    # ── TAB 3: TICKET QUEUE ─────────────────────────────────

    def _build_tickets(self):
        self._tab_title("🎟","Ticket Queue","Linked Queue — FIFO, no starvation, O(1) enqueue/dequeue")
        ctrl = self._ctrl_scroll(); self.q_out = self._out_panel()
        section_card(ctrl,"➕","Join Queue","Enqueue customer at rear",0)
        field_lbl(ctrl,"Customer Name",1); self.q_name = mk_entry(ctrl,"e.g. Bilal Ahmed",2)
        mk_btn(ctrl,"➕  Join Queue",self._q_enqueue,3,C_STEEL); mk_divider(ctrl,4)
        section_card(ctrl,"✅","Issue Ticket","Dequeue from front — FIFO order",5)
        mk_btn(ctrl,"✅  Issue Ticket  (Dequeue)",self._q_dequeue,6,"#1a5c3a"); mk_divider(ctrl,7)
        section_card(ctrl,"👁","View Queue","Show all waiting customers in order",8)
        mk_btn(ctrl,"📋  Show Full Queue",self._q_show,9,"#4a2080")
        if self._q_cmds:
            self._show(self.q_out, run_engine(self._q_cmds + ["SHOW_QUEUE"]))

    def _q_enqueue(self):
        name=self.q_name.get().strip()
        if not name: return
        self._q_cmds.append(f"ENQUEUE {name}")
        self._show(self.q_out, run_engine(self._q_cmds + ["SHOW_QUEUE"]))

    def _q_dequeue(self):
        self._q_cmds.append("DEQUEUE")
        self._show(self.q_out, run_engine(self._q_cmds + ["SHOW_QUEUE"]))

    def _q_show(self):
        if not self._q_cmds: self._show(self.q_out,"Queue is empty."); return
        self._show(self.q_out, run_engine(self._q_cmds + ["SHOW_QUEUE"]))

    # ── TAB 4: BRACKET ──────────────────────────────────────

    def _build_bracket(self):
        self._tab_title("📊","Tournament Bracket","Directed Acyclic Graph + BFS — tier-by-tier match traversal")
        ctrl = self._ctrl_scroll(); self.br_out = self._out_panel()
        section_card(ctrl,"🥊","Add Match","Insert graph node with match label",0)
        field_lbl(ctrl,"Match Label",1); self.br_lbl = mk_entry(ctrl,"e.g. QF1: TeamA vs TeamB",2)
        mk_btn(ctrl,"🥊  Add Match Node",self._br_match,3,C_STEEL); mk_divider(ctrl,4)
        section_card(ctrl,"🔗","Connect Matches","Add directed edge  From → To",5)
        field_lbl(ctrl,"From Node Index",6); self.br_from = mk_entry(ctrl,"e.g. 0",7)
        field_lbl(ctrl,"To Node Index",8);   self.br_to   = mk_entry(ctrl,"e.g. 2",9)
        mk_btn(ctrl,"🔗  Add Edge",self._br_edge,10,C_STEEL); mk_divider(ctrl,11)
        section_card(ctrl,"📡","BFS Traversal","Display bracket round by round",12)
        field_lbl(ctrl,"Start Node Index",13); self.br_start = mk_entry(ctrl,"e.g. 0",14)
        mk_btn(ctrl,"📊  Run BFS → Show Bracket",self._br_bfs,15,"#4a2080")
        if self._bracket_cmds:
            self._show(self.br_out, run_engine(self._bracket_cmds + ["SHOW_BRACKET 0"]))

    def _br_match(self):
        lbl=self.br_lbl.get().strip()
        if not lbl: return
        self._bracket_cmds.append(f"ADD_MATCH {lbl}")
        self._show(self.br_out, run_engine(self._bracket_cmds).strip().split("\n")[-1])

    def _br_edge(self):
        frm=self.br_from.get().strip(); to=self.br_to.get().strip()
        if not (frm and to): return
        self._bracket_cmds.append(f"ADD_EDGE {frm} {to}")
        self._show(self.br_out, run_engine(self._bracket_cmds).strip().split("\n")[-1])

    def _br_bfs(self):
        start=self.br_start.get().strip() or "0"
        self._show(self.br_out, run_engine(self._bracket_cmds + [f"SHOW_BRACKET {start}"]))


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = SportsApp()
    app.mainloop()