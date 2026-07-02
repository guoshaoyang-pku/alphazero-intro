#!/usr/bin/env python3
"""Generate design-tradeoff diagrams: why-descend-to-leaf, and complexity comparison."""
import os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch, Rectangle
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
    fig.savefig(path,dpi=DPI,bbox_inches='tight',facecolor='white',edgecolor='none',pad_inches=0.12)
    plt.close(fig); print(f"  [+] {name}"); return path

# ── 1. Why descend to leaf? Only decide at root? ────────────────────
def why_leaf():
    fig,ax=plt.subplots(figsize=(11,6),facecolor='white')
    ax.set_xlim(0,11);ax.set_ylim(0,7);ax.axis('off')

    # left: shallow (1-ply) - greedy
    ax.text(2.6,6.6,'方案 A: 只看一层 (贪心)',fontsize=13,ha='center',color=C_RED,fontweight='bold')
    # root
    ax.add_patch(Circle((2.6,5.4),0.3,fc=C_NAVY,ec=C_NAVY,zorder=3))
    ax.text(2.6,5.4,'s0',fontsize=11,ha='center',va='center',color='w',fontweight='bold',zorder=4)
    for i,x in enumerate([1.4,2.6,3.8]):
        ax.plot([2.6,x],[5.1,4.2],'-',color=C_GRAY,lw=1.5)
        ax.add_patch(Circle((x,4.2),0.22,fc=C_LGRAY,ec=C_GRAY,zorder=3))
        ax.text(x,3.8,f'v={0.6-i*0.2:.1f}',fontsize=9,ha='center',color=C_RED)
    ax.text(2.6,3.2,'只评估直接子节点\n无法前瞻 → 短视',fontsize=10,ha='center',color=C_RED,style='italic')
    ax.add_patch(FancyBboxPatch((0.5,2.6),4.2,0.5,boxstyle='round,pad=0.08',fc='#FFEBEE',ec=C_RED,lw=1))
    ax.text(2.6,2.85,'X 无 lookahead，错过陷阱',fontsize=10,ha='center',color=C_RED,fontweight='bold')

    # right: MCTS descend to leaf
    ax.text(8.2,6.6,'方案 B: MCTS 下行到叶子',fontsize=13,ha='center',color=C_GREEN,fontweight='bold')
    # root
    ax.add_patch(Circle((8.2,5.8),0.3,fc=C_NAVY,ec=C_NAVY,zorder=3))
    ax.text(8.2,5.8,'s0',fontsize=11,ha='center',va='center',color='w',fontweight='bold',zorder=4)
    ax.text(8.6,5.9,'← 唯一决策点',fontsize=9,ha='left',color=C_NAVY,fontweight='bold')
    # path
    nodes=[(8.2,5.8),(7.4,4.9),(6.8,4.0),(7.2,3.1)]
    for i in range(len(nodes)-1):
        ax.add_patch(FancyArrowPatch(nodes[i],nodes[i+1],arrowstyle='->,head_width=5,head_length=7',color=C_BLUE,lw=2.2,zorder=2))
    for i,(x,y) in enumerate(nodes[1:-1]):
        ax.add_patch(Circle((x,y),0.2,fc=C_BLUE,ec=C_BLUE,zorder=3))
    # leaf
    ax.add_patch(Circle(nodes[-1],0.24,fc=C_GOLD,ec=C_GOLD,zorder=3))
    ax.text(nodes[-1][0],nodes[-1][1],'v',fontsize=11,ha='center',va='center',color=C_DARK,fontweight='bold',zorder=4)
    ax.text(nodes[-1][0]+0.4,nodes[-1][1]+0.15,'叶子\n网络评估',fontsize=8.5,ha='left',color=C_GOLD,fontweight='bold')
    # side branches (explored)
    for x in [9.0,7.0]:
        ax.plot([8.2,x],[5.5,4.9],'-',color=C_LGRAY,lw=1)
        ax.add_patch(Circle((x,4.9),0.15,fc=C_LGRAY,ec=C_GRAY,zorder=2))
    # depth annotation
    ax.annotate('',xy=(6.3,3.1),xytext=(6.3,5.8),arrowprops=dict(arrowstyle='<->',color=C_GRAY,lw=1))
    ax.text(6.0,4.45,'深度 d\n(前瞻)',fontsize=9,ha='center',va='center',color=C_GRAY,rotation=90)
    ax.text(8.2,2.6,'下行到叶子 → 评估完整变化\n深层选择=资源调度，非最终落子',fontsize=10,ha='center',color=C_GREEN,style='italic')
    ax.add_patch(FancyBboxPatch((5.8,2.0),4.8,0.5,boxstyle='round,pad=0.08',fc='#E8F5E9',ec=C_GREEN,lw=1))
    ax.text(8.2,2.25,'V lookahead，评估长远后果',fontsize=10,ha='center',color=C_GREEN,fontweight='bold')

    # bottom: the key insight
    ax.add_patch(FancyBboxPatch((0.5,0.5),10,1.1,boxstyle='round,pad=0.12',fc='#0D1B3E',ec='#0D1B3E'))
    ax.text(5.5,1.35,'核心洞察',fontsize=12,ha='center',color=C_GOLD,fontweight='bold')
    ax.text(5.5,0.85,'最终决策只在根节点 s0 一层（看 N(s0,a) 分布）；下行到叶子是为了把搜索预算分配到有前途的分支，做 lookahead',
            fontsize=11,ha='center',color='w')
    plt.tight_layout(); save(fig,'why_leaf.png')

# ── 2. Complexity: traditional rollout vs AlphaGo Zero ──────────────
def complexity_compare():
    fig,ax=plt.subplots(figsize=(11,5.8),facecolor='white')
    ax.set_xlim(0,11);ax.set_ylim(0,7);ax.axis('off')

    ax.text(5.5,6.6,'每步落子的计算复杂度',fontsize=15,ha='center',color=C_NAVY,fontweight='bold')

    # left: traditional
    ax.add_patch(FancyBboxPatch((0.3,1.0),5.1,5.0,boxstyle='round,pad=0.12',fc='#FFF3E0',ec=C_ORANGE,lw=1.5))
    ax.text(2.85,5.7,'传统 MCTS (rollout)',fontsize=13,ha='center',color=C_ORANGE,fontweight='bold')
    # illustrate: N simulations, each rollout length L
    # draw N paths
    for i in range(5):
        y0=5.0-i*0.15
        xs=np.linspace(0.7,4.8,8)
        ys=y0-np.arange(8)*0.45+np.random.RandomState(i).randn(8)*0.05
        ax.plot(xs,ys,'-',color=C_ORANGE,lw=1,alpha=0.5)
        ax.plot(xs[-1],ys[-1],'o',color=C_RED,markersize=4)
    ax.text(2.85,1.6,'N 次模拟 × 每次 rollout L 步',fontsize=11,ha='center',color=C_DARK,fontweight='bold')
    ax.text(2.85,1.25,r'$\mathrm{cost} \propto N \times L$'+'  (L = 剩余步数)',fontsize=12,ha='center',color=C_RED,fontweight='bold')

    # right: AlphaGo Zero
    ax.add_patch(FancyBboxPatch((5.6,1.0),5.1,5.0,boxstyle='round,pad=0.12',fc='#E3F2FD',ec=C_BLUE,lw=1.5))
    ax.text(8.15,5.7,'AlphaGo Zero',fontsize=13,ha='center',color=C_BLUE,fontweight='bold')
    # N simulations, each: descend d + 1 network call
    for i in range(5):
        x0=6.0+i*0.55
        ax.plot([x0,x0],[5.0,3.8],'-',color=C_BLUE,lw=1.5)
        ax.add_patch(Circle((x0,3.8),0.12,fc=C_GOLD,ec=C_GOLD,zorder=3))
        ax.text(x0,3.5,'×1',fontsize=7,ha='center',color=C_GOLD,fontweight='bold')
    ax.text(8.15,5.35,'下行 d 层 (查表)',fontsize=9,ha='center',color=C_BLUE)
    ax.text(8.15,2.9,'N 次模拟 × 每次叶子 1 次网络',fontsize=11,ha='center',color=C_DARK,fontweight='bold')
    ax.text(8.15,2.4,r'$\mathrm{cost} \propto N \times 1$'+'  (网络调用)',fontsize=12,ha='center',color=C_RED,fontweight='bold')
    ax.text(8.15,1.95,'省去了 L 步 rollout',fontsize=9,ha='center',color=C_GRAY,style='italic')

    # bottom comparison table
    ax.add_patch(FancyBboxPatch((0.3,0.1),10.4,0.75,boxstyle='round,pad=0.08',fc='#F5F5F5',ec=C_GRAY,lw=1))
    ax.text(0.6,0.62,'每步总算力',fontsize=10,ha='left',color=C_DARK,fontweight='bold')
    ax.text(2.85,0.62,'N×L 步',fontsize=11,ha='center',color=C_ORANGE,fontweight='bold')
    ax.text(5.5,0.62,'→',fontsize=14,ha='center',color=C_NAVY)
    ax.text(8.15,0.62,'N×1 次网络',fontsize=11,ha='center',color=C_BLUE,fontweight='bold')
    ax.text(0.6,0.28,'教学版 N=25',fontsize=9,ha='left',color=C_GRAY)
    ax.text(2.85,0.28,'~25×60=1500 步',fontsize=9,ha='center',color=C_GRAY)
    ax.text(8.15,0.28,'25 次前向传播',fontsize=9,ha='center',color=C_GRAY)
    plt.tight_layout(); save(fig,'complexity_compare.png')

# ── 3. MCTS as policy improvement operator ──────────────────────────
def policy_operator():
    fig,ax=plt.subplots(figsize=(11,5),facecolor='white')
    ax.set_xlim(0,11);ax.set_ylim(0,5.5);ax.axis('off')
    ax.text(5.5,5.1,'MCTS = 策略改进算子',fontsize=15,ha='center',color=C_NAVY,fontweight='bold')

    # pipeline: network p -> MCTS -> improved pi -> train
    boxes=[
        (1.3,2.5,'网络策略\n$p(a|s)$','(有噪声\n未收敛)',C_GRAY),
        (4.0,2.5,'MCTS 搜索\n(25 次模拟)','+ PUCT\n+ N(s,a) 统计',C_BLUE),
        (6.7,2.5,'改进策略\n$\\pi \\propto N^{1/T}$','(更接近\n最优)',C_GREEN),
        (9.4,2.5,'训练网络\n逼近 $\\pi$','策略提升',C_GOLD),
    ]
    for x,y,t,d,c in boxes:
        ax.add_patch(FancyBboxPatch((x-1.0,y-0.9),2.0,1.8,boxstyle='round,pad=0.1',fc=c,ec=c,alpha=0.92,zorder=2))
        ax.text(x,y+0.3,t,fontsize=11,ha='center',va='center',color='w',fontweight='bold',zorder=3)
        ax.text(x,y-0.45,d,fontsize=8.5,ha='center',va='center',color='w',zorder=3,style='italic')
    for i in range(3):
        ax.add_patch(FancyArrowPatch((boxes[i][0]+1.05,2.5),(boxes[i+1][0]-1.05,2.5),
                     arrowstyle='->,head_width=6,head_length=8',color=C_NAVY,lw=2,zorder=2))
    # loop back
    ax.add_patch(FancyArrowPatch((9.4,1.5),(1.3,1.5),arrowstyle='->,head_width=6,head_length=8',
                 color=C_RED,lw=1.8,connectionstyle='arc3,rad=0.25',linestyle='--',zorder=2))
    ax.text(5.5,0.7,'迭代：π 越来越强 → 网络越来越准 → 搜索越来越好',fontsize=11,ha='center',color=C_RED,fontweight='bold',style='italic')

    # key point
    ax.text(5.5,4.2,'关键：MCTS 用搜索把"粗糙的网络 p"改进成"更强的策略 π"，再让网络学 π',fontsize=11,ha='center',color=C_DARK)
    ax.text(5.5,3.7,'这本质是策略迭代 (Policy Iteration)：π_policy → MCTS → π_improved → 更新 policy',fontsize=10,ha='center',color=C_PURPLE)
    plt.tight_layout(); save(fig,'policy_operator.png')

if __name__=="__main__":
    print("Generating design-tradeoff diagrams...")
    why_leaf();complexity_compare();policy_operator()
    print("Done!")
