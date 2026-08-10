# 部署步骤

## 1. 建仓库
在 GitHub 上新建一个仓库（Public 或 Private 都行，Private 也能用免费的 GitHub Pages + Actions 额度）。
把这四个文件按原样放进去：

```
.github/workflows/update-data.yml
fetch_data.py
index.html
data.json
```

目录结构必须保持一致，尤其 `.github/workflows/update-data.yml` 这个路径不能变，GitHub 靠这个路径识别工作流。

## 2. 开两个开关

**开关A - 让 Actions 有权限往仓库里提交更新：**
仓库页面 → Settings → Actions → General → 往下翻到 "Workflow permissions"，
选择 "Read and write permissions"，保存。
（不开这个，Actions 抓完数据没法把 data.json 提交回仓库）

**开关B - 打开 GitHub Pages：**
仓库页面 → Settings → Pages → Source 选择 "Deploy from a branch"，
Branch 选 `main`，目录选 `/ (root)`，保存。
过一两分钟页面会给你一个 `https://你的用户名.github.io/仓库名/` 的链接，这就是能直接打开看日历的网址。

## 3. 手动跑一次，别等定时任务

仓库页面 → Actions 标签 → 左侧选 "Update show data" → 右边有个 "Run workflow" 按钮，点一下，
手动触发一次抓取，几十秒后 `data.json` 会被自动更新并提交。这样你不用等到下周一才有数据。

之后它会按 `update-data.yml` 里设的时间（默认每周一凌晨2点，北京时间）自动跑，
每次都会去查最新数据，如果和仓库里现在的不一样就自动提交更新，网页会自动跟着变，
你完全不用管，也不需要点"同步"按钮 —— 打开网址看到的就是最近一次自动抓取的结果。

## 4. 想改成别的人 / 别的抓取频率

- 改查询对象：编辑 `fetch_data.py` 最上面的 `NAME_A` / `NAME_B`
- 改抓取频率：编辑 `.github/workflows/update-data.yml` 里的 `cron` 表达式
  （cron 用的是 UTC 时间，北京时间要减8小时换算，比如想要"每天早上8点北京时间"跑，
  写 `0 0 * * *`）

## 关于"已看"打勾记录

已看的打勾状态存在**你自己浏览器的本地存储**里，跟 GitHub 上的数据完全独立 ——
别人打开同一个网址看到的日历是一样的，但看到的"已看"勾选状态只跟他们自己的浏览器有关，
不会互相干扰，也不会因为数据每周刷新而被清空。
