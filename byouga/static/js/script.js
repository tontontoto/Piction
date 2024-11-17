const canvas = document.getElementById("mycanvas");
const context = canvas.getContext("2d");

context.rect(0,0, canvas.width, canvas.height);
context.fillStyle = "black";
context.fill();
context.beginPath();
context.moveTo(100, 100);
context.lineTo(100, 200);
context.lineWidth = 5;
context.strokeStyle = '#fff';

let mouse = {x:0, y:0};

canvas.addEventListener("mousemove", function(e) {
    mouse.x = e.pageX - this.offsetLeft;
    mouse.y = e.pageY - this.offsetTop;

    // console.log(mouse);
}, false);

canvas.addEventListener("mousedown", function(e) {
    context.beginPath();
    context.moveTo(mouse.x, mouse.y);

    canvas.addEventListener("mousemove", onPaint, false);
}, false);

canvas.addEventListener("mouseup", function() {
    canvas.removeEventListener("mousemove", onPaint, false);
})

const onPaint = function() {
    context.lineTo(mouse.x, mouse.y);
    context.stroke();
}

// 画像保存
document.getElementById("download").onclick = (event) => {
	let canvas = document.getElementById("mycanvas");

	let link = document.createElement("a");
	link.href = canvas.toDataURL("image/jpeg");
	link.download = "test.jpg";
	link.click();
}


download.addEventListener('click', () => {
    const dataURL = canvas.toDataURL('image/png'); // 画像をBase64に変換
    fetch('/save-image', {
      method: 'POST',
      body: JSON.stringify({ image: dataURL }),
      headers: {
        'Content-Type': 'application/json',
      },
                    }).then(response => {
      if (response.ok) {
        alert('Image saved successfully!');
      } else {
        alert('Failed to save image.');
      }
    });
  });