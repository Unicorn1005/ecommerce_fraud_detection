# 电商交易反欺诈：从 SQL 到 LightGBM 的完整分析流程

基于 Kaggle 的 [IEEE-CIS Fraud Detection](https://www.kaggle.com/competitions/ieee-fraud-detection) 数据集（Vesta 电商交易数据），完成从数据提取、特征工程、建模评估、模型解释到业务建议和可视化看板的端到端项目。

> 项目进行中，下面标注"待补充"的部分会随进度更新。

## 项目目标

1. 用 SQL 完成数据提取与分群统计，计算电商风控核心指标（分产品、邮箱域名、设备、时段的欺诈率等）。
2. 用 Python 完成数据清洗与特征工程。
3. 训练逻辑回归（基线）、LightGBM、XGBoost，并用 ROC-AUC、PR-AUC、召回率评估。
4. 用 SHAP 解释模型，找出主要风险驱动因素。
5. 输出可落地的业务风控建议。
6. 用 Tableau 制作看板，展示欺诈交易的特征画像。

## 数据说明

- 来源：Kaggle IEEE-CIS Fraud Detection（`train_transaction.csv` + `train_identity.csv`）。
- 规模：约 59 万笔交易，欺诈占比约 3.5%（样本不平衡）。
- 说明：数据集中部分字段（如 V、C、D、M 系列）已脱敏，分析主要围绕可解释字段展开（产品类型、卡信息、邮箱域名、设备、地址、金额、时间）。
- 数据不包含在本仓库中，请按下方步骤自行下载。

## 项目结构

```
ecommerce-fraud-detection/
├── data/
│   └── raw/            # 放原始 CSV（不上传）
├── sql/                # SQL 查询脚本
├── src/                # Python 脚本（建库、特征工程、训练等）
├── notebooks/          # 探索性分析与建模 Notebook
├── reports/            # 结果图表与业务建议文档
├── requirements.txt
└── README.md
```

## 复现步骤

1. 安装依赖：`pip install -r requirements.txt`
2. 在 Kaggle 接受比赛规则后，下载 `train_transaction.csv` 和 `train_identity.csv`，放入 `data/raw/`。
3. 构建 SQLite 数据库：`python src/build_db.py`
4. （可选）在 SQLite 中运行 `sql/02_sanity_checks.sql` 核对数据。
5. 后续步骤的脚本和 Notebook 会按进度补充。

## 方法概览

| 步骤 | 内容 | 状态 |
|---|---|---|
| SQL 数据提取与分群统计 | SQLite 建库、关联交易表与身份表、分群欺诈率 | 进行中 |
| 数据清洗与特征工程 | 缺失值、时间特征、频次编码、卡片聚合特征 | 待补充 |
| 模型训练与评估 | 时间切分；逻辑回归 / LightGBM / XGBoost | 待补充 |
| SHAP 解释 | 全局特征重要性与单笔案例 | 待补充 |
| 业务风控建议 | 基于模型结果的规则与流程建议 | 待补充 |
| Tableau 看板 | 欺诈特征画像看板 | 待补充 |

## 研究问题

总问题：哪些交易具有高欺诈风险？如何建立模型预测它？有没有什么可以减少欺诈率的策略？

要解决这个问题，我们分成三个阶段:了解欺诈情况、选择变量建模、结合前两者提出建设性策略： 如何在降低欺诈损失的同时，尽量少误拦正常用户

## 1. 了解欺诈情况

| 子问题 | 用到的变量 | 衡量指标 | 假设 |
|---|---|---|---|
| 整体欺诈有多严重? | isFraud、TransactionAmt | 欺诈率、欺诈金额占比 | 欺诈率很低,但金额占比可能高于笔数占比 |
| 哪类产品风险高? | ProductCD | 各产品欺诈率、交易数 | 交易量最大的产品欺诈率最低,小众产品交易数少但欺诈率可能明显更高,需结合样本量判断 |
| 哪类银行卡风险高? | card4、card6 | 各 card 类型的欺诈率及人数 | — |
| 哪些邮箱域名风险高? | P_emaildomain、R_emaildomain | 每种域名的欺诈率及每组样本量 | — |
| 哪类设备风险高? | DeviceType | 每种设备的欺诈率、交易数 | — |
| 什么时段风险高? | TransactionDT | 切分成每小时,计算欺诈率、交易数 | — |
| 什么金额风险高? | TransactionAmt | 十分位数,计算每组欺诈率、交易数 | 欺诈集中在极小额和极大额两端 |
| 有没有身份信息? | has_identity(视图里建的那一列) | 有、无两组的欺诈率和交易数 | — |
| 欺诈随时间有变化吗? | TransactionDT 换算成相对第几天 | 每天欺诈率走势 | — |


* 因为小金额和大金额盗刷问题最严重，所以需要切出两端的数据
* 只有card 4 & 6 是分类型变量，分组有意义。其他card取值种类太多，分组后每组样本量过小，无意义。


## 技术栈

SQL（SQLite）· Python（pandas、scikit-learn、LightGBM、XGBoost、SHAP）· Tableau
