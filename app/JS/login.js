// 显示登录盒子，隐藏注册盒子
const signInBox = document.getElementById("sign-in-box");
signInBox.style.display = "block";
const registerBox = document.getElementById("register-box");
registerBox.style.display = "none";

// 正则表达式
const UnameRegex = /^[a-zA-Z0-9]{1,6}$/;
const PasswordRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{9,11}$/;
const TextRegex = /^[\u4e00-\u9fa5a-zA-Z0-9\s]{1,10}$/;

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
    }
}
//关闭弹窗按钮
closeBtn.addEventListener('click', () => {
    popup.classList.remove('showing');
    popup.classList.add('hiding');
});

// 注册链接点击事件
document.getElementById("register-link").addEventListener("click", () => {
    document.getElementById("sign-in-box").style.display = "none";
    document.getElementById("register-box").style.display = "block";
});

// 登录链接点击事件
document.getElementById("sign-in-link").addEventListener("click", () => {
    document.getElementById("sign-in-box").style.display = "block";
    document.getElementById("register-box").style.display = "none";
});

// 登录业务
document.querySelector(".sign-in-btn").addEventListener("click", (e) => {
    e.preventDefault();
    // 获取表单的值
    const signInUname = document.querySelector(".sign-in-box input[name='username']").value;
    const signInPassword = document.querySelector(".sign-in-box input[name='password']").value;

    // 检查是否符合正则表达式
    const UnameFlag = UnameRegex.test(signInUname);
    const PasswordFlag = PasswordRegex.test(signInPassword);

    if (UnameFlag && PasswordFlag) {
        // 禁用按钮
        e.target.disabled = true;

        // 创建 WebSocket 连接
        const ws = new WebSocket('ws://localhost:8769');

        // 连接建立后发送用户登录数据
        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'login',
                credentials: {
                    username: signInUname,
                    password: signInPassword,
                }
            }));
            console.log('数据已发送');
        };

        // 接收后端响应
        ws.onmessage = (event) => {
            const { Back } = JSON.parse(event.data);
            if (Back === true) {
                // 登录成功后清空表单
                document.querySelector(".sign-in-box input[name='username']").value = "";
                document.querySelector(".sign-in-box input[name='password']").value = "";
                //将用户账户密码存储到本地存储
                const userData = {
                    username: signInUname,
                    password: signInPassword,
                };
                localStorage.setItem("userData", JSON.stringify(userData));
                ws.close();
                showPopup("登录成功！");
                // 登录成功后跳转到其他页面
                setTimeout(() => {
                    location.href = "./text.html";
                }, 1500);
            } else {
                showPopup("账号或密码错误！")
                // 可以在这里重新启用按钮，以便用户可以再次尝试
                e.target.disabled = false;
            }
        };

        // 可以在这里处理 WebSocket 的关闭事件
        ws.onclose = () => {
            console.log('WebSocket连接已关闭');
        };

        // 可以在这里处理 WebSocket 的错误事件
        ws.onerror = (error) => {
            console.error('WebSocket发生错误:', error);
            showPopup("连接失败，请检查服务器状态");
            e.target.disabled = false; // 重新启用按钮
        };
    } else {
        showPopup("登录失败，请检查输入是否符合要求");
    }
});
// 注册业务
document.querySelector(".register-btn").addEventListener("click", (e) => {
    e.preventDefault();
    // 获取表单的值
    const registerUname = document.querySelector(".register-box input[name='username']").value;
    const registerPassword = document.querySelector(".register-box input[name='password']").value;
    const registerHint = document.querySelector(".register-box input[name='hint']").value;
    const registerAnswer = document.querySelector(".register-box input[name='answer']").value;
    const registerCheckbox = document.querySelector(".register-box input[name='checkbox']").checked;

    // 检查是否符合正则表达式
    const UnameFlag = UnameRegex.test(registerUname);
    const PasswordFlag = PasswordRegex.test(registerPassword);
    const HintFlag = TextRegex.test(registerHint);
    const AnswerFlag = TextRegex.test(registerAnswer);

    if (!registerCheckbox) {
        showPopup("请同意用户协议");
        return;
    }

    if (UnameFlag && PasswordFlag && HintFlag && AnswerFlag) {
        //禁用按钮
        e.target.disabled = true;

        // 创建 WebSocket 连接
        const ws = new WebSocket('ws://localhost:8769');
        // 连接建立后发送用户注册数据
        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'register',
                credentials: {
                    username: registerUname,
                    password: registerPassword,
                    passwordKey: registerHint,
                    passwordValue: registerAnswer
                }
            }));
            console.log('数据已发送');
        };

        // 接收后端响应
        ws.onmessage = (event) => {
            e.target.disabled = false; // 重新启用按钮
            const { Back } = JSON.parse(event.data);
            if (Back === true) {
                showPopup("注册成功")
                //注册成功后清空表单
                document.querySelector(".register-box input[name='username']").value = "";
                document.querySelector(".register-box input[name='password']").value = "";
                document.querySelector(".register-box input[name='hint']").value = "";
                document.querySelector(".register-box input[name='answer']").value = "";
                ws.close(); // 确保 WebSocket 连接关闭
                // 注册成功后跳转到登录页面
                document.getElementById("sign-in-box").style.display = "block";
                document.getElementById("register-box").style.display = "none";
            } else {
                showPopup("注册失败，已有账户")
            }
            ws.close();
        };
    } else {
        showPopup("注册失败，请检查输入是否符合要求")
    }

});