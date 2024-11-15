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