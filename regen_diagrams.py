#!/usr/bin/env python3
"""Regenerate diagrams that must align with alpha-zero-general codebase."""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CN_FONT = "Noto Sans CJK SC"
matplotlib.rcParams['font.sans-serif'] = [CN_FONT, 'STHeiti', 'Heiti TC', 'PingFang HK']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

C_NAVY="#0D1B3E"; C_BLUE="#1565C0"; C_LIGHT_BLUE="#E3F2FD"
C_TEAL="#00897B"; C_GREEN="#2E7D32"; C_GOLD="#E8A838"
C_RED="#E53935"; C_ORANGE="#FB8C00"; C_GRAY="#9E9E9E"
C_LIGHT_GRAY="#E0E0E0"; C_WHITE="#FFFFFF"; C_DARK="#1A1A2E"
C_PURPLE="#7B1FA2"
DPI=200

def save(fig,name):
    path=os.path.join(ASSET_DIR,name)
    fig.savefig(path,dpi=DPI,bbox_inches='tight',facecolor=fig.get_facecolor(),edgecolor='none',pad_inches=0.15)
    plt.close(fig); print(f"  [+] {name}"); return path

# ── PUCT formula (aligned with MCTS.py:112-115) ───────────────────────
def create_puct():
    fig, ax = plt.subplots(figsize=(11,5.2), facecolor=C_WHITE)
    ax.set_xlim(0,11); ax.set_ylim(0,6); ax.axis('off')
    ax.text(5.5,5.6,"MCTS + 神经网络: PUCT 选择公式",fontsize=16,ha='center',fontweight='bold',color=C_NAVY)
    # formula from MCTS.py line 112: Q + cpuct * P * sqrt(Ns) / (1 + Nsa)
    ax.text(5.5,4.3,
        r'$a^* = \arg\max_a \left[ Q(s,a) + c_{\mathrm{puct}} \cdot P(s,a) \cdot \frac{\sqrt{N(s)}}{1 + N(s,a)} \right]$',
        fontsize=19,ha='center',va='center',color=C_NAVY)
    items=[
        (1.7,2.8,"$Q(s,a)$","动作价值\n增量平均回传\n$\\frac{NQ+v}{N+1}$",C_BLUE),
        (5.5,2.8,"$P(s,a)$","神经网络先验\n策略头输出\n(经合法动作掩码)",C_GOLD),
        (9.3,2.8,"$N(s,a)$","访问次数\n$c_{puct}=1$\n(MCTS.py)",C_RED),
    ]
    for x,y,f,d,c in items:
        rect=FancyBboxPatch((x-1.3,y-0.85),2.6,1.7,boxstyle="round,pad=0.1",fc=c,ec=c,alpha=0.12,zorder=1)
        ax.add_patch(rect)
        ax.text(x,y+0.25,f,fontsize=16,ha='center',va='center',color=c,fontweight='bold')
        ax.text(x,y-0.4,d,fontsize=10,ha='center',va='center',color=C_DARK)
    ax.plot([1,10],[1.3,1.3],'-',color=C_LIGHT_GRAY,lw=1)
    ax.text(3,0.8,"利用 (Exploitation)",fontsize=12,ha='center',color=C_BLUE,fontweight='bold')
    ax.text(8,0.8,"探索 (Exploration)",fontsize=12,ha='center',color=C_GOLD,fontweight='bold')
    ax.annotate('',xy=(1.7,1.1),xytext=(4.3,1.1),arrowprops=dict(arrowstyle='<->',color=C_BLUE,lw=1.5))
    ax.annotate('',xy=(6.7,1.1),xytext=(9.3,1.1),arrowprops=dict(arrowstyle='<->',color=C_GOLD,lw=1.5))
    # note: sqrt(N) not sqrt(ln N)
    ax.text(5.5,0.2,"注: 论文版用 $\\sqrt{N(s)}$（非传统 UCT 的 $\\sqrt{\\ln N}$），$c_{puct}$ 不在根号内",
            fontsize=10,ha='center',color=C_GRAY,style='italic')
    plt.tight_layout(); save(fig,"puct.png")

# ── NN architecture aligned with OthelloNNet.py (4-layer CNN, not ResNet) ─
def create_nn_arch():
    fig, ax = plt.subplots(figsize=(11,6.8), facecolor=C_WHITE)
    ax.set_xlim(0,11); ax.set_ylim(0,11); ax.axis('off')
    def block(x,y,w,h,t,c,tc=C_WHITE,fs=12):
        r=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.1",fc=c,ec=c,alpha=0.92,zorder=2)
        ax.add_patch(r)
        ax.text(x+w/2,y+h/2,t,fontsize=fs,ha='center',va='center',color=tc,fontweight='bold',zorder=3)
    def arrow(x,y1,y2,c=C_GRAY):
        ax.annotate('',xy=(x,y2),xytext=(x,y1),arrowprops=dict(arrowstyle='->',color=c,lw=2))
    ax.text(5.5,10.6,r"双头神经网络  $f_\theta(s)=(\mathbf{p},v)$   —  alpha-zero-general 实现",
            fontsize=14,ha='center',va='center',color=C_NAVY,fontweight='bold')
    # input (single channel, OthelloNNet.py:41)
    block(3,9.3,5,0.65,"输入: s  (单通道棋盘  board_x × board_y)",C_NAVY,fs=11)
    arrow(5.5,9.25,8.75,C_NAVY)
    # 4 conv layers (OthelloNNet.py:19-22)
    block(2.5,8.0,6,0.7,"Conv1: 1→512, 3×3, pad=1  +  BN + ReLU",C_BLUE,fs=11)
    arrow(5.5,7.95,7.5,C_BLUE)
    block(2.5,6.8,6,0.7,"Conv2: 512→512, 3×3, pad=1  +  BN + ReLU",C_BLUE,fs=11)
    arrow(5.5,6.75,6.3,C_BLUE)
    block(2.5,5.6,6,0.7,"Conv3: 512→512, 3×3 (no pad)  +  BN + ReLU",C_BLUE,fs=11)
    arrow(5.5,5.55,5.1,C_BLUE)
    block(2.5,4.4,6,0.7,"Conv4: 512→512, 3×3 (no pad)  +  BN + ReLU",C_BLUE,fs=11)
    arrow(5.5,4.35,3.85,C_BLUE)
    # split
    ax.plot([5.5,5.5],[3.8,3.4],'-',color=C_GRAY,lw=2)
    ax.plot([3,8],[3.4,3.4],'-',color=C_GRAY,lw=2)
    ax.plot([3,3],[3.4,3.0],'-',color=C_GRAY,lw=2)
    ax.plot([8,8],[3.4,3.0],'-',color=C_GRAY,lw=2)
    # policy head (OthelloNNet.py:29-35)
    block(0.8,2.0,4.4,0.95,"策略头 Policy Head\nFC: →1024→512 → action_size\nDropout 0.3",C_GOLD,C_DARK,fs=10)
    arrow(3,1.95,1.55,C_GOLD)
    block(1.3,0.6,3.4,0.9,r"$\mathbf{p}=\log\mathrm{softmax}$"+" (362维)\n预测时 $\\exp$ 还原",C_GOLD,C_DARK,fs=10)
    # value head (OthelloNNet.py:32-37)
    block(5.8,2.0,4.4,0.95,"价值头 Value Head\nFC: →1024→512 → 1\nDropout 0.3",C_RED,C_WHITE,fs=10)
    arrow(8,1.95,1.55,C_RED)
    block(6.3,0.6,3.4,0.9,r"$v=\tanh \in [-1,1]$"+"",C_RED,C_WHITE,fs=10)
    ax.text(3,0.15,"下一步走哪？",fontsize=10,ha='center',color=C_GOLD,style='italic',fontweight='bold')
    ax.text(8,0.15,"当前局面谁赢？",fontsize=10,ha='center',color=C_RED,style='italic',fontweight='bold')
    # annotation: simplification vs paper
    ax.text(10.7,7.4,"简化\nvs 论文\n(20/40 残差块)",fontsize=9,ha='center',va='center',color=C_GRAY,style='italic')
    ax.annotate('',xy=(8.6,7.4),xytext=(10.2,7.4),arrowprops=dict(arrowstyle='->',color=C_GRAY,lw=1,connectionstyle='arc3,rad=0'))
    plt.tight_layout(); save(fig,"nn_arch.png")

# ── Code-parameter alignment table ─────────────────────────────────────
def create_param_table():
    fig, ax = plt.subplots(figsize=(12,6.5), facecolor=C_WHITE)
    ax.set_xlim(0,12); ax.set_ylim(0,10); ax.axis('off')
    ax.text(6,9.5,"alpha-zero-general 关键参数对照",fontsize=16,ha='center',fontweight='bold',color=C_NAVY)
    # three columns
    cols=[("MCTS  (MCTS.py / main.py)",C_BLUE,1.0,[
        ("numMCTSSims","25","每步 MCTS 模拟次数"),
        ("cpuct","1","PUCT 探索常数 $c_{puct}$"),
        ("tempThreshold","15","前15步 temp=1，之后 0"),
        ("PUCT","$Q + c\\cdot P\\frac{\\sqrt{N}}{1+N_{sa}}$","$\\sqrt{N}$ 非 $\\sqrt{\\ln N}$"),
        ("Q 更新","$\\frac{NQ+v}{N+1}$","增量平均"),
        ("动作概率","$\\pi \\propto N^{1/temp}$","访问次数温度采样"),
    ]),
    ("神经网络  (OthelloNNet.py)",C_TEAL,4.7,[
        ("架构","4 层 CNN","非 ResNet（教学简化）"),
        ("通道数","512","num_channels"),
        ("卷积核","3×3","前2层pad=1，后2层无"),
        ("策略头","→1024→512→A","log_softmax 输出"),
        ("价值头","→1024→512→1","tanh，标量 [-1,1]"),
        ("正则化","BN + Dropout 0.3","无 L2 权重衰减"),
    ]),
    ("训练 / 自我对弈  (NNet.py / Coach.py)",C_RED,8.4,[
        ("numIters","1000","外层迭代轮数"),
        ("numEps","100","每轮自我对弈局数"),
        ("lr","0.001","Adam 优化器"),
        ("epochs / batch","10 / 64","每轮训练"),
        ("损失","$-\\pi\\log p + (z{-}v)^2$","无 $c\\|\\theta\\|^2$"),
        ("arenaCompare","40","新vs旧对弈，≥60%接受"),
    ])]
    for title,c,x,rows in cols:
        rect=FancyBboxPatch((x-0.1,6.4),3.4,0.8,boxstyle="round,pad=0.08",fc=c,ec=c,alpha=0.95)
        ax.add_patch(rect)
        ax.text(x+1.6,6.8,title,fontsize=11.5,ha='center',va='center',color=C_WHITE,fontweight='bold')
        for i,(k,v,d) in enumerate(rows):
            y=5.8-i*0.92
            bg = C_LIGHT_BLUE if c==C_BLUE else ("#E0F2F1" if c==C_TEAL else "#FFEBEE")
            rect=FancyBboxPatch((x-0.1,y-0.05),3.4,0.82,boxstyle="round,pad=0.05",fc=bg,ec='none',alpha=0.6)
            ax.add_patch(rect)
            ax.text(x+0.05,y+0.5,k,fontsize=10,ha='left',va='center',color=C_DARK,fontweight='bold')
            ax.text(x+0.05,y+0.2,v,fontsize=11,ha='left',va='center',color=c,fontweight='bold')
            ax.text(x+0.05,y-0.12,d,fontsize=8,ha='left',va='center',color=C_GRAY)
        # vertical divider
        if x<5:
            ax.plot([x+3.4,x+3.4],[0.5,6.4],'-',color=C_LIGHT_GRAY,lw=0.8)
    # footer
    ax.text(6,0.15,"所有数值均为 suragnair/alpha-zero-general 默认配置 (Othello 6×6)，对应代码文件已在标题标出",
            fontsize=9,ha='center',color=C_GRAY,style='italic')
    plt.tight_layout(); save(fig,"param_table.png")

# ── Compute comparison: paper vs teaching reproduction ─────────────────
def create_compute_compare():
    fig, ax = plt.subplots(figsize=(12,5.8), facecolor=C_WHITE)
    ax.set_xlim(0,12); ax.set_ylim(0,9); ax.axis('off')
    ax.text(6,8.5,"复现算力对比：论文 vs 教学版",fontsize=16,ha='center',fontweight='bold',color=C_NAVY)
    # left: paper
    rect=FancyBboxPatch((0.3,0.8),5.4,7.0,boxstyle="round,pad=0.15",fc="#0D1B3E",ec="#0D1B3E",alpha=0.95)
    ax.add_patch(rect)
    ax.text(3,7.3,"AlphaGo Zero 论文",fontsize=15,ha='center',color=C_GOLD,fontweight='bold')
    ax.text(3,6.85,"(Silver et al., Nature 2017)",fontsize=9,ha='center',color="#90A4AE")
    paper=[
        ("游戏","围棋 19×19"),
        ("训练时长","3 天 (超 Lee) → 40 天 (最终)"),
        ("硬件","评估: 单机 4 TPU (Lee 用 48 TPU)"),
        ("每步 MCTS","1,600 次模拟 (≈0.4s/步)"),
        ("网络","20 / 40 残差块, 256 通道"),
        ("训练数据","700k batch × 2048 (3天版)"),
        ("总自我对弈","3天版 490 万局; 40天版 2900 万局"),
        ("Elo","72h ≈ 5185 (超 Master)"),
    ]
    for i,(k,v) in enumerate(paper):
        y=6.2-i*0.72
        ax.text(0.6,y,k,fontsize=11,ha='left',color=C_LIGHT_GRAY,fontweight='bold')
        ax.text(2.6,y,v,fontsize=11,ha='left',color=C_WHITE)
    # right: teaching
    rect=FancyBboxPatch((6.3,0.8),5.4,7.0,boxstyle="round,pad=0.15",fc="#E3F2FD",ec="#1565C0",alpha=0.95)
    ax.add_patch(rect)
    ax.text(9,7.3,"alpha-zero-general (教学)",fontsize=15,ha='center',color=C_BLUE,fontweight='bold')
    ax.text(9,6.85,"(suragnair, Stanford CS238)",fontsize=9,ha='center',color=C_GRAY)
    teach=[
        ("游戏","Othello 6×6"),
        ("训练时长","~3 天 (80 迭代收敛)"),
        ("硬件","1 块 NVIDIA Tesla K80"),
        ("每轮自我对弈","100 局"),
        ("每步 MCTS","25 次模拟"),
        ("网络","4 层 CNN, 512 通道"),
        ("总自我对弈","~8,000 局"),
        ("计算量","比论文小 ~6 个数量级"),
    ]
    for i,(k,v) in enumerate(teach):
        y=6.2-i*0.72
        ax.text(6.6,y,k,fontsize=11,ha='left',color=C_DARK,fontweight='bold')
        ax.text(8.6,y,v,fontsize=11,ha='left',color=C_BLUE)
    # arrow
    ax.annotate('',xy=(6.2,4),xytext=(5.8,4),arrowprops=dict(arrowstyle='->',color=C_RED,lw=2.5))
    ax.text(6,3.4,"复现",fontsize=10,ha='center',color=C_RED,fontweight='bold')
    # bottom note
    ax.text(6,0.3,"作者原话: \"orders of magnitude smaller than the computation used in the AlphaGo paper\"",
            fontsize=10,ha='center',color=C_GRAY,style='italic')
    plt.tight_layout(); save(fig,"compute_compare.png")

# ── Paper parameters: AlphaGo Lee / AlphaGo Zero / AlphaZero ───────────
def create_paper_params():
    """三版论文参数量级对照表 (参数量级 aware)。数据据 Nature 2017 & Science 2018 正文。"""
    fig, ax = plt.subplots(figsize=(12.5,6.8), facecolor=C_WHITE)
    ax.set_xlim(0,12.5); ax.set_ylim(0,9); ax.axis('off')
    ax.text(6.25,8.6,"论文参数量级对照 (参数量级 aware)",fontsize=16,ha='center',fontweight='bold',color=C_NAVY)
    ax.text(6.25,8.15,"据 Silver et al. Nature 2017 (AGZ) & Science 2018 (AZ) 正文",fontsize=9.5,ha='center',color=C_GRAY,style='italic')

    # 列定义: (标题, 副标题, 颜色, x, [(参数, 值), ...])
    cols=[
        ("AlphaGo Lee","2016 · 战李世石",C_GRAY,0.4,[
            ("输入特征","手工特征 (48 平面)"),
            ("网络","分离: 策略网 + 价值网\n(13 层 CNN 各一)"),
            ("MCTS 模拟","随机 rollout 到终局"),
            ("训练数据","人类棋谱 (SL) + 自对弈 (RL)"),
            ("MCTS 模拟数","~数千/步"),
            ("硬件","分布式, 48 TPU (评估)"),
            ("训练时长","数月"),
            ("Elo (vs 人类)","≈ 3600 (胜李世石)"),
        ]),
        ("AlphaGo Zero","Nature 2017 · 无人类知识",C_GOLD,4.35,[
            ("输入特征","原始棋盘 (17/19 平面)"),
            ("网络","单一双头 ResNet\n20 块(3天) / 40 块(40天)"),
            ("MCTS 模拟","无 rollout, 用 v(s)"),
            ("训练数据","纯自我对弈 (零人类)"),
            ("MCTS 模拟数","1,600 / 步 (≈0.4s)"),
            ("硬件","评估: 单机 4 TPU"),
            ("训练时长","3 天 (超 Lee) / 40 天 (超 Master)"),
            ("Elo","72h ≈ 5185; 40 天 ≈ 超人"),
        ]),
        ("AlphaZero","Science 2018 · 通用算法",C_RED,8.3,[
            ("输入特征","原始棋盘 (规则平面)"),
            ("网络","同一 ResNet 架构, 三棋种通用"),
            ("MCTS 模拟","无 rollout, 用 v(s)"),
            ("训练数据","纯自我对弈, 无对称性增强"),
            ("MCTS 模拟数","800 / 步 (评估)"),
            ("硬件","5000 一代 TPU 自对弈\n+ 16 二代 TPU 训练"),
            ("训练时长","9h 象棋 / 12h 将棋 / 13天围棋"),
            ("搜索吞吐","60k pos/s (Stockfish 60M)"),
        ]),
    ]
    for title,sub,c,x,rows in cols:
        # header
        rect=FancyBboxPatch((x-0.1,6.7),3.6,0.95,boxstyle="round,pad=0.08",fc=c,ec=c,alpha=0.95)
        ax.add_patch(rect)
        ax.text(x+1.7,7.35,title,fontsize=12.5,ha='center',va='center',color=C_WHITE,fontweight='bold')
        ax.text(x+1.7,6.92,sub,fontsize=8.5,ha='center',va='center',color=C_WHITE,alpha=0.9)
        # rows
        for i,(k,v) in enumerate(rows):
            y=6.25-i*0.74
            bg = "#F5F5F5" if c==C_GRAY else ("#FFF8E1" if c==C_GOLD else "#FFEBEE")
            rect=FancyBboxPatch((x-0.1,y-0.05),3.6,0.68,boxstyle="round,pad=0.04",fc=bg,ec='none',alpha=0.7)
            ax.add_patch(rect)
            ax.text(x,y+0.42,k,fontsize=9,ha='left',va='center',color=C_DARK,fontweight='bold')
            ax.text(x,y+0.13,v,fontsize=8.5,ha='left',va='center',color=C_DARK)
    # footer
    ax.text(6.25,0.2,"关键量级直觉: AGZ 1600 模拟/步 · AZ 800 模拟/步 · 教学版 25 模拟/步  |  搜索量 AZ 仅为 Stockfish 的 1/1000 仍胜",
            fontsize=9.5,ha='center',color=C_RED,fontweight='bold')
    plt.tight_layout(); save(fig,"paper_params.png")

# ── Self-play training pipeline (aligned with Coach.py) ────────────────
def create_training_pipeline():
    fig, ax = plt.subplots(figsize=(12,4.8), facecolor=C_WHITE)
    ax.set_xlim(0,12); ax.set_ylim(0,5); ax.axis('off')
    ax.text(6,4.6,"AlphaGo Zero 训练流程  (Coach.py)",fontsize=16,ha='center',fontweight='bold',color=C_NAVY)
    steps=[
        (1.5,2.5,"初始化\n随机权重 $\\theta$\n(Coach.py)",C_GRAY),
        (4,2.5,"自我对弈\nMCTS + $f_\\theta$\n生成 $(s, \\pi, z)$\nnumEps=100",C_TEAL),
        (7,2.5,"采样训练\n最小化 $\\ell$\nepochs=10\nbatch=64",C_BLUE),
        (10,2.5,"Arena 评估\n新 vs 旧对弈\n40局, ≥60%接受\n否则回退",C_GOLD),
    ]
    for x,y,t,c in steps:
        rect=FancyBboxPatch((x-1.3,y-0.95),2.6,1.9,boxstyle="round,pad=0.12",fc=c,ec=c,alpha=0.92,zorder=2)
        ax.add_patch(rect)
        ax.text(x,y,t,fontsize=10.5,ha='center',va='center',color=C_WHITE,fontweight='bold',zorder=3)
    for i in range(3):
        ax.annotate('',xy=(steps[i+1][0]-1.4,2.5),xytext=(steps[i][0]+1.4,2.5),
                    arrowprops=dict(arrowstyle='->',color=C_NAVY,lw=2.5))
    ax.annotate('',xy=(4,1.3),xytext=(10,1.3),
                arrowprops=dict(arrowstyle='->',color=C_RED,lw=2,connectionstyle='arc3,rad=0.35',linestyle='--'))
    ax.text(7,0.5,"numIters=1000 次迭代循环，越来越强",fontsize=12,ha='center',color=C_RED,fontweight='bold',style='italic')
    plt.tight_layout(); save(fig,"training_pipeline.png")

if __name__=="__main__":
    print("Regenerating code-aligned diagrams...")
    create_puct()
    create_nn_arch()
    create_param_table()
    create_compute_compare()
    create_paper_params()
    create_training_pipeline()
    print("Done!")
