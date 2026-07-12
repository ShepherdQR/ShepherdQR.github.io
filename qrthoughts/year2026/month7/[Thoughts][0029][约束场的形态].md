<!---------------------------------------------------------
 - Author: Qirong ZHANG
 - Date: 2026-07-07 22:39:39
 - Github: https://github.com/ShepherdQR
 - LastEditors: Qirong ZHANG
 - LastEditTime: 2026-07-07 22:43:19
 - Copyright (c) 2026 Qirong ZHANG. All rights reserved.
 - SPDX-License-Identifier: LGPL-3.0-or-later.
 --------------------------------------------------------->
---
type: Thoughts
id: "0029"
title: "约束场的形态"
created: "2026-07-07 22:39:39"
created_date: "2026-07-07"
published: "2026-07-07"
updated: "2026-07-07 22:39:39"
updated_date: "2026-07-07"
slug: "thoughts-0029"
status: "published"
summary: "以海报生产和 s012 Domain Research OS 为实例，刻画约束场由横向任务循环、纵向控制线和事件证据脊柱共同组成的 repo-native 运行形态。"
tags: ["ASI", "agent", "constraint-field", "software-engineering", "evaluation"]
series: "约束场与复杂智能"
source:
  date_source:
    created: "new-note"
    published: "new-note"
    updated: "new-note"
---

# 约束场的形态


## 实例1：我们的海报任务流程

海报任务
-> classify visibility
-> 启用审美叙事线 / visual workflow 【纵向硬的 + 横向软的】
-> 如需要，编制 topic-object aesthetic brief
-> 路由 V4/V5 审美角色：Reference Curator, Aesthetic Director, Visual QA Verifier 等
-> 并行启动 skill-agent operations
-> 记录是否触碰 skill / agent / tool / MCP / eval / audit surface
-> 产出海报源文件、source note、QA JSON、最终图/PDF
-> 若产生可复用经验，再进入 pattern review / skill-agent eval / profile update


## 实例2：我们的s012 Domain Research OS

质量问题是纵向的收缩场。我随便一问，可以看见我们发展的形态。

### 问题

我们的s012 Domain Research OS的实际运作形式是什么？是一系列横向的loop和纵向的一系列控制线吗？
### 回答

是的，你这个理解基本准确；更精确地说：

**s012 Domain Research OS = 横向研究 loops + 纵向控制线 + 一条事件/证据脊柱。**

它不是一个后台 daemon，也不是一个单一脚本，而是 repo-native 的控制面：Markdown / YAML / CSV / JSONL / validators / topic-pack artifact 共同组成的操作系统。

**横向 Loops**
横向 loop 是“一个具体研究任务如何被做完”：

```text
研究请求
-> 选择 program row / topic pack
-> 建立 source register
-> 生成 reviewable artifact
-> gate review
-> failure class
-> repair / accept / pause / promote decision
-> evidence / event / join record
-> validator
-> next action
```

现在已经存在的主要横向 loop 有：

- **Research Request Loop**：从一个话题请求进入 topic pack / domain lab。
- **Field Genesis Loop**：从 sparse pressure 到 candidate field、artifact、review、promotion/block。
- **Evaluation Loop**：三轴评估：surface professionalism / structural field understanding / epistemic reliability。
- **Promotion Blocking Loop**：防止因为“话题很有趣”就升级。
- **Evidence-to-Claim Loop**：把 claim 拆成 source、evidence、supports、does-not-support、uncertainty、update condition。

**纵向控制线**
纵向控制线是“每个研究动作必须被哪些层约束”：

```text
L0 command center：当前目标、边界、停止条件
L1 s008 routing：skill、domain route、quality gate
L2 t006 terrain：C01-C14 / SC01-SC07 / truth operator
L3 execution：topic pack、domain lab、G-level program、artifact
L4 evaluation：rubric、failure taxonomy、repair decision
L5 memory：evidence index、promotion registry、reports archive
L6 validators：结构一致性、路径、事件、join、crosswalk
```

所以一个短提示词能展开，是因为它会被这些纵向线“拉住”，不会只靠语言自由扩写。

**第三个关键：事件/证据脊柱**
只有横纵还不够。真正让 OS 像 OS 的，是中间这条脊柱：

```text
research-topic-register.csv
-> lifecycle schema
-> field-genesis-events.jsonl
-> evaluation-promotion-join.jsonl
-> evidence-index / promotion-registry
-> validators
```

它让每次动作变成可追踪状态，而不是一次性聊天输出。

所以实际运作形式可以画成一句话：

```text
横向 loop 负责推进研究；
纵向控制线负责约束质量；
事件/证据脊柱负责留下可复查状态。
```

当前成熟度：**半自动 control-plane**。  
它已经能实战展开深研，但仍然需要真实 source reading、artifact review 和人类 judgment；validator 只能保证结构不漂，不能保证思想一定深。

