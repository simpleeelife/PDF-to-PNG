import from PIL import Image
import os

png_path = r"c:\website\QJ\qj-compass\public\images\gallery\pdf-to-png-converter.png"
ico_path = r"C:\AntigravityProjects\pdf-to-png\pdf_to_png_converter\icon.ico"

if os.path.exists(png_path):
    img = Image.open(png_path)
    # Icon sizes to include
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)]
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"Icon saved to {ico_path}")
else:
    print(f"PNG not found at {png_path}")
