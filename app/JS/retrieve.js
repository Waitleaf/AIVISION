const retrieveBtn = document.querySelector('.retrieve-btn');
const retrieveSubBtn = document.querySelector('.retrieve-sub-btn');
const inputUsername = document.querySelector('input[name="inputUsername"]');
const inputPasswordValue = document.querySelector('input[name="passwordValue"]');
const registerText = document.querySelector('.registerText');
let backendPasswordValue = '';
let backendPassword = '';

const popup = document.querySelector('#popup');
const closeBtn = document.querySelector('#closePopupBtn');
// 显示弹窗
function showPopup(text, haveTime = true) {
    document.getElementById('text').textContent = `${text}`;
    popup.classList.add('showing');
    popup.classList.remove('hiding');
    if (haveTime) {
        setTimeout(() => {
            popup.classList.remove('showing');
            popup.classList.add('hiding');
            timerStarted = false;
        }, 2000);
    } else {
        popup.classList.remove('showing');
        popup.classList.add('hiding');
        timerStarted = false;
    }
}
//关闭弹窗按钮
closeBtn.addEventListener('click', () => {
    popup.classList.remove('showing');
    popup.classList.add('hiding');
});

retrieveBtn.addEventListener('click', (e) => {
    e.preventDefault();
    retrieveBtn.disabled = true;

    const ws = new WebSocket('ws://localhost:8769');
    ws.onopen = function (event) {
        console.log('连接成功');
        ws.send(JSON.stringify({
            action: 'retrieve',
            credentials: {
                username: inputUsername.value
            }
        }));
        console.log('找回密码--数据已发送');
    };

    ws.onmessage = (event) => {
        const { Back, password, passwordKey, passwordValue } = JSON.parse(event.data); // 解析后端返回的数据
        if (Back === true) {
            showPopup('请输入密保问题答案');
            registerText.innerText = passwordKey;
            inputUsername.style.display = "none";
            inputPasswordValue.style.display = "block";
            backendPasswordValue = passwordValue;
            backendPassword = password;
            retrieveBtn.disabled = false;
        } else {
            showPopup('找回失败，没有此用户');
            retrieveBtn.disabled = false;
        }
        ws.close();
    };
});

// retrieveSubBtn.addEventListener('click', (e) => {
//     if (inputPasswordValue.value === backendPasswordValue) {
//         showPopup(`找回成功，您的密码是：${backendPassword}`)
//     } else {
//         showPopup('找回失败，回答错误！')
//     }
// });

inputPasswordValue.addEventListener('blur', () => {
    if (inputPasswordValue.value === backendPasswordValue) {
        showPopup(`找回成功，您的密码是：${backendPassword}`)
    } else {
        showPopup('找回失败，回答错误！')
    }
});