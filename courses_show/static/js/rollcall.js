var colors = ["#B8D430", "#3AB745", "#029990", "#3501CB","#2E2C75", "#673A7E", "#CC0071", "#F80120","#F35B20", "#FB9A00", "#FFCC00", "#FEF200"];
var names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
var callTimes = [];
var absentTimes = [];
var callInClass = [];
var rollIndex = null;

var totalPieces = names.length * 20;
var originPieces = names.length * 20;
var names_num = names.length;
var startAngle = 0;
var arc = 2 * Math.PI;
var spinTimeout = null;
var spinArcStart = 10;
var spinTime = 0;
var spinTimeTotal = 0;
var ctx;
var MIME_TYPE = "text/plain";

function reset() {
    for (var i in callInClass) {
        callInClass[i] = 0;
    }
    totalPieces = originPieces;
    draw();
}

function absent() {
    if (rollIndex) {
        absentTimes[rollIndex] += 1;
        totalPieces -= 4 * (absentTimes[rollIndex] - 1);
    }
    draw();
}

function initDraw() {
    for (var i = 0; i < 26; i++) {
        callTimes.push(0);
        callInClass.push(0);
        absentTimes.push(0);
    }
    draw();
}

function updateData(content) {

    var lines = content.split(/\r?\n/);
    var divs = new Array();
    names = [];
    callTimes = [];
    absentTimes = [];
    totalPieces = 0;

    for (var i in lines) {
        var line = lines[i],
            fields = line.split(','),
            callTime = 0,
            absentTime = 0;

        if (line == '' || line == ' ') continue;

        if (fields.length >= 2) {
            callTime = parseInt(fields[1]);
            if (fields.length == 3) {
                absentTime = parseInt(fields[2]);
            }
        }
        names.push(fields[0]);
        callTimes.push(callTime);
        absentTimes.push(absentTime);
        callInClass.push(0);
        totalPieces += 20 - 2 * callTime + 4 * absentTime;
    }

    originPieces = totalPieces;

    names_num = names.length;
    arc = 2 * Math.PI;
    draw();
}

function draw() {
  //console.log(callTimes);
  //console.log(totalPieces);
    drawRouletteWheel();
}

function drawRouletteWheel() {
    var canvas = document.getElementById("wheelcanvas");
    if (canvas.getContext) {
        var outsideRadius = 300;
        var textRadius = 250;
        var insideRadius = 200;
        var angle = startAngle;
        ctx = canvas.getContext("2d");
        ctx.clearRect(0,0,800,800);
        ctx.strokeStyle = "black";
        ctx.lineWidth = 2;
        ctx.font = 'bold 12px sans-serif';
        //console.log(names_num);
        for(var i = 0; i < names_num; i++) {
            if (callInClass[i]) {
                continue;
            }

            arc = 2 * Math.PI * (20 - 2 * callTimes[i] + 4 * absentTimes[i]) / totalPieces;

            ctx.fillStyle = colors[i];
            ctx.beginPath();
            ctx.arc(350, 350, outsideRadius, angle, angle + arc, false);
            ctx.arc(350, 350, insideRadius, angle + arc, angle, true);
            ctx.stroke();
            ctx.fill();
            ctx.save();
            ctx.shadowOffsetX = -1;
            ctx.shadowOffsetY = -1;
            ctx.shadowBlur    = 0;
            ctx.shadowColor   = "rgb(220,220,220)";
            ctx.fillStyle = "black";
            ctx.translate(350 + Math.cos(angle + arc / 2) * textRadius, 350 + Math.sin(angle + arc / 2) * textRadius);
            ctx.rotate(angle + arc / 2 + Math.PI / 2);
            var text = names[i];
            ctx.fillText(text, -ctx.measureText(text).width / 2, 0);
            ctx.restore();

            angle += arc;
        }
        //Arrow
        ctx.fillStyle = "black";
        ctx.beginPath();
        ctx.moveTo(350 - 4, 350 - (outsideRadius + 5));
        ctx.lineTo(350 + 4, 350 - (outsideRadius + 5));
        ctx.lineTo(350 + 4, 350 - (outsideRadius - 5));
        ctx.lineTo(350 + 9, 350 - (outsideRadius - 5));
        ctx.lineTo(350 + 0, 350 - (outsideRadius - 13));
        ctx.lineTo(350 - 9, 350 - (outsideRadius - 5));
        ctx.lineTo(350 - 4, 350 - (outsideRadius - 5));
        ctx.lineTo(350 - 4, 350 - (outsideRadius + 5));
        ctx.fill();
    }
}

function spin() {
    spinAngleStart = Math.random() * 10 + 10;
    spinTime = 0;
    spinTimeTotal = Math.random() * 3 + 4 * 1000;
    rotateWheel();
}

function rotateWheel() {
    spinTime += 30;
    if(spinTime >= spinTimeTotal) {
        stopRotateWheel();
        return;
    }

    var spinAngle = spinAngleStart - easeOut(spinTime, 0, spinAngleStart, spinTimeTotal);

    startAngle += (spinAngle * Math.PI / 180);
    //console.log('final angle? in what? ' + startAngle);

    drawRouletteWheel();
    spinTimeout = setTimeout('rotateWheel()', 30);
}

function stopRotateWheel() {
    clearTimeout(spinTimeout);
    var degrees = (startAngle * 180 / Math.PI + 90) % 360,
        arrow = 360 - degrees;
    //console.log(startAngle + ' degree ' + degrees + ' arrow at ' + arrow);
    var index = 0;

    for (var i = 0; i < names.length; i++) {

        if (callInClass[i])
            continue;

        var localarc = 360 * (20 - 2 * callTimes[i] + 4 * absentTimes[i]) / totalPieces;
        //console.log(i + ' ' + localarc);

        if (arrow - localarc < 0) {
            //console.log(i);
            index = i;
            break;
        }

        arrow -= localarc;
    }

  //console.log(index);
  //console.log(callInClass[index]);
    ctx.save();
    var text = names[index];

    rollIndex = index;

    callInClass[index] = 1;
    callTimes[index] += 1;

    totalPieces -= 20 - 2 * (callTimes[index] - 1);

    ctx.font = 'bold 30px sans-serif';
    ctx.fillText(text, 350 - ctx.measureText(text).width / 2, 350 + 10);
    ctx.restore();
}

function easeOut(t, b, c, d) {
    var ts = (t/=d)*t;
    var tc = ts*t;
    return b+c*(tc + -3*ts + 3*t);
}

function save() {

    var data = "";
    for (var i = 0; i < names.length; i++) {
        data += names[i] + "," + callTimes[i] + "," + absentTimes[i] + "\n";
    }

    var bb = new Blob([data], {type: MIME_TYPE}),
    a = document.createElement('a');

    var d = new Date();
    a.download = "record-" + d.getFullYear() + '' + d.getMonth() + '' + d.getDate() + ".txt";
    a.href = window.URL.createObjectURL(bb);
    a.textContent = '点击下载';

    a.dataset.downloadurl = [MIME_TYPE, a.download, a.href].join(':');
    document.querySelectorAll("#downloadLinkWrap")[0].innerHTML = "";
    document.querySelectorAll("#downloadLinkWrap")[0].appendChild(a);

}
