from PIL import Image, ImageDraw, ImageFont
import colorsys
import textwrap


class Color:
    @staticmethod
    def average_color(image) -> tuple[int, int, int]:
        im: Image = Image.open(image)
        pixels = list(im.getdata())

        total_red: int = 0
        total_green: int = 0
        total_blue: int = 0
        for pixel in pixels:
            red, green, blue = pixel
            total_red += red
            total_green += green
            total_blue += blue

        num_pixels = len(pixels)
        red: int = total_red // num_pixels
        green: int = total_green // num_pixels
        blue: int = total_blue // num_pixels
        color: tuple[int, int, int] = (red, green, blue)

        return color

    @staticmethod
    def find_contrast_color(rgb_color: tuple[int, int, int]) -> tuple[int, ...]:
        hsv_color: tuple[float, float, float] = colorsys.rgb_to_hsv(rgb_color[0] / 255.0, rgb_color[1] / 255.0,
                                                                    rgb_color[2] / 255.0)
        inverted_hue: float = (hsv_color[0] + 0.5) % 1.0
        inverted_rgb_color = colorsys.hsv_to_rgb(inverted_hue, hsv_color[1], hsv_color[2])
        inverted_rgb_color = tuple(int(value * 255) for value in inverted_rgb_color)
        inverted_rgb_color = tuple(int(value * 255) for value in inverted_rgb_color)
        inverted_rgb_color = tuple(int(value * 255) for value in inverted_rgb_color)

        return inverted_rgb_color


class AddText:
    @staticmethod
    def draw_multiple_line_text(image, text: str, font, text_color: tuple[int, int, int],
                                text_start_height: int) -> None:
        draw = ImageDraw.Draw(image)
        image_width, image_height = image.size
        y_text = text_start_height
        lines = textwrap.wrap(text, width=40)
        for line in lines:
            line_width, line_height = font.getsize(line)
            draw.text(((image_width - line_width) / 2, y_text),
                      line, font=font, fill=text_color)
            y_text += line_height

    def add_text(self, image, text, color) -> None:
        im: Image = Image.open(image)
        fontsize: int = 40
        font = ImageFont.truetype("arial.ttf", fontsize)
        text_start_height: int = im.size[1] // 2 + im.size[1] // 4 - 50
        self.draw_multiple_line_text(im, text, font, color, text_start_height)
        im.save('image_with_text.png')
