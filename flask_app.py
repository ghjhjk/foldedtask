from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 봇의 토큰과 관리자의 Telegram ID
BOT_TOKEN = "8086387643:AAGX1Mzd5GUHdmtELtVB2nmuZn566du_SkM"
ADMIN_CHAT_ID = "7001739586"

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': ADMIN_CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"RequestException: {e}")
        return False

HTML_FORM = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAN 선텔정지 전용</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .gradient-bg {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
        /* 포커스 시 입력칸과 아이콘이 함께 올라가도록 부모에만 transform 적용 */
        .relative:focus-within {
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        .input-focus-effect:focus {
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
            outline: none;
        }
        .btn-hover-effect:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .btn-active-effect:active { transform: translateY(-1px); }
        .shake { animation: shake 0.5s; }
        @keyframes shake {
            0%,100% { transform: translateX(0); }
            10%,30%,50%,70%,90% { transform: translateX(-5px); }
            20%,40%,60%,80% { transform: translateX(5px); }
        }
        .fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 gradient-bg">
    <div class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-2xl overflow-hidden transition-all duration-300 transform hover:scale-[1.01]">
            <div class="p-8">
                <div class="flex justify-center mb-8">
                    <div class="bg-blue-100 p-4 rounded-full">
                        <i class="fab fa-telegram text-blue-500 text-4xl"></i>
                    </div>
                </div>
                <h2 class="text-2xl font-bold text-center text-gray-800 mb-2">MAN 선텔정지 전용</h2>
                <form id="telegramForm" class="space-y-6">
                    <!-- 닉네임 입력 -->
                    <div>
                        <label for="nickname" class="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none icon-absolute z-10">
                                <i class="fas fa-user text-gray-400"></i>
                            </div>
                            <input
                                type="text"
                                id="nickname"
                                name="nickname"
                                required
                                class="pl-10 input-focus-effect w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200"
                                placeholder="닉네임"
                            />
                        </div>
                    </div>
                    <!-- Telegram ID 입력 -->
                    <div>
                        <label for="telegramId" class="block text-sm font-medium text-gray-700 mb-1">Telegram ID</label>
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none icon-absolute z-10">
                                <i class="fab fa-telegram text-gray-400"></i>
                            </div>
                            <input
                                type="text"
                                id="telegramId"
                                name="telegramId"
                                required
                                class="pl-10 input-focus-effect w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200"
                                placeholder="텔레그램 ID (@제외)"
                            />
                        </div>
                    </div>
                    <!-- Contact Reason 드롭다운 -->
                    <div>
                        <label for="contactReason" class="block text-sm font-medium text-gray-700 mb-1">Contact Reason</label>
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none icon-absolute z-10">
                                <i class="fas fa-question-circle text-gray-400"></i>
                            </div>
                            <select
                                id="contactReason"
                                name="contactReason"
                                required
                                class="pl-10 input-focus-effect w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 appearance-none"
                            >
                                <option value="선텔정지" selected>선텔정지</option>
                            </select>
                        </div>
                    </div>
                    <div id="messageContainer" class="hidden"></div>
                    <button type="submit" id="submitBtn"
                            class="w-full btn-hover-effect btn-active-effect flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200">
                        <span id="btnText">전송</span>
                        <span id="btnSpinner" class="hidden ml-2"><i class="fas fa-spinner fa-spin"></i></span>
                    </button>
                </form>
            </div>
            <div class="bg-gray-50 px-8 py-6 rounded-b-2xl">
                <p class="text-xs text-gray-500 text-center">
                    By submitting this form, you agree to our
                    <a href="#" class="text-blue-600 hover:underline">Terms of Service</a>
                    and acknowledge our
                    <a href="#" class="text-blue-600 hover:underline">Privacy Policy</a>.
                </p>
            </div>
        </div>
    </div>
    <script>
        document.getElementById('telegramForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const nickname = document.getElementById('nickname').value.trim();
            const telegramId = document.getElementById('telegramId').value.trim();
            const contactReason = document.getElementById('contactReason').value;
            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnSpinner = document.getElementById('btnSpinner');
            const messageContainer = document.getElementById('messageContainer');
            messageContainer.innerHTML = '';
            messageContainer.classList.add('hidden');
            if (!nickname || !telegramId || !contactReason) {
                showMessage('모든 항목을 입력해주세요.', 'error');
                document.getElementById('telegramForm').classList.add('shake');
                setTimeout(() => document.getElementById('telegramForm').classList.remove('shake'), 500);
                return;
            }
            submitBtn.disabled = true;
            btnText.textContent = '전송 중...';
            btnSpinner.classList.remove('hidden');
            try {
                const res = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({nickname, telegramId, contactReason})
                });
                const result = await res.json();
                if (result.success) {
                    showMessage('전송 완료!', 'success');
                    document.getElementById('telegramForm').reset();
                } else {
                    showMessage('전송 실패', 'error');
                }
            } catch {
                showMessage('오류 발생. 다시 시도해주세요.', 'error');
            } finally {
                submitBtn.disabled = false;
                btnText.textContent = '전송';
                btnSpinner.classList.add('hidden');
            }
        });
        function showMessage(message, type) {
            const mc = document.getElementById('messageContainer');
            mc.innerHTML = `
                <div class="fade-in rounded-lg p-4 ${type==='success'?'bg-green-100 text-green-800':'bg-red-100 text-red-800'}">
                    <div class="flex items-center">
                        <i class="fas ${type==='success'?'fa-check-circle':'fa-exclamation-circle'} mr-2"></i>
                        <span>${message}</span>
                    </div>
                </div>`;
            mc.classList.remove('hidden');
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    nickname = data.get('nickname')
    telegram_id = data.get('telegramId')
    contact_reason = data.get('contactReason')
    message = f"New user info:\nNickname: {nickname}\nTelegram ID: {telegram_id}\nContact Reason: {contact_reason}"
    success = send_telegram_message(message)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True)
