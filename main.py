import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import vlc  # Pour la lecture des fichiers WebM

class MangaReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Manhwa Reader")
        self.root.geometry("1200x800")
        self.current_image = None
        self.image_label = None
        self.video_player = None
        self.is_video_playing = False
        self.images = []
        self.current_image_index = -1
        self.image_cache = {}  # Cache dictionary
        self.read_button = None
        self.supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webm', '.webp')
        
        # Variables pour le zoom
        self.zoom_level = 1.0
        self.is_fullscreen = False
        self.original_geometry = "1200x800"
        
        self.setup_ui()
        self.configure_styles()
        
        # Bindings clavier et souris
        self.setup_bindings()
        
    def setup_bindings(self):
        """Configure tous les raccourcis clavier et les actions de la souris"""
        # Navigation d'images
        self.root.bind('<Left>', self.prev_image)
        self.root.bind('<Right>', self.next_image)
        self.root.bind('<Up>', lambda e: self.canvas.yview_scroll(-3, "units"))
        self.root.bind('<Down>', lambda e: self.canvas.yview_scroll(3, "units"))
        
        # Zoom
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        self.root.bind('<Control-MouseWheel>', self.on_zoom_mousewheel)
        
        # Plein écran
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)

    def zoom_in(self, factor=1.2):
        """Zoom avant"""
        self.zoom_level *= factor
        if self.comics_frame:
            self.apply_zoom()
        print(f"Zoom: {self.zoom_level:.2f}x")
        self.update_status(f"Zoom: {self.zoom_level:.2f}x")
            
    def zoom_out(self, factor=1.2):
        """Zoom arrière"""
        self.zoom_level /= factor
        if self.zoom_level < 0.1:
            self.zoom_level = 0.1
        if hasattr(self, 'comics_frame'):
            self.apply_zoom()
        print(f"Zoom: {self.zoom_level:.2f}x")
        self.update_status(f"Zoom: {self.zoom_level:.2f}x")
            
    def reset_zoom(self):
        """Réinitialise le zoom à 100%"""
        self.zoom_level = 1.0
        if hasattr(self, 'comics_frame'):
            self.apply_zoom()
        print("Zoom reset to 100%")
        self.update_status("Zoom reset to 100%")
            
    def apply_zoom(self):
        """Applique le niveau de zoom actuel aux images"""
        if not hasattr(self, 'comics_frame') or not self.images:
            return
            
        # Recalculer la largeur avec zoom
        base_width = self.canvas.winfo_width() - 20
        zoomed_width = int(base_width * self.zoom_level)
        
        # Supprimer et recréer tous les widgets dans comics_frame
        for widget in self.comics_frame.winfo_children():
            widget.destroy()
            
        # Recréer les images avec le nouveau zoom
        self.start_reading(force_reload=True, custom_width=zoomed_width)
            
    def on_zoom_mousewheel(self, event):
        """Zoom avec Ctrl+molette de souris"""
        if event.delta > 0:
            self.zoom_in(factor=1.1)
        else:
            self.zoom_out(factor=1.1)
            
    def toggle_fullscreen(self, event=None):
        """Basculer en mode plein écran"""
        if not self.is_fullscreen:
            self.original_geometry = self.root.geometry()
            self.root.attributes("-fullscreen", True)
            self.is_fullscreen = True
            self.update_status("Fullscreen mode enabled (Esc to exit)")
        else:
            self.exit_fullscreen()
            
    def exit_fullscreen(self, event=None):
        """Quitter le mode plein écran"""
        if self.is_fullscreen:
            self.root.attributes("-fullscreen", False)
            self.root.geometry(self.original_geometry)
            self.is_fullscreen = False
            self.update_status("Fullscreen mode disabled")
            
    def update_status(self, message):
        """Met à jour la barre d'état"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)

    def display_image(self, path):
        # Arrêter une vidéo en cours si nécessaire
        if self.is_video_playing and self.video_player:
            self.video_player.stop()
            self.is_video_playing = False
            
        # Nettoyer l'affichage précédent
        if self.image_label:
            self.image_label.destroy()
        
        # Vérifier si c'est un fichier WebM (vidéo)
        if path.lower().endswith('.webm'):
            try:
                # Créer un cadre pour le lecteur vidéo
                self.video_frame = tk.Frame(self.canvas, bg='#1e1e1e', bd=0, highlightthickness=0)
                video_width = self.canvas.winfo_width() - 20
                video_height = video_width * 9 // 16  # Aspect ratio 16:9
                
                self.canvas.create_window((10, 10), window=self.video_frame, anchor='nw', 
                                         width=video_width, 
                                         height=video_height)
                
                # Initialiser le lecteur VLC
                self.instance = vlc.Instance()
                self.video_player = self.instance.media_player_new()
                media = self.instance.media_new(path)
                self.video_player.set_media(media)
                
                # Intégrer VLC dans tkinter
                if os.name == "nt":  # Windows
                    self.video_player.set_hwnd(self.video_frame.winfo_id())
                else:  # Linux, MacOS
                    self.video_player.set_xwindow(self.video_frame.winfo_id())
                    
                # Démarrer la lecture
                self.video_player.play()
                self.is_video_playing = True
                
                # Mettre à jour le scrollregion
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox('all'))
                self.update_status(f"Playing: {os.path.basename(path)}")
            except Exception as e:
                print(f"Error playing video: {e}")
                self.update_status(f"Error: {str(e)}")
                
        else:
            try:
                # C'est une image, utiliser le code existant
                img = Image.open(path)
                
                # Calculer les dimensions pour l'affichage
                display_width = self.canvas.winfo_width() - 20
                if display_width <= 0:  # Éviter la division par zéro
                    display_width = 800
                    
                # Appliquer le zoom
                display_width = int(display_width * self.zoom_level)
                
                # Redimensionner l'image en préservant le ratio
                ratio = display_width / img.width
                display_height = int(img.height * ratio)
                
                # Générer une clé de cache avec le chemin et les dimensions
                cache_key = (path, display_width)
                
                # Vérifier le cache d'abord
                if cache_key not in self.image_cache:
                    resized_img = img.resize((display_width, display_height), Image.LANCZOS)
                    self.image_cache[cache_key] = ImageTk.PhotoImage(resized_img)
                
                self.current_image = self.image_cache[cache_key]
                self.image_label = tk.Label(self.canvas, image=self.current_image, bg='#1e1e1e', bd=0, highlightthickness=0)
                self.canvas.create_window((10, 10), window=self.image_label, anchor='nw')
                
                # Mettre à jour le scrollregion
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox('all'))
                self.update_status(f"Image: {os.path.basename(path)}")
            except Exception as e:
                print(f"Error displaying image: {e}")
                self.update_status(f"Error: {str(e)}")
                
    def on_canvas_configure(self, event):
        if self.image_label:
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def on_mousewheel(self, event):
        """Gestion améliorée du défilement avec la molette de souris"""
        # Détection de Ctrl pour le zoom
        if event.state & 0x4: # Ctrl enfoncé
            if event.delta > 0:
                self.zoom_in(factor=1.1)
            else:
                self.zoom_out(factor=1.1)
        else:
            # Défilement normal
            scroll_speed = 3  # Augmenter pour un défilement plus rapide
            if event.delta > 0:
                self.canvas.yview_scroll(-scroll_speed, "units")
            else:
                self.canvas.yview_scroll(scroll_speed, "units")

    def setup_ui(self):
        # Create main paned window
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # Create left frame with treeview and buttons
        self.left_frame = ttk.Frame(self.main_pane, width=300)
        self.left_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with header
        self.tree_header = ttk.Frame(self.left_frame)
        self.tree_header.pack(fill=tk.X, padx=5, pady=5)
        
        self.header_label = ttk.Label(self.tree_header, text="Library", font=("Arial", 14, "bold"))
        self.header_label.pack(side=tk.LEFT, padx=5)
        
        # Bouton d'ouverture de dossier dans le header
        self.open_button = ttk.Button(self.tree_header, text="📂", width=3, command=self.open_directory)
        self.open_button.pack(side=tk.RIGHT, padx=5)
        
        # Create treeview
        self.tree_frame = ttk.Frame(self.left_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(self.tree_frame, columns=('type', 'path'), show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Add scrollbar to treeview
        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        
        # Button frame for the left panel
        self.left_button_frame = ttk.Frame(self.left_frame)
        self.left_button_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Info label and Read button in left panel
        self.info_label = ttk.Label(self.left_button_frame, text="", font=("Arial", 9))
        self.info_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Read button
        self.read_button = ttk.Button(self.left_button_frame, text="📖 Read", command=self.start_reading, width=8)
        # Le bouton n'est pas empaqueté initialement
        
        # Create canvas frame for manga display
        self.canvas_frame = ttk.Frame(self.main_pane)
        
        # Reader controls frame (at the top of canvas frame)
        self.reader_controls = ttk.Frame(self.canvas_frame)
        self.reader_controls.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)
        
        # Zoom controls
        self.zoom_frame = ttk.Frame(self.reader_controls)
        self.zoom_frame.pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_btn = ttk.Button(self.zoom_frame, text="🔍-", width=3, command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_reset_btn = ttk.Button(self.zoom_frame, text="100%", width=5, command=self.reset_zoom)
        self.zoom_reset_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_in_btn = ttk.Button(self.zoom_frame, text="🔍+", width=3, command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        # Fullscreen button
        self.fullscreen_btn = ttk.Button(self.reader_controls, text="⛶", width=3, command=self.toggle_fullscreen)
        self.fullscreen_btn.pack(side=tk.RIGHT, padx=5)
        
        # Canvas for manga display
        self.canvas = tk.Canvas(self.canvas_frame, bg='#1e1e1e', bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Barre d'état en bas
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", anchor=tk.W, relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)

        # Add frames to paned window
        self.main_pane.add(self.left_frame, weight=1)
        self.main_pane.add(self.canvas_frame, weight=3)

        # Add menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        
        # Menu Fichier
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Directory", command=self.open_directory)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Menu Affichage
        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Zoom In", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        self.view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Fullscreen", command=self.toggle_fullscreen)

    def start_reading(self, force_reload=False, custom_width=None):
        """Commence la lecture des images du dossier sélectionné en mode comics"""
        if not self.images:
            print("No images to display")
            self.update_status("No images to display")
            return
            
        # Si on a déjà chargé les images et qu'on ne force pas le rechargement, on ne fait rien
        if hasattr(self, 'comics_frame') and not force_reload:
            return
            
        # Nettoyer l'affichage précédent
        if self.image_label:
            self.image_label.destroy()
            
        # Arrêter une vidéo en cours si nécessaire
        if self.is_video_playing and self.video_player:
            self.video_player.stop()
            self.is_video_playing = False
        
        print(f"Loading {len(self.images)} images in manhwa mode...")
        self.update_status(f"Loading {len(self.images)} images...")
        
        # Calculer la largeur disponible
        if custom_width:
            available_width = custom_width
        else:
            available_width = self.canvas.winfo_width() - 20
            if available_width <= 0:
                available_width = 800
                
        # Créer ou réutiliser le frame pour les images
        if hasattr(self, 'comics_frame') and force_reload:
            # Déjà créé, on réutilise
            pass
        else:
            # Créer un nouveau frame
            self.comics_frame = tk.Frame(self.canvas, bg='#1e1e1e', bd=0, highlightthickness=0)
            self.canvas.create_window((0, 0), window=self.comics_frame, anchor='nw')
            
        # Charger et afficher toutes les images verticalement
        for index, img_path in enumerate(self.images):
            try:
                if img_path.lower().endswith('.webm'):
                    # Pour les vidéos, afficher juste un message indiquant qu'il s'agit d'une vidéo
                    video_label = tk.Label(self.comics_frame, text=f"Video: {os.path.basename(img_path)}\nClick to play", 
                                               bg='#1e1e1e', fg='white', font=('Arial', 12), pady=5)
                    video_label.pack(fill=tk.X, padx=0, pady=0)
                    video_label.bind("<Button-1>", lambda e, path=img_path: self.display_image(path))
                else:
                    # Charger et afficher l'image
                    img = Image.open(img_path)
                    
                    # Redimensionner l'image en préservant le ratio
                    ratio = available_width / img.width
                    display_height = int(img.height * ratio)
                    
                    # Redimensionner l'image
                    resized_img = img.resize((available_width, display_height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_img)
                    
                    # Stocker la référence à l'image (sinon elle sera collectée par le garbage collector)
                    setattr(self, f"photo_{index}", photo)
                    
                    # Créer un label pour afficher l'image sans aucun padding
                    img_label = tk.Label(self.comics_frame, image=photo, bg='#1e1e1e', bd=0, highlightthickness=0)
                    img_label.pack(pady=0, padx=0, ipady=0, ipadx=0)
                    
                    print(f"Image loaded: {os.path.basename(img_path)}")
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                # Afficher un message d'erreur à la place de l'image
                error_label = tk.Label(self.comics_frame, text=f"Loading error: {os.path.basename(img_path)}", 
                                           bg='#1e1e1e', fg='red', pady=5)
                error_label.pack(fill=tk.X, pady=0, padx=0)
        
        # Mettre à jour la région de défilement du canvas
        self.comics_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
        # Revenir au début du canvas
        self.canvas.yview_moveto(0)
        
        print("Manhwa mode initialized - use mouse wheel or scrollbar to navigate")
        self.update_status(f"Reading {len(self.images)} images - Zoom: {self.zoom_level:.2f}x")

    def prev_image(self, event=None):
        """Navigate to the previous image"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_image(self.images[self.current_image_index])
            
    def next_image(self, event=None):
        """Navigate to the next image"""
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.display_image(self.images[self.current_image_index])

    def populate_tree(self, directory):
        """Populate the tree view with directory contents"""
        self.tree.delete(*self.tree.get_children())
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                self.tree.insert('', 'end', text=item, values=('directory', full_path))
            elif item.lower().endswith(tuple(self.supported_extensions)):
                self.images.append(full_path)
                self.tree.insert('', 'end', text=item, values=('image', full_path))

    def open_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.populate_tree(directory)
            self.update_status(f"Directory opened: {os.path.basename(directory)}")

    def on_tree_select(self, event):
        item = self.tree.focus()
        item_values = self.tree.item(item, 'values')
        
        if item_values:
            if item_values[0] == 'image':
                path = item_values[1]
                self.display_image(path)
                # Trouver l'index de cette image dans la liste
                if path in self.images:
                    self.current_image_index = self.images.index(path)
            elif item_values[0] == 'directory':
                # Si c'est un dossier, on l'ouvre dans l'arborescence
                dir_path = item_values[1]
                try:
                    # Effacer les enfants existants
                    self.tree.delete(*self.tree.get_children(item))
                    # Ajouter les nouveaux éléments
                    has_media_files = False
                    for file_item in os.listdir(dir_path):
                        full_path = os.path.join(dir_path, file_item)
                        if os.path.isdir(full_path):
                            self.tree.insert(item, 'end', text=file_item, values=('directory', full_path))
                        elif file_item.lower().endswith(tuple(self.supported_extensions)):
                            has_media_files = True
                            self.tree.insert(item, 'end', text=file_item, values=('image', full_path))
                    
                    # Vérifier s'il y a des images/vidéos dans ce dossier
                    media_count = self._gather_directory_images(item)
                    
                    # Mettre à jour l'étiquette d'information
                    if media_count > 0:
                        # Déballer le bouton et afficher les informations
                        self.info_label.config(text=f"{media_count} media files")
                        # Retirer le bouton s'il est déjà affiché
                        self.read_button.pack_forget()
                        # Afficher le bouton
                        self.read_button.pack(side=tk.LEFT, padx=5, pady=5)
                        print(f"Read button displayed - {media_count} media files")
                        self.update_status(f"{media_count} media files found in {os.path.basename(dir_path)}")
                    else:
                        self.info_label.config(text="No media files")
                        self.read_button.pack_forget()
                        print("Read button hidden - no media files")
                        self.update_status("No media files found")
                        
                except Exception as e:
                    print(f"Error opening directory: {e}")
                    self.info_label.config(text=f"Error: {str(e)}")
                    self.update_status(f"Error: {str(e)}")

    def _gather_directory_images(self, item):
        """Collecte toutes les images/vidéos d'un dossier"""
        self.images = []
        if not item:
            return 0
            
        try:
            dir_path = self.tree.item(item, 'values')[1]  # Le chemin est à l'index 1
            print(f"Searching for media in: {dir_path}")
            
            if not os.path.exists(dir_path):
                print(f"Path does not exist: {dir_path}")
                return 0
                
            # Collecter tous les fichiers média du répertoire
            for file in os.listdir(dir_path):
                full_path = os.path.join(dir_path, file)
                if os.path.isfile(full_path) and file.lower().endswith(tuple(self.supported_extensions)):
                    self.images.append(full_path)
                    print(f"Media found: {file}")
            
            # Trier les images numériquement si possible
            self.images.sort(key=lambda x: self._natural_sort_key(os.path.basename(x)))
            
            # Retourner le nombre d'images trouvées
            return len(self.images)
        except Exception as e:
            print(f"Error reading directory: {e}")
            return 0

    def _natural_sort_key(self, s):
        """Fonction pour trier naturellement les noms de fichiers (01.jpg vient avant 10.jpg)"""
        import re
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern colors
        bg_color = '#1e1e1e'  # Dark gray
        fg_color = '#ffffff'  # White
        accent_color = '#007acc'  # Blue accent
        
        # Style configuration
        style.configure('.', background=bg_color, foreground=fg_color)
        style.configure('Treeview', background=bg_color, foreground=fg_color, fieldbackground=bg_color)
        style.configure('Treeview.Heading', background=accent_color, foreground=fg_color)
        style.configure('TButton', background=bg_color, foreground=fg_color)
        style.map('TButton', background=[('active', accent_color)])
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TPanedwindow', background=bg_color)
        
        # Status bar style
        style.configure('TLabel', background='#252525', foreground='#cccccc')
        
        # Canvas
        self.canvas.configure(bg=bg_color, bd=0, highlightthickness=0)
        
        # Root configuration
        self.root.configure(bg=bg_color)
        
        # Apply dark theme to menus (tkinter standard)
        self.menu.configure(bg=bg_color, fg=fg_color, activebackground=accent_color, activeforeground=fg_color)
        for menu in [self.file_menu, self.view_menu]:
            menu.configure(bg=bg_color, fg=fg_color, activebackground=accent_color, activeforeground=fg_color)
            
if __name__ == "__main__":
    root = tk.Tk()
    app = MangaReader(root)
    root.mainloop()