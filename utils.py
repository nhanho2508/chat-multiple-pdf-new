import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.faiss import FAISS
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain

VECTORSTORE_PATH = "faiss_index"

def get_pdf_text(pdf_docs):
    """
    Đọc và trích xuất toàn bộ nội dung văn bản từ danh sách các file PDF.
    
    Args:
        pdf_docs (list): Danh sách các file PDF tải lên.
    
    Returns:
        str: Nội dung văn bản được trích xuất từ tất cả các PDF.
    """
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
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
