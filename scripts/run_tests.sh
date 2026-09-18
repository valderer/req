#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# 优先使用项目虚拟环境中的 pytest
PYTEST_BIN="pytest"
if [ -x "$PROJECT_ROOT/.venv/bin/pytest" ]; then
    PYTEST_BIN="$PROJECT_ROOT/.venv/bin/pytest"
fi

# 运行测试，并保留 pytest 的退出状态
"$PYTEST_BIN" "$@"
pytest_status=$?

# 根据本次测试结果生成静态 Allure 报告
if ! allure generate "$PROJECT_ROOT/allure-results" \
    -o "$PROJECT_ROOT/allure-report" --clean; then
    echo "Allure 报告生成失败，请确认 allure 命令已安装。" >&2
    exit "$pytest_status"
fi

# 通过 Allure 自带的 HTTP 服务打开报告，避免直接打开 file:// 导致 500
if [ -f "$PROJECT_ROOT/allure-report/index.html" ]; then
    echo "Allure 报告已生成，正在通过本地服务打开浏览器。"
    allure open "$PROJECT_ROOT/allure-report"
else
    echo "找不到 Allure 报告：$PROJECT_ROOT/allure-report/index.html" >&2
fi

exit "$pytest_status"
