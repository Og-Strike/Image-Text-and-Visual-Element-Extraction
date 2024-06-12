import cv2
import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import os

MIN_SEGMENT_AREA = 50 # Increase or Decrease to discard very small segment 

def extract_text(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)
        
        mask = cv2.bitwise_not(thresh)
        occlusion_mask = cv2.dilate(mask, None, iterations=2)
        occluded_image = cv2.bitwise_and(gray, gray, mask=occlusion_mask)
        text = pytesseract.image_to_string(Image.fromarray(occluded_image))
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def segment_image(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        visual_elements = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > MIN_SEGMENT_AREA: 
                segment = image[y:y+h, x:x+w]
                visual_elements.append(segment)
        return visual_elements
    except Exception as e:
        print(f"Error segmenting image: {e}")
        return []

def save_segments(visual_elements, output_dir):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for idx, element in enumerate(visual_elements):
            segment_path = os.path.join(output_dir, f"segment_{idx}.png")
            cv2.imwrite(segment_path, element)
    except Exception as e:
        print(f"Error saving segments: {e}")

def generate_html(text, visual_elements):
    try:
        html_content = "<html>\n<body>\n"
        html_content += f"<p>{text}</p>\n"
        for idx in range(len(visual_elements)):
            html_content += f'<img src="segment_{idx}.png" alt="Segment {idx}"><br>\n'
        html_content += "</body>\n</html>"
        
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.html")
        with open(html_path, "w") as html_file:
            html_file.write(html_content)
    except Exception as e:
        print(f"Error generating HTML: {e}")

def clear_output_dir(output_dir):
    try:
        for f in os.listdir(output_dir):
            file_path = os.path.join(output_dir, f)
            try:
                os.remove(file_path)
            except FileNotFoundError:
                continue
    except Exception as e:
        print(f"Error clearing output directory: {e}")

def main():
    try:
        root = tk.Tk()
        root.withdraw()
        image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not image_path:
            messagebox.showerror("Error", "No file selected!")
            return

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        clear_output_dir(output_dir)
        text = extract_text(image_path)
        visual_elements = segment_image(image_path)
        save_segments(visual_elements, output_dir)
        generate_html(text, visual_elements)
        
        messagebox.showinfo("Success", f"Processing completed. Check the {output_dir} directory for results.")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


main()
