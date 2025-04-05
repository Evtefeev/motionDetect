import os
import random
import time
import cv2
import pygame
from helpers import add_gradient, add_png_overlay_simple


class GradientEffect:
    EFFECT_LIFE = 20

    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self.life = 0
        # self.add_effect()

    def tick(self, frame, WINDOW_HEIGHT, WINDOW_WIDTH):
        if self.life == 0:
            return frame
        self.life -= 1
        return add_gradient(frame, self.color1, self.color2, self.life/self.EFFECT_LIFE)

    def add_effect(self, *args):
        if self.life == 0:
            self.color1 = random.choice(
                self.colors)
            self.color2 = random.choice(
                self.colors)
            self.percent = random.random()
            self.life = self.EFFECT_LIFE


class BallsEffect:
    EFFECT_LIFE = 10

    def __init__(self, img_path, colors=[]):
        self.effects = []
        self.EFFECT_IMG = cv2.imread(
            img_path, cv2.IMREAD_UNCHANGED)
        self.colors = colors
        self.gx = 0
        self.gy = 1

    def set_colors(self, colors):
        self.colors = colors

    def set_gravity(self, gx, gy):
        self.gx = gx
        self.gy = gy

    class Effect:
        def __init__(self, x, y, w, h, colors):
            self.x = x
            self.y = y
            self.w = w
            self.h = h
            if not colors:
                self.color = [random.randint(0, 255)
                              for _ in range(3)]
            else:
                self.color = random.choice(colors)
            self.life = BallsEffect.EFFECT_LIFE
            self.gravity = random.randint(0, 20)
            self.size = 0.5+random.random()

    def apply_effect(self, frame, effect):
        alpha = effect.life / self.EFFECT_LIFE
        add_png_overlay_simple(frame, self.EFFECT_IMG, effect.x,
                               effect.y, effect.color, alpha, effect.size)
        return frame

    def tick(self, frame, WINDOW_HEIGHT, WINDOW_WIDTH):
        for effect in self.effects:
            frame = self.apply_effect(frame, effect)
            effect.life -= 1
            effect.y += effect.gravity*self.gy
            effect.x += effect.gravity*self.gx
            if effect.life == 0 or \
                    effect.y+effect.h > WINDOW_HEIGHT or \
                    effect.x+effect.w > WINDOW_WIDTH or \
                    effect.y < 0 or effect.x < 0:
                self.effects.remove(effect)
        return frame

    def add_effect(self, *args):
        self.effects.append(self.Effect(*args, self.colors))


class Music:
    MOTION_TIMEOUT = .7
    FADE_STEPS = 20  # шагов затухания
    FADE_INTERVAL = MOTION_TIMEOUT / FADE_STEPS

    def __init__(self, music_file):
        # Инициализация звука
        pygame.mixer.init()
        alert_path = music_file  # замени на путь к своему звуку
        if not os.path.exists(alert_path):
            print("Файл звука не найден:", alert_path)
            exit()
        pygame.mixer.music.load(alert_path)

        # Флаг для отслеживания состояния звука
        self.is_playing = False
        self.was_started = False
        self.volume = 1.0  # от 0.0 до 1.0
        pygame.mixer.music.set_volume(self.volume)
        self.last_volume_update = time.time()

    def activate(self):
        # Воспроизведение звука при движении
        # Воспроизведение музыки с паузы
        if not self.was_started:
            pygame.mixer.music.play()
            self.was_started = True
            self.is_playing = True
        elif not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True

        # Вернуть громкость к максимуму
        if self.volume < 1.0:
            self.volume = 1.0
            pygame.mixer.music.set_volume(self.volume)

    def decrease(self, now):
        step = 1.0 / Music.FADE_STEPS
        self.volume = max(0.0, self.volume - step)
        pygame.mixer.music.set_volume(self.volume)
        self.last_volume_update = now

    def stop(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        self.volume = 1.0
        pygame.mixer.music.set_volume(self.volume)

    def deactivate(self, now, last_motion_time):
        time_since_motion = now - last_motion_time

        if time_since_motion < self.MOTION_TIMEOUT:
            if now - self.last_volume_update >= self.FADE_INTERVAL:
                self.decrease(now)
        else:
            self.stop()


class Camera:
    MIN_CONTOUR_AREA = 3000
    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 480
    WINDOW_NAME = "DancingApp"

    def __init__(self, music):
        self.music = music
        # Инициализация видеопотока с камеры
        self.cap = cv2.VideoCapture(0)

        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.WINDOW_NAME, self.WINDOW_WIDTH,
                         self.WINDOW_HEIGHT)

        # Начальное значение для сравнения
        _, self.frame1 = self.cap.read()
        self.frame1_gray = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)
        self.frame1_gray = cv2.GaussianBlur(self.frame1_gray, (21, 21), 0)

        self.last_motion_time = time.time()
        self.effects = []

    def detect_motions(self):
        _, self.frame2 = self.cap.read()
        frame2_gray = cv2.cvtColor(self.frame2, cv2.COLOR_BGR2GRAY)
        self.frame2_gray = cv2.GaussianBlur(frame2_gray, (21, 21), 0)

        # Вычисляем разницу между кадрами
        diff = cv2.absdiff(self.frame1_gray, self.frame2_gray)
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Находим контуры движения
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def add_effect(self, effect):
        self.effects.append(effect)

    def apply_effects(self):
        for effect in self.effects:
            self.frame2 = effect.tick(
                self.frame2, self.WINDOW_HEIGHT, self.WINDOW_WIDTH)

    def start(self):
        while True:
            # Прерываем цикл, если окно закрыто
            if cv2.getWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

            motion_detected = False
            for contour in self.detect_motions():
                if cv2.contourArea(contour) < self.MIN_CONTOUR_AREA:
                    continue
                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(contour)
                for effect in self.effects:
                    effect.add_effect(x, y, w, h)

            now = time.time()
            if motion_detected:
                self.last_motion_time = now
                cv2.putText(self.frame2, "Motion detected", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                self.music.activate()
            else:
                self.music.deactivate(now, self.last_motion_time)
                cv2.putText(self.frame2, "No motion", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            self.apply_effects()

            cv2.imshow(self.WINDOW_NAME, self.frame2)

            # Обновляем предыдущий кадр
            self.frame1_gray = self.frame2_gray

            # Выход по нажатию клавиши 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    colors = [[n, n, 255] for n in range(0, 255, 10)]
    ballsEffect = BallsEffect("effect.png")
    gradientEffect = GradientEffect([[255, 0, 0], [0, 0, 255]])
    ballsEffect.set_colors(colors)
    ballsEffect.set_gravity(0, -2)
    music = Music("lambada.mp3")
    camera = Camera(music)
    camera.add_effect(gradientEffect)
    camera.add_effect(ballsEffect)
    camera.start()
