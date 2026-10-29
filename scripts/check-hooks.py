#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check-hooks.py —— .codebuddy/hooks/ 的功能冒烟与门禁回归测试

为什么需要这个文件
------------------
上游用 `scripts/hook-battery.sh`（196 KB）测 hook，但它是纯 Bash，依赖
GNU coreutils、`diff <()`、`mktemp -d` 等；Windows Git Bash 下部分用例不可靠，
且它假定 hook 位于 `.claude/hooks/` 并用 `python3` 调用。迁移后需要一份
**跨平台、可被 CI 与本地同时执行**的最小回归集。

本文件不替代 hook-battery.sh（后者是上游的全量用例集，仍保留供 Linux CI
使用），只覆盖「迁移是否会静默削弱门禁」这一个问题。原则是：

  宁可少测，也不测出假绿。任何一条用例无法在本环境判定，就记为 SKIP 并
  写明原因，绝不写成 PASS。

用法
----
    python scripts/check-hooks.py            # 全部用例
    python scripts/check-hooks.py -v         # 打印每个 hook 的原始输出
    python scripts/check-hooks.py --only root-of-trust

退出码
------
    0  全部 PASS（SKIP 不计为失败）
    1  存在 FAIL
    2  测试器自身异常（找不到 hook 目录等）

被测对象
--------
只测 Python hook。`notify.sh` / `hook-runner.sh` 需要在真实 shell 里执行，
本测试器不 spawn shell（沙箱策略禁止从脚本侧绕过命令校验），
因此它们由运行时验证覆盖，见 quality_reports/audits/。
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK_DIR = ROOT / ".codebuddy" / "hooks"

# 钩子会把会话状态写进用户目录（`~/.workbuddy/sessions/<hash>/`）。用例跑在
# 调用者的真实家目录里会做两件坏事：留下垃圾，以及**让上一次运行的残留影响
# 这一次的判定**（throttle 状态、pre-compact 状态都是按项目 hash 存在那里的）。
# 所以整个电池跑在一个临时家目录里。Windows 上 `Path.home()` 读 USERPROFILE 而
# 不是 HOME，两个都要设，否则隔离只在 POSIX 上生效。
_TMP_HOME = tempfile.mkdtemp(prefix="check-hooks-home-")
atexit.register(shutil.rmtree, _TMP_HOME, True)

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


# --------------------------------------------------------------------------
# 用例定义
#
# 每条： (id, hook 文件名, 事件名, 工具名, tool_input, 期望, 一句话说明)
# 期望取值：
#   "deny"  —— hook 必须输出 permissionDecision=deny
#   "allow" —— hook 必须不输出 deny（可以为空，也可以是 allow/无 decision）
#   "exit0" —— 只要求正常退出、输出合法 JSON 或空（用于记录类 hook）
# --------------------------------------------------------------------------

BASH = lambda cmd: {"command": cmd}  # noqa: E731

CASES = [
    # --- git-guardrails：历史改写类命令 -----------------------------------
    ("G1", "git-guardrails.py", "PreToolUse", "Bash",
     BASH("git reset --hard HEAD"), "deny", "reset --hard 必须拦截"),
    ("G2", "git-guardrails.py", "PreToolUse", "Bash",
     BASH("git add -A"), "deny", "git add -A 必须拦截（P0 已在运行时验证）"),
    ("G3", "git-guardrails.py", "PreToolUse", "Bash",
     BASH("git push --force origin main"), "deny", "强推必须拦截"),
    ("G4", "git-guardrails.py", "PreToolUse", "Bash",
     BASH("git clean -fd"), "deny", "git clean -fd 必须拦截"),
    ("G5", "git-guardrails.py", "PreToolUse", "Bash",
     BASH("git status"), "allow", "只读命令不得误杀"),
    ("G6", "git-guardrails.py", "PreToolUse", "Bash",
     BASH("git commit -m 'x'"), "allow", "普通提交不得误杀"),

    # --- root-of-trust-guard：信任根保护（迁移的关键点）-------------------
    ("R1", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("rm -f .codebuddy/hooks/git-guardrails.py"), "deny",
     "删除新信任根的 hook 必须拦截 —— 迁移前这里会被放行"),
    ("R2", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("echo X > .codebuddy/settings.json"), "deny",
     "覆写新信任根的 settings.json 必须拦截"),
    ("R3", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("echo X > .codebuddy/settings.local.json"), "deny",
     "覆写 settings.local.json 必须拦截"),
    ("R4", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("rm -rf .codebuddy/hooks"), "deny",
     "整目录删除 hooks 必须拦截"),
    ("R5", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("echo X > .claude/settings.json"), "deny",
     "旧信任根仍受保护（迁移期双保护）"),
    ("R6", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("rm -f .codebuddy/rules/plan-first.md"), "allow",
     "rules 属普通内容，不得误拒（否则正常工作流被卡死）"),
    ("R7", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("echo hello"), "allow", "无关命令不得误杀"),
    ("R8", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH('bash -c "git reset --hard"'), "deny",
     "shell 包装必须解包后再判定"),
    ("R9", "root-of-trust-guard.py", "PreToolUse", "Bash",
     BASH("rm -f .codebuddy/skills/hello/SKILL.md"), "allow",
     "skills 属普通内容，不得误拒"),

    # --- issue-guard ------------------------------------------------------
    ("I1", "issue-guard.py", "PreToolUse", "Bash",
     BASH("gh issue create --title x"), "deny",
     "绕过 file-issue.py 直接建 issue 必须拦截"),
    ("I2", "issue-guard.py", "PreToolUse", "Bash",
     BASH("gh issue list"), "allow", "只读 gh 命令不得误杀"),
    ("I3", "issue-guard.py", "PreToolUse", "Bash",
     BASH("python scripts/file-issue.py --title x"), "allow",
     "正规入口必须放行"),

    # --- 记录类 hook：只要求不崩 ------------------------------------------
    ("C1", "claim-reconcile.py", "PostToolUse", "Write",
     {"file_path": str(ROOT / "quality_reports" / "checkpoints" / "_hooktest.md"),
      "content": "hook smoke"}, "exit0", "写入后对账不得崩溃"),
    ("C2", "context-monitor.py", "PostToolUse", "Bash",
     BASH("echo hi"), "exit0", "上下文监控不得崩溃"),
    ("C3", "session-handoff.py", "UserPromptSubmit", None,
     {"prompt": "hook smoke test"}, "exit0", "会话交接不得崩溃"),
    ("C4", "open-issues.py", "SessionStart", None,
     {"source": "startup"}, "exit0", "未决问题清单不得崩溃"),
    ("C5", "pre-compact.py", "PreCompact", None,
     {"trigger": "manual"}, "exit0", "压缩前快照不得崩溃"),
    ("C6", "post-compact-restore.py", "SessionStart", None,
     {"source": "compact"}, "exit0", "压缩后恢复不得崩溃"),
    ("C7", "log-reminder.py", "Stop", None,
     {"stop_hook_active": False}, "exit0", "日志提醒不得崩溃"),
]


def build_stdin(event: str, tool: str | None, tool_input: dict,
                cwd: Path) -> str:
    payload: dict = {"hook_event_name": event, "cwd": str(cwd)}
    if tool:
        payload["tool_name"] = tool
    if tool_input is not None:
        payload["tool_input"] = tool_input
    # 各种 hook 会读不同字段，一次性都填上，避免因缺字段而走 fail-open 分支
    payload.setdefault("session_id", "hook-smoke-session")
    payload.setdefault("transcript_path", "")
    payload.setdefault("stop_hook_active", False)
    payload.setdefault("source", "startup")
    payload.setdefault("trigger", "manual")
    return json.dumps(payload, ensure_ascii=False)


def interpret(stdout: str) -> str:
    """把 hook 的 stdout 归类为 deny / allow。

    WorkBuddy 与上游协议一致：PreToolUse 通过
    hookSpecificOutput.permissionDecision 表达，也接受顶层 decision。
    非 JSON 输出（纯文本提醒）视为 allow。
    """
    text = (stdout or "").strip()
    if not text:
        return "allow"
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return "allow"
    if not isinstance(data, dict):
        return "allow"
    hso = data.get("hookSpecificOutput") or {}
    if isinstance(hso, dict) and str(hso.get("permissionDecision", "")).lower() == "deny":
        return "deny"
    if str(data.get("decision", "")).lower() == "block":
        return "deny"
    if data.get("continue") is False:
        return "deny"
    return "allow"


def run_case(case) -> tuple[str, str, str]:
    cid, hook, event, tool, tool_input, expect, note = case
    hook_path = HOOK_DIR / hook
    if not hook_path.is_file():
        return SKIP, f"hook 文件不存在：{hook_path}", ""

    env = dict(os.environ)
    env["CODEBUDDY_PROJECT_DIR"] = str(ROOT)
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["HOME"] = _TMP_HOME
    env["USERPROFILE"] = _TMP_HOME

    stdin = build_stdin(event, tool, tool_input, ROOT)
    try:
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=stdin.encode("utf-8"),
            capture_output=True,
            cwd=str(ROOT),
            env=env,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return FAIL, "超时（60s）—— hook 阻塞会冻结会话", ""

    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    verdict = interpret(out)
    detail = (out.strip() or err.strip())[:300]

    if expect == "exit0":
        if proc.returncode != 0:
            return FAIL, f"退出码 {proc.returncode}（期望 0）", detail
        # 输出若有内容，必须是合法 JSON，否则平台会解析失败
        if out.strip():
            try:
                json.loads(out.strip())
            except json.JSONDecodeError:
                return FAIL, "stdout 非空但不是合法 JSON", detail
        return PASS, "exit 0，输出合法", detail

    if proc.returncode not in (0, 2):
        return FAIL, f"退出码 {proc.returncode}", detail
    if verdict != expect:
        return FAIL, f"判定为 {verdict}（期望 {expect}）", detail
    return PASS, f"判定为 {verdict}", detail


def check_wiring() -> list:
    """每条注册在 settings.json 里的命令，必须真的到达它的 hook 文件。

    2026-10-30 发现的缺陷：hook-runner.sh 用 `SCRIPT_DIR/../..` 推导仓库根，
    而它自己位于 `<repo>/.codebuddy/hooks/lib/`，于是 ROOT 停在 `.codebuddy`，
    HOOK_PATH 变成 `.codebuddy/.codebuddy/hooks/<name>`。12 条命令全部以 exit 0
    结束、只在 stderr 留一行——fail-open 让「一条都没跑」看起来和「全跑过了」
    一样。下面的用例集测不到它，因为用例直接调用 hook 文件，从不经过注册的
    命令字符串。本函数补的正是这一层：**注册的路径是否可用**。
    """
    import json as _json
    import subprocess as _sp

    settings = HOOK_DIR.parent / "settings.json"
    try:
        data = _json.loads(settings.read_text(encoding="utf-8"))
    except Exception as exc:                       # noqa: BLE001
        return [f"读不到 {settings}: {exc}"]

    repo_root = str(HOOK_DIR.parent.parent)
    bad = []
    for event, entries in (data.get("hooks") or {}).items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                if "notify.sh" in cmd:             # 会真的弹桌面通知
                    continue
                try:
                    proc = _sp.run(["bash", "-c", cmd], input="{}", text=True,
                                   capture_output=True, timeout=90, cwd=repo_root)
                except Exception as exc:           # noqa: BLE001
                    bad.append(f"{event}: 无法执行 → {exc}")
                    continue
                err = proc.stderr or ""
                if "hook 文件不存在" in err or "未找到可用的 Python" in err:
                    bad.append(f"{event}: {err.strip().splitlines()[0]}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description="hook 功能冒烟测试")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印原始输出")
    ap.add_argument("--only", default="", help="只跑 id 或 hook 名包含该子串的用例")
    args = ap.parse_args()

    if not HOOK_DIR.is_dir():
        print(f"[致命] 找不到 hook 目录：{HOOK_DIR}", file=sys.stderr)
        return 2

    cases = CASES
    if args.only:
        needle = args.only.lower()
        cases = [c for c in CASES
                 if needle in c[0].lower() or needle in c[1].lower()]
        if not cases:
            print(f"[致命] 没有匹配 `{args.only}` 的用例", file=sys.stderr)
            return 2

    print(f"hook 目录：{HOOK_DIR}")
    print(f"解释器  ：{sys.executable}")
    print(f"用例数  ：{len(cases)}\n")
    print(f"{'ID':<4} {'结果':<5} {'hook':<26} 说明")
    print("-" * 96)

    counts = {PASS: 0, FAIL: 0, SKIP: 0}
    failures = []
    for case in cases:
        status, msg, detail = run_case(case)
        counts[status] += 1
        print(f"{case[0]:<4} {status:<5} {case[1]:<26} {case[6]}  → {msg}")
        if status == FAIL:
            failures.append((case[0], case[6], msg, detail))
        if args.verbose and detail:
            for line in detail.splitlines():
                print(f"        | {line}")

    print("-" * 96)
    print(f"PASS {counts[PASS]}   FAIL {counts[FAIL]}   SKIP {counts[SKIP]}")

    wiring = check_wiring()
    if wiring:
        print(f"\n[FAIL] 注册接线：{len(wiring)} 条命令到不了 hook 文件")
        for line in wiring:
            print(f"  {line}")
        counts[FAIL] += len(wiring)

    if counts[FAIL]:
        print("\n失败明细：")
        for cid, note, msg, detail in failures:
            print(f"\n[{cid}] {note}")
            print(f"  {msg}")
            if detail:
                print(f"  输出：{detail}")
        return 1

    print("\n全部通过。注意：本测试器不覆盖需要真实 shell 的 "
          "hook-runner.sh 与 notify.sh，"
          "也不证明 hook 已被平台在正确事件上触发——后者见运行时验收记录。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
