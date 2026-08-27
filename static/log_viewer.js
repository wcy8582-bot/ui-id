/**
 * 执行日志实时查看器（断线重连 + 断点续传客户端）
 *
 * 可靠性设计：
 * 1. lastSeq 记录已渲染的最大序号，重连时通过连接参数上报，
 *    服务端补发断线期间的日志（replay 事件），实现断点续传；
 * 2. 对每条实时 log 消息做 seq 连续性校验：seq !== lastSeq + 1
 *    说明中间有静默丢失（如消息在断线瞬间发出），主动断开重连触发补发，
 *    而不是把"不完整的日志"当完整日志展示；
 * 3. 重连用 socket.io 内置的指数退避，避免服务端重启时被重连风暴打满；
 * 4. 服务端缓冲截断（truncated）时明确提示用户，不伪造完整性。
 */

let lastSeq = 0;
let socket = null;

function connectLogStream() {
  socket = io({
    query: { last_seq: lastSeq },
    reconnection: true,
    reconnectionDelay: 1000,       // 首次重连 1s
    reconnectionDelayMax: 15000,   // 退避上限 15s
    randomizationFactor: 0.5,      // 加抖动，防多客户端同时重连
  });

  // 连接/重连成功：服务端会先推 replay 补缺口，之后进入实时流
  socket.on("replay", (data) => {
    data.logs.forEach((m) => renderLine(m.seq, m.line));
    lastSeq = Math.max(lastSeq, data.current_seq);
    if (data.truncated) {
      renderSystemLine("⚠ 断线时间过久，中间部分日志已不可恢复");
    }
    setStatus("已连接");
  });

  socket.on("log", (m) => {
    if (m.seq <= lastSeq) return;          // 补发与实时流重叠，去重
    if (m.seq !== lastSeq + 1) {
      // 序号出现空洞 → 静默丢消息，主动重连触发服务端补发
      socket.disconnect();
      socket.connect();
      return;
    }
    renderLine(m.seq, m.line);
    lastSeq = m.seq;
  });

  socket.on("disconnect", () => setStatus("连接断开，重连中…"));
}

function renderLine(seq, line) {
  const el = document.getElementById("log-panel");
  const div = document.createElement("div");
  div.dataset.seq = seq;
  div.textContent = line;
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

function renderSystemLine(text) { /* 渲染系统提示行，样式区分 */ }
function setStatus(text) { /* 更新连接状态角标 */ }

connectLogStream();
