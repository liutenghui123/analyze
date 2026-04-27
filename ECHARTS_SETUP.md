# ECharts 库设置说明

## 问题

当前项目中缺少 `echarts.min.js` 文件，导致HTML报告无法显示图表。

## 解决方案

### 方法一：下载ECharts（推荐）

1. 访问 ECharts 官方网站：

   ```
   https://echarts.apache.org/zh/download.html
   ```

2. 点击"在线定制"或直接下载完整版：

   ```
   https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js
   ```

3. 将下载的 `echarts.min.js` 文件放置到：
   ```
   Fenxi8/assets/echarts.min.js
   ```

### 方法二：使用CDN（临时方案）

如果暂时无法下载，可以修改 `chart_generator.py` 第115行：

```python
# 原来：
<script src="assets/echarts.min.js"></script>

# 改为：
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
```

**注意**：这需要网络连接才能显示图表。

### 验证安装

安装完成后，目录结构应该是：

```
Fenxi8/
├── assets/
│   └── echarts.min.js    # ~1MB 的JavaScript文件
├── chart_generator.py
├── ui.py
└── ...
```

然后重新运行程序，HTML报告就能正常显示图表了。

## 文件大小

- echarts.min.js: 约 1MB (压缩后)
- 完整版的echarts.js: 约 3MB (未压缩)

建议使用压缩版本（.min.js）以获得更快的加载速度。
