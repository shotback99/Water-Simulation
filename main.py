"""
specify pos, size and colour
increase size -- done
problems:
gravity glitching -- done
particles building up on mouse -- done
explosion -- done

pyinstaller --onefile -w name_of_file.py
--onefile : converted into one file
-w : doesn't show terminal
don't need build or spec
if have dependicies then put in main directory
setup file to download
"""
import pygame, sys, pymunk
print(pymunk.__file__)
from time import sleep
from random import randint
from math import ceil
import os
pygame.init()
pymunk_dir = os.path.dirname(pymunk.__file__)
chipmunk_libs = [
    ('chipmunk.dll', os.path.join(pymunk_dir, 'chipmunk.dll'), 'DATA'),
]
# #...
# coll = COLLECT(exe,
#                a.binaries + chipmunk_libs,
#                a.zipfiles,
#                a.datas,
#                strip=None,
#                upx=True,
#                name=os.path.join('dist', 'basic_test'))

class Area():
    def __init__(self, width = 1950, height = 1090, font_style = None, font_size = 50, g_strength = 500, physics_fps = 60, fluid_size = 10, fluid_buff = .5):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font(font_style, font_size)
        self.clock = pygame.time.Clock()
        self.space = pymunk.Space()
        self.g_strength = g_strength
        self.g_dir = 0
        self.space.gravity = (0, self.g_strength)

        self.dyn_obj = []
        self.stat_obj = {"circles":[], "rects":[]}
        self.exp_obj = []
        self.colours = [(111, 196, 169), (111, 196, 169), (111, 196, 169), (111, 196, 169)]

        self.physics_fps = physics_fps
        self.spawn_fluid = False
        self.static_visible = True
        self.spawn_close_static = False
        self.fluid_size = 10
        self.fluid_buff = self.fluid_size * fluid_buff
        self.stat_choice = 1
        self.static_size = 1
        self.exp_time = 100
        self.counter = 0
        self.bg_image_on = False
        self.escape = False
        self.mouse_pos = pygame.mouse.get_pos()
        self.image_counter = 0
        self.images = os.listdir("images/")


    def upd_bg(self):
        self.bg_image_on = True
        if self.image_counter+1 > len(self.images):
            self.bg_image_on = not self.bg_image_on
            self.image_counter = 0
            return
        bg_image = pygame.image.load("images/" + self.images[self.image_counter]).convert_alpha()
        bg_image = pygame.transform.scale(bg_image, (self.width, self.height))
        self.bg_image = bg_image
        self.image_counter += 1

    def create_dynamic(self):
        body = pymunk.Body(1, 100, body_type = pymunk.Body.DYNAMIC) # mass, inertia, body_type
        mp = list(self.mouse_pos)
        if self.g_dir in [0, 1]:
            mp[0] += randint(-1, 1)
        else: mp[1] += randint(-1, 1)
        body.position = mp
        shape = pymunk.Circle(body, self.fluid_buff)
        self.space.add(body, shape)
        area.dyn_obj.append(shape)

    def draw_dynamic(self):
        for item in self.dyn_obj:
            # removes particle if it goes out-of-bounds for optimisation to increase fps
            if item.body.position[1] > 2*self.height or item.body.position[1] < -self.height or item.body.position[0] < -self.width or item.body.position[0] > 2*self.width: self.dyn_obj.remove(item)
            pygame.draw.circle(self.screen, (0, 0, 255), item.body.position, self.fluid_size)

    def create_static_circle(self):
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = self.mouse_pos
        shape = pymunk.Circle(body, 49*self.static_size)
        self.space.add(body, shape)
        self.stat_obj["circles"].append(shape)

    def upd_static_circle(self, pos):
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Circle(body, 49*self.static_size)
        self.space.add(body, shape)
        return shape

    def create_static_rect(self):
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = self.mouse_pos
        shape = pymunk.Poly.create_box(body,(100*self.static_size, 100*self.static_size)) # left, bottom, right, top
        self.space.add(body, shape)
        self.stat_obj["rects"].append(shape)

    def upd_static_rect(self, pos):
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body,(99*self.static_size, 99*self.static_size)) # left, bottom, right, top
        self.space.add(body, shape)
        return shape

    def draw_static(self):
        for key, items in self.stat_obj.items():
            for index, item in enumerate(items):
                if key == "circles":
                    self.stat_obj[key][index] = self.upd_static_circle(item.body.position)
                    self.space.remove(item)
                    if self.static_visible: pygame.draw.circle(self.screen, (107, 107, 107), item.body.position, 50*self.static_size)
                elif key == "rects":
                    left, bottom = item.body.position
                    self.stat_obj[key][index] = self.upd_static_rect(item.body.position)
                    self.space.remove(item)
                    if self.static_visible: pygame.draw.rect(self.screen, (107, 107, 107), (left-50*self.static_size, bottom-50*self.static_size, 100*self.static_size,  100*self.static_size), ceil(50*self.static_size))
                else: return

    def check_mouse_pos_col(self, obj_pos, mouse_pos):
        #left, bottom, right,  top
        case = 0
        if mouse_pos[0] > obj_pos.left: case += 1
        if mouse_pos[1] > obj_pos.bottom: case += 1
        if mouse_pos[0] < obj_pos.right: case += 1
        if mouse_pos[1] < obj_pos.top: case += 1
        check = True if case == 4 else False
        return check

    def draw_text(self):
        self.colours[self.g_dir] = (111, 150, 255)
        num_obj = self.font.render(f"{len(self.dyn_obj)}", False, (111, 196, 169))
        directions = [
            [self.font.render("down", False, self.colours[0]), (self.width-150, 60)],
            [self.font.render("up", False, self.colours[1]), (self.width-150, 20)],
            [self.font.render("left", False, self.colours[2]), (self.width-230, 40)],
            [self.font.render("right", False, self.colours[3]), (self.width-70, 40)]
        ]
        num_obj_rect = num_obj.get_rect(center = (50, 20))
        self.screen.blit(num_obj, num_obj_rect)
        for dir, pos in directions:
            self.screen.blit(dir, dir.get_rect(center = pos))

class ExpObj:
    def __init__(self, space, fps, tud = 1, size = 50):
        self.time_until_destroy = fps * tud
        self.space = space
        self.size = size
        self.shape = self.create_exp()
    def create_exp(self):
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = pygame.mouse.get_pos()
        shape = pymunk.Circle(body, self.size)
        self.space.add(body, shape)
        return shape
    def upd_timer(self):
        self.time_until_destroy -= 1
        check = self.check_destroy()
        return check
    def check_destroy(self):
        if self.time_until_destroy <= 0:
            self.space.remove(self.shape)
            return True
        else: return False

area = Area()

while True:
    area.screen.fill((217, 217, 217))
    if area.bg_image_on: area.screen.blit(area.bg_image, (0, 0))
    area.mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        mouse_press = pygame.mouse.get_pressed()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                area.static_visible = False
            if event.key == pygame.K_LSHIFT:
                area.spawn_close_static = True
            if event.key == pygame.K_1:
                area.stat_choice = 1
            if event.key == pygame.K_2:
                area.stat_choice = 2
            if event.key == pygame.K_z:
                area.spawn_fluid = True
            if event.key == pygame.K_x:
                area.upd_bg()
            if event.key in (pygame.K_LEFT, pygame.K_a):
                area.space.gravity = (-area.g_strength, 0)
                area.g_dir = 2
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                area.space.gravity = (area.g_strength, 0)
                area.g_dir = 3
            if event.key in (pygame.K_UP, pygame.K_w):
                area.space.gravity = (0, -area.g_strength)
                area.g_dir = 1
            if event.key in (pygame.K_DOWN, pygame.K_s):
                area.space.gravity = (0, area.g_strength)
                area.g_dir = 0
            if event.key == pygame.K_r:
                for items in area.stat_obj.values():
                    for obj in items:
                        area.space.remove(obj)
                area.stat_obj = {"circles":[], "rects":[]}
            if event.key == pygame.K_e:
                obj = ExpObj(area.space, fps = 120, tud = 0.08, size = 100)
                area.exp_obj.append(obj)
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                area.static_visible = True
            if event.key == pygame.K_LSHIFT:
                area.spawn_close_static = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_press[0]:
                area.spawn_fluid = True
            elif event.button == 4: # scroll up
                area.static_size += 0.1
            elif event.button == 5:
                area.static_size -= 0.1
                if area.static_size <= 0: area.static_size = 0
            elif mouse_press[2]:
                for key, items in area.stat_obj.items():
                    for obj in items:
                        if area.spawn_close_static:
                            if area.stat_choice == 1:
                                area.create_static_circle()
                            elif area.stat_choice == 2:
                                area.create_static_rect()
                            area.escape = True
                            break
                        elif area.check_mouse_pos_col(obj.cache_bb(), area.mouse_pos): # item.body.posiyion
                            area.space.remove(obj)
                            area.stat_obj[key].remove(obj)
                            area.escape = True
                            break
                    if area.escape:
                        area.escape = False
                        break
                else:
                    if area.stat_choice == 1:
                         area.create_static_circle()
                    elif area.stat_choice == 2:
                        area.create_static_rect()
        if event.type == pygame.MOUSEBUTTONUP:
            area.spawn_fluid = False

    if area.spawn_fluid:
        area.create_dynamic()
    for index, obj in enumerate(area.exp_obj):
        check = obj.upd_timer()
        if check:
            area.exp_obj.pop(index)

    area.draw_dynamic()
    area.draw_static()
    area.draw_text()

    area.colours = [(111, 196, 169) for i in range(4)]
    area.space.step(1/area.physics_fps)

    pygame.display.update()
    area.clock.tick(120)
    area.counter += 1
