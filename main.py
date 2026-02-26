import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

class MimConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("mimrpim Video Converter")
        self.root.geometry("400x180")
        self.root.resizable(False, False)
        
        # Pokus o nastavení ikony
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        self.label_var = tk.StringVar(value="Čekám na zadání...")
        self.progress_var = tk.DoubleVar(value=0)

        tk.Label(self.root, textvariable=self.label_var, wraplength=350, pady=15).pack()
        
        self.progress_bar = ttk.Progressbar(self.root, length=320, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(pady=5)
        
        self.files = []
        self.output_dir = ""
        
        # Inicializace po startu
        self.root.after(500, self.setup_conversion)

    def setup_conversion(self):
        # 1. Výběr souborů (pokud nebyly předány přes Drag & Drop)
        if len(sys.argv) <= 1:
            selected_files = filedialog.askopenfilenames(
                title="1. Vyber videa ke konverzi",
                filetypes=[("Video soubory", "*.mp4 *.mkv *.avi *.mov"), ("Všechny soubory", "*.*")]
            )
            if not selected_files:
                self.label_var.set("Nebyly vybrány žádné soubory.")
                return
            self.files = list(selected_files)
        else:
            self.files = sys.argv[1:]

        # 2. Výběr cílové složky
        dest_dir = filedialog.askdirectory(title="2. Vyber složku, kam uložit hotová videa")
        if not dest_dir:
            self.label_var.set("Nebyla vybrána cílová složka.")
            return
        
        self.output_dir = dest_dir
        self.start_conversion()

    def get_duration(self, filename):
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', filename
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
            return float(result.stdout)
        except:
            return 0

    def convert_thread(self):
        for file in self.files:
            if not os.path.isfile(file): continue

            # Vytvoření názvu v cílové složce
            file_name = os.path.basename(file)
            base, _ = os.path.splitext(file_name)
            output_path = os.path.join(self.output_dir, f"{base}_fixed.mp4")
            
            self.label_var.set(f"Zpracovávám: {file_name}")
            self.progress_var.set(0)
            total_duration = self.get_duration(file)

            cmd = [
                'ffmpeg', '-progress', 'pipe:1', '-i', file,
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-preset', 'fast', '-crf', '20',
                '-y', output_path
            ]

            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL,
                text=True, 
                bufsize=1, 
                universal_newlines=True
            )

            for line in process.stdout:
                if "out_time_ms=" in line:
                    try:
                        time_ms = int(line.split('=')[1].strip())
                        current_time = time_ms / 1000000
                        if total_duration > 0:
                            progress = (current_time / total_duration) * 100
                            self.progress_var.set(progress)
                            self.root.update_idletasks()
                    except:
                        pass

            process.wait()

        self.label_var.set("Dokončeno!")
        self.progress_var.set(100)
        
        # Zobrazení OK okna na konci
        messagebox.showinfo("Hotovo", "Všechna videa byla úspěšně zkonvertována, mimrpime!")
        self.root.destroy()

    def start_conversion(self):
        t = threading.Thread(target=self.convert_thread, daemon=True)
        t.start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MimConverter()
    app.run()