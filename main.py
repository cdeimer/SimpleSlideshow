import os
import sys
import time
import argparse
import random
import tkinter as tk
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
        self.root.config(cursor="none") # Hides the mouse cursor

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Label to hold the image
        self.label = tk.Label(self.root, bg='black')
        self.label.pack(expand=True, fill=tk.BOTH)

        # Debug mode labels - using place() to overlay on top of the image
        if self.debug:
            self.info_label = tk.Label(self.root, text="", fg="white", bg="black", font=("Arial", 16))
            # Place in the bottom left corner
            self.info_label.place(relx=0.02, rely=0.95, anchor="w")

        # Keybindings for controls
        self.root.bind("<Escape>", self.exit_slideshow)
        self.root.bind("<Up>", self.increase_speed)
        self.root.bind("<Down>", self.decrease_speed)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Left>", self.prev_image)

        self.job = None
        self.countdown_job = None
        self.target_time = 0
        
        self.show_image()

    def get_images(self):
        """Fetches image paths from the directory."""
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
        files = []
        for f in os.listdir(self.directory):
            if os.path.splitext(f)[1].lower() in valid_extensions:
                files.append(os.path.join(self.directory, f))
        return files

    def show_image(self):
        """Loads, resizes, and displays the current image."""
        if self.job:
            self.root.after_cancel(self.job)
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)

        img_path = self.image_files[self.current_index]
        try:
            img = Image.open(img_path)
            
            # Rotate the image based on its EXIF metadata
            img = ImageOps.exif_transpose(img)
            
            # Resize image to fit screen while maintaining aspect ratio
            img.thumbnail((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            
            self.tk_img = ImageTk.PhotoImage(img)
            self.label.config(image=self.tk_img)
        except Exception as e:
            print(f"Error loading {img_path}: {e}")

        # Record the exact target time for the countdown
        self.target_time = time.time() + (self.delay / 1000)

        # Schedule the next image
        self.job = self.root.after(self.delay, self.next_image)
        
        # Start the countdown UI loop if debug is on
        if self.debug:
            self.update_countdown()

    def update_countdown(self):
        """Rapidly updates the on-screen countdown timer."""
        if not self.debug:
            return

        remaining_time = max(0, self.target_time - time.time())
        img_name = os.path.basename(self.image_files[self.current_index])
        
        # Update the label text
        self.info_label.config(
            text=f"[{img_name}] | Set Delay: {self.delay/1000:.1f}s | Next in: {remaining_time:.1f}s"
        )

        # Loop this specific UI update every 100ms
        if remaining_time > 0:
            self.countdown_job = self.root.after(100, self.update_countdown)

    def next_image(self, event=None):
        """Advances to the next image and loops back to the start if at the end."""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.show_image()

    def prev_image(self, event=None):
        """Goes back to the previous image and loops to the end if at the start."""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.show_image()

    def increase_speed(self, event=None):
        """Increases slideshow speed (decreases delay)."""
        self.delay = max(500, self.delay - 500)  # Minimum delay of 0.5 seconds
        self.show_image()

    def decrease_speed(self, event=None):
        """Decreases slideshow speed (increases delay)."""
        self.delay += 500
        self.show_image()

    def exit_slideshow(self, event=None):
        """Exits the application cleanly."""
        if self.job:
            self.root.after_cancel(self.job)
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fullscreen Randomized Image Slideshow")
    parser.add_argument("directory", help="Path to the folder containing images")
    parser.add_argument("-s", "--speed", type=float, default=3.0, help="Initial speed in seconds per image (default: 3.0)")
    parser.add_argument("-d", "--debug", action="store_true", help="Turn on informational labels during the slideshow")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: The directory '{args.directory}' does not exist.")
        sys.exit(1)

    app = SlideshowApp(args.directory, args.speed, debug=args.debug)
    app.run()