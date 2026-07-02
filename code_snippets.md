# 代码讲解片段速查 (alpha-zero-general)

汇报时按需点开对应文件讲解。以下片段均带行号，对应 `alpha-zero-general/` 仓库。

---

## 1. MCTS 四阶段 + PUCT  — `MCTS.py`

### PUCT 选择 (第 109-119 行) → 对应 PPT "PUCT 搜索"页
```python
109|        for a in range(self.game.getActionSize()):
110|            if valids[a]:
111|                if (s, a) in self.Qsa:
112|                    u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
113|                            1 + self.Nsa[(s, a)])
114|                else:
115|                    u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?
116|                if u > cur_best:
117|                    cur_best = u
118|                    best_act = a
```
**讲解要点**：
- 第 112 行：`Q + cpuct * P * sqrt(Ns) / (1+Nsa)` —— 注意是 `sqrt(Ns)`（父节点访问数），**不是** `sqrt(ln N)`
- `cpuct = 1`（main.py 第 22 行）
- 第 115 行：未访问节点 Q=0，只算探索项

### 叶节点：神经网络评估替代 rollup (第 83-102 行) → 对应"与传统 MCTS 区别"
```python
83|        if s not in self.Ps:
84|            # leaf node
85|            self.Ps[s], v = self.nnet.predict(canonicalBoard)
86|            valids = self.game.getValidMoves(canonicalBoard, 1)
87|            self.Ps[s] = self.Ps[s] * valids  # masking invalid moves
88|            sum_Ps_s = np.sum(self.Ps[s])
89|            if sum_Ps_s > 0:
90|                self.Ps[s] /= sum_Ps_s  # renormalize
...
100|            self.Vs[s] = valids
101|            self.Ns[s] = 0
102|            return -v   # ← 关键：直接返回网络 v，不再随机模拟到终局
```
**讲解要点**：第 85 行一次前向传播得到 (P, v)；第 102 行 `return -v` 直接回传，**这就是 AlphaGo Zero 用神经网络替代 Simulation 的核心**。负号是零和博弈对手视角。

### 回传：增量平均 (第 127-136 行) → 对应"MCTS 四阶段·回传"
```python
127|        if (s, a) in self.Qsa:
128|            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
129|            self.Nsa[(s, a)] += 1
130|        else:
131|            self.Qsa[(s, a)] = v
132|            self.Nsa[(s, a)] = 1
133|
134|        self.Ns[s] += 1
135|        return -v   # ← 对手视角取负
```
**讲解要点**：第 128 行 `Q = (N*Q + v)/(N+1)` 是增量平均；第 135 行 `return -v` 让 minimax 自然成立。

### 动作概率：温度采样 (第 43-53 行) → 对应自我对弈选子
```python
43|        if temp == 0:
44|            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
45|            bestA = np.random.choice(bestAs)
46|            probs = [0] * len(counts)
47|            probs[bestA] = 1
48|            return probs
49|
50|        counts = [x ** (1. / temp) for x in counts]
51|        counts_sum = float(sum(counts))
52|        probs = [x / counts_sum for x in counts]
53|        return probs
```
**讲解要点**：`π ∝ N^(1/temp)`。temp=1 时按访问次数采样（探索），temp=0 时取 argmax（利用）。

---

## 2. 自我对弈生成数据 — `Coach.py`

### executeEpisode (第 32-69 行) → 对应"自我对弈与数据生成"
```python
53|        while True:
54|            episodeStep += 1
55|            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)
56|            temp = int(episodeStep < self.args.tempThreshold)   # 前15步 temp=1
57|
58|            pi = self.mcts.getActionProb(canonicalBoard, temp=temp)
59|            sym = self.game.getSymmetries(canonicalBoard, pi)    # 数据增强：旋转/翻转
60|            for b, p in sym:
61|                trainExamples.append([b, self.curPlayer, p, None])
62|
63|            action = np.random.choice(len(pi), p=pi)             # 按策略采样落子
64|            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action)
65|
66|            r = self.game.getGameEnded(board, self.curPlayer)
67|
68|            if r != 0:
69|                return [(x[0], x[2], r * ((-1) ** (x[1] != self.curPlayer))) for x in trainExamples]
```
**讲解要点**：
- 第 56 行：`tempThreshold=15`，前 15 步探索、之后利用
- 第 59 行：`getSymmetries` 做 8 倍数据增强
- 第 69 行：终局时用 `r * (-1)^(x[1]!=curPlayer)` 给每步打标签 z —— **这就是 MC 方法**（用终局结果回填），z=±1

### learn 主循环 (第 80-128 行) → 对应"训练流程"
```python
80|        for i in range(1, self.args.numIters + 1):              # 1000 轮
...
87|                for _ in tqdm(range(self.args.numEps), desc="Self Play"):   # 每轮 100 局
88|                    self.mcts = MCTS(self.game, self.nnet, self.args)        # 重置搜索树
89|                    iterationTrainExamples += self.executeEpisode()
...
113|            self.nnet.train(trainExamples)                       # 训练
...
117|            arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
118|                          lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
119|            pwins, nwins, draws = arena.playGames(self.args.arenaCompare)   # 40 局评估
...
122|            if pwins + nwins == 0 or float(nwins) / (pwins + nwins) < self.args.updateThreshold:
123|                log.info('REJECTING NEW MODEL')                  # <60% 胜率 → 回退
124|                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
125|            else:
126|                log.info('ACCEPTING NEW MODEL')                  # ≥60% → 保留
```
**讲解要点**：第 88 行每局重置 MCTS；第 122 行 `updateThreshold=0.6` 是策略迭代稳定的关键。

---

## 3. 神经网络与损失 — `othello/pytorch/OthelloNNet.py` + `NNet.py`

### 双头网络前向 (OthelloNNet.py 第 39-54 行) → 对应"双头神经网络"
```python
39|    def forward(self, s):
41|        s = s.view(-1, 1, self.board_x, self.board_y)            # 单通道输入
42|        s = F.relu(self.bn1(self.conv1(s)))                      # Conv1: 1→512, 3×3, pad=1
43|        s = F.relu(self.bn2(self.conv2(s)))                      # Conv2: 512→512
44|        s = F.relu(self.bn3(self.conv3(s)))                      # Conv3: 512→512 (no pad)
45|        s = F.relu(self.bn4(self.conv4(s)))                      # Conv4: 512→512 (no pad)
46|        s = s.view(-1, self.args.num_channels*(self.board_x-4)*(self.board_y-4))
47|
48|        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.args.dropout, training=self.training)
49|        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.args.dropout, training=self.training)
50|
51|        pi = self.fc3(s)                                         # 策略头 → action_size
52|        v = self.fc4(s)                                          # 价值头 → 1
53|
54|        return F.log_softmax(pi, dim=1), torch.tanh(v)
```
**讲解要点**：4 层 CNN（非 ResNet，教学简化）；策略头 `log_softmax`、价值头 `tanh`；Dropout=0.3。

### 损失函数 (NNet.py 第 96-100 行) → 对应"损失函数"
```python
96|    def loss_pi(self, targets, outputs):
97|        return -torch.sum(targets * outputs) / targets.size()[0]    # 交叉熵（outputs已是log_softmax）
98|
99|    def loss_v(self, targets, outputs):
100|        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]   # MSE
```
**讲解要点**：**只有两项，无 L2 正则**（论文有 `c||θ||²`，代码省略）。`loss_pi` 因网络输出 `log_softmax`，所以 `-Σ π·logp` 直接是交叉熵。

### 训练超参 (NNet.py 第 17-24 行)
```python
17|args = dotdict({
18|    'lr': 0.001,          # Adam 学习率
19|    'dropout': 0.3,
20|    'epochs': 10,
21|    'batch_size': 64,
22|    'cuda': torch.cuda.is_available(),
23|    'num_channels': 512,
24|})
```

---

## 4. 全局参数 — `main.py` (第 14-29 行) → 对应"参数对照表"
```python
14|args = dotdict({
15|    'numIters': 1000,              # 外层迭代轮数
16|    'numEps': 100,                 # 每轮自我对弈局数
17|    'tempThreshold': 15,           # 前15步 temp=1
18|    'updateThreshold': 0.6,        # Arena ≥60% 才接受
19|    'maxlenOfQueue': 200000,
20|    'numMCTSSims': 25,             # 每步 MCTS 模拟次数
21|    'arenaCompare': 40,            # Arena 对弈局数
22|    'cpuct': 1,                    # PUCT 探索常数
...
27|    'numItersForTrainExamplesHistory': 20,   # 滑动窗口：保留最近20轮数据
28|})
```
**讲解要点**：这是全篇的参数锚点。`numMCTSSims=25` vs 论文 AGZ 1600 / AZ 800；`numEps=100` vs AGZ 总 490万局（3天版）—— 算力差距的核心来源。

> **论文参数量级参考**（据 Nature 2017 / Science 2018 正文，讲解须量级 aware）：
> - **AlphaGo Lee** (2016)：48 手工特征平面 · 分离策略网+价值网（各13层CNN）· MCTS 随机 rollout · 分布式 48 TPU · 训练数月 · Elo≈3600
> - **AlphaGo Zero** (Nature 2017)：17/19 原始棋盘平面 · 单一双头 ResNet（20块3天/40块40天，256通道）· 无 rollout 用 v(s) · 1600 模拟/步(≈0.4s) · 评估单机 4 TPU · 3天超 Lee、72h≈5185 · 总 490万局/700k batch×2048
> - **AlphaZero** (Science 2018)：规则平面 · 同一 ResNet 架构通吃三棋种 · 无 rollout · 800 模拟/步 · 5000 一代 TPU 自对弈 + 16 二代 TPU 训练 · 9h 象棋 / 12h 将棋 / 13天围棋 · 60k pos/s（Stockfish 60M，1/1000 仍胜）
> - **注意**：AGZ 论文未公开自对弈 worker 数，"64 TPU worker" 是误传，勿讲。
