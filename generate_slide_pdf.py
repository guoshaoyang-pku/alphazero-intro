import os

html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>算力估算与 KataGo 优化讲义（演示版）</title>
  <style>
    @page { 
      size: A4 landscape; 
      margin: 0; 
    }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0; 
      padding: 0;
      background-color: #555;
    }
    .slide {
      background: white;
      width: 297mm;
      height: 210mm;
      padding: 20mm;
      box-sizing: border-box;
      page-break-after: always;
      position: relative;
      overflow: hidden;
    }
    h1 { color: #0D1B3E; border-bottom: 4px solid #0D1B3E; padding-bottom: 10px; font-size: 42px; margin-top: 0; }
    h2 { color: #0D1B3E; border-bottom: 2px solid #ccc; padding-bottom: 10px; font-size: 36px; margin-top: 0; }
    h3 { color: #1565C0; font-size: 26px; margin-top: 20px; margin-bottom: 10px; }
    p, li { font-size: 22px; line-height: 1.6; color: #333; }
    li { margin-bottom: 10px; }
    .card {
      background: #FAFAFA;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      margin-bottom: 20px;
      border-left: 8px solid #1565C0;
    }
    .formula {
      font-family: "Courier New", Courier, monospace;
      background: #F3F4F6;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
      font-size: 26px;
      margin: 20px 0;
      font-weight: bold;
    }
    table {
      width: 100%; border-collapse: collapse; margin: 20px 0;
      background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      font-size: 22px;
    }
    th, td { border: 1px solid #E0E0E0; padding: 15px; text-align: left; }
    th { background-color: #0D1B3E; color: white; font-size: 24px; }
    tr:nth-child(even) { background-color: #F8F9FA; }
    .highlight { color: #C62828; font-weight: bold; }
    .note { font-size: 20px; color: #666; margin-top: 10px; }
    .footer { position: absolute; bottom: 15mm; right: 20mm; color: #999; font-size: 16px; }
  </style>
</head>
<body>

  <!-- Slide 1: Title -->
  <div class="slide">
    <div style="margin-top: 30mm;">
      <h1 style="font-size: 56px; border: none;">AlphaGo Zero 算力估算与 KataGo 进化范式</h1>
      <h2 style="border: none; color: #666;">模型参数、推理算力与重要性采样分析</h2>
      <div style="margin-top: 30mm; font-size: 24px; color: #555;">
        <p><strong>重点议题：</strong></p>
        <ul>
          <li>AlphaGo Zero 模型参数量精算</li>
          <li>算力黑洞：天文数字的推理次数估算</li>
          <li>训练样本量与模型参数比例 (Data-to-Parameter Ratio)</li>
          <li>低算力外挂 Heuristic 的数学框架 (重要性采样)</li>
          <li>KataGo 工程降维打击优化</li>
        </ul>
      </div>
    </div>
    <div class="footer">1 / 7</div>
  </div>

  <!-- Slide 2: Parameters -->
  <div class="slide">
    <h2>1. AlphaGo Zero 模型参数量精算</h2>
    <div class="card" style="border-left-color: #7B1FA2;">
      <h3>共享特征提取层：双头残差网络 (ResNet 256通道)</h3>
      <ul>
        <li><strong>输入层：</strong> 19×19×17，初始卷积 (3×3×256) → 约 3.9 万参数</li>
        <li><strong>残差块 (20个)：</strong> 单块约 118 万，20 块共计 → 约 2359 万参数</li>
        <li><strong>策略头 (Policy Head)：</strong> 输出 362 维分布 → 约 26 万参数</li>
        <li><strong>价值头 (Value Head)：</strong> 输出 1 维标量 → 约 9 万参数</li>
      </ul>
      <table>
        <tr>
          <th>模型版本</th>
          <th>总参数量</th>
          <th>训练总局数</th>
        </tr>
        <tr>
          <td><strong>AGZ (3天版)</strong> - 20个残差块</td>
          <td><span class="highlight">~2400 万 (24M)</span></td>
          <td>490 万局</td>
        </tr>
        <tr>
          <td><strong>AGZ (40天版)</strong> - 40个残差块</td>
          <td><span class="highlight">~4750 万 (47.5M)</span></td>
          <td>2900 万局</td>
        </tr>
      </table>
      <p class="note">💡 <strong>对比观察：</strong> 这是典型的“小模型、巨算力”，算力绝大多数被消耗在了搜索（推理）过程，而非单次前向传播计算。</p>
    </div>
    <div class="footer">2 / 7</div>
  </div>

  <!-- Slide 3: Inferences -->
  <div class="slide">
    <h2>2. 算力黑洞：天文数字的推理次数估算</h2>
    <div class="card" style="border-left-color: #E65100;">
      <p>生成一条训练数据需要极其庞大的 MCTS 模拟，每次模拟都需要调用一次神经网络评估叶节点。</p>
      <div class="formula">
        推理总次数 = 训练总局数 × 每局平均步数 × 每步模拟数
      </div>
      <h3>以 AlphaGo Zero (3天 20-block 版) 为例：</h3>
      <ul>
        <li><strong>训练总局数 (Total Games)：</strong> 4,900,000 局</li>
        <li><strong>每局平均步数 (Moves/Game)：</strong> 围棋平均约 200 步</li>
        <li><strong>每步模拟数 (Sims/Move)：</strong> 1,600 次</li>
      </ul>
      <div class="formula" style="background:#FFF3E0; border: 1px solid #FFCC80; color: #E65100; font-size:32px;">
        4.9M × 200 × 1600 ≈ 1.56 万亿次前向推理 (1.56 × 10¹²)
      </div>
      <p>每次推理计算一个 24M 参数的 ResNet (约 10 GFLOPs)。<strong>生成数据总共消耗 10²³ 量级的 FLOPs！</strong></p>
    </div>
    <div class="footer">3 / 7</div>
  </div>

  <!-- Slide 4: Data/Param Ratio -->
  <div class="slide">
    <h2>3. 训练样本量与模型参数比例 (Data-to-Parameter Ratio)</h2>
    <div class="card" style="border-left-color: #2E7D32;">
      <p>基于对局数，可计算出真实的<strong>训练样本规模</strong> (每个样本是一个 <code>(s_t, π_t, z)</code> 元组)：</p>
      <div class="formula" style="background:#E8F5E9; border: 1px solid #81C784; color: #2E7D32;">
        总样本量 = 4,900,000 局 × 200 步/局 ≈ 9.8 亿 (1 Billion)
      </div>
      <ul>
        <li><strong>训练样本量：</strong> ~1 Billion (1B)</li>
        <li><strong>模型参数量：</strong> ~24 Million (24M)</li>
        <li><strong>数据-参数比：</strong> 1,000,000,000 / 24,000,000 ≈ <span class="highlight">40 倍</span></li>
      </ul>
      <h3>学术启示 (与 LLM 对比)：</h3>
      <p>目前千亿参数的大语言模型 (LLM)，受限于真实世界高质量数据枯竭，往往只能勉强满足 Chinchilla Scaling Laws (约 20 倍的 Token/参数比)。</p>
      <p>而 AlphaGo Zero 依靠人工合成的 10 亿无偏高质量对弈样本，达到了奢侈的 <strong>40 倍</strong>数据/参数比。这种极端的数据充沛度把 24M 参数的特征表达能力压榨到了物理极限，完全免疫过拟合。</p>
    </div>
    <div class="footer">4 / 7</div>
  </div>

  <!-- Slide 5: Importance Sampling -->
  <div class="slide">
    <h2>4. 低算力外挂 Heuristic 必须遵循重要性采样</h2>
    <div class="card" style="border-left-color: #00838F;">
      <p>在个人算力受限时，我们需要手动设计 Heuristic（如：子力优势、目数估算）来引导树的搜索。但粗暴相加会<strong>破坏 MCTS 的无偏性 (Unbiasedness)</strong>。</p>
      <h3>重要性采样 (Importance Sampling) 框架</h3>
      <ul>
        <li><strong>目标分布 p(x)：</strong> 原版纯粹无偏的 MCTS 搜索分布。</li>
        <li><strong>提议分布 q(x)：</strong> 叠加人类 Heuristic 后的有偏分布 (收敛快)。</li>
      </ul>
      <p>在 MCTS 回传和提取策略时，必须引入<strong>重要性权重</strong>：</p>
      <div class="formula">
        w_i = p(x_i) / q(x_i) &nbsp;&nbsp; ⇒ &nbsp;&nbsp; Q = Σ (w_i · v_i) / Σ w_i
      </div>
      <p><strong>💡 物理共鸣 (Lattice QCD / VMC)：</strong> 这完全等价于在计算路径积分时，构造包含物理直觉的 Trial Action 进行 Metropolis-Hastings 采样 (提议分布 q)，再通过 <strong>Reweighting (重新加权)</strong> 恢复真实的物理观测量，维持数学纯洁性。</p>
    </div>
    <div class="footer">5 / 7</div>
  </div>

  <!-- Slide 6: KataGo Optimizations -->
  <div class="slide">
    <h2>5. 凡人算力的救星：KataGo 范式改良</h2>
    <div class="card" style="border-left-color: #1565C0;">
      <p>开源社区 (KataGo) 对 AGZ 进行降维打击优化，用极少算力达到同等水平：</p>
      <ul>
        <li><strong>访问量上限随机化 (Playout Cap Randomization)：</strong><br>
        训练时 90% 的回合仅给 50~100 次模拟，仅 10% 满负荷搜 800 次。单局推理从 32万次 锐减到 4万次，提速近 10 倍。</li>
        <br>
        <li><strong>TD-Bootstrap 辅助价值目标：</strong><br>
        AGZ 的纯 MC 信号极度稀疏 (1 bit 终局胜负) 且方差大。KataGo 用未来 MCTS 的 Q 值做 TD Bootstrap 目标，将低方差信号借给价值网络，早期收敛极快。</li>
        <br>
        <li><strong>多任务学习 (Multi-Task Learning)：</strong><br>
        预测领地所有权 (361维密集标签) 和具体比分差。不仅测总截面，还要测多粒子末态分布，快速反演内部结构。</li>
      </ul>
    </div>
    <div class="footer">6 / 7</div>
  </div>

  <!-- Slide 7: Summary -->
  <div class="slide">
    <h2>6. 总结对比</h2>
    <table>
      <tr>
        <th>维度</th>
        <th>AlphaGo Zero</th>
        <th>KataGo (优化后)</th>
      </tr>
      <tr>
        <td><strong>数据生成效率</strong></td>
        <td>极低（固定 1600次/步）</td>
        <td>极高（动态 50~800次/步，省近10倍）</td>
      </tr>
      <tr>
        <td><strong>价值(v)信号源</strong></td>
        <td>纯终局 MC (1 bit，极稀疏，方差大)</td>
        <td>终局 MC + 局部 TD Bootstrap</td>
      </tr>
      <tr>
        <td><strong>辅助任务</strong></td>
        <td>无，网络自己悟</td>
        <td>预测所有权、具体比分 (密集监督)</td>
      </tr>
      <tr>
        <td><strong>数学纯洁性 vs 效率</strong></td>
        <td>原教旨主义的无偏闭环</td>
        <td>重要性采样 + 算力动态分配</td>
      </tr>
      <tr>
        <td><strong>收敛到高水平速度</strong></td>
        <td>Google 级别 TPU 集群跑数天</td>
        <td>高端民用显卡数周即可追平早期AGZ</td>
      </tr>
    </table>
  </div>

</body>
</html>
"""

with open('handout_slides.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("Slide HTML generated.")
