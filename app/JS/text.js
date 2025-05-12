// 保持原有的脚本部分不变 
let a = 0, b = 0, c = 0, d = 0, e = 0, f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
let level = 46
let correct_count = 0
let wrong_count = 0
let count = [a, b, c, d, e, f, g, h, i, j, k, l, m, n]
let flag = ['Right', 'Left', 'Up', 'Down']
let size = ["730px", "580px", "460px", "360px", "290px", "230px", "180px", "150px", "120px", "90px", "70px", "60px", "50px", "40px"]
current_size_index = 6
width = size[current_size_index]
// console.log(count)
let randomIndex = '-1'

//弹窗的
// 声明一个变量并赋值
var pageTitle = `您的视力值为 ${level / 10}`;

// 使用变量设置 h1 标签的内容
document.getElementById("pageTitle").innerText = pageTitle;

var p = '您已完成视力检测！感谢您的使用！'
// 使用变量设置 h2 标签的内容
document.getElementById("p").innerText = p;
var experience = 0
var image1Path = './picture/eUp.jpg'

let dataFromFrontend = ""; // 全局变量用于存储前端发送的数据
// 模式选择
document.getElementById("leftHand").addEventListener("click", function () {
    const socket = new WebSocket("ws://localhost:8767");
    socket.onopen = function () {
        console.log("已连接");
        const data = "1";
        dataFromFrontend = data; // 将数据存储在全局变量中

        // 在接收到终端响应后再刷新页面
        socket.onmessage = function (event) {
            // 处理终端响应
            console.log("收到终端响应:", event.data);
            location.reload(); // 刷新页面
        };

        socket.send(data);
    };
});

document.getElementById("rightHand").addEventListener("click", function () {
    const socket = new WebSocket("ws://localhost:8767");
    socket.onopen = function () {
        //发送参数给终端
        console.log("已连接");
        const data = "2";
        dataFromFrontend = data; // 将数据存储在全局变量中
        // 在接收到终端响应后再刷新页面
        socket.onmessage = function (event) {
            // 处理终端响应
            console.log("收到终端响应:", event.data);
            location.reload(); // 刷新页面
        };

        socket.send(data);
    };
});
document.getElementById("speak").addEventListener("click", function () {
    const socket = new WebSocket("ws://localhost:8767");
    socket.onopen = function () {
        //发送参数给终端
        console.log("已连接");
        const data = "3";
        dataFromFrontend = data; // 将数据存储在全局变量中
        // 在接收到终端响应后再刷新页面
        socket.onmessage = function (event) {
            // 处理终端响应
            console.log("收到终端响应:", event.data);
            location.reload(); // 刷新页面
        };

        socket.send(data);
    };
});

document.getElementById("head").addEventListener("click", function () {
    const socket = new WebSocket("ws://localhost:8767");
    socket.onopen = function () {
        //发送参数给终端
        console.log("已连接");
        const data = "5";
        dataFromFrontend = data; // 将数据存储在全局变量中
        // 在接收到终端响应后再刷新页面
        socket.onmessage = function (event) {
            // 处理终端响应
            console.log("收到终端响应:", event.data);
            location.reload(); // 刷新页面
        };
        socket.send(data);
    };
});
document.getElementById("teach").addEventListener("click", function () {
    const socket = new WebSocket("ws://localhost:8767");
    socket.onopen = function () {
        //发送参数给终端
        console.log("已连接");
        const data = "4";
        dataFromFrontend = data; // 将数据存储在全局变量中
        // 在接收到终端响应后再刷新页面
        socket.onmessage = function (event) {
            // 处理终端响应
            console.log("收到终端响应:", event.data);
            location.reload(); // 刷新页面
        };

        socket.send(data);
    };
});

//历史数据查询---获取图片数据
function getHistory(picture) {
    // 创建 WebSocket 连接
    const username = JSON.parse(localStorage.getItem('userData')).username;
    const wsGetH = new WebSocket('ws://localhost:8770');

    // 连接建立后发送用户数据
    wsGetH.onopen = () => {
        wsGetH.send(JSON.stringify({
            action: 'getHistory',
            username: username,
        }));
        console.log('获取历史数据请求数据已发送：,', username);
    };

    // 接收后端响应
    wsGetH.onmessage = function (event) {
        const response = JSON.parse(event.data);
        console.log("接收到的数据:", response.data);  // 打印接收到的数据
        if (response.Back === '1') {
            // 显示图片
            // const picture = document.getElementById('vision-chart');
            picture.src = 'data:image/jpeg;base64,' + response.imgData;
            picture.style.display = 'block';
        } else {
            // 显示错误信息
            const errorMessage = document.getElementById('error-text');
            errorMessage.innerHTML = '未获取到数据，请稍后再试。';
            picture.style.display = 'none';
            errorMessage.style.display = 'block';
        }
    };

    // 连接异常处理
    wsGetH.onerror = function (error) {
        console.error("连接出错:", error);
        const errorMessage = document.getElementById('error-text');
        const visionChart = document.getElementById('vision-chart');
        errorMessage.innerHTML = '连接出错，请检查网络或稍后再试。';
        visionChart.style.display = 'none';
        errorMessage.style.display = 'block';
    };
}

//给历史数据按钮绑定事件
document.getElementById("getHistory").addEventListener("click", function () {
    // 选择外层容器
    const historyModal = document.querySelector('.history-modal');
    const visionPicture = document.querySelector('.vision-chart');
    getHistory(visionPicture);
    historyModal.style.display = 'block';
    // 使用唯一 ID 选择确认按钮
    historyModal.querySelector("button").addEventListener('click', () => {
        historyModal.style.display = 'none';
    });
});

// 结束弹窗按钮
document.getElementById("done-yes").addEventListener("click", function () {
    //刷新页面（即也清空了之前的数据）
    location.reload();
})
document.getElementById("done-break").addEventListener("click", function () {
    //跳转到登录页面
    location.href = "./login.html";
})

//网页弹窗
function set(a) {
    alert(a)
}

// 获取按钮元素
const startButton = document.getElementById("start");
const breakButton = document.getElementById("break");

// 初始状态下禁用结束按钮
breakButton.disabled = true;
breakButton.style.opacity = "0.5";
breakButton.style.cursor = "not-allowed";

// 开始测试按钮点击事件
startButton.addEventListener("click", function () {
    //颜色变化
    const picture = document.querySelector('.picture');
    picture.classList.add("white-box");
    console.log(this.classList);
    // 禁用开始按钮
    startButton.disabled = true;
    startButton.style.opacity = "0.5";
    startButton.style.cursor = "not-allowed";

    // 启用结束按钮
    breakButton.disabled = false;
    breakButton.style.opacity = "1";
    breakButton.style.cursor = "pointer";

    // 执行测试代码
    console.log("开始执行测试...");
    // 这里可以添加你的测试逻辑
});


// 结束测试按钮点击事件
breakButton.addEventListener("click", function () {
    if (this.disabled) return; // 如果按钮被禁用，不执行任何操作

    // 显示模态框
    var modal = document.getElementById("myModal");
    modal.style.display = "block";

    // 修改变量的值
    pageTitle = "您已提前结束！期待你的下一次使用！";
    document.getElementById("pageTitle").innerText = pageTitle;

    p = "您未完成视力检测哦！";
    document.getElementById("p").innerText = p;

    // 创建 WebSocket 连接
    const resPicture = document.querySelector('.resPicture');
    // 禁用结束按钮
    breakButton.disabled = true;
    breakButton.style.opacity = "0.5";
    breakButton.style.cursor = "not-allowed";

    // 重新启用开始按钮
    startButton.disabled = false;
    startButton.style.opacity = "1";
    startButton.style.cursor = "pointer";
});

// 添加点击事件处理程序 - 保留这部分，但使用上面定义的变量
startButton.addEventListener("click", function () {
    // 当按钮被点击时调用 executeMyCode 函数
    executeMyCode();
});

// 将 JavaScript 代码包装在一个函数中，以便在点击按钮时调用

const popup = document.querySelector('#popup');
const closeBtn = document.querySelector('#closePopupBtn');
const modeButtons = document.querySelector('.mode-buttons');

modeButtons.addEventListener('click', (e) => {
    const targetBtn = e.target.closest('.triggerBtn');
    if (!targetBtn) return;

    const modeMap = {
        teach: '示教',
        rightHand: '右手',
        leftHand: '左手',
        speak: '语音',
        head: '头部',
        colourBN: '色盲'
    };

    const mode = modeMap[targetBtn.id];
    if (mode) {
        document.getElementById('text').textContent = `已切换至【${mode}】模式`;
        popup.classList.add('showing');
        popup.classList.remove('hiding');

        let timerStarted = false;
        if (!timerStarted) {
            setTimeout(() => {
                popup.classList.remove('showing');
                popup.classList.add('hiding');
                timerStarted = false;
            }, 2000);
            timerStarted = true;
        }
    }
});

closeBtn.addEventListener('click', () => {
    popup.classList.remove('showing');
    popup.classList.add('hiding');
});

function executeMyCode() {
    console.log("开始执行...");
    if ((dataFromFrontend === "1") || (dataFromFrontend === "2") || (dataFromFrontend === "5")) {

        console.log("检测模式");

        const images = [
            { path: './picture/eUp.jpg', index: 0 },
            { path: './picture/eDown.jpg', index: 1 },
            { path: './picture/eLeft.jpg', index: 2 },
            { path: './picture/eRight.jpg', index: 3 },
        ];

        const images1 = [
            { path: './picture/true.png', index: 0 },
            { path: './picture/false.png', index: 1 }
        ]
        // 上一张图片的索引
        let lastIndex = '-1';
        // 显示图片的函数
        function showImage() {
            // 生成随机索引，确保与上一张不同
            // let randomIndex;
            do {
                randomIndex = Math.floor(Math.random() * images.length);
            } while (randomIndex === lastIndex);
            console.log(randomIndex)
            // 更新上一张图片的索引
            lastIndex = randomIndex;

            // 获取当前应该显示的图片路径
            const imagePath = images[randomIndex].path;
            // 在页面中显示图片，这里假设有一个名为 'image-container' 的 div 用于显示图片
            document.getElementById('image-container').src = imagePath;
            // 在页面中显示图片，这里假设有一个名为 'image-container' 的 div 用于显示图片
            const imageElement = document.getElementById('image-container');
        }
        // 定时切换图片
        // setInterval(showImage, 8000);
        // 初始化显示第一张图片,调用函数
        showImage();
        // 获取图片元素
        var imgElement = document.getElementById("image-container");

        // 修改图片大小
        imgElement.style.width = `${width}`;
        imgElement.style.height = `${width}`;

        const socket = new WebSocket('ws://localhost:8765');

        // 监听来自服务器的消息
        socket.addEventListener('message', function (event) {
            console.log('value:', event.data);
            const value = event.data;
            if (value != "None") {
                if (value === String(randomIndex)) {
                    console.log("yes");
                    correct_count += 1;
                    document.getElementById('image-container').src = "./picture/true.png";
                    setTimeout(() => { showImage(); }, 500); // 0.5秒后重新显示图片
                }
                else if (value != String(randomIndex)) {
                    console.log("No");
                    wrong_count += 1;
                    document.getElementById('image-container').src = "./picture/false.png";
                    setTimeout(() => { showImage(); }, 500);
                }

                if ((correct_count >= 2) && (0 < current_size_index && current_size_index < 13)) {
                    level += 1
                    // 修改变量的值
                    level1 = `level:${level / 10}`;
                    // 更新 h1 标签的内容，显示新的标题
                    document.getElementById("level").innerText = level1;
                    // 修改变量的值
                    pageTitle = `您的视力值为${level / 10}`;
                    // 更新 h1 标签的内容，显示新的标题
                    document.getElementById("pageTitle").innerText = pageTitle;
                    current_size_index += 1
                    width = size[current_size_index]
                    console.log("width", width)
                    console.log('current_size_index', current_size_index)
                    console.log("count[current_size_index]", count[current_size_index])
                    // 获取图片元素
                    var imgElement = document.getElementById("image-container");
                    // 修改图片大小
                    imgElement.style.width = `${width}`;
                    imgElement.style.height = `${width}`;
                    correct_count = 0
                    count[current_size_index] += 1//对了才+1
                    if (count[current_size_index] >= 2) {
                        level -= 1
                        // 修改变量的值
                        level1 = `视力值:${level / 10}`;
                        // 更新 h1 标签的内容，显示新的标题
                        document.getElementById("level").innerText = level1;
                        // 修改变量的值
                        pageTitle = `您的视力值为${level / 10}`;
                        // 更新 h1 标签的内容，显示新的标题
                        document.getElementById("pageTitle").innerText = pageTitle;
                    }

                }
                if ((wrong_count >= 2) && (current_size_index > 0)) {
                    level -= 1
                    level1 = `视力值:${level / 10}`;

                    // 更新 h1 标签的内容，显示新的标题
                    document.getElementById("level").innerText = level1;
                    current_size_index -= 1
                    width = size[current_size_index]
                    console.log("width", width)
                    console.log('current_size_index', current_size_index)
                    console.log("count[current_size_index]", count[current_size_index])
                    // 获取图片元素
                    var imgElement = document.getElementById("image-container");

                    // 修改图片大小
                    imgElement.style.width = `${width}`;
                    imgElement.style.height = `${width}`;
                    wrong_count = 0
                }
            }



            var modal = document.getElementById("myModal");
            var span = document.getElementsByClassName("modal-buttons")[0];

            var btn_break = document.getElementById("break");

            btn_break.onclick = function () {
                modal.style.display = "block";
                pageTitle = "您已提前结束！期待你的下一次使用！";
                // pageTitle="您的视力值为[4.7]"
                // 更新 h1 标签的内容，显示新的标题
                document.getElementById("pageTitle").innerText = pageTitle;

                p = "您未完成视力检测哦！";
                document.getElementById("p").innerText = p;
            }

            //显示level
            if ((current_size_index == 13 && correct_count == 2) || (current_size_index == 0 && correct_count == 2) || (count[current_size_index] == 2)) {
                console.log("break")

                //结束测试---发送视力数据
                //获取本地userData里面的username
                const username = JSON.parse(localStorage.getItem('userData')).username;
                const data = JSON.stringify({
                    action: 'submitLevel',
                    username: username,
                    level: level / 10
                });

                const ws = new WebSocket('ws://localhost:8770');
                ws.onopen = function () {
                    ws.send(data);
                    console.log('Level 历史数据查询请求已发送:', data);
                    const resPicture = document.querySelector('.resPicture');
                    const H2 = document.getElementById("pageTitle");
                    resPicture.style.height = "325px";
                    H2.style.fontSize = "30px";
                    getHistory(resPicture);
                };
                ws.onclose = function () {
                    console.log('WebSocket连接已关闭');
                };

                //显示
                modal.style.display = "block";
                // 定义关闭模态框的函数
                function closeModal() {
                    modal.style.display = "none";
                    //刷新页面（即也清空了之前的数据），关闭同时刷新
                    location.reload();
                }
                // 关闭按钮点击事件
                span.addEventListener('click', closeModal);
                // 当用户点击模态框外部时，关闭模态框
                window.onclick = function (event) {
                    if (event.target == modal) {
                        closeModal();
                    }
                }
            }
        });

    }

    if (dataFromFrontend === "3") {

        console.log("执行3语音模式");
        const videoContainer = document.querySelector("#video_container");
        videoContainer.innerHTML = '';
        // 存储图片信息的数组
        const images = [
            { path: './picture/eUp.jpg', index: 0 },
            { path: './picture/eDown.jpg', index: 1 },
            { path: './picture/eLeft.jpg', index: 2 },
            { path: './picture/eRight.jpg', index: 3 },
        ];

        const images1 = [
            { path: './picture/true.png', index: 0 },
            { path: './picture/false.png', index: 1 }
        ]

        let lastIndex = '-1';

        function showImage() {
            // 生成随机索引，确保与上一张不同
            // let randomIndex;
            do {
                randomIndex = Math.floor(Math.random() * images.length);
            } while (randomIndex === lastIndex);
            console.log(randomIndex)

            lastIndex = randomIndex;
            const imagePath = images[randomIndex].path;
            document.getElementById('image-container').src = imagePath;
            const imageElement = document.getElementById('image-container');
        }

        showImage();
        var imgElement = document.getElementById("image-container");

        imgElement.style.width = `${width}`;
        imgElement.style.height = `${width}`;

        const socket = new WebSocket('ws://localhost:8768');

        socket.addEventListener('message', function (event) {
            console.log('value:', event.data);
            let value = event.data
            if (value != "None") {
                if (value === String(randomIndex)) {
                    console.log("yes");
                    correct_count += 1;
                    document.getElementById('image-container').src = "./picture/true.png";
                    setTimeout(() => { showImage(); }, 500);

                }
                else if (value != String(randomIndex)) {
                    console.log("No");
                    wrong_count += 1;
                    document.getElementById('image-container').src = "./picture/false.png";
                    setTimeout(() => { showImage(); }, 500);
                }

                if ((correct_count >= 2) && (0 < current_size_index && current_size_index < 13)) {
                    level += 1
                    level1 = `视力值:${level / 10}`;
                    document.getElementById("level").innerText = level1;
                    pageTitle = `您的视力值为${level / 10}`;
                    document.getElementById("pageTitle").innerText = pageTitle;
                    current_size_index += 1
                    width = size[current_size_index]
                    console.log("width", width)
                    console.log('current_size_index', current_size_index)
                    console.log("count[current_size_index]", count[current_size_index])
                    var imgElement = document.getElementById("image-container");
                    imgElement.style.width = `${width}`;
                    imgElement.style.height = `${width}`;
                    correct_count = 0
                    count[current_size_index] += 1
                    if (count[current_size_index] >= 2) {
                        level -= 1
                        level1 = `视力值:${level / 10}`;
                        document.getElementById("level").innerText = level1;
                        pageTitle = `您的视力值为${level / 10}`;
                        document.getElementById("pageTitle").innerText = pageTitle;
                    }

                }
                if ((wrong_count >= 2) && (current_size_index > 0)) {
                    level -= 1
                    level1 = `视力值:${level / 10}`;

                    document.getElementById("level").innerText = level1;
                    current_size_index -= 1
                    width = size[current_size_index]
                    console.log("width", width)
                    console.log('current_size_index', current_size_index)
                    console.log("count[current_size_index]", count[current_size_index])
                    var imgElement = document.getElementById("image-container");

                    imgElement.style.width = `${width}`;
                    imgElement.style.height = `${width}`;
                    wrong_count = 0
                }
            }

            var modal = document.getElementById("myModal");
            var span = document.getElementsByClassName("close")[0];

            var btn_break = document.getElementById("break");

            btn_break.onclick = function () {
                modal.style.display = "block";
                pageTitle = "您已提前结束！期待你的下一次使用！";
                document.getElementById("pageTitle").innerText = pageTitle;

                p = "您未完成视力检测哦！";
                document.getElementById("p").innerText = p;
            }

            if ((current_size_index == 13 && correct_count == 2) || (current_size_index == 0 && correct_count == 2) || (count[current_size_index] == 2)) {
                console.log("break")
                const username = JSON.parse(localStorage.getItem('userData')).username;
                const data = JSON.stringify({
                    action: 'submitLevel',
                    username: username,
                    level: level / 10
                });

                const ws = new WebSocket('ws://localhost:8770');
                ws.onopen = function () {
                    ws.send(data);
                    console.log('Level 历史数据查询请求已发送:', data);
                    const resPicture = document.querySelector('.resPicture');
                    const H2 = document.getElementById("pageTitle");
                    resPicture.style.height = "325px";
                    H2.style.fontSize = "30px";
                    getHistory(resPicture);
                };
                ws.onclose = function () {
                    console.log('WebSocket连接已关闭');
                };

                modal.style.display = "block";
                function closeModal() {
                    modal.style.display = "none";
                    location.reload();
                }

                span.onclick = closeModal;
                window.onclick = function (event) {
                    if (event.target == modal) {
                        closeModal();
                    }
                }

            }
        });
    }

    if (dataFromFrontend === "4") {
        var modal = document.getElementById("myModal");
        var span = document.getElementsByClassName("close")[0];
        const speak = ["如果你想表示向上，请将你的右手向正上方伸直",
            "如果你想表示向下，请将你的右手向下伸直，稍稍远离身体",
            "如果你想表示向左，请将你的右手向左水平伸直",
            "如果你想表示向右，请将你的右手向右水平伸直",
        ];
        let speakIndex = 0;
        let experience = 0;

        console.log("执行4示教模式");

        const socket = new WebSocket('ws://localhost:8765');

        const images = [
            { path: './picture/eUp.jpg', index: 0 },
            { path: './picture/eDown.jpg', index: 1 },
            { path: './picture/eLeft.jpg', index: 2 },
            { path: './picture/eRight.jpg', index: 3 },
        ];

        let currentIndex = 0;
        document.getElementById('image-container').src = images[currentIndex].path;
        if ('speechSynthesis' in window) {
            const synthesis = window.speechSynthesis;
            let textToSpeak = speak[speakIndex];
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = 'zh-CN';

            synthesis.speak(utterance);
        } else {
            console.error('抱歉，您的浏览器不支持语音合成功能。');
        }

        socket.addEventListener('message', function (event) {
            console.log('value:', event.data);
            const value = event.data;
            if (value === String(currentIndex)) {

                if (currentIndex < 3) {
                    currentIndex += 1;
                    speakIndex += 1;
                }
                experience += 1;
                let imagePath = images[currentIndex].path;
                document.getElementById('image-container').src = imagePath;

                if ('speechSynthesis' in window) {

                    const synthesis = window.speechSynthesis;
                    let textToSpeak = speak[speakIndex];
                    if (experience == 4) {
                        textToSpeak = "示教结束";
                    }

                    const utterance = new SpeechSynthesisUtterance(textToSpeak);
                    utterance.lang = 'zh-CN';

                    synthesis.speak(utterance);


                } else {
                    console.error('抱歉，您的浏览器不支持语音合成功能。');
                }


                if (experience === 4) {
                    modal.style.display = "block";
                    pageTitle = "您已掌握手势检测模式的使用方法！现在，让我们一开始检测视力吧！";
                    document.getElementById("pageTitle").innerText = pageTitle;
                    p = "您已完成示教！";
                    document.getElementById("p").innerText = p;
                }
            }
        });

        function displayModal() {
            modal.style.display = "block";


            pageTitle = "您已提前结束！期待你的下一次使用！";

            document.getElementById("pageTitle").innerText = pageTitle;


            p = "您未完成是视力检测哦！";
            document.getElementById("p").innerText = p;
            function closeModal() {
                modal.style.display = "none";
                location.reload();
            }

            span.onclick = closeModal;
            window.onclick = function (event) {
                if (event.target == modal) {
                    closeModal();
                }
            }
        }
    }
}





const videoContainer = document.getElementById('video');
const websocket = new WebSocket('ws://localhost:8766');
let intervalId;

websocket.onmessage = function (event) {
    const img = document.createElement('img');
    img.src = 'data:image/jpeg;base64,' + event.data;
    videoContainer.innerHTML = '';
    videoContainer.appendChild(img);

};

