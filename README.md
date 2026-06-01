# G-Scout

海外户外网站装备**价格 / 折扣监测**原型。当前关注品类：**服装**（冲锋衣 / 羽绒服 / 保暖层）和**鞋类**（徒步鞋 / 登山靴 / 越野跑鞋）。

## 监测网站

| 网站 | 类型 | 说明 |
|------|------|------|
| REI | 价格源 | 电商，有自有价格与折扣 |
| Backcountry | 价格源 | 电商 |
| Steep & Cheap | 价格源 | 电商（特卖） |
| Public Lands | 价格源 | 电商 |
| Switchback Travel | 导购源 | 测评 / 榜单站，价格跳转至上述零售商 |

> Switchback Travel 不卖货，定位为「选品来源」而非「价格来源」，所以抓取时按 `review` 类处理、不作为价格源。

## 架构

```
config.py            站点 + 品类注册表
models.py            Product 数据模型（含折扣百分比计算）
scrapers/
  fetch.py           HTTP 抓取 + Playwright 渲染回退
  adapters.py        各站适配器 + 抓取编排（解析 schema.org JSON-LD）
  sample_data.py     抓取被反爬拦截时的示例回退数据
storage.py           SQLite（products + price_snapshots 价格历史）
app.py               FastAPI：触发抓取 / 查询 / 页面
static/              极简前端页面（index.html + app.js）
```

抓取策略（**真实抓取 + 容错降级**）：静态请求 → Playwright 渲染 → 解析页面内嵌的 schema.org `Product` 数据；任一环节失败或被反爬拦截时，回退到该站示例数据，保证整条链路端到端可演示。

## 运行

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# 可选：启用真实渲染抓取（否则仅静态请求 + 示例回退）
.venv/bin/playwright install chromium

.venv/bin/python -m uvicorn app:app --reload --port 8137
```

打开 http://localhost:8137 ，点「抓取最新」拉数据，按网站 / 品类 / 最低折扣筛选。

## API

- `GET  /api/meta` — 站点与品类列表
- `POST /api/scrape?category=<可选>` — 触发一次抓取并入库
- `GET  /api/products?site=&category=&min_discount=` — 各商品最新价格快照

## 现状与后续

- 4 个价格源目前多会被反爬拦截而走示例回退，这是预期内的（回退机制正常工作）。后续按站逐个调真实抓取：补对 `CATEGORY_PATHS` 的真实列表页 URL，并针对各站反爬（Akamai/Cloudflare）完善 Playwright 抓取。
- `price_snapshots` 已按时间存历史，后续可做降价提醒 / 价格走势图。
