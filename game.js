const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const tankSize = 30;
const bulletSize = 5;
const bulletSpeed = 5;

let tank1 = {
    x: 100,
    y: 100,
    width: tankSize,
    height: tankSize,
    color: 'green',
    dx: 0,
    dy: 0,
    angle: 0
};

let tank2 = {
    x: 700,
    y: 500,
    width: tankSize,
    height: tankSize,
    color: 'red',
    dx: 0,
    dy: 0,
    angle: 0
};

// 子弹数组
let bullets = [];

// 监听按键事件
document.addEventListener('keydown', (event) => {
    switch (event.key) {
        case 'w':
            tank1.dy = -3;
            break;
        case 's':
            tank1.dy = 3;
            break;
        case 'a':
            tank1.dx = -3;
            break;
        case 'd':
            tank1.dx = 3;
            break;
        case ' ':
            fireBullet(tank1);
            break;
        case 'ArrowUp':
            tank2.dy = -3;
            break;
        case 'ArrowDown':
            tank2.dy = 3;
            break;
        case 'ArrowLeft':
            tank2.dx = -3;
            break;
        case 'ArrowRight':
            tank2.dx = 3;
            break;
        case 'Enter':
            fireBullet(tank2);
            break;
    }
});

document.addEventListener('keyup', (event) => {
    if (event.key === 'w' || event.key === 's') tank1.dy = 0;
    if (event.key === 'a' || event.key === 'd') tank1.dx = 0;
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') tank2.dy = 0;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') tank2.dx = 0;
});


function fireBullet(tank) {
    bullets.push({
        x: tank.x + tank.width / 2,
        y: tank.y + tank.height / 2,
        dx: Math.cos(tank.angle) * bulletSpeed,
        dy: Math.sin(tank.angle) * bulletSpeed,
        color: tank.color
    });
}


function updateTank(tank) {
    tank.x += tank.dx;
    tank.y += tank.dy;

    if (tank.x < 0) tank.x = 0;
    if (tank.y < 0) tank.y = 0;
    if (tank.x + tank.width > canvas.width) tank.x = canvas.width - tank.width;
    if (tank.y + tank.height > canvas.height) tank.y = canvas.height - tank.height;
}


function updateBullets() {
    bullets.forEach((bullet, index) => {
        bullet.x += bullet.dx;
        bullet.y += bullet.dy;
        if (bullet.x < 0 || bullet.y < 0 || bullet.x > canvas.width || bullet.y > canvas.height) {
            bullets.splice(index, 1);
        }
    });
}


function drawTank(tank) {
    ctx.save();
    ctx.translate(tank.x + tank.width / 2, tank.y + tank.height / 2);
    ctx.rotate(tank.angle);
    ctx.fillStyle = tank.color;
    ctx.fillRect(-tank.width / 2, -tank.height / 2, tank.width, tank.height);
    ctx.restore();
}


function drawBullets() {
    bullets.forEach(bullet => {
        ctx.beginPath();
        ctx.arc(bullet.x, bullet.y, bulletSize, 0, Math.PI * 2);
        ctx.fillStyle = bullet.color;
        ctx.fill();
    });
}


function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    updateTank(tank1);
    updateTank(tank2);
    updateBullets();
    
    drawTank(tank1);
    drawTank(tank2);
    drawBullets();

    requestAnimationFrame(gameLoop);
}


gameLoop();
