"""
AnswerGenerator: builds a grounded answer from retrieved chunks.

Hallucination-suppression prompt:
  - Instructs the LLM to answer ONLY from the provided context.
  - If the context is insufficient, explicitly say so in Japanese.
  - Always cite the source document and page number.
"""

from __future__ import annotations

from typing import Any, Generator

from app.core.config import settings

SYSTEM_PROMPT = """\
あなたは社内ドキュメントQ&Aアシスタントです。
以下のルールを厳守してください：

1. 回答は必ず「提供されたコンテキスト」の情報のみに基づくこと。
2. コンテキストに記載のない情報は回答に含めないこと。
3. コンテキストが不十分な場合は「提供されたドキュメントにはその情報が見つかりませんでした。」と答えること。
4. 回答の末尾に必ず参照元ドキュメント名とページ番号を記載すること。
5. 回答は日本語で行うこと。
"""

HUMAN_TEMPLATE = """\
## 参照コンテキスト

{context}

## 質問

{question}
"""


def _build_context(chunks: list[dict[str, Any]]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        meta = chunk["metadata"]
        parts.append(
            f"[{i}] ファイル: {meta['filename']}  ページ: {meta['page']}\n"
            f"{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)


def _build_llm(streaming: bool = False):
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.llm_model,
            anthropic_api_key=settings.anthropic_api_key,
            streaming=streaming,
            max_tokens=1024,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            streaming=streaming,
        )


class AnswerGenerator:
    def generate(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> str:
        """Generate a grounded answer (blocking)."""
        from langchain_core.messages import HumanMessage, SystemMessage

        context = _build_context(chunks)
        llm = _build_llm(streaming=False)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=HUMAN_TEMPLATE.format(context=context, question=question)),
        ]
        response = llm.invoke(messages)
        return response.content  # type: ignore[return-value]

    def stream(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> Generator[str, None, None]:
        """Stream answer tokens one by one."""
        from langchain_core.messages import HumanMessage, SystemMessage

        context = _build_context(chunks)
        llm = _build_llm(streaming=True)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=HUMAN_TEMPLATE.format(context=context, question=question)),
        ]
        for token in llm.stream(messages):
            yield token.content  # type: ignore[attr-defined]
