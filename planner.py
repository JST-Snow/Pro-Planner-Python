import customtkinter as ctk
from tkcalendar import Calendar
import sqlite3
import datetime
import winsound
import requests
import time
from tkinter import messagebox

# --- Начальные настройки ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class UltimatePlanner2026(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pro Planner v19.3 | Final Stable")
        self.geometry("1240x980")

        self.db_name = "planner_final.db"
        self.init_db()

        self.lang = "RU"
        self.translations = {
            "RU": {
                "title": "📅 ПЛАНИРОВЩИК", "search": "Поиск:", "find": "Найти",
                "legend_off": "🔴 - Праздник/Выходной", "legend_today": "🔵 - Сегодня",
                "time_cat": "Время и Категория:", "today_btn": "📍 СЕГОДНЯ",
                "annual": "🔁 Повторять ежегодно", "desc": "Описание события:",
                "save": "💾 СОХРАНИТЬ", "delete": "🗑️ УДАЛИТЬ", "search_res": "Результаты поиска",
                "weather_off": "Погода: оффлайн", "save_ok": "Сохранено!", "del_q": "Удалить запись?",
                "anniv_title": "🔔 СОБЫТИЯ СЕГОДНЯ:", "lang_btn": "English"
            },
            "EN": {
                "title": "📅 PRO PLANNER", "search": "Search:", "find": "Search",
                "legend_off": "🔴 - Holiday/Weekend", "legend_today": "🔵 - Today",
                "time_cat": "Time & Category:", "today_btn": "📍 TODAY",
                "annual": "🔁 Repeat annually", "desc": "Event description:",
                "save": "💾 SAVE NOTE", "delete": "🗑️ DELETE", "search_res": "Search results",
                "weather_off": "Weather: offline", "save_ok": "Saved!", "del_q": "Delete this note?",
                "anniv_title": "🔔 EVENTS TODAY:", "lang_btn": "Русский"
            }
        }

        self.categories = {"Общее/General": "#4A90E2", "Работа/Work": "#E74C3C", "Учеба/Study": "#F1C40F", "Личное/Personal": "#2ECC71", "Важно/Urgent": "#9B59B6"}
        self.fixed_holidays = ["01-01", "01-02", "01-03", "01-04", "01-05", "01-06", "01-07", "01-08", "02-23", "03-08", "05-01", "05-09", "06-12", "11-04"]

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_content()
        self.refresh_calendar_design()
        self.update_weather()
        self.update_clock()

    def init_db(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes (date TEXT, time TEXT, content TEXT, category TEXT, is_annual INTEGER DEFAULT 0, PRIMARY KEY (date, time))''')
        self.conn.commit()

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        date_str = datetime.datetime.now().strftime("%d.%m.%Y")
        self.clock_label.configure(text=f"{now}\n{date_str}")
        self.after(1000, self.update_clock)

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.after(100, self.refresh_calendar_design)

    def switch_language(self):
        self.lang = "EN" if self.lang == "RU" else "RU"
        self.update_ui_text()
        self.refresh_calendar_design()

    def update_ui_text(self):
        t = self.translations[self.lang]
        self.sidebar_title.configure(text=t["title"])
        self.lang_btn.configure(text=t["lang_btn"])
        self.leg_off.configure(text=t["legend_off"])
        self.leg_today.configure(text=t["legend_today"])
        self.search_lbl.configure(text=t["search"])
        self.search_btn.configure(text=t["find"])
        self.time_cat_lbl.configure(text=t["time_cat"])
        self.today_btn.configure(text=t["today_btn"])
        self.annual_cb.configure(text=t["annual"])
        self.desc_lbl.configure(text=t["desc"])
        self.save_btn.configure(text=t["save"])
        self.delete_btn.configure(text=t["delete"])

    def update_weather(self):
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=55.75&longitude=37.61&current_weather=true"
            res = requests.get(url, timeout=5).json()
            temp = res['current_weather']['temperature']
            self.weather_label.configure(text=f"Moscow: {temp}°C 🌤" if self.lang=="EN" else f"Москва: {temp}°C 🌤")
        except:
            self.weather_label.configure(text=self.translations[self.lang]["weather_off"])

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="", font=("Arial", 26, "bold"))
        self.sidebar_title.pack(pady=(40, 10))

        self.clock_label = ctk.CTkLabel(self.sidebar, text="", font=("Courier New", 28, "bold"), text_color="#3498DB")
        self.clock_label.pack(pady=10)

        self.weather_label = ctk.CTkLabel(self.sidebar, text="", font=("Arial", 16))
        self.weather_label.pack(pady=5)

        self.lang_btn = ctk.CTkButton(self.sidebar, text="", command=self.switch_language, fg_color="#34495E")
        self.lang_btn.pack(pady=15)

        info = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        info.pack(pady=20, padx=20, fill="x")
        self.leg_off = ctk.CTkLabel(info, text="", text_color="#E74C3C", font=("Arial", 14)); self.leg_off.pack(anchor="w")
        self.leg_today = ctk.CTkLabel(info, text="", text_color="#3498DB", font=("Arial", 14)); self.leg_today.pack(anchor="w")

        self.search_lbl = ctk.CTkLabel(self.sidebar, text="", font=("Arial", 14)); self.search_lbl.pack(pady=(20, 0))
        self.search_entry = ctk.CTkEntry(self.sidebar, height=40); self.search_entry.pack(pady=10, padx=30, fill="x")
        self.search_btn = ctk.CTkButton(self.sidebar, text="", command=self.search_notes); self.search_btn.pack(pady=5, padx=30, fill="x")

        ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light"], command=self.change_theme).pack(side="bottom", pady=40)

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=40, pady=20, sticky="nsew")

        self.cal = Calendar(self.main_frame, selectmode='day', date_pattern='y-mm-dd', font="Arial 14", 
                            firstweekday="monday", showweeknumbers=False)
        self.cal.pack(pady=10, fill="x", ipady=35)
        self.cal.bind("<<CalendarMonthChanged>>", self.refresh_calendar_design)
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_note())

        ctrl = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b", corner_radius=10)
        ctrl.pack(fill="x", pady=10, ipady=10)
        self.time_cat_lbl = ctk.CTkLabel(ctrl, text="", font=("Arial", 14, "bold")); self.time_cat_lbl.pack(pady=5)
        
        inner_ctrl = ctk.CTkFrame(ctrl, fg_color="transparent")
        inner_ctrl.pack()
        self.today_btn = ctk.CTkButton(inner_ctrl, text="", width=120, command=self.go_to_today); self.today_btn.pack(side="left", padx=10)
        self.hour_cb = ctk.CTkComboBox(inner_ctrl, values=[f"{i:02d}" for i in range(24)], width=80); self.hour_cb.set(datetime.datetime.now().strftime("%H")); self.hour_cb.pack(side="left", padx=5)
        self.min_cb = ctk.CTkComboBox(inner_ctrl, values=[f"{i:02d}" for i in range(0, 60, 5)], width=80); self.min_cb.set("00"); self.min_cb.pack(side="left", padx=5)
        self.cat_cb = ctk.CTkComboBox(inner_ctrl, values=list(self.categories.keys()), width=180); self.cat_cb.set("Общее/General"); self.cat_cb.pack(side="left", padx=10)

        self.annual_var = ctk.IntVar(value=0)
        self.annual_cb = ctk.CTkCheckBox(self.main_frame, text="", variable=self.annual_var, font=("Arial", 14)); self.annual_cb.pack(pady=5, anchor="w", padx=10)

        self.desc_lbl = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 16, "bold")); self.desc_lbl.pack(anchor="w", padx=10)
        self.text_area = ctk.CTkTextbox(self.main_frame, font=("Arial", 18), corner_radius=12, border_width=1); self.text_area.pack(pady=10, fill="both", expand=True)

        btn_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=10)
        self.save_btn = ctk.CTkButton(btn_row, text="", height=60, font=("Arial", 18, "bold"), fg_color="#2ecc71", command=self.save_note); self.save_btn.pack(side="left", expand=True, padx=10, fill="x")
        self.delete_btn = ctk.CTkButton(btn_row, text="", height=60, font=("Arial", 18, "bold"), fg_color="#e74c3c", command=self.delete_note); self.delete_btn.pack(side="left", expand=True, padx=10, fill="x")
        
        self.update_ui_text()

    def refresh_calendar_design(self, event=None):
        """Полная принудительная перерисовка стилей"""
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg = "#1d1d1d" if is_dark else "#ffffff"
        fg = "white" if is_dark else "black"
        hbg = "#333333" if is_dark else "#eeeeee"
        hfg = "white" if is_dark else "black"

        self.cal.configure(
            background=bg, foreground=fg, 
            normalbackground=bg, normalforeground=fg,
            headersbackground=hbg, headersforeground=hfg,
            selectbackground="#3498DB", selectforeground="white",
            weekendbackground=bg, weekendforeground="#E74C3C",
            othermonthbackground=bg, othermonthforeground="gray"
        )
        
        self.cal.calevent_remove('all')
        _, year = self.cal.get_displayed_month()
        today = datetime.date.today()
        
        for h_str in self.fixed_holidays:
            try: self.cal.calevent_create(datetime.date(year, int(h_str[:2]), int(h_str[3:])), "H", "weekend_holiday")
            except: pass
        self.cal.calevent_create(today, "T", "today_marker")
        
        self.cursor.execute("SELECT DISTINCT date, category FROM notes")
        for d_str, cat in self.cursor.fetchall():
            try: self.cal.calevent_create(datetime.date.fromisoformat(d_str), cat, cat)
            except: pass
        
        self.cal.tag_config("weekend_holiday", background="#E74C3C", foreground="white")
        self.cal.tag_config("today_marker", background="#3498DB", foreground="white")
        for name, color in self.categories.items(): 
            self.cal.tag_config(name, background=color, foreground='white')

    def go_to_today(self):
        self.cal.selection_set(datetime.date.today()); self.load_note()

    def save_note(self):
        date, time_str, content, cat, ann = self.cal.get_date(), f"{self.hour_cb.get()}:{self.min_cb.get()}", self.text_area.get("1.0", "end-1c").strip(), self.cat_cb.get(), self.annual_var.get()
        if content:
            self.cursor.execute("INSERT OR REPLACE INTO notes VALUES (?, ?, ?, ?, ?)", (date, time_str, content, cat, ann))
            self.conn.commit(); self.refresh_calendar_design()
            messagebox.showinfo("OK", self.translations[self.lang]["save_ok"])

    def load_note(self):
        date, time_str = self.cal.get_date(), f"{self.hour_cb.get()}:{self.min_cb.get()}"
        self.text_area.delete("1.0", "end"); self.annual_var.set(0)
        self.cursor.execute("SELECT content, category, is_annual FROM notes WHERE date=? AND time=?", (date, time_str))
        res = self.cursor.fetchone()
        if res: self.text_area.insert("1.0", res[0]); self.cat_cb.set(res[1]); self.annual_var.set(res[2])
        
        d_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.cursor.execute("SELECT content, time FROM notes WHERE is_annual=1 AND date LIKE ?", ('%' + d_obj.strftime("-%m-%d"),))
        anniv = self.cursor.fetchall()
        if anniv: messagebox.showinfo(self.translations[self.lang]["anniv_title"], "\n".join([f"• [{r[1]}] {r[0]}" for r in anniv]))

    def delete_note(self):
        if messagebox.askyesno("?", self.translations[self.lang]["del_q"]):
            self.cursor.execute("DELETE FROM notes WHERE date=? AND time=?", (self.cal.get_date(), f"{self.hour_cb.get()}:{self.min_cb.get()}"))
            self.conn.commit(); self.text_area.delete("1.0", "end"); self.refresh_calendar_design()

    def search_notes(self):
        q = self.search_entry.get()
        if not q: return
        self.cursor.execute("SELECT date, time, content FROM notes WHERE content LIKE ?", ('%'+q+'%',))
        res = self.cursor.fetchall()
        win = ctk.CTkToplevel(self); win.title(self.translations[self.lang]["search_res"]); win.geometry("600x450")
        txt = ctk.CTkTextbox(win, width=580, height=430, font=("Arial", 16)); txt.pack(padx=10, pady=10)
        for r in res: txt.insert("end", f"📅 {r[0]} ({r[1]}):\n📝 {r[2][:100]}...\n{'-'*30}\n")

if __name__ == "__main__":
    app = UltimatePlanner2026()
    app.mainloop()