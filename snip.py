import datetime
import os
import sys
from tkinter import *

import pyautogui
import pyperclip
from ykutil import AzureModelWrapper, local_image_to_data_url


class Application:
    def __init__(self, master):
        self.snip_surface = None
        self.master = master
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.save_folder = "C:/Users/ykeller/Pictures/snips"
        os.makedirs(self.save_folder, exist_ok=True)
        self.model = AzureModelWrapper()

        self.master_screen = Toplevel(root)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "maroon3")
        self.picture_frame = Frame(self.master_screen, background="maroon3")
        self.picture_frame.pack(fill=BOTH, expand=YES)
        if len(sys.argv) > 1:
            self.prompt = sys.argv[1]
        else:
            self.prompt = "What's in this image?"

        self.create_screen_canvas()

    def take_bounded_screenshot(self, x1, y1, x2, y2):
        image = pyautogui.screenshot(region=(int(x1), int(y1), int(x2), int(y2)))
        self.exit_screenshot_mode()
        file_name = datetime.datetime.now().strftime("%f")
        img_path = os.path.join(self.save_folder, f"{file_name}.png")
        image.save(img_path)
        data_url = local_image_to_data_url(
            os.path.join(self.save_folder, f"{file_name}.png")
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self.prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ]
        reply = self.model.complete(messages)
        print(reply)
        pyperclip.copy(reply)
        sys.exit()

    def create_screen_canvas(self):
        self.master_screen.deiconify()
        root.withdraw()

        self.snip_surface = Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.snip_surface.pack(fill=BOTH, expand=YES)

        self.snip_surface.bind("<ButtonPress-1>", self.on_button_press)
        self.snip_surface.bind("<B1-Motion>", self.on_snip_drag)
        self.snip_surface.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen.attributes("-fullscreen", True)
        self.master_screen.attributes("-alpha", 0.3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)

    def on_button_release(self, event):
        if self.start_x <= self.current_x and self.start_y <= self.current_y:
            print("right down")
            self.take_bounded_screenshot(
                self.start_x,
                self.start_y,
                self.current_x - self.start_x,
                self.current_y - self.start_y,
            )

        elif self.start_x >= self.current_x and self.start_y <= self.current_y:
            print("left down")
            self.take_bounded_screenshot(
                self.current_x,
                self.start_y,
                self.start_x - self.current_x,
                self.current_y - self.start_y,
            )

        elif self.start_x <= self.current_x and self.start_y >= self.current_y:
            print("right up")
            self.take_bounded_screenshot(
                self.start_x,
                self.current_y,
                self.current_x - self.start_x,
                self.start_y - self.current_y,
            )

        elif self.start_x >= self.current_x and self.start_y >= self.current_y:
            print("left up")
            self.take_bounded_screenshot(
                self.current_x,
                self.current_y,
                self.start_x - self.current_x,
                self.start_y - self.current_y,
            )

        self.exit_screenshot_mode()
        return event

    def exit_screenshot_mode(self):
        self.snip_surface.destroy()
        self.master_screen.withdraw()

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.snip_surface.canvasx(event.x)
        self.start_y = self.snip_surface.canvasy(event.y)
        self.snip_surface.create_rectangle(
            0, 0, 1, 1, outline="red", width=3, fill="maroon3"
        )

    def on_snip_drag(self, event):
        self.current_x, self.current_y = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.snip_surface.coords(
            1, self.start_x, self.start_y, self.current_x, self.current_y
        )


if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()
