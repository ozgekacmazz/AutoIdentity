import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
metin = pytesseract.image_to_string(Image.open("test.png"))
print("Okunan Yazı:", metin)
