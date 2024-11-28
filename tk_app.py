import tkinter as tk
from tkinter import filedialog, messagebox
import requests

# pyinstaller --onefile --windowed --name=ZipLoader .\tk_app.py

class ZipUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZIP Uploader")

        self.label = tk.Label(root, text="Select a ZIP file to upload:")
        self.label.pack(pady=10)

        self.upload_button = tk.Button(root, text="Upload ZIP", command=self.upload_zip)
        self.upload_button.pack(pady=10)

    def upload_zip(self):
        file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if file_path:
            self.send_zip_to_server(file_path)

    def send_zip_to_server(self, file_path):
        url = 'https://shunliservertruck.ddns.net:5000/upload'  # Замените на URL вашего сервера
        files = {'file': open(file_path, 'rb')}

        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                messagebox.showinfo("Success", "File uploaded successfully!")
            else:
                messagebox.showerror("Error", f"Failed to upload file. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ZIP Loader")
    root.geometry("500x200")
    app = ZipUploaderApp(root)
    root.mainloop()
