import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.faiss import FAISS
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from docx import Document
import pytesseract
from PIL import Image
import openpyxl
from langchain.schema import SystemMessage, HumanMessage

VECTORSTORE_PATH = "faiss_index"


def get_text_from_word(doc):
    """
    Đọc văn bản từ tài liệu Word.
    """
    doc = Document(doc)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def get_text_from_excel(doc):
    """
    Đọc văn bản từ tệp Excel.
    """
    wb = openpyxl.load_workbook(doc)
    sheet = wb.active
    text = ""
    for row in sheet.iter_rows(values_only=True):
        text += " ".join([str(cell) for cell in row]) + "\n"
    return text

def get_text_from_image(image_file):
    """
    Chuyển đổi văn bản trong hình ảnh thành text bằng OCR.
    """
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def get_pdf_text(pdf_docs):
    """
    Đọc và trích xuất văn bản từ PDF, Word, Excel và Hình ảnh.
    """
    text = ""
    for doc in pdf_docs:
        if doc.type == "application/pdf":
            pdf_reader = PdfReader(doc)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif doc.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text += get_text_from_word(doc)
        elif doc.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            text += get_text_from_excel(doc)
        elif doc.type in ["image/png", "image/jpeg"]:
            text += get_text_from_image(doc)
    return text

def get_text_chunks(text):
    """
    Chia nội dung văn bản thành các đoạn nhỏ để xử lý dễ dàng hơn.

    Args:
        text (str): Nội dung văn bản cần chia nhỏ.

    Returns:
        list: Danh sách các đoạn văn bản nhỏ.
    """
    text_splitter = CharacterTextSplitter(
        separator="\n",  # Ngăn cách các đoạn bằng dấu xuống dòng
        chunk_size=1000,  # Kích thước mỗi đoạn
        chunk_overlap=200,  # Độ chồng lấn giữa các đoạn để giữ ngữ cảnh
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks, open_ai_keys):
    """
    Kiểm tra nếu đã có FAISS index lưu trữ, thì tải lại.
    Nếu chưa có, tạo mới và lưu lại để sử dụng sau này.
    """
    embeddings = OpenAIEmbeddings(
        base_url="https://models.inference.ai.azure.com",
        api_key=open_ai_keys,
        model="text-embedding-3-large"
    )

    # Kiểm tra nếu index đã tồn tại
    if os.path.exists(f"{VECTORSTORE_PATH}/index"):
        print("✅ Loading existing FAISS index...")
        vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings)
    else:
        print("⚠️ No existing FAISS index found. Creating a new one...")
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        vectorstore.save_local(VECTORSTORE_PATH)  # Lưu lại FAISS index

    return vectorstore

def get_conversation_chain(vectorstore, open_ai_keys):
    """
    Tạo chuỗi hội thoại bằng mô hình ngôn ngữ và vector store để xử lý truy vấn.

    Args:
        vectorstore (FAISS): Vector store chứa dữ liệu embeddings.
        open_ai_keys (str): API key của OpenAI để sử dụng mô hình ChatGPT.

    Returns:
        ConversationalRetrievalChain: Chuỗi hội thoại với trí nhớ ngữ cảnh.
    """
    llm = ChatOpenAI(
        openai_api_base="https://models.inference.ai.azure.com",
        openai_api_key=open_ai_keys,
        model_name="gpt-4o-mini",
        temperature=1,
        max_tokens=4096
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True  # Lưu trữ lịch sử hội thoại
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),  # Lấy dữ liệu từ vector store
        memory=memory
    )
    return conversation_chain

def summarize_text_from_documents(documents, open_ai_keys):
    """
    Tóm tắt nội dung tài liệu bằng cách sử dụng OpenAI GPT.
    """
    llm = ChatOpenAI(
        openai_api_base="https://models.inference.ai.azure.com",
        openai_api_key=open_ai_keys,
        model_name="gpt-4o-mini",
        temperature=1,
        max_tokens=4096
    )

    # Kết hợp nội dung từ tất cả các tài liệu thành một văn bản lớn
    combined_text = "\n\n".join([doc['text'] for doc in documents])

    # Định dạng tin nhắn để tóm tắt nội dung
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=f"Summarize the following text: {combined_text}")
    ]

    # Gọi mô hình ChatOpenAI để tóm tắt văn bản
    response = llm.invoke(messages)

    # Trả về nội dung tóm tắt từ kết quả
    summarized_text = response.content
    return summarized_text


def save_feedback(feedback_data, filename="feedback.json"):
    """
    Save feedback data to a JSON file for persistence.
    """
    try:
        with open(filename, "a") as f:
            json.dump(feedback_data, f)
            f.write("\n")  # To separate each feedback entry by a new line.
    except Exception as e:
        print(f"Error saving feedback: {e}")

def handle_user_feedback(response_message):
    """
    Collect user feedback on the quality and relevance of a response.
    """
    thumbs_up = st.button("👍 Thumbs Up")
    thumbs_down = st.button("👎 Thumbs Down")

    if thumbs_up:
        feedback = {"feedback": "positive", "message": response_message}
        st.session_state.feedback.append(feedback)
        save_feedback(feedback)
        st.success("Thank you for your positive feedback!")
    elif thumbs_down:
        feedback = {"feedback": "negative", "message": response_message}
        st.session_state.feedback.append(feedback)
        save_feedback(feedback)
        st.success("Thank you for your feedback! We'll work on improving the answers.")


def adjust_relevance_based_on_feedback(vectorstore, feedback_file="feedback.json"):
    """
    Adjust document relevance in the vectorstore based on accumulated feedback.
    """
    try:
        with open(feedback_file, 'r') as f:
            feedback_data = [json.loads(line) for line in f.readlines()]
        
        # Process feedback and adjust vectorstore accordingly
        # For example, increase the weight of documents marked as "positive" feedback
        for feedback in feedback_data:
            if feedback["feedback"] == "positive":
                # Adjust vectorstore based on positive feedback (this is a simplified example)
                # In practice, you'd use the feedback to fine-tune document embeddings or retrieval strategy.
                pass
    except Exception as e:
        print(f"Error adjusting relevance: {e}")