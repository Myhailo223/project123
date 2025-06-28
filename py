import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog


class ChatClient:
    def init(self, root):
        self.root = root
        self.root.title("Логічний чат")
        self.root.geometry("600x400")

        try:
            self.root.iconbitmap("")  # вимикаємо іконку
        except:
            pass

        self.username = simpledialog.askstring("Ім’я", "Введіть своє ім’я:", parent=self.root)
        if not self.username:
            self.username = "Користувач"

        # Створення GUI
        self.chat_display = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(padx=10, pady=5, fill=tk.X)

        self.message_entry = tk.Entry(bottom_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        send_button = tk.Button(bottom_frame, text="Надіслати", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        # Спроба підключення
        self.sock = None
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(("localhost", 8080))  # можеш змінити на IP
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався до чату!\n"
            self.sock.sendall(hello.encode('utf-8'))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.display_message("[SYSTEM] Підключення успішне.")
        except Exception as e:
            self.display_message(f"[SYSTEM] Помилка підключення: {e}")
            print(f"[DEBUG] Не вдалося підключитися: {e}")
            self.sock = None

    def display_message(self, message):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def send_message(self):
        message = self.message_entry.get()
        if message and self.sock:
            full_message = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(full_message.encode())
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.display_message("[SYSTEM] Не вдалося надіслати повідомлення")
                print(f"[DEBUG] Помилка надсилання: {e}")

    def receive_messages(self):
        buffer = ""
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
        except:
            pass
        finally:
            self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        if parts[0] == "TEXT" and len(parts) >= 3:
            author = parts[1]
            content = parts[2]
            self.display_message(f"{author}: {content}")
        else:
            self.display_message(line)


if name == "main":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
