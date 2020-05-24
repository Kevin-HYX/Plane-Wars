import pygame
from sys import exit
from random import randint

pygame.init()

clock = pygame.time.Clock()
IF_WEAPON_AUTO = False
# 若为True,则副武器自动发射
IF_GUN_WILL_NEVER_BREAK = False
# 若为True,则主武器永远不会过热
IF_GUN_AUTO = False
# 若为True,则武器自动发射,并开启永远不过热
LOAD_BGM_TO_RAM = False
# 这将使得BGM预先加载进内存,开启后会略微提升游戏性能,但是游戏开始前会有5秒左右的加载时间,固态硬盘建议不开启
IF_DOUBLE_BUFF = True
# 将会开启硬件加速和OpenGL引擎,显卡不强建议不开
pygame.display.set_caption("飞机大战4.1")
if IF_DOUBLE_BUFF:
    screen = pygame.display.set_mode((1366, 768), pygame.DOUBLEBUF)
else:
    screen = pygame.display.set_mode((1366, 768))
moudle = 1
if moudle == 1:
    color = (150, 50, 50)
else:
    color = (233, 152, 50)
boommusic = pygame.mixer.Sound("Sounds/boommusic.ogg")

l2_going_on = True
final_score = 0


def collide_mask(rect1, image1, rect2, image2):
    x_offset = rect1[0] - rect2[0]
    y_offset = rect1[1] - rect2[1]
    left_mask = pygame.mask.from_surface(image2)
    right_mask = pygame.mask.from_surface(image1)
    return bool(left_mask.overlap(right_mask, (x_offset, y_offset)))


def object_out_of_screen(rec):
    """判断一个实例的是否超出屏幕范围"""
    if rec.bottom < 0:
        return True
    elif rec.top > 768:
        return True
    elif rec.right < 0:
        return True
    elif rec.left > 1366:
        return True
    else:
        return False


class score:
    def __init__(self):
        self.recyclable = False
        self.score_value = 0
        self.lake = 0

    def set_score(self, set_value):
        self.score_value = set_value

    def get_score(self):
        return self.score_value

    def score_append(self, add_value):
        self.lake += add_value

    def update(self):
        """拥有加分动效"""
        if self.lake > 1000:
            self.lake -= 50
            self.score_value += 50
        elif self.lake > 500:
            self.lake -= 10
            self.score_value += 10
        elif self.lake > 300:
            self.lake -= 5
            self.score_value += 5
        elif self.lake > 100:
            self.lake -= 3
            self.score_value += 3
        elif self.lake > 30:
            self.lake -= 2
            self.score_value += 2
        elif self.lake:
            self.lake -= 1
            self.score_value += 1

        font = pygame.font.Font("lucon.ttf", 50)
        global color
        image = font.render(str(self.get_score()), True, color)
        Rec = image.get_rect()
        Rec.top = 50
        Rec.left = 125
        screen.blit(image, Rec)


class none:
    """用于填充"""

    def __init__(self):
        self.recyclable = False

    def update(self):
        pass


class background_photo:
    """背景图片类"""

    def __init__(self):
        global moudle
        self.image = pygame.image.load("Photo/background" + str(moudle) + ".bmp")
        self.rec = self.image.get_rect()


class jetico:
    """左上角飞机图标"""

    def __init__(self):
        self.image = pygame.image.load("Photo/飞机Big.png")
        self.rec = self.image.get_rect()


class fire_ico:
    def __init__(self):
        self.photo = pygame.image.load('Photo/火焰.png')
        self.recyclable = False

    def update(self):
        global moudle
        if moudle == 2:
            if newMoveblePhoto.photolist[7].get_score() >= 5000:
                screen.blit(self.photo, (20, 100))
            if newMoveblePhoto.photolist[7].get_score() >= 10000:
                screen.blit(self.photo, (20, 200))
            if newMoveblePhoto.photolist[7].get_score() >= 25000:
                screen.blit(self.photo, (20, 300))


class gun_hotter_line:
    """机枪热力条"""

    def __init__(self):
        self.recyclable = False

    def update(self):
        if newMoveblePhoto.photolist[3].gunhotter < 0:
            # photolist[3]为机枪实例
            screen.blit(pygame.image.load("Photo/HotgunLine/HotgunLine1_" + str(1000) + ".png"), (1286, 270))
        elif newMoveblePhoto.photolist[3].gunhotter >= 250:
            screen.blit(pygame.image.load("Photo/HotgunLine/HotgunLine1_" + str(1249) + ".png"), (1286, 270))
        else:
            screen.blit(pygame.image.load(
                "Photo/HotgunLine/HotgunLine1_" + str(1000 + newMoveblePhoto.photolist[3].gunhotter) + ".png"),
                (1286, 270))


class gun_hotter_ico:
    """右下角机枪冷却图标"""

    def __init__(self):
        self.recyclable = False
        self.lake = 0

    def update(self):
        if newMoveblePhoto.photolist[3].gunbreak:
            screen.blit(pygame.image.load(
                "Photo/Hotgun/Hotgun" + str(1000 + newMoveblePhoto.photolist[3].gunbreaktick) + ".png"), (1256, 658))
            self.lake += 1
            if self.lake == 5:
                self.lake = 0
                newMoveblePhoto.photolist[3].gunbreaktick += 1
            if newMoveblePhoto.photolist[3].gunbreaktick == 100:
                newMoveblePhoto.photolist[3].gunbreak = False
                newMoveblePhoto.photolist[3].gunbreaktick = 0
        else:
            screen.blit(pygame.image.load("Photo/Hotgun/Hotgun" + str(1099) + ".png"), (1256, 658))

    def disappear(self):
        pass


class gun:
    """机枪类"""

    def __init__(self):
        self.gunhotter = 0
        self.gunbreak = False
        self.gunbreaktick = 0
        self.ifshooting = False
        self.recyclable = False
        self.music_tick = 0
        # 确保子弹的声音不频繁

    def update(self):
        pygame.event.pump()
        # 更新事件列表
        list_press = pygame.key.get_pressed()
        global IF_GUN_WILL_NEVER_BREAK
        global IF_GUN_AUTO

        if (list_press[pygame.K_SPACE] or list_press[pygame.K_j]) and (
                not self.gunbreak or IF_GUN_WILL_NEVER_BREAK) or IF_GUN_AUTO:
            self.shoot()
            # 内置子弹发射方法
            if not newMoveblePhoto.photolist[8].be_used:
                self.gunhotter += 1

        #     这里可以选择播放适合的音乐,比如"fire"
        elif self.gunhotter >= 0:
            self.gunhotter -= 3

        if self.gunhotter >= 250:
            self.gunbreak = True

    def shoot(self):
        """内置子弹发射方法"""
        global moudle
        if moudle == 2:
            if newMoveblePhoto.photolist[8].be_used:
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet4.png", 30))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet4.png", 30))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.right - 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet4.png", 30))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.left + 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet4.png", 30))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.centerx, newMoveblePhoto.photolist[0].rec.top - 25),
                            "Photo/Bollet4.png", 30))
            elif self.gunhotter == 249:
                newWappen.create(
                    bullet2(15, (newMoveblePhoto.photolist[0].rec.right - 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/last bullet.png", 5000))
            elif self.gunhotter >= 220:
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet3.png", 20))
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet3.png", 20))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.right - 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet4.png", 20))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.left + 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet4.png", 20))
                newWappen.create(
                    bullet3(40, (newMoveblePhoto.photolist[0].rec.centerx, newMoveblePhoto.photolist[0].rec.top - 25),
                            "Photo/Bollet4.png", 20))
            elif self.gunhotter >= 180:
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet3.png", 20))
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet3.png", 20))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.right - 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet2.png", 5))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.left + 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet2.png", 5))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.centerx, newMoveblePhoto.photolist[0].rec.top - 25),
                            "Photo/Bollet2.png", 9))
            elif self.gunhotter >= 150:
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet.png", 4))
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet.png", 4))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.right - 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet2.png", 5))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.left + 15, newMoveblePhoto.photolist[0].rec.top - 2),
                            "Photo/Bollet2.png", 5))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.centerx, newMoveblePhoto.photolist[0].rec.top - 25),
                            "Photo/Bollet2.png", 3))
            elif self.gunhotter >= 50:
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet.png", 4))
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet.png", 4))
                newWappen.create(
                    bullet2(40, (newMoveblePhoto.photolist[0].rec.centerx, newMoveblePhoto.photolist[0].rec.top - 25),
                            "Photo/Bollet2.png", 3))
            else:
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet.png", 3))
                newWappen.create(
                    bullet(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                           "Photo/Bollet.png", 3))
        else:
            newWappen.create(
                bullet(40, (newMoveblePhoto.photolist[0].rec.right - 2, newMoveblePhoto.photolist[0].rec.top - 2),
                       "Photo/Bollet.png", 4))
            newWappen.create(
                bullet(40, (newMoveblePhoto.photolist[0].rec.left + 2, newMoveblePhoto.photolist[0].rec.top - 2),
                       "Photo/Bollet.png", 4))
            newWappen.create(
                bullet2(40, (newMoveblePhoto.photolist[0].rec.centerx, newMoveblePhoto.photolist[0].rec.top - 25),
                        "Photo/Bollet2.png", 3))
        # 创造左右各一颗子弹的实例,被wappen代为管理
        self.music_tick += 1
        if self.music_tick == 5:
            newMisic.create(bullet_music())
            self.music_tick = 0

    def disappear(self):
        pass


class bullet_music:
    def __init__(self):
        pygame.mixer.Sound.play(pygame.mixer.Sound("Sounds/Bolletshoot.ogg"))
        self.recyclable = True

    def update(self):
        pass

    def disappear(self):
        pass


class bullet:
    """子弹类,每一个子弹都是一个实例"""

    def __init__(self, move, center, String, hurt):
        """移动速度,子弹中心坐标,子弹图片路径,子弹伤害"""
        self.move = move
        self.image = pygame.image.load(String)
        self.rec = self.image.get_rect()
        self.rec.center = center
        self.inaccuracy = randint(-4, 4)
        self.recyclable = False
        self.hurt = hurt
        self.system_made = False

    def update(self):
        screen.blit(self.image, self.rec)
        self.rec.top -= self.move
        self.rec.left -= self.inaccuracy
        if object_out_of_screen(self.rec):
            self.recyclable = True

    def disappear(self):
        pass


class bullet2(bullet):
    """子弹类,每一个子弹都是一个实例"""

    def __init__(self, move, center, String, hurt):
        """移动速度,子弹中心坐标,子弹图片路径,子弹伤害"""
        super().__init__(move, center, String, hurt)
        self.inaccuracy = 0


class bullet3(bullet2):
    """子弹类,每一个子弹都是一个实例"""

    def __init__(self, move, center, String, hurt):
        """移动速度,子弹中心坐标,子弹图片路径,子弹伤害"""
        super().__init__(move, center, String, hurt)
        self.inaccuracy = randint(-10, 10)


class light_load_ico:
    def __init__(self):
        self.tick = 1
        self.lake = 0
        self.recyclable = False

    def update(self):
        if self.tick != 100:
            screen.blit(pygame.image.load("Photo/LightLoading/LightLoading" + str(10000 + self.tick) + ".png"),
                        (1256, 160))
            self.lake += 1
            if self.lake % 6 == 0:
                self.tick += 1
                self.lake == 0
        else:
            screen.blit(pygame.image.load("Photo/LightLoading/LightLoading10100.png"), (1256, 160))
            pygame.event.pump()
            global IF_WEAPON_AUTO
            key_pressed_list = pygame.key.get_pressed()
            if key_pressed_list[pygame.K_i] or IF_WEAPON_AUTO:
                newWappen.create(light_shoot())
                self.tick = 1

    def disappear(self):
        pass


class light_shoot:
    def __init__(self):
        self.shootick = 0
        self.rec = None
        self.hurt = None
        self.recyclable = False
        self.system_made = False

    def update(self):
        if self.shootick == 205:
            self.shootick = 0
            self.recyclable = True
            newMoveblePhoto.photolist[4].tick = 1
            self.hurt = 0
        else:
            image = pygame.image.load("Photo/LightShoot/LightShoot" + str(1000 + self.shootick) + ".png")
            self.rec = image.get_rect()
            self.rec.center = newMoveblePhoto.photolist[0].rec.center
            self.rec.bottom = newMoveblePhoto.photolist[0].rec.top - 6
            screen.blit(image, self.rec)
            self.shootick += 1
            if 40 < self.shootick < 190:
                self.hurt = 20
            else:
                self.hurt = 5

    def disappear(self):
        pass


class boom_load_ico:
    def __init__(self):
        self.tick = 1
        self.recyclable = False
        self.image = pygame.image.load("Photo/Boomloading/Boomloading" + str(1179) + ".png")
        self.rect = self.image.get_rect()

    def update(self):
        if self.tick != 180:
            screen.blit(pygame.image.load("Photo/Boomloading/Boomloading" + str(1000 + self.tick) + ".png"),
                        (1256, 10))
            self.tick += 1
        else:
            pygame.event.pump()
            key_pressed_list = pygame.key.get_pressed()
            global IF_WEAPON_AUTO
            if key_pressed_list[pygame.K_k] or IF_WEAPON_AUTO:
                newWappen.create(boom())
                self.tick = 1
            screen.blit(self.image, (1256, 10))

    def disappear(self):
        pass


class boom_music:
    def __init__(self):
        global boommusic
        self.music = boommusic
        pygame.mixer.Sound.play(self.music)
        self.recyclable = False

    def update(self):
        pass


class big_boom_music:
    def __init__(self):
        self.music = pygame.mixer.Sound("Sounds/bigboommusic.ogg")
        pygame.mixer.Sound.play(self.music)
        self.recyclable = False

    def update(self):
        pass


class big_boom_ico:
    def __init__(self):
        self.tick = 1
        self.lake = 0
        self.recyclable = False
        global moudle
        self.moudle = moudle

    def update(self):
        if self.tick < 100 and newMoveblePhoto.photolist[7].get_score() > 10000 and self.moudle == 2:
            self.lake += 1
            if self.lake % 18 == 0:
                self.lake = 0
                self.tick += 1
        elif self.tick == 100:
            pygame.event.pump()
            key_pressed_list = pygame.key.get_pressed()
            global IF_WEAPON_AUTO
            if key_pressed_list[pygame.K_u] or IF_WEAPON_AUTO:
                self.tick = 1
                newWappen.create(big_boom())
        screen.blit(pygame.image.load("Photo/bigboom/bigboom" + str(10000 + self.tick) + ".png"), (1154, 0))


class big_boom:
    def __init__(self):
        self.recyclable = False
        self.hurt = 0
        self.rec = (pygame.image.load("Photo/bigboom_boom/bigboom10001.png")).get_rect()
        self.tick = 1
        self.system_made = False
        newMisic.create(big_boom_music())

    def update(self):
        if self.tick <= 34:
            screen.blit(pygame.image.load("Photo/bigboom_boom/bigboom" + str(10000 + self.tick) + ".png"), (0, 0))
            self.tick += 1
            for monster in newMonster.monsterlist:
                monster.recyclable = True
        else:
            self.recyclable = True

    def disappear(self):
        pass


class return_life:
    def __init__(self):
        self.tick = 1
        self.lake = 0
        self.recyclable = False
        global moudle
        self.moudle = moudle

    def update(self):
        if self.tick < 100 and newMoveblePhoto.photolist[7].get_score() > 5000 and moudle == 2:
            self.lake += 1
            if self.lake % 18 == 0:
                self.lake = 0
                self.tick += 1
        elif self.tick == 100:
            pygame.event.pump()
            key_pressed_list = pygame.key.get_pressed()
            global IF_WEAPON_AUTO
            if key_pressed_list[pygame.K_h] or IF_WEAPON_AUTO:
                newMoveblePhoto.photolist[6].lake -= 15
                self.tick = 1
        screen.blit(pygame.image.load("Photo/returnlife/returnlife" + str(10000 + self.tick) + ".png"), (1078, 45))


class gun_plus:
    def __init__(self):
        self.tick = 1
        self.lake = 0
        self.recyclable = False
        self.be_used = False
        global moudle
        self.moudle = moudle

    def update(self):
        if (not self.be_used) and moudle == 2:
            if self.tick < 100 and newMoveblePhoto.photolist[7].get_score() > 15000:
                self.lake += 1
                if self.lake % 11 == 0:
                    self.lake = 0
                    self.tick += 1
            elif self.tick == 100:
                pygame.event.pump()
                key_pressed_list = pygame.key.get_pressed()
                global IF_WEAPON_AUTO
                if key_pressed_list[pygame.K_n] or IF_WEAPON_AUTO:
                    self.be_used = True
                    newMoveblePhoto.photolist[3].gunbreak = False
                    newMoveblePhoto.photolist[3].gunbreaktick = 0
        else:
            if self.tick > 1:
                self.lake += 1
                if self.lake % 4 == 0:
                    self.lake = 0
                    self.tick -= 1
            else:
                self.be_used = False
        screen.blit(pygame.image.load("Photo/gunplus/gunplus" + str(10000 + self.tick) + ".png"), (1154, 88))


class boom:
    def __init__(self):
        self.image = pygame.image.load("Photo/Boom.png")
        self.rec = self.image.get_rect()
        self.rec.center = newMoveblePhoto.photolist[0].rec.center
        self.recyclable = False
        self.system_made = False
        self.hurt = 2000
        self.speed = 1

    def update(self):
        screen.blit(self.image, self.rec)
        self.rec.top -= self.speed
        self.speed += 4
        if object_out_of_screen(self.rec):
            self.recyclable = True
            self.system_made = True

    def disappear(self):
        self.rec = self.rec.inflate(20, 56)
        if newMonster.monsterlist:
            for monster in newMonster.monsterlist:
                if monster.rec.colliderect(self.rec):
                    monster.blood -= 400
        self.rec = self.rec.inflate(100, 100)
        if newMonster.monsterlist:
            for monster in newMonster.monsterlist:
                if monster.rec.colliderect(self.rec):
                    monster.blood -= 300
        self.rec = self.rec.inflate(100, 100)
        if newMonster.monsterlist:
            for monster in newMonster.monsterlist:
                if monster.rec.colliderect(self.rec):
                    monster.blood -= 200
        self.rec = self.rec.inflate(100, 100)
        if newMonster.monsterlist:
            for monster in newMonster.monsterlist:
                if monster.rec.colliderect(self.rec):
                    monster.blood -= 100

        newMoveblePhoto.create(boom_disappear(self.rec))


class boom_disappear:
    def __init__(self, rec):
        self.disappeartick = 0
        self.tick = 1
        self.rec = pygame.image.load("Photo/Break/Break" + str(10000 + self.tick) + ".png").get_rect()
        self.rec.center = rec.center
        self.recyclable = False
        newMisic.create(boom_music())

    def update(self):
        if self.tick == 17:
            self.recyclable = True
        else:
            screen.blit(pygame.image.load("Photo/Break/Break" + str(10000 + self.tick) + ".png"), self.rec)
            self.tick += 1

    def disappear(self):
        pass


class player_blood_line:
    def __init__(self):
        self.lake = 1
        self.tick = 1
        self.recyclable = False

    def Aftrekking(self, value):
        self.lake += value

        if self.tick > 100:
            self.recyclable = True

    def update(self):
        screen.blit(pygame.image.load(("Photo/LIFE/LIFE" + str(10000 + int(self.tick)) + ".jpg")), (105, 5))
        if self.lake:
            if self.lake > 0:
                self.tick += 1
                self.lake -= 1
            elif self.tick > 1:
                self.tick -= 1
                self.lake += 1
            else:
                self.lake = 0
        if self.tick == 101:
            self.disappear()

    def disappear(self):
        global l2_going_on
        l2_going_on = False
        global final_score
        final_score = newMoveblePhoto.photolist[7].get_score()


class player:
    def __init__(self):
        self.image = pygame.image.load("Photo/飞机.png")
        self.rec = self.image.get_rect()
        self.rec.center = (683, 700)
        self.temp = [False, False, False, False]
        self.movespeed = 10
        screen.blit(self.image, self.rec)
        self.recyclable = False

    def update(self):
        pygame.event.pump()
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.temp[0] = True
        else:
            self.temp[0] = False
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.temp[1] = True
        else:
            self.temp[1] = False
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.temp[2] = True
        else:
            self.temp[2] = False
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.temp[3] = True
        else:
            self.temp[3] = False
        if keys_pressed[pygame.K_ESCAPE]:
            exit()
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        if self.temp[0] and self.rec.top > 0:
            self.rec.top -= self.movespeed
        if self.temp[1] and self.rec.bottom < 768:
            self.rec.top += self.movespeed
        if self.temp[2] and self.rec.left > 0:
            self.rec.left -= self.movespeed
        if self.temp[3] and self.rec.right < 1366:
            self.rec.left += self.movespeed
        screen.blit(self.image, self.rec)

    def disappear(self):
        pass


class not_move_photos_control:
    """该类管理所有的静态图刷新"""

    def __init__(self):
        self.photolist = [background_photo(), jetico()]

    def update(self):
        for a in range(0, len(self.photolist)):
            screen.blit(self.photolist[a].image, self.photolist[a].rec)

    def create(self, a):
        self.photolist.append(a)


class move_photo_control:
    """该类管理所有的动态图刷新"""

    def __init__(self):
        self.photolist = [player(), boom_load_ico(), gun_hotter_line(), gun(), gun_hotter_ico(), light_load_ico(),
                          player_blood_line(), score(), gun_plus(), return_life(), big_boom_ico(), fire_ico()]

    def update(self):
        if self.photolist:
            for a in range(0, len(self.photolist)):
                self.photolist[a].update()
            #     使用每个对象的update方法
            for a in range(0, len(self.photolist)):
                if a < len(self.photolist):
                    if self.photolist[a].recyclable:
                        del self.photolist[a]

    def create(self, a):
        self.photolist.append(a)


#     动态图可以被回收


class weapons_control(move_photo_control):
    """该类管理所有的武器运行,武器亦可看作动态图,加入方法"制造伤害" 即可"""

    def __init__(self):
        """方法已重写"""
        self.photolist = []

    def update(self):
        if self.photolist:
            for a in range(0, len(self.photolist)):
                self.photolist[a].update()
            #     使用每个对象的update方法
            for a in range(0, len(self.photolist)):
                if a < len(self.photolist):
                    if self.photolist[a].recyclable:
                        if not self.photolist[a].system_made:
                            self.photolist[a].disappear()
                        del self.photolist[a]

    def makehurt(self):
        for a in range(0, len(self.photolist)):
            for b in range(0, len(newMonster.monsterlist)):
                if self.photolist[a].rec.colliderect(newMonster.monsterlist[b].rec):
                    newMonster.monsterlist[b].hurted(self.photolist[a].hurt)
                    if not (isinstance(self.photolist[a], light_shoot) or isinstance(self.photolist[a],
                                                                                     bullet2) or isinstance(
                        self.photolist[a], big_boom)):
                        self.photolist[a].recyclable = True


class monsters_control:
    """该类管理所有怪物运行,怪物亦可看作动态图"""

    def __init__(self):
        self.monsterlist = []
        global moudle
        self.moudle = moudle
        self.tick = 180

    def auto_create(self):
        if self.tick <= 0:
            if self.moudle == 1:

                if newMoveblePhoto.photolist[7].get_score() < 20000:
                    if True:
                        temp = randint(0, 50)
                        if temp == 25:
                            self.monsterlist.append(monster_lvl_1())
                    if 300 <= newMoveblePhoto.photolist[7].get_score():
                        temp = randint(0, 60)
                        if temp == 25:
                            self.monsterlist.append(monster_lvl_2())
                    if 800 <= newMoveblePhoto.photolist[7].get_score():
                        temp = randint(0, 70)
                        if temp == 25:
                            self.monsterlist.append(monster_lvl_3())
                    if 1500 <= newMoveblePhoto.photolist[7].get_score():
                        temp = randint(0, 80)
                        if temp == 25:
                            self.monsterlist.append(monster_lvl_4())
                    if 3000 <= newMoveblePhoto.photolist[7].get_score():
                        temp = randint(0, 120)
                        if temp == 25:
                            self.monsterlist.append(monster_lvl_5())
                    if 5000 <= newMoveblePhoto.photolist[7].get_score():
                        temp = randint(0, 5000)
                        if temp == 25:
                            self.monsterlist.append(monster_boss())
                else:
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_1())
                    temp = randint(0, 80)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_2())
                    temp = randint(0, 70)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_3())
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_4())
                    temp = randint(0, 55)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_5())
                    temp = randint(0, 7500)
                    if temp == 25:
                        self.monsterlist.append(monster_boss())
            else:
                if newMoveblePhoto.photolist[7].get_score() >= 25000:
                    temp = randint(0, 50)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_7())
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_3())
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_4())
                    temp = randint(0, 70)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_6())
                    temp = randint(0, 80)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_8())
                    temp = randint(0, 3000)
                    if temp == 25:
                        self.monsterlist.append(monster_boss_3())
                elif newMoveblePhoto.photolist[7].get_score() >= 10000:
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_7())
                    temp = randint(0, 70)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_3())
                    temp = randint(0, 80)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_4())
                    temp = randint(0, 80)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_6())
                    temp = randint(0, 5000)
                    if temp == 25:
                        self.monsterlist.append(monster_boss_3())
                elif newMoveblePhoto.photolist[7].get_score() >= 5000:
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_7())
                    temp = randint(0, 70)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_3())
                    temp = randint(0, 80)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_4())
                    temp = randint(0, 90)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_6())
                    temp = randint(0, 7000)
                    if temp == 25:
                        self.monsterlist.append(monster_boss_3())
                else:
                    temp = randint(0, 30)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_1())
                    temp = randint(0, 40)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_2())
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_3())
                    temp = randint(0, 60)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_4())
                    temp = randint(0, 70)
                    if temp == 25:
                        self.monsterlist.append(monster_lvl_5())
        else:
            self.tick -= 1

    def create(self, object):
        self.monsterlist.append(object)

    def update(self):
        self.auto_create()
        if self.monsterlist:
            for a in range(0, len(self.monsterlist)):
                self.monsterlist[a].update()
            #     使用每个对象的update方法
            for a in range(0, len(self.monsterlist)):
                if a < len(self.monsterlist):
                    if self.monsterlist[a].recyclable:
                        if not self.monsterlist[a].system_made:
                            self.monsterlist[a].disappear()
                        del self.monsterlist[a]


class monster_object:
    # def __init__(self):
    #     self.image = None
    #     # 正常状态
    #     self.image1 = None
    #     # 被攻击后变为白色
    #     self.move = None
    #     # x,y
    #     self.image3 = self.image
    #     self.rec = self.image.get_rect()
    #     self.rec.centerx = None
    #     # 出现范围
    #     self.recyclable = False
    #     self.system_made = False
    #     self.hurtplayer = None
    #     # 对玩家的伤害
    #     self.blood = None
    #     # 怪物血量
    #     self.score = None
    #
    # #     击败后得分

    def update(self):
        screen.blit(self.image3, self.rec)
        self.image3 = self.image
        self.rec.bottom += self.move[1]
        self.rec.left -= self.move[0]
        if self.blood < 0:
            self.recyclable = True
        self.out_of_screen()
        self.hurt_player()

    def out_of_screen(self):
        if object_out_of_screen(self.rec):
            self.recyclable = True
            self.system_made = True

    def hurt_player(self):
        if self.rec.colliderect(newMoveblePhoto.photolist[0].rec):
            if collide_mask(newMoveblePhoto.photolist[0].rec, newMoveblePhoto.photolist[0].image, self.rec,
                            self.image3):
                newMoveblePhoto.photolist[6].Aftrekking(self.hurtplayer)
                self.recyclable = True

    def hurted(self, a):
        self.blood -= a
        self.image3 = self.image1

    def disappear(self):
        newMoveblePhoto.photolist[7].score_append(self.score)
        newMoveblePhoto.create(boom_disappear(self.rec))


class monster_lvl_1(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster1/monster1.png")
        self.image1 = pygame.image.load("Photo/Monster/monster1/monster1.1.png")
        self.move = randint(-3, 3), 6
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.centerx = randint(0, 1366)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 2
        # 对玩家的伤害
        self.blood = 7
        # 怪物血量
        self.score = 10


class monster_lvl_2(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster2/monster2.png")
        self.image1 = pygame.image.load("Photo/Monster/monster2/monster2.1.png")
        self.move = randint(-3, 3), 5
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.centerx = randint(0, 1366)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 4
        # 对玩家的伤害
        self.blood = 60
        # 怪物血量
        self.score = 10


class monster_lvl_3(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster3/monster3.png")
        self.image1 = pygame.image.load("Photo/Monster/monster3/monster3.1.png")
        self.move = 0, 8
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.centerx = randint(0, 1365)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 6
        # 对玩家的伤害
        self.blood = 170
        # 怪物血量
        self.score = 30


class monster_lvl_4(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster4/monster4.png")
        self.image1 = pygame.image.load("Photo/Monster/monster4/monster4.1.png")
        self.move = 0, 4
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.centerx = randint(0, 1365)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 10
        # 对玩家的伤害
        self.blood = 500
        # 怪物血量
        self.score = 60


class monster_lvl_5(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster5/monster5.png")
        self.image1 = pygame.image.load("Photo/Monster/monster5/monster5.1.png")
        self.move = 0, 10
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.centerx = randint(0, 1365)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 15
        # 对玩家的伤害
        self.blood = 700
        # 怪物血量
        self.score = 100


class monster_lvl_6(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster6/monster6.png")
        self.image1 = pygame.image.load("Photo/Monster/monster6/monster6.1.png")
        self.move = 0, 18
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.left = randint(0, 765)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 20
        # 对玩家的伤害
        self.blood = 800
        # 怪物血量
        self.score = 200


class monster_lvl_7(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster7/monster7.png")
        self.image1 = pygame.image.load("Photo/Monster/monster7/monster7.1.png")
        self.move = randint(-3, 3), 10
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.left = randint(0, 1350)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 5
        # 对玩家的伤害
        self.blood = 500
        # 怪物血量
        self.score = 50


class monster_lvl_8(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/monster8/monster8.png")
        self.image1 = pygame.image.load("Photo/Monster/monster8/monster8.1.png")
        self.move = 0, 12
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.left = randint(0, 1350)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 25
        # 对玩家的伤害
        self.blood = 1500
        # 怪物血量
        self.score = 600


class monster_boss(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/boss/boss.png")
        self.image1 = pygame.image.load("Photo/Monster/boss/boss1.png")
        self.move = 0, 1
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.centerx = 683
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 100
        # 对玩家的伤害
        self.blood = 10000
        # 怪物血量
        self.score = 1000


class monster_boss_3(monster_object):
    def __init__(self):
        self.image = pygame.image.load("Photo/Monster/boss3/boss3.png")
        self.image1 = pygame.image.load("Photo/Monster/boss3/boss3.1.png")
        self.move = 0, 2
        # x,y
        self.image3 = self.image
        self.rec = self.image.get_rect()
        self.rec.left = randint(0, 766)
        self.rec.bottom = 2
        # 出现范围
        self.recyclable = False
        self.system_made = False
        self.hurtplayer = 60
        # 对玩家的伤害
        self.blood = 20000
        # 怪物血量
        self.score = 2000


class music_control:
    """该类管理所有的音乐播放"""

    def __init__(self):
        global moudle
        pygame.mixer.music.load("Sounds/backgroundmusic" + str(moudle) + ".ogg")
        pygame.mixer.music.play()
        self.music_list = []

    def update(self):
        for a in range(0, len(self.music_list)):
            self.music_list[a].update()
        #     使用每个对象的update方法
        for a in range(0, len(self.music_list)):
            if a < len(self.music_list):
                if self.music_list[a].recyclable:
                    del self.music_list[a]
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

    def create(self, a):
        self.music_list.append(a)

    # 对指定物品造成伤害


while True:
    newMoveblePhoto = move_photo_control()
    newMonster = monsters_control()
    newUnMovePhoto = not_move_photos_control()
    newWappen = weapons_control()
    newMisic = music_control()
    while l2_going_on:
        newUnMovePhoto.update()
        newMonster.update()
        newMonster.auto_create()

        newWappen.update()
        newWappen.makehurt()
        newMoveblePhoto.update()
        newMisic.update()

        # 不可超越此块,否则将不被刷新
        pygame.display.update()

        clock.tick(60)

    tick_volue = 0
    lake = 0
    recttemp = screen.get_rect()
    center = (483, 384)
    image = pygame.image.load("Photo/game_over.png")
    font = pygame.font.Font("lucon.ttf", 90)
    background = pygame.image.load("Photo/background" + str(moudle) + ".jpg")
    image_exit = pygame.image.load("Photo/exit.png")
    image_exit_rec = image_exit.get_rect()
    image_exit_rec.center = (1140, 160)
    image_restart = pygame.image.load("Photo/restart.png")
    image_restart_rec = image_restart.get_rect()
    image_restart_rec.center = (1140, 600)
    OK = True
    while OK:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        screen.blit(background, (0, 0))
        screen.blit(image_restart, image_restart_rec)
        screen.blit(image_exit, image_exit_rec)
        image_rec = image.get_rect()
        image_rec.center = center
        screen.blit(image, image_rec)
        pygame.event.pump()
        key_list = pygame.key.get_pressed()
        if key_list[pygame.K_ESCAPE]:
            exit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if image_exit_rec.collidepoint(pygame.mouse.get_pos()):
                    exit()
                if image_restart_rec.collidepoint(pygame.mouse.get_pos()):
                    OK = False
                    l2_going_on = True

        if final_score > 5000:
            final_score -= 100
            lake += 100
        elif final_score > 1000:
            final_score -= 20
            lake += 20
        elif final_score > 300:
            final_score -= 10
            lake += 10
        elif final_score > 100:
            final_score -= 8
            lake += 8
        elif final_score > 30:
            final_score -= 4
            lake += 4
        elif final_score:
            final_score -= 1
            lake += 1

        score_image = font.render(str(lake), True, color)
        Rec = score_image.get_rect()
        Rec.center = center
        screen.blit(score_image, Rec)

        # 不可超越此块,否则将不被刷新
        pygame.display.update()
        tick_volue += 1
        clock.tick(60)
