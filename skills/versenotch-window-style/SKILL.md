---
name: versenotch-window-style
description: 为 VerseNotch 设计浮窗宽度、材质、透明度和音乐共振预设，提供不同显示器与辅助功能状态的预览方案。
---

# 设计浮窗样式

0.3.0 开发宿主可单独导入材质、前奏和共振。每种只激活一个包；换歌词时继续使用原选择。config.json 需要 operation 和六位 RGB 色值 color。对应槽位可使用以下 operation 值。

| 包类型 | 通用绘制 | 原版外观绘制 |
| --- | --- | --- |
| material | solid、frost | graphite、ocean、pine、bronze、paper、transparent、black |
| prelude-style | dots、pulse | seven-dots、lifeline |
| resonance-style | bars、glow | diaphragm、contour、grain、bloom |

关闭前奏或共振由宿主清空槽位。前奏在首句前生效，共振随播放音量变化，开启减少动态效果时停用。0.3.0 的这三类包分别控制一个槽位。用于较早预览客户端的 window-style 组合包保留原契约。

在本技能目录运行以下示例，以 --config 传入自定义 JSON。

```sh
python3 scripts/pack-preview.py material ./graphite.vnplugin --id app.example.graphite --name 石墨 --author Example --license MIT
```


1. 确认使用场景和优先目标，例如桌面工作时持续显示歌词或随节奏轻量共振。分别记录宽度、材质、圆角、样式层透明度和共振的目标值。宿主允许的枚举和范围以目标版本文档为准。浮窗固定展开，高度由宿主管理。宽度注明 pt 或比例。
2. 将浮窗轮廓与歌词绘制分别描述。规划控件避让、长歌词裁切和材质下的可读性。桌面全息舞台与浮窗分别给出表现。
3. 写明暂停、拖动播放、开启系统「减少动态效果」时的表现，以及材质或渲染能力不可用时采用的宿主默认值。

## 交付

提供预设参数表，以及「场景、预期布局、回退结果」验收表。至少覆盖有刘海与无刘海、窄宽、长歌词、切换显示器、减少动态效果和恢复默认样式。若有示意图，用原创示例歌词并标明演示尺寸。
