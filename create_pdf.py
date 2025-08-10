import os
import shutil
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import fitz  # PyMuPDF

# --- CONFIG ---
charts_folder = 'charts'
charts_daily_folder = 'chartsDaily'  # second image source
pdf_folder = 'pdf'
page_width, page_height = letter
padding = 20  # space between the two images

os.makedirs(pdf_folder, exist_ok=True)

daily_charts = os.listdir(charts_daily_folder)

for image in os.listdir(charts_folder):
    if not image.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    # --- Get date ---
    try:
        image_date = datetime.strptime(image.split('_')[1], '%Y-%m-%d').strftime('%d-%b-%Y').upper()
    except ValueError:
        image_date = datetime.strptime(image.split('_')[2], '%Y-%m-%d').strftime('%d-%b-%Y').upper()

    base_name = image.split('_')[0]
    pdf_file = os.path.join(pdf_folder, f"{base_name}.pdf")
    image_path = os.path.join(charts_folder, image)

    # --- Find matching daily chart ---
    daily_image_file = '_'.join(image.split('_')[:-2])
    daily_image = next((item for item in daily_charts if item.startswith(daily_image_file)), None)
    
    # --- Temp PDF for these two images ---
    temp_pdf = os.path.join(pdf_folder, "_temp.pdf")
    c = canvas.Canvas(temp_pdf, pagesize=letter)

    # Header
    c.setFont("Helvetica", 20)
    c.drawString(100, page_height - 50, base_name + ' : ' + image_date)

    # First image
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        scale_factor = page_width / img_width
        new_width = page_width
        new_height1 = img_height * scale_factor
    y_position = page_height - new_height1 - 80
    c.drawImage(image_path, 0, y_position, width=new_width, height=new_height1)

    # Second image (with padding)
    if not daily_image:
        print(f"No matching daily chart found for {image}")
        continue
    daily_image_path = os.path.join(charts_daily_folder, daily_image)

    with Image.open(daily_image_path) as img:
        img_width, img_height = img.size
        scale_factor = page_width / img_width
        new_width = page_width
        new_height2 = img_height * scale_factor
    y_position -= (new_height2 + padding)
    c.drawImage(daily_image_path, 0, 0, width=new_width, height=new_height2)

    c.save()

    # --- Append or Create ---
    if os.path.exists(pdf_file):
        temp_output = os.path.join(pdf_folder, "_merged.pdf")
        existing_doc = fitz.open(pdf_file)
        new_page_doc = fitz.open(temp_pdf)
        existing_doc.insert_pdf(new_page_doc)
        existing_doc.save(temp_output)
        existing_doc.close()
        new_page_doc.close()
        shutil.move(temp_output, pdf_file)
        print(f"Appended '{image}' + '{daily_image}' to {pdf_file}")
    else:
        os.rename(temp_pdf, pdf_file)
        print(f"Created new PDF {pdf_file}")

    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)
