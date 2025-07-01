const canvas = document.getElementById("backgroundCanvas");
const ctx = canvas.getContext("2d");
let width, height;

function resizeCanvas() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();

class Ball {
  constructor() {
    this.radius = Math.random() * 10 + 5;
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    this.dx = (Math.random() - 0.5) * 2;
    this.dy = (Math.random() - 0.5) * 2;
    this.color = `hsla(${Math.random() * 360}, 100%, 70%, 0.2)`;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
  }

  update() {
    if (this.x + this.radius > width || this.x - this.radius < 0) this.dx *= -1;
    if (this.y + this.radius > height || this.y - this.radius < 0)
      this.dy *= -1;
    this.x += this.dx;
    this.y += this.dy;
    this.draw();
  }
}

const balls = Array.from({ length: 75 }, () => new Ball());

function animate() {
  ctx.clearRect(0, 0, width, height);
  balls.forEach((ball) => ball.update());
  requestAnimationFrame(animate);
}

animate();