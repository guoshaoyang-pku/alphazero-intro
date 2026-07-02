#!/usr/bin/env python3
"""Generate minimax / alpha-beta / heuristic diagrams, and why-go-fails diagram."""
import os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

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

# ── 1. Minimax tree (chess-like, with leaf values) ──────────────────
def minimax_tree():
    fig, ax = plt.subplots(figsize=(12,6), facecolor='white')
    ax.set_xlim(-0.5,12); ax.set_ylim(-0.5,7); ax.axis('off')
    ax.text(6,6.7,'Minimax 搜索  (冯·诺依曼)',fontsize=14,ha='center',color=C_NAVY,fontweight='bold')
    ax.text(6,6.3,'我方最大化 (MAX), 对手最小化 (MIN) — 深度 d 的完整博弈树',fontsize=11,ha='center',color=C_GRAY)

    # 3 levels: root(MAX,depth2) -> 3 MIN(depth1) -> leaves(depth0)
    root=(6,5.5)
    mins=[(2,3.8),(6,3.8),(10,3.8)]
    leaves = {
        0:[(0.5,1.5),(2,1.5),(3.5,1.5)],
        1:[(5,1.5),(6,1.5),(7,1.5)],
        2:[(8.5,1.5),(10,1.5),(11.5,1.5)],
    }
    leaf_vals = {0:[3,12,8], 1:[2,4,6], 2:[14,5,2]}
    # minimax: min of each group = [3,2,2]; max = 3 -> choose left
    min_vals=[min(leaf_vals[0]),min(leaf_vals[1]),min(leaf_vals[2])]  # [3,2,2]
    best=min(min_vals) # 3 at index 0

    # draw edges
    for i,m in enumerate(mins):
        ax.plot([root[0],m[0]],[root[1],m[1]],'-',color=C_GRAY,lw=1.5)
        for j,lf in enumerate(leaves[i]):
            c = C_RED if leaf_vals[i][j]==min_vals[i] else C_LGRAY
            lw = 2 if leaf_vals[i][j]==min_vals[i] else 1
            ax.plot([m[0],lf[0]],[m[1],lf[1]],'-',color=c,lw=lw)

    # root node
    ax.add_patch(Circle(root,0.32,fc=C_NAVY,ec=C_NAVY,zorder=3))
    ax.text(root[0],root[1],'MAX',fontsize=9,ha='center',va='center',color='w',fontweight='bold',zorder=4)
    ax.text(root[0]+0.5,root[1],'='+str(best),fontsize=12,ha='left',va='center',color=C_GREEN,fontweight='bold')

    # MIN nodes
    for i,m in enumerate(mins):
        is_best = (i==0)
        fc = C_RED if is_best else C_ORANGE
        ax.add_patch(Circle(m,0.28,fc=fc,ec=fc,zorder=3))
        ax.text(m[0],m[1],'MIN',fontsize=8,ha='center',va='center',color='w',fontweight='bold',zorder=4)
        ax.text(m[0],m[1]+0.45,'='+str(min_vals[i]),fontsize=11,ha='center',color=(C_GREEN if is_best else C_DARK),fontweight='bold')

    # leaf nodes
    for i in range(3):
        for j,lf in enumerate(leaves[i]):
            is_min = (leaf_vals[i][j]==min_vals[i])
            fc = C_RED if is_min else C_LGRAY
            ec = C_RED if is_min else C_GRAY
            lc = 'w' if is_min else C_DARK
            ax.add_patch(Circle(lf,0.22,fc=fc,ec=ec,zorder=3))
            ax.text(lf[0],lf[1],str(leaf_vals[i][j]),fontsize=9,ha='center',va='center',color=lc,fontweight='bold',zorder=4)

    # annotations
    ax.text(2,0.8,'min=3',fontsize=9,ha='center',color=C_GREEN,fontweight='bold')
    ax.text(6,0.8,'min=2',fontsize=9,ha='center',color=C_DARK)
    ax.text(10,0.8,'min=2',fontsize=9,ha='center',color=C_DARK)
    ax.annotate('',xy=(2.3,5.5),xytext=(5.6,5.5),arrowprops=dict(arrowstyle='->',color=C_GREEN,lw=2))
    ax.text(4,5.9,'我方选最大=3',fontsize=10,ha='center',color=C_GREEN,fontweight='bold')
    ax.text(6,0.2,'叶节点 = 估值函数 (如象棋子力: 车=9 马=4 兵=1)',fontsize=10,ha='center',color=C_GRAY,style='italic')

    plt.tight_layout(); save(fig,'minimax.png')

# ── 2. Alpha-beta pruning ────────────────────────────────────────────
def alpha_beta():
    fig, ax = plt.subplots(figsize=(11,5.5), facecolor='white')
    ax.set_xlim(-0.5,11); ax.set_ylim(-0.5,6); ax.axis('off')
    ax.text(5.5,5.7,'Alpha-Beta 剪枝',fontsize=14,ha='center',color=C_NAVY,fontweight='bold')
    ax.text(5.5,5.3,'剪掉不可能影响决策的分支 — 不改变结果，只减少搜索量',fontsize=11,ha='center',color=C_GRAY)

    root=(4.5,4.5)
    children=[(1.5,2.8),(4.5,2.8),(7.5,2.8)]
    # child 0: fully evaluated, value 3
    # child 1: first leaf =2, since root MAX already has alpha=3 from child0, 2<3 -> prune rest
    leaf_c0=[(0.3,1.0),(1.5,1.0),(2.7,1.0)]
    val_c0=[3,12,8]
    leaf_c1=[(3.8,1.0),(4.5,1.0),(5.2,1.0)]
    val_c1=[2,None,None]  # 2 then prune
    leaf_c2=[(6.5,1.0),(7.5,1.0),(8.5,1.0)]
    val_c2=[14,5,2]

    # edges
    for c in children:
        ax.plot([root[0],c[0]],[root[1],c[1]],'-',color=C_GRAY,lw=1.5)
    for lf in leaf_c0:
        ax.plot([children[0][0],lf[0]],[children[0][1],lf[1]],'-',color=C_GRAY,lw=1)
    ax.plot([children[1][0],leaf_c1[0][0]],[children[1][1],leaf_c1[0][1]],'-',color=C_GRAY,lw=1)
    # pruned (dashed)
    for lf in leaf_c1[1:]:
        ax.plot([children[1][0],lf[0]],[children[1][1],lf[1]],'--',color=C_GRAY,lw=1,alpha=0.4)
    for lf in leaf_c2:
        ax.plot([children[2][0],lf[0]],[children[2][1],lf[1]],'--',color=C_GRAY,lw=1,alpha=0.4)

    # root
    ax.add_patch(Circle(root,0.3,fc=C_NAVY,ec=C_NAVY,zorder=3))
    ax.text(root[0],root[1],'MAX',fontsize=8,ha='center',va='center',color='w',fontweight='bold',zorder=4)
    ax.text(root[0]+0.45,root[1],'=3',fontsize=12,ha='left',color=C_GREEN,fontweight='bold')

    # child 0 (evaluated, =3)
    ax.add_patch(Circle(children[0],0.26,fc=C_RED,ec=C_RED,zorder=3))
    ax.text(children[0][0],children[0][1],'MIN',fontsize=7,ha='center',va='center',color='w',fontweight='bold',zorder=4)
    ax.text(children[0][0],children[0][1]+0.4,'=3',fontsize=10,ha='center',color=C_GREEN,fontweight='bold')
    for lf,v in zip(leaf_c0,val_c0):
        is_min=(v==3)
        fc=C_RED if is_min else C_LGRAY; ec=C_RED if is_min else C_GRAY; lc='w' if is_min else C_DARK
        ax.add_patch(Circle(lf,0.2,fc=fc,ec=ec,zorder=3))
        ax.text(lf[0],lf[1],str(v),fontsize=8,ha='center',va='center',color=lc,fontweight='bold',zorder=4)

    # child 1 (pruned after first leaf=2 < alpha=3)
    ax.add_patch(Circle(children[1],0.26,fc=C_ORANGE,ec=C_ORANGE,zorder=3))
    ax.text(children[1][0],children[1][1],'MIN',fontsize=7,ha='center',va='center',color='w',fontweight='bold',zorder=4)
    ax.text(children[1][0],children[1][1]+0.4,'<=2\n(剪枝)',fontsize=9,ha='center',color=C_ORANGE,fontweight='bold')
    ax.add_patch(Circle(leaf_c1[0],0.2,fc=C_LGRAY,ec=C_GRAY,zorder=3))
    ax.text(leaf_c1[0][0],leaf_c1[0][1],'2',fontsize=8,ha='center',va='center',color=C_DARK,fontweight='bold',zorder=4)
    for lf in leaf_c1[1:]:
        ax.text(lf[0],lf[1],'X',fontsize=10,ha='center',va='center',color=C_GRAY,zorder=4)
        ax.add_patch(Circle(lf,0.2,fc='white',ec=C_GRAY,linestyle='--',zorder=3))
    ax.text(4.5,0.4,'2 < α=3 → 剪枝',fontsize=9,ha='center',color=C_ORANGE,fontweight='bold')

    # child 2 (pruned entirely - not needed since root already has 3)
    ax.add_patch(Circle(children[2],0.26,fc='white',ec=C_GRAY,linestyle='--',zorder=3))
    ax.text(children[2][0],children[2][1],'MIN',fontsize=7,ha='center',va='center',color=C_GRAY,fontweight='bold',zorder=4)
    ax.text(children[2][0],children[2][1]+0.4,'(整体\n剪枝)',fontsize=9,ha='center',color=C_GRAY,fontweight='bold')
    for lf in leaf_c2:
        ax.text(lf[0],lf[1],'X',fontsize=10,ha='center',va='center',color=C_GRAY,zorder=4)
        ax.add_patch(Circle(lf,0.2,fc='white',ec=C_GRAY,linestyle='--',zorder=3))

    ax.text(9.5,3.0,'α=已找到的\n最好下界(MAX)\nβ=对手能\n容忍的上界(MIN)\n\nα≥β → 剪枝',fontsize=9,ha='center',va='center',color=C_DARK,
            bbox=dict(boxstyle='round,pad=0.3',fc='#F5F5F5',ec=C_GRAY))

    plt.tight_layout(); save(fig,'alpha_beta.png')

# ── 3. Why Go fails: branching factor + evaluation ───────────────────
def why_go_fails():
    fig, ax = plt.subplots(figsize=(11,5.5), facecolor='white')
    ax.set_xlim(0,11); ax.set_ylim(0,6); ax.axis('off')
    ax.text(5.5,5.6,'为什么围棋不能用 Minimax？',fontsize=14,ha='center',color=C_NAVY,fontweight='bold')

    # Two columns
    # Left: branching factor
    ax.add_patch(FancyBboxPatch((0.3,0.5),5,4.3,boxstyle='round,pad=0.15',fc='#FFEBEE',ec=C_RED,lw=1.5))
    ax.text(2.8,4.5,'问题 1: 分支因子太大',fontsize=13,ha='center',color=C_RED,fontweight='bold')
    rows=[
        ('国际象棋','分支因子 ~35','深度 6-7 层可搜'),
        ('围棋 19×19','分支因子 ~250','深度 4 层已极难'),
    ]
    for i,(g,bf,d) in enumerate(rows):
        y=3.7-i*0.9
        ax.text(0.7,y,g,fontsize=11,ha='left',color=C_DARK,fontweight='bold')
        ax.text(2.6,y,bf,fontsize=11,ha='left',color=C_DARK)
        ax.text(4.8,y,d,fontsize=10,ha='right',color=C_GRAY)
    ax.text(2.8,1.3,'35^6 ≈ 18亿  vs  250^4 ≈ 39亿',fontsize=11,ha='center',color=C_RED,fontweight='bold')
    ax.text(2.8,0.8,'同样算力下围棋搜索深度远不够',fontsize=9,ha='center',color=C_GRAY,style='italic')

    # Right: evaluation function
    ax.add_patch(FancyBboxPatch((5.7,0.5),5,4.3,boxstyle='round,pad=0.15',fc='#FFF3E0',ec=C_ORANGE,lw=1.5))
    ax.text(8.2,4.5,'问题 2: 估值函数难写',fontsize=13,ha='center',color=C_ORANGE,fontweight='bold')
    ax.text(6.0,3.8,'象棋: 子力价值明确',fontsize=11,ha='left',color=C_GREEN,fontweight='bold')
    ax.text(6.0,3.4,'车=9  马/炮=4  兵=1  →  简单求和',fontsize=10,ha='left',color=C_DARK)
    ax.text(6.0,2.7,'围棋: 局面价值极难评估',fontsize=11,ha='left',color=C_RED,fontweight='bold')
    ax.text(6.0,2.3,'• 一子的价值随全局形势剧烈变化',fontsize=9.5,ha='left',color=C_DARK)
    ax.text(6.0,1.9,'• "厚薄""势""实地" 难以量化',fontsize=9.5,ha='left',color=C_DARK)
    ax.text(6.0,1.5,'• 深层局面并不比浅层更容易评估',fontsize=9.5,ha='left',color=C_DARK)
    ax.text(8.2,0.8,'→ Minimax 需要好的叶节点估值，围棋给不了',fontsize=10,ha='center',color=C_ORANGE,fontweight='bold',style='italic')

    plt.tight_layout(); save(fig,'why_go_fails.png')

# ── 4. Heuristic search (move ordering by value) ─────────────────────
def heuristic():
    fig, ax = plt.subplots(figsize=(11,5), facecolor='white')
    ax.set_xlim(0,11); ax.set_ylim(0,5.5); ax.axis('off')
    ax.text(5.5,5.1,'Heuristic 启发式搜索：优先搜索好局面',fontsize=14,ha='center',color=C_NAVY,fontweight='bold')

    # chess board with piece values
    ax.text(2.5,4.5,'象棋子力估值',fontsize=12,ha='center',color=C_GREEN,fontweight='bold')
    pieces=[('车',9,C_RED),('马',4,C_ORANGE),('炮',4,C_ORANGE),('相',2,C_GOLD),('兵',1,C_GRAY)]
    for i,(name,val,c) in enumerate(pieces):
        x=0.8+i*0.85
        ax.add_patch(FancyBboxPatch((x-0.3,3.3),0.6,0.6,boxstyle='round,pad=0.05',fc=c,ec=c,alpha=0.8,zorder=2))
        ax.text(x,3.6,name,fontsize=11,ha='center',va='center',color='w',fontweight='bold',zorder=3)
        ax.text(x,3.0,'='+str(val),fontsize=10,ha='center',color=c,fontweight='bold')
    ax.text(2.5,2.4,'叶节点 = 双方子力差\n(简单可计算的估值函数)',fontsize=9,ha='center',color=C_DARK)
    ax.text(2.5,1.7,'→ Minimax 用此估值\n   搜索深度 6-7 层',fontsize=9,ha='center',color=C_GREEN)

    # arrow
    ax.annotate('',xy=(5.3,3.0),xytext=(4.5,3.0),arrowprops=dict(arrowstyle='->',color=C_NAVY,lw=2))
    ax.text(4.9,3.3,'指导',fontsize=9,ha='center',color=C_NAVY)

    # move ordering: search promising first
    ax.add_patch(FancyBboxPatch((5.5,1.0),5,3.8,boxstyle='round,pad=0.12',fc='#E3F2FD',ec=C_BLUE,lw=1.5))
    ax.text(8,4.4,'Move Ordering (走法排序)',fontsize=12,ha='center',color=C_BLUE,fontweight='bold')
    moves=[
        ('吃车 (+9)','优先搜索',C_RED,3.7),
        ('吃马 (+4)','优先搜索',C_ORANGE,3.1),
        ('将军','优先搜索',C_GOLD,2.5),
        ('普通走法 (0)','延迟/剪枝',C_GRAY,1.9),
        ('被动防守 (-2)','延迟/剪枝',C_GRAY,1.3),
    ]
    for name,action,c,y in moves:
        ax.text(6,y,name,fontsize=10,ha='left',color=c,fontweight='bold')
        ax.text(9.5,y,action,fontsize=9,ha='center',color=C_DARK)
    ax.text(8,0.5,'先搜子力收益大的走法 → α-β 剪枝更高效 (剪得更多)',fontsize=9,ha='center',color=C_BLUE,style='italic')

    plt.tight_layout(); save(fig,'heuristic.png')

if __name__=="__main__":
    print("Generating minimax/heuristic diagrams...")
    minimax_tree(); alpha_beta(); why_go_fails(); heuristic()
    print("Done!")
