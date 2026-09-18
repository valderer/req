# Python 接口自动化测试入门项目

这是一个尽量简单、可以直接运行的示例项目，使用公开的 JSONPlaceholder 接口练习：

- Python
- Requests
- Pytest
- Allure
- YAML
- Git
- Jenkins

## 1. 创建虚拟环境

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows：

```bash
python -m venv .venv
.venv\\Scripts\\activate
```

## 2. 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 3. 执行测试

```bash
pytest
```

测试通过后会在 `allure-results/` 生成 Allure 原始结果。

## 4. 查看 Allure 报告

需要先安装 Allure Commandline，并确认 `allure --version` 可以执行：

```bash
allure serve allure-results
```

## 5. 目录说明

```text
config/       环境配置
data/         测试数据
common/       通用能力：请求和 YAML 读取
api/          接口封装
tests/        测试用例
conftest.py   Pytest 公共 fixture
Jenkinsfile   Jenkins 流水线
```

## 6. Git 初始化

```bash
git init
git add .
git commit -m "初始化接口自动化项目"
```

如果网络不可用，测试会因为无法访问公开接口而失败；代码本身不需要账号或其他本地服务。
