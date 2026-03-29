# Simple Slideshow Command Line Utility

I had to put together a slideshow at an event, and I was annoyed at how difficult it was to do this with Apple Photos. To solve this, I used Google Gemini to cook up a quick Python utility that got the slideshow to behave exactly as I needed it to.

## How To Use
- `uv run main.py [path to directory with photos]`
- `-s` / `--speed` flag to set a custom duration for the slideshow in seconds (default is 6)
- `-d` / `--debug` flag to enable debug mode (shows filename and slide duration)

## Features
- Specify directory for photos
- Specify desired length per slide
- Debug mode
- Built with Tkinter (ensure you have this installed)
- Managed with `uv`