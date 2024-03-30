import os
from io import BytesIO
import openpyxl
from PIL import Image as PilImage
from utils.PathManager import load_path_manager as lpm

folder_input_db_schema = str(lpm.input("DB-Schema"))
file_db_schema = lpm.input("DB-Schema.xlsx")
os.makedirs(folder_input_db_schema, exist_ok=True)


def extract_images_from_sheet(sheet, sheet_name):
    for img in sheet._images:
        try:
            img_data = img._data()
            img_pil = PilImage.open(BytesIO(img_data))
            new_img_name = f"{sheet_name}.{img_pil.format.lower()}"
            img_pil.save(os.path.join(folder_input_db_schema, new_img_name))
            print(f"Extracted and copied image: {new_img_name}")
        except Exception as e:
            print(f"Error extracting image: {e}")


if __name__ == '__main__':

    workbook = openpyxl.load_workbook(file_db_schema)

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        extract_images_from_sheet(sheet, sheet_name)
