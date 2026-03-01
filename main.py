import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

def resource_path(relative_path):
    """ Získá absolutní cestu k souboru, funguje pro vývoj i pro PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MimConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("mimrpim Video Converter")
        self.root.geometry("284x100")
        self.root.resizable(False, False)
        
        # Správné napojení protokolu bez závorek
        self.root.protocol("WM_DELETE_WINDOW", self.pri_uzavreni)
        
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except:
            pass

        self.label_var = tk.StringVar(value="Čekám na zadání...")
        self.progress_var = tk.DoubleVar(value=0)

        tk.Label(self.root, textvariable=self.label_var, wraplength=250, pady=15).pack()
        
        self.progress_bar = ttk.Progressbar(self.root, length=250, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(pady=5)
        
        self.files = []
        self.output_dir = ""
        
        # Příznak pro skrytí konzole ve Windows
        self.HIDE_CONSOLE = 0x08000000

        self.root.after(500, self.setup_conversion)

    def setup_conversion(self):
        if len(sys.argv) <= 1:
            selected_files = filedialog.askopenfilenames(
                title="1. Vyber videa ke konverzi",
                filetypes=[("Video soubory", "*.mp4 *.mkv *.avi *.mov"), ("Všechny soubory", "*.*")]
            )
            if not selected_files:
                self.label_var.set("Nebyly vybrány žádné soubory.")
                # Místo os._exit(0) raději zavřeme okno standardně
                self.root.destroy()
                return
            self.files = list(selected_files)
        else:
            self.files = sys.argv[1:]

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
            # PŘIDÁNO: creationflags pro skrytí okna ffprobe
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, check=True, shell=False, creationflags=self.HIDE_CONSOLE
            )
            return float(result.stdout)
        except:
            return 0

    def convert_thread(self):
        for file in self.files:
            if not os.path.isfile(file): continue

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

            # PŘIDÁNO: creationflags pro skrytí okna ffmpeg
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL,
                text=True, 
                bufsize=1, 
                universal_newlines=True,
                shell=False,
                creationflags=self.HIDE_CONSOLE
            )

            if process.stdout:
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
        
        messagebox.showinfo("Hotovo", "Všechna videa byla úspěšně zkonvertována.")
        self.pri_uzavreni_bez_dotazu()

    def start_conversion(self):
        t = threading.Thread(target=self.convert_thread, daemon=True)
        t.start()

    def run(self):
        self.root.mainloop()
    
    def pri_uzavreni_bez_dotazu(self):
        """ Pomocná funkce pro ukončení bez ptaní po dokončení práce """
        moje_pid = os.getpid()
        try:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(moje_pid)], creationflags=self.HIDE_CONSOLE)
        except:
            os._exit(0)

    def pri_uzavreni(self):
        if messagebox.askokcancel("Ukončit", "Opravdu chceš zavřít program?"):
            moje_pid = os.getpid()
            try:
                # PŘIDÁNO: creationflags pro skrytí okna taskkill
                subprocess.call(
                    ['taskkill', '/F', '/T', '/PID', str(moje_pid)], 
                    creationflags=self.HIDE_CONSOLE
                )
            except Exception:
                self.root.destroy()
                os._exit(0)

if __name__ == "__main__":
    app = MimConverter()
    app.run()