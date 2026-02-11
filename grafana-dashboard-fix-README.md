# Luckin USA Master Dashboard 修复方案

## 问题诊断

### 仪表板信息
- **名称**: Luckin Coffee USA - Master Operations Dashboard
- **UID**: `luckin-usa-master`
- **URL**: https://iumbgrafana.luckincoffee.us/grafana/d/luckin-usa-master/luckin-coffee-usa-master-operations-dashboard
- **面板总数**: 39个

### 根本原因

仪表板配置了3个MySQL数据源变量，但只有1个变量能找到匹配的数据源：

| 变量名 | 匹配规则 | 状态 | 实际数据源 |
|--------|---------|------|-----------|
| DS_ILUCKYHEALTH | `.*iluckyhealth.*` | ✅ 正常 | MySQL-luckyhealth (UID: 3x14XnENk) |
| DS_SALESORDER | `.*salesorder.*` | ❌ 缺失 | 无匹配数据源 |
| DS_OPSHOP | `.*opshop.*` | ❌ 缺失 | 无匹配数据源 |

### 数据库依赖分析

#### 1. luckyus_iluckyhealth (✅ 可用)
- **表**:
  - t_collect_order_inter (订单汇总数据)
  - t_collect_shop_inter (店铺状态数据)
  - t_collect_payment_inter (支付数据)
  - t_collect_crm_inter (会员数据)
- **连接**: aws-luckyus-iluckyhealth-rw.cxwu08m2qypw.us-east-1.rds.amazonaws.com
- **数据源**: MySQL-luckyhealth

#### 2. luckyus_sales_order (❌ 缺失)
- **表**:
  - t_order (订单详细数据)
- **需要用于**:
  - Revenue Today (今日收入)
  - Avg Order Value (平均订单价值)
  - Top 10 Stores by Orders (按订单量排名前10的店铺)
  - Store Performance Table (店铺绩效表)
  - Store Orders Over Time (店铺订单趋势)
  - 3P Orders by Store (第三方平台订单按店铺)

## 影响的面板

### 🔴 需要 luckyus_sales_order 的面板 (6个)
1. **Revenue Today** (Panel ID: 2) - 今日收入统计
2. **Avg Order Value** (Panel ID: 3) - 平均订单价值
3. **Top 10 Stores by Orders** (Panel ID: 14) - 订单量前10店铺
4. **Store Performance Table** (Panel ID: 15) - 店铺绩效表
5. **Store Orders Over Time** (Panel ID: 16) - 店铺订单趋势
6. **3P Orders by Store** (Panel ID: 19) - 第三方订单按店铺

### ✅ 使用 luckyus_iluckyhealth 的面板 (25个)
所有其他面板都可以正常工作

## 修复方案

### 方案1: 添加缺失的数据源 (推荐)

需要创建一个新的MySQL数据源，名称包含 "salesorder"，例如：
- 名称: `MySQL-salesorder` 或 `MySQL-luckyus-salesorder`
- 数据库: `luckyus_sales_order`
- 连接地址: [需要确认RDS实例]

### 方案2: 临时修复 - 禁用缺失数据的面板

将无法获取数据的面板标记为"数据源缺失"状态，保留其他正常工作的面板。

已创建修复后的配置文件：
- `luckin-usa-master-dashboard-fixed.json` - 部分修复版本（演示）
- 删除了数据源变量
- 直接使用MySQL-luckyhealth的UID (3x14XnENk)
- 标记需要salesorder数据源的面板

### 方案3: 检查MySQL-Ldas数据源

MySQL-Ldas数据源连接到 `luckyus_db_collection` 数据库。需要确认：
1. 该数据库是否包含 `t_order` 表？
2. 如果包含，可以修改变量匹配规则或创建新数据源

## 下一步操作

1. **确认数据库位置**:
   ```bash
   # 检查是否有其他RDS实例包含 luckyus_sales_order 数据库
   ```

2. **创建新数据源** (如果数据库存在):
   - 在Grafana中添加新的MySQL数据源
   - 名称: MySQL-salesorder
   - 数据库: luckyus_sales_order
   - 用户权限: 只读权限即可

3. **或者使用修复后的JSON**:
   - 导入 `luckin-usa-master-dashboard-fixed.json`
   - 新UID为 `luckin-usa-master-fixed`
   - 标记了所有缺失数据源的面板

## 当前可用的MySQL数据源

```
1. MySQL-luckyhealth (UID: 3x14XnENk)
   - Database: luckyus_iluckyhealth
   - Host: aws-luckyus-iluckyhealth-rw.cxwu08m2qypw.us-east-1.rds.amazonaws.com

2. MySQL-Ldas (UID: LJ7ObqYNk)
   - Database: luckyus_db_collection
   - Host: aws-luckyus-ldas01-rw.cxwu08m2qypw.us-east-1.rds.amazonaws.com

3. MySQL-iriskcontrol (UID: BdRo02LNk)

4. Doris-iriskcontrol (UID: T-FUz9aNz)
```

## 检查清单

- [ ] 确认 luckyus_sales_order 数据库的RDS实例地址
- [ ] 验证数据库中是否存在 t_order 表
- [ ] 创建新的MySQL数据源 (名称包含 "salesorder")
- [ ] 测试数据源连接
- [ ] 刷新仪表板确认所有面板正常

---

**日期**: 2026-02-11
**问题分类**: 数据源配置缺失
**严重程度**: 中等 (影响6个关键业务指标面板)
