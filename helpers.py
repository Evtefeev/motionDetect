import cv2
import numpy as np


def add_png_overlay_simple(frame, overlay_img, x, y, color, alpha, size):
    """Наложение PNG с прозрачностью на изображение из камеры."""
    # Получаем размеры изображения и области, куда будет накладываться эффект
    h, w = overlay_img.shape[:2]
    fh, fw = frame.shape[:2]
    h = int(h*size)
    w = int(w*size)
    h = 1 if h == 0 else h
    w = 1 if w == 0 else w
    # Ограничиваем область, чтобы не выйти за пределы изображения
    if x + w > fw:
        w = fw - x
    if y + h > fh:
        h = fh - y

    # Масштабируем PNG изображение до нужного размера (h, w)
    overlay_img = cv2.resize(overlay_img, (w, h))
    # Вырезаем альфа-канал и RGB-каналы из PNG
    overlay_rgb = overlay_img[:, :, :3]  # RGB каналы
    overlay_alpha = overlay_img[:, :, 3]  # Альфа-канал

    # Создаем маску из альфа-канала
    mask = overlay_alpha / 255.0*alpha  # Маска прозрачности

    # Вычисляем обратную маску для фона
    mask_inv = 1.0 - mask

    # Вырезаем область фрейма, куда будет накладываться изображение
    roi = frame[y:y+h, x:x+w]
 # Генерация случайного цвета
    random_color = color
   # Применяем маскировку, смешиваем с случайным цветом
    for c in range(3):  # Для каждого канала (R, G, B)
        # Наложение случайного цвета
        roi[:, :, c] = (mask_inv * roi[:, :, c]) + \
            (mask * overlay_rgb[:, :, c] * random_color[c] / 255)

    # Вставляем результат обратно в кадр
    frame[y:y+h, x:x+w] = roi

    return frame


def add_gradient(frame, color_start, color_end, alpha):

    gradient = create_gradient_with_transparency(
        width=frame.shape[1],
        height=frame.shape[0],
        start_color=color_start,
        end_color=color_end,
        alpha_start=100*alpha,
        alpha_end=50*alpha,
        direction="vertical"
    )

    return overlay_gradient(frame, gradient)


def create_gradient_with_transparency(width, height, start_color, end_color, alpha_start=255, alpha_end=0, direction='horizontal'):
    """Creates a RGBA gradient from start_color to end_color.

    Args:
        width: Width of the image
        height: Height of the image
        start_color: (R, G, B) tuple
        end_color: (R, G, B) tuple
        alpha_start: Start alpha (0-255)
        alpha_end: End alpha (0-255)
        direction: 'horizontal' or 'vertical'
    """
    gradient_image = np.zeros((height, width, 4), dtype=np.uint8)

    for i in range(width if direction == 'horizontal' else height):
        ratio = i / (width - 1 if direction == 'horizontal' else height - 1)
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        a = int(alpha_start * (1 - ratio) + alpha_end * ratio)

        if direction == 'horizontal':
            gradient_image[:, i] = (b, g, r, a)
        else:
            gradient_image[i, :] = (b, g, r, a)

    return gradient_image


def overlay_gradient(base_image, gradient):
    # Ensure base image is 3-channel BGR
    if base_image.shape[2] == 4:
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGRA2BGR)

    # Resize gradient if needed
    gradient_resized = cv2.resize(
        gradient, (base_image.shape[1], base_image.shape[0]))

    # Separate channels
    overlay_rgb = gradient_resized[:, :, :3]
    alpha_mask = gradient_resized[:, :, 3] / 255.0

    # Expand alpha mask to 3 channels
    alpha_mask = np.stack([alpha_mask]*3, axis=-1)

    # Perform alpha blending
    blended = (overlay_rgb * alpha_mask + base_image *
               (1 - alpha_mask)).astype(np.uint8)
    return blended


if __name__ == "__main__":
    # ==== Live Camera with Gradient Overlay ====

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot access camera")
        exit()

    # Customize your gradient here:
    start_color = (255, 255, 0)   # Red
    end_color = (0, 0, 255)     # Blue
    alpha_start = 255
    alpha_end = 0
    direction = 'vertical'    # Try 'vertical' too!

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)

        gradient = create_gradient_with_transparency(
            width=frame.shape[1],
            height=frame.shape[0],
            start_color=start_color,
            end_color=end_color,
            alpha_start=alpha_start,
            alpha_end=alpha_end,
            direction=direction
        )

        blended = overlay_gradient(frame, gradient)

        cv2.imshow("Camera with Custom Gradient", blended)

        # Press ESC to exit
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
