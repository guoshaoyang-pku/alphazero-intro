#!/usr/bin/env python3
"""Generate traditional MCTS diagrams (complete 4-phase with rollout, UCT formula, tree growth)."""
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
C_LGRAY="#E0E0E0";C_WHITE="#FFFFFF";C_DARK="#1A1A2E";C_PURPLE="#7B1FA2"
DPI=200

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

# ── 1. Traditional MCTS full 4-phase (with rollout to terminal) ──────
def trad_full():
    fig,ax=plt.subplots(figsize=(12,5),facecolor='white')
    ax.set_xlim(0,12);ax.set_ylim(0,5.5);ax.axis('off')
    ax.text(6,5.2,'传统 MCTS 完整四阶段  (含 rollout 到终局)',fontsize=14,ha='center',color=C_NAVY,fontweight='bold')

    # Phase 1: Selection (tree with path highlighted)
    ax.text(1.5,4.6,'① 选择 Selection',fontsize=11,ha='center',color=C_BLUE,fontweight='bold')
    N1={'R':(1.5,4.0),'A':(1.0,3.2),'B':(2.0,3.2),'A1':(0.7,2.4),'A2':(1.3,2.4),'B1':(1.7,2.4),'B2':(2.3,2.4)}
    E1=[('R','A'),('R','B'),('A','A1'),('A','A2'),('B','B1'),('B','B2')]
    for p,q in E1:
        c=C_BLUE if (p,q) in {('R','B'),('B','B1')} else C_LGRAY
        lw=2.5 if (p,q) in {('R','B'),('B','B1')} else 1
        line(ax,N1[p],N1[q],c=c,lw=lw)
    for nm in N1:
        fc=C_BLUE if nm in {'R','B','B1'} else C_LGRAY
        lc=C_WHITE if nm in {'R','B','B1'} else C_DARK
        node(ax,*N1[nm],fc=fc,ec=fc,lcolor=lc)
    ax.text(1.5,1.9,'沿 UCT 下行',fontsize=8,ha='center',color=C_BLUE)

    # Phase 2: Expansion
    ax.text(4.5,4.6,'② 扩展 Expansion',fontsize=11,ha='center',color=C_GREEN,fontweight='bold')
    N2={**N1,'C':(2.0,1.6)}
    N2['B1']=(2.0,2.4)
    E2=[('R','A'),('R','B'),('A','A1'),('A','A2'),('B','B1'),('B','B2'),('B1','C')]
    for p,q in E2:
        c=C_GREEN if (p,q)==('B1','C') else C_LGRAY
        lw=2.5 if (p,q)==('B1','C') else 1
        line(ax,N2[p],N2[q],c=c,lw=lw)
    for nm in N2:
        fc=C_GREEN if nm=='C' else C_LGRAY
        lc=C_WHITE if nm=='C' else C_DARK
        node(ax,*N2[nm],fc=fc,ec=fc,lcolor=lc)
    ax.text(4.5,1.1,'新增子节点 C',fontsize=8,ha='center',color=C_GREEN)

    # Phase 3: Simulation (rollout - dashed to terminal)
    ax.text(7.5,4.6,'③ 模拟 Simulation',fontsize=11,ha='center',color=C_ORANGE,fontweight='bold')
    # tree small
    node(ax,7.5,4.0,fc=C_GREEN,ec=C_GREEN,lcolor=C_WHITE,label='C')
    # rollout dashed
    roll=[(7.5,3.7),(7.2,3.0),(7.8,2.4),(7.3,1.8),(7.7,1.2)]
    for i in range(len(roll)-1):
        ax.plot([roll[i][0],roll[i+1][0]],[roll[i][1],roll[i+1][1]],'--',color=C_ORANGE,lw=2,zorder=2)
    for x,y in roll[1:-1]:
        node(ax,x,y,r=0.12,fc=C_ORANGE,ec=C_ORANGE)
    # terminal
    ax.add_patch(FancyBboxPatch((7.3,0.7),0.8,0.35,boxstyle='round,pad=0.05',fc=C_RED,ec=C_RED,zorder=4))
    ax.text(7.7,0.87,'胜/负',fontsize=8,ha='center',va='center',color='w',fontweight='bold',zorder=5)
    ax.text(7.5,0.3,'随机 rollout 至终局',fontsize=8,ha='center',color=C_ORANGE)

    # Phase 4: Backprop
    ax.text(10.5,4.6,'④ 回传 Backprop',fontsize=11,ha='center',color=C_RED,fontweight='bold')
    N4={'R':(10.5,4.0),'B':(10.5,3.2),'B1':(10.5,2.4),'C':(10.5,1.6)}
    E4=[('C','B1'),('B1','B'),('B','R')]
    for p,q in E4:
        line(ax,N4[p],N4[q],c=C_RED,lw=2.5)
    for nm in N4:
        node(ax,*N4[nm],fc=C_RED,ec=C_RED,lcolor=C_WHITE)
    # annotations
    ax.text(11.1,4.0,'10/15',fontsize=8,ha='left',color=C_RED,fontweight='bold')
    ax.text(11.1,3.2,'7/10',fontsize=8,ha='left',color=C_RED,fontweight='bold')
    ax.text(11.1,2.4,'4/5',fontsize=8,ha='left',color=C_RED,fontweight='bold')
    ax.text(11.1,1.6,'1/1',fontsize=8,ha='left',color=C_RED,fontweight='bold')
    ax.text(10.5,1.0,'胜/总 沿路径更新',fontsize=8,ha='center',color=C_RED)

    # arrows between phases
    for x in [3.0,6.0,9.0]:
        ax.text(x,3.0,'→',fontsize=18,ha='center',va='center',color=C_GOLD,fontweight='bold')

    plt.tight_layout(); save(fig,'trad_mcts_full.png')

# ── 2. Traditional UCT formula (standard form) ──────────────────────
def trad_uct():
    fig,ax=plt.subplots(figsize=(11,5),facecolor='white')
    ax.set_xlim(0,11);ax.set_ylim(0,5.5);ax.axis('off')
    ax.text(5.5,5.1,'传统 UCT 公式  (Kocsis & Szepesvari, 2006)',fontsize=14,ha='center',color=C_NAVY,fontweight='bold')

    # formula - standard UCB1 form
    ax.text(5.5,3.9,r'$UCT(i) = \frac{w_i}{n_i} + c\sqrt{\frac{\ln N}{n_i}}$',
            fontsize=24,ha='center',va='center',color=C_NAVY)
    ax.text(2.0,3.3,'利用',fontsize=11,ha='center',color=C_BLUE,fontweight='bold')
    ax.text(5.5,3.3,'探索',fontsize=11,ha='center',color=C_ORANGE,fontweight='bold')

    # annotations
    items=[
        (2.0,2.0,'$w_i/n_i$','第 i 个子节点\n平均胜率\n(利用项)',C_BLUE),
        (5.5,2.0,'$\\sqrt{\\ln N/n_i}$','N=父节点总访问\nn_i=该子访问\n访问少→探索大',C_ORANGE),
        (9.0,2.0,'$c$','探索常数\n通常 $c=\\sqrt{2}$\n或 $c=2$',C_PURPLE),
    ]
    for x,y,f,d,c in items:
        ax.add_patch(FancyBboxPatch((x-1.4,y-0.7),2.8,1.5,boxstyle='round,pad=0.1',fc=c,ec=c,alpha=0.12))
        ax.text(x,y+0.25,f,fontsize=15,ha='center',va='center',color=c,fontweight='bold')
        ax.text(x,y-0.3,d,fontsize=9,ha='center',va='center',color=C_DARK)

    # key difference note
    ax.add_patch(FancyBboxPatch((0.5,0.2),10,0.85,boxstyle='round,pad=0.1',fc='#FFF8E1',ec=C_GOLD,lw=1.5))
    ax.text(5.5,0.75,'与 AlphaGo Zero PUCT 的关键区别',fontsize=11,ha='center',color=C_GOLD,fontweight='bold')
    ax.text(5.5,0.4,'传统: $\\sqrt{\\ln N}$ (无先验)   vs   PUCT: $\\sqrt{N}\\cdot P(s,a)$ (神经网络先验引导)',fontsize=10,ha='center',color=C_DARK)

    plt.tight_layout(); save(fig,'trad_uct.png')

# ── 3. Tree growth over iterations ──────────────────────────────────
def tree_growth():
    fig,axes=plt.subplots(1,3,figsize=(12,4),facecolor='white')
    titles=['初始 (1次模拟)','10 次模拟后','100 次模拟后']
    for idx,(ax,title) in enumerate(zip(axes,titles)):
        ax.set_xlim(-0.3,2.3);ax.set_ylim(-0.3,2.3);ax.set_aspect('equal');ax.axis('off')
        ax.set_title(title,fontsize=12,color=C_NAVY,fontweight='bold',pad=8)
        np.random.seed(idx*7+1)
        if idx==0:
            # just root + 1 child
            node(ax,1,2,fc=C_NAVY,ec=C_NAVY,lcolor=C_WHITE,label='R')
            node(ax,1,1.2,fc=C_LGRAY,ec=C_GRAY)
            line(ax,(1,2),(1,1.2))
        elif idx==1:
            # small tree
            node(ax,1,2,fc=C_NAVY,ec=C_NAVY,lcolor=C_WHITE,label='R')
            for i,(x,y) in enumerate([(0.5,1.2),(1.0,1.2),(1.5,1.2)]):
                line(ax,(1,2),(x,y))
                fc=C_BLUE if i==1 else C_LGRAY
                node(ax,x,y,fc=fc,ec=(C_BLUE if i==1 else C_GRAY),lcolor=(C_WHITE if i==1 else C_DARK))
                # one grandchild
                if i==1:
                    line(ax,(x,y),(x+0.1,0.5))
                    node(ax,x+0.1,0.5,fc=C_GOLD,ec=C_GOLD,lcolor=C_DARK)
        else:
            # bigger asymmetric tree (more on good branch)
            node(ax,1,2,fc=C_NAVY,ec=C_NAVY,lcolor=C_WHITE,label='R')
            # good branch (left, more explored)
            for i in range(4):
                y=1.4-i*0.35
                x=0.6+np.random.randn()*0.1
                if i==0:
                    line(ax,(1,2),(x,y))
                else:
                    line(ax,(0.6,1.4-(i-1)*0.35),(x,y))
                node(ax,x,y,r=0.13,fc=C_BLUE if i<3 else C_LGRAY,ec=(C_BLUE if i<3 else C_GRAY))
            # less explored branch (right)
            for i in range(2):
                y=1.2-i*0.4
                x=1.5
                if i==0:
                    line(ax,(1,2),(x,y))
                else:
                    line(ax,(1.5,1.2),(x,y))
                node(ax,x,y,r=0.13,fc=C_LGRAY,ec=C_GRAY)
        if idx==2:
            ax.text(0.6,0.1,'资源集中在\n有前途分支',fontsize=8,ha='center',color=C_BLUE,fontweight='bold')
            ax.text(1.5,0.5,'少探索',fontsize=8,ha='center',color=C_GRAY)

    fig.suptitle('MCTS 搜索树的非对称增长  (算力集中在有价值的分支)',fontsize=13,color=C_NAVY,fontweight='bold',y=1.02)
    plt.tight_layout(); save(fig,'tree_growth.png')

if __name__=="__main__":
    print("Generating traditional MCTS diagrams...")
    trad_full();trad_uct();tree_growth()
    print("Done!")
