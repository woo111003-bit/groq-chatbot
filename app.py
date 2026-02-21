import streamlit as st
from groq import Groq
import urllib.parse
from datetime import datetime

# [필수] 페이지 설정
st.set_page_config(page_title="번개 챗봇 AI", page_icon="⚡", layout="centered")

# 1. API 키 체크 및 클라이언트 초기화
def get_groq_client():
    if "GROQ_API_KEY" not in st.secrets:
        st.error("🔑 API 키가 설정되지 않았습니다! `.streamlit/secrets.toml` 파일을 확인해주세요.")
        st.stop()
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

client = get_groq_client()

# 2. 세션 상태 관리 (대화 및 메모)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "너는 코딩을 아주 쉽게 알려주는 친절한 선생님이야."}]

# 3. 사이드바 구성
with st.sidebar:
    st.title("⚡ 번개 메뉴")
    if st.button("🧹 대화 기록 지우기"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    
    st.divider()
    st.caption("기록 저장하기")
    chat_log = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system'])
    st.download_button("💾 채팅 로그 다운로드", chat_log, file_name="chat_log.txt")

# 4. 채팅 화면 구현
st.title("⚡ 번개 챗봇 AI")
st.info("무엇이든 물어보세요! 관련 링크도 함께 찾아드립니다.")

# 기존 대화 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="⚡" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

# 5. 사용자 입력 및 AI 응답 (상태 표시 추가)
if prompt := st.chat_input("질문을 입력하세요..."):
    # 유저 메시지 출력
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant", avatar="⚡"):
        # 실용 기능: 상태 바 표시 (생각 중...)
        with st.status("⚡ 번개처럼 생각하는 중...", expanded=True) as status:
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.messages,
                    stream=True
                )
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                
                status.update(label="✅ 답변 완료!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.stop()

        # 6. 실용적인 사이트 바로가기 (답변 완료 후 하단에 자동 생성)
        st.markdown("---")
        st.caption("🔗 추가 학습을 위한 바로가기")
        q = urllib.parse.quote(prompt)
        c1, c2, c3 = st.columns(3)
        c1.link_button("🔍 구글 검색", f"https://www.google.com/search?q={q}")
        c2.link_button("📺 유튜브 강의", f"https://www.youtube.com/results?search_query={q}")
        c3.link_button("📜 위키백과", f"https://ko.wikipedia.org/wiki/{q}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})