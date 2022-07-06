import pygame
import math


pygame.init()

WIDTH, HEIGTH = 1200, 700
UNPRESSED_COL = pygame.Color((255, 76, 76))
PRESSED_COL = pygame.Color((56, 204, 129))
FONT = pygame.font.Font('font/Pixeltype.ttf', 60)
BASE_FONT = pygame.font.Font('font/Pixeltype.ttf', 28)


class Switcher:

    def __init__(self, position, w, h, title):
        self.x, self.y = position
        self.w = w
        self.h = h
        self.title = title
        self.color = PRESSED_COL
        self.font = BASE_FONT

        self.is_pressed = False
        self.state = False
        self.button_rect = pygame.Rect(self.x, self.y, w, h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.is_pressed = not self.is_pressed
                self.state = self.is_pressed

        if self.is_pressed:
            self.color = PRESSED_COL
        else:
            self.color = UNPRESSED_COL

        return self.state

    def draw(self, surface):
        label = self.font.render(self.title, True, self.color)
        surface.blit(label, (self.button_rect.x, self.button_rect.y - 25))
        if self.is_pressed:
            pygame.draw.rect(surface, self.color, self.button_rect)
        else:
            pygame.draw.rect(surface, self.color, self.button_rect, 1)


class User_Input:

    def __init__(self, position, w, h, title, user_input=''):
        self.x, self.y = position
        self.w = w
        self.h = h
        self.title = title
        self.user_input = user_input
        self.font = BASE_FONT
        self.color = UNPRESSED_COL

        self.input_rect = pygame.Rect(self.x, self.y, w, h)
        self.text_surface = FONT.render(user_input, False, self.color)
        self.is_active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.is_active = not self.is_active
            else:
                self.is_active = False

        if self.is_active:
            self.color = PRESSED_COL
        else:
            self.color = UNPRESSED_COL

        if event.type == pygame.KEYDOWN:
            if self.is_active:
                if event.key == pygame.K_RETURN:
                    output = self.user_input
                    self.user_input = ''
                    return output
                if event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                else:
                    self.user_input += event.unicode

                self.text_surface = self.font.render(
                    self.user_input, False, self.color)

    def resize(self):
        if self.input_rect.w < 150:
            new_width = max(100, self.text_surface.get_width() + 15)
            self.input_rect.w = new_width
        else:
            self.is_active = False

    def draw(self, surface):
        label = self.font.render(self.title, True, self.color)
        self.resize()
        pygame.draw.rect(surface, self.color, self.input_rect, 1)
        surface.blit(self.text_surface,
                     (self.input_rect.x + 5, self.input_rect.y + 5))
        surface.blit(label, (self.input_rect.x, self.input_rect.y - 25))


class Pendulum:

    g = 9.8

    def __init__(self, mass, length, surf_width, radius, angle=2 * math.pi, ball_pos=(0, 0)):

        self.__x, self.__y = ball_pos

        self.__angle = angle
        self.__length = length if length > 20 else 20
        self.__origin_x = surf_width / 2
        self.__origin_y = 50
        self.__mass = mass if mass > 1 else 1
        self.__radius = radius if radius > 1 else 1
        self.__angular_velocity = 0

    def recalc_angle(self):
        self.__length = math.sqrt(
            (self.__x - self.__origin_x) ** 2 + (self.__y - self.__origin_y) ** 2)

        self.__angle = math.asin((self.__x - self.__origin_x) / self.__length)

    def swing(self):
        angular_accelaration = -self.g / 10 * \
            math.sin(self.__angle) / self.__length
        self.__angular_velocity += angular_accelaration
        self.__angular_velocity *= 0.991
        self.__angle += self.__angular_velocity

        self.__x = math.floor(self.__origin_x +
                              self.__length * math.sin(self.__angle))
        self.__y = math.floor(self.__origin_y +
                              self.__length * math.cos(self.__angle))

    def draw(self, surface):
        pygame.draw.line(surface, 'Black', (self.__origin_x,
                         self.__origin_y), (self.__x, self.__y))
        pygame.draw.circle(surface, 'Black', (self.__origin_x,
                                              self.__origin_y), 5)
        pygame.draw.circle(surface, (157, 157, 157), (self.__origin_x,
                                                      self.__origin_y), 3)
        pygame.draw.circle(
            surface, 'Black', (self.__x, self.__y), self.__radius)
        pygame.draw.circle(surface, (172, 99, 249),
                           (self.__x, self.__y), self.__radius - 2)


class Solar_System:

    ASTRO_UNIT = 149597870700

    def __init__(self, position, type, radius, mass):

        self.__x, self.__y = position

        self.__radius = radius
        self.__type = type
        self.__mass = mass

        self.is_sun = False
        self.sun_distance = 0

        self.x_velocity = 0
        self.y_velocity = 0

        self.scope = 100 / self.ASTRO_UNIT
        self.time_scope = 3600 * 24
        self.G = 6.67 * (10 ** -11)

    def motion(self, planets):
        Fx = 0
        Fy = 0

        for item in planets:
            if self == item:
                continue

            full_distance = math.sqrt(
                (item.__x - self.__x) ** 2 + (item.__y - self.__y) ** 2)
            angle = math.atan2(item.__y - self.__y, item.__x - self.__x)

            if item.is_sun:
                self.sun_distance = full_distance

            Fx += math.cos(angle) * self.G * self.__mass * \
                item.__mass / full_distance ** 2
            Fy += math.sin(angle) * self.G * self.__mass * \
                item.__mass / full_distance ** 2

        self.x_velocity += Fx / self.__mass * self.time_scope
        self.y_velocity += Fy / self.__mass * self.time_scope

        self.__x += self.x_velocity * self.time_scope
        self.__y += self.y_velocity * self.time_scope

    def draw(self, surface, width, heigth):
        pygame.draw.circle(surface, self.__type, (self.__x * self.scope + width / 2, self.__y * self.scope + heigth / 2
                                                  ), self.__radius)


def init_window(size, caption):
    pygame.display.set_caption(caption)
    WIN = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    return WIN, clock


def main():
    WIN, clock = init_window((WIDTH, HEIGTH), 'Course Work')

    fps = 60
    inMenu = True
    pendulum = False
    solar_system = False

    # BG
    menu_bg = pygame.image.load('images/menu_bg.jpeg').convert()
    graphic_area = pygame.Surface((WIDTH - 450, HEIGTH - 50))
    solar_system_bg = pygame.Surface((WIDTH - 450, HEIGTH - 50))

    # Pendulum
    radius = 15
    mass = 5
    length_of_pendulum = 200

    radius_input = User_Input((850, 50), 100, 25, 'Radius')
    mass_input = User_Input((850, 125), 100, 25, 'Mass')
    len_of_pend_input = User_Input((850, 200), 100, 25, 'Length')
    angle_input = User_Input((850, 275),
                             100, 25, 'Angle [0, 90]')

    interactive_mode = Switcher((1025, 50), 25, 25, 'Interactive Mode')
    is_interactive = False

    pendulum_obj = Pendulum(mass, length_of_pendulum, WIDTH - 450, radius)

    # Solar System
    sun = Solar_System((0, 0), (240, 255, 0), 30, 1.98892 * 10 ** 30)
    sun.is_sun = True

    earth = Solar_System((-Solar_System.ASTRO_UNIT, 0),
                         (13, 111, 212), 10, 5.97 * 10 ** 24)
    earth.y_velocity = 29.8 * 1000

    mars = Solar_System((-1.52 * Solar_System.ASTRO_UNIT, 0),
                        (168, 75, 75), 6, 0.642 * 10 ** 24)
    mars.y_velocity = 24.1 * 1000

    mercury = Solar_System((-0.39 * Solar_System.ASTRO_UNIT, 0),
                           (193, 193, 193), 4, 0.330 * 10 ** 24)
    mercury.y_velocity = 47.4 * 1000

    venus = Solar_System((-0.72 * Solar_System.ASTRO_UNIT, 0),
                         (255, 255, 255), 8, 4.87 * 10 ** 24)
    venus.y_velocity = 35 * 1000

    jupiter = Solar_System((-5.2 * Solar_System.ASTRO_UNIT, 0),
                           (216, 202, 157), 15, 1898 * 10 ** 24)
    jupiter.y_velocity = 13.1 * 1000

    saturn = Solar_System((-9.5 * Solar_System.ASTRO_UNIT, 0),
                          (233, 199, 85), 10, 568 * 10 ** 24)
    saturn.y_velocity = 9.7 * 1000

    uranus = Solar_System((-19.2 * Solar_System.ASTRO_UNIT, 0),
                          (89, 210, 187), 8, 86.8 * 10 ** 24)
    uranus.y_velocity = 6.8 * 1000

    neptune = Solar_System((-30.1 * Solar_System.ASTRO_UNIT, 0),
                           (89, 169, 210), 6, 102 * 10 ** 24)
    neptune.y_velocity = 5.4 * 1000

    galaxy_objects = [sun]

    add_earth = Switcher((850, 75), 25, 25, 'Earth')
    add_mars = Switcher((850, 150), 25, 25, 'Mars')
    add_mercury = Switcher((850, 225), 25, 25, 'Mercury')
    add_venus = Switcher((850, 300), 25, 25, 'Venus')
    add_jupiter = Switcher((850, 75), 25, 25, 'Jupiter')
    add_saturn = Switcher((850, 150), 25, 25, 'Saturn')
    add_uranus = Switcher((850, 225), 25, 25, 'Uranus')
    add_neptune = Switcher((850, 300), 25, 25, 'Neptune')

    other_planets = Switcher((1025, 75), 25, 25, 'Other')
    is_other_btn_pressed = False

    # Menu
    name = FONT.render('Physical Procceses', True, (255, 255, 255))
    name_rect = name.get_rect(center=(WIDTH / 2, 70))

    options_text = FONT.render('Choose the Option:', True, (255, 255, 255))
    options_text_rect = options_text.get_rect(midleft=(70, HEIGTH / 2))

    pendulum_text = FONT.render('Pendulum', True, (255, 255, 255))
    pendulum_text_rect = pendulum_text.get_rect(
        center=(WIDTH / 2, HEIGTH / 2))

    solar_system_text = FONT.render('Solar System', True, (255, 255, 255))
    solar_system_text_rect = solar_system_text.get_rect(
        center=(WIDTH * 3 / 4, HEIGTH / 2))

    stop = False

    while not stop:
        clock.tick(fps)

        for event in pygame.event.get():
            stop = event.type == pygame.QUIT

            if inMenu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pendulum_text_rect.collidepoint(event.pos):
                        inMenu = False
                        pendulum = True
                    elif solar_system_text_rect.collidepoint(event.pos):
                        inMenu = False
                        solar_system = True

            elif pendulum:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pendulum = False
                        inMenu = True

                temp_radius = radius_input.handle_event(event)
                if temp_radius != None:
                    if temp_radius.isdigit():
                        radius = int(temp_radius)
                        pendulum_obj = Pendulum(
                            mass, length_of_pendulum, WIDTH - 450, radius)

                temp_mass = mass_input.handle_event(event)
                if temp_mass != None:
                    if temp_mass.isdigit():
                        mass = int(temp_mass)
                        pendulum_obj = Pendulum(
                            mass, length_of_pendulum, WIDTH - 450, radius)

                is_interactive = interactive_mode.handle_event(event)
                if is_interactive:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if graphic_area.get_rect().collidepoint(event.pos):
                            pendulum_obj = Pendulum(
                                mass, length_of_pendulum, WIDTH - 450, radius,  ball_pos=pygame.mouse.get_pos())
                            pendulum_obj.recalc_angle()

                if not is_interactive:
                    temp_len_of_pend = len_of_pend_input.handle_event(event)
                    if temp_len_of_pend != None:
                        if temp_len_of_pend.isdigit():
                            length_of_pendulum = int(temp_len_of_pend)
                            pendulum_obj = Pendulum(
                                mass, length_of_pendulum, WIDTH - 450, radius)

                    temp_angle = angle_input.handle_event(event)
                    if temp_angle != None:
                        if temp_angle.isdigit():
                            angle = math.radians(int(temp_angle)) if (
                                int(temp_angle) in range(0, 91)) else 2 * math.pi
                            pendulum_obj = Pendulum(
                                mass, length_of_pendulum, WIDTH - 450, radius, angle=angle)

            elif solar_system:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        solar_system = False
                        inMenu = True

                is_other_btn_pressed = other_planets.handle_event(event)
                galaxy_objects = [sun]

                if is_other_btn_pressed:
                    is_jupiter_added = add_jupiter.handle_event(event)
                    if is_jupiter_added:
                        if jupiter not in galaxy_objects:
                            galaxy_objects.append(jupiter)

                    if not is_jupiter_added:
                        if jupiter in galaxy_objects:
                            galaxy_objects.remove(jupiter)

                    is_saturn_added = add_saturn.handle_event(event)
                    if is_saturn_added:
                        if saturn not in galaxy_objects:
                            galaxy_objects.append(saturn)

                    if not is_saturn_added:
                        if saturn in galaxy_objects:
                            galaxy_objects.remove(saturn)

                    is_uranus_added = add_uranus.handle_event(event)
                    if is_uranus_added:
                        if uranus not in galaxy_objects:
                            galaxy_objects.append(uranus)

                    if not is_uranus_added:
                        if uranus in galaxy_objects:
                            galaxy_objects.remove(uranus)

                    is_neptune_added = add_neptune.handle_event(event)
                    if is_neptune_added:
                        if neptune not in galaxy_objects:
                            galaxy_objects.append(neptune)

                    if not is_neptune_added:
                        if neptune in galaxy_objects:
                            galaxy_objects.remove(neptune)

                    for item in galaxy_objects:
                        item.scope = 10 / item.ASTRO_UNIT

                        if not item.is_sun:
                            item.time_scope = 3600 * 24 * 7

                if not is_other_btn_pressed:
                    is_earth_added = add_earth.handle_event(event)
                    if is_earth_added:
                        if earth not in galaxy_objects:
                            galaxy_objects.append(earth)

                    if not is_earth_added:
                        if earth in galaxy_objects:
                            galaxy_objects.remove(earth)

                    is_mars_added = add_mars.handle_event(event)
                    if is_mars_added:
                        if mars not in galaxy_objects:
                            galaxy_objects.append(mars)

                    if not is_mars_added:
                        if mars in galaxy_objects:
                            galaxy_objects.remove(mars)

                    is_mercury_added = add_mercury.handle_event(event)
                    if is_mercury_added:
                        if mercury not in galaxy_objects:
                            galaxy_objects.append(mercury)

                    if not is_mercury_added:
                        if mercury in galaxy_objects:
                            galaxy_objects.remove(mercury)

                    is_venus_added = add_venus.handle_event(event)
                    if is_venus_added:
                        if venus not in galaxy_objects:
                            galaxy_objects.append(venus)

                    if not is_venus_added:
                        if venus in galaxy_objects:
                            galaxy_objects.remove(venus)

        if inMenu:
            menu_bg.blit(name, name_rect)
            menu_bg.blit(options_text, options_text_rect)
            menu_bg.blit(pendulum_text, pendulum_text_rect)
            menu_bg.blit(solar_system_text, solar_system_text_rect)
            WIN.blit(menu_bg, (0, 0))

        elif pendulum:
            WIN.fill((220, 220, 220))
            graphic_area.fill((192, 192, 192))

            pendulum_obj.swing()
            pendulum_obj.draw(graphic_area)

            radius_input.draw(WIN)
            mass_input.draw(WIN)

            if not is_interactive:
                len_of_pend_input.draw(WIN)
                angle_input.draw(WIN)

            interactive_mode.draw(WIN)
            WIN.blit(graphic_area, (25, 25))

        elif solar_system:
            WIN.fill((0, 0, 0))
            solar_system_bg.fill((0, 0, 0))

            for item in galaxy_objects:
                item.motion(galaxy_objects)
                item.draw(solar_system_bg, WIDTH - 450, HEIGTH - 50)

            other_planets.draw(WIN)

            if is_other_btn_pressed:
                add_jupiter.draw(WIN)
                add_saturn.draw(WIN)
                add_uranus.draw(WIN)
                add_neptune.draw(WIN)

            else:
                add_earth.draw(WIN)
                add_mars.draw(WIN)
                add_mercury.draw(WIN)
                add_venus.draw(WIN)

            WIN.blit(solar_system_bg, (25, 25))

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
