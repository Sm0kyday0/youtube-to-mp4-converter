# pip install yt-dlp imageio-ffmpeg pyinstaller
# pyinstaller --onefile --noconsole --hidden-import=yt_dlp --hidden-import=imageio_ffmpeg "Youtube to mp4 converter.py."

import os
import threading
import yt_dlp
import imageio_ffmpeg as ffmpeg
import tkinter as tk
from tkinter import messagebox

def download_youtube_mp4(url, quality, filename=None):
    save_path = os.path.join(os.path.expanduser("~"), "Desktop", "mp4DL")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    if filename and filename.strip() != "":
        out_template = os.path.join(save_path, f"{filename}.%(ext)s")
    else:
        out_template = os.path.join(save_path, "%(title)s.%(ext)s")

    ydl_opts = {
        'format': f"bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best",
        'merge_output_format': 'mp4',
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4'
        }],
        'outtmpl': out_template,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def reset_gui():
    url_entry.delete(0, tk.END)
    filename_entry.delete(0, tk.END)
    quality_var.set("1080")

def start_download_thread():
    url = url_entry.get().strip()
    quality = quality_var.get()
    filename = filename_entry.get().strip()

    if not url:
        messagebox.showerror("エラー", "YouTubeのURLを入力してください")
        return

    download_btn.config(text="ダウンロード中...", state="disabled", bg="gray")

    def download_task():
        try:
            download_youtube_mp4(url, quality, filename)
            root.after(0, lambda: messagebox.showinfo("完了", f"MP4ダウンロード完了（最大 {quality}p）"))
            root.after(0, reset_gui)
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("失敗", f"ダウンロードに失敗しました:\n{e}"))
        finally:
            root.after(0, lambda: download_btn.config(text="ダウンロード", state="normal", bg="blue"))

    threading.Thread(target=download_task, daemon=True).start()
# GUI
root = tk.Tk()
root.title("YouTube MP4ダウンローダー")
root.configure(bg='black')
root.geometry("400x350")
root.resizable(False, False)

tk.Label(root, text="YouTube URL:", bg='black', fg='white').pack(pady=(10, 0))
url_entry = tk.Entry(root, width=50, bg='white', fg='black')
url_entry.pack(pady=5)

tk.Label(root, text="画質を選択（最大）:", bg='black', fg='white').pack(pady=(10, 0))
quality_var = tk.StringVar(value="1080")
qualities = [
    ("360p", "360"),
    ("480p", "480"),
    ("720p HD", "720"),
    ("1080p FullHD", "1080"),
    ("1440p 2K", "1440"),
    ("2160p 4K", "2160")
]

for text, value in qualities:
    tk.Radiobutton(root, text=text, variable=quality_var, value=value,
                   bg='black', fg='white', selectcolor='blue').pack(anchor='center')

tk.Label(root, text="MP4の名前（省略可）:", bg='black', fg='white').pack(pady=(10, 0))
filename_entry = tk.Entry(root, width=50, bg='white', fg='black')
filename_entry.pack(pady=5)

download_btn = tk.Button(root, text="ダウンロード", command=start_download_thread, bg='blue', fg='white')
download_btn.pack(pady=10)

root.mainloop()
