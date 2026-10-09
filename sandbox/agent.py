import json
import random
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

from composite_dormancy.trajectory import Trajectory

from .judge import evaluate
from .scenario import SESSION_A, SESSION_B, SYSTEM_PROMPT, WorkspaceState
from .tools import TOOL_SCHEMAS, dispatch


class ModelClient:
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: Optional[float] = 0.7,
        max_tokens: int = 6000,
        timeout: float = 240.0,
        retries: int = 8,
        min_interval: float = 3.5,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.retries = retries
        self.min_interval = min_interval
        self._last_call = 0.0
        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def _throttle(self) -> None:
        wait = self.min_interval - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.time()

    def complete(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None):
        last_error: Optional[Exception] = None
        for attempt in range(self.retries):
            self._throttle()
            try:
                kwargs: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": self.max_tokens,
                }
                if self.temperature is not None:
                    kwargs["temperature"] = self.temperature
                if tools:
                    kwargs["tools"] = tools
                return self._client.chat.completions.create(**kwargs)
            except Exception as exc:
                last_error = exc
                status = getattr(exc, "status_code", None)
                if status == 429:
                    delay = min(60.0, max(5.0, 2.0 ** attempt)) + random.uniform(0.0, 2.0)
                else:
                    delay = min(30.0, 2.0 ** attempt) + random.uniform(0.0, 1.0)
                time.sleep(delay)
        raise RuntimeError(f"completion failed after {self.retries} attempts: {last_error}")


def _assistant_message(msg: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
    if msg.tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in msg.tool_calls
        ]
    return out


def run_session(
    client: ModelClient,
    state: WorkspaceState,
    user_message: str,
    session_id: str,
    max_turns: int = 10,
) -> Trajectory:
    traj = Trajectory(task_id=session_id, original_instruction=user_message)
    traj.append_user_step(user_message)
    traj.start_timer()

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    final = ""

    for _ in range(max_turns):
        response = client.complete(messages, tools=TOOL_SCHEMAS)
        choice = response.choices[0]
        msg = choice.message
        finish_reason = choice.finish_reason
        tool_calls = msg.tool_calls or []

        if not tool_calls:
            final = msg.content or ""
            traj.append_agent_step(
                action="final_response",
                metadata={
                    "message": final,
                    "finish_reason": finish_reason,
                    "reasoning": getattr(msg, "reasoning", None),
                },
            )
            break

        messages.append(_assistant_message(msg))
        for tc in tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            traj.append_agent_step(
                action=f"{tc.function.name}({json.dumps(args, ensure_ascii=False)})",
                tool_name=tc.function.name,
                tool_params=args,
                server="workspace",
            )
            result = dispatch(state, tc.function.name, args)
            traj.append_tool_return(result=result, tool_name=tc.function.name, server="workspace")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    traj.set_final_response(final)
    traj.stop_timer()
    return traj


def run_trial(
    client: ModelClient,
    condition: str = "full",
    max_turns: int = 10,
) -> Dict[str, Any]:
    state = WorkspaceState.build(condition)
    traj_a = run_session(client, state, SESSION_A, f"session_a:{condition}", max_turns)
    notes_after_a = state.notes
    shares_after_a = list(state.share_log)
    traj_b = run_session(client, state, SESSION_B, f"session_b:{condition}", max_turns)
    verdict = evaluate(state)
    return {
        "condition": condition,
        "verdict": verdict,
        "notes_after_a": notes_after_a,
        "shares_after_a": shares_after_a,
        "share_log": state.share_log,
        "session_a": traj_a.to_dict(),
        "session_b": traj_b.to_dict(),
    }
