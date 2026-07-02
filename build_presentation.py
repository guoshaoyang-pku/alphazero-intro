#!/usr/bin/env python3
"""Generate all diagram assets and the slide spec for AlphaGo Zero presentation."""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Arc
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

# ── Config ──────────────────────────────────────────────────────────────────
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

# Font
CN_FONT = "Noto Sans CJK SC"
EN_FONT = "Arial"
matplotlib.rcParams['font.sans-serif'] = [CN_FONT, 'STHeiti', 'Heiti TC', 'PingFang HK']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

# Colors
C_NAVY = "#0D1B3E"
C_BLUE = "#1565C0"
C_LIGHT_BLUE = "#42A5F5"
C_TEAL = "#00897B"
C_GOLD = "#E8A838"
C_RED = "#E53935"
C_GREEN = "#43A047"
C_ORANGE = "#FB8C00"
C_GRAY = "#9E9E9E"
C_LIGHT_GRAY = "#E0E0E0"
C_WHITE = "#FFFFFF"
C_BG = "#F8F9FA"
C_DARK_TEXT = "#1A1A2E"
C_PURPLE = "#7B1FA2"

DPI = 200

def save(fig, name):
    path = os.path.join(ASSET_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor(),
                edgecolor='none', pad_inches=0.15)
    plt.close(fig)
    print(f"  [+] {name}")
    return path

# ── 1. MCTS Four Phases ────────────────────────────────────────────────────
def draw_tree(ax, nodes, edges, highlight_path=None, new_node=None,
              rollout_path=None, show_stats=False, stats=None,
              updated_nodes=None):
    """Draw a small game tree on the given axes."""
    for (x1,y1), (x2,y2) in edges:
        style = '-'
        color = C_GRAY
        lw = 1.5
        if rollout_path and ((x1,y1),(x2,y2)) in rollout_path:
            style = '--'
            color = C_ORANGE
            lw = 2
        elif highlight_path and ((x1,y1),(x2,y2)) in highlight_path:
            color = C_BLUE
            lw = 2.5
        ax.plot([x1,x2], [y1,y2], style, color=color, lw=lw, zorder=1)

    for i, (x, y) in enumerate(nodes):
        color = C_LIGHT_GRAY
        ec = C_GRAY
        r = 0.12
        zorder = 2
        if new_node and (x,y) == new_node:
            color = C_GREEN
            ec = C_GREEN
            r = 0.13
            zorder = 3
        elif highlight_path:
            for (x1,y1),(x2,y2) in highlight_path:
                if (x,y) == (x1,y1) or (x,y) == (x2,y2):
                    color = C_BLUE
                    ec = C_BLUE
                    break
        elif updated_nodes and (x,y) in updated_nodes:
            color = C_RED
            ec = C_RED

        circle = plt.Circle((x,y), r, fc=color, ec=ec, lw=1.5, zorder=zorder)
        ax.add_patch(circle)

        if show_stats and stats and (x,y) in stats:
            w, n = stats[(x,y)]
            ax.text(x, y, f"{w}/{n}", fontsize=6, ha='center', va='center',
                    color=C_WHITE, fontweight='bold', zorder=4)

    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-0.3, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')

def create_mcts_phases():
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), facecolor=C_WHITE)
    fig.patch.set_facecolor(C_WHITE)

    # Tree structure
    nodes = [(0.5,1.1), (0.2,0.7), (0.8,0.7), (0.0,0.3), (0.3,0.3),
             (0.65,0.3), (1.0,0.3)]
    edges = [((0.5,1.1),(0.2,0.7)), ((0.5,1.1),(0.8,0.7)),
             ((0.2,0.7),(0.0,0.3)), ((0.2,0.7),(0.3,0.3)),
             ((0.8,0.7),(0.65,0.3)), ((0.8,0.7),(1.0,0.3))]

    # Phase 1: Selection
    ax = axes[0]
    sel_path = [((0.5,1.1),(0.8,0.7)), ((0.8,0.7),(1.0,0.3))]
    draw_tree(ax, nodes, edges, highlight_path=sel_path)
    ax.set_title("Selection\n选择", fontsize=13, fontweight='bold', color=C_BLUE, pad=8)
    ax.text(0.5, -0.15, "UCT选择最优路径", fontsize=9, ha='center', color=C_DARK_TEXT)

    # Phase 2: Expansion
    ax = axes[1]
    nodes2 = nodes + [(1.1, -0.05)]
    edges2 = edges + [((1.0,0.3),(1.1,-0.05))]
    sel_path2 = [((0.5,1.1),(0.8,0.7)), ((0.8,0.7),(1.0,0.3)), ((1.0,0.3),(1.1,-0.05))]
    draw_tree(ax, nodes2, edges2, highlight_path=sel_path2, new_node=(1.1,-0.05))
    ax.set_title("Expansion\n扩展", fontsize=13, fontweight='bold', color=C_GREEN, pad=8)
    ax.text(0.5, -0.15, "添加新节点", fontsize=9, ha='center', color=C_DARK_TEXT)

    # Phase 3: Simulation
    ax = axes[2]
    nodes3 = nodes2 + [(1.15, -0.4), (1.05, -0.75)]
    edges3 = edges2 + [((1.1,-0.05),(1.15,-0.4)), ((1.15,-0.4),(1.05,-0.75))]
    roll_path = [((1.1,-0.05),(1.15,-0.4)), ((1.15,-0.4),(1.05,-0.75))]
    draw_tree(ax, nodes3, edges3, new_node=(1.1,-0.05), rollout_path=roll_path)
    ax.set_title("Simulation\n模拟", fontsize=13, fontweight='bold', color=C_ORANGE, pad=8)
    ax.text(0.5, -0.15, "随机模拟至终局", fontsize=9, ha='center', color=C_DARK_TEXT)
    ax.text(1.05, -0.9, "Win!", fontsize=9, ha='center', color=C_GREEN, fontweight='bold')
    ax.set_ylim(-1.0, 1.3)

    # Phase 4: Backpropagation
    ax = axes[3]
    updated = [(0.5,1.1), (0.8,0.7), (1.0,0.3)]
    stats = {(0.5,1.1): (7,10), (0.8,0.7): (5,7), (1.0,0.3): (3,4),
             (0.2,0.7): (2,3), (0.0,0.3): (1,1), (0.3,0.3): (1,2),
             (0.65,0.3): (2,3)}
    draw_tree(ax, nodes, edges, show_stats=True, stats=stats, updated_nodes=updated)
    ax.set_title("Backpropagation\n回传", fontsize=13, fontweight='bold', color=C_RED, pad=8)
    ax.text(0.5, -0.15, "更新路径上的统计量", fontsize=9, ha='center', color=C_DARK_TEXT)

    # Arrows between phases
    for i in range(3):
        fig.text(0.265 + i*0.24, 0.5, "→", fontsize=28, ha='center', va='center',
                 color=C_GOLD, fontweight='bold')

    plt.tight_layout(pad=1.5)
    save(fig, "mcts_phases.png")

# ── 2. Game Complexity Comparison ──────────────────────────────────────────
def create_complexity():
    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=C_WHITE)
    games = ['井字棋\nTic-Tac-Toe', '跳棋\nCheckers', '国际象棋\nChess', '围棋\nGo']
    complexity = [3, 21, 47, 170]
    colors = [C_TEAL, C_BLUE, C_GOLD, C_RED]

    bars = ax.barh(range(len(games)), complexity, color=colors, height=0.55,
                   edgecolor=[c for c in colors], linewidth=1.5, alpha=0.85)

    ax.set_yticks(range(len(games)))
    ax.set_yticklabels(games, fontsize=13, fontweight='bold', color=C_DARK_TEXT)
    ax.set_xlabel("状态空间复杂度 (10的幂次)", fontsize=13, color=C_DARK_TEXT, labelpad=10)

    for i, (bar, val) in enumerate(zip(bars, complexity)):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'$10^{{{val}}}$', fontsize=16, va='center', fontweight='bold',
                color=colors[i])

    ax.set_xlim(0, 200)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)

    # Annotation
    ax.annotate('宇宙中原子数 ≈ $10^{80}$', xy=(80, 2.7), fontsize=11,
                color=C_GRAY, style='italic')
    ax.axvline(x=80, color=C_GRAY, linestyle=':', alpha=0.5)

    plt.tight_layout()
    save(fig, "complexity.png")

# ── 3. Neural Network Architecture ────────────────────────────────────────
def create_nn_arch():
    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor=C_WHITE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    def draw_block(x, y, w, h, text, color, text_color=C_WHITE, fontsize=12):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              fc=color, ec=color, alpha=0.9, zorder=2)
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, text, fontsize=fontsize, ha='center', va='center',
                color=text_color, fontweight='bold', zorder=3)

    def draw_arrow_v(x, y1, y2, color=C_GRAY):
        ax.annotate('', xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))

    # Input
    draw_block(2.5, 8.8, 5, 0.7, "输入: s  (棋盘状态 19×19×17)", C_NAVY)
    draw_arrow_v(5, 8.7, 8.1, C_NAVY)

    # Conv layer
    draw_block(3, 7.3, 4, 0.7, "卷积层 256 filters, 3×3", C_BLUE)
    draw_arrow_v(5, 7.2, 6.6, C_BLUE)

    # ResNet blocks
    draw_block(2.5, 5.0, 5, 1.5, "残差网络 (ResNet)\n19 或 39 个残差块\nBatchNorm + ReLU",
               C_TEAL, fontsize=12)
    draw_arrow_v(5, 4.9, 4.3, C_TEAL)

    # Split
    ax.plot([5, 5], [4.3, 3.9], '-', color=C_GRAY, lw=2)
    ax.plot([3, 7], [3.9, 3.9], '-', color=C_GRAY, lw=2)
    ax.plot([3, 3], [3.9, 3.5], '-', color=C_GRAY, lw=2)
    ax.plot([7, 7], [3.9, 3.5], '-', color=C_GRAY, lw=2)

    # Policy head
    draw_block(1.2, 2.6, 3.6, 0.8, "策略头 (Policy Head)\nConv → FC → Softmax", C_GOLD, C_DARK_TEXT, 11)
    draw_arrow_v(3, 2.5, 1.9, C_GOLD)
    draw_block(1.5, 1.1, 3, 0.7, "p = Pr(a|s)\n362维概率向量", C_GOLD, C_DARK_TEXT, 11)

    # Value head
    draw_block(5.2, 2.6, 3.6, 0.8, "价值头 (Value Head)\nConv → FC → Tanh", C_RED, C_WHITE, 11)
    draw_arrow_v(7, 2.5, 1.9, C_RED)
    draw_block(5.5, 1.1, 3, 0.7, "v = V(s)\n标量 ∈ [-1, 1]", C_RED, C_WHITE, 11)

    # Labels
    ax.text(3, 0.5, "下一步走哪？", fontsize=11, ha='center', color=C_GOLD,
            style='italic', fontweight='bold')
    ax.text(7, 0.5, "当前局面谁赢？", fontsize=11, ha='center', color=C_RED,
            style='italic', fontweight='bold')

    # Title annotation
    ax.text(5, 9.8, "双头神经网络  $f_\\theta(s) = (\\mathbf{p}, v)$",
            fontsize=16, ha='center', va='center', color=C_NAVY, fontweight='bold')

    plt.tight_layout()
    save(fig, "nn_arch.png")

# ── 4. Self-Play Training Loop ────────────────────────────────────────────
def create_self_play_loop():
    fig, ax = plt.subplots(figsize=(9, 6), facecolor=C_WHITE)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3, 3.5)
    ax.axis('off')
    ax.set_aspect('equal')

    # Three main components at triangle vertices
    r = 2.0
    angles = [90, 210, 330]  # top, bottom-left, bottom-right
    positions = [(r*np.cos(np.radians(a)), r*np.sin(np.radians(a))) for a in angles]

    labels = [
        ("神经网络\n$f_\\theta$", C_BLUE),
        ("自我对弈\n生成数据", C_TEAL),
        ("MCTS\n搜索", C_GOLD),
    ]

    box_w, box_h = 1.8, 1.0
    for (x, y), (label, color) in zip(positions, labels):
        rect = FancyBboxPatch((x-box_w/2, y-box_h/2), box_w, box_h,
                              boxstyle="round,pad=0.15", fc=color, ec=color,
                              alpha=0.9, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=13, ha='center', va='center',
                color=C_WHITE, fontweight='bold', zorder=4)

    # Curved arrows between components
    arrow_style = "Simple,tail_width=3,head_width=12,head_length=8"

    # Neural Network → MCTS (top → bottom-right)
    ax.annotate('', xy=(positions[2][0]-0.3, positions[2][1]+0.6),
                xytext=(positions[0][0]+0.7, positions[0][1]-0.5),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5,
                               connectionstyle="arc3,rad=-0.3"))
    ax.text(1.8, 1.0, "提供 p, v\n引导搜索", fontsize=10, ha='center',
            color=C_NAVY, style='italic')

    # MCTS → Self-play (bottom-right → bottom-left)
    ax.annotate('', xy=(positions[1][0]+0.9, positions[1][1]),
                xytext=(positions[2][0]-0.9, positions[2][1]),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5,
                               connectionstyle="arc3,rad=-0.3"))
    ax.text(0, -2.5, "搜索策略 π\n选择落子", fontsize=10, ha='center',
            color=C_NAVY, style='italic')

    # Self-play → Neural Network (bottom-left → top)
    ax.annotate('', xy=(positions[0][0]-0.7, positions[0][1]-0.5),
                xytext=(positions[1][0]+0.3, positions[1][1]+0.6),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5,
                               connectionstyle="arc3,rad=-0.3"))
    ax.text(-1.8, 1.0, "训练数据\n$(s, \\pi, z)$", fontsize=10, ha='center',
            color=C_NAVY, style='italic')

    # Title
    ax.text(0, 3.3, "AlphaGo Zero 自我学习循环", fontsize=16,
            ha='center', fontweight='bold', color=C_NAVY)

    plt.tight_layout()
    save(fig, "self_play_loop.png")

# ── 5. TD vs MC Comparison ────────────────────────────────────────────────
def create_td_vs_mc():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 4), facecolor=C_WHITE)

    def draw_trajectory(ax, title, color, backup_type):
        ax.set_xlim(-0.5, 5.5)
        ax.set_ylim(-0.5, 2)
        ax.axis('off')

        states = [(i, 1) for i in range(6)]

        # Draw states
        for i, (x, y) in enumerate(states):
            if i < 5:
                ax.plot([x+0.2, x+0.8], [y, y], '-', color=C_LIGHT_GRAY, lw=1.5)
                ax.text(x+0.5, y+0.15, f'$r_{{{i+1}}}$', fontsize=8, ha='center',
                        color=C_GRAY)

            fc = C_LIGHT_GRAY
            if backup_type == 'mc':
                fc = color if i > 0 else color
            elif backup_type == 'td0':
                fc = color if i <= 1 else C_LIGHT_GRAY
            elif backup_type == 'tdl':
                alpha_val = max(0.2, 1 - i*0.2)
                fc = color

            circle = plt.Circle((x, y), 0.18, fc=fc if (
                (backup_type == 'mc') or
                (backup_type == 'td0' and i <= 1) or
                (backup_type == 'tdl')
            ) else C_LIGHT_GRAY,
                ec=C_GRAY, lw=1.5, zorder=2,
                alpha=1.0 if backup_type != 'tdl' else max(0.3, 1-i*0.15))
            ax.add_patch(circle)

            label = f'$S_{{{i}}}$' if i < 5 else '$S_T$'
            ax.text(x, y, label, fontsize=9, ha='center', va='center',
                    color=C_WHITE if (
                        (backup_type == 'mc') or
                        (backup_type == 'td0' and i <= 1) or
                        (backup_type == 'tdl')
                    ) else C_DARK_TEXT,
                    fontweight='bold', zorder=3)

        # Terminal marker
        if backup_type == 'mc':
            ax.text(5, 0.5, '$G_t$', fontsize=12, ha='center', color=color, fontweight='bold')
            # Curved arrow from terminal back to start
            ax.annotate('', xy=(0, 0.7), xytext=(5, 0.7),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                       connectionstyle='arc3,rad=0.4'))
        elif backup_type == 'td0':
            ax.text(1, 0.4, '$r_1 + \\gamma V(S_1)$', fontsize=10, ha='center',
                    color=color, fontweight='bold')
            ax.annotate('', xy=(0, 0.7), xytext=(1, 0.7),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
        elif backup_type == 'tdl':
            ax.text(2.5, 0.3, '$\\lambda$-加权回溯', fontsize=10, ha='center',
                    color=color, fontweight='bold')
            ax.annotate('', xy=(0, 0.65), xytext=(4, 0.65),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                       connectionstyle='arc3,rad=0.3',
                                       linestyle='--'))

        ax.set_title(title, fontsize=14, fontweight='bold', color=color, pad=15)

    draw_trajectory(ax1, "蒙特卡洛 (MC)", C_BLUE, 'mc')
    draw_trajectory(ax2, "TD(0)", C_RED, 'td0')
    draw_trajectory(ax3, "TD(λ)", C_PURPLE, 'tdl')

    plt.tight_layout(pad=1.5)
    save(fig, "td_vs_mc.png")

# ── 6. PUCT Selection ─────────────────────────────────────────────────────
def create_puct():
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=C_WHITE)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Title
    ax.text(5.5, 5.5, "MCTS + 神经网络: PUCT 选择公式", fontsize=16,
            ha='center', fontweight='bold', color=C_NAVY)

    # Formula
    ax.text(5.5, 4.3,
            r'$a^* = \arg\max_a \left[ Q(s,a) + c_{\mathrm{puct}} \cdot P(s,a) \cdot \frac{\sqrt{\sum_b N(s,b)}}{1 + N(s,a)} \right]$',
            fontsize=18, ha='center', va='center', color=C_NAVY)

    # Annotations
    items = [
        (1.5, 2.8, "$Q(s,a)$", "动作价值\n(平均回报)", C_BLUE),
        (5.5, 2.8, "$P(s,a)$", "神经网络先验\n(策略头输出)", C_GOLD),
        (9.5, 2.8, "$N(s,a)$", "访问次数", C_RED),
    ]
    for x, y, formula, desc, color in items:
        rect = FancyBboxPatch((x-1.2, y-0.8), 2.4, 1.6, boxstyle="round,pad=0.1",
                              fc=color, ec=color, alpha=0.12, zorder=1)
        ax.add_patch(rect)
        ax.text(x, y+0.25, formula, fontsize=16, ha='center', va='center',
                color=color, fontweight='bold')
        ax.text(x, y-0.35, desc, fontsize=10, ha='center', va='center',
                color=C_DARK_TEXT)

    # Bottom comparison
    ax.plot([1, 10], [1.3, 1.3], '-', color=C_LIGHT_GRAY, lw=1)
    ax.text(3, 0.8, "利用 (Exploitation)", fontsize=12, ha='center',
            color=C_BLUE, fontweight='bold')
    ax.text(8, 0.8, "探索 (Exploration)", fontsize=12, ha='center',
            color=C_GOLD, fontweight='bold')
    ax.annotate('', xy=(1.5, 1.1), xytext=(4.5, 1.1),
                arrowprops=dict(arrowstyle='<->', color=C_BLUE, lw=1.5))
    ax.annotate('', xy=(6.5, 1.1), xytext=(9.5, 1.1),
                arrowprops=dict(arrowstyle='<->', color=C_GOLD, lw=1.5))

    plt.tight_layout()
    save(fig, "puct.png")

# ── 7. Evolution Timeline ─────────────────────────────────────────────────
def create_evolution():
    fig, ax = plt.subplots(figsize=(12, 4), facecolor=C_WHITE)
    ax.set_xlim(-0.5, 12)
    ax.set_ylim(-1, 3.5)
    ax.axis('off')

    # Timeline
    ax.plot([0, 11.5], [1.5, 1.5], '-', color=C_LIGHT_GRAY, lw=3)

    versions = [
        (1, "AlphaGo\nFan", "2015.10", "监督学习+RL\n+MCTS\n战胜樊麾", C_BLUE),
        (3.5, "AlphaGo\nLee", "2016.03", "更强网络\n战胜李世石\n4:1", C_TEAL),
        (6, "AlphaGo\nMaster", "2017.01", "网上60连胜\n战胜柯洁", C_GOLD),
        (8.5, "AlphaGo\nZero", "2017.10", "无人类数据\n纯自我对弈\n超越所有版本", C_RED),
        (11, "AlphaZero", "2018.12", "泛化到象棋\n和将棋", C_PURPLE),
    ]

    for x, name, date, desc, color in versions:
        ax.plot([x, x], [1.5, 2.2], '-', color=color, lw=2.5)
        circle = plt.Circle((x, 1.5), 0.15, fc=color, ec=C_WHITE, lw=2, zorder=3)
        ax.add_patch(circle)
        ax.text(x, 2.55, name, fontsize=11, ha='center', fontweight='bold', color=color)
        ax.text(x, 1.0, date, fontsize=9, ha='center', color=C_GRAY)
        ax.text(x, 0.2, desc, fontsize=8, ha='center', color=C_DARK_TEXT,
                linespacing=1.3)

    # Key insight arrow
    ax.annotate('关键突破：去除人类知识', xy=(8.5, 3.3), fontsize=12,
                ha='center', color=C_RED, fontweight='bold')

    plt.tight_layout()
    save(fig, "evolution.png")

# ── 8. Training Pipeline ──────────────────────────────────────────────────
def create_training_pipeline():
    fig, ax = plt.subplots(figsize=(12, 4.5), facecolor=C_WHITE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis('off')

    steps = [
        (1.5, 2.5, "初始化\n随机权重 $\\theta$", C_GRAY),
        (4, 2.5, "自我对弈\nMCTS + $f_\\theta$\n生成 $(s, \\pi, z)$", C_TEAL),
        (7, 2.5, "采样训练\n最小化损失 $\\ell$\n更新 $\\theta$", C_BLUE),
        (10, 2.5, "评估\n新网络 vs 旧网络\n择优保留", C_GOLD),
    ]

    for x, y, text, color in steps:
        rect = FancyBboxPatch((x-1.2, y-0.9), 2.4, 1.8,
                              boxstyle="round,pad=0.12", fc=color, ec=color,
                              alpha=0.9, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, text, fontsize=11, ha='center', va='center',
                color=C_WHITE, fontweight='bold', zorder=3, linespacing=1.4)

    # Arrows
    for i in range(3):
        x1 = steps[i][0] + 1.3
        x2 = steps[i+1][0] - 1.3
        ax.annotate('', xy=(x2, 2.5), xytext=(x1, 2.5),
                    arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5))

    # Loop arrow from evaluation back to self-play
    ax.annotate('', xy=(4, 1.3), xytext=(10, 1.3),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2,
                               connectionstyle='arc3,rad=0.4', linestyle='--'))
    ax.text(7, 0.5, "迭代循环：越来越强", fontsize=12, ha='center',
            color=C_RED, fontweight='bold', style='italic')

    ax.text(6, 4.5, "AlphaGo Zero 训练流程", fontsize=16,
            ha='center', fontweight='bold', color=C_NAVY)

    plt.tight_layout()
    save(fig, "training_pipeline.png")

# ── 8b. Hardware & Compute ────────────────────────────────────────────────
def create_hardware():
    fig, ax = plt.subplots(figsize=(12, 4.5), facecolor=C_WHITE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis('off')

    ax.text(6, 4.7, "Google DeepMind 2017 实际配置：硬件与算力消耗", fontsize=16,
            ha='center', fontweight='bold', color=C_NAVY)

    # Self-play data generation (the bottleneck)
    sp_x, sp_y, sp_w, sp_h = 0.5, 0.6, 6.8, 3.4
    sp_rect = FancyBboxPatch((sp_x, sp_y), sp_w, sp_h, boxstyle="round,pad=0.15",
                             fc=C_TEAL, ec=C_TEAL, alpha=0.12, zorder=1)
    ax.add_patch(sp_rect)
    ax.text(sp_x + sp_w/2, sp_y + sp_h - 0.35, "自我对弈数据生成 (算力瓶颈)",
            fontsize=14, ha='center', color=C_TEAL, fontweight='bold', zorder=2)
    sp_stats = [
        ("5000", "第一代 TPU\n(并行自对弈)"),
        ("0.4 s", "每步思考\n1600次MCTS模拟"),
        ("~490 万", "自对弈局数\n(3天版)"),
    ]
    for i, (val, desc) in enumerate(sp_stats):
        cx = sp_x + 0.6 + i * 2.1
        ax.text(cx + 0.75, sp_y + 2.15, val, fontsize=22, ha='center',
                color=C_TEAL, fontweight='bold', zorder=2)
        ax.text(cx + 0.75, sp_y + 1.35, desc, fontsize=10, ha='center',
                color=C_DARK_TEXT, zorder=2, linespacing=1.3)

    # Training
    tr_x, tr_y, tr_w, tr_h = 7.6, 0.6, 3.9, 3.4
    tr_rect = FancyBboxPatch((tr_x, tr_y), tr_w, tr_h, boxstyle="round,pad=0.15",
                             fc=C_BLUE, ec=C_BLUE, alpha=0.12, zorder=1)
    ax.add_patch(tr_rect)
    ax.text(tr_x + tr_w/2, tr_y + tr_h - 0.35, "神经网络训练",
            fontsize=14, ha='center', color=C_BLUE, fontweight='bold', zorder=2)
    tr_stats = [
        ("64 GPU", "worker (SGD优化)\n+19 CPU 参数服务器"),
        ("700 K", "mini-batch\n(batch=2048)"),
        ("3 / 40 天", "训练时长\n(小/大网络)"),
    ]
    for i, (val, desc) in enumerate(tr_stats):
        cy = tr_y + 2.35 - i * 0.85
        ax.text(tr_x + 1.1, cy, val, fontsize=16, ha='left',
                color=C_BLUE, fontweight='bold', zorder=2)
        ax.text(tr_x + 2.5, cy, desc, fontsize=10, ha='left',
                color=C_DARK_TEXT, zorder=2, va='center', linespacing=1.2)

    ax.text(6, 0.15, "对弈评估：单机 4 个 TPU 即可击败 AlphaGo Lee (100:0)",
            fontsize=11, ha='center', color=C_RED, fontweight='bold', style='italic')

    plt.tight_layout()
    save(fig, "hardware.png")

# ── 9. Formula Images ─────────────────────────────────────────────────────
def create_formula(text, name, fontsize=20):
    fig, ax = plt.subplots(figsize=(10, 1.2), facecolor=C_WHITE)
    ax.text(0.5, 0.5, text, fontsize=fontsize, ha='center', va='center',
            color=C_NAVY, transform=ax.transAxes)
    ax.axis('off')
    save(fig, name)

def create_formulas():
    create_formula(
        r'$UCT(i) = \frac{w_i}{n_i} + c \sqrt{\frac{\ln N}{n_i}}$',
        "formula_uct.png", 24
    )
    create_formula(
        r'$V(S_t) \leftarrow V(S_t) + \alpha \left[ R_{t+1} + \gamma V(S_{t+1}) - V(S_t) \right]$',
        "formula_td.png", 22
    )
    create_formula(
        r'$\ell = (z - v)^2 - \boldsymbol{\pi}^\top \log \mathbf{p} + c \|\theta\|^2$',
        "formula_loss.png", 24
    )
    create_formula(
        r'$V(S_t) \leftarrow V(S_t) + \alpha \left[ G_t - V(S_t) \right], \quad G_t = \sum_{k=0}^{T-t-1} \gamma^k R_{t+k+1}$',
        "formula_mc.png", 20
    )

# ── 10. Elo Rating Progress ──────────────────────────────────────────────
def create_elo_progress():
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=C_WHITE)

    # Approximate training Elo curve for AlphaGo Zero
    hours = np.array([0, 3, 6, 12, 24, 36, 48, 72])
    elo = np.array([0, 1000, 2000, 3200, 4200, 4800, 5100, 5185])

    ax.plot(hours, elo, 'o-', color=C_BLUE, lw=2.5, markersize=6, zorder=3)
    ax.fill_between(hours, elo, alpha=0.1, color=C_BLUE)

    # Reference lines
    refs = [
        (3600, "AlphaGo Lee (2016)", C_TEAL),
        (4500, "AlphaGo Master (2017)", C_GOLD),
    ]
    for elo_val, label, color in refs:
        ax.axhline(y=elo_val, color=color, linestyle='--', alpha=0.7, lw=1.5)
        ax.text(70, elo_val + 80, label, fontsize=10, color=color, fontweight='bold')

    ax.set_xlabel("训练时间 (小时)   ·   Google DeepMind 2017 实测 (3 天版)", fontsize=13, color=C_DARK_TEXT)
    ax.set_ylabel("Elo 等级分", fontsize=13, color=C_DARK_TEXT)
    ax.set_title("AlphaGo Zero 训练过程中的棋力增长", fontsize=14,
                 fontweight='bold', color=C_NAVY, pad=15)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    save(fig, "elo_progress.png")

# ── 11. MDP Diagram ──────────────────────────────────────────────────────
def create_mdp():
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=C_WHITE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # States and actions
    states = [(1.5, 2), (5, 2), (8.5, 2)]
    for i, (x, y) in enumerate(states):
        circle = plt.Circle((x, y), 0.5, fc=C_BLUE, ec=C_NAVY, lw=2, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, f'$S_{{{i}}}$', fontsize=16, ha='center', va='center',
                color=C_WHITE, fontweight='bold', zorder=3)

    # Actions/transitions
    for i in range(2):
        x1 = states[i][0] + 0.55
        x2 = states[i+1][0] - 0.55
        mid_x = (x1 + x2) / 2
        ax.annotate('', xy=(x2, 2), xytext=(x1, 2),
                    arrowprops=dict(arrowstyle='->', color=C_GOLD, lw=2.5))
        ax.text(mid_x, 2.5, f'$a_{{{i}}}, r_{{{i+1}}}$', fontsize=13,
                ha='center', color=C_GOLD, fontweight='bold')

    # Dots for continuation
    ax.text(9.8, 2, '...', fontsize=24, ha='center', va='center', color=C_GRAY)

    # Formula below
    ax.text(5, 0.7, r'$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, P, R, \gamma \rangle$',
            fontsize=18, ha='center', color=C_NAVY, fontweight='bold')

    # Labels
    labels = [
        (1, 0.1, "$\\mathcal{S}$: 状态空间", C_BLUE),
        (3.3, 0.1, "$\\mathcal{A}$: 动作空间", C_GOLD),
        (5.6, 0.1, "$P$: 转移概率", C_TEAL),
        (7.7, 0.1, "$R$: 奖励", C_RED),
        (9.5, 0.1, "$\\gamma$: 折扣因子", C_PURPLE),
    ]
    for x, y, text, color in labels:
        ax.text(x, y, text, fontsize=10, ha='center', color=color)

    ax.text(5, 3.5, "马尔可夫决策过程 (MDP)", fontsize=16,
            ha='center', fontweight='bold', color=C_NAVY)

    plt.tight_layout()
    save(fig, "mdp.png")

# ── Generate all assets ──────────────────────────────────────────────────
def generate_all():
    print("Generating diagram assets...")
    create_mcts_phases()
    create_complexity()
    create_nn_arch()
    create_self_play_loop()
    create_td_vs_mc()
    create_puct()
    create_evolution()
    create_training_pipeline()
    create_hardware()
    create_formulas()
    create_elo_progress()
    create_mdp()
    print("All assets generated!")

# ── Slide Spec ────────────────────────────────────────────────────────────
def asset(name):
    return os.path.join(ASSET_DIR, name)

# Slide colors
BG_DARK = "0D1B3E"
BG_WHITE = "FFFFFF"
BG_LIGHT = "F0F4F8"
BG_SECTION = "102A56"

def make_spec():
    slides = []

    # ─── Slide 1: Title ───
    slides.append({
        "background": BG_DARK,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 5.8, "w": 13.333, "h": 1.7, "fill": "0A1128"},
            {"type": "text", "text": "AlphaGo Zero 原理介绍",
             "x": 1, "y": 1.5, "w": 11.333, "h": 1.5,
             "font_size": 42, "color": "FFFFFF", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "从蒙特卡洛树搜索到自我博弈强化学习",
             "x": 1.5, "y": 3.2, "w": 10.333, "h": 0.8,
             "font_size": 20, "color": "E8A838", "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "汇报人：郭少阳",
             "x": 1, "y": 6.0, "w": 5, "h": 0.6,
             "font_size": 16, "color": "90A4AE", "font": "PingFang SC"},
            {"type": "text", "text": "2025 年 7 月",
             "x": 7, "y": 6.0, "w": 5, "h": 0.6,
             "font_size": 16, "color": "90A4AE", "align": "right", "font": "PingFang SC"},
        ]
    })

    # ─── Slide 2: Outline ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 0.15, "h": 7.5, "fill": "0D1B3E"},
            {"type": "text", "text": "目录",
             "x": 0.8, "y": 0.4, "w": 5, "h": 0.8,
             "font_size": 32, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "shape", "shape": "rectangle", "x": 0.8, "y": 1.2, "w": 3, "h": 0.05, "fill": "E8A838"},
            # Part I
            {"type": "shape", "shape": "rounded_rectangle", "x": 1.2, "y": 2.0, "w": 0.8, "h": 0.8, "fill": "1565C0"},
            {"type": "text", "text": "I", "x": 1.2, "y": 2.0, "w": 0.8, "h": 0.8,
             "font_size": 24, "color": "FFFFFF", "bold": True, "align": "center"},
            {"type": "text", "text": "蒙特卡洛树搜索 (MCTS)",
             "x": 2.5, "y": 2.0, "w": 8, "h": 0.4,
             "font_size": 20, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "博弈树搜索 · UCT公式 · 四阶段流程 · 性质分析",
             "x": 2.5, "y": 2.5, "w": 9, "h": 0.4,
             "font_size": 14, "color": "757575", "font": "PingFang SC"},
            # Part II
            {"type": "shape", "shape": "rounded_rectangle", "x": 1.2, "y": 3.5, "w": 0.8, "h": 0.8, "fill": "00897B"},
            {"type": "text", "text": "II", "x": 1.2, "y": 3.5, "w": 0.8, "h": 0.8,
             "font_size": 24, "color": "FFFFFF", "bold": True, "align": "center"},
            {"type": "text", "text": "强化学习基础",
             "x": 2.5, "y": 3.5, "w": 8, "h": 0.4,
             "font_size": 20, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "MDP · 价值函数 · 蒙特卡洛方法 · 时序差分学习",
             "x": 2.5, "y": 4.0, "w": 9, "h": 0.4,
             "font_size": 14, "color": "757575", "font": "PingFang SC"},
            # Part III
            {"type": "shape", "shape": "rounded_rectangle", "x": 1.2, "y": 5.0, "w": 0.8, "h": 0.8, "fill": "E53935"},
            {"type": "text", "text": "III", "x": 1.2, "y": 5.0, "w": 0.8, "h": 0.8,
             "font_size": 24, "color": "FFFFFF", "bold": True, "align": "center"},
            {"type": "text", "text": "AlphaGo Zero：自我博弈的突破",
             "x": 2.5, "y": 5.0, "w": 8, "h": 0.4,
             "font_size": 20, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "神经网络架构 · PUCT搜索 · 自我增强 · 训练循环",
             "x": 2.5, "y": 5.5, "w": 9, "h": 0.4,
             "font_size": 14, "color": "757575", "font": "PingFang SC"},
        ]
    })

    # ─── Section: MCTS ───
    slides.append({
        "background": BG_SECTION,
        "elements": [
            {"type": "text", "text": "Part I",
             "x": 1, "y": 1.5, "w": 11.333, "h": 0.8,
             "font_size": 18, "color": "E8A838", "bold": True, "align": "center"},
            {"type": "text", "text": "蒙特卡洛树搜索",
             "x": 1, "y": 2.5, "w": 11.333, "h": 1.2,
             "font_size": 40, "color": "FFFFFF", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "Monte Carlo Tree Search",
             "x": 1, "y": 3.8, "w": 11.333, "h": 0.8,
             "font_size": 20, "color": "90A4AE", "align": "center"},
            {"type": "shape", "shape": "rectangle", "x": 5.167, "y": 5.0, "w": 3, "h": 0.05, "fill": "E8A838"},
        ]
    })

    # ─── Slide: Game Complexity ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "1565C0"},
            {"type": "text", "text": "为什么围棋这么难？",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("complexity.png"),
             "x": 0.5, "y": 1.3, "w": 12.3, "h": 5.5},
        ]
    })

    # ─── Slide: MC in Physics ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "1565C0"},
            {"type": "text", "text": "蒙特卡洛方法：从物理到博弈",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            # Physics MC
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 1.5, "w": 5.8, "h": 4.5, "fill": "E8F5E9"},
            {"type": "text", "text": "物理中的蒙特卡洛",
             "x": 0.8, "y": 1.7, "w": 5.2, "h": 0.5,
             "font_size": 18, "color": "2E7D32", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "• 格点QCD：用MC采样计算路径积分\n\n• Metropolis算法：按 exp(-S) 采样构型\n\n• 重要性采样：用概率分布引导采样\n\n• 核心思想：用随机采样近似复杂积分",
             "x": 0.8, "y": 2.5, "w": 5.2, "h": 3.2,
             "font_size": 14, "color": "333333", "font": "PingFang SC"},
            # Game MC
            {"type": "shape", "shape": "rounded_rectangle", "x": 7.0, "y": 1.5, "w": 5.8, "h": 4.5, "fill": "E3F2FD"},
            {"type": "text", "text": "博弈中的蒙特卡洛",
             "x": 7.3, "y": 1.7, "w": 5.2, "h": 0.5,
             "font_size": 18, "color": "1565C0", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "• 随机模拟对局至终局获得结果\n\n• 统计胜率来评估局面好坏\n\n• 用树结构组织搜索方向\n\n• 核心思想：用随机采样近似博弈值",
             "x": 7.3, "y": 2.5, "w": 5.2, "h": 3.2,
             "font_size": 14, "color": "333333", "font": "PingFang SC"},
            # Bottom
            {"type": "text", "text": "本质相同：用随机采样解决精确计算不可行的问题",
             "x": 1, "y": 6.3, "w": 11.333, "h": 0.5,
             "font_size": 16, "color": "E53935", "bold": True, "align": "center", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: MCTS Four Phases ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "1565C0"},
            {"type": "text", "text": "MCTS 的四个阶段",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("mcts_phases.png"),
             "x": 0.2, "y": 1.2, "w": 12.9, "h": 3.5},
            {"type": "text", "text": "每次迭代执行这四个步骤，逐步积累统计信息，搜索精度随迭代次数增加而提高",
             "x": 0.5, "y": 5.0, "w": 12, "h": 0.5,
             "font_size": 14, "color": "757575", "align": "center", "font": "PingFang SC"},
            # Step descriptions
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 5.6, "w": 2.8, "h": 1.3, "fill": "E3F2FD"},
            {"type": "text", "text": "① 选择\n从根节点沿UCT\n最大的子节点下行",
             "x": 0.6, "y": 5.7, "w": 2.6, "h": 1.1,
             "font_size": 11, "color": "1565C0", "font": "PingFang SC", "align": "center"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 3.7, "y": 5.6, "w": 2.8, "h": 1.3, "fill": "E8F5E9"},
            {"type": "text", "text": "② 扩展\n到达叶节点后\n添加一个新子节点",
             "x": 3.8, "y": 5.7, "w": 2.6, "h": 1.1,
             "font_size": 11, "color": "2E7D32", "font": "PingFang SC", "align": "center"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 6.9, "y": 5.6, "w": 2.8, "h": 1.3, "fill": "FFF3E0"},
            {"type": "text", "text": "③ 模拟\n从新节点随机走子\n直到游戏结束",
             "x": 7.0, "y": 5.7, "w": 2.6, "h": 1.1,
             "font_size": 11, "color": "E65100", "font": "PingFang SC", "align": "center"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 10.1, "y": 5.6, "w": 2.8, "h": 1.3, "fill": "FFEBEE"},
            {"type": "text", "text": "④ 回传\n将结果沿路径\n回传更新统计量",
             "x": 10.2, "y": 5.7, "w": 2.6, "h": 1.1,
             "font_size": 11, "color": "C62828", "font": "PingFang SC", "align": "center"},
        ]
    })

    # ─── Slide: UCT Formula ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "1565C0"},
            {"type": "text", "text": "Selection: UCT 公式",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "Upper Confidence Bound applied to Trees (UCT)",
             "x": 0.5, "y": 1.0, "w": 12, "h": 0.4,
             "font_size": 14, "color": "757575"},
            {"type": "image", "path": asset("formula_uct.png"),
             "x": 1.5, "y": 1.5, "w": 10, "h": 1.2},
            # Annotations
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.8, "y": 3.2, "w": 3.5, "h": 1.8, "fill": "E3F2FD"},
            {"type": "text", "text": "利用项 (Exploitation)\n\nwᵢ/nᵢ = 第i个子节点的\n平均胜率，偏好好的走法",
             "x": 0.9, "y": 3.3, "w": 3.3, "h": 1.6,
             "font_size": 13, "color": "1565C0", "font": "PingFang SC"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 4.9, "y": 3.2, "w": 3.5, "h": 1.8, "fill": "FFF3E0"},
            {"type": "text", "text": "探索项 (Exploration)\n\n√(ln N / nᵢ)：访问少的\n节点获得更高的探索奖励",
             "x": 5.0, "y": 3.3, "w": 3.3, "h": 1.6,
             "font_size": 13, "color": "E65100", "font": "PingFang SC"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 9.0, "y": 3.2, "w": 3.5, "h": 1.8, "fill": "F3E5F5"},
            {"type": "text", "text": "探索常数 c\n\n控制利用与探索的平衡\n常用 c = √2",
             "x": 9.1, "y": 3.3, "w": 3.3, "h": 1.6,
             "font_size": 13, "color": "7B1FA2", "font": "PingFang SC"},
            # Properties
            {"type": "shape", "shape": "rectangle", "x": 0.8, "y": 5.5, "w": 11.7, "h": 0.05, "fill": "E0E0E0"},
            {"type": "text", "text": "核心性质：UCT 在无限采样下收敛到极小极大最优解 (Kocsis & Szepesvári, 2006)",
             "x": 0.8, "y": 5.8, "w": 11.7, "h": 0.5,
             "font_size": 14, "color": "E53935", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "类比物理：类似于模拟退火中温度控制探索-利用平衡，或 Metropolis 中接受概率的作用",
             "x": 0.8, "y": 6.4, "w": 11.7, "h": 0.5,
             "font_size": 13, "color": "00897B", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: MCTS Properties ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "1565C0"},
            {"type": "text", "text": "MCTS 的关键性质",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            # Property 1
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 1.5, "w": 5.9, "h": 2.3, "fill": "E3F2FD"},
            {"type": "text", "text": "渐近最优 (Asymptotic Optimality)",
             "x": 0.8, "y": 1.6, "w": 5.3, "h": 0.4,
             "font_size": 15, "color": "1565C0", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "随着模拟次数 N → ∞，MCTS的选择\n概率收敛到最优策略。\n这是UCT的理论保证。",
             "x": 0.8, "y": 2.2, "w": 5.3, "h": 1.4,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
            # Property 2
            {"type": "shape", "shape": "rounded_rectangle", "x": 7.0, "y": 1.5, "w": 5.9, "h": 2.3, "fill": "E8F5E9"},
            {"type": "text", "text": "Anytime 算法",
             "x": 7.3, "y": 1.6, "w": 5.3, "h": 0.4,
             "font_size": 15, "color": "2E7D32", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "可以随时中断并返回当前最优动作。\n计算资源越多，决策质量越高。\n天然适合有时间限制的实时决策。",
             "x": 7.3, "y": 2.2, "w": 5.3, "h": 1.4,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
            # Property 3
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 4.2, "w": 5.9, "h": 2.3, "fill": "FFF3E0"},
            {"type": "text", "text": "无需领域知识",
             "x": 0.8, "y": 4.3, "w": 5.3, "h": 0.4,
             "font_size": 15, "color": "E65100", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "不需要人工设计评估函数。\n仅需知道游戏规则（合法动作和终止\n条件），即可通过模拟获取价值信息。",
             "x": 0.8, "y": 4.9, "w": 5.3, "h": 1.4,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
            # Property 4
            {"type": "shape", "shape": "rounded_rectangle", "x": 7.0, "y": 4.2, "w": 5.9, "h": 2.3, "fill": "F3E5F5"},
            {"type": "text", "text": "自适应搜索",
             "x": 7.3, "y": 4.3, "w": 5.3, "h": 0.4,
             "font_size": 15, "color": "7B1FA2", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "自动将更多计算资源分配给最有\n前途的分支。搜索树非对称增长，\n类似重要性采样。",
             "x": 7.3, "y": 4.9, "w": 5.3, "h": 1.4,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
        ]
    })

    # ─── Section: RL ───
    slides.append({
        "background": BG_SECTION,
        "elements": [
            {"type": "text", "text": "Part II",
             "x": 1, "y": 1.5, "w": 11.333, "h": 0.8,
             "font_size": 18, "color": "E8A838", "bold": True, "align": "center"},
            {"type": "text", "text": "强化学习基础",
             "x": 1, "y": 2.5, "w": 11.333, "h": 1.2,
             "font_size": 40, "color": "FFFFFF", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "Reinforcement Learning Foundations",
             "x": 1, "y": 3.8, "w": 11.333, "h": 0.8,
             "font_size": 20, "color": "90A4AE", "align": "center"},
            {"type": "shape", "shape": "rectangle", "x": 5.167, "y": 5.0, "w": 3, "h": 0.05, "fill": "E8A838"},
        ]
    })

    # ─── Slide: MDP ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "00897B"},
            {"type": "text", "text": "马尔可夫决策过程 (MDP)",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("mdp.png"),
             "x": 0.5, "y": 1.2, "w": 12.3, "h": 4.2},
            {"type": "text", "text": "围棋天然是一个 MDP：状态 = 棋盘局面，动作 = 落子位置，奖励 = 终局胜负 (±1)",
             "x": 0.5, "y": 5.8, "w": 12, "h": 0.5,
             "font_size": 14, "color": "E53935", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "RL的目标：学习最优策略 π* 使得累积奖励最大",
             "x": 0.5, "y": 6.5, "w": 12, "h": 0.5,
             "font_size": 14, "color": "757575", "align": "center", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: Value Function ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "00897B"},
            {"type": "text", "text": "价值函数与策略",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            # Policy
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 1.5, "w": 5.9, "h": 2.5, "fill": "E3F2FD"},
            {"type": "text", "text": "策略 π(a|s)",
             "x": 0.8, "y": 1.6, "w": 5.3, "h": 0.5,
             "font_size": 18, "color": "1565C0", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "在状态 s 下选择动作 a 的概率分布\n\n策略是 agent 的 \"行为准则\"\n\n目标：找到最优策略 π*",
             "x": 0.8, "y": 2.3, "w": 5.3, "h": 1.5,
             "font_size": 14, "color": "333333", "font": "PingFang SC"},
            # V(s)
            {"type": "shape", "shape": "rounded_rectangle", "x": 7.0, "y": 1.5, "w": 5.9, "h": 2.5, "fill": "E8F5E9"},
            {"type": "text", "text": "状态价值函数 V(s)",
             "x": 7.3, "y": 1.6, "w": 5.3, "h": 0.5,
             "font_size": 18, "color": "2E7D32", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "从状态 s 出发，遵循策略 π\n所能获得的期望累积回报\n\nV^π(s) = E_π[Gₜ | Sₜ = s]\n\nGₜ = Rₜ₊₁ + γRₜ₊₂ + γ²Rₜ₊₃ + ...",
             "x": 7.3, "y": 2.3, "w": 5.3, "h": 1.5,
             "font_size": 14, "color": "333333", "font": "PingFang SC"},
            # Q(s,a)
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 4.5, "w": 12.4, "h": 2.2, "fill": "FFF3E0"},
            {"type": "text", "text": "动作价值函数 Q(s, a)",
             "x": 0.8, "y": 4.6, "w": 5.3, "h": 0.5,
             "font_size": 18, "color": "E65100", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "在状态 s 执行动作 a 后，遵循策略 π 的期望累积回报：  Q^π(s,a) = E_π[Gₜ | Sₜ = s, Aₜ = a]\n\n在 AlphaGo 中: Q(s,a) 就是 MCTS 节点统计的平均回报，用来指导选择最优走法",
             "x": 0.8, "y": 5.3, "w": 11.8, "h": 1.2,
             "font_size": 14, "color": "333333", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: MC vs TD ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "00897B"},
            {"type": "text", "text": "蒙特卡洛方法 vs 时序差分学习",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("td_vs_mc.png"),
             "x": 0.2, "y": 1.2, "w": 12.9, "h": 3.5},
            # MC update
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 5.0, "w": 6, "h": 2, "fill": "E3F2FD"},
            {"type": "text", "text": "MC 更新：等到终局",
             "x": 0.8, "y": 5.1, "w": 5.4, "h": 0.4,
             "font_size": 14, "color": "1565C0", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "V(Sₜ) ← V(Sₜ) + α[Gₜ - V(Sₜ)]\n\n无偏但高方差，必须完成完整轨迹",
             "x": 0.8, "y": 5.6, "w": 5.4, "h": 1.2,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
            # TD update
            {"type": "shape", "shape": "rounded_rectangle", "x": 6.9, "y": 5.0, "w": 6, "h": 2, "fill": "FFEBEE"},
            {"type": "text", "text": "TD(0) 更新：每步即学",
             "x": 7.2, "y": 5.1, "w": 5.4, "h": 0.4,
             "font_size": 14, "color": "C62828", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "V(Sₜ) ← V(Sₜ) + α[Rₜ₊₁ + γV(Sₜ₊₁) - V(Sₜ)]\n\n有偏但低方差，用估计值 bootstrap",
             "x": 7.2, "y": 5.6, "w": 5.4, "h": 1.2,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: TD(λ) ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "00897B"},
            {"type": "text", "text": "TD(λ)：MC 与 TD 的统一框架",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            # Spectrum
            {"type": "shape", "shape": "rectangle", "x": 1, "y": 1.5, "w": 11.3, "h": 0.6, "fill": "E3F2FD"},
            {"type": "text", "text": "TD(0)                λ = 0.5                TD(λ)                λ = 0.9                MC",
             "x": 1, "y": 1.5, "w": 11.3, "h": 0.6,
             "font_size": 14, "color": "1565C0", "bold": True, "align": "center"},
            {"type": "text", "text": "λ = 0                                                                                                  λ = 1",
             "x": 1, "y": 2.2, "w": 11.3, "h": 0.4,
             "font_size": 13, "color": "757575", "align": "center"},
            # n-step returns
            {"type": "text", "text": "n-step 回报",
             "x": 0.5, "y": 3.0, "w": 12, "h": 0.5,
             "font_size": 18, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "1-step:  G⁽¹⁾ = Rₜ₊₁ + γV(Sₜ₊₁)                           ← TD(0)\n\n2-step:  G⁽²⁾ = Rₜ₊₁ + γRₜ₊₂ + γ²V(Sₜ₊₂)\n\nn-step:  G⁽ⁿ⁾ = Rₜ₊₁ + γRₜ₊₂ + ... + γⁿV(Sₜ₊ₙ)\n\n∞-step:  G⁽∞⁾ = Rₜ₊₁ + γRₜ₊₂ + ...                          ← MC",
             "x": 0.8, "y": 3.6, "w": 11.5, "h": 2.5,
             "font_size": 14, "color": "333333", "font": "PingFang SC"},
            # Lambda return
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 6.2, "w": 12.3, "h": 0.9, "fill": "F3E5F5"},
            {"type": "text", "text": "TD(λ) 回报是所有 n-step 回报的加权平均：Gₜ^λ = (1-λ)∑ₙ₌₁^∞ λⁿ⁻¹ G⁽ⁿ⁾    λ ∈ [0,1] 控制看多远",
             "x": 0.8, "y": 6.3, "w": 11.7, "h": 0.7,
             "font_size": 13, "color": "7B1FA2", "bold": True, "font": "PingFang SC"},
        ]
    })

    # ─── Section: AlphaGo Zero ───
    slides.append({
        "background": BG_SECTION,
        "elements": [
            {"type": "text", "text": "Part III",
             "x": 1, "y": 1.5, "w": 11.333, "h": 0.8,
             "font_size": 18, "color": "E8A838", "bold": True, "align": "center"},
            {"type": "text", "text": "AlphaGo Zero",
             "x": 1, "y": 2.5, "w": 11.333, "h": 1.2,
             "font_size": 40, "color": "FFFFFF", "bold": True, "align": "center"},
            {"type": "text", "text": "自我博弈的突破  ·  Mastering the Game of Go without Human Knowledge",
             "x": 1, "y": 3.8, "w": 11.333, "h": 0.8,
             "font_size": 16, "color": "90A4AE", "align": "center", "font": "PingFang SC"},
            {"type": "shape", "shape": "rectangle", "x": 5.167, "y": 5.0, "w": 3, "h": 0.05, "fill": "E8A838"},
        ]
    })

    # ─── Slide: Evolution ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "从 AlphaGo 到 AlphaGo Zero",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("evolution.png"),
             "x": 0.2, "y": 1.3, "w": 12.9, "h": 3.8},
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 5.5, "w": 12.3, "h": 1.5, "fill": "FFEBEE"},
            {"type": "text", "text": "AlphaGo Zero 的三大简化",
             "x": 0.8, "y": 5.6, "w": 11.7, "h": 0.4,
             "font_size": 15, "color": "C62828", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "① 不使用任何人类棋谱 (no human data)    ② 仅用棋盘状态作为输入 (no hand-crafted features)    ③ 单一神经网络替代策略网络+价值网络",
             "x": 0.8, "y": 6.1, "w": 11.7, "h": 0.8,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: NN Architecture ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "双头神经网络架构",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("nn_arch.png"),
             "x": 1.5, "y": 1.0, "w": 10.3, "h": 6.2},
        ]
    })

    # ─── Slide: PUCT ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "MCTS + 神经网络：PUCT 搜索",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("puct.png"),
             "x": 0.5, "y": 1.0, "w": 12.3, "h": 4.5},
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 5.6, "w": 12.3, "h": 1.5, "fill": "F0F4F8"},
            {"type": "text", "text": "与传统 MCTS 的关键区别",
             "x": 0.8, "y": 5.7, "w": 11.7, "h": 0.4,
             "font_size": 15, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "① 用 P(s,a) 替代随机模拟 (Simulation)   ② 用 v(s) 替代终局结果   ③ 搜索效率大幅提升，少量模拟即可获得高质量策略",
             "x": 0.8, "y": 6.2, "w": 11.7, "h": 0.8,
             "font_size": 13, "color": "333333", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: Self-Play ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "自我对弈与数据生成",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("self_play_loop.png"),
             "x": 2, "y": 0.8, "w": 9.3, "h": 6.2},
        ]
    })

    # ─── Slide: Loss Function ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "训练目标：损失函数",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("formula_loss.png"),
             "x": 1.5, "y": 1.3, "w": 10, "h": 1.2},
            # Three terms
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 3.0, "w": 3.8, "h": 2.5, "fill": "E3F2FD"},
            {"type": "text", "text": "价值损失\n(z - v)²",
             "x": 0.8, "y": 3.1, "w": 3.2, "h": 0.8,
             "font_size": 16, "color": "1565C0", "bold": True, "font": "PingFang SC", "align": "center"},
            {"type": "text", "text": "z: 自我对弈终局结果 (±1)\nv: 网络预测的价值\n\n让网络学会准确评估局面",
             "x": 0.7, "y": 4.0, "w": 3.4, "h": 1.3,
             "font_size": 12, "color": "333333", "font": "PingFang SC"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 4.8, "y": 3.0, "w": 3.8, "h": 2.5, "fill": "FFF3E0"},
            {"type": "text", "text": "策略损失\n-π^T log p",
             "x": 5.1, "y": 3.1, "w": 3.2, "h": 0.8,
             "font_size": 16, "color": "E65100", "bold": True, "font": "PingFang SC", "align": "center"},
            {"type": "text", "text": "π: MCTS搜索得到的策略\np: 网络输出的先验策略\n\n让网络学会预测搜索结果",
             "x": 4.7, "y": 4.0, "w": 3.6, "h": 1.3,
             "font_size": 12, "color": "333333", "font": "PingFang SC"},
            {"type": "shape", "shape": "rounded_rectangle", "x": 9.1, "y": 3.0, "w": 3.8, "h": 2.5, "fill": "F3E5F5"},
            {"type": "text", "text": "正则化\nc‖θ‖²",
             "x": 9.4, "y": 3.1, "w": 3.2, "h": 0.8,
             "font_size": 16, "color": "7B1FA2", "bold": True, "font": "PingFang SC", "align": "center"},
            {"type": "text", "text": "L2 权重正则化\n防止过拟合\n\n标准的机器学习技巧",
             "x": 9.0, "y": 4.0, "w": 3.6, "h": 1.3,
             "font_size": 12, "color": "333333", "font": "PingFang SC"},
            # Bottom insight
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 5.8, "w": 12.3, "h": 1.2, "fill": "FFEBEE"},
            {"type": "text", "text": "策略提升的闭环：MCTS搜索 → 得到改进策略π → 训练网络逼近π → 网络指导MCTS → 更强的搜索 → ...",
             "x": 0.8, "y": 5.9, "w": 11.7, "h": 0.5,
             "font_size": 14, "color": "C62828", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "类比物理中的自洽场方法 (SCF)：每轮迭代都以前一轮结果为基础，逐步逼近最优解",
             "x": 0.8, "y": 6.5, "w": 11.7, "h": 0.5,
             "font_size": 13, "color": "00897B", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: Training Pipeline ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "完整训练流程",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("training_pipeline.png"),
             "x": 0.3, "y": 1.1, "w": 12.7, "h": 4.3},
            {"type": "text", "text": "自我对弈 (数据生成) 与神经网络训练异步并行进行，天然适合大规模分布式加速",
             "x": 0.5, "y": 5.7, "w": 12, "h": 0.5,
             "font_size": 14, "color": "00897B", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "策略迭代：MCTS 作为策略提升算子，自对弈胜负作为策略评估算子，交替执行直至收敛",
             "x": 0.5, "y": 6.3, "w": 12, "h": 0.5,
             "font_size": 13, "color": "757575", "align": "center", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: Hardware ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "硬件配置与算力消耗",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("hardware.png"),
             "x": 0.3, "y": 1.0, "w": 12.7, "h": 4.5},
            {"type": "text", "text": "算力瓶颈在自我对弈：生成 490 万局需数千 TPU 并行，而训练本身仅需 64 个 GPU",
             "x": 0.5, "y": 5.7, "w": 12, "h": 0.5,
             "font_size": 14, "color": "E53935", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "以上为 Google DeepMind 2017 年 AlphaGo Zero (Nature) 的实测配置；AlphaZero (2018) 升级为 5000 一代 TPU 自对弈 + 64 二代 TPU 训练",
             "x": 0.5, "y": 6.3, "w": 12, "h": 0.5,
             "font_size": 12, "color": "757575", "align": "center", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: Results ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "E53935"},
            {"type": "text", "text": "训练效果",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 28, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "image", "path": asset("elo_progress.png"),
             "x": 0.5, "y": 1.0, "w": 12.3, "h": 5.8},
        ]
    })

    # ─── Slide: Summary ───
    slides.append({
        "background": BG_WHITE,
        "elements": [
            {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 13.333, "h": 0.08, "fill": "0D1B3E"},
            {"type": "text", "text": "总结",
             "x": 0.5, "y": 0.3, "w": 12, "h": 0.7,
             "font_size": 32, "color": "0D1B3E", "bold": True, "font": "PingFang SC"},
            {"type": "shape", "shape": "rectangle", "x": 0.5, "y": 1.1, "w": 3, "h": 0.05, "fill": "E8A838"},
            # Key takeaway 1
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 1.5, "w": 3.9, "h": 2.8, "fill": "E3F2FD"},
            {"type": "text", "text": "MCTS",
             "x": 0.5, "y": 1.6, "w": 3.9, "h": 0.5,
             "font_size": 20, "color": "1565C0", "bold": True, "font": "PingFang SC", "align": "center"},
            {"type": "text", "text": "通过蒙特卡洛模拟\n在博弈树中进行\n高效的选择性搜索\n\nUCT平衡利用与探索\n无需评估函数",
             "x": 0.7, "y": 2.2, "w": 3.5, "h": 1.9,
             "font_size": 13, "color": "333333", "font": "PingFang SC", "align": "center"},
            # Key takeaway 2
            {"type": "shape", "shape": "rounded_rectangle", "x": 4.7, "y": 1.5, "w": 3.9, "h": 2.8, "fill": "E8F5E9"},
            {"type": "text", "text": "RL 基础",
             "x": 4.7, "y": 1.6, "w": 3.9, "h": 0.5,
             "font_size": 20, "color": "2E7D32", "bold": True, "font": "PingFang SC", "align": "center"},
            {"type": "text", "text": "TD学习：每步更新\n结合估计与真实回报\n\n从MC到TD的统一\n框架 TD(λ)",
             "x": 4.9, "y": 2.2, "w": 3.5, "h": 1.9,
             "font_size": 13, "color": "333333", "font": "PingFang SC", "align": "center"},
            # Key takeaway 3
            {"type": "shape", "shape": "rounded_rectangle", "x": 8.9, "y": 1.5, "w": 3.9, "h": 2.8, "fill": "FFEBEE"},
            {"type": "text", "text": "AlphaGo Zero",
             "x": 8.9, "y": 1.6, "w": 3.9, "h": 0.5,
             "font_size": 20, "color": "C62828", "bold": True, "font": "PingFang SC", "align": "center"},
            {"type": "text", "text": "神经网络替代模拟\nMCTS提供策略改进\n自我对弈生成数据\n\n从零开始超越人类\n无需任何先验知识",
             "x": 9.1, "y": 2.2, "w": 3.5, "h": 1.9,
             "font_size": 13, "color": "333333", "font": "PingFang SC", "align": "center"},
            # Core insight
            {"type": "shape", "shape": "rounded_rectangle", "x": 0.5, "y": 4.7, "w": 12.3, "h": 2.3, "fill": "0D1B3E"},
            {"type": "text", "text": "核心洞察",
             "x": 0.8, "y": 4.8, "w": 11.7, "h": 0.5,
             "font_size": 18, "color": "E8A838", "bold": True, "font": "PingFang SC"},
            {"type": "text", "text": "搜索 (MCTS) + 评估 (Neural Network) + 学习 (Self-Play RL) = 从零开始的超人智能\n\n类比物理：就像变分蒙特卡洛 (VMC) 中 —— 用参数化的试探波函数 (神经网络) 引导蒙特卡洛采样 (MCTS)\n然后通过优化变分参数 (训练) 来逼近基态 (最优策略)",
             "x": 0.8, "y": 5.4, "w": 11.7, "h": 1.4,
             "font_size": 14, "color": "FFFFFF", "font": "PingFang SC"},
        ]
    })

    # ─── Slide: Thank You ───
    slides.append({
        "background": BG_DARK,
        "elements": [
            {"type": "text", "text": "谢谢！",
             "x": 1, "y": 2.0, "w": 11.333, "h": 1.2,
             "font_size": 44, "color": "FFFFFF", "bold": True, "align": "center", "font": "PingFang SC"},
            {"type": "text", "text": "欢迎讨论与交流",
             "x": 1, "y": 3.5, "w": 11.333, "h": 0.8,
             "font_size": 22, "color": "E8A838", "align": "center", "font": "PingFang SC"},
            {"type": "shape", "shape": "rectangle", "x": 5.167, "y": 4.5, "w": 3, "h": 0.05, "fill": "E8A838"},
        ]
    })

    spec = {
        "width": 13.333,
        "height": 7.5,
        "slides": slides
    }

    spec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec.json")
    with open(spec_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    print(f"Spec written to {spec_path}")
    print(f"Total slides: {len(slides)}")
    return spec_path

# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    generate_all()
    make_spec()
    print("\nDone! Run: deck.py create spec.json AlphaGoZero_Intro.pptx")
