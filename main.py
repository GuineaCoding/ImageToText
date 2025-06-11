from PIL import Image
import pytesseract

image = Image.open("example.png")  
text = pytesseract.image_to_string(image)

print("Extracted Text:")
print(text)
