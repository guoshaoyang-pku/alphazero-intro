#!/usr/bin/env python3
"""Generate tic-tac-toe based MCTS walkthrough diagrams, inspired by 李理's blog approach.
Uses real board states as tree nodes with N/W/P values."""
import os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.patheffects as pe

CN_FONT="Noto Sans CJK SC"
matplotlib.rcParams['font.sans-serif']=[CN_FONT,'STHeiti','Heiti TC']
matplotlib.rcParams['axes.unicode_minus']=False

ASSET_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets")
C_NAVY="#0D1B3E";C_BLUE="#1565C0";C_TEAL="#00897B";C_GREEN="#2E7D32"
C_GOLD="#E8A838";C_RED="#E53935";C_ORANGE="#FB8C00";C_GRAY="#BDBDBD"
C_LGRAY="#E0E0E0";C_WHITE="#FFFFFF";C_DARK="#1A1A2E";C_PURPLE="#7B1FA2"
DPI=200

def save(fig,name):
    path=os.path.join(ASSET_DIR,name)
    fig.savefig(path,dpi=DPI,bbox_inches='tight',facecolor='white',edgecolor='none',pad_inches=0.1)
    plt.close(fig); print(f"  [+] {name}"); return path

def draw_board(ax, cx, cy, board, size=0.5, highlight=None, label=None, label_color=C_DARK):
    """Draw a tic-tac-toe board centered at (cx,cy). board is 3x3, 0=empty,1=X,-1=O."""
    s = size
    x0, y0 = cx - 1.5*s, cy - 1.5*s
    # grid lines
    for i in range(1,3):
        ax.plot([x0+i*s, x0+i*s], [y0, y0+3*s], '-', color=C_GRAY, lw=1, zorder=1)
        ax.plot([x0, x0+3*s], [y0+i*s, y0+i*s], '-', color=C_GRAY, lw=1, zorder=1)
    # border
    ax.plot([x0,x0+3*s,x0+3*s,x0,x0],[y0,y0,y0+3*s,y0+3*s,y0],'-',color=C_DARK,lw=1.2,zorder=1)
    # pieces
    for r in range(3):
        for c in range(3):
            v = board[r][c]
            px, py = x0+(c+0.5)*s, y0+(2-r+0.5)*s
            if v == 1:  # X
                d = s*0.25
                ax.plot([px-d,px+d],[py-d,py+d],'-',color=C_RED,lw=1.8,zorder=2)
                ax.plot([px-d,px+d],[py+d,py-d],'-',color=C_RED,lw=1.8,zorder=2)
            elif v == -1:  # O
                circ = plt.Circle((px,py),s*0.25,fill=False,ec=C_BLUE,lw=1.8,zorder=2)
                ax.add_patch(circ)
            if highlight and (r,c) == highlight:
                rect = Rectangle((x0+c*s, y0+(2-r)*s), s, s, fc=C_GOLD, alpha=0.25, zorder=0)
                ax.add_patch(rect)
    if label:
        ax.text(cx, cy-1.5*s-0.15, label, fontsize=7, ha='center', va='top', color=label_color)

def edge(ax, p1, p2, color=C_GRAY, lw=1.2, style='-', z=1):
    ax.plot([p1[0],p2[0]],[p1[1],p2[1]],style,color=color,lw=lw,zorder=z)

def arrow(ax, p1, p2, color, lw=1.8, style='-'):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle='->,head_width=4,head_length=6',color=color,lw=lw,linestyle=style,zorder=2))

def edge_label(ax, p1, p2, text, color=C_DARK, offset=0.12):
    mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    length = np.sqrt(dx**2+dy**2)
    nx, ny = -dy/length, dx/length
    ax.text(mx+nx*offset, my+ny*offset, text, fontsize=7, ha='center', va='center', color=color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.8))

# ── 1. Traditional MCTS: first iteration (Expand + Rollout + Backup) ─
def trad_iter1():
    fig, ax = plt.subplots(figsize=(13,5.5), facecolor='white')
    ax.set_xlim(-0.5, 13); ax.set_ylim(-0.5, 5.5); ax.axis('off')
    ax.text(6.5, 5.2, '传统 MCTS 第 1 次模拟：展开 + Rollout + 回传', fontsize=13, ha='center', color=C_NAVY, fontweight='bold')

    # Root board: X to move, center taken
    root = [[0,0,0],[0,1,0],[0,0,0]]
    draw_board(ax, 1.2, 3.0, root, size=0.38, label='s0  (X走)')

    # 5 children (5 possible moves for O)
    children_boards = [
        ([[-1,0,0],[0,1,0],[0,0,0]], (0,0)),
        ([[0,-1,0],[0,1,0],[0,0,0]], (0,1)),
        ([[0,0,-1],[0,1,0],[0,0,0]], (0,2)),
        ([[0,0,0],[0,1,-1],[0,0,0]], (1,2)),
        ([[0,0,0],[0,1,0],[-1,0,0]], (2,0)),
    ]
    child_pos = [(3.5,4.3),(4.5,4.3),(5.5,4.3),(3.5,2.0),(4.5,2.0)]
    child_labels = ['s01','s02','s03','s04','s05']
    child_vals = [1, -1, 1, 0, -1]  # rollout results (from X's perspective)
    
    for i,((board,hl),pos,lbl) in enumerate(zip(children_boards, child_pos, child_labels)):
        draw_board(ax, pos[0], pos[1], board, size=0.3, highlight=hl, label=lbl)
        edge(ax, (1.2, 3.0), pos, color=C_GRAY, lw=1)

    # Rollout from s01 (dashed path to terminal)
    rollout_boards = [
        ([[-1,0,0],[1,1,0],[0,0,0]], None),
        ([[-1,0,0],[1,1,-1],[0,0,0]], None),
        ([[-1,1,0],[1,1,-1],[0,0,0]], None),
        ([[-1,1,0],[1,1,-1],[-1,0,1]], None),
        ([[-1,1,1],[1,1,-1],[-1,0,1]], None),  # X wins (diagonal)
    ]
    rpos = [(6.8,4.3),(7.8,4.3),(8.8,4.3),(9.8,4.3),(10.8,4.3)]
    for i,((board,hl),pos) in enumerate(zip(rollout_boards, rpos)):
        draw_board(ax, pos[0], pos[1], board, size=0.28)
        if i==0:
            arrow(ax, (5.5, 4.3), pos, color=C_ORANGE, lw=1.5, style='--')
        else:
            arrow(ax, rpos[i-1], pos, color=C_ORANGE, lw=1.5, style='--')
    # terminal result
    ax.add_patch(FancyBboxPatch((10.4,3.4),1.0,0.4,boxstyle='round,pad=0.08',fc=C_GREEN,ec=C_GREEN,zorder=4))
    ax.text(10.9,3.6,'X 胜 v=+1',fontsize=8,ha='center',va='center',color='w',fontweight='bold',zorder=5)

    # Rollout annotations for other children
    ax.text(3.5,3.55,'v=+1',fontsize=8,ha='center',color=C_GREEN,fontweight='bold')
    ax.text(4.5,3.25,'v=-1',fontsize=8,ha='center',color=C_RED,fontweight='bold')
    ax.text(5.5,3.55,'v=+1',fontsize=8,ha='center',color=C_GREEN,fontweight='bold')
    ax.text(3.5,1.25,'v=0',fontsize=8,ha='center',color=C_GRAY,fontweight='bold')
    ax.text(4.5,1.25,'v=-1',fontsize=8,ha='center',color=C_RED,fontweight='bold')

    ax.text(7.8,3.7,'随机 rollout (虚线)',fontsize=9,ha='center',color=C_ORANGE,style='italic')

    # Backup annotation
    ax.add_patch(FancyBboxPatch((0.3,0.3),2.2,0.8,boxstyle='round,pad=0.1',fc='#FFEBEE',ec=C_RED,lw=1))
    ax.text(1.4,0.85,'回传 Backup',fontsize=9,ha='center',color=C_RED,fontweight='bold')
    ax.text(1.4,0.5,'N=5, W=0\n(5局: 2胜2负1平)',fontsize=8,ha='center',color=C_DARK)
    arrow(ax, (1.4, 1.15), (1.2, 2.7), color=C_RED, lw=1.5, style='--')

    plt.tight_layout(); save(fig, 'ttt_iter1.png')

# ── 2. Traditional MCTS: second iteration (Selection by UCT) ─────────
def trad_iter2():
    fig, ax = plt.subplots(figsize=(13,5.5), facecolor='white')
    ax.set_xlim(-0.5, 13); ax.set_ylim(-0.5, 5.5); ax.axis('off')
    ax.text(6.5, 5.2, '传统 MCTS 第 2 次模拟：UCT 选择 → 展开 → 回传', fontsize=13, ha='center', color=C_NAVY, fontweight='bold')

    root = [[0,0,0],[0,1,0],[0,0,0]]
    draw_board(ax, 1.2, 3.0, root, size=0.38, label='s0  N=5, W=0')

    # children with N, W from iter 1
    children = [
        ([[-1,0,0],[0,1,0],[0,0,0]], (0,0), (3.2,4.3), 's01', 'N=1\nW=+1', 'UCT=0.71', C_GREEN),
        ([[0,-1,0],[0,1,0],[0,0,0]], (0,1), (4.2,4.3), 's02', 'N=1\nW=-1', 'UCT=0.51', C_RED),
        ([[0,0,-1],[0,1,0],[0,0,0]], (0,2), (5.2,4.3), 's03', 'N=1\nW=+1', 'UCT=0.71', C_GREEN),
        ([[0,0,0],[0,1,-1],[0,0,0]], (1,2), (3.2,1.5), 's04', 'N=1\nW=0', 'UCT=0.61', C_GRAY),
        ([[0,0,0],[0,1,0],[-1,0,0]], (2,0), (4.2,1.5), 's05', 'N=1\nW=-1', 'UCT=0.51', C_RED),
    ]
    sel_idx = 0  # s01 selected (highest UCT, tied with s03 but let's say s01)
    
    for i,(board,hl,pos,lbl,nw,uct,vc) in enumerate(zip(
        [(c[0],c[1]) for c in children],
        [c[1] for c in children],
        [c[2] for c in children],
        [c[3] for c in children],
        [c[4] for c in children],
        [c[5] for c in children],
        [c[6] for c in children])):
        is_sel = (i == sel_idx)
        draw_board(ax, pos[0], pos[1], board[0], size=0.3, highlight=board[1],
                   label=f'{lbl}\n{nw}')
        ec = C_BLUE if is_sel else C_GRAY
        lw = 2.5 if is_sel else 1
        edge(ax, (1.2, 3.0), pos, color=ec, lw=lw)
        edge_label(ax, (1.2, 3.0), pos, uct, color=(C_BLUE if is_sel else C_GRAY))

    # Expand s01: its children
    s01_pos = (3.2, 4.3)
    grandchildren = [
        ([[-1,1,0],[0,1,0],[0,0,0]], None, (6.5,4.6), 's011\nv=+1', C_GREEN),
        ([[-1,0,0],[1,1,0],[0,0,0]], None, (6.5,3.8), 's012\nv=+1', C_GREEN),
        ([[-1,0,0],[0,1,1],[0,0,0]], None, (6.5,3.0), 's013\nv=+1', C_GREEN),
        ([[-1,0,0],[0,1,0],[1,0,0]], None, (6.5,2.2), 's014\nv=0', C_GRAY),
    ]
    for board,hl,pos,lbl,vc in grandchildren:
        draw_board(ax, pos[0], pos[1], board, size=0.26, label=lbl)
        arrow(ax, s01_pos, pos, color=C_GREEN, lw=1.2)

    # Selection annotation
    ax.add_patch(FancyBboxPatch((0.3,0.3),2.5,0.8,boxstyle='round,pad=0.1',fc='#E3F2FD',ec=C_BLUE,lw=1))
    ax.text(1.55,0.85,'选择 s01 (UCT最高)',fontsize=9,ha='center',color=C_BLUE,fontweight='bold')
    ax.text(1.55,0.5,'展开4个子节点\nrollout得 v=+1,+1,+1,0',fontsize=8,ha='center',color=C_DARK)
    arrow(ax,(1.55,1.15),(1.2,2.7),color=C_BLUE,lw=1.5,style='--')

    # Backup: s01 updated
    ax.text(3.2,3.55,'N=5\nW=4',fontsize=8,ha='center',color=C_GREEN,fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.1',fc='white',ec=C_GREEN,alpha=0.9))
    ax.text(1.2,2.3,'N=9\nW=4',fontsize=8,ha='center',color=C_NAVY,fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.1',fc='white',ec=C_NAVY,alpha=0.9))

    ax.text(7.5,1.5,'UCT = W/N + c√(ln Np / N)\n选UCT最高的子节点下行',fontsize=9,ha='center',color=C_BLUE,
            bbox=dict(boxstyle='round,pad=0.2',fc='#E3F2FD',ec=C_BLUE))

    plt.tight_layout(); save(fig, 'ttt_iter2.png')

# ── 3. Evolution: rollout → policy → value → AlphaZero ──────────────
def evolution():
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), facecolor='white')
    titles = [
        '(a) 传统 MCTS: 随机 Rollout',
        '(b) AlphaGo: + 策略网络 P(s,a)',
        '(c) AlphaGo Zero: + 价值网络 v(s)',
        '(d) AlphaZero: 单网络 f(s)→(p,v)',
    ]
    colors = [C_ORANGE, C_GOLD, C_RED, C_PURPLE]

    for idx, (ax, title, color) in enumerate(zip(axes.flat, titles, colors)):
        ax.set_xlim(-0.5, 6); ax.set_ylim(-0.5, 4); ax.set_aspect('equal'); ax.axis('off')
        ax.set_title(title, fontsize=11, color=color, fontweight='bold', pad=8)

        # Draw a simple tree: root -> 3 children
        root_pos = (1, 3)
        child_pos = [(3, 3.5), (3, 2.5), (3, 1.5)]

        # root board
        root_b = [[0,0,0],[0,1,0],[0,0,0]]
        draw_board(ax, root_pos[0], root_pos[1], root_b, size=0.28)

        if idx == 0:
            # Traditional: rollout (dashed) from each child
            for i, cp in enumerate(child_pos):
                edge(ax, root_pos, cp, color=C_GRAY, lw=1)
                cb = [[0,0,0],[0,1,0],[0,0,0]]
                cb[0][i] = -1
                draw_board(ax, cp[0], cp[1], cb, size=0.24)
                # rollout dashed
                rp = (cp[0]+1.2, cp[1])
                arrow(ax, cp, rp, color=C_ORANGE, lw=1.2, style='--')
                draw_board(ax, rp[0], rp[1], [[0,-1,0],[1,1,0],[0,0,0]], size=0.2)
                ax.text(rp[0]+0.3, rp[1], '...', fontsize=10, ha='left', va='center', color=C_ORANGE)
            ax.text(5.5, 0.3, '随机走子到终局\n慢，质量差', fontsize=8, ha='center', color=C_ORANGE, style='italic',
                    bbox=dict(boxstyle='round,pad=0.2',fc='#FFF3E0',ec=C_ORANGE))
            ax.text(1, 3.7, 'N,W', fontsize=8, ha='center', color=C_DARK)

        elif idx == 1:
            # AlphaGo: policy network guides selection
            for i, cp in enumerate(child_pos):
                p_vals = ['P=0.6','P=0.2','P=0.2']
                edge(ax, root_pos, cp, color=C_GOLD if i==0 else C_GRAY, lw=2 if i==0 else 1)
                edge_label(ax, root_pos, cp, p_vals[i], color=C_GOLD)
                cb = [[0,0,0],[0,1,0],[0,0,0]]
                cb[0][i] = -1
                draw_board(ax, cp[0], cp[1], cb, size=0.24)
                # still rollout but shorter
                if i==0:
                    rp = (cp[0]+1.2, cp[1])
                    arrow(ax, cp, rp, color=C_ORANGE, lw=1, style='--')
                    ax.text(rp[0]+0.1, rp[1], 'rollout', fontsize=7, ha='left', va='center', color=C_ORANGE)
            ax.text(5.5, 0.3, 'P(s,a) 引导搜索方向\n仍保留 rollout', fontsize=8, ha='center', color=C_GOLD, style='italic',
                    bbox=dict(boxstyle='round,pad=0.2',fc='#FFF8E1',ec=C_GOLD))

        elif idx == 2:
            # AlphaGo Zero: value network replaces rollout
            for i, cp in enumerate(child_pos):
                edge(ax, root_pos, cp, color=C_RED if i==0 else C_GRAY, lw=2 if i==0 else 1)
                edge_label(ax, root_pos, cp, ['P=0.6','P=0.2','P=0.2'][i], color=C_RED)
                cb = [[0,0,0],[0,1,0],[0,0,0]]
                cb[0][i] = -1
                draw_board(ax, cp[0], cp[1], cb, size=0.24)
                # value network
                ax.add_patch(FancyBboxPatch((cp[0]+0.6, cp[1]-0.2),0.8,0.4,boxstyle='round,pad=0.05',fc=C_RED,ec=C_RED,zorder=4))
                v_txt = ['v=0.8','v=0.2','v=0.1'][i]
                ax.text(cp[0]+1.0, cp[1], v_txt, fontsize=7, ha='center', va='center', color='w', fontweight='bold', zorder=5)
            ax.text(5.5, 0.3, 'v(s) 替代 rollout\n一次前向传播', fontsize=8, ha='center', color=C_RED, style='italic',
                    bbox=dict(boxstyle='round,pad=0.2',fc='#FFEBEE',ec=C_RED))

        else:
            # AlphaZero: single network
            for i, cp in enumerate(child_pos):
                edge(ax, root_pos, cp, color=C_PURPLE if i==0 else C_GRAY, lw=2 if i==0 else 1)
                edge_label(ax, root_pos, cp, ['P=0.6','P=0.2','P=0.2'][i], color=C_PURPLE)
                cb = [[0,0,0],[0,1,0],[0,0,0]]
                cb[0][i] = -1
                draw_board(ax, cp[0], cp[1], cb, size=0.24)
                ax.add_patch(FancyBboxPatch((cp[0]+0.5, cp[1]-0.25),1.0,0.5,boxstyle='round,pad=0.05',fc=C_PURPLE,ec=C_PURPLE,zorder=4))
                pv_txt = ['p,v','p,v','p,v'][i]
                ax.text(cp[0]+1.0, cp[1], pv_txt, fontsize=7, ha='center', va='center', color='w', fontweight='bold', zorder=5)
            # single network box at root
            ax.add_patch(FancyBboxPatch((root_pos[0]-0.1, root_pos[1]-0.1),0.2,0.2,boxstyle='round,pad=0.02',fc=C_NAVY,ec=C_NAVY))
            ax.text(5.5, 0.3, 'f(s)→(p,v) 单网络\n策略+价值共享特征', fontsize=8, ha='center', color=C_PURPLE, style='italic',
                    bbox=dict(boxstyle='round,pad=0.2',fc='#F3E5F5',ec=C_PURPLE))

    fig.suptitle('MCTS 的演进：从随机 Rollout 到 AlphaZero 单网络', fontsize=14, color=C_NAVY, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0,0,1,0.96]); save(fig, 'ttt_evolution.png')

if __name__ == "__main__":
    print("Generating tic-tac-toe MCTS diagrams...")
    trad_iter1()
    trad_iter2()
    evolution()
    print("Done!")
