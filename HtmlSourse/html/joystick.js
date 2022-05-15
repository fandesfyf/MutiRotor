var on_leftcontrol = false;
var on_rightcontrol = false;
var touchids = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
var touchLid = -1;
var touchRid = -1;
var timeId = null;
var timeId2 = null;

function getDistance(x1, y1, x2, y2) {
    return Math.sqrt(Math.pow((x1 - x2), 2) + Math.pow((y1 - y2), 2));
}

function isinArea(pos, x, y, w, h) {
    console.log(pos, x, y, w, h)
    return x <= pos[0] && pos[0] <= x + w && y <= pos[1] && pos[1] <= y + h;

}

document.oncontextmenu = function (e) {
    e.preventDefault();
};

function onEf() {//指定频率触发的函数
    //send data
    // if (!connected)
    //     return
    var scalex = subX / R;
    var scaley = (-subY + R) / (2 * R);
    t = controller.scale_cp * 2 * scaley
    r = controller.scale_cp * scalex
    t = (Math.abs(t) > controller.err * 2) ? t : 0
    r = (Math.abs(r) > controller.err) ? r : 0
    set_cur_data(t, r)
}

function onEf2() {//指定频率触发的函数
    //send data
    // if (!connected)
    //     return
    console.log("onfef2")
    var scalex = subX2 / R;
    var scaley = -subY2 / R;
    p = controller.scale_cp * scaley
    y = controller.scale_cp * scalex
    p = (Math.abs(p) > controller.err) ? p : 0
    y = (Math.abs(y) > controller.err) ? y : 0
    set_cur_data(null, null, p, y)
}

function onTouchStartL(e) {//这个是屏幕点击开始,不是按键那个
    console.log("onTouchStartL", e.touches, touchLid)
    touch_statrt = false
    if (touchLid === -1) {
        for (var i = 0; i < touchids.length; i++) {
            if (touchids[i] !== -1) {
                touchLid = i
                touch_statrt = true
                break
            }
        }
    }

    debugtext.innerText = e.touches.length.toString() + touchLid.toString() + touchRid.toString()
    t = e.touches[0]
    for (var i = 0; i < e.touches.length; i++) {
        debugtext.innerText += e.touches[i].identifier + ":".toString() + e.touches[i].clientX.toString() + "/ ".toString()
        if (e.touches[i].identifier === touchLid) {
            t = e.touches[i]
        }
        touchids[e.touches[i].identifier] = -1
    }
    if (touch_statrt)
        startHandleL(t.clientX, t.clientY);
    e.preventDefault()
}

function onTouchStartR(e) {//这个是屏幕点击开始,不是按键那个
    console.log("onTouchStartR", e.touches)
    touch_statrt = false
    if (touchRid === -1) {
        for (var i = 0; i < touchids.length; i++) {
            if (touchids[i] !== -1) {
                touchRid = i
                touch_statrt = true
                break
            }
        }
    }

    debugtext.innerText = e.touches.length.toString() + touchLid.toString() + touchRid.toString()
    t = e.touches[0]
    for (var i = 0; i < e.touches.length; i++) {
        debugtext.innerText += e.touches[i].identifier.toString() + ":".toString() + e.touches[i].clientX.toString() + "/ ".toString()
        if (e.touches[i].identifier === touchRid) {
            t = e.touches[i]
        }
        touchids[e.touches[i].identifier] = -1
    }

    if (touch_statrt)
        startHandleR(t.clientX, t.clientY);
    e.preventDefault()
}

function onMouseDownL(e) {//和上面等作用
    startHandleL(e.clientX, e.clientY);
}

function onMouseDownR(e) {//和上面等作用
    startHandleR(e.clientX, e.clientY);
}

var ontouchjoystick1 = false;
joystick1.ontouchstart = function (e) {
    ontouchjoystick1 = true
}
joystick1.onmousedown = function (e) {
    console.log("oncleic  ", e)
    ontouchjoystick1 = true
}

function startHandleL(clientX, clientY) {//摇杆按下,从onMouseMove或者onTouchStart触发
    if (!touchmode) {
        return
    }

    on_rotation = window.innerWidth < window.innerHeight;
    if (on_rotation) [clientX, clientY] = [clientY, document.body.clientHeight - clientX]
    // debugtext.innerText = clientX.toString() + " " + clientY.toString()
    console.log("onMouseDownL", clientX, clientY)
    // cx = clientX
    // cy = clientY

    if (ontouchjoystick1) {
        ontouchjoystick1 = false
        on_leftcontrol = true;
        console.log("in the area")

        if (!isinArea(Array(clientX, clientY), bg.offsetLeft, bg.offsetTop, bg.clientWidth, bg.clientHeight)) {
            if (clientX < bg.offsetLeft) clientX = bg.offsetLeft;
            else if (clientX > bg.offsetLeft + bg.clientWidth) clientX = bg.offsetLeft + bg.clientWidth;
            if (clientY < bg.offsetTop) clientY = bg.offsetTop;
            else if (clientY > bg.offsetTop + bg.clientHeight) clientY = bg.offsetTop + bg.clientHeight;
        }
        joystick1.style.left = clientX + "px";
        joystick1.style.top = clientY + "px";
        joystick1.style.display = "block";

        if (timeId)
            clearInterval(timeId);
        // subY=R;
        // console.log(subY)
        //开启每帧处理
        timeId = setInterval(onEf, 50);
    }
    // bg.style.top = joystick1.style.top = cy + "px";
    // bg.style.display = "block";

}

function startHandleR(clientX, clientY) {//摇杆按下,从onMouseMove或者onTouchStart触发
    if (!touchmode) {
        return
    }
    console.log(clientX, clientY, stage1.clientWidth)
    on_rotation = window.innerWidth < window.innerHeight;
    if (on_rotation) {
        [clientX, clientY] = [clientY, document.body.clientHeight - clientX]
    }
    clientX -= stage1.clientWidth
    // debugtext.innerText = clientX.toString() + " " + clientY.toString()

    console.log("onMouseDownR", clientX, clientY, on_rotation)
    on_rightcontrol = true;
    cx2 = clientX
    cy2 = clientY
    bg2.style.left = joystick2.style.left = cx2 + "px";
    bg2.style.top = joystick2.style.top = cy2 + "px";
    bg2.style.display = "block";
    joystick2.style.display = "block";
    if (timeId2)
        clearInterval(timeId2)
    subX2 = subY2 = 0
    //开启每帧处理
    timeId2 = setInterval(onEf2, 50);
}


function onTouchMoveL(e) {
    e.preventDefault();
    debugtext.innerText = e.touches.length.toString() + touchLid.toString() + touchRid.toString()
    t = e.touches[0]
    for (var i = 0; i < e.touches.length; i++) {
        debugtext.innerText += e.touches[i].identifier + ":".toString() + e.touches[i].clientX.toString() + "/ ".toString()
        if (e.touches[i].identifier === touchLid) {
            t = e.touches[i]
        }
    }
    if (!e.touches || !touchmode || !on_leftcontrol) return;
    console.log("onTouchMoveL", touchLid, t.clientX, t.clientY)
    moveHandleL(t.clientX, t.clientY);
}

function onMouseMoveL(e) {
    e.preventDefault();
    if (!touchmode || !on_leftcontrol) return;
    console.log("onMouseMoveL", e.clientX, e.clientY)
    moveHandleL(e.clientX, e.clientY);
}

function onTouchMoveR(e) {
    e.preventDefault();
    debugtext.innerText = e.touches.length.toString() + touchLid.toString() + touchRid.toString()
    t = e.touches[0]
    for (var i = 0; i < e.touches.length; i++) {
        debugtext.innerText += e.touches[i].identifier + ":".toString() + e.touches[i].clientX.toString() + "/ ".toString()
        if (e.touches[i].identifier === touchRid) {
            t = e.touches[i]
        }
    }
    if (!e.touches || !touchmode || !on_rightcontrol) return;
    console.log("onTouchMoveR", touchRid, t.clientX, t.clientY)
    moveHandleR(t.clientX, t.clientY);

}

function onMouseMoveR(e) {
    e.preventDefault();
    if (!touchmode || !on_rightcontrol) return;
    console.log("onMouseMoveR", e.clientX, e.clientY)
    moveHandleR(e.clientX, e.clientY);

}

function moveHandleL(clientX, clientY) {
    on_rotation = window.innerWidth < window.innerHeight;
    if (on_rotation) {
        [clientX, clientY] = [clientY, document.body.clientHeight - clientX]
    }
    temp_subX = clientX - cx;//相对位移
    temp_subY = clientY - cy;
    // var subLen = Math.sqrt(temp_subX * temp_subX + temp_subY * temp_subY);//长度
    R = bg.clientWidth / 2;
    var x;
    var y;
    if (Math.abs(temp_subX) <= R) {
        subX = temp_subX
        x = clientX
    } else {
        subX = (temp_subX > 0) ? R : -R;
        x = cx + subX
    }
    if (Math.abs(temp_subY) <= R) {
        subY = temp_subY
        y = clientY
    } else {
        subY = (temp_subY > 0) ? R : -R
        y = cy + subY
    }

    joystick1.style.left = x + "px";
    joystick1.style.top = y + "px";
}

function moveHandleR(clientX, clientY) {
    on_rotation = window.innerWidth < window.innerHeight;
    if (on_rotation) {
        [clientX, clientY] = [clientY, document.body.clientHeight - clientX]
    }
    clientX -= stage1.clientWidth
    temp_subX2 = clientX - cx2;//相对位移
    temp_subY2 = clientY - cy2;
    // var subLen = Math.sqrt(temp_subX2 * temp_subX2 + temp_subY2 * temp_subY2);//长度
    R = bg2.clientWidth / 2;
    var x;
    var y;

    // console.log(subLen,R)
    if (Math.abs(temp_subX2) <= R) {
        subX2 = temp_subX2
        x = clientX
    } else {
        subX2 = (temp_subX2 > 0) ? R : -R;
        x = cx2 + subX2
    }
    if (Math.abs(temp_subY2) <= R) {
        subY2 = temp_subY2
        y = clientY
    } else {
        subY2 = (temp_subY2 > 0) ? R : -R;
        y = cy2 + subY2
    }

    joystick2.style.left = x + "px";
    joystick2.style.top = y + "px";
}

function onEndL(e) {//触屏释放
    e.preventDefault();
    if (!touchmode) return
    console.log("onEndL", e.touches)
    var touch_end = false
    left_ids = []
    for (i = 0; i < e.touches.length; i++) {
        left_ids.push(e.touches[i].identifier)
    }

    for (var i = 0; i < touchids.length; i++) {
        if (left_ids.indexOf(i) === -1) {
            touchids[i] = 0;
            if (i === touchLid) {
                touchLid = -1;
                touch_end = true
            }
        }
    }

    if (touch_end) {
        mouseEndL(e)
    }
}

function mouseEndL(e) {
    if (!touchmode) return
    on_leftcontrol = false
    if (timeId)
        clearInterval(timeId);
    set_cur_data(null, 0)
    joystick1.style.left = cx + "px";
    // joystick1.style.top = bg.style.top = cy + "px";
    // bg.style.display = "none";
    // joystick1.style.display = "none";
}

function onEndR(e) {//触屏释放或者按键释放
    e.preventDefault();
    if (!touchmode) return
    console.log("onEndR")
    var touch_end = false
    debugtext.innerText = ""
    left_ids = []
    for (i = 0; i < e.touches.length; i++) {
        left_ids.push(e.touches[i].identifier)
    }
    for (var i = 0; i < touchids.length; i++) {
        if (left_ids.indexOf(i) === -1) {
            touchids[i] = 0
            if (i === touchRid) {
                touchRid = -1
                touch_end = true
            }
        }
    }
    debugtext.innerText += touch_end.toString() + touchLid.toString() + touchRid.toString() + left_ids.toString()
    if (touch_end) {
        mouseEndR(e)
    }
}

function mouseEndR(e) {
    if (!touchmode) return
    on_rightcontrol = false
    if (timeId2)
        clearInterval(timeId2);
    set_cur_data(null, null, 0, 0)
    joystick2.style.left = bg2.style.left = cx2 + "px";
    joystick2.style.top = bg2.style.top = cy2 + "px";
    // bg.style.display = "none";
    // joystick1.style.display = "none";
}

function setjoystickpos(v, t) {
    var scalesubx = t / controller.max_theta
    var scalesuby = v / controller.max_v
    var subx = -scalesubx * R
    var suby = -scalesuby * R
    joystick1.style.left = cx + subx + "px";
    joystick1.style.top = cy + suby + "px";
    debugtext.innerText = v.toString() + " " + t.toString() + " " + joystick1.style.left + " " + joystick1.style.top
}

function set_cur_data(t = null, r = null, p = null, y = null, d = null) {
    t = (t !== null) ? t : controller.cur_param["t"]
    r = (r !== null) ? r : controller.cur_param["r"]
    p = (p !== null) ? p : controller.cur_param["p"]
    y = (y !== null) ? y : controller.cur_param["y"]
    d = (d !== null) ? d : controller.cur_param["d"]
    // t=controller.cur_param["t"], r=controller.cur_param["r"],p=controller.cur_param["p"],y=controller.cur_param["y"],d=controller.cur_param["d"]
    // console.log("setdata",{"t": t, "r": r, "p": p, "y": y, "d": d})
    controller.cur_param = {"t": t, "r": r, "p": p, "y": y, "d": d}
    controller.send_speed()
}

stage1.addEventListener('touchstart', onTouchStartL);
stage1.addEventListener('touchmove', onTouchMoveL);
stage1.addEventListener('touchend', onEndL);
stage1.addEventListener('mousedown', onMouseDownL);
stage1.addEventListener('mousemove', onMouseMoveL);
stage1.addEventListener('mouseup', mouseEndL);
stage2.addEventListener('touchstart', onTouchStartR);
stage2.addEventListener('touchmove', onTouchMoveR);
stage2.addEventListener('touchend', onEndR);
stage2.addEventListener('mousedown', onMouseDownR);
stage2.addEventListener('mousemove', onMouseMoveR);
stage2.addEventListener('mouseup', mouseEndR);
