import pygame
import random
from PIL import Image

pygame.init()


# Сначала создадим все функции, которыми будем пользоваться в игре

def save_data(data, line):  # Функция, которая будет записывать счет в файлик при выходе из игры
    with open('data.txt', 'r') as datafile:
        datalines = datafile.readlines()
        datalines[line] = str(data) + '\n'
    with open('data.txt', 'w') as datafile:
        datafile.writelines(datalines)


def maxscore(score):  # Функция, в случае смерти возвращающая этап, на котором игрок находился
    if score < 285:
        return 0
    elif score < 555:
        return 285
    elif score < 956:
        return 555
    elif score < 1181:
        return 956
    else:
        return 1181


def gifs(filename):  # Создаем функцию распознования гиф-файлов
    image = Image.open(filename)
    frames = []
    try:
        while True:
            frame = image.copy()
            frame = frame.convert("RGBA")
            frame_surface = pygame.image.fromstring(frame.tobytes(), image.size, "RGBA")
            frame_surface = pygame.transform.scale(frame_surface, (w, h))
            frames.append(frame_surface)
            image.seek(image.tell() + 1)  # Переход к следующему кадру
    except EOFError:  # если закончились кадры
        pass
    return frames


# Теперь основные параметры: окно, название, иконка, статус на момент начала, переменная для частоты кадров
# Для навигации: основные параметры, счет, фоны, музыка, текст (+ функция для него)
w = 1400
h = 788
scr = pygame.display.set_mode((w, h))
pygame.display.set_caption("retro wave game")
icon = pygame.image.load("icon.bmp")
pygame.display.set_icon(icon)
state = "menu"
clock = pygame.time.Clock()

with open('data.txt', 'r') as file:  # загружаем счет из первой строчки файла
    lines = file.readlines()
    score = int(lines[0].strip())
    deaths = int(lines[1].strip())
score_event = pygame.USEREVENT + 1
pygame.time.set_timer(score_event, 1000)

menugif = gifs("backgrounds/menu.gif")  # в главном меню сделаем фоновое изображение
menu_gif_count = len(menugif)
current_frame = 0
frame_delay = 100
last_update = pygame.time.get_ticks()

backgrounds = [
    pygame.transform.scale(pygame.image.load("backgrounds/0.bmp"), (w, h)),
    pygame.transform.scale(pygame.image.load("backgrounds/1.bmp"), (w, h)),
    pygame.transform.scale(pygame.image.load("backgrounds/2.bmp"), (w, h)),
    pygame.transform.scale(pygame.image.load("backgrounds/3.bmp"), (w, h)),
    pygame.transform.scale(pygame.image.load("backgrounds/4.bmp"), (w, h))
]  # загружаем все фоны и музыку (ниже)

music = ["music/music0.mp3", "music/music1.mp3", "music/music2.mp3", "music/music3.mp3", "music/music4.mp3"]
hearts = [pygame.image.load("hearts/heart.0.png"),
          pygame.image.load("hearts/heart.1.png"),
          pygame.image.load("hearts/heart.2.png"),
          ]

font = pygame.font.Font("Silkscreen.ttf", 40)  # Разбираемся со всеми текстами, которые будут в игре
font1 = pygame.font.Font("Silkscreen.ttf", 20)

quittext = font.render('quit', True, (255, 255, 255))  # В меню
quittext_rect = quittext.get_rect(center=(w // 2, h // 2 + 250))
playtext = font.render('play', True, (255, 255, 255))
playtext_rect = playtext.get_rect(center=(w // 2, h // 2 + 100))
resettext = font.render('reset', True, (255, 255, 255))
resettext_rect = resettext.get_rect(center=(w // 2, h // 2 + 175))

suretext = font.render('sure?', True, (255, 255, 255))  # Начать с начала
suretext_rect = suretext.get_rect(center=(w // 2, h // 2 + 125))
notext = font.render('no', True, (255, 255, 255))
notext_rect = notext.get_rect(center=(w // 2, h // 2 + 325))
yestext = font.render('yes', True, (255, 255, 255))
yestext_rect = yestext.get_rect(center=(w // 2, h // 2 + 225))

deadtext = font1.render("Oh no, you died!", True, (255, 255, 255))  # Экран смерти
deadtext_rect = deadtext.get_rect(center=(w // 2, h // 2 + 200))
restarttext = font1.render("I wanna restart", True, (255, 255, 255))
restarttext_rect = restarttext.get_rect(center=(w // 2, h // 2 + 250))


# Работа со спрайтами, в порядке: корабль, город, препятствия
class Starship(pygame.sprite.Sprite):  # Создаем кораблик
    def __init__(self, x, y, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 114, 69)
        self.image = pygame.image.load(f"ship/ship.{i}.png").convert_alpha()
        self.yvel = 5

    def move_up(self):  # Функции движения
        self.yvel = -12

    def move_down(self):
        self.yvel = 12

    def move_stop(self):
        self.yvel = 5

    def update(self):  # Функция изменения положения кораблика с учетом ограничений вверх / вниз
        self.rect.y += self.yvel
        if self.rect.y < 120:
            self.rect.y = 120
        elif self.rect.y > (h - 70) - self.rect.height:
            self.rect.y = (h - 70) - self.rect.height


class City(pygame.sprite.Sprite):  # Создаем город на фоне
    def __init__(self, x, y, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 4200, 526)
        self.image = pygame.image.load(f'city/nightcity.{i}.png').convert_alpha()
        self.xvel = -7


def update_city(city_1, city_2):  # Функция изменения положения города
    city_1.rect.x += city_1.xvel
    city_2.rect.x += city_2.xvel
    if city_1.rect.x < -4200:
        city_1.rect.x = 0
        city_2.rect.x = 4200


class Buildings(pygame.sprite.Sprite):  # Создаем город как препятствие
    def __init__(self, x, y, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 612, 300)
        self.image = pygame.image.load(f"items/build.{i}.png").convert_alpha()
        self.xvel = -7

    def update(self):
        self.rect.x += self.xvel
        if self.rect.x < -612:
            self.kill()


class Ships(pygame.sprite.Sprite):  # Создаем препятствие в виде кораблей
    def __init__(self, x, y, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 150, 94)
        self.image = pygame.image.load(f"items/othership.{i}.png").convert_alpha()
        self.xvel = -10

    def update(self):
        self.rect.x += self.xvel
        if self.rect.x < -150:
            self.kill()


class Vats(pygame.sprite.Sprite):  # Еще одно препятствие
    def __init__(self, x, y, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 200, 200)
        self.image = pygame.image.load(f"items/vat.{i}.png").convert_alpha()
        self.xvel = -7

    def update(self):
        self.rect.x += self.xvel
        if self.rect.x < -200:
            self.kill()


class Hearts(pygame.sprite.Sprite):  # Спасение, возвращающее жизни
    def __init__(self, x, y, i):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 45, 42)
        self.image = pygame.image.load(f"hearts/save/save.{i}.png").convert_alpha()
        self.xvel = -7
        self.yvel = 1

    def update(self):
        self.rect.x += self.xvel
        if self.rect.x < -45:
            self.kill()


def draw(sprite, scr):  # Функция, которая будет рисовать спрайты
    scr.blit(sprite.image, (sprite.rect.x, sprite.rect.y))


you = []  # Перед самой игрой обозначаем спрайты
city1 = []  # Город на фоне, который будет меняться
city2 = []
items = pygame.sprite.Group()  # Группа для хранения всех препятствий
saving = pygame.sprite.Group()  # Группа для хранения спасений
for i in range(5):
    u = Starship(200, 450, i)
    you.append(u)
    city_1 = City(0, h - 526, i)
    city_2 = City(4200, h - 526, i)
    city1.append(city_1)
    city2.append(city_2)

# Основной цикл
while True:
    if state == "reset":  # Статус, в котором можно обнулить счет и начать играть с начала
        now = pygame.time.get_ticks()  # Гифка на фоне
        if now - last_update > frame_delay:
            current_frame = (current_frame + 1) % menu_gif_count
            last_update = now
        scr.blit(menugif[current_frame], (0, 0))
        pygame.time.delay(30)
        scr.blit(suretext, suretext_rect)  # Тексты
        scr.blit(notext, notext_rect)
        scr.blit(yestext, yestext_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выключение игры по нажатию крестика
                save_data(score, 0)  # Сохраняем данные при выходе, счет и количество жизней
                save_data(deaths, 1)
                pygame.quit()
                raise SystemExit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Переход к меню
                if event.button == 1:
                    if notext_rect.collidepoint(event.pos):  # Просто выходим в меню
                        state = "menu"
                    if yestext_rect.collidepoint(event.pos):  # Обнуляем игру и выходим в меню
                        score = 0
                        deaths = 0
                        state = "menu"
    if state == "menu":  # Статус "меню", в котором можно выйти из игры, обнулить счет и начать игру
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("music/menumusic.mp3")  # Музыка в меню
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(1)
        now = pygame.time.get_ticks()  # Гифка на фоне
        if now - last_update > frame_delay:
            current_frame = (current_frame + 1) % menu_gif_count
            last_update = now
        scr.blit(menugif[current_frame], (0, 0))
        pygame.time.delay(30)
        scr.blit(quittext, quittext_rect)  # Тексты
        scr.blit(playtext, playtext_rect)
        scr.blit(resettext, resettext_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выключение игры по нажатию крестика
                save_data(score, 0)
                save_data(deaths, 1)
                pygame.quit()
                raise SystemExit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Выключение игры по нажатию кнопки выхода
                if event.button == 1:
                    if quittext_rect.collidepoint(event.pos):
                        save_data(score, 0)
                        save_data(deaths, 1)
                        pygame.quit()
                        raise SystemExit()
                    if resettext_rect.collidepoint(event.pos):  # Переход к ресету, чтобы начать сначала
                        state = "reset"
                    if playtext_rect.collidepoint(event.pos):  # Переход к самой игре
                        pygame.mixer.music.stop()
                        state = "play"
    if state == "play":  # Сама игра
        scr.fill((0, 0, 0))  # Очищение экрана
        if score < 285:  # черно-белый этап
            stage = 0  # Переменная для понимания, какой этап игры
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music[stage])  # музыка
                pygame.mixer.music.play(1, start=score)
                pygame.mixer.music.set_volume(1)
        elif score < 555:  # синий этап
            stage = 1
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music[stage])  # музыка
                pygame.mixer.music.play(1, start=score - 285)
                pygame.mixer.music.set_volume(1)
        elif score < 956:  # зеленый этап
            stage = 2
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music[stage])  # музыка
                pygame.mixer.music.play(1, start=score - 555)
                pygame.mixer.music.set_volume(1)
        elif score < 1181:  # фиолетовый этап
            stage = 3
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music[stage])  # музыка
                pygame.mixer.music.play(1, start=score - 956)
                pygame.mixer.music.set_volume(1)
        elif score < 1416:  # оранжевый этап
            stage = 4
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music[stage])  # музыка
                pygame.mixer.music.play(1, start=score - 1181)
                pygame.mixer.music.set_volume(1)
        else:  # концовка
            stage = 0
            score = 0
        if random.randint(1, 1000) > 995:  # спавн зданий как препятствий
            build_x = 1400
            build_y = 526
            building = Buildings(build_x, build_y, stage)
            items.add(building)
        if random.randint(1, 1000) > 995 - stage:  # спавн кораблей
            ship_x = 1400
            ship_y = random.randint(94, 600)
            ship = Ships(ship_x, ship_y, stage)
            items.add(ship)
        if stage > 1 and random.randint(1, 1000) > 998:  # чанов
            vat_x = 1400
            vat_y = h - 200
            vat = Vats(vat_x, vat_y, stage)
            items.add(vat)
        if random.randint(1, 10000) > 9999 - stage:  # сердец
            save_x = 1400
            save_y = random.randint(94, 600)
            save = Hearts(save_x, save_y, stage)
            saving.add(save)
        scr.blit(backgrounds[stage], (0, 0))  # Добавление фона
        scoretext = font.render(f'score {score}', True, (255, 255, 255))  # отображаем счет
        scoretext_rect = scoretext.get_rect(center=(150, 50))
        scr.blit(hearts[deaths], (50, 75))  # Показываем количество жизней
        scr.blit(scoretext, scoretext_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выход по нажатию крестика
                save_data(score, 0)
                save_data(deaths, 1)
                pygame.quit()
                raise SystemExit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Переход к меню
                    pygame.mixer.music.stop()
                    state = "menu"
                if event.key == pygame.K_w:  # Начинаем двигать корабль
                    you[stage].move_up()
                if event.key == pygame.K_s:
                    you[stage].move_down()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:  # Прекращение движения
                    you[stage].move_stop()
            if event.type == score_event:  # Обновление счета каждую секунду
                score += 1
        draw(city1[stage], scr)  # Рисуем город на фоне
        draw(city2[stage], scr)
        update_city(city1[stage], city2[stage])  # Обновляем их
        you[stage].update()
        draw(you[stage], scr)
        for item in items:  # Для всех препятствий
            item.update()
            draw(item, scr)
            if you[stage].rect.colliderect(item.rect):  # Если прошло столкновение
                if deaths == 2:  # Если жизней не осталось
                    pygame.mixer.music.stop()
                    state = "dead"
                    deaths = 0
                    item.kill()
                else:  # Если остались
                    deaths += 1
                    item.kill()
        for item in saving:  # Для сердец
            item.update()
            draw(item, scr)
            if you[stage].rect.colliderect(item.rect):  # Повышение жизней
                if deaths > 0:
                    deaths += -1
                item.kill()
        if score == 0 or score == 285 or score == 555 or score == 956 or score == 1181 or score == 1416:  # переходы
            noise = pygame.image.load("backgrounds/noise.bmp")
            pygame.transform.scale(noise, (w, h))
            scr.blit(noise, (0, 0))
            noise_sound = pygame.mixer.Sound("music/noisesound.mp3")
            noise_sound.play()
            noise_sound.set_volume(0.1)
            pygame.mixer.music.stop()
            for item in items:
                item.kill()
    if state == "dead":  # Экран смерти
        scr.fill((0, 0, 0))
        score = maxscore(score)  # Чтобы начинался этап с начала, а не вся игра заново
        dead_pic = pygame.image.load("deadpic.png").convert_alpha()
        dead_pic_rect = dead_pic.get_rect(center=(w // 2, h // 2 - 100))
        scr.blit(dead_pic, dead_pic_rect)
        scr.blit(deadtext, deadtext_rect)
        scr.blit(restarttext, restarttext_rect)
        if not pygame.mixer.music.get_busy():  # Музыка
            pygame.mixer.music.load("music/dead.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выход из игры
                save_data(score, 0)
                save_data(deaths, 1)
                pygame.quit()
                raise SystemExit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Выход в меню
                    pygame.mixer.music.stop()
                    state = "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if restarttext_rect.collidepoint(event.pos):  # Начать с начала
                        state = "play"
    pygame.display.flip()
    clock.tick(60)