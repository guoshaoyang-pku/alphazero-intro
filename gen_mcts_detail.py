#!/usr/bin/env python3
"""Generate 4 detailed MCTS phase diagrams (one per phase), same tree, different highlight."""
import os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch

CN_FONT="Noto Sans CJK SC"
matplotlib.rcParams['font.sans-serif']=[CN_FONT,'STHeiti','Heiti TC']
matplotlib.rcParams['axes.unicode_minus']=False

ASSET_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets")
C_NAVY="#0D1B3E";C_BLUE="#1565C0";C_TEAL="#00897B";C_GREEN="#2E7D32"
C_GOLD="#E8A838";C_RED="#E53935";C_ORANGE="#FB8C00";C_GRAY="#BDBDBD"
C_LGRAY="#E0E0E0";C_WHITE="#FFFFFF";C_DARK="#1A1A2E"
DPI=200

# shared tree
N={
 'R':(3,4.2),'A':(1.5,3.0),'B':(3,3.0),'C':(4.5,3.0),
 'A1':(0.8,1.8),'A2':(2.2,1.8),'B1':(2.5,1.8),'B2':(3.5,1.8),
 'C1':(3.8,1.8),'C2':(5.2,1.8),
}
E=[('R','A'),('R','B'),('R','C'),('A','A1'),('A','A2'),('B','B1'),('B','B2'),('C','C1'),('C','C2')]

def save(fig,name):
    path=os.path.join(ASSET_DIR,name)
    fig.savefig(path,dpi=DPI,bbox_inches='tight',facecolor='white',edgecolor='none',pad_inches=0.12)
    plt.close(fig); print(f"  [+] {name}"); return path

def node(ax,x,y,r=0.22,fc=C_LGRAY,ec=C_GRAY,lw=1.5,label=None,lcolor=C_DARK,fs=9,z=3):
    ax.add_patch(Circle((x,y),r,fc=fc,ec=ec,lw=lw,zorder=z))
    if label: ax.text(x,y,label,fontsize=fs,ha='center',va='center',color=lcolor,fontweight='bold',zorder=z+1)

def line(ax,p,q,c=C_GRAY,lw=1.5,ls='-',z=1):
    ax.plot([p[0],q[0]],[p[1],q[1]],ls,color=c,lw=lw,zorder=z)

def arrow(ax,p,q,c,lw=2.5,ls='-'):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='->,head_width=6,head_length=8',color=c,lw=lw,linestyle=ls,zorder=2))

def base_tree(ax, xlim=(-0.2,6.2), ylim=(0.2,5)):
    ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_aspect('equal');ax.axis('off')

# ── 1. Selection ─────────────────────────────────────────────────────
def sel():
    fig,ax=plt.subplots(figsize=(5.8,5),facecolor='white')
    base_tree(ax)
    path={('R','B'),('B','B1')}
    for p,q in E:
        c=C_BLUE if (p,q) in path else C_LGRAY
        lw=3.5 if (p,q) in path else 1.2
        line(ax,N[p],N[q],c=c,lw=lw)
    for nm in ['A','C','A1','A2','B2','C1','C2']:
        node(ax,*N[nm])
    node(ax,*N['R'],fc=C_BLUE,ec=C_BLUE,lcolor=C_WHITE)
    node(ax,*N['B'],fc=C_BLUE,ec=C_BLUE,lcolor=C_WHITE)
    node(ax,*N['B1'],fc=C_GOLD,ec=C_GOLD,lcolor=C_DARK)
    # UCT values at R's children
    ax.text(1.5,3.38,'UCT=0.71',fontsize=8.5,ha='center',color=C_GRAY)
    ax.text(3,3.38,'UCT=0.85',fontsize=9,ha='center',color=C_BLUE,fontweight='bold')
    ax.text(4.5,3.38,'UCT=0.68',fontsize=8.5,ha='center',color=C_GRAY)
    ax.text(2.5,2.18,'0.92',fontsize=9,ha='center',color=C_GOLD,fontweight='bold')
    ax.text(3.5,2.18,'0.55',fontsize=8.5,ha='center',color=C_GRAY)
    arrow(ax,(3,3.95),(3,3.25),C_BLUE)
    arrow(ax,(2.75,2.75),(2.5,2.05),C_BLUE)
    ax.text(3,4.7,'根节点 s',fontsize=10,ha='center',color=C_NAVY,fontweight='bold')
    ax.text(1.7,1.8,'叶节点',fontsize=9,ha='right',color=C_GOLD,fontweight='bold')
    ax.text(6.1,4.8,'① Selection',fontsize=13,ha='right',color=C_BLUE,fontweight='bold')
    ax.text(6.1,0.5,'从根节点出发\n沿 UCT 最大的子节点\n递归下行至叶节点',fontsize=9.5,ha='right',color=C_DARK)
    save(fig,'mcts_1_selection.png')

# ── 2. Expansion ─────────────────────────────────────────────────────
def exp():
    fig,ax=plt.subplots(figsize=(5.8,5),facecolor='white')
    base_tree(ax,ylim=(0,5))
    Nb={'B1a':(2.5,0.55)}
    E2=E+[('B1','B1a')]
    for p,q in E2:
        c=C_GREEN if (p,q)==('B1','B1a') else C_LGRAY
        lw=3.5 if (p,q)==('B1','B1a') else 1.2
        line(ax,{**N,**Nb}[p],{**N,**Nb}[q],c=c,lw=lw)
    for nm in ['R','A','B','C','A1','A2','B2','C1','C2']:
        node(ax,*N[nm])
    node(ax,*N['B1'],fc=C_BLUE,ec=C_BLUE,lcolor=C_WHITE)
    node(ax,*Nb['B1a'],fc=C_GREEN,ec=C_GREEN,lcolor=C_WHITE)
    arrow(ax,(2.5,1.55),(2.5,0.8),C_GREEN)
    ax.text(2.5,0.2,'新节点 s\'',fontsize=9,ha='center',color=C_GREEN,fontweight='bold')
    ax.text(1.7,1.8,'选中的叶',fontsize=9,ha='right',color=C_BLUE,fontweight='bold')
    ax.text(6.1,4.8,'② Expansion',fontsize=13,ha='right',color=C_GREEN,fontweight='bold')
    ax.text(6.1,0.4,'在叶节点下\n添加一个\n未尝试的合法动作',fontsize=9.5,ha='right',color=C_DARK)
    save(fig,'mcts_2_expansion.png')

# ── 3. Simulation ────────────────────────────────────────────────────
def sim():
    fig,ax=plt.subplots(figsize=(6.2,5),facecolor='white')
    base_tree(ax,ylim=(-1.9,5))
    for p,q in E:
        line(ax,N[p],N[q],c=C_LGRAY,lw=1.2)
    line(ax,N['B1'],(2.5,0.55),c=C_LGRAY,lw=1.2)
    for nm in N:
        node(ax,*N[nm])
    node(ax,*N['B1'],fc=C_BLUE,ec=C_BLUE,lcolor=C_WHITE)
    node(ax,2.5,0.55,fc=C_GREEN,ec=C_GREEN,lcolor=C_WHITE)
    # rollout dashed path (traditional)
    roll=[(2.5,0.55),(2.9,-0.3),(2.1,-0.9),(3.0,-1.45)]
    for i in range(len(roll)-1):
        ax.plot([roll[i][0],roll[i+1][0]],[roll[i][1],roll[i+1][1]],'--',color=C_ORANGE,lw=2.2,zorder=2)
    for x,y in roll[1:-1]:
        node(ax,x,y,r=0.13,fc=C_ORANGE,ec=C_ORANGE)
    ax.add_patch(FancyBboxPatch((2.55,-1.78),0.9,0.32,boxstyle='round,pad=0.05',fc=C_RED,ec=C_RED,zorder=4))
    ax.text(3,-1.62,'z = ±1',fontsize=9,ha='center',va='center',color=C_WHITE,fontweight='bold',zorder=5)
    ax.text(1.4,-0.6,'传统: 随机 rollout\n到终局',fontsize=8.5,ha='right',color=C_ORANGE,style='italic')
    # AlphaGo Zero comparison box
    ax.add_patch(FancyBboxPatch((3.9,-1.6),2.2,2.1,boxstyle='round,pad=0.12',fc='#FFF3E0',ec=C_GOLD,lw=1.5))
    ax.text(5.0,0.3,'AlphaGo Zero',fontsize=10,ha='center',color=C_ORANGE,fontweight='bold')
    ax.text(5.0,-0.15,'不做随机 rollout',fontsize=9,ha='center',color=C_DARK)
    ax.text(5.0,-0.7,'直接调用神经网络\n$v, P = f_\\theta(s)$',fontsize=10,ha='center',color=C_RED,fontweight='bold')
    ax.text(5.0,-1.35,'一次前向传播',fontsize=8.5,ha='center',color=C_GRAY)
    ax.text(6.1,4.8,'③ Simulation',fontsize=13,ha='right',color=C_ORANGE,fontweight='bold')
    save(fig,'mcts_3_simulation.png')

# ── 4. Backpropagation ───────────────────────────────────────────────
def bp():
    fig,ax=plt.subplots(figsize=(6,5),facecolor='white')
    base_tree(ax,ylim=(0,5))
    Nb={'B1a':(2.5,0.55)}
    alln={**N,**Nb}
    alledge=E+[('B1','B1a')]
    bpath={('B1a','B1'),('B1','B'),('B','R')}
    for p,q in alledge:
        c=C_RED if (p,q) in bpath else C_LGRAY
        lw=3.5 if (p,q) in bpath else 1.2
        line(ax,alln[p],alln[q],c=c,lw=lw)
    for nm in ['A','C','A1','A2','B2','C1','C2']:
        node(ax,*N[nm])
    for nm in ['R','B','B1']:
        node(ax,*N[nm],fc=C_RED,ec=C_RED,lcolor=C_WHITE)
    node(ax,*Nb['B1a'],fc=C_GREEN,ec=C_GREEN,lcolor=C_WHITE)
    arrow(ax,(2.5,0.8),(2.5,1.55),C_RED)
    arrow(ax,(2.6,2.05),(2.95,2.75),C_RED)
    arrow(ax,(3,3.25),(3,3.95),C_RED)
    ax.text(3.25,0.55,'v',fontsize=12,ha='left',color=C_GREEN,fontweight='bold')
    ax.text(3.3,1.8,'N: 0→1\nQ: 0→v',fontsize=8.5,ha='left',color=C_RED,fontweight='bold')
    ax.text(3.3,3.0,'N: 5→6\nQ←(5Q+v)/6',fontsize=8.5,ha='left',color=C_RED,fontweight='bold')
    ax.text(3.3,4.2,'N: 12→13\nQ←(12Q+v)/13',fontsize=8.5,ha='left',color=C_RED,fontweight='bold')
    ax.text(6.0,4.8,'④ Backprop',fontsize=13,ha='right',color=C_RED,fontweight='bold')
    ax.text(6.0,0.5,'沿路径回传 v\n更新 N(s,a) 与 Q(s,a)\nreturn -v（对手视角）',fontsize=9.5,ha='right',color=C_DARK)
    save(fig,'mcts_4_backprop.png')

if __name__=="__main__":
    print("Generating MCTS detail diagrams...")
    sel();exp();sim();bp()
    print("Done!")
