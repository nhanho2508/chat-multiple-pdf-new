import streamlit as st
from dotenv import load_dotenv
import os
import tempfile
from utils import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain, summarize_text_from_documents
from html_lib import bot_template, user_template, not_found_template
from gtts import gTTS  # Thư viện chuyển văn bản thành giọng nói
from io import StringIO
from io import BytesIO

def save_chat_history():
    """
    Lưu lịch sử hội thoại vào file TXT để tải xuống.
    """
    if "chat_history" in st.session_state and st.session_state.chat_history:
        with open("chat_history.txt", "w", encoding="utf-8") as file:
            for message in st.session_state.chat_history:
                role = "User" if message.content.startswith("Q:") else "Bot"
                file.write(f"{role}: {message.content}\n")
        st.success("✅ Chat history saved!")

def text_to_speech(text):
    """
    Chuyển đổi văn bản thành giọng nói và phát âm thanh.

    Args:
        text (str): Văn bản cần chuyển thành giọng nói.
    """
    try:
        tts = gTTS(text, lang="en")
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)
        st.audio(temp_audio.name, format="audio/mp3")
    except Exception as e:
        st.error(f"⚠️ Error in TTS: {str(e)}")

def handle_userinput(user_question):
    """
    Xử lý câu hỏi của người dùng và hiển thị phản hồi từ chatbot.
    """
    if "conversation" not in st.session_state or st.session_state.conversation is None:
        st.error("⚠️ Please upload PDFs and click 'Process' before asking questions.")
        return


    response = st.session_state.conversation.invoke({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            if "I don't know" in message.content or "I couldn't find an answer" in message.content:
                st.write(not_found_template, unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                text_to_speech(message.content)





def generate_report(documents, open_ai_keys):
    """
    Tạo báo cáo từ nội dung các tài liệu đã tải lên và cung cấp khả năng tải xuống.
    """
    # Tóm tắt nội dung từ các tài liệu
    summarized_text = summarize_text_from_documents(documents, open_ai_keys)

    # Tạo báo cáo từ nội dung tóm tắt
    report_content = f"Document Summary Report\n\nSummarized Content:\n{summarized_text}"

    # Chuyển đổi nội dung báo cáo thành dạng bytes
    report_bytes = BytesIO(report_content.encode("utf-8"))

    # Cho phép người dùng tải xuống báo cáo
    return report_bytes

def main():
    """
    Chạy ứng dụng Streamlit và xử lý các bước tải file PDF.
    """
    load_dotenv()
    open_ai_keys = os.getenv("OPENAI_API_KEY")

    st.set_page_config(page_title="Chat with multiple Documents", page_icon="📚")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("🧠 Chat with multiple PDFs 📚")

    user_question = st.text_input("💬 Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("📂 Your documents")
        pdf_docs = st.file_uploader("📤 Upload your PDFs here and click 'Process'", accept_multiple_files=True)

        if st.button("⚙️ Process"):
            if not pdf_docs:
                st.error("⚠️ Please upload at least one PDF file before processing!")
            else:
                with st.spinner("🔄 Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)

                    if not text_chunks:
                        st.error("⚠️ No text extracted from the uploaded PDFs. Please check the file content.")
                    else:
                        vectorstore = get_vector_store(text_chunks, open_ai_keys)
                        st.session_state.conversation = get_conversation_chain(vectorstore, open_ai_keys)
                        st.success("✅ Processing complete! You can now ask questions.")


        # Nút lưu lịch sử chat
        if st.button("💾 Save Chat History"):
            save_chat_history()
            with open("chat_history.txt", "rb") as file:
                st.download_button("⬇️ Download Chat History", file, "chat_history.txt")

        if st.button("Generate Report"):
        # Kiểm tra xem đã có tài liệu nào được tải lên chưa
            if not pdf_docs:
                st.error("⚠️ Please upload at least one PDF before generating the report.")
            else:
                # Xử lý tạo báo cáo từ các tài liệu PDF
                with st.spinner("🔄 Generating Report..."):
                    raw_text = get_pdf_text(pdf_docs)  # Lấy nội dung văn bản từ tài liệu
                    text_chunks = get_text_chunks(raw_text)  # Chia văn bản thành các đoạn nhỏ
                    if not text_chunks:
                        st.error("⚠️ No text extracted from the uploaded PDFs. Please check the file content.")
                    else:
                        # Tạo báo cáo từ nội dung đã được chia thành các đoạn
                        documents = [{'text': chunk} for chunk in text_chunks]
                        report_bytes = generate_report(documents, open_ai_keys)  # Tạo báo cáo từ nội dung tài liệu
                        st.download_button("⬇️ Download Report", report_bytes, "document_report.txt", "text/plain")

if __name__ == '__main__':
    main()
