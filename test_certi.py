import os
from PIL import Image, ImageDraw, ImageFont

def generate_certificate(user_name):
        template_path = "D:\\Python_Projects\\irc\\output.png"
        img = Image.open(template_path)

        draw = ImageDraw.Draw(img)
        font_path = "D:\\Python_Projects\\irc\\birthstone.ttf" 
        font_size = 169
        font = ImageFont.truetype(font_path, font_size)

        text_bbox = draw.textbbox((0, 0), user_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        position = ((img.width - text_width) // 2, 760) 

        draw.text(position, user_name, font=font, fill="black")

        cert_path = f"{user_name}_certificate.pdf"
        img.save(cert_path, "PDF")

        return cert_path
# Calling the function
generate_certificate("Mohammad Tanvir Shaikh")


