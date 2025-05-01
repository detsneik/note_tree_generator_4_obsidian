import os
import re
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import zipfile
from datetime import datetime
import shutil

class NoteTreeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Árbol de Notas")
        
        # Configurar el tema y estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Usar un tema más moderno
        
        # Configurar estilos personalizados
        self.style.configure('Title.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'))
        self.style.configure('Action.TButton', padding=5)
        self.style.configure('Copy.TButton', padding=5, background='#4CAF50')
        self.style.configure('Zip.TButton', padding=5, background='#2196F3')
        
        # Variables
        self.input_dir = tk.StringVar()
        self.selected_note = tk.StringVar()
        self.md_files = []
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)
        self.all_files = []  # Lista completa de archivos
        self.sort_order = tk.StringVar(value="name")  # Inicializar con ordenamiento por nombre
        
        # Crear la interfaz
        self.create_widgets()
        
        # Configurar el comportamiento responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Centrar la ventana
        self.center_window(900, 700)
        
    def center_window(self, width, height):
        """Centra la ventana en la pantalla"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Título principal
        title_label = ttk.Label(main_frame, text="Generador de Árbol de Notas", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame para la sección de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Selección de Carpeta", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Carpeta de entrada
        ttk.Label(input_frame, text="Carpeta de notas:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        input_entry = ttk.Entry(input_frame, textvariable=self.input_dir)
        input_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(input_frame, text="Buscar", command=self.browse_input_dir, style='Action.TButton').grid(row=0, column=2)
        
        # Frame para la lista y vista previa
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar pesos de columnas para centrar
        content_frame.grid_columnconfigure(0, weight=2)  # Espacio izquierdo
        content_frame.grid_columnconfigure(1, weight=3)  # Lista de archivos
        content_frame.grid_columnconfigure(2, weight=5)  # Vista previa
        
        # Frame izquierdo para la lista de archivos (ahora en la columna 1)
        list_frame = ttk.LabelFrame(content_frame, text="Archivos Disponibles", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # Barra de búsqueda con mejor alineamiento
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Contenedor para la barra de búsqueda
        search_container = ttk.Frame(search_frame, padding=(0, 0, 0, 5))
        search_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        search_container.grid_columnconfigure(1, weight=1)
        
        # Icono de búsqueda y entrada alineados
        ttk.Label(search_container, text="🔍", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        search_entry = ttk.Entry(search_container, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Lista de archivos con scrollbar
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, activestyle='dotbox', width=40)
        self.file_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select_file)
        
        # Frame derecho para la vista previa
        preview_frame = ttk.LabelFrame(content_frame, text="Vista Previa", padding="10")
        preview_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)
        
        # Vista previa con scroll
        self.preview = ScrolledText(preview_frame, wrap=tk.WORD)
        self.preview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para botones de acción
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        
        # Botón de copiar centrado
        copy_button = ttk.Button(action_frame, text="Copiar al Portapapeles", 
                               command=self.copy_to_clipboard, style='Copy.TButton')
        copy_button.grid(row=0, column=0, padx=5, pady=10)
        
        # Botón para crear ZIP
        zip_button = ttk.Button(action_frame, text="Crear ZIP con notas", 
                              command=self.create_notes_zip, style='Zip.TButton')
        zip_button.grid(row=0, column=1, padx=5, pady=10)
        
    def browse_input_dir(self):
        """Abre el diálogo para seleccionar la carpeta de entrada"""
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.set(directory)
            self.update_file_list()
    
    def copy_to_clipboard(self):
        """Copia el contenido del árbol al portapapeles"""
        if not self.selected_note.get():
            messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo primero")
            return
        
        content = self.preview.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Éxito", "Contenido copiado al portapapeles")
        else:
            messagebox.showwarning("Advertencia", "No hay contenido para copiar")
            
    def filter_files(self, *args):
        """Filtra los archivos basado en el texto de búsqueda"""
        search_term = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)
        
        for file in self.all_files:
            if search_term in file.lower():
                self.file_listbox.insert(tk.END, file)
                
    def update_file_list(self):
        """Actualiza la lista de archivos markdown con ordenamiento"""
        self.file_listbox.delete(0, tk.END)
        try:
            files = []
            for f in os.listdir(self.input_dir.get()):
                if f.endswith('.md'):
                    file_path = os.path.join(self.input_dir.get(), f)
                    creation_time = os.path.getctime(file_path)
                    name = f[:-3]  # Eliminar la extensión .md
                    files.append((name, creation_time))

            # Ordenar primero alfabéticamente
            files.sort(key=lambda x: x[0].lower())

            # Si se seleccionó otro tipo de ordenamiento, aplicarlo
            if self.sort_order.get() == "date_asc":
                files.sort(key=lambda x: x[1])  # Ordenar por fecha ascendente
            elif self.sort_order.get() == "date_desc":
                files.sort(key=lambda x: x[1], reverse=True)  # Ordenar por fecha descendente

            # Actualizar la lista completa
            self.all_files = [f[0] for f in files]
            self.filter_files()  # Aplicar el filtro actual

        except Exception as e:
            messagebox.showerror("Error", f"Error al leer la carpeta: {str(e)}")
            
    def on_select_file(self, event):
        """Maneja la selección de un archivo de la lista"""
        if self.file_listbox.curselection():
            self.selected_note.set(self.file_listbox.get(self.file_listbox.curselection()))
            self.update_preview()
            
    def update_preview(self):
        """Actualiza la vista previa del árbol"""
        if not self.selected_note.get():
            return
            
        try:
            graph = self.build_note_graph(self.input_dir.get())
            tree_content = "# Estructura de notas\n\n"
            tree_content += self.write_note_tree(graph, self.selected_note.get())
            
            self.preview.delete('1.0', tk.END)
            self.preview.insert('1.0', tree_content)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar vista previa: {str(e)}")
            
    def read_markdown_links(self, file_path):
        """Lee los enlaces de un archivo markdown manteniendo el orden original"""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Encuentra todos los enlaces [[...]] y mantén el orden
                matches = re.finditer(r'\[\[(.*?)\]\]', content)
                for match in matches:
                    link = match.group(1)
                    if link not in links:  # Evitar duplicados pero mantener el primer orden de aparición
                        links.append(link)
        except Exception as e:
            print(f"Error al leer el archivo {file_path}: {str(e)}")
        return links
        
    def build_note_graph(self, notes_dir):
        """Construye el grafo de conexiones entre notas manteniendo el orden original"""
        graph = defaultdict(list)
        md_files = [f for f in os.listdir(notes_dir) if f.endswith('.md')]
        
        for md_file in md_files:
            file_path = os.path.join(notes_dir, md_file)
            note_name = os.path.splitext(md_file)[0]
            links = self.read_markdown_links(file_path)
            if links:
                graph[note_name] = links  # Asignar la lista directamente para mantener el orden
        
        return graph
        
    def write_note_tree(self, graph, root_note, level=0, visited=None, counters=None):
        """Escribe el árbol de notas con la numeración correcta, manteniendo el orden original"""
        if visited is None:
            visited = set()
        if counters is None:
            counters = {}
        
        if root_note in visited:
            return ""
        
        visited.add(root_note)
        indent = '\t' * level
        
        # Si este nivel no tiene contador, inicializarlo
        if level not in counters:
            counters[level] = 0
        
        # Incrementar el contador para este nivel
        counters[level] += 1
        
        content = f"{indent}{counters[level]}. [[{root_note}]]\n"
        
        # Usar los hijos en el orden original del grafo
        children = graph[root_note]
        
        # Antes de procesar los hijos, eliminar los contadores de niveles más profundos
        levels_to_remove = [k for k in counters.keys() if k > level]
        for k in levels_to_remove:
            del counters[k]
        
        # Procesar cada hijo en el orden original
        for child in children:
            content += self.write_note_tree(graph, child, level + 1, visited, counters)
        
        return content

    def create_notes_zip(self):
        """Crea un archivo ZIP con todas las notas relacionadas"""
        if not self.selected_note.get():
            messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo primero")
            return

        try:
            # Obtener la ubicación donde guardar el archivo ZIP
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{self.selected_note.get()}_{timestamp}.zip"
            
            zip_filename = filedialog.asksaveasfilename(
                defaultextension=".zip",
                initialfile=default_filename,
                filetypes=[("Archivo ZIP", "*.zip")],
                title="Guardar archivo ZIP"
            )
            
            if not zip_filename:  # Si el usuario cancela la selección
                return

            # Crear un directorio temporal
            temp_dir = "temp_notes"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            # Obtener todas las notas relacionadas
            graph = self.build_note_graph(self.input_dir.get())
            related_notes = set()
            self.collect_related_notes(graph, self.selected_note.get(), related_notes)

            # Copiar las notas al directorio temporal
            for note in related_notes:
                source_file = os.path.join(self.input_dir.get(), f"{note}.md")
                if os.path.exists(source_file):
                    shutil.copy2(source_file, temp_dir)

            # Crear el archivo ZIP en la ubicación seleccionada
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            # Limpiar el directorio temporal
            shutil.rmtree(temp_dir)
            
            messagebox.showinfo("Éxito", f"Archivo ZIP creado en:\n{zip_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear el archivo ZIP: {str(e)}")

    def collect_related_notes(self, graph, note, visited):
        """Recolecta todas las notas relacionadas recursivamente"""
        if note in visited:
            return
        visited.add(note)
        for child in graph[note]:
            self.collect_related_notes(graph, child, visited)

def main():
    root = tk.Tk()
    app = NoteTreeGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()