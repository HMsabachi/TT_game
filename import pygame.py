import pygame
import math

# 初始化 Pygame
pygame.init()

# 游戏设置
WIDTH, HEIGHT = 800, 600
FPS = 60
TANK_SIZE = 30
BULLET_SIZE = 5
BULLET_SPEED = 5
# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("坦克动荡")

# 颜色定义
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 设置坦克类
class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = TANK_SIZE
        self.height = TANK_SIZE
        self.color = color
        self.dx = 0
        self.dy = 0
        self.angle = 0  # 坦克的朝向

    def update(self):
        self.x += self.dx
        self.y += self.dy
        # 保证坦克不会走出边界
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.y = max(0, min(HEIGHT - self.height, self.y))

    def draw(self):
        # 绘制坦克
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def rotate(self, angle):
        self.angle += angle

    def move(self):
        self.x += self.dx
        self.y += self.dy

# 设置子弹类
class Bullet:
    def __init__(self, x, y, angle, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color
        self.dx = math.cos(math.radians(self.angle)) * BULLET_SPEED
        self.dy = math.sin(math.radians(self.angle)) * BULLET_SPEED

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BULLET_SIZE)

# 创建坦克实例
tank1 = Tank(100, 100, GREEN)
tank2 = Tank(700, 500, RED)

# 子弹列表
bullets = []

# 设置游戏循环的时钟
clock = pygame.time.Clock()

# 游戏主循环
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 获取按键
    keys = pygame.key.get_pressed()

    # 玩家1控制
    if keys[pygame.K_w]:
        tank1.dy = -3
    elif keys[pygame.K_s]:
        tank1.dy = 3
    else:
        tank1.dy = 0

    if keys[pygame.K_a]:
        tank1.dx = -3
    elif keys[pygame.K_d]:
        tank1.dx = 3
    else:
        tank1.dx = 0

    if keys[pygame.K_SPACE]:
        # 发射子弹
        bullets.append(Bullet(tank1.x + TANK_SIZE // 2, tank1.y + TANK_SIZE // 2, tank1.angle, GREEN))

    # 玩家2控制
    if keys[pygame.K_UP]:
        tank2.dy = -3
    elif keys[pygame.K_DOWN]:
        tank2.dy = 3
    else:
        tank2.dy = 0

    if keys[pygame.K_LEFT]:
        tank2.dx = -3
    elif keys[pygame.K_RIGHT]:
        tank2.dx = 3
    else:
        tank2.dx = 0

    if keys[pygame.K_RETURN]:
        # 发射子弹
        bullets.append(Bullet(tank2.x + TANK_SIZE // 2, tank2.y + TANK_SIZE // 2, tank2.angle, RED))

    # 更新坦克位置
    tank1.update()
    tank2.update()

    # 更新子弹位置
    for bullet in bullets[:]:
        bullet.update()
        if bullet.x < 0 or bullet.y < 0 or bullet.x > WIDTH or bullet.y > HEIGHT:
            bullets.remove(bullet)

    # 绘制坦克和子弹
    tank1.draw()
    tank2.draw()

    for bullet in bullets:
        bullet.draw()

    pygame.display.flip()

# 退出游戏
pygame.quit()
{
    "x": 100,
    "y": 100,
    "width": 30,
    "height": 30,
    "color": [0, 255, 0],
    "dx": 0,
    "dy": 0,
}