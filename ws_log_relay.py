"""执行日志 WebSocket 实时推送 + 断线重连续传模块

解决的问题：
    管理平台查看用例执行日志时，WebSocket 断线（网络抖动、电脑休眠、
    Nginx 空闲超时）后，断线期间的日志永久丢失，用户只能刷新重来，
    而刷新会丢失上下文且长任务执行中无法回看。

方案：
    服务端维护一个带递增序号的环形日志缓冲（LogBuffer）。
    每条日志分配 seq 后才推送。客户端记录已收到的最大 seq，
    重连时在连接参数里带上 last_seq，服务端把 (last_seq, current]
    区间的日志补发（断点续传），客户端按 seq 去重渲染。
    同时对每条下行消息做 seq 连续性校验，发现空洞主动请求全量同步，
    防止"静默丢消息"。

挂载方式（在 app.py 中）：
    from ws_log_relay import init_log_relay, push_log
    socketio = init_log_relay(app)
    # 业务代码/日志 Handler 里调用 push_log("...") 即可推送
    if __name__ == "__main__":
        socketio.run(app, host="0.0.0.0", port=5000)  # 替换 app.run()

依赖：pip install flask-socketio
"""

import logging
from collections import deque

from flask import request
from flask_socketio import SocketIO

BUFFER_SIZE = 5000  # 环形缓冲容量：约覆盖一次完整执行的日志量


class LogBuffer:
    """带递增序号的环形日志缓冲。

    序号只增不减；缓冲满时最旧的消息被淘汰。
    若客户端 last_seq 太旧（缺口已被淘汰），补发时返回 truncated=True，
    客户端据此提示"中间部分日志已不可恢复"并展示现有部分，
    而不是假装日志是完整的。
    """

    def __init__(self, maxlen: int = BUFFER_SIZE):
        self._buf: deque[tuple[int, str]] = deque(maxlen=maxlen)
        self._seq = 0

    def append(self, line: str) -> int:
        self._seq += 1
        self._buf.append((self._seq, line))
        return self._seq

    @property
    def current_seq(self) -> int:
        return self._seq

    def since(self, last_seq: int) -> tuple[list[tuple[int, str]], bool]:
        """返回 last_seq 之后的日志，以及缓冲是否已截断（缺口不可恢复）。"""
        truncated = bool(self._buf) and self._buf[0][0] > last_seq + 1
        return [(s, line) for s, line in self._buf if s > last_seq], truncated


log_buffer = LogBuffer()
socketio: SocketIO | None = None


def push_log(line: str, execution_id: str | None = None) -> None:
    """业务侧唯一入口：写入缓冲并广播。先落缓冲再推送，保证断线者可补。"""
    seq = log_buffer.append(line)
    if socketio is not None:
        socketio.emit(
            "log",
            {"seq": seq, "line": line, "execution_id": execution_id},
        )


class SocketIOLogHandler(logging.Handler):
    """挂到现有 logger 上的 Handler，把日志旁路推送到 WebSocket。

    不改动现有日志文件逻辑，只追加一个输出通道，符合最小侵入原则：
        from ws_log_relay import SocketIOLogHandler
        logger.addHandler(SocketIOLogHandler())
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            push_log(self.format(record))
        except Exception:
            # 推送失败绝不能影响测试执行主流程
            pass


def init_log_relay(app) -> SocketIO:
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    @socketio.on("connect")
    def on_connect():
        # 客户端重连时带上已收到的最大序号，服务端补发缺口 = 断点续传
        last_seq = int(request.args.get("last_seq", 0))
        missed, truncated = log_buffer.since(last_seq)
        socketio.emit(
            "replay",
            {
                "logs": [{"seq": s, "line": line} for s, line in missed],
                "current_seq": log_buffer.current_seq,
                "truncated": truncated,
            },
            to=request.sid,
        )

    return socketio
