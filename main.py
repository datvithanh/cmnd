from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2

image = cv2.imread("b.png")

cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_im = Image.fromarray(cv2_im_rgb)

draw = ImageDraw.Draw(pil_im)

font = ImageFont.truetype("font/palatino_linotype.ttf", 23)

draw.text((5, 8), "Nguyễn Đình Đắc", font=font, fill=(0,0,0))

cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
cv2_im_processed = cv2.resize(cv2_im_processed, (2200,376))
cv2.imwrite("result.png", cv2_im_processed)