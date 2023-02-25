import asyncio
import os
import time
import tkinter as tk
import uuid
from enum import Enum
from pathlib import Path

import pytesseract as tesseract
from PIL import Image
from pytesseract import Output
from selenium.webdriver.common.by import By

import driver as uc

os.system("taskkill /im chrome.exe /f")

# Tesseract needs to be installed if you are running on Windows
tesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR/tesseract.exe"


class Languages(Enum):
    C = "c"
    CPlus = "cpp"
    PYTHON = "py"
    JS = "js"
    JAVA = "java"
    RUST = "rust"
    PHP = "php"


def solver(result: dict, language: str) -> None:
    if result:
        print(f"[{time.ctime()}] Text from image is extracted")
    options = uc.options.ChromeOptions()
    options.add_argument(
        "--user-data-dir="
        + os.environ["USERPROFILE"]
        + "\\AppData\\Local\\Google\\Chrome\\User Data"
    )

    # options.add_argument("--headless")

    uc.TARGET_VERSION = 95

    driver = uc.Chrome(version_main=110, options=options)

    driver.get("https://chat.openai.com/chat")
    input_area = driver.find_element(By.TAG_NAME, "textarea")
    if result:
        print(f"[{time.ctime()}] Opening GPT OpenAI")
    for i, each_line in enumerate(result.get("text").split("\n")):
        if i == 0:
            each_line = f"Write a {language} program without explanation. Program requirements:  " + each_line
        input_area.send_keys(each_line)

    input_area.send_keys("\n")
    print(f"[{time.ctime()}] Send task to Open AI")

    async def is_finished():
        while True:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for each in buttons:
                if "Regenerate response" in each.text:
                    print(f"[{time.ctime()}] OpenAI is completed the task")
                    return
            await asyncio.sleep(1)
            print(f"[{time.ctime()}] OpenAI is processing the task", end="\r")

    is_finished()
    try:
        driver.find_element(
            By.CSS_SELECTOR,
            "#__next > div.overflow-hidden.w-full.h-full.relative > div.flex.h-full.flex-1.flex-col.md\:pl-\[260px\] > main > div.flex-1.overflow-hidden > div > div > div > div.w-full.border-b.border-black\/10.dark\:border-gray-900\/50.text-gray-800.dark\:text-gray-100.group.bg-gray-50.dark\:bg-\[\#444654\] > div > div.relative.flex.w-\[calc\(100\%-50px\)\].flex-col.gap-1.md\:gap-3.lg\:w-\[calc\(100\%-115px\)\] > div.flex.flex-grow.flex-col.gap-3 > div > div > pre > div > div.flex.items-center.relative.text-gray-200.bg-gray-800.px-4.py-2.text-xs.font-sans > button",
        ).click()
    except :
        return print(f"[{time.ctime()}] Code can not be copied")
    root = tk.Tk()
    root.withdraw()
    variable = root.clipboard_get()
    if variable:
        print(f"[{time.ctime()}] Copy results")
    Path("sources").mkdir(parents=True, exist_ok=True)
    filename = f"task_{uuid.uuid4()}.{language}"
    with open(f"sources/{filename}", "w+") as file:
        file.write(variable)
        print(f"[{time.ctime()}] Creating python program {filename}")
    print(f"[{time.ctime()}] Job Completed")
    driver.close()


# https://softwareuniversity-my.sharepoint.com/:w:/g/personal/joana_veskova_students_softuni_bg/EQd1EJ6PHt5IoQ91QVTLca8B1hc82atLNWphArtShO0sJw?rtime=GaPyhiwT20g

async def main():
    print(f"\n------------| Task solver |------------- \n")
    while True:
        work = input("Provide screenshot of a task: ").replace("\"", "")
        language = input(f"In what language? {[i.value for i in Languages]}")
        if work == "Done":
            break
        if not language in [i.value for i in Languages]:
            language = Languages.PYTHON.value
            print("Default language of Python will be used")
        if os.path.isfile(work):
            result = tesseract.image_to_string(Image.open(work), output_type=Output.DICT)
            solver(result, language)
        else:
            print("Please provide an image file")


if __name__ == '__main__':
    asyncio.run(main())
