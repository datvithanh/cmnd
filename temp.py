from PIL import Image, ImageDraw, ImageFont
import cv2

img = Image.new('RGBA', (398, 62), (255, 0, 0, 0))

draw = ImageDraw.Draw(img)
font = ImageFont.truetype("font/palatino_linotype.ttf", 35)

draw.text((10, 15), "Nguyễn Đình Đắc", font=font, fill=(0,0,0,255))
img = img.resize((1196,188))

# image = cv2.imread("2_ho-khau-1.png")

# cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
pil_im = Image.open("2_ho-khau-1.png")
# pil_im = Image.fromarray(cv2_im_rgb)

text_img = Image.new('RGBA', (1196,188), (0, 0, 0, 0))
text_img.paste(pil_im, (0,0))
text_img.paste(img, (0,0), mask=img)
text_img.save("ball.png", format="png")

img.save('test.png', 'PNG')

