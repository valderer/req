# 商城接口自动化测试项目

这是一个基于真实商城业务场景持续完善的接口自动化测试项目。目前覆盖登录鉴权、商品列表、购物车和收货地址模块，并已接入 GitHub、Jenkins、Webhook 和 Allure，实现代码推送后自动执行测试并发布报告。

> 本项目仅用于经过授权的测试环境。账号、密码、Token 等敏感信息不提交到 Git 仓库。

## 技术栈

- Python
- Requests
- Pytest
- Allure
- YAML
- Git / GitHub
- Jenkins Pipeline
- GitHub Webhook

## 已实现功能

### 登录鉴权

- 登录接口封装
- 从登录响应中提取 Bearer Token
- 使用 session 级 fixture 复用登录 Token
- Jenkins Credentials 注入账号、密码和环境地址

### 商品模块

- 查询商品列表
- 商品分页查询
- 校验商品列表响应结构和关键字段

### 购物车模块

- 添加商品到购物车
- 查询购物车并校验新增商品
- 商品数量参数化测试
- 验证数量为 `0` 的商品进入失效购物车
- 删除购物车商品
- 删除后再次查询，确认商品不存在

### 地址模块

- 添加、查询和删除地址的完整流程
- 手机号正常值、空值、短值和超长值测试
- 精确校验地址字段和接口错误信息
- 测试结束后清理创建的数据

### 工程能力

- API 层与测试层分离
- YAML 管理测试数据
- pytest fixture 管理客户端、Token 和 API 对象
- pytest 参数化和测试标记
- 请求方法、URL、状态码和耗时日志
- Allure 测试步骤、请求参数和响应附件
- GitHub Webhook 自动触发服务器 Jenkins

## 项目结构

```text
req/
├── api/                    # 接口封装
│   ├── login_api.py
│   ├── product_api.py
│   ├── cart_api.py
│   └── address_api.py
├── common/                 # 公共工具
│   ├── env_util.py
│   ├── logger.py
│   ├── request_client.py
│   └── yaml_util.py
├── data/                   # YAML 测试数据
│   ├── product.yaml
│   ├── cart.yaml
│   └── address.yaml
├── tests/                  # pytest 测试用例
│   ├── test_product.py
│   ├── test_cart_flow.py
│   ├── test_cart_parameters.py
│   ├── test_address_flow.py
│   └── test_address_parameters.py
├── scripts/
│   └── run_tests.sh        # 本地测试、生成并打开 Allure 报告
├── conftest.py             # 公共 fixture
├── pytest.ini              # pytest 配置和标记
├── requirements.txt        # Python 依赖
├── Jenkinsfile             # Jenkins Pipeline
├── .env.example            # 环境变量模板
└── .gitignore
```

## 本地运行

### 1. 创建虚拟环境

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows：

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 3. 配置测试环境

复制环境变量模板：

```bash
cp .env.example .env
```

在 `.env` 中填写有权使用的测试环境信息：

```dotenv
BASE_URL=https://your-test-environment.example.com
TEST_USERNAME=your_test_username
TEST_PASSWORD=your_test_password
TEST_COMPANY_ID=2
TEST_TIMEOUT=15
```

`.env` 已加入 `.gitignore`，不要将真实账号、密码或 Token 提交到 GitHub。

### 4. 执行测试

执行默认测试集：

```bash
pytest -v
```

执行指定模块：

```bash
pytest -m product -v
pytest -m cart -v
pytest -m address -v
```

执行冒烟或回归测试：

```bash
pytest -m smoke -v
pytest -m regression -v
```

组合标记：

```bash
pytest -m "cart and regression" -v
```

## Allure 报告

pytest 会根据 `pytest.ini` 自动清理并生成：

```text
allure-results/
```

使用 Allure 本地服务查看报告：

```bash
allure serve allure-results
```

macOS 也可以使用项目脚本完成测试、生成报告并打开浏览器：

```bash
./scripts/run_tests.sh
```

运行指定模块：

```bash
./scripts/run_tests.sh tests/test_product.py -v -s
```

## 测试标记

| 标记 | 用途 |
|---|---|
| `smoke` | 核心业务冒烟测试 |
| `regression` | 完整回归测试 |
| `product` | 商品模块 |
| `cart` | 购物车模块 |
| `address` | 地址模块 |

## 日志

请求层会记录请求方法、URL、HTTP 状态码、耗时和网络异常。日志文件为：

```text
logs/test.log
```

日志不会主动记录密码、Token、Authorization 或完整响应正文，`*.log` 也已加入 `.gitignore`。

## Jenkins 持续集成

流水线当前执行：

```text
GitHub Checkout
    ↓
创建 .venv-ci 虚拟环境
    ↓
安装 requirements.txt
    ↓
注入 Jenkins Credentials
    ↓
执行 pytest
    ↓
发布 Allure Report
```

Jenkins 需要创建以下凭据：

| Credentials ID | 类型 | 用途 |
|---|---|---|
| `req-test-account` | Username with password | 提供 `TEST_USERNAME` 和 `TEST_PASSWORD` |
| `req-base-url` | Secret text | 提供 `BASE_URL` |

同时需要安装并配置：

- Git Plugin
- Pipeline Plugin
- Credentials Binding Plugin
- Allure Jenkins Plugin
- Allure Commandline

Pipeline 任务配置：

```text
Definition: Pipeline script from SCM
SCM: Git
Repository: https://github.com/valderer/req.git
Branch: */main
Script Path: Jenkinsfile
```

GitHub Webhook 地址格式：

```text
http://<Jenkins服务器地址>:8080/github-webhook/
```

代码推送后的执行链路：

```text
git push
    ↓
GitHub Webhook
    ↓
服务器 Jenkins 自动构建
    ↓
pytest 自动测试
    ↓
在构建页面查看 Allure Report
```

## 日常开发流程

```bash
git switch -c feature/your-feature
pytest -v
git status
git diff
git add .
git commit -m "新增某模块接口测试"
git push origin feature/your-feature
```

合并到 `main` 后，GitHub Webhook 会触发 Jenkins 自动构建。

## 后续计划

- 增加商品详情和商品异常查询场景
- 增加购物车数量修改接口
- 增加地址修改接口
- 增加订单创建、查询和取消模块
- 使用 `yield fixture` 统一管理测试数据清理
- 增加非法 Token、缺少字段、类型错误等异常用例
- 将 Jenkins 拆分为冒烟测试和回归测试阶段
- 增加数据库校验和构建失败通知

目标是持续完善为包含 3～5 个业务模块、30～80 条有效用例的商城接口自动化测试项目。
