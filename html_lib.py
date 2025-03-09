css = '''
<style>
.chat-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 15px; /* Tăng khoảng cách giữa các tin nhắn */
}

/* Hộp chứa tin nhắn */
.chat-message {
    display: flex;
    align-items: center;
    padding: 12px;
    border-radius: 12px;
    max-width: 80%;
    word-wrap: break-word;
    gap: 12px; /* Tạo khoảng cách giữa avatar và nội dung */
    margin-bottom: 15px; /* Tăng khoảng cách giữa các tin nhắn */
}

/* Màu nền tin nhắn người dùng */
.chat-message.user {
    background-color: #0078ff;
    color: white;
    align-self: flex-end;
    text-align: left;
}

/* Màu nền tin nhắn bot */
.chat-message.bot {
    background-color: #f0f0f0;
    color: black;
    align-self: flex-start;
    text-align: left;
}

/* Màu nền tin nhắn bot khi không tìm thấy câu trả lời */
.chat-message.bot.not-found {
    background-color: #ffeb3b;
    color: black;
    font-weight: bold;
    text-align: left;
    border: 2px solid #ff9800;
}

/* Avatar */
.chat-message .avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
}

/* Hộp chứa nội dung tin nhắn */
.chat-message .message-content {
    display: flex;
    flex-direction: column;
    padding: 10px;
    border-radius: 10px;
    font-size: 16px;
    line-height: 1.5;
    max-width: 100%;
    background-color: rgba(255, 255, 255, 0.9);
}
</style>
'''


bot_template = '''
<div class="chat-message bot" style="display: flex; align-items: center; padding: 12px; border-radius: 12px; background-color: #f0f0f0; color: black; max-width: 80%; gap: 10px; margin-bottom: 15px; ">
    <img class="avatar" src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
    <div class="message" style="font-size: 16px; line-height: 1.5; padding: 10px; border-radius: 10px; background-color: rgba(255, 255, 255, 0.9);">
        {{MSG}}
    </div>
</div>
'''

user_template = '''
<div class="chat-message user" style="display: flex; align-items: center; padding: 12px; border-radius: 12px; background-color: #0078ff; color: white; max-width: 80%; gap: 10px; align-self: flex-end; margin-bottom: 15px; ">
    <img class="avatar" src="https://cdn-icons-png.flaticon.com/512/9187/9187532.png" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
    <div class="message" style="font-size: 16px; line-height: 1.5; padding: 10px; border-radius: 10px; background-color: rgba(255, 255, 255, 0.2);">
        {{MSG}}
    </div>
</div>
'''



not_found_template = '''
<div class="chat-container">
    <div class="chat-message bot not-found" style="display: flex; align-items: center; padding: 12px; border-radius: 12px; background-color: #ffeb3b; color: black; border: 2px solid #ff9800; max-width: 80%; gap: 10px; margin-bottom: 15px; ">
        <img class="avatar" src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
        <div class="message-content" style="font-size: 16px; line-height: 1.5; padding: 10px; border-radius: 10px; background-color: rgba(255, 255, 255, 0.8);">
            ⚠️ Sorry, I couldn't find an answer to your question. Try rephrasing it or providing more details!
        </div>
    </div>
</div>
'''
