from dancingapp import BallsEffect, GradientEffect, Music, Camera


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
