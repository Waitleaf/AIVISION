const popup = document.querySelector('#popup');
const closeBtn = document.querySelector('#closePopupBtn');
const modeButtons = document.querySelector('.mode-buttons');


closeBtn.addEventListener('click', () => {
    popup.classList.remove('showing');
    popup.classList.add('hiding');
});


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


// 结束弹窗按钮
document.getElementById("done-yes").addEventListener("click", function () {
    //刷新页面（即也清空了之前的数据）
    location.reload();
})
document.getElementById("done-break").addEventListener("click", function () {
    //跳转到登录页面
    location.href = "./login.html";
})