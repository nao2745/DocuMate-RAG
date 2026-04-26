"""
DocuMate – Streamlit フロントエンド

3 ページ構成:
  1. チャット    – 質問 → 回答 + 引用元
  2. ドキュメント管理 – アップロード / 一覧 / 削除
  3. 設定       – LLM モデル・チャンクサイズ変更
"""

from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


# ── Utilities ─────────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    url = f"{API_BASE}{path}"
    try:
        resp = getattr(requests, method)(url, timeout=120, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("バックエンドに接続できません。`uvicorn app.main:app --reload` を起動してください。")
        return None
    except requests.exceptions.HTTPError as exc:
        detail = exc.response.json().get("detail", str(exc))
        st.error(f"エラー: {detail}")
        return None


# ── Page: Chat ────────────────────────────────────────────────────────────────

def page_chat():
    st.title("💬 DocuMate チャット")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "last_sources" not in st.session_state:
        st.session_state.last_sources = []

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    question = st.chat_input("社内ドキュメントについて質問してください…")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("⏳ 回答を生成中…")

            result = api(
                "post",
                "/api/chat/query",
                json={
                    "question": question,
                    "session_id": st.session_state.session_id,
                },
            )

            if result:
                answer = result["answer"]
                st.session_state.session_id = result["session_id"]
                st.session_state.last_sources = result.get("sources", [])

                placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Feedback buttons
                col1, col2, _ = st.columns([1, 1, 8])
                if col1.button("👍 役立った", key=f"up_{len(st.session_state.messages)}"):
                    api("post", "/api/chat/feedback", json={
                        "session_id": result["session_id"],
                        "question": question,
                        "answer": answer,
                        "rating": 1,
                    })
                    st.toast("フィードバックありがとうございます！")
                if col2.button("👎 的外れ", key=f"down_{len(st.session_state.messages)}"):
                    api("post", "/api/chat/feedback", json={
                        "session_id": result["session_id"],
                        "question": question,
                        "answer": answer,
                        "rating": -1,
                    })
                    st.toast("フィードバックありがとうございます。")
            else:
                placeholder.markdown("回答を取得できませんでした。")

    # Source citation sidebar
    if st.session_state.last_sources:
        with st.sidebar:
            st.subheader("📄 引用元")
            for src in st.session_state.last_sources:
                with st.expander(f"{src['filename']}  p.{src['page']}"):
                    st.caption(f"関連スコア: {src['score']:.4f}")
                    st.text(src["excerpt"])

    if st.sidebar.button("🗑️ 会話をリセット"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.session_state.last_sources = []
        st.rerun()


# ── Page: Document Management ─────────────────────────────────────────────────

def page_documents():
    st.title("📁 ドキュメント管理")

    # Upload
    st.subheader("アップロード")
    uploaded = st.file_uploader(
        "PDF / Word / Markdown / TXT",
        type=["pdf", "docx", "md", "txt"],
        accept_multiple_files=True,
    )
    category = st.text_input("カテゴリ（任意）", value="general")

    if st.button("取り込む", disabled=not uploaded):
        for f in uploaded:
            with st.spinner(f"{f.name} を取り込み中…"):
                result = api(
                    "post",
                    "/api/documents/upload",
                    files={"file": (f.name, f.getvalue(), f.type)},
                    data={"category": category},
                )
                if result:
                    st.success(f"✅ {f.name}  ({result['page_count']} ページ)")

    st.divider()

    # Document list
    st.subheader("登録済みドキュメント")
    result = api("get", "/api/documents")
    if result and result["total"] > 0:
        for doc in result["documents"]:
            col1, col2 = st.columns([5, 1])
            col1.markdown(
                f"**{doc['filename']}**  "
                f"`{doc['file_type'].upper()}`  "
                f"{doc['page_count']} p  —  {doc['category']}"
            )
            if col2.button("削除", key=f"del_{doc['doc_id']}"):
                res = api("delete", f"/api/documents/{doc['doc_id']}")
                if res:
                    st.success(res["message"])
                    st.rerun()
    elif result:
        st.info("登録済みドキュメントはありません。")


# ── Page: Settings ────────────────────────────────────────────────────────────

def page_settings():
    st.title("⚙️ 設定")
    st.info("設定変更は `.env` ファイルを編集してバックエンドを再起動してください。")

    result = api("get", "/health")
    if result:
        st.success(f"バックエンド接続: {API_BASE}  ✅")
    else:
        st.error(f"バックエンド接続: {API_BASE}  ❌")

    st.subheader("現在の設定")
    from app.core.config import settings as cfg
    st.json({
        "llm_provider": cfg.llm_provider,
        "llm_model": cfg.llm_model,
        "embedding_model": cfg.embedding_model,
        "chunk_size": cfg.chunk_size,
        "chunk_overlap": cfg.chunk_overlap,
        "top_k": cfg.top_k,
    })


# ── App shell ─────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="DocuMate",
        page_icon="📚",
        layout="wide",
    )

    page = st.sidebar.selectbox(
        "ページ",
        ["💬 チャット", "📁 ドキュメント管理", "⚙️ 設定"],
    )

    if page == "💬 チャット":
        page_chat()
    elif page == "📁 ドキュメント管理":
        page_documents()
    else:
        page_settings()


if __name__ == "__main__":
    main()
