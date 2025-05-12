const retrieveBtn = document.querySelector('.retrieve-btn');
const inputUsername = document.querySelector('input[name="inputUsername"]');
const inputPasswordValue = document.querySelector('input[name="passwordValue"]');
const registerText = document.querySelector('.registerText');
let backendPasswordValue = '';
let backendPassword = '';

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
            alert("请输入密保问题答案");
            registerText.innerText = passwordKey;
            inputUsername.style.display = "none";
            inputPasswordValue.style.display = "block";
            backendPasswordValue = passwordValue;
            backendPassword = password;
            retrieveBtn.disabled = false;
        } else {
            alert("找回失败，没有此用户");
            retrieveBtn.disabled = false;
        }
        ws.close();
    };
});


inputPasswordValue.addEventListener('blur', () => {
    if (inputPasswordValue.value === backendPasswordValue) {
        alert("找回成功，您的密码是：" + backendPassword);
        location.reload(true);
    } else {
        alert("找回失败，回答错误！");
    }
});