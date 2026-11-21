# 声明式歌词样式 v2

本契约用于实现 v2 渲染器的 VerseNotch macOS 0.2.2 起的本地文件导入。插件市场目前沿用 v1。v2 仍使用清单版本 1，`pluginAPIVersion` 填 `2`，`minAppVersion` 至少填 `0.2.2`。既有 v1 包可在新版客户端导入。

包结构、路径、大小、图片格式、色值和原有字段沿用 [v1 契约](lyric-style-v1.md)。必填字段和允许值见 [清单 Schema](manifest-v2.schema.json) 与 [样式 Schema](style-v2.schema.json)。

## 字体

在 `text` 中可增加以下字段。

| 字段 | 取值与效果 |
| --- | --- |
| `design` | `default`、`rounded`、`serif`、`monospaced`，使用 macOS 系统字体及对应的字形回退。 |
| `fontAsset` | `assets/` 中的一份 TTF 或 OTF 字体文件，上限 8 MiB。该文件的字形与字重用于歌词，字号沿用 `fontSize`。请按目标字重挑选字体文件，并检查实际歌词文字的覆盖范围。与 `design` 二选一。 |
| `tracking` | 以点为单位的整数字距，范围 `-2` 至 `8`，默认 `0`。 |

使用系统字体时 `weight` 控制字重。使用随包字体时该必填字段保留语义字重，实际字重由字体文件决定。可变字体使用文件的默认轴值。字体只在此样式内使用。

## 循环背景

```json
{
  "type": "scroll",
  "asset": "assets/train-strip.png",
  "direction": "leftToRight",
  "durationMs": 24000
}
```

`scroll` 按浮窗高度等比缩放图片，再横向平铺。支持 `leftToRight` 和 `rightToLeft`，`durationMs` 表示移动一张图片所需的时间，范围 1000 至 120000 毫秒。图宽至少等于图高。制作素材时检查左右边缘，把需要保留完整边框的人物卡片放在接缝以内。

```json
{
  "type": "frames",
  "asset": "assets/star-sea.png",
  "scaling": "fill",
  "columns": 8,
  "rows": 4,
  "durationMs": 4000
}
```

`frames` 从单张 PNG 或 JPEG 读取等尺寸网格。按从左到右、从上到下的顺序使用所有格子。行列各为 1 至 8，至少两格，图片宽高须分别被列数和行数整除。帧时长相同，平均每帧至少 34 毫秒，每轮至多 120000 毫秒。画格内保留文字安全区，并检查最后一格回到第一格的动作。

背景播放跟随媒体时间，暂停保持当前相位，拖动进度同步切换相位。导入预览采用独立时钟。打开减少动态效果时采用初始画面。插件样式显示在展开的歌词浮窗，刘海单行和全息桌面使用各自的宿主渲染。

## 效果边界

通过素材控制画面和序列帧，通过声明参数控制字体、高亮、转场和循环。可导入包仍是无权限数据包。自定义 Metal 着色器、脚本、新窗口布局和全息舞台属于客户端开发。需要这些能力时，按实际目标评估宿主改造。
