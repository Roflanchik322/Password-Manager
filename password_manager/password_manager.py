import re
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, simpledialog

HISTORY_FILE = ""
CURRENT_THEME_NAME = "dark"

THEME_DATA = {
    "dark": {"bg": "#000000", "text": "#ffffff", "entry": "#1a1a1a", "btn": "#2a2a2a", "font": ("Arial", 10), "title": "МЕНЕДЖЕР ПАРОЛЕЙ", "btn_txt": "Сохранить"},
    "light": {"bg": "#f5f5f5", "text": "#111111", "entry": "#dddddd", "btn": "#cccccc", "font": ("Arial", 10), "title": "МЕНЕДЖЕР ПАРОЛЕЙ", "btn_txt": "Сохранить"}
}

def check_password(password):
    score, recs = 0, []
    if re.search(r'[а-яА-ЯёЁ]', password):
        recs.append("Используйте латиницу.")
        return "СЛАБЫЙ", 0, recs
    if len(password) < 8:
        recs.append("Минимум 8 символов.")
    else:
        score += 1
    if not re.search(r'[A-Z]', password):
        recs.append("Нужны заглавные.")
    else:
        score += 1
    if not re.search(r'[a-z]', password):
        recs.append("Нужны строчные.")
    else:
        score += 1
    if not re.search(r'[0-9]', password):
        recs.append("Нужны цифры.")
    else:
        score += 1
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        recs.append("Добавьте спецсимволы.")
    else:
        score += 1
    if re.search(r'(.)\1{3,}', password):
        score -= 1
    if re.search(r'(012345|123456|234567|345678|456789|567890)', password):
        score -= 1
    if score >= 5:
        return "СИЛЬНЫЙ", score, recs
    elif score >= 3:
        return "СРЕДНИЙ", score, recs
    return "СЛАБЫЙ", score, recs

def get_file_path():
    return os.path.join(HISTORY_FILE, "passwords.txt") if HISTORY_FILE else None

def save_to_file(resource, login, password, strength):
    if not HISTORY_FILE:
        messagebox.showerror("Ошибка", "Выберите папку!")
        return False
    path = get_file_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(f"Ресурс: {resource} | Логин: {login} |"):
                    messagebox.showwarning("Дубликат", f"Ресурс '{resource}' с логином '{login}' уже существует! Нельзя добавлять дубликаты.")
                    return False
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"Ресурс: {resource} | Логин: {login} | Пароль: {password} | Надёжность: {strength}\n")
    return True

def change_password(resource, login, new_pass, new_str):
    path = get_file_path()
    if not path or not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines, found = [], False
    for line in lines:
        if line.startswith(f"Ресурс: {resource} | Логин: {login} |"):
            new_lines.append(f"Ресурс: {resource} | Логин: {login} | Пароль: {new_pass} | Надёжность: {new_str}\n")
            found = True
        else:
            new_lines.append(line)
    if found:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    return False

def get_history():
    path = get_file_path()
    if not path:
        return "Папка не выбрана."
    if not os.path.exists(path):
        return "История пуста."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def choose_folder():
    global HISTORY_FILE
    folder = filedialog.askdirectory()
    if folder:
        HISTORY_FILE = folder
        label_folder.config(text=f"Папка: ...{folder[-20:]}", fg=TEXT_COLOR)

def on_check():
    p = entry_password.get()
    if not p:
        messagebox.showwarning("Пусто", "Введите пароль.")
        return
    s, sc, r = check_password(p)
    label_result.config(text=f"ОЦЕНКА: {s} (Балл: {sc}/6)")
    text_recs.delete(1.0, tk.END)
    text_recs.insert(tk.END, "Советы:\n" + "\n".join([f"— {x}" for x in r]) if r else "Отлично!")

def on_save():
    res = entry_resource.get().strip()
    login = entry_login.get().strip()
    p = entry_password.get()
    if not res or not login or not p:
        messagebox.showwarning("Пусто", "Заполните все поля.")
        return
    s, _, _ = check_password(p)
    if save_to_file(res, login, p, s):
        messagebox.showinfo("Готово", f"Пароль для '{res}' (логин: {login}) сохранён!")

def on_change():
    res = simpledialog.askstring("Смена", "Введите название ресурса:")
    if not res:
        return
    login = simpledialog.askstring("Смена", f"Введите логин для '{res}':")
    if not login:
        return
    new_p = simpledialog.askstring("Смена", f"Новый пароль для '{res}' (логин: {login}):")
    if not new_p:
        return
    s, _, _ = check_password(new_p)
    if change_password(res, login, new_p, s):
        messagebox.showinfo("Успешно", "Пароль обновлён!")
    else:
        messagebox.showerror("Ошибка", f"Ресурс '{res}' с логином '{login}' не найден.")

def on_history():
    win = tk.Toplevel(root)
    win.title("История")
    win.geometry("600x450")
    win.configure(bg=BG_COLOR)
    txt = scrolledtext.ScrolledText(win, bg=ENTRY_BG, fg=TEXT_COLOR, font=FONT_STYLE)
    txt.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
    txt.insert(tk.END, get_history())
    txt.config(state=tk.DISABLED)

def apply_theme(theme_name):
    global BG_COLOR, TEXT_COLOR, ENTRY_BG, BTN_BG, FONT_STYLE, BTN_TEXT, TITLE_TEXT, CURRENT_THEME_NAME
    CURRENT_THEME_NAME = theme_name
    data = THEME_DATA[theme_name]
    BG_COLOR, TEXT_COLOR, ENTRY_BG, BTN_BG, FONT_STYLE, BTN_TEXT, TITLE_TEXT = \
        data["bg"], data["text"], data["entry"], data["btn"], data["font"], data["btn_txt"], data["title"]
    root.configure(bg=BG_COLOR)
    for widget in [frame_theme, frame_folder, frame_input, frame_buttons, res_frame, login_frame, pass_frame, frame_recs]:
        widget.config(bg=BG_COLOR)
    label_title.config(text=TITLE_TEXT, bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_STYLE[0], 16, "bold"))
    label_folder.config(bg=BG_COLOR, fg=TEXT_COLOR)
    label_result.config(bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_STYLE)
    lbl_res.config(bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_STYLE)
    lbl_login.config(bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_STYLE)
    lbl_pass.config(bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_STYLE)
    frame_recs.config(highlightbackground=TEXT_COLOR)
    text_recs.config(bg=ENTRY_BG, fg=TEXT_COLOR, font=FONT_STYLE)
    for entry in [entry_resource, entry_login, entry_password]:
        entry.config(bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_STYLE)
    for btn in [btn_folder, btn_check, btn_save, btn_change, btn_history, btn_exit]:
        btn.config(bg=BTN_BG, fg=TEXT_COLOR, activebackground=ENTRY_BG, font=FONT_STYLE)
    for radio in frame_theme.winfo_children():
        radio.config(bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR)
    btn_check.config(text="Проверить")
    btn_save.config(text=f"{BTN_TEXT}")

root = tk.Tk()
root.title("Менеджер Паролей")
root.geometry("600x620")
root.minsize(500, 500)
root.configure(bg="#000000")

frame_theme = tk.Frame(root)
frame_theme.place(relx=0.5, rely=0.04, anchor=tk.CENTER)
theme_var = tk.StringVar(value="dark")
for txt, val in [("Тёмный", "dark"), ("Светлый", "light")]:
    tk.Radiobutton(frame_theme, text=txt, variable=theme_var, value=val,
                   command=lambda t=val: apply_theme(t)).pack(side=tk.LEFT, padx=3)

label_title = tk.Label(root, text="МЕНЕДЖЕР ПАРОЛЕЙ", font=("Arial", 16, "bold"))
label_title.place(relx=0.5, rely=0.10, anchor=tk.CENTER)

frame_folder = tk.Frame(root)
frame_folder.place(relx=0.5, rely=0.18, anchor=tk.CENTER)
btn_folder = tk.Button(frame_folder, text="Выбрать папку", command=choose_folder, relief="flat")
btn_folder.pack(side=tk.LEFT, padx=5)
label_folder = tk.Label(frame_folder, text="Папка не выбрана")
label_folder.pack(side=tk.LEFT, padx=10)

frame_input = tk.Frame(root)
frame_input.place(relx=0.5, rely=0.28, anchor=tk.CENTER)

res_frame = tk.Frame(frame_input)
res_frame.pack(pady=3)
lbl_res = tk.Label(res_frame, text="Ресурс:")
lbl_res.pack(side=tk.LEFT, padx=5)
entry_resource = tk.Entry(res_frame, width=25, relief="flat")
entry_resource.pack(side=tk.LEFT, padx=5)

login_frame = tk.Frame(frame_input)
login_frame.pack(pady=3)
lbl_login = tk.Label(login_frame, text="Логин:")
lbl_login.pack(side=tk.LEFT, padx=5)
entry_login = tk.Entry(login_frame, width=25, relief="flat")
entry_login.pack(side=tk.LEFT, padx=5)

pass_frame = tk.Frame(frame_input)
pass_frame.pack(pady=3)
lbl_pass = tk.Label(pass_frame, text="Пароль:")
lbl_pass.pack(side=tk.LEFT, padx=5)
entry_password = tk.Entry(pass_frame, width=25, show="*", relief="flat")
entry_password.pack(side=tk.LEFT, padx=5)

btn_check = tk.Button(root, text="Проверить", command=on_check, relief="flat")
btn_check.place(relx=0.5, rely=0.42, anchor=tk.CENTER)

label_result = tk.Label(root, text="Ожидание...")
label_result.place(relx=0.5, rely=0.49, anchor=tk.CENTER)

frame_recs = tk.Frame(root, highlightthickness=1)
frame_recs.place(relx=0.5, rely=0.57, anchor=tk.CENTER, width=400)
text_recs = tk.Text(frame_recs, height=4, relief="flat", wrap=tk.WORD, bd=0)
text_recs.pack(padx=10, pady=10, fill=tk.BOTH)

frame_buttons = tk.Frame(root)
frame_buttons.place(relx=0.5, rely=0.77, anchor=tk.CENTER)
btn_save = tk.Button(frame_buttons, text="Сохранить", command=on_save, relief="flat")
btn_save.pack(side=tk.LEFT, padx=8)
btn_change = tk.Button(frame_buttons, text="Сменить", command=on_change, relief="flat")
btn_change.pack(side=tk.LEFT, padx=8)
btn_history = tk.Button(frame_buttons, text="История", command=on_history, relief="flat")
btn_history.pack(side=tk.LEFT, padx=8)
btn_exit = tk.Button(frame_buttons, text="Выход", command=root.quit, relief="flat")
btn_exit.pack(side=tk.LEFT, padx=8)

apply_theme("dark")
root.mainloop()