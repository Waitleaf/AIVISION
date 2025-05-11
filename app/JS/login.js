
const signInBox = document.getElementById("sign-in-box");
signInBox.style.display = "block";
const registerBox = document.getElementById("register-box");
registerBox.style.display = "none";

const UnameRegex = /^[a-zA-Z0-9]{1, 6}$/;
const PasswordRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{9, 11}$/;
const TextRegex = /^[\u4e00-\u9fa5a-zA-Z0-9\s]{1, 10}$/;

document.getElementById("register-link").addEventListener("click", () => {
    document.getElementById("sign-in-box").style.display = "none";
    document.getElementById("register-box").style.display = "block";
});

document.getElementById("sign-in-link").addEventListener("click", () => {
    document.getElementById("sign-in-box").style.display = "block";
    document.getElementById("register-box").style.display = "none";
});

document.querySelector(".sign-in-btn").addEventListener("click", (e) => {
    e.preventDefault();
    const signInUname = document.querySelector(".sign-in-box input[name='username']").value;
    const signInPassword = document.querySelector(".sign-in-box input[name='password']").value;

    const UnameFlag = UnameRegex.test(signInUname);
    const PasswordFlag = PasswordRegex.test(signInPassword);

    if (UnameFlag && PasswordFlag) {
        e.target.disabled = true;

        const ws = new WebSocket('ws://localhost:8769');

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

        ws.onmessage = (event) => {
            const { Back } = JSON.parse(event.data);
            if (Back === true) {
                document.querySelector(".sign-in-box input[name='username']").value = "";
                document.querySelector(".sign-in-box input[name='password']").value = "";
                const userData = {
                    username: signInUname,
                    password: signInPassword,
                };
                localStorage.setItem("userData", JSON.stringify(userData));
                ws.close();
                location.href = "./text.html";
            } else {
                alert("账号或密码错误！");
                e.target.disabled = false;
            }
        };

        ws.onclose = () => {
            console.log('WebSocket连接已关闭');
        };

        ws.onerror = (error) => {
            console.error('WebSocket发生错误:', error);
            alert("连接失败，请检查服务器状态");
            e.target.disabled = false;
        };
    } else {
        alert("登录失败，请检查输入是否符合要求");
    }
});
document.querySelector(".register-btn").addEventListener("click", (e) => {
    e.preventDefault();
    const registerUname = document.querySelector(".register-box input[name='username']").value;
    const registerPassword = document.querySelector(".register-box input[name='password']").value;
    const registerHint = document.querySelector(".register-box input[name='hint']").value;
    const registerAnswer = document.querySelector(".register-box input[name='answer']").value;
    const registerCheckbox = document.querySelector(".register-box input[name='checkbox']").checked;

    const UnameFlag = UnameRegex.test(registerUname);
    const PasswordFlag = PasswordRegex.test(registerPassword);
    const HintFlag = TextRegex.test(registerHint);
    const AnswerFlag = TextRegex.test(registerAnswer);

    if (!registerCheckbox) {
        alert("请同意用户协议");
        return;
    }

    if (UnameFlag && PasswordFlag && HintFlag && AnswerFlag) {
        e.target.disabled = true;

        const ws = new WebSocket('ws://localhost:8769');
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

        ws.onmessage = (event) => {
            e.target.disabled = false;
            const { Back } = JSON.parse(event.data);
            if (Back === true) {
                alert("注册成功");
                document.querySelector(".register-box input[name='username']").value = "";
                document.querySelector(".register-box input[name='password']").value = "";
                document.querySelector(".register-box input[name='hint']").value = "";
                document.querySelector(".register-box input[name='answer']").value = "";
                ws.close();
                document.getElementById("sign-in-box").style.display = "block";
                document.getElementById("register-box").style.display = "none";
            } else {
                alert("注册失败,已有账户");
            }
            ws.close();
        };
    } else {
        alert("注册失败，请检查输入是否符合要求")
    }

});
