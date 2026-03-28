import os
import sys
import argparse
import random
import tkinter as tk
import threading
from PIL import Image, ImageTk, ImageOps

class SlideshowApp:
    def __init__(self, directory, delay, debug=False):
        self.directory = directory
        self.delay = int(delay * 1000)  # Convert seconds to milliseconds
        self.debug = debug
        self.image_files = self.get_images()
        
        if not self.image_files:
            print(f"No valid images found in the directory: {directory}")
            sys.exit(1)

        # Shuffle the images randomly
        random.shuffle(self.image_files)
        
        self.current_index = 0

        # Set up the main window
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.configure(background='black')
        self.root.config(cursor="none")

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Label to hold the image
        self.label = tk.Label(self.root, bg='black')
        self.label.pack(expand=True, fill=tk.BOTH)

        # Debug mode label
        if self.debug:
            self.info_label = tk.Label(self.root, text="", fg="white", bg="black", font=("Arial", 16))
            self.info_label.place(relx=0.02, rely=0.95, anchor="w")

        # Keybindings for controls
        self.root.bind("<Escape>", self.exit_slideshow)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Left>", self.prev_image)

        self.job = None
        self.next_pil_img = None 
        
        # Load the very first image synchronously, then start the loop
        self.next_pil_img = self.process_image_data(self.current_index)
        self.show_image()

    def get_images(self):
        """Fetches image paths from the directory."""
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
        files = []
        for f in os.listdir(self.directory):
            if os.path.splitext(f)[1].lower() in valid_extensions:
                files.append(os.path.join(self.directory, f))
        return files

    def process_image_data(self, index):
        """Heavy lifting: loads and resizes the PIL image (Thread Safe)."""
        img_path = self.image_files[index]
        try:
            img = Image.open(img_path)
            img = ImageOps.exif_transpose(img)
            img.thumbnail((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            return None

    def background_preload(self, next_index):
        """Runs in a background thread to prepare the next image."""
        self.next_pil_img = self.process_image_data(next_index)

    def show_image(self):
        """Displays the current image and triggers the preload for the next."""
        if self.job:
            self.root.after_cancel(self.job)

        # 1. Display the image that was preloaded
        if self.next_pil_img:
            self.tk_img = ImageTk.PhotoImage(self.next_pil_img)
            self.label.config(image=self.tk_img)

        # 2. Update debug info once per slide
        if self.debug:
            img_name = os.path.basename(self.image_files[self.current_index])
            self.info_label.config(text=f"[{img_name}] | Set Delay: {self.delay/1000:.1f}s")

        # 3. Fire up a background thread to prepare the *next* image
        next_idx = (self.current_index + 1) % len(self.image_files)
        threading.Thread(target=self.background_preload, args=(next_idx,), daemon=True).start()

        # 4. Schedule the next display
        self.job = self.root.after(self.delay, self.next_image)

    def next_image(self, event=None):
        """Advances to the next image."""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        if event: 
            self.next_pil_img = self.process_image_data(self.current_index)
        self.show_image()

    def prev_image(self, event=None):
        """Goes back to the previous image."""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        if event:
            self.next_pil_img = self.process_image_data(self.current_index)
        self.show_image()

    def exit_slideshow(self, event=None):
        """Exits the application cleanly."""
        if self.job:
            self.root.after_cancel(self.job)
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fullscreen Randomized Image Slideshow")
    parser.add_argument("directory", help="Path to the folder containing images")
    parser.add_argument("-s", "--speed", type=float, default=6.0, help="Initial speed in seconds per image (default: 6.0)")
    parser.add_argument("-d", "--debug", action="store_true", help="Turn on informational labels during the slideshow")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: The directory '{args.directory}' does not exist.")
        sys.exit(1)

    app = SlideshowApp(args.directory, args.speed, debug=args.debug)
    app.run()