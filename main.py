import pygame
import pygame.gfxdraw

screen = pygame.display.set_mode((700, 500))

clock = pygame.time.Clock()

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.selected = False
        self.locked = False
        self.r = 3
    def __eq__(self, p):
        return self.x == p.x and self.y == p.y
    def draw(self):
        pygame.gfxdraw.filled_circle(screen, self.x, self.y, self.r, (0, 200, 0))
        pygame.gfxdraw.aacircle(screen, self.x, self.y, self.r, (200, 0, 0))
        if self.selected:
            pygame.gfxdraw.aacircle(screen, self.x, self.y, self.r + 2, (255, 0, 255))
    def update(self):
        self.draw()
    def update_event(self, event):
        if not self.locked:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.x - 3 <= event.pos[0] < self.x + 3 and self.y - 3 <= event.pos[1] < self.y + 3:
                        self.selected = not self.selected
                        return True
            elif event.type == pygame.MOUSEMOTION:
                b1, b2, b3 = pygame.mouse.get_pressed()
                if b1:
                    pygame.event.set_grab(True)
                    if self.selected:
                        self.x += event.rel[0]
                        self.y += event.rel[1]
                else:
                    pygame.event.set_grab(False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:
                    if self.selected:
                        points.remove(self)
        return False

class Shape:
    def __init__(self):
        self.points = []
    def init(self, x, y):
        pass
    def drag(self, x, y):
        pass
    def final(self, x, y):
        pass
    def draw(self):
        for i in range(1, len(self.points)):
            pygame.draw.aaline(screen, (0, 0, 0), (self.points[i - 1].x, self.points[i - 1].y), (self.points[i].x, self.points[i].y))
    def update(self):
        self.draw()

class Line(Shape):
    def __init__(self):
        self.point1 = None
        self.point2 = None
        self.p2raw = None
    def init(self, x, y):
        ip1 = select_point(x, y)
        if ip1 != -1:
            p1 = points[ip1]
        else:
            p1 = Point(x, y)
        p2 = Point(x, y)
        p1.locked = True
        p2.locked = True
        self.point1 = p1
        self.point2 = p2
        self.p2raw = p2
        points.append(p1)
        points.append(p2)
    def drag(self, x, y):
        if self.point1.locked and self.p2raw.locked:
            for point in points:
                if point is not self.p2raw and point is not self.point2 and point is not self.point1:
                    if point.x - 5 <= x < point.x + 5 and point.y - 5 <= y < point.y + 5:
                        point.r = 5
                        if self.point2 is self.p2raw:
                            points.remove(self.p2raw)
                        self.point2 = point
                        break
                    else:
                        point.r = 3
                        if self.point2 is not self.p2raw:
                            points.append(self.p2raw)
                            self.point2 = self.p2raw
            self.p2raw.x = x
            self.p2raw.y = y
    def final(self, x, y):
        select_point(-10000000, -10000000)
        self.point1.locked = False
        if self.p2raw is not self.point2:
            self.point2.locked = False
            self.p2raw = None
        if self.point1 == self.point2:
            points.remove(self.point1)
            points.remove(self.point2)
            shapes.remove(self)
            for point in points:
                point.selected = False
    def draw(self):
        if self.point1 is not None and self.point2 is not None:
            pygame.draw.aaline(screen, (0, 0, 0), (self.point1.x, self.point1.y), (self.point2.x, self.point2.y))
    def update(self):
        if self.point1 not in points or self.point2 not in points:
            shapes.remove(self)
        self.draw()

class Circle(Line):
    def draw(self):
        if self.point1 is not None and self.point2 is not None:
            distance = ((self.point1.x - self.point2.x) ** 2 + (self.point1.y - self.point2.y) ** 2) ** 0.5
            pygame.gfxdraw.aacircle(screen, self.point1.x, self.point1.y, round(distance), (0, 0, 0))

class Rect(Line):
    def draw(self):
        if self.point1 is not None and self.point2 is not None:
            pygame.draw.rect(screen, (0, 0, 0), (self.point1.x, self.point1.y, self.point2.x - self.point1.x, self.point2.y - self.point1.y), 1)

def select_point(x, y):
    for point in points:
        if point.x - 3 <= x < point.x + 3 and point.y - 3 <= x < point.y + 3:
            point.r = 5
            return points.index(point)
        else:
            point.r = 3
    return -1

pygame.key.set_repeat(500, 100)

points = [Point(300, 300), Point(400, 400)]
shapes = []
now = Circle
while True:
    screen.fill((255, 255, 255))
    for shape in shapes[:]:
        shape.update()
    for point in points[:]:
        point.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                mods = pygame.key.get_mods()
                if mods in (pygame.KMOD_LCTRL, pygame.KMOD_RCTRL):
                    for point in points:
                        point.selected = True
        for point in points[:]:
            if point.update_event(event):
                break
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    shapes.append(now())
                    shapes[-1].init(*event.pos)
                elif event.button == 3:
                    if now == Circle:
                        now = Line
                    elif now == Line:
                        now = Rect
                    else:
                        now = Circle
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if len(shapes) > 0:
                        shapes[-1].final(*event.pos)
            elif event.type == pygame.MOUSEMOTION:
                b1, b2, b3 = pygame.mouse.get_pressed()
                if b1:
                    if len(shapes) > 0:
                        shapes[-1].drag(*event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    for point in points:
                        if point.selected:
                            point.x -= 2
                elif event.key == pygame.K_RIGHT:
                    for point in points:
                        if point.selected:
                            point.x += 2
                elif event.key == pygame.K_UP:
                    for point in points:
                        if point.selected:
                            point.y -= 2
                elif event.key == pygame.K_DOWN:
                    for point in points:
                        if point.selected:
                            point.y += 2
    pygame.display.update()
    clock.tick(60)
