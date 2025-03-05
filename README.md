# Manga+ | Manhwa and Comics Reader

![License](https://img.shields.io/badge/licence-MIT-blue) ![Language](https://img.shields.io/badge/Python-3.10-yellow) ![Interface](https://img.shields.io/badge/Interface-Tkinter-green)

Manga+ is a lightweight and elegant application designed to read manhwas, webtoons, and comics in a vertical scrolling format. The application offers a seamless reading experience similar to online platforms, but for your local collections.

![Manga+ Screenshot](docs/images/screenshot.png)

## ✨ Features

- **Intuitive navigation** through your manhwa and comics folders
- **Vertical reading** optimized for webtoons and manhwas
- **Multi-format support** (PNG, JPG, JPEG, GIF, BMP, WEBP, WEBM)
- **Smooth navigation** with seamless vertical scrolling
- **Smart zoom** to adapt to all screens
- **Full-screen mode** for total immersion
- **Modern interface** with dark theme
- **Automatic organization** of your files in natural order

## 🚀 Installation

### Method 1: Executable (Windows)

1. Download the latest version from the [Releases](https://github.com/your-username/manga-plus/releases) section
2. Extract the ZIP contents
3. Double-click on `ManhwaReader.exe`

### Method 2: From source

```bash
# Clone the repository
git clone https://github.com/your-username/manga-plus.git
cd manga-plus

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py
```

## 📖 User Guide

1. **Open a folder** containing your images by clicking the "📂" button
2. **Navigate** through the tree view to select a folder with images
3. **Click on "Read"** to start reading in vertical mode
4. **Scroll** with the wheel to read the content
5. **Zoom in/out** with CTRL+Wheel or the dedicated buttons

### Keyboard Shortcuts

| Key | Action |
|--------|--------|
| ↑/↓ Arrows | Vertical scrolling |
| ←/→ Arrows | Navigate between images (frame-by-frame mode) |
| Ctrl + Wheel | Zoom in/out |
| Ctrl + "+" | Zoom in |
| Ctrl + "-" | Zoom out |
| Ctrl + "0" | Reset zoom |
| F11 | Full-screen mode |
| Esc | Exit full-screen |

## 🛠️ Technologies Used

- **Python 3.10+**: Main programming language
- **Tkinter**: Native graphical interface
- **Pillow**: Image processing and display
- **python-vlc**: WEBM video playback

## ⚙️ Project Structure

```
manga-plus/
├── main.py           # Main entry point of the application
├── requirements.txt  # Project dependencies
├── docs/             # Documentation and resources
│   └── images/       # Images for documentation
├── LICENSE           # Project license
└── README.md         # This file
```

## 📝 Development Notes

The application uses Tkinter for the graphical interface, which allows it to be lightweight and fast without complex external dependencies. Image handling is optimized to allow for fast loading and smooth navigation, even with large collections.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is distributed under the MIT license. See the `LICENSE` file for more information.

## 💬 Contact

Nanami - Discord: nanami2002

---

Made with ❤️ for all manhwa and webtoon enthusiasts 