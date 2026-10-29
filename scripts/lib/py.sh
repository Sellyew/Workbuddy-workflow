# py.sh —— 统一的 Python 3 解释器探测（被 scripts/*.sh source）
#
# 为什么必须有这个文件
# --------------------
# 上游所有脚本都写死 `python3`。在 Windows 上：
#
#   $ python3 -c 'print(1)'
#   Python was not found; run without arguments to install from the
#   Microsoft Store...            （退出码 9009）
#
# 注意 `command -v python3` **是成功的** —— 它指向
# %LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe 这个应用执行别名存根。
# 所以判断解释器可用性只能用「真实跑一次 import sys」，绝不能用 command -v。
#
# 这一点在门禁脚本里尤其致命：解释器缺失时脚本退出码非 0，而多数调用方把
# 非 0 当作「检查未通过」，于是看起来是门禁在起作用，实际是它根本没跑。
#
# 用法
# ----
#   . "$(dirname "$0")/lib/py.sh"
#   cb_require_python || exit 127      # 门禁脚本：缺解释器必须失败，不能放行
#   "$PY" scripts/check-links.py
#
# 约定
# ----
#   PY          可用的 Python 命令（可能含空格，如 `py -3`，调用时不要加引号）
#   CB_PY_OK    1 表示可用，0 表示不可用
#   cb_require_python   不可用时打印中文诊断并返回 1

# 允许外部覆盖：CI 里可以用 CODEBUDDY_PYTHON 锁定版本
cb_probe_python() {
    _cand_list="${CODEBUDDY_PYTHON:-} python python3 'py -3'"
    # shellcheck disable=SC2086
    for _cand in $_cand_list; do
        [ -z "$_cand" ] && continue
        # 真实执行一次：存根会在这里暴露（9009 / 非 0）
        if eval "$_cand -c 'import sys; sys.exit(0 if sys.version_info[0]==3 else 1)'" >/dev/null 2>&1; then
            printf '%s' "$_cand"
            return 0
        fi
    done
    return 1
}

PY="$(cb_probe_python)" || PY=""
if [ -n "$PY" ]; then
    CB_PY_OK=1
else
    CB_PY_OK=0
fi
export PY CB_PY_OK

cb_require_python() {
    if [ "${CB_PY_OK:-0}" = "1" ]; then
        return 0
    fi
    {
        echo "错误：未找到可用的 Python 3 解释器。"
        echo "  已尝试：CODEBUDDY_PYTHON / python / python3 / py -3"
        echo "  常见原因：Windows 上 python3 指向 Microsoft Store 存根，执行返回 9009。"
        echo "  处理：安装 python.org 的 Python 3，或设置 CODEBUDDY_PYTHON 指向真实解释器。"
        echo "  注意：本脚本不会在没有 Python 的情况下报告通过——那会产生假绿。"
    } >&2
    return 1
}
