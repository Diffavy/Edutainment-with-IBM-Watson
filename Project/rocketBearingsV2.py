import pygame
import math
import sys

wScreen = 800
hScreen = 640

pygame.init()
win = pygame.display.set_mode((wScreen, hScreen))
pygame.display.set_caption('Projectile Motion')

font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 60)

class Ball(object):
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.trail = []
        self.max_trail_length = 50
        self.hit_wall = False
        self.wall_hit_pos = None
        self.wall_hit_angle = 0
        self.velx = 0
        self.vely = 0

    def draw(self, win):
        if len(self.trail) > 1:
            pygame.draw.lines(win, (200, 200, 200), False, self.trail, 2)
        
        pygame.draw.circle(win, (0, 0, 0), (self.x, self.y), self.radius)
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius - 1)
        
        if self.hit_wall and self.wall_hit_pos:
            self.draw_arrow(win, self.wall_hit_pos, self.wall_hit_angle, 30, (255, 0, 0))
    
    def draw_arrow(self, win, pos, angle, length, color):
        end_pos = (pos[0] + math.cos(angle) * length, pos[1] - math.sin(angle) * length)
        pygame.draw.line(win, color, pos, end_pos, 2)
        
        arrow_angle1 = angle + math.pi * 0.8
        arrow_angle2 = angle - math.pi * 0.8
        head_length = 10
        
        pygame.draw.line(win, color, end_pos, (
            end_pos[0] + math.cos(arrow_angle1) * head_length,
            end_pos[1] - math.sin(arrow_angle1) * head_length
        ), 2)
        
        pygame.draw.line(win, color, end_pos, (
            end_pos[0] + math.cos(arrow_angle2) * head_length,
            end_pos[1] - math.sin(arrow_angle2) * head_length
        ), 2)

    def update_trail(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    @staticmethod
    def ballPath(startx, starty, power, ang, time):
        angle = ang
        velx = math.cos(angle) * power
        vely = math.sin(angle) * power

        distX = velx * time
        distY = (vely * time) + (-4.9 * (time ** 2)) / 2

        newx = round(distX + startx)
        newy = round(starty - distY)

        return (newx, newy, velx, vely)

def redrawWindow():
    # Added planet background
    win.fill((0, 0, 20))  # Dark space background
    planet_radius = 300
    pygame.draw.circle(win, (50, 80, 120), (wScreen//2, hScreen + planet_radius - 150), planet_radius)
    
    # Original drawing
    golfBall.draw(win)
    
    if not shoot:
        pygame.draw.line(win, (0, 0, 0), line[0], line[1])
    
    bearing = math.degrees(angle)
    bearing = (90 - bearing) % 360
    
    bearing_text = font.render(f'Bearing: {round(bearing)}°', True, (255, 255, 255))
    win.blit(bearing_text, (10, 10))

    prompt_text = font.render(f'Aim due NE (North East) within 10 (deg)', True, (255, 255, 255))
    #
    win.blit(prompt_text, (200, 30))

    if show_message:
        if is_success:
            msg = large_font.render('SUCCESS!', True, (0, 255, 0))
        else:
            msg = large_font.render('MISSED!', True, (255, 0, 0))
        win.blit(msg, (wScreen//2 - 100, hScreen//2 - 30))

    pygame.display.update()

def findAngle(pos):
    sX = golfBall.x
    sY = golfBall.y
    angle = math.atan2(sY - pos[1], pos[0] - sX)
    return angle

def restrict_line():
    global line
    max_length = 200
    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]
    length = math.sqrt(dx**2 + dy**2)
    if length > max_length:
        scale = max_length / length
        line = [line[0], (int(line[0][0] + dx * scale), int(line[0][1] + dy * scale))]

# Initialize
golfBall = Ball(wScreen // 2, 494, 5, (255, 255, 255))
line = [(wScreen//2, 494), (wScreen//2, 494)]  # Initialize line

run = True
time = 0
power = 0
angle = 0
shoot = False
show_message = False
is_success = False
clock = pygame.time.Clock()

target_bearing = 45
tolerance_deg = 10

target_min = math.radians(target_bearing - tolerance_deg)
target_max = math.radians(target_bearing + tolerance_deg)

while run:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

        if not shoot and event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            angle = findAngle(pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not shoot:
                golfBall.trail = []
                golfBall.hit_wall = False
                x = golfBall.x
                y = golfBall.y
                shoot = True
                power = math.sqrt((line[1][1] - line[0][1]) ** 2 + (line[1][0] - line[0][0]) ** 2)/4
                angle = findAngle(pygame.mouse.get_pos())
                time = 0
                is_success = target_min <= angle <= target_max
                show_message = True

    if shoot:
        if golfBall.y < 500 - golfBall.radius and not golfBall.hit_wall:
            time += 0.05
            po = Ball.ballPath(x, y, power, angle, time)
            
            new_x = max(golfBall.radius, min(wScreen - golfBall.radius, po[0]))
            new_y = max(golfBall.radius, min(494, po[1]))
            
            if new_x <= golfBall.radius or new_x >= wScreen - golfBall.radius:
                golfBall.hit_wall = True
                golfBall.wall_hit_pos = (new_x, new_y)
                golfBall.wall_hit_angle = angle
                golfBall.x = new_x
                golfBall.y = new_y
                golfBall.update_trail()
            else:
                golfBall.x = new_x
                golfBall.y = new_y
                golfBall.update_trail()
        elif golfBall.hit_wall:
            pass
        else:
            shoot = False
            golfBall.y = 494
            time = 0
            pygame.time.set_timer(pygame.USEREVENT, 2000, True)

    if event.type == pygame.USEREVENT:
        show_message = False

    if not shoot:
        line = [(golfBall.x, golfBall.y), pygame.mouse.get_pos()]
        restrict_line()
    
    redrawWindow()

pygame.quit()
sys.exit()