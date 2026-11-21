# 场景歌词 v3

VerseNotch macOS 0.2.3 及更新的兼容构建可从本地导入场景歌词。沿用 [v2 契约](lyric-style-v2.md) 的字段和打包规则，清单使用 `pluginAPIVersion: 3`，最低客户端版本填 `0.2.3`。对应的 [清单 Schema](manifest-v3.schema.json) 和 [样式 Schema](style-v3.schema.json) 列出字段约束。

```json
{
  "background": {
    "type": "scene",
    "asset": "assets/street.png",
    "foreground": "assets/street-foreground.png",
    "direction": "rightToLeft",
    "durationMs": 32000,
    "anchors": [{"x": 180, "y": 320}, {"x": 570, "y": 660}]
  },
  "transition": {"effect": "scene", "durationMs": 360, "exitMs": 320}
}
```

使用[浮窗适配与顶部播放栏](viewport-and-header.md)中的场景尺寸、轮廓和验收清单构图。

- 两张 PNG 尺寸一致，并按浮窗高度等比平铺。背景绘制在歌词后方，带 Alpha 的前景绘制在歌词前方。用前景只遮住局部字边，保留主要文字可见。画带左右边缘的地平线、地面和色调应相接。
- `anchors` 是 2 到 16 个文字锚点，横坐标为 0 到 999，纵坐标为 250 到 750，单位为画带宽高的千分之一。横坐标保持唯一。选择人物身旁的留白，每句在开头选定离浮窗中心最近的画带锚点，并随画面移动，接近边缘时限制位置以保留文字。
- `scene` 背景与 `scene` 转场一起使用。入场和退场各支持 80 到 700 毫秒，短句最多使用各一半的时间。文字沿卷动方向进出，同时渐显或渐隐。
- 逐字高亮、字体和字距沿用 v2。场景和转场以媒体时间推进，暂停及跳转沿用宿主时间轴。减少动态效果时显示首屏场景与静态文字。场景用于展开的歌词浮窗。
