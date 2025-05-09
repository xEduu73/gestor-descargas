import os
import json
import requests
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
from PIL import Image, ImageTk
import threading
from io import BytesIO
import random

# Configuración
APP_NAME = "Super Gestor de Descargas 🚀"
APP_THEME = "cosmo"  # Cambiado a tema claro por defecto
APP_VERSION = "1.2.0"
STATS_FILE = "download_stats.json"
FAVORITES_FILE = "favorites.json"

# Lista de programas ampliada
PROGRAMAS = [
    {
        "nombre": "WinRAR",
        "descripcion": "Compresor de archivos (RAR, ZIP).",
        "url": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-623.exe",
        "comando_instalacion": "/S",
        "version": "6.23",
        "categoria": "Utilidades",
        "popularidad_inicial": 15
    },
    {
        "nombre": "VLC Media Player",
        "descripcion": "Reproductor multimedia para cualquier formato.",
        "url": "https://get.videolan.org/vlc/3.0.18/win64/vlc-3.0.18-win64.exe",
        "comando_instalacion": "/S",
        "version": "3.0.18",
        "categoria": "Multimedia",
        "popularidad_inicial": 18
    },
    {
        "nombre": "Google Chrome",
        "descripcion": "Navegador web rápido y seguro.",
        "url": "https://dl.google.com/chrome/install/chrome_installer.exe",
        "comando_instalacion": "--silent --install",
        "version": "118.0.5993.118",
        "categoria": "Navegadores",
        "popularidad_inicial": 20
    },
    {
        "nombre": "Mozilla Firefox",
        "descripcion": "Navegador web centrado en privacidad.",
        "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=es-ES",
        "comando_instalacion": "-ms",
        "version": "119.0",
        "categoria": "Navegadores",
        "popularidad_inicial": 14
    },
    {
        "nombre": "7-Zip",
        "descripcion": "Compresor gratuito de alta relación de compresión.",
        "url": "https://www.7-zip.org/a/7z2301-x64.exe",
        "comando_instalacion": "/S",
        "version": "23.01",
        "categoria": "Utilidades",
        "popularidad_inicial": 12
    },
    {
        "nombre": "Notepad++",
        "descripcion": "Editor de texto avanzado para código.",
        "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.5.6/npp.8.5.6.Installer.x64.exe",
        "comando_instalacion": "/S",
        "version": "8.5.6",
        "categoria": "Desarrollo",
        "popularidad_inicial": 10
    },
    {
        "nombre": "Spotify",
        "descripcion": "Servicio de streaming de música.",
        "url": "https://download.scdn.co/SpotifySetup.exe",
        "comando_instalacion": "/silent",
        "version": "1.2.13",
        "categoria": "Multimedia",
        "popularidad_inicial": 16
    },
    {
        "nombre": "Adobe Reader",
        "descripcion": "Lector de documentos PDF.",
        "url": "https://ardownload2.adobe.com/pub/adobe/reader/win/AcrobatDC/2300320284/AcroRdrDC2300320284_es_ES.exe",
        "comando_instalacion": "/sAll /rs /msi /norestart /quiet",
        "version": "23.003.20284",
        "categoria": "Ofimática",
        "popularidad_inicial": 13
    },
    {
        "nombre": "Microsoft Teams",
        "descripcion": "Plataforma de comunicación y colaboración.",
        "url": "https://teams.microsoft.com/downloads/desktopurl?env=production&plat=windows&arch=x64&download=true",
        "comando_instalacion": "-s",
        "version": "1.6.0",
        "categoria": "Comunicación",
        "popularidad_inicial": 11
    },
    {
        "nombre": "WhatsApp Desktop",
        "descripcion": "Cliente de mensajería para Windows.",
        "url": "https://web.whatsapp.com/desktop/windows/release/x64/WhatsAppSetup.exe",
        "comando_instalacion": "--silent",
        "version": "2.2326.12",
        "categoria": "Comunicación",
        "popularidad_inicial": 17
    },
    {
        "nombre": "Discord",
        "descripcion": "Plataforma de chat y voz para comunidades.",
        "url": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x86",
        "comando_instalacion": "-s",
        "version": "1.0.9016",
        "categoria": "Comunicación",
        "popularidad_inicial": 15
    },
    {
        "nombre": "Zoom",
        "descripcion": "Software para videoconferencias.",
        "url": "https://zoom.us/client/latest/ZoomInstallerFull.msi",
        "comando_instalacion": "/quiet /qn /norestart",
        "version": "5.15.5",
        "categoria": "Comunicación",
        "popularidad_inicial": 14
    }
]

# Corregir la clave "Todas las Apps" para tener el mismo espaciado
CATEGORIAS = {
    "🏆 Top Programas": ["WinRAR", "VLC Media Player", "Google Chrome", "Mozilla Firefox", "7-Zip"],
    "🛠️Todas las Apps": [p["nombre"] for p in PROGRAMAS],  # Quitado espacio extra
    "🌐 Navegadores": [p["nombre"] for p in PROGRAMAS if p["categoria"] == "Navegadores"],
    "📱 Comunicación": [p["nombre"] for p in PROGRAMAS if p["categoria"] == "Comunicación"],
    "🎵 Multimedia": [p["nombre"] for p in PROGRAMAS if p["categoria"] == "Multimedia"],
    "🔧 Utilidades": [p["nombre"] for p in PROGRAMAS if p["categoria"] == "Utilidades"],
    "💻 Desarrollo": [p["nombre"] for p in PROGRAMAS if p["categoria"] == "Desarrollo"],
    "📄 Ofimática": [p["nombre"] for p in PROGRAMAS if p["categoria"] == "Ofimática"]
}

class GestorDescargasApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.style = Style(theme=APP_THEME)  # Inicia con tema claro
        self.root.geometry("1000x750")
        
        # Variables
        self.progress = tk.DoubleVar()
        self.search_text = tk.StringVar()
        self.theme_mode = tk.BooleanVar(value=False)  # Inicia en modo día (False = día, True = noche)
        self.current_category = "🛠️Todas las Apps"  # Actualizado sin espacio
        
        # Cargar datos
        self.stats = self.load_stats()
        self.favorites = self.load_favorites()
        
        # Definir colores para estrellas
        self.definir_colores_estrellas()
        
        # Interfaz
        self.setup_ui()
        
    def definir_colores_estrellas(self):
        """Define los colores para las estrellas de popularidad"""
        # Crear etiquetas de colores para las estrellas
        self.etiquetas_estrellas = {
            1: "estrella1",  # Nivel más bajo
            2: "estrella2",
            3: "estrella3",
            4: "estrella4",
            5: "estrella5"   # Nivel más alto
        }
    
    def load_stats(self):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            # Si no hay archivo de estadísticas, crear uno con datos iniciales
            stats_iniciales = {}
            for programa in PROGRAMAS:
                # Asignar la popularidad inicial definida para cada programa
                stats_iniciales[programa["nombre"]] = programa.get("popularidad_inicial", 0)
            return stats_iniciales
    
    def save_stats(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f)
    
    def load_favorites(self):
        try:
            with open(FAVORITES_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    
    def save_favorites(self):
        with open(FAVORITES_FILE, "w") as f:
            json.dump(self.favorites, f)
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar estilos para las estrellas con colores más amigables
        self.style.configure("estrella1.TLabel", foreground="#9E9E9E")  # Gris
        self.style.configure("estrella2.TLabel", foreground="#42A5F5")  # Azul claro
        self.style.configure("estrella3.TLabel", foreground="#7E57C2")  # Púrpura
        self.style.configure("estrella4.TLabel", foreground="#26A69A")  # Verde azulado
        self.style.configure("estrella5.TLabel", foreground="#66BB6A")  # Verde
        
        # Barra superior
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Botón de tema
        ttk.Checkbutton(
            top_frame,
            text="Modo Noche",
            variable=self.theme_mode,
            command=self.toggle_theme,
            style="round-toggle"
        ).pack(side=tk.RIGHT, padx=5)
        
        # Barra de búsqueda
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_text)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_programs())
        
        # Panel lateral
        sidebar_frame = ttk.Frame(main_frame, width=200, style="secondary.TFrame")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(
            sidebar_frame,
            text="Categorías",
            style="h4.TLabel"
        ).pack(pady=10)
        
        # Botón de favoritos
        ttk.Button(
            sidebar_frame,
            text="⭐ Mis Favoritos",
            command=self.filter_by_favorites,
            style="warning.outline.TButton",
            width=20
        ).pack(pady=3, fill=tk.X)
        
        # Botones de categorías
        for categoria in CATEGORIAS:
            btn = ttk.Button(
                sidebar_frame,
                text=categoria,
                command=lambda c=categoria: self.filter_by_category(c),
                style="outline.TButton",
                width=20
            )
            btn.pack(pady=3, fill=tk.X)
        
        # Lista de programas
        self.list_frame = ttk.Frame(main_frame)
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("Nombre", "Descripción", "Versión", "Popularidad"),
            show="headings",
            selectmode="extended"
        )
        
        # Configurar columnas
        for col in ("Nombre", "Descripción", "Versión", "Popularidad"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col == "Nombre" else 100, 
                            anchor="w" if col == "Descripción" else "center")
        
        # Menú contextual
        self.setup_context_menu()
        
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress,
            maximum=100,
            style="success.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="⬇️ Instalar seleccionados",
            style="success.TButton",
            command=self.start_installation
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📊 Estadísticas",
            style="info.TButton",
            command=self.show_stats
        ).pack(side=tk.RIGHT, padx=5)
        
        # Barra de estado
        self.status_var = tk.StringVar(value=f"Versión {APP_VERSION} | Listo")
        ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        ).pack(fill=tk.X)
        
        # Configurar los colores de las etiquetas en el Treeview (con nuevos colores)
        self.tree.tag_configure("estrella1", foreground="#9E9E9E")  # Gris
        self.tree.tag_configure("estrella2", foreground="#42A5F5")  # Azul claro
        self.tree.tag_configure("estrella3", foreground="#7E57C2")  # Púrpura
        self.tree.tag_configure("estrella4", foreground="#26A69A")  # Verde azulado
        self.tree.tag_configure("estrella5", foreground="#66BB6A")  # Verde
        
        # Cargar todos los programas al inicio
        self.filter_by_category("🛠️Todas las Apps")  # Actualizado sin espacio
    
    def setup_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Instalar", command=self.start_installation)
        self.context_menu.add_command(label="Añadir/Quitar favorito", command=self.toggle_favorite_selected)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_nivel_popularidad(self, nombre):
        """Obtiene el nivel de popularidad (1-5) para un programa"""
        popularidad = self.stats.get(nombre, 0)
        
        if popularidad >= 16:
            return 5  # Muy popular
        elif popularidad >= 12:
            return 4
        elif popularidad >= 8:
            return 3
        elif popularidad >= 4:
            return 2
        else:
            return 1  # Poco popular
    
    def get_estrella_label(self, nombre):
        """Obtiene la etiqueta de estilo para las estrellas según popularidad"""
        nivel = self.get_nivel_popularidad(nombre)
        return self.etiquetas_estrellas[nivel]
    
    def get_estrellas_popularidad(self, nombre):
        """Devuelve la cadena de estrellas y su nivel de popularidad"""
        nivel = self.get_nivel_popularidad(nombre)
        
        if nivel == 5:
            return "★★★★★"  # 5 estrellas
        elif nivel == 4:
            return "★★★★☆"  # 4 estrellas
        elif nivel == 3:
            return "★★★☆☆"  # 3 estrellas
        elif nivel == 2:
            return "★★☆☆☆"  # 2 estrellas
        else:
            return "★☆☆☆☆"  # 1 estrella
    
    def filter_programs(self):
        query = self.search_text.get().lower()
        
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Añadir programas que coincidan
        for programa in PROGRAMAS:
            nombre = programa["nombre"]
            descripcion = programa["descripcion"]
            version = programa.get("version", "N/A")
            
            if (query in nombre.lower() or 
                query in descripcion.lower() or 
                query in str(version).lower()):
                
                # Obtener estrellas y estilo según popularidad
                estrellas = self.get_estrellas_popularidad(nombre)
                
                # Marcar favoritos
                nombre_display = f"⭐ {nombre}" if nombre in self.favorites else nombre
                
                item_id = self.tree.insert("", "end", values=(
                    nombre_display,
                    descripcion,
                    version,
                    estrellas
                ))
                
                # Aplicar color a las estrellas usando etiquetas
                etiqueta = self.get_estrella_label(nombre)
                self.tree.item(item_id, tags=(etiqueta,))
        
        self.update_status(f"Búsqueda: {query}" if query else "Listo")
    
    def filter_by_category(self, category):
        self.current_category = category
        programas_filtrados = CATEGORIAS[category]
        
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Añadir solo programas de la categoría
        for programa in PROGRAMAS:
            if programa["nombre"] in programas_filtrados:
                nombre = programa["nombre"]
                
                # Obtener estrellas según popularidad
                estrellas = self.get_estrellas_popularidad(nombre)
                
                # Marcar favoritos
                nombre_display = f"⭐ {nombre}" if nombre in self.favorites else nombre
                
                item_id = self.tree.insert("", "end", values=(
                    nombre_display,
                    programa["descripcion"],
                    programa.get("version", "N/A"),
                    estrellas
                ))
                
                # Aplicar color a las estrellas usando etiquetas
                etiqueta = self.get_estrella_label(nombre)
                self.tree.item(item_id, tags=(etiqueta,))
                
        self.update_status(f"Mostrando: {category}")
    
    def filter_by_favorites(self):
        self.current_category = "⭐ Mis Favoritos"
        
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Añadir solo favoritos
        for programa in PROGRAMAS:
            if programa["nombre"] in self.favorites:
                nombre = programa["nombre"]
                
                # Obtener estrellas según popularidad
                estrellas = self.get_estrellas_popularidad(nombre)
                
                item_id = self.tree.insert("", "end", values=(
                    f"⭐ {nombre}",
                    programa["descripcion"],
                    programa.get("version", "N/A"),
                    estrellas
                ))
                
                # Aplicar color a las estrellas usando etiquetas
                etiqueta = self.get_estrella_label(nombre)
                self.tree.item(item_id, tags=(etiqueta,))
        
        self.update_status("Mostrando: Favoritos")
    
    def toggle_favorite_selected(self):
        if not (selected := self.tree.selection()):
            messagebox.showwarning("Advertencia", "Selecciona al menos un programa")
            return
        
        for item_id in selected:
            item_nombre = self.tree.item(item_id)["values"][0]
            # Quitar prefijo si es un favorito
            if item_nombre.startswith("⭐ "):
                item_nombre = item_nombre[2:].strip()
            
            if item_nombre in self.favorites:
                self.favorites.remove(item_nombre)
                self.update_status(f"{item_nombre} quitado de favoritos")
            else:
                self.favorites.append(item_nombre)
                self.update_status(f"{item_nombre} añadido a favoritos")
        
        # Guardar y actualizar vista
        self.save_favorites()
        
        # Refrescar vista actual
        if self.current_category == "⭐ Mis Favoritos":
            self.filter_by_favorites()
        else:
            self.filter_by_category(self.current_category)
    
    def start_installation(self):
        if not (selected := self.tree.selection()):
            messagebox.showwarning("Advertencia", "Selecciona al menos un programa")
            return
        
        threading.Thread(target=self.install_programs, args=(selected,), daemon=True).start()
    
    def install_programs(self, selected_items):
        total = len(selected_items)
        success_count = 0
        failed_count = 0
        
        for i, item_id in enumerate(selected_items, 1):
            try:
                # Obtener nombre sin prefijo si es un favorito
                item_nombre = self.tree.item(item_id)["values"][0]
                if item_nombre.startswith("⭐ "):
                    item_nombre = item_nombre[2:].strip()
                
                programa = next(p for p in PROGRAMAS if p["nombre"] == item_nombre)
                nombre = programa["nombre"]
                
                self.update_status(f"Descargando {nombre}...")
                self.progress.set((i-1)/total * 100)
                
                # Descarga
                response = requests.get(programa["url"], stream=True, timeout=30)
                file_path = os.path.basename(programa["url"])
                total_size = int(response.headers.get("content-length", 0))
                
                with open(file_path, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Actualizar progreso
                            if total_size > 0:
                                progress = (i-1 + downloaded/total_size)/total * 100
                                self.progress.set(progress)
                
                # Instalación
                self.update_status(f"Instalando {nombre}...")
                subprocess.run(
                    [file_path, programa["comando_instalacion"]],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300  # 5 minutos máx.
                )
                
                # Actualizar estadísticas - Aumentar popularidad en cada instalación
                self.stats[nombre] = self.stats.get(nombre, 0) + 1
                self.save_stats()
                
                # Limpiar archivo
                os.remove(file_path)
                
                success_count += 1
                self.update_status(f"{nombre} instalado correctamente")
                
            except Exception as e:
                failed_count += 1
                self.update_status(f"Error con {nombre}: {str(e)}", error=True)
        
        # Finalizar
        self.progress.set(100)
        self.update_status(f"Instalación completada: {success_count} éxitos, {failed_count} errores")
        
        # Actualizar lista
        if self.current_category == "⭐ Mis Favoritos":
            self.filter_by_favorites()
        else:
            self.filter_by_category(self.current_category)
        
        # Mostrar mensaje final
        messagebox.showinfo("Instalación finalizada", f"{success_count} programas instalados correctamente\n{failed_count} errores")
    
    def show_stats(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas de instalación")
        stats_window.geometry("500x350")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        ttk.Label(stats_window, text="📊 Programas más instalados", style="h2.TLabel").pack(pady=10)
        
        frame = ttk.Frame(stats_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Encabezados
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=5)
        ttk.Label(header, text="Programa", width=25, font=("", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Popularidad", width=15, font=("", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Puntos", width=10, font=("", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Mostrar lista de programas ordenados por popularidad
        for nombre, popularidad in sorted(self.stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            
            # Nombre del programa
            ttk.Label(row, text=nombre, width=25).pack(side=tk.LEFT, padx=5)
            
            # Estrellas coloreadas
            estrellas = self.get_estrellas_popularidad(nombre)
            nivel = self.get_nivel_popularidad(nombre)
            estrella_label = ttk.Label(
                row, 
                text=estrellas, 
                width=15,
                style=f"{self.etiquetas_estrellas[nivel]}.TLabel"
            )
            estrella_label.pack(side=tk.LEFT, padx=5)
            
            # Puntuación numérica
            ttk.Label(row, text=f"{popularidad} pts", width=10).pack(side=tk.LEFT, padx=5)
    
    def toggle_theme(self):
        self.style.theme_use("darkly" if self.theme_mode.get() else "cosmo")
        
        # Actualizar los colores de las estrellas según el tema
        if self.theme_mode.get():  # Tema oscuro
            self.style.configure("estrella1.TLabel", foreground="#9E9E9E")  # Gris
            self.style.configure("estrella2.TLabel", foreground="#42A5F5")  # Azul claro
            self.style.configure("estrella3.TLabel", foreground="#7E57C2")  # Púrpura
            self.style.configure("estrella4.TLabel", foreground="#26A69A")  # Verde azulado
            self.style.configure("estrella5.TLabel", foreground="#66BB6A")  # Verde
        else:  # Tema claro - mantener colores visibles en modo claro
            self.style.configure("estrella1.TLabel", foreground="#757575")  # Gris oscuro
            self.style.configure("estrella2.TLabel", foreground="#1976D2")  # Azul más oscuro
            self.style.configure("estrella3.TLabel", foreground="#5E35B1")  # Púrpura más oscuro
            self.style.configure("estrella4.TLabel", foreground="#00897B")  # Verde azulado más oscuro
            self.style.configure("estrella5.TLabel", foreground="#388E3C")  # Verde más oscuro
        
        # Actualizar colores en el TreeView también
        if self.theme_mode.get():  # Tema oscuro
            self.tree.tag_configure("estrella1", foreground="#9E9E9E")  # Gris
            self.tree.tag_configure("estrella2", foreground="#42A5F5")  # Azul claro
            self.tree.tag_configure("estrella3", foreground="#7E57C2")  # Púrpura
            self.tree.tag_configure("estrella4", foreground="#26A69A")  # Verde azulado
            self.tree.tag_configure("estrella5", foreground="#66BB6A")  # Verde
        else:  # Tema claro
            self.tree.tag_configure("estrella1", foreground="#757575")  # Gris oscuro
            self.tree.tag_configure("estrella2", foreground="#1976D2")  # Azul más oscuro
            self.tree.tag_configure("estrella3", foreground="#5E35B1")  # Púrpura más oscuro
            self.tree.tag_configure("estrella4", foreground="#00897B")  # Verde azulado más oscuro
            self.tree.tag_configure("estrella5", foreground="#388E3C")  # Verde más oscuro
        
        self.update_status(f"Tema cambiado a {'Noche' if self.theme_mode.get() else 'Día'}")
        
        # Actualizar vista actual para aplicar nuevos colores
        if self.current_category == "⭐ Mis Favoritos":
            self.filter_by_favorites()
        else:
            self.filter_by_category(self.current_category)
    
    def update_status(self, message, error=False):
        self.status_var.set(message)
        if error:
            self.root.bell()
    
    def check_for_updates(self):
        """Función para verificar actualizaciones (simulada)"""
        # En un caso real, consultaríamos un servidor o API
        messagebox.showinfo("Verificación de actualizaciones", 
                           "La aplicación está actualizada a la versión más reciente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GestorDescargasApp(root)
    root.mainloop()