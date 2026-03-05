"""
CloPos XPrinter Auto-Installer v6.1
Made by Fuad Huseynov © 2026  |  CloPos IT Team
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import socket
import subprocess
import ipaddress
import os
import sys
import ctypes
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

VERSION = "8.1.1"
APP_TITLE = f"CloPos XPrinter Auto-Installer v{VERSION}"

# ═══ UAC — Admin olaraq yenidən aç ══════════════════════════════
def ensure_admin():
    """Windows UAC: admin deyilsə, runas ilə özünü yenidən aç"""
    if sys.platform != "win32": return
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    if not is_admin:
        try:
            script = sys.executable if getattr(sys,"frozen",False) else os.path.abspath(__file__)
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable if not getattr(sys,"frozen",False) else script,
                f'"{script}"' if not getattr(sys,"frozen",False) else None,
                None, 1)
            if ret > 32:
                sys.exit(0)
        except Exception:
            pass

ensure_admin()

# ═══ Rəng Palitası — boz-mavi tematika ══════════════════════════
CL_BLUE    = "#3469D4"   # CloPos mavi
CL_BLUE_D  = "#2251B8"   # tünd mavi
CL_BLUE_L  = "#5B8FEF"   # açıq mavi
CL_BG      = "#2C3347"   # əsas fon — tünd boz-mavi
CL_BG2     = "#242938"   # başlıq/tab fonu
CL_CARD    = "#333A50"   # kart fonu
CL_CARD2   = "#3D4560"   # kart hover
CL_BORDER  = "#404869"   # border
CL_TEXT    = "#E8EEFF"   # əsas mətn
CL_DIM     = "#8892B0"   # soluk mətn
CL_SUB     = "#A0AAC8"   # köməkçi mətn
CL_WHITE   = "#FFFFFF"
CL_CUT     = "#38BDF8"   # kəsicili badge
CL_RED     = "#F43F5E"
CL_GREEN   = "#34D399"
CL_AMBER   = "#F59E0B"

PORT    = 9100
TIMEOUT = 1.5   # test üçün daha qısa
WORKERS = 150
SCAN_TIMEOUT = 0.5

FONT_H1  = ("Segoe UI", 14, "bold")
FONT_H2  = ("Segoe UI", 11, "bold")
FONT_H3  = ("Segoe UI", 10, "bold")
FONT_B   = ("Segoe UI", 10)
FONT_S   = ("Segoe UI", 9)
FONT_XS  = ("Segoe UI", 8)
FONT_MON = ("Consolas", 9)

# ═══ Translations ════════════════════════════════════════════════
LANGS = {
    "AZ": {
        "tab_driver":"   Driver   ","tab_lan":"   LAN   ",
        "tab_usb":"   USB   ","tab_list":"   Qurulmuş Cihazlar   ",
        "tab_info":"   Məlumat   ",
        "driver_install":"XPrinter Driver V7.77 Quraşdır",
        "already":"Artıq Quraşdırılıb — Növbəti addıma keç",
        "driver_file":"Driver EXE:","browse":"Qovluğu Dəyiş",
        "net_label":"Şəbəkə:","port_label":"Port:","scan":"Scan Et",
        "found":"Tapılan Printerlər","cfg":"Konfiqurasiya",
        "log":"Log","clear":"Sil",
        "pname":"Printer Adı:","model":"Model:",
        "iface_usb":"USB Port:","check_usb":"USB Portu Yoxla",
        "apply_all":"Hamısına tətbiq et","test_print_lan":"Test Print",
        "sel_all":"Hamısını seç","desel":"Seçimi sil",
        "install_sel":"Seçilənləri Quraşdır",
        "installed":"Qurulmuş Cihazlar","refresh":"Yenilə",
        "sel_all_list":"Hamısını seç",
        "delete":"Seçilənləri Sil","rename":"Adını Dəyiş",
        "print_test":"Test Çapı",
        "col_name":"Ad","col_port":"Port / IP","col_mac":"MAC",
        "col_drv":"Driver",
        "confirm_del":"Silinəcək:\n\n{}\n\nDavam?",
        "confirm_ins":"{} printer quraşdırılacaq:\n\n{}\n\nDavam?",
        "no_file":"XPrinter Driver EXE faylını seçin.",
        "sel_one":"Ən az bir printer seçin.",
        "done":"Tamamlandı",
        "drv_ok":"XPrinter Driver quraşdırıldı!\nNövbəti taba keçin.",
        "waiting":"Gözləyin…","loading":"Yüklənir…",
        "status_scan":"Scan gedir…","status_ready":"Hazır",
        "status_done":"{}/{} quraşdırıldı","status_del":"{} silindi",
        "rename_title":"Printer Adını Dəyiş",
        "rename_lbl":"Yeni ad:","rename_ok":"Dəyiş","cancel":"İptal",
        "no_cutter":"Kəsicisiz","with_cutter":"Kəsicili",
        "usb_found":"USB printer tapıldı\nPort: {}",
        "usb_tab_title":"Printer Quraşdır",
        "usb_install":"⬇  USB Printer Quraşdır",
        "usb_not_found":"USB printer tapılmadı!\nPrinteri USB ilə qoşub yenidən yoxlayın.",
        "test_ok":"✓ Test çapı göndərildi","test_fail":"✗ Test çapı alınmadı",
        "test_timeout":"✗ Cavab gəlmədi (timeout)",
        "copy_ip":"IP Kopyala","copy_mac":"MAC Kopyala",
        "copied":"Kopyalandı!",
        "check_update":"Yeniləməni Yoxla",
                "update_checking":"GitHub-da yoxlanılır…",
        "update_found":"🔔  Yeni versiya mövcuddur: v{}\n\nYükləmək istəyirsiniz?",
        "update_uptodate":"✓  Proqram ən yeni versiyadır (v{})",
        "update_error":"Yoxlama zamanı xəta:\n{}",
        "update_download":"Yüklə",
        "update_later":"Sonra",
        "update_title":"Versiya yoxlanışı",
"update_title":"Versiya yoxlanışı",
        "update_msg":f"Hazırki versiya: v{VERSION}\nYeniləmə axtarılır…\n\n(Bu funksiya tezliklə aktivləşdiriləcək)",
        "about_title":"Proqram haqqında",
        "about_text":(
            "CloPos XPrinter Installer — restoran\n"
            "şəbəkəsindəki POS printerlərini\n"
            "avtomatik quraşdırmaq üçün alətdir.\n\n"
            "•  Şəbəkəni scan edib XPrinter tapır\n"
            "•  Model və kağız eni seçimi\n"
            "•  USB printer dəstəyi\n"
            "•  Cihaz idarəetməsi: adını dəyiş,\n"
            "   sil, test çapı"
        ),
        "models_footer":"XP-58 · XP-80 · XP-90 · XP-76",
        "website":"clopos.com",
        "version_label":f"Versiya:  v{VERSION}",
        "developer":"Made by:  Fuad Huseynov",
                "user_guide":"📄  İstifadəçi Bələdçisi (PDF)",
        "usb_checking":"USB yoxlanılır…",
        "folder_changed":"Quraşdırma yeri dəyişdirildi",
        "printers_found":"{} printer tapıldı",
        "scan_start":"Scan gedir…",
        "installing_n":"{} printer quraşdırılır…",
        "deleting_n":"{} silinir…",
        "test_sending":"Test çapı göndərilir: {}…",
        "test_sent_ok":"Test çapı OK",
        "test_after_reg":"Test çapı: printer qeydiyyatdan sonra işləyir",
        "install_dest":"Quraşdırma yeri: {}",
        "about_models":"Dəstəklənən modellər:",
        "drv_installing":"  XPrinter Driver V7.77 quraşdırılır…",
        "drv_window_open":"  Quraşdırıcı pəncərəsi açılır…",
        "drv_finished":"✓  Tamamlandı!",
        "file_not_found":"✗  Fayl tapılmadı: {}",
        "no_driver_installed":"  ✗  Driver tapılmadı — əvvəlcə XPrinter Driver quraşdırın",
        "printer_deleted":"  ✓  '{}' silindi",
        "select_printer":"← Printer seçin","install_hint":"Quraşdırmaq üçün aşağıdakı düyməni basın",
"team":"CloPos IT Team  ©2026",
    },
    "EN": {
        "tab_driver":"   Driver   ","tab_lan":"   LAN   ",
        "tab_usb":"   USB   ","tab_list":"   Installed   ",
        "tab_info":"   Info   ",
        "driver_install":"Install XPrinter Driver V7.77",
        "already":"Already Installed — Skip to next",
        "driver_file":"Driver EXE:","browse":"Change Folder",
        "net_label":"Network:","port_label":"Port:","scan":"Scan",
        "found":"Found Printers","cfg":"Configuration",
        "log":"Log","clear":"Clear",
        "pname":"Printer Name:","model":"Model:",
        "iface_usb":"USB Port:","check_usb":"Check USB Port",
        "apply_all":"Apply to all selected","test_print_lan":"Test Print",
        "sel_all":"Select all","desel":"Deselect",
        "install_sel":"Install Selected",
        "installed":"Installed Devices","refresh":"Refresh",
        "sel_all_list":"Select all",
        "delete":"Delete Selected","rename":"Rename",
        "print_test":"Print Test",
        "col_name":"Name","col_port":"Port / IP","col_mac":"MAC",
        "col_drv":"Driver",
        "confirm_del":"Will be deleted:\n\n{}\n\nContinue?",
        "confirm_ins":"Install {}:\n\n{}\n\nContinue?",
        "no_file":"Please select XPrinter Driver EXE file.",
        "sel_one":"Select at least one printer.",
        "done":"Done",
        "drv_ok":"XPrinter Driver installed!\nGo to next tab.",
        "waiting":"Please wait…","loading":"Loading…",
        "status_scan":"Scanning…","status_ready":"Ready",
        "status_done":"Installed {}/{}","status_del":"Deleted {}",
        "rename_title":"Rename Printer",
        "rename_lbl":"New name:","rename_ok":"Rename","cancel":"Cancel",
        "no_cutter":"No cutter","with_cutter":"Cutter",
        "usb_found":"USB printer found\nPort: {}",
        "usb_tab_title":"Install Printer",
        "usb_install":"⬇  Install USB Printer",
        "usb_not_found":"No USB printer found!\nConnect printer via USB and retry.",
        "test_ok":"✓ Test page sent","test_fail":"✗ Test page failed",
        "test_timeout":"✗ No response (timeout)",
        "copy_ip":"Copy IP","copy_mac":"Copy MAC",
        "copied":"Copied!",
        "check_update":"Check for Updates",
                "update_checking":"Checking GitHub…",
        "update_found":"🔔  New version available: v{}\n\nWould you like to download?",
        "update_uptodate":"✓  You have the latest version (v{})",
        "update_error":"Check failed:\n{}",
        "update_download":"Download",
        "update_later":"Later",
        "update_title":"Version Check",
"update_title":"Version Check",
        "update_msg":f"Current version: v{VERSION}\nChecking for updates…\n\n(This feature will be activated soon)",
        "about_title":"About",
        "about_text":(
            "CloPos XPrinter Installer — professional\n"
            "tool for automatic POS printer\n"
            "installation in restaurant networks.\n\n"
            "•  Network scan & printer discovery\n"
            "•  Model & paper width selection\n"
            "•  USB printer support\n"
            "•  Device management: rename,\n"
            "   delete, print test"
        ),
        "models_footer":"XP-58 · XP-80 · XP-90 · XP-76",
        "website":"clopos.com",
        "version_label":f"Version:  v{VERSION}",
        "developer":"Developer:  Fuad Huseynov",
                "user_guide":"📄  User Guide  (PDF)",
        "usb_checking":"Checking USB…",
        "folder_changed":"Install folder changed",
        "printers_found":"{} printers found",
        "scan_start":"Scanning…",
        "installing_n":"Installing {} printer(s)…",
        "deleting_n":"Deleting {}…",
        "test_sending":"Sending test page: {}…",
        "test_sent_ok":"Test page OK",
        "test_after_reg":"Test page: works after registration",
        "install_dest":"Install folder: {}",
        "about_models":"Supported models:",
        "drv_installing":"  Installing XPrinter Driver V7.77…",
        "drv_window_open":"  Opening installer window…",
        "drv_finished":"✓  Done!",
        "file_not_found":"✗  File not found: {}",
        "no_driver_installed":"  ✗  Driver not found — install XPrinter Driver first",
        "printer_deleted":"  ✓  '{}' deleted",
        "select_printer":"← Select a printer","install_hint":"Click the button below to install",
"team":"CloPos IT Team  ©2026",
    },
    "TR": {
        "tab_driver":"   Sürücü   ","tab_lan":"   LAN   ",
        "tab_usb":"   USB   ","tab_list":"   Kurulu Cihazlar   ",
        "tab_info":"   Bilgi   ",
        "driver_install":"XPrinter Driver V7.77 Kur",
        "already":"Zaten Kurulu — Sonraki adıma geç",
        "driver_file":"Sürücü EXE:","browse":"Klasör Değiştir",
        "net_label":"Ağ:","port_label":"Port:","scan":"Tara",
        "found":"Bulunan Yazıcılar","cfg":"Yapılandırma",
        "log":"Günlük","clear":"Temizle",
        "pname":"Yazıcı Adı:","model":"Model:",
        "iface_usb":"USB Port:","check_usb":"USB Kontrol",
        "apply_all":"Seçililere uygula","test_print_lan":"Test Print",
        "sel_all":"Tümünü seç","desel":"Seçimi kaldır",
        "install_sel":"Seçilileri Kur",
        "installed":"Kurulu Cihazlar","refresh":"Yenile",
        "sel_all_list":"Tümünü seç",
        "delete":"Seçilileri Sil","rename":"Yeniden Adlandır",
        "print_test":"Test Yazdır",
        "col_name":"Ad","col_port":"Port / IP","col_mac":"MAC",
        "col_drv":"Sürücü",
        "confirm_del":"Silinecek:\n\n{}\n\nDevam?",
        "confirm_ins":"Kurulacak {}:\n\n{}\n\nDevam?",
        "no_file":"XPrinter Driver EXE seçin.",
        "sel_one":"En az bir yazıcı seçin.",
        "done":"Tamamlandı",
        "drv_ok":"Sürücü kuruldu!\nSonraki sekmeye geçin.",
        "waiting":"Lütfen bekleyin…","loading":"Yükleniyor…",
        "status_scan":"Taranıyor…","status_ready":"Hazır",
        "status_done":"Kuruldu {}/{}","status_del":"Silindi {}",
        "rename_title":"Yazıcıyı Adlandır",
        "rename_lbl":"Yeni ad:","rename_ok":"Değiştir","cancel":"İptal",
        "no_cutter":"Kesicisiz","with_cutter":"Kesicili",
        "usb_found":"USB yazıcı bulundu\nPort: {}",
        "usb_tab_title":"Yazıcı Kur",
        "usb_install":"⬇  USB Yazıcı Kur",
        "usb_not_found":"USB yazıcı bulunamadı!\nBağlayıp tekrar deneyin.",
        "test_ok":"✓ Test sayfası gönderildi","test_fail":"✗ Test sayfası alınamadı",
        "test_timeout":"✗ Yanıt gelmedi (timeout)",
        "copy_ip":"IP Kopyala","copy_mac":"MAC Kopyala",
        "copied":"Kopyalandı!",
        "check_update":"Güncelleme Kontrol",
                "update_checking":"GitHub kontrol ediliyor…",
        "update_found":"🔔  Yeni sürüm mevcut: v{}\n\nİndirmek ister misiniz?",
        "update_uptodate":"✓  En güncel sürümdesiniz (v{})",
        "update_error":"Kontrol başarısız:\n{}",
        "update_download":"İndir",
        "update_later":"Sonra",
        "update_title":"Sürüm Kontrolü",
"update_title":"Versiyon Kontrolü",
        "update_msg":f"Mevcut versiyon: v{VERSION}\nGüncelleme aranıyor…\n\n(Bu özellik yakında aktifleştirilecek)",
        "about_title":"Hakkında",
        "about_text":(
            "CloPos XPrinter Installer — restoran\n"
            "ağlarında POS yazıcılarını otomatik\n"
            "kurmak için profesyonel araç.\n\n"
            "•  Ağ taraması ve yazıcı keşfi\n"
            "•  Model ve kağıt eni seçimi\n"
            "•  USB yazıcı desteği\n"
            "•  Cihaz yönetimi: adlandırma,\n"
            "   silme, test baskı"
        ),
        "models_footer":"XP-58 · XP-80 · XP-90 · XP-76",
        "website":"clopos.com",
        "version_label":f"Versiyon:  v{VERSION}",
        "developer":"Made by:  Fuad Huseynov",
                "user_guide":"📄  Kullanım Kılavuzu (PDF)",
        "usb_checking":"USB kontrol ediliyor…",
        "folder_changed":"Kurulum konumu değiştirildi",
        "printers_found":"{} yazıcı bulundu",
        "scan_start":"Taranıyor…",
        "installing_n":"{} yazıcı kuruluyor…",
        "deleting_n":"{} siliniyor…",
        "test_sending":"Test sayfası gönderiliyor: {}…",
        "test_sent_ok":"Test sayfası OK",
        "test_after_reg":"Test sayfası: kayıt sonrası çalışır",
        "install_dest":"Kurulum konumu: {}",
        "about_models":"Desteklenen modeller:",
        "drv_installing":"  XPrinter Driver V7.77 kuruluyor…",
        "drv_window_open":"  Yükleyici penceresi açılıyor…",
        "drv_finished":"✓  Tamamlandı!",
        "file_not_found":"✗  Dosya bulunamadı: {}",
        "no_driver_installed":"  ✗  Sürücü bulunamadı — önce XPrinter Driver kurun",
        "printer_deleted":"  ✓  '{}' silindi",
        "select_printer":"← Yazıcı seçin","install_hint":"Kurmak için aşağıdaki düğmeye basın",
"team":"CloPos IT Team  ©2026",
    },
    "RU": {
        "tab_driver":"   Драйвер   ","tab_lan":"   LAN   ",
        "tab_usb":"   USB   ","tab_list":"   Установленные   ",
        "tab_info":"   Инфо   ",
        "driver_install":"Установить XPrinter Driver V7.77",
        "already":"Уже установлен — Пропустить",
        "driver_file":"EXE файл:","browse":"Изм. папку",
        "net_label":"Сеть:","port_label":"Порт:","scan":"Сканировать",
        "found":"Найденные принтеры","cfg":"Конфигурация",
        "log":"Журнал","clear":"Очистить",
        "pname":"Имя принтера:","model":"Модель:",
        "iface_usb":"USB Порт:","check_usb":"Проверить USB",
        "apply_all":"Применить ко всем","test_print_lan":"Test Print",
        "sel_all":"Выбрать все","desel":"Снять",
        "install_sel":"Установить выбранные",
        "installed":"Установленные устройства","refresh":"Обновить",
        "sel_all_list":"Выбрать все",
        "delete":"Удалить выбранные","rename":"Переименовать",
        "print_test":"Тест печати",
        "col_name":"Имя","col_port":"Порт / IP","col_mac":"MAC",
        "col_drv":"Драйвер",
        "confirm_del":"Будут удалены:\n\n{}\n\nПродолжить?",
        "confirm_ins":"Установить {}:\n\n{}\n\nПродолжить?",
        "no_file":"Выберите EXE файл XPrinter Driver.",
        "sel_one":"Выберите хотя бы один принтер.",
        "done":"Готово",
        "drv_ok":"Драйвер установлен!\nПерейдите на следующую вкладку.",
        "waiting":"Подождите…","loading":"Загрузка…",
        "status_scan":"Сканирование…","status_ready":"Готово",
        "status_done":"Установлено {}/{}","status_del":"Удалено {}",
        "rename_title":"Переименовать принтер",
        "rename_lbl":"Новое имя:","rename_ok":"Применить","cancel":"Отмена",
        "no_cutter":"Без ножа","with_cutter":"С ножом",
        "usb_found":"USB принтер найден\nПорт: {}",
        "usb_tab_title":"Установка принтера",
        "usb_install":"⬇  Установить USB-принтер",
        "usb_not_found":"USB принтер не найден!\nПодключите принтер и повторите.",
        "test_ok":"✓ Тест напечатан","test_fail":"✗ Ошибка теста",
        "test_timeout":"✗ Нет ответа (timeout)",
        "copy_ip":"Копировать IP","copy_mac":"Копировать MAC",
        "copied":"Скопировано!",
        "check_update":"Проверить обновления",
                "update_checking":"Проверка GitHub…",
        "update_found":"🔔  Доступна новая версия: v{}\n\nЗагрузить?",
        "update_uptodate":"✓  У вас последняя версия (v{})",
        "update_error":"Ошибка проверки:\n{}",
        "update_download":"Загрузить",
        "update_later":"Позже",
        "update_title":"Проверка версии",
"update_title":"Проверка версии",
        "update_msg":f"Текущая версия: v{VERSION}\nПоиск обновлений…\n\n(Функция будет активирована в ближайшее время)",
        "about_title":"О программе",
        "about_text":(
            "CloPos XPrinter Installer — инструмент\n"
            "для автоматической установки POS\n"
            "принтеров в ресторанной сети.\n\n"
            "•  Сканирование сети и поиск принтеров\n"
            "•  Выбор модели и ширины бумаги\n"
            "•  Поддержка USB принтеров\n"
            "•  Управление устройствами:\n"
            "   переименование, удаление, тест"
        ),
        "models_footer":"XP-58 · XP-80 · XP-90 · XP-76",
        "website":"clopos.com",
        "version_label":f"Версия:  v{VERSION}",
        "developer":"Made by:  Fuad Huseynov",
                "user_guide":"📄  Руководство (PDF)",
        "usb_checking":"Проверка USB…",
        "folder_changed":"Папка установки изменена",
        "printers_found":"Найдено {} принтеров",
        "scan_start":"Сканирование…",
        "installing_n":"Установка {} принтеров…",
        "deleting_n":"Удаление {}…",
        "test_sending":"Тест печати: {}…",
        "test_sent_ok":"Тест печати OK",
        "test_after_reg":"Тест: доступен после регистрации",
        "install_dest":"Папка установки: {}",
        "about_models":"Поддерживаемые модели:",
        "drv_installing":"  Установка XPrinter Driver V7.77…",
        "drv_window_open":"  Открывается окно установщика…",
        "drv_finished":"✓  Готово!",
        "file_not_found":"✗  Файл не найден: {}",
        "no_driver_installed":"  ✗  Драйвер не найден — установите XPrinter Driver",
        "printer_deleted":"  ✓  '{}' удалён",
        "select_printer":"← Выберите принтер","install_hint":"Нажмите кнопку ниже для установки",
"team":"CloPos IT Team  ©2026",
    },
}

# ═══ Backend ══════════════════════════════════════════════════════
NO_WIN = subprocess.CREATE_NO_WINDOW

def get_local_networks():
    nets = []
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith("127."):
                p = ip.split(".")
                nets.append(f"{p[0]}.{p[1]}.{p[2]}.0/24")
    except Exception:
        pass
    return list(set(nets)) or ["192.168.1.0/24"]

def get_usb_ports_list():
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             "[System.IO.Ports.SerialPort]::GetPortNames()"],
            capture_output=True, text=True, timeout=8,
            check=False, creationflags=NO_WIN)
        ports = [p.strip() for p in r.stdout.splitlines() if p.strip()]
        if ports: return ["USB001","USB002"] + ports
    except Exception:
        pass
    return ["USB001","USB002","COM1","COM2","COM3","COM4"]

def check_usb_printer():
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             "Get-PrinterPort | Where-Object {$_.Name -match '^USB'} | "
             "Sort-Object Name | Select-Object -First 1 -ExpandProperty Name"],
            capture_output=True, text=True, timeout=12,
            check=False, creationflags=NO_WIN)
        port = r.stdout.strip()
        if port: return port, f"USB Printer ({port})"
        r2 = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             "Get-WmiObject Win32_Printer | "
             "Where-Object {$_.PortName -match '^USB'} | "
             "Select-Object -First 1 Name,PortName | ConvertTo-Csv -NoTypeInformation"],
            capture_output=True, text=True, timeout=12,
            check=False, creationflags=NO_WIN)
        for line in r2.stdout.splitlines()[1:]:
            parts = [x.strip('"') for x in line.split('","')]
            if len(parts) >= 2 and parts[1].upper().startswith("USB"):
                return parts[1], parts[0]
        r3 = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             "Get-PnpDevice -Class 'USB' -Status 'OK' 2>$null | "
             "Where-Object { $_.FriendlyName -like '*Print*' } | "
             "Select-Object -First 1 -ExpandProperty FriendlyName"],
            capture_output=True, text=True, timeout=12,
            check=False, creationflags=NO_WIN)
        if r3.stdout.strip():
            return "USB001", r3.stdout.strip()
        return None, None
    except Exception:
        return None, None

def check_port(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(SCAN_TIMEOUT)
            return s.connect_ex((ip, PORT)) == 0
    except Exception:
        return False

def scan_network(cidr, cb_prog, cb_log):
    found = []
    try:
        hosts = list(ipaddress.ip_network(cidr, strict=False).hosts())
        total = len(hosts)
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(check_port, str(h)): str(h) for h in hosts}
            done = 0
            for f in as_completed(futures):
                ip = futures[f]; done += 1
                if f.result():
                    found.append(ip); cb_log(f"✓  {ip}")
                cb_prog(int(done/total*100))
    except Exception as e:
        cb_log(f"✗  {e}")
    return sorted(found)

def get_mac_for_ip(ip):
    """
    ARP vasitəsilə MAC adresi al.
    Əvvəlcə ping edib ARP cədvəlinə əlavə edir, sonra oxuyur.
    """
    if not ip or ip in ("—", ""):
        return "—"
    try:
        # Əvvəlcə ping edib ARP cache-i doldur (1 ping, 500ms timeout)
        subprocess.run(
            ["ping", "-n", "1", "-w", "500", ip],
            capture_output=True, timeout=3,
            check=False, creationflags=NO_WIN)
    except Exception:
        pass
    # Method 1: PowerShell Get-NetNeighbor
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             f"Get-NetNeighbor -IPAddress '{ip}' -EA SilentlyContinue | "
             f"Where-Object {{$_.State -ne 'Unreachable'}} | "
             f"Select-Object -First 1 -ExpandProperty LinkLayerAddress"],
            capture_output=True, text=True, timeout=8,
            check=False, creationflags=NO_WIN)
        mac = r.stdout.strip()
        if mac and mac not in ("FF-FF-FF-FF-FF-FF","00-00-00-00-00-00"):
            return mac.upper()
    except Exception:
        pass
    # Method 2: arp -a fallback
    try:
        r2 = subprocess.run(["arp","-a",ip], capture_output=True,
                            text=True, timeout=5, check=False, creationflags=NO_WIN)
        for line in r2.stdout.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if "-" in part and len(part) == 17:
                        return part.upper()
    except Exception:
        pass
    return "—"

def extract_ip_from_port(port_name):
    """Port adından IP çıxar: IP_192_168_1_10 → 192.168.1.10"""
    if not port_name:
        return ""
    if port_name.upper().startswith("IP_"):
        return port_name[3:].replace("_",".")
    # Some ports use format like 192.168.1.10 directly
    parts = port_name.split(".")
    if len(parts) == 4:
        try:
            if all(0 <= int(p) <= 255 for p in parts):
                return port_name
        except ValueError:
            pass
    return ""


def get_installed_drivers():
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             "Get-PrinterDriver | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, timeout=15,
            check=False, creationflags=NO_WIN)
        return [d.strip() for d in r.stdout.splitlines() if d.strip()]
    except Exception:
        return []

def find_xprinter_driver(model):
    drivers = get_installed_drivers()
    for d in drivers:
        if model.upper() in d.upper(): return d
    for d in drivers:
        if "xprinter" in d.lower() or "xp-" in d.lower(): return d
    return None

def get_bundled_exe():
    base = sys._MEIPASS if getattr(sys,"frozen",False) \
           else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base,"XPrinter Driver Setup V7.77.exe")

def ps_run(cmd, timeout=30):
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            check=False, creationflags=NO_WIN)
        return r.returncode == 0, (r.stderr or r.stdout).strip()[:300]
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def run_install_exe(exe_path, cb_log, t_fn=None):
    t = t_fn if t_fn else (lambda k, *a: k)
    if not exe_path or not os.path.exists(exe_path):
        cb_log(t("file_not_found").format(exe_path)); return False
    try:
        cb_log(t("drv_installing"))
        r = subprocess.run([exe_path,"/SILENT","/NORESTART"],
                           timeout=180, check=False, creationflags=NO_WIN)
        if r.returncode in [0,1,3010]:
            cb_log(t("drv_finished")); return True
        cb_log(t("drv_window_open"))
        subprocess.Popen([exe_path]); return True
    except subprocess.TimeoutExpired:
        subprocess.Popen([exe_path]); return True
    except Exception as e:
        cb_log(f"✗  {e}"); return False

def install_lan(ip, model, name, cb_log, t_fn=None):
    pn = f"IP_{ip.replace('.','_')}"
    drv = find_xprinter_driver(model)
    if not drv:
        t = t_fn if t_fn else (lambda k, *a: k)
        cb_log(t("no_driver_installed")); return False
    cb_log(f"  driver: {drv}")
    ps_run(f"$p=Get-PrinterPort -Name '{pn}' -EA SilentlyContinue;"
           f"if($p){{Set-PrinterPort -Name '{pn}' -PrinterHostAddress '{ip}' -PortNumber {PORT}}}"
           f"else{{Add-PrinterPort -Name '{pn}' -PrinterHostAddress '{ip}' -PortNumber {PORT}}}")
    ok, err = ps_run(
        f"try{{if(Get-Printer -Name '{name}' -EA SilentlyContinue)"
        f"{{Set-Printer -Name '{name}' -PortName '{pn}' -DriverName '{drv}'}}"
        f"else{{Add-Printer -Name '{name}' -PortName '{pn}' -DriverName '{drv}'}}}}"
        f"catch{{Write-Error $_.Exception.Message}}")
    if ok: cb_log(f"  ✓  '{name}'")
    else:  cb_log(f"  ✗  {err}")
    return ok

def install_usb(usb_port, model, name, cb_log, t_fn=None):
    drv = find_xprinter_driver(model)
    t = t_fn if t_fn else (lambda k, *a: k)
    if not drv:
        cb_log(t("no_driver_installed")); return False
    cb_log(f"  driver: {drv}")
    pn = usb_port.split("(")[-1].replace(")","").strip() if "(" in usb_port else usb_port
    ok, err = ps_run(
        f"try{{if(Get-Printer -Name '{name}' -EA SilentlyContinue)"
        f"{{Set-Printer -Name '{name}' -PortName '{pn}' -DriverName '{drv}'}}"
        f"else{{Add-Printer -Name '{name}' -PortName '{pn}' -DriverName '{drv}'}}}}"
        f"catch{{Write-Error $_.Exception.Message}}")
    if ok: cb_log(f"  ✓  '{name}'")
    else:  cb_log(f"  ✗  {err}")
    return ok

def get_printers_with_mac():
    """Printer siyahısı + port-dan IP çıxar"""
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-WindowStyle","Hidden","-Command",
             "Get-Printer | Select-Object Name,PortName,DriverName | ConvertTo-Csv -NoTypeInformation"],
            capture_output=True, text=True, timeout=20,
            check=False, creationflags=NO_WIN)
        rows = []
        for line in r.stdout.strip().splitlines()[1:]:
            p = [x.strip('"') for x in line.split('","')] 
            if len(p) >= 3:
                name, port, drv = p[0], p[1], p[2]
                ip = extract_ip_from_port(port)
                rows.append((name, port, ip, drv))
        return rows
    except Exception:
        return []
def rename_printer(old, new):
    return ps_run(f"Rename-Printer -Name '{old}' -NewName '{new}' -EA Stop")

def delete_printer(name, cb_log, t_fn=None):
    ok, err = ps_run(f"Remove-Printer -Name '{name}' -EA Stop")
    t = t_fn if t_fn else (lambda k, *a: k)
    if ok: cb_log(t("printer_deleted").format(name))
    else:  cb_log(f"  ✗  {err}")
    return ok

def print_test_lan(ip, printer_name):
    """
    LAN printer test: əvvəl TCP 9100 port yoxla (1.5s),
    açılırsa Windows test page göndər, açılmırsa dərhal error qaytar.
    """
    # Step 1: quick TCP check
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            if s.connect_ex((ip, PORT)) != 0:
                return False, f"Printer offline ({ip}:{PORT} əlçatmazdır)"
    except Exception as e:
        return False, f"Şəbəkə xətası: {e}"
    # Step 2: Windows test page
    ok, err = ps_run(
        f"$p=Get-WmiObject -Class Win32_Printer -Filter \"Name='{printer_name}'\";"
        f"if($p){{$r=$p.PrintTestPage();if($r.ReturnValue -eq 0){{'ok'}}"
        f"else{{Write-Error ('Code: '+$r.ReturnValue)}}}}"
        f"else{{Write-Error 'Printer not found'}}",
        timeout=10)
    return ok, err

def print_test_usb(printer_name):
    """USB printer test: port yoxlaması yoxdur, birbaşa WMI"""
    ok, err = ps_run(
        f"$p=Get-WmiObject -Class Win32_Printer -Filter \"Name='{printer_name}'\";"
        f"if($p){{$r=$p.PrintTestPage();if($r.ReturnValue -eq 0){{'ok'}}"
        f"else{{Write-Error ('Code: '+$r.ReturnValue)}}}}"
        f"else{{Write-Error 'Printer not found'}}",
        timeout=10)
    return ok, err

# ═══ GUI Helpers ══════════════════════════════════════════════════
def _adj(hx, amt):
    try:
        r=int(hx[1:3],16); g=int(hx[3:5],16); b=int(hx[5:7],16)
        return f"#{min(255,max(0,r+amt)):02x}{min(255,max(0,g+amt)):02x}{min(255,max(0,b+amt)):02x}"
    except Exception:
        return hx

def mk_btn(parent, text, cmd, bg=None, fg=CL_WHITE, font=None, pad=(14,8)):
    bg = bg or CL_BLUE
    f = font or FONT_H3
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                  font=f, relief="flat", padx=pad[0], pady=pad[1],
                  cursor="hand2", activebackground=_adj(bg,22),
                  activeforeground=fg, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=_adj(bg,22)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def mk_lbl(parent, text, fg=CL_TEXT, font=FONT_B, bg=None, **kw):
    return tk.Label(parent, text=text, fg=fg, font=font,
                    bg=bg or parent.cget("bg"), **kw)

def mk_entry(parent, var, width=28):
    outer = tk.Frame(parent, bg=CL_CARD2,
                     highlightthickness=1,
                     highlightbackground=CL_BORDER,
                     highlightcolor=CL_BLUE)
    e = tk.Entry(outer, textvariable=var, width=width,
                 font=FONT_B, bg=CL_CARD2, fg=CL_TEXT,
                 insertbackground=CL_TEXT, relief="flat", bd=6)
    e.pack()
    def _fi(ev): outer.config(highlightbackground=CL_BLUE, highlightthickness=2)
    def _fo(ev): outer.config(highlightbackground=CL_BORDER, highlightthickness=1)
    e.bind("<FocusIn>", _fi); e.bind("<FocusOut>", _fo)
    bind_touch_keyboard(e)
    return outer, e

def mk_div(parent, pady=8, col=None):
    tk.Frame(parent, bg=col or CL_BORDER, height=1).pack(fill="x", pady=pady)

def mk_card(parent, **kw):
    return tk.Frame(parent, bg=CL_CARD, **kw)

def mk_log(parent, h=8):
    return scrolledtext.ScrolledText(
        parent, bg=CL_BG, fg="#4ECCA3",
        font=FONT_MON, relief="flat", height=h, state="disabled",
        selectbackground=CL_BLUE, wrap="word")

def log_add(w, msg, color=None):
    w.config(state="normal")
    if color:
        tag = f"c{color.replace('#','')}"
        w.tag_config(tag, foreground=color)
        w.insert("end", msg+"\n", tag)
    else:
        w.insert("end", msg+"\n")
    w.see("end"); w.config(state="disabled")

def log_clear(w):
    w.config(state="normal"); w.delete("1.0","end"); w.config(state="disabled")

def make_scrollable(parent, bg=None):
    """
    Scrollable frame — içindəki content scroll olur
    - Boşluq problemi fix: canvas scrollregion daim yenilənir
    - Trackpad + mouse wheel + touch scroll dəstəyi
    """
    bg = bg or CL_BG
    container = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=bg)
    frame_id = canvas.create_window((0,0), window=frame, anchor="nw")

    def _update_scroll(e=None):
        canvas.update_idletasks()
        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=bbox)
        # Ensure canvas height matches or scrollbar appears correctly
        if frame.winfo_reqheight() <= canvas.winfo_height():
            canvas.yview_moveto(0)

    def _on_canvas_configure(e):
        canvas.itemconfig(frame_id, width=e.width)
        _update_scroll()

    frame.bind("<Configure>", _update_scroll)
    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    def _scroll(e):
        # Mouse wheel: delta=120 per notch on Windows
        # Trackpad: may send fractional delta
        delta = e.delta
        if abs(delta) >= 120:
            units = int(-1 * (delta / 120))
        else:
            units = int(-1 * (delta / 40))
        canvas.yview_scroll(units, "units")

    def _bind_scroll(widget):
        widget.bind("<MouseWheel>", _scroll)
        widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1,"units"))
        widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1,"units"))

    def _bind_recursive(widget):
        _bind_scroll(widget)
        for child in widget.winfo_children():
            _bind_recursive(child)

    _bind_scroll(canvas)
    _bind_scroll(frame)
    frame.bind("<Map>", lambda e: _bind_recursive(frame))

    return container, frame


def draw_clopos_logo(canvas, x, y, sq=18, gap=4, color=CL_WHITE, outline_w=2):
    """
    CloPos v6.2 loqosu: 3 dolu ağ kvadrat + sağ-alt kvadratda printer ikonu.
    """
    positions = [(x,y),(x+sq+gap,y),(x,y+sq+gap),(x+sq+gap,y+sq+gap)]
    rr = max(2, int(sq*0.18))
    for i,(px,py) in enumerate(positions):
        if i < 3:
            canvas.create_rectangle(px,py,px+sq,py+sq, fill=color, outline="")
        else:
            # Sağ-alt: outline + printer
            canvas.create_rectangle(px,py,px+sq,py+sq,
                                     fill=CL_CARD2, outline=color, width=outline_w)
            m  = max(2, int(sq*0.10))
            pb_x, pb_y = px+m, py+int(sq*0.40)
            pb_w, pb_h = sq-2*m, int(sq*0.34)
            # printer body
            canvas.create_rectangle(pb_x, pb_y, pb_x+pb_w, pb_y+pb_h,
                                     fill=color, outline="")
            # paper feed top
            pt_x = px + int(sq*0.25); pt_w = int(sq*0.50)
            canvas.create_rectangle(pt_x, py+int(sq*0.18),
                                     pt_x+pt_w, py+int(sq*0.42),
                                     fill=CL_DIM, outline="")
            # paper output
            pp_x = px + int(sq*0.31); pp_w = int(sq*0.38)
            canvas.create_rectangle(pp_x, pb_y+pb_h,
                                     pp_x+pp_w, pb_y+pb_h+int(sq*0.18),
                                     fill=color, outline="")
            # blue dot
            dc = pb_x+pb_w-int(sq*0.14); dr = max(1,int(sq*0.07))
            canvas.create_oval(dc-dr, pb_y+pb_h//2-dr,
                                dc+dr, pb_y+pb_h//2+dr,
                                fill=CL_BLUE_L, outline="")


class WaitOverlay:
    def __init__(self, parent, text):
        self.f = tk.Frame(parent, bg=CL_BG2)
        self.f.place(relx=0, rely=0, relwidth=1, relheight=1)
        c = tk.Frame(self.f, bg=CL_CARD, padx=48, pady=32)
        c.place(relx=0.5, rely=0.5, anchor="center")
        self._dots = 0
        self._lbl = tk.Label(c, text="⬤  ○  ○", font=("Segoe UI",14),
                             bg=CL_CARD, fg=CL_BLUE)
        self._lbl.pack()
        tk.Label(c, text=text, font=("Segoe UI",12,"bold"),
                 bg=CL_CARD, fg=CL_TEXT).pack(pady=(8,0))
        self._animate()
    def _animate(self):
        if not self.f.winfo_exists(): return
        patterns = ["⬤  ○  ○","○  ⬤  ○","○  ○  ⬤"]
        self._dots = (self._dots + 1) % 3
        self._lbl.config(text=patterns[self._dots])
        self.f.after(400, self._animate)
    def destroy(self):
        try: self.f.destroy()
        except Exception: pass

class RenameDialog(tk.Toplevel):
    def __init__(self, parent, old_name, t_fn, on_ok):
        super().__init__(parent)
        self.title(t_fn("rename_title"))
        self.configure(bg=CL_BG)
        self.resizable(False, False)
        self.grab_set()
        hdr = tk.Frame(self, bg=CL_BLUE, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=t_fn("rename_title"), font=FONT_H2,
                 bg=CL_BLUE, fg=CL_WHITE).pack(padx=20)
        body = tk.Frame(self, bg=CL_BG, padx=24, pady=16)
        body.pack(fill="both")
        tk.Label(body, text=old_name, font=FONT_H3, bg=CL_BG, fg=CL_SUB).pack(anchor="w", pady=(0,8))
        tk.Label(body, text=t_fn("rename_lbl"), font=FONT_XS,
                 bg=CL_BG, fg=CL_DIM).pack(anchor="w")
        self.var = tk.StringVar(value=old_name)
        ef, e = mk_entry(body, self.var, 32)
        ef.pack(anchor="w", pady=(4,16))
        e.focus(); e.select_range(0,"end")
        # Touch: entry-ə birbaşa klik ilə klaviatura aç
        def _touch_entry(ev):
            try:
                extra = ctypes.windll.user32.GetMessageExtraInfo()
                is_touch = bool(extra & 0xFF515700 == 0xFF515700) or bool(extra & 0x80)
                if is_touch:
                    e.after(80, open_tabtip)
            except Exception:
                pass
        e.bind("<Button-1>", _touch_entry, add="+")
        bf = tk.Frame(body, bg=CL_BG)
        bf.pack(anchor="w")
        mk_btn(bf, t_fn("rename_ok"),
               lambda: on_ok(self.var.get()) or self.destroy(),
               pad=(20,8)).pack(side="left", padx=(0,8))
        mk_btn(bf, t_fn("cancel"), self.destroy, bg=CL_CARD2, fg=CL_SUB, pad=(16,8)).pack(side="left")
        self.update_idletasks()
        pw,ph = parent.winfo_width(), parent.winfo_height()
        px,py = parent.winfo_rootx(), parent.winfo_rooty()
        w,h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px+(pw-w)//2}+{py+(ph-h)//2}")
        # Touch screen — pəncərə tam render olandan sonra qeydiyyat
        self.after(50, self._register_touch)

    def _register_touch(self):
        try:
            import ctypes
            hwnd = self.winfo_id()
            ctypes.windll.user32.RegisterTouchWindow(hwnd, 0)
        except Exception:
            pass



# ═══ Touch / On-Screen Keyboard ══════════════════════════════════
import ctypes, ctypes.wintypes

# Windows mesaj sabitləri
WM_TOUCH        = 0x0240
TOUCHEVENTF_UP  = 0x0002

def open_tabtip():
    """Windows 10/11 touch klaviaturasını aç"""
    import subprocess, os
    paths = [
        r"C:\Program Files\Common Files\microsoft shared\ink\TabTip.exe",
        r"C:\Program Files (x86)\Common Files\microsoft shared\ink\TabTip.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            subprocess.Popen([p], creationflags=subprocess.DETACHED_PROCESS)
            return
    # Fallback: Windows 11 yeni touch keyboard
    try:
        subprocess.Popen(
            ["powershell","-Command",
             "Start-Process -FilePath 'shell:AppsFolder\\Microsoft.TabletInput_8wekyb3d8bbwe!TabletInput'"],
            creationflags=subprocess.DETACHED_PROCESS | 0x08000000)
    except Exception:
        pass

def bind_touch_keyboard(widget):
    """
    Widget-ə touch klaviatura bind et.
    YALNIZ birbaşa barmaq toxunması ilə açılır.
    Tab dəyişməsi, mouse və ya proqramlı focus-da açılmır.
    """
    _touched = [False]   # closure flag

    def on_touch_press(ev):
        _touched[0] = True

    def on_focus(ev):
        if _touched[0]:
            _touched[0] = False
            widget.after(80, open_tabtip)
        else:
            _touched[0] = False

    # <Button-1> həm touch həm mouse üçün işləyir
    # Touch-da GetMessageExtraInfo ilə fərqləndir
    def on_click(ev):
        try:
            extra = ctypes.windll.user32.GetMessageExtraInfo()
            is_touch = bool(extra & 0xFF515700 == 0xFF515700) or bool(extra & 0x80)
            if is_touch:
                _touched[0] = True
                widget.after(80, open_tabtip)
        except Exception:
            pass

    widget.bind("<Button-1>", on_click, add="+")
    widget.bind("<FocusIn>", on_focus, add="+")

def setup_touch_detection(root):
    """
    Windows WM_TOUCH mesajını root pəncərəyə qeydiyyatdan keçir.
    Bu olmasa touch event-lər gəlmir.
    """
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        if hwnd == 0:
            hwnd = root.winfo_id()
        # RegisterTouchWindow
        ctypes.windll.user32.RegisterTouchWindow(hwnd, 0)
    except Exception:
        pass

# ═══ GitHub Update Check ══════════════════════════════════════════
# GitHub repo: clopos/xprinter-installer
# Release tag format: "v7.0", "v7.1" etc.
# Each release must have an .exe asset attached.

GITHUB_REPO   = "huseynov77/xprinter-installer"
GITHUB_API    = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def _parse_version(tag: str) -> tuple:
    """'v7.1.2' → (7, 1, 2)"""
    tag = tag.lstrip("v").strip()
    try:
        return tuple(int(x) for x in tag.split("."))
    except Exception:
        return (0,)

def check_for_update():
    """
    GitHub-da ən son release-i yoxla.
    Qaytarır: (yeni_versiya_var: bool, yeni_tag: str, download_url: str, error: str|None)
    """
    try:
        import urllib.request, json, ssl
        # SSL sertifikat problemi — certifi varsa istifadə et, yoxsa verify=False
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": f"CloPos-XPrinter/{VERSION}",
                     "Accept": "application/vnd.github+json"}
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())

        latest_tag = data.get("tag_name", "")
        latest_ver = _parse_version(latest_tag)
        current_ver = _parse_version(VERSION)

        if latest_ver <= current_ver:
            return False, latest_tag, "", None

        # EXE asset-i tap
        download_url = ""
        for asset in data.get("assets", []):
            if asset.get("name","").endswith(".exe"):
                download_url = asset.get("browser_download_url","")
                break
        if not download_url:
            download_url = data.get("html_url","")

        return True, latest_tag, download_url, None

    except Exception as e:
        return False, "", "", str(e)


def auto_update_and_restart():
    """
    Proqram acilarkən GitHub-dan yeni versiya yoxlayir.
    Yeni versiya varsa:
      1. EXE-ni eyni qovluqa yukleyir
      2. Kohne EXE-ni silen + yenini acan batch/script yaradir
      3. Ozunu baglayir, script isleyir
    Frozen (PyInstaller) rejimdə isleyir, .py rejimdə skip edir.
    """
    if not getattr(sys, "frozen", False):
        return  # .py-dən işlədildikdə skip

    has_update, new_tag, url, err = check_for_update()
    if not has_update or not url:
        return

    # Hazırki EXE yolu və qovluğu
    current_exe = sys.executable
    exe_dir = os.path.dirname(current_exe)
    new_exe_name = f"CloPos XPrinter Install v{new_tag.lstrip('v')}.exe"
    new_exe_path = os.path.join(exe_dir, new_exe_name)

    # Yüklə
    try:
        import urllib.request, ssl
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"CloPos-XPrinter/{VERSION}"}
        )

        # Splash pəncərəsi göstər
        splash = tk.Tk()
        splash.overrideredirect(True)
        sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
        w, h = 420, 140
        splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        splash.configure(bg=CL_BG)
        splash.attributes("-topmost", True)

        tk.Label(splash, text=f"Yeni versiya tapildi: v{new_tag.lstrip('v')}",
                 font=("Segoe UI", 13, "bold"), fg=CL_WHITE, bg=CL_BG).pack(pady=(18,4))
        progress_lbl = tk.Label(splash, text="Yuklenilir...  0%",
                                font=("Segoe UI", 10), fg=CL_SUB, bg=CL_BG)
        progress_lbl.pack(pady=4)

        bar = ttk.Progressbar(splash, length=350, mode="determinate")
        bar.pack(pady=(8,12))
        splash.update()

        # Yüklə
        tmp_path = new_exe_path + ".tmp"
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = int(downloaded * 100 / total)
                        bar["value"] = pct
                        mb_done = downloaded / (1024*1024)
                        mb_total = total / (1024*1024)
                        progress_lbl.config(
                            text=f"Yuklenilir...  {pct}%  ({mb_done:.1f}/{mb_total:.1f} MB)")
                    splash.update()

        # tmp → final
        if os.path.exists(new_exe_path):
            os.remove(new_exe_path)
        os.rename(tmp_path, new_exe_path)

        splash.destroy()

        # Batch script: köhnə EXE-ni sil, yenini aç
        bat_path = os.path.join(tempfile.gettempdir(), "_clopos_update.bat")
        with open(bat_path, "w", encoding="utf-8") as bf:
            bf.write(f'@echo off\n')
            bf.write(f'timeout /t 2 /nobreak >nul\n')
            bf.write(f'del /f /q "{current_exe}"\n')
            bf.write(f'start "" "{new_exe_path}"\n')
            bf.write(f'del /f /q "%~f0"\n')

        # Batch-ı işlət və çıx
        subprocess.Popen(
            ["cmd", "/c", bat_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        sys.exit(0)

    except Exception:
        # Yükləmə uğursuz olsa, sadəcə davam et
        try:
            splash.destroy()
        except Exception:
            pass
        # Yarımçıq tmp faylını sil
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


# ═══ MAIN APP ═════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang      = tk.StringVar(value="AZ")
        self.lang.trace_add("write", self._lang_ch)
        self.exe_path  = tk.StringVar()
        self.net_var   = tk.StringVar(value=get_local_networks()[0])
        self.port_var  = tk.StringVar(value="9100")
        self.lan_cfgs  = {}
        self.W         = {}
        self._mac_cache= {}  # ip → mac cache

        self.title(APP_TITLE)
        self.configure(bg=CL_BG)
        self.state("zoomed")        # tam ekran açılır
        self.minsize(900, 600)
        self.resizable(True, True)
        self._build()
        setup_touch_detection(self)

    def t(self, k):
        return LANGS.get(self.lang.get(), LANGS["AZ"]).get(k, k)

    def _build(self):
        self._styles()
        self._header()
        self._notebook()
        self._statusbar()
        auto = self._detect_exe()
        if auto: self.exe_path.set(auto)

    # ── Styles ────────────────────────────────────────────────────
    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("CL.TNotebook", background=CL_BG2, borderwidth=0, tabmargins=[0,0,0,0])
        s.configure("CL.TNotebook.Tab",
                    background=CL_BG2, foreground=CL_DIM,
                    font=("Segoe UI",10,"bold"), padding=[20,10], borderwidth=0)
        s.map("CL.TNotebook.Tab",
              background=[("selected",CL_CARD),("active",CL_CARD2)],
              foreground=[("selected",CL_WHITE),("active",CL_TEXT)])
        s.configure("CL.Horizontal.TProgressbar",
                    troughcolor=CL_CARD, background=CL_BLUE,
                    borderwidth=0, thickness=4)
        s.configure("CL.Treeview", background=CL_CARD, foreground=CL_TEXT,
                    fieldbackground=CL_CARD, rowheight=30,
                    font=FONT_B, borderwidth=0)
        s.configure("CL.Treeview.Heading", background=CL_BG2,
                    foreground=CL_SUB, font=FONT_H3,
                    relief="flat", borderwidth=0)
        s.map("CL.Treeview",
              background=[("selected",CL_BLUE_D)],
              foreground=[("selected",CL_WHITE)])

    # ── Header ────────────────────────────────────────────────────
    def _header(self):
        hdr = tk.Frame(self, bg=CL_BG2)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=CL_BLUE, height=2).pack(fill="x")
        inner = tk.Frame(hdr, bg=CL_BG2, padx=22, pady=12)
        inner.pack(fill="x")

        lf = tk.Frame(inner, bg=CL_BG2)
        lf.pack(side="left")
        sq, gap = 17, 4
        total_w = sq*2+gap
        c = tk.Canvas(lf, width=total_w+2, height=total_w+2,
                      bg=CL_BG2, highlightthickness=0)
        c.pack(side="left", padx=(0,14))
        draw_clopos_logo(c, 1, 1, sq=sq, gap=gap, color=CL_WHITE, outline_w=2)

        tf = tk.Frame(inner, bg=CL_BG2)
        tf.pack(side="left")
        nr = tk.Frame(tf, bg=CL_BG2)
        nr.pack(anchor="w")
        tk.Label(nr, text="clopos", font=("Segoe UI",17,"bold"),
                 bg=CL_BG2, fg=CL_WHITE).pack(side="left")
        tk.Label(nr, text="  ×  ", font=("Segoe UI",14),
                 bg=CL_BG2, fg=CL_BORDER).pack(side="left")
        tk.Label(nr, text="xprinter", font=("Segoe UI",17,"bold"),
                 bg=CL_BG2, fg=CL_BLUE_L).pack(side="left")
        tk.Label(tf, text=f"Auto-Installer  ·  v{VERSION}",
                 font=("Segoe UI",9), bg=CL_BG2, fg=CL_DIM).pack(anchor="w")

        # Lang buttons: AZ EN TR RU
        lg_f = tk.Frame(inner, bg=CL_BG2)
        lg_f.pack(side="right")
        self._lbtns = {}
        for lg in ["AZ","EN","TR","RU"]:
            b = tk.Button(lg_f, text=lg, width=4,
                          command=lambda l=lg: self.lang.set(l),
                          font=("Segoe UI",9,"bold"), relief="flat",
                          cursor="hand2", bd=0, padx=8, pady=6)
            b.pack(side="left", padx=2)
            self._lbtns[lg] = b
        self._upd_lang_btns()
        self.lang.trace_add("write", lambda *_: self._upd_lang_btns())
        tk.Frame(hdr, bg=CL_BORDER, height=1).pack(fill="x")

    def _upd_lang_btns(self):
        cur = self.lang.get()
        for lg, b in self._lbtns.items():
            b.config(bg=CL_BLUE if lg==cur else CL_CARD2,
                     fg=CL_WHITE if lg==cur else CL_DIM)

    # ── Notebook (5 tab) ──────────────────────────────────────────
    def _notebook(self):
        self.nb = ttk.Notebook(self, style="CL.TNotebook")
        self.nb.pack(fill="both", expand=True)
        self.t1 = tk.Frame(self.nb, bg=CL_BG)
        self.t2 = tk.Frame(self.nb, bg=CL_BG)
        self.t3 = tk.Frame(self.nb, bg=CL_BG)
        self.t4 = tk.Frame(self.nb, bg=CL_BG)
        self.t5 = tk.Frame(self.nb, bg=CL_BG)
        for tab, key in [(self.t1,"tab_driver"),(self.t2,"tab_lan"),
                          (self.t3,"tab_usb"),(self.t4,"tab_list"),
                          (self.t5,"tab_info")]:
            self.nb.add(tab, text=self.t(key))
        self._build_t1(); self._build_t2()
        self._build_t3(); self._build_t4()
        self._build_t5()
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab)

    def _statusbar(self):
        bar = tk.Frame(self, bg=CL_BG2)
        bar.pack(fill="x", side="bottom")
        tk.Frame(bar, bg=CL_BORDER, height=1).pack(fill="x")
        inn = tk.Frame(bar, bg=CL_BG2, padx=18)
        inn.pack(fill="x")
        self.status_var = tk.StringVar(value=self.t("status_ready"))
        tk.Label(inn, textvariable=self.status_var,
                 bg=CL_BG2, fg=CL_DIM, font=FONT_XS).pack(side="left", pady=5)
        tk.Label(inn, text=f"© 2026  CloPos IT Team  ·  v{VERSION}",
                 bg=CL_BG2, fg=CL_BORDER, font=FONT_XS).pack(side="right")

    def _upd_browse_lbl(self):
        """Browse label mətnini aktiv dilə uyğun yenilə"""
        if hasattr(self, "W") and "w_browse" in self.W:
            try:
                self.W["w_browse"].config(text="⚙ " + self.t("browse"))
            except Exception:
                pass

    def _lang_ch(self, *_):
        for i, key in enumerate(["tab_driver","tab_lan","tab_usb","tab_list","tab_info"]):
            self.nb.tab(i, text=self.t(key))
        self.status_var.set(self.t("status_ready"))
        wmap = {
            "w_nl":"net_label","w_pl":"port_label","w_scan":"scan",
            "w_found":"found","w_cfgt":"cfg","w_logl":"log","w_clear":"clear",
            "w_pn_l":"pname","w_ml_l":"model",
            "w_selall":"sel_all","w_desel":"desel","w_isel":"install_sel",
            "w_inst":"installed","w_ref":"refresh",
            "w_sala":"sel_all_list","w_del":"delete",
            "w_pt":"print_test","w_chusb":"check_usb",
            "w_upd":"check_update","w_pdf":"user_guide","w_usb_inst":"usb_install",
            "w_apply_all":"apply_all","w_tpl":"test_print_lan",
        }
        for wk, tk_ in wmap.items():
            if wk in self.W:
                try: self.W[wk].config(text=self.t(tk_))
                except Exception: pass
        # Buttons with icon prefix
        for wk, key, prefix in [
            ("w_ren",      "rename",         "✏  "),
            ("w_copy_ip",  "copy_ip",        "⎘  "),
            ("w_copy_mac", "copy_mac",       "⎘  "),
            ("w_di",       "driver_install", "⬇   "),
            ("w_already",  "already",        "→   "),
        ]:
            if wk in self.W:
                try: self.W[wk].config(text=prefix + self.t(key))
                except Exception: pass
        if "tree" in self.W:
            self.W["tree"].heading("name", text=self.t("col_name"))
            self.W["tree"].heading("port", text=self.t("col_port"))
            self.W["tree"].heading("mac",  text=self.t("col_mac"))
            self.W["tree"].heading("drv",  text=self.t("col_drv"))
        # Update dynamic labels in about panel & info tab
        for attr, key in [
            ("_about_title_lbl", "about_title"),
            ("_about_text_lbl",  "about_text"),
            ("_about_models_lbl","about_models"),
            ("_info_ver_lbl",    "version_label"),
            ("_info_dev_lbl",    "developer"),
            ("_usb_title_lbl",   "usb_tab_title"),
            ("_install_hint_lbl","install_hint"),
            ("_sel_printer_lbl", "select_printer"),
        ]:
            lbl = getattr(self, attr, None)
            if lbl:
                try: lbl.config(text=self.t(key))
                except Exception: pass
        self._upd_browse_lbl()
        # Refresh model selector if config panel is open
        try: self._refresh_model_labels()
        except Exception: pass

    def _refresh_model_labels(self):
        """Dil dəyişdikdə LAN + USB model selectorlarını yenidən qur"""
        # LAN cfg paneli
        try:
            sel = self.ip_lb.curselection()
            if sel:
                ip = self.ip_lb.get(sel[-1]).strip()
                if ip:
                    self._show_cfg(ip)
            else:
                for w in self.cfg_frame.winfo_children():
                    try:
                        if w.cget("text") in ["← Printer seçin","← Select a printer",
                                              "← Yazıcı seçin","← Выберите принтер"]:
                            w.config(text=self.t("select_printer"))
                    except Exception:
                        pass
        except Exception:
            pass
        # USB model selector yenilə
        try:
            if hasattr(self, "_usb_model_frame"):
                for w in self._usb_model_frame.winfo_children():
                    w.destroy()
                self._model_sel(self._usb_model_frame, self.usb_model)
            if hasattr(self, "_usb_model_lbl"):
                self._usb_model_lbl.config(text=self.t("model"))
            if hasattr(self, "_usb_pname_lbl"):
                self._usb_pname_lbl.config(text=self.t("pname"))
        except Exception:
            pass



    def _detect_exe(self):
        b = get_bundled_exe()
        if os.path.exists(b): return b
        base = os.path.dirname(sys.executable) if getattr(sys,"frozen",False) \
               else os.path.dirname(os.path.abspath(__file__))
        for p in [os.path.join(base,"XPrinter Driver Setup V7.77.exe"),
                  r"D:\printer\XPrinter Driver Setup V7.77.exe",
                  os.path.join(os.path.expanduser("~"),"Desktop","XPrinter Driver Setup V7.77.exe")]:
            if os.path.exists(p): return p
        return ""

    # ══════════════════════════════════════════════════════════════
    #  TAB 1 — Driver
    # ══════════════════════════════════════════════════════════════
    def _build_t1(self):
        f = self.t1
        left = tk.Frame(f, bg=CL_BG)
        left.pack(side="left", fill="both", expand=True, padx=(18,8), pady=18)
        rw = tk.Frame(f, bg=CL_BLUE, width=3)
        rw.pack(side="right", fill="y", pady=18)
        right = tk.Frame(f, bg=CL_CARD, padx=24, pady=22, width=310)
        right.pack(side="right", fill="y", pady=18, padx=(0,18))
        right.pack_propagate(False)

        c1 = mk_card(left, padx=28, pady=24)
        c1.pack(fill="x")

        # Header row: badge + title
        hdr = tk.Frame(c1, bg=CL_CARD)
        hdr.pack(anchor="w", pady=(0,10))
        step_badge = tk.Frame(hdr, bg=CL_BLUE, padx=10, pady=3)
        step_badge.pack(side="left")
        tk.Label(step_badge, text="STEP 1", font=("Segoe UI",8,"bold"),
                 bg=CL_BLUE, fg=CL_WHITE).pack()

        tk.Label(c1, text="XPrinter Driver V7.77",
                 font=("Segoe UI",15,"bold"), bg=CL_CARD, fg=CL_WHITE).pack(anchor="w")
        self._install_hint_lbl = tk.Label(c1, text=self.t("install_hint"),
                 font=("Segoe UI",9), bg=CL_CARD, fg=CL_DIM)
        self._install_hint_lbl.pack(anchor="w", pady=(2,12))

        mk_div(c1, 2)

        # Big install button — with icon, full width, prominent
        btn_frame = tk.Frame(c1, bg=CL_BLUE, padx=2, pady=2)
        btn_frame.pack(fill="x", pady=(10,0))
        self.W["w_di"] = tk.Button(btn_frame, text="⬇   " + self.t("driver_install"),
                                    command=self._do_install,
                                    bg=CL_BLUE, fg=CL_WHITE, relief="flat", bd=0,
                                    font=("Segoe UI",12,"bold"), cursor="hand2",
                                    padx=24, pady=14, activebackground=CL_BLUE_D,
                                    activeforeground=CL_WHITE)
        self.W["w_di"].pack(fill="x")

        # Skip button — subtle but clear
        self.W["w_already"] = tk.Button(c1, text="→   " + self.t("already"),
                                         command=lambda: self.nb.select(1),
                                         bg=CL_BG2, fg=CL_BLUE_L, relief="flat", bd=0,
                                         font=("Segoe UI",10), cursor="hand2",
                                         padx=16, pady=10, activebackground=CL_CARD2,
                                         activeforeground=CL_WHITE)
        self.W["w_already"].pack(fill="x", pady=(6,0))

        # Subtle folder change link
        self.W["w_browse"] = tk.Label(c1, text="",
                                       bg=CL_CARD, fg=CL_BORDER,
                                       font=("Segoe UI",8,"underline"),
                                       cursor="hand2")
        self.W["w_browse"].pack(anchor="e", pady=(6,0))
        self.W["w_browse"].bind("<Button-1>", lambda e: self._browse_folder())
        self._upd_browse_lbl()

        mk_div(left, 12)
        self.log1 = mk_log(left, h=9)
        self.log1.pack(fill="both", expand=True)

        # Right info panel
        c_logo = tk.Canvas(right, width=36, height=36,
                           bg=CL_CARD, highlightthickness=0)
        c_logo.pack(anchor="w", pady=(0,10))
        draw_clopos_logo(c_logo, 1, 1, sq=16, gap=3, color=CL_BLUE_L, outline_w=1)

        self._about_title_lbl = tk.Label(right, text=self.t("about_title"),
                 font=("Segoe UI",12,"bold"), bg=CL_CARD, fg=CL_WHITE,
                 wraplength=275, justify="left")
        self._about_title_lbl.pack(anchor="w")

        mk_div(right, 10)

        self._about_text_lbl = tk.Label(right, text=self.t("about_text"),
                 font=("Segoe UI",10), bg=CL_CARD, fg=CL_SUB,
                 justify="left", wraplength=275, pady=2)
        self._about_text_lbl.pack(anchor="w")

        mk_div(right, 12)

        self._about_models_lbl = tk.Label(right, text=self.t("about_models"),
                 font=("Segoe UI",9), bg=CL_CARD, fg=CL_DIM)
        self._about_models_lbl.pack(anchor="w")
        tk.Label(right, text=self.t("models_footer"),
                 font=("Segoe UI",11,"bold"), bg=CL_CARD, fg=CL_BLUE_L,
                 wraplength=275, justify="left").pack(anchor="w", pady=(3,0))

        mk_div(right, 14)

        tk.Label(right, text="Made by Fuad Huseynov",
                 font=("Segoe UI",10,"bold"), bg=CL_CARD, fg=CL_SUB).pack(anchor="w")
        tk.Label(right, text="CloPos IT Team  ·  © 2026",
                 font=("Segoe UI",9), bg=CL_CARD, fg=CL_DIM).pack(anchor="w", pady=(2,0))

    def _browse_folder(self):
        """
        Quraşdırma qovluğunu seç.
        EXE dəyişmir — yalnız quraşdırılacaq YER dəyişir.
        Seçilməyibsə: default bundled temp yolu istifadə olunur.
        """
        folder = filedialog.askdirectory(
            title="XPrinter Driver-in quraşdırılacağı qovluğu seçin"
        )
        if folder:
            # Seçilmiş qovluqda EXE-nin tam yolunu qur
            exe_name = "XPrinter Driver Setup V7.77.exe"
            new_path = os.path.join(folder, exe_name)
            self.exe_path.set(new_path)
            log_add(self.log1, f"  📁  {self.t('folder_changed')}: {folder}")

    def _browse(self):
        """Legacy fallback"""
        p = filedialog.askopenfilename(filetypes=[("EXE","*.exe"),("*","*.*")])
        if p: self.exe_path.set(p)

    def _do_install(self):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.exists(exe):
            messagebox.showerror("", self.t("no_file")); return
        self.W["w_di"].config(state="disabled")
        ov = WaitOverlay(self.t1, self.t("waiting"))
        def run():
            ok = run_install_exe(exe, lambda m: self.after(0, log_add, self.log1, m), t_fn=self.t)
            self.after(0, ov.destroy)
            if ok:
                self.after(0, lambda: messagebox.showinfo(self.t("done"), self.t("drv_ok")))
                self.after(0, lambda: self.nb.select(1))
            self.after(0, lambda: self.W["w_di"].config(state="normal"))
        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════════
    #  TAB 2 — LAN  (scrollable, install button inside)
    # ══════════════════════════════════════════════════════════════
    def _build_t2(self):
        f = self.t2

        # Top scan bar — always visible
        top = mk_card(f, padx=16, pady=12)
        top.pack(fill="x", padx=18, pady=(18,6))
        self.W["w_nl"] = mk_lbl(top, self.t("net_label"),
                                 fg=CL_DIM, bg=CL_CARD, font=FONT_XS)
        self.W["w_nl"].grid(row=0, column=0, sticky="w", padx=(0,4))
        cb = ttk.Combobox(top, textvariable=self.net_var,
                          values=get_local_networks(), width=18, font=FONT_B)
        cb.grid(row=0, column=1, padx=(0,12))
        bind_touch_keyboard(cb)
        self.W["w_pl"] = mk_lbl(top, self.t("port_label"),
                                 fg=CL_DIM, bg=CL_CARD, font=FONT_XS)
        self.W["w_pl"].grid(row=0, column=2, padx=(0,4))
        ef, _ = mk_entry(top, self.port_var, 5)
        ef.grid(row=0, column=3, padx=(0,16))
        self.W["w_scan"] = mk_btn(top, self.t("scan"), self._scan, pad=(18,7))
        self.W["w_scan"].grid(row=0, column=4)

        self.progress = ttk.Progressbar(f, style="CL.Horizontal.TProgressbar",
                                         mode="determinate")
        self.progress.pack(fill="x", padx=18, pady=(0,6))

        # Main 3-column area — scrollable wrapper
        main_outer = tk.Frame(f, bg=CL_BG)
        main_outer.pack(fill="both", expand=True, padx=18, pady=(0,8))

        # ── Col 1: IP list (fixed, no scroll needed)
        lc = mk_card(main_outer)
        lc.pack(side="left", fill="y", padx=(0,6))
        self.W["w_found"] = mk_lbl(lc, self.t("found"),
                                    fg=CL_SUB, bg=CL_CARD, font=FONT_XS)
        self.W["w_found"].pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(lc, bg=CL_BORDER, height=1).pack(fill="x")
        self.ip_lb = tk.Listbox(lc, selectmode="extended",
                                 bg=CL_BG, fg=CL_TEXT,
                                 selectbackground=CL_BLUE_D,
                                 selectforeground=CL_WHITE,
                                 font=("Consolas",10), relief="flat",
                                 width=20, activestyle="none", bd=0)
        sy = ttk.Scrollbar(lc, orient="vertical", command=self.ip_lb.yview)
        self.ip_lb.config(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        self.ip_lb.pack(fill="both", expand=True)
        self.ip_lb.bind("<<ListboxSelect>>", self._ip_sel)
        br = tk.Frame(lc, bg=CL_CARD, pady=7, padx=8)
        br.pack(fill="x")
        self.W["w_selall"] = mk_btn(br, self.t("sel_all"),
            lambda: self.ip_lb.select_set(0,"end"),
            bg=CL_CARD2, fg=CL_TEXT, font=FONT_XS, pad=(8,4))
        self.W["w_selall"].pack(side="left")
        self.W["w_desel"] = mk_btn(br, self.t("desel"),
            lambda: self.ip_lb.selection_clear(0,"end"),
            bg=CL_CARD2, fg=CL_TEXT, font=FONT_XS, pad=(8,4))
        self.W["w_desel"].pack(side="left", padx=(4,0))

        # ── Col 2: Config — scrollable
        co_outer = tk.Frame(main_outer, bg=CL_BG)
        co_outer.pack(side="left", fill="both", padx=(0,6))
        co_outer.config(width=280)
        co_outer.pack_propagate(False)
        co_sc_cont, co_sc_inner = make_scrollable(co_outer, CL_CARD)
        co_sc_cont.pack(fill="both", expand=True)
        # Header always visible
        cfg_hdr = tk.Frame(co_sc_inner, bg=CL_CARD, padx=12)
        cfg_hdr.pack(fill="x", pady=(8,2))
        self.W["w_cfgt"] = mk_lbl(cfg_hdr, self.t("cfg"),
                                   fg=CL_SUB, bg=CL_CARD, font=FONT_XS)
        self.W["w_cfgt"].pack(side="left")
        tk.Frame(co_sc_inner, bg=CL_BORDER, height=1).pack(fill="x")
        self.cfg_frame = tk.Frame(co_sc_inner, bg=CL_CARD)
        self.cfg_frame.pack(fill="both", expand=True, padx=12, pady=10)
        self._sel_printer_lbl = mk_lbl(self.cfg_frame, self.t("select_printer"),
               fg=CL_DIM, bg=CL_CARD, font=FONT_S)
        self._sel_printer_lbl.pack(expand=True)

        # Install button — inside scrollable config, bottom
        install_wrap = tk.Frame(co_sc_inner, bg=CL_CARD, padx=12, pady=10)
        install_wrap.pack(fill="x")
        self.W["w_isel"] = mk_btn(install_wrap, self.t("install_sel"),
                                   self._lan_install,
                                   font=FONT_H3, pad=(12,8))
        self.W["w_isel"].config(state="disabled")
        self.W["w_isel"].pack(fill="x")

        # ── Col 3: Log
        rc = mk_card(main_outer)
        rc.pack(side="left", fill="both", expand=True)
        self.W["w_logl"] = mk_lbl(rc, self.t("log"),
                                   fg=CL_SUB, bg=CL_CARD, font=FONT_XS)
        self.W["w_logl"].pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(rc, bg=CL_BORDER, height=1).pack(fill="x")
        self.log2 = mk_log(rc)
        self.log2.pack(fill="both", expand=True, padx=6, pady=6)
        self.W["w_clear"] = mk_btn(rc, self.t("clear"),
            lambda: log_clear(self.log2),
            bg=CL_BG2, fg=CL_DIM, font=FONT_XS, pad=(8,3))
        self.W["w_clear"].pack(anchor="e", padx=8, pady=(0,6))

    def _ip_sel(self, event=None):
        sel = self.ip_lb.curselection()
        if not sel: return
        self._show_cfg(self.ip_lb.get(sel[-1]).strip())

    def _show_cfg(self, ip):
        for w in self.cfg_frame.winfo_children(): w.destroy()
        if ip not in self.lan_cfgs:
            self.lan_cfgs[ip] = {"model": tk.StringVar(value="XP-80C"),
                                  "name":  tk.StringVar(value=ip)}
        cfg = self.lan_cfgs[ip]
        mk_lbl(self.cfg_frame, ip, fg=CL_TEXT, bg=CL_CARD,
               font=("Segoe UI",11,"bold")).pack(anchor="w", pady=(0,10))
        self.W["w_pn_l"] = mk_lbl(self.cfg_frame, self.t("pname"),
                                   fg=CL_DIM, bg=CL_CARD, font=FONT_XS)
        self.W["w_pn_l"].pack(anchor="w")
        ef, _ = mk_entry(self.cfg_frame, cfg["name"], 22)
        ef.pack(anchor="w", pady=(3,10))
        self.W["w_ml_l"] = mk_lbl(self.cfg_frame, self.t("model"),
                                   fg=CL_DIM, bg=CL_CARD, font=FONT_XS)
        self.W["w_ml_l"].pack(anchor="w")
        self._model_sel(self.cfg_frame, cfg["model"])
        mk_div(self.cfg_frame, 8)

        # Düymələr sırası: Hamısına tətbiq et + Test Print
        btn_row = tk.Frame(self.cfg_frame, bg=CL_CARD)
        btn_row.pack(anchor="w", fill="x")

        self.W["w_apply_all"] = mk_btn(btn_row, self.t("apply_all"),
               lambda: self._apply_all(ip),
               bg=CL_CARD2, fg=CL_BLUE_L, font=FONT_XS, pad=(10,5))
        self.W["w_apply_all"].pack(side="left", padx=(0,6))

        # Test Print — quraşdırılmasa belə birbaşa TCP 9100-ə göndərir
        self.W["w_tpl"] = mk_btn(btn_row, self.t("test_print_lan"),
               lambda i=ip: self._do_lan_test_print(i),
               bg=CL_CARD2, fg=CL_GREEN, font=FONT_XS, pad=(10,5))
        self.W["w_tpl"].pack(side="left")

    def _model_sel(self, parent, var):
        groups = {
            "58 mm": [("XP-58",False),("XP-58C",True)],
            "80 mm": [("XP-80",False),("XP-80C",True),("XP-90",True)],
            "76 mm": [("XP-76",False),("XP-76C",True)],
        }
        mf = tk.Frame(parent, bg=CL_CARD)
        mf.pack(anchor="w", pady=(4,0))
        for paper, items in groups.items():
            hf = tk.Frame(mf, bg=CL_CARD)
            hf.pack(anchor="w", fill="x", pady=(7,2))
            tk.Label(hf, text=paper, font=("Segoe UI",8,"bold"),
                     bg=CL_CARD2, fg=CL_BLUE_L,
                     padx=8, pady=2).pack(side="left")
            tk.Frame(hf, bg=CL_BORDER, height=1).pack(
                side="left", fill="x", expand=True, padx=(6,0), pady=6)
            for val, has_cut in items:
                row = tk.Frame(mf, bg=CL_CARD, pady=2)
                row.pack(anchor="w", fill="x")
                rb = tk.Radiobutton(row, variable=var, value=val,
                               bg=CL_CARD, fg=CL_WHITE,
                               selectcolor=CL_BLUE_D,
                               activebackground=CL_CARD,
                               cursor="hand2", relief="flat", bd=0)
                rb.pack(side="left")
                tk.Label(row, text=val, font=("Segoe UI",9,"bold"),
                         bg=CL_CARD, fg=CL_WHITE,
                         width=7, anchor="w").pack(side="left")
                if has_cut:
                    tk.Label(row, text=f" ✂  {self.t('with_cutter')} ",
                             font=("Segoe UI",8,"bold"),
                             bg=CL_CUT, fg=CL_BG,
                             padx=4, pady=2).pack(side="left", padx=(2,0))
                else:
                    tk.Label(row, text=f"  {self.t('no_cutter')}  ",
                             font=("Segoe UI",8),
                             bg=CL_CARD2, fg=CL_SUB,
                             padx=4, pady=2).pack(side="left", padx=(2,0))

    def _apply_all(self, src):
        sel = self.ip_lb.curselection()
        c = self.lan_cfgs.get(src)
        if not c: return
        for i in sel:
            ip = self.ip_lb.get(i).strip()
            if ip not in self.lan_cfgs:
                self.lan_cfgs[ip] = {"model": tk.StringVar(value=c["model"].get()),
                                      "name":  tk.StringVar(value=ip)}
            else:
                self.lan_cfgs[ip]["model"].set(c["model"].get())
        log_add(self.log2, f"  → {len(sel)}× {c['model'].get()}")

    def _do_lan_test_print(self, ip):
        """
        LAN printer-ə birbaşa TCP 9100 üzərindən test çapı göndər.
        Printer quraşdırılmasa belə işləyir.
        """
        def run():
            self.after(0, log_add, self.log2,
                       f"\n▸  Test Print → {ip}:{PORT}")
            try:
                import socket
                # ESC/POS test səhifəsi
                test_data = (
                    b"\x1b\x40"                  # ESC @ — printer sıfırla
                    b"\x1b\x61\x01"              # ESC a 1 — mərkəzlə
                    b"\x1b\x21\x30"              # ESC ! — böyük şrift
                    b"CloPos XPrinter\n"
                    b"\x1b\x21\x00"              # normal şrift
                    b"--- Test Print ---\n"
                    b"\x1b\x61\x00"              # sola hizala
                    b"IP: " + ip.encode() + b"\n"
                    b"Port: 9100\n"
                    b"\n\n\n"
                    b"\x1d\x56\x41\x03"          # GS V A — kəs
                )
                with socket.create_connection((ip, PORT), timeout=5) as s:
                    s.sendall(test_data)
                self.after(0, log_add, self.log2,
                           f"  ✓  {self.t('test_ok')}", CL_GREEN)
            except Exception as e:
                self.after(0, log_add, self.log2,
                           f"  ✗  {self.t('test_fail')}: {e}", CL_RED)

        threading.Thread(target=run, daemon=True).start()

    def _scan(self):
        self.ip_lb.delete(0,"end"); self.lan_cfgs.clear()
        self.W["w_isel"].config(state="disabled")
        self.W["w_scan"].config(state="disabled")
        self.progress["value"] = 0
        log_add(self.log2, f"\n▸  {self.net_var.get()}")
        self.status_var.set(self.t("status_scan"))
        def run():
            res = scan_network(self.net_var.get().strip(),
                cb_prog=lambda v: self.after(0, self.progress.configure, {"value":v}),
                cb_log=lambda m: self.after(0, log_add, self.log2, m))
            self.after(0, self._scan_done, res)
        threading.Thread(target=run, daemon=True).start()

    def _scan_done(self, res):
        self.W["w_scan"].config(state="normal")
        self.progress["value"] = 100
        if res:
            for ip in res:
                self.ip_lb.insert("end", f"  {ip}")
                self.lan_cfgs[ip] = {"model": tk.StringVar(value="XP-80C"),
                                      "name":  tk.StringVar(value=ip)}
            self.W["w_isel"].config(state="normal")
            self.status_var.set(self.t("printers_found").format(len(res)))
            log_add(self.log2, "\n  " + self.t("printers_found").format(len(res)))
        else:
            self.status_var.set(self.t("status_ready"))
            log_add(self.log2, "  " + self.t("printers_found").format(0))

    def _lan_install(self):
        sel = self.ip_lb.curselection()
        if not sel: messagebox.showwarning("", self.t("sel_one")); return
        tasks = [(self.ip_lb.get(i).strip(),
                  self.lan_cfgs.get(self.ip_lb.get(i).strip(),{}).get(
                      "model", tk.StringVar(value="XP-80C")).get(),
                  self.lan_cfgs.get(self.ip_lb.get(i).strip(),{}).get(
                      "name", tk.StringVar(value=self.ip_lb.get(i).strip())).get())
                 for i in sel]
        s = "\n".join(f"  {t[0]}  →  {t[2]}  [{t[1]}]" for t in tasks)
        if not messagebox.askyesno("", self.t("confirm_ins").format(len(tasks), s)): return
        self.W["w_isel"].config(state="disabled")
        self.W["w_scan"].config(state="disabled")
        ov = WaitOverlay(self.t2, self.t("waiting"))
        log_add(self.log2, "\n▸  " + self.t("installing_n").format(len(tasks)))
        def run():
            ok = 0
            for ip, model, name in tasks:
                self.after(0, log_add, self.log2, f"\n  {ip}  →  {name}  [{model}]")
                if install_lan(ip, model, name,
                               lambda m: self.after(0, log_add, self.log2, m),
                               t_fn=self.t): ok += 1
            self.after(0, ov.destroy)
            self.after(0, self._lan_done, ok, len(tasks))
        threading.Thread(target=run, daemon=True).start()

    def _lan_done(self, ok, total):
        self.W["w_isel"].config(state="normal")
        self.W["w_scan"].config(state="normal")
        msg = self.t("status_done").format(ok, total)
        self.status_var.set(msg)
        log_add(self.log2, f"\n  ✓  {msg}")
        messagebox.showinfo(self.t("done"), msg)

    # ══════════════════════════════════════════════════════════════
    #  TAB 3 — USB  (scrollable form)
    # ══════════════════════════════════════════════════════════════
    def _build_t3(self):
        f = self.t3
        # 2 sütun: sol scrollable form, sağ log
        main = tk.Frame(f, bg=CL_BG)
        main.pack(fill="both", expand=True, padx=18, pady=18)

        # Sol: scrollable
        left_outer = tk.Frame(main, bg=CL_BG)
        left_outer.pack(side="left", fill="y", padx=(0,8))
        left_outer.config(width=320)
        left_outer.pack_propagate(False)

        sc_container, sc_inner = make_scrollable(left_outer, CL_CARD)
        sc_container.pack(fill="both", expand=True)
        form = sc_inner
        form.config(padx=20, pady=18)

        step = tk.Frame(form, bg=CL_BLUE, padx=8, pady=2)
        step.pack(anchor="w", pady=(0,6))
        tk.Label(step, text="USB", font=("Segoe UI",8,"bold"),
                 bg=CL_BLUE, fg=CL_WHITE).pack()
        self._usb_title_lbl = tk.Label(form, text=self.t("usb_tab_title"),
                 font=("Segoe UI",13,"bold"), bg=CL_CARD, fg=CL_WHITE)
        self._usb_title_lbl.pack(anchor="w")
        mk_div(form, 12)

        self.W["w_chusb"] = mk_btn(form, self.t("check_usb"),
                                    self._check_usb, pad=(16,10))
        self.W["w_chusb"].config(font=("Segoe UI",10,"bold"))
        self.W["w_chusb"].pack(fill="x", pady=(0,12))
        mk_div(form, 6)

        mk_lbl(form, self.t("iface_usb"), fg=CL_DIM, bg=CL_CARD, font=FONT_XS).pack(anchor="w")
        self._usb_ports = get_usb_ports_list()
        self.usb_port_var = tk.StringVar(value=self._usb_ports[0])
        self.usb_cb = ttk.Combobox(form, textvariable=self.usb_port_var,
                                    values=self._usb_ports, width=24, font=FONT_B)
        self.usb_cb.pack(anchor="w", pady=(3,12), ipady=3)

        self._usb_pname_lbl = mk_lbl(form, self.t("pname"), fg=CL_DIM, bg=CL_CARD, font=FONT_XS)
        self._usb_pname_lbl.pack(anchor="w")
        self.usb_name = tk.StringVar(value="USB-Printer")
        ef, _ = mk_entry(form, self.usb_name, 22)
        ef.pack(anchor="w", pady=(3,12))

        self._usb_model_lbl = mk_lbl(form, self.t("model"), fg=CL_DIM, bg=CL_CARD, font=FONT_XS)
        self._usb_model_lbl.pack(anchor="w")
        self.usb_model = tk.StringVar(value="XP-80C")
        self._usb_model_frame = tk.Frame(form, bg=CL_CARD)
        self._usb_model_frame.pack(anchor="w", fill="x")
        self._model_sel(self._usb_model_frame, self.usb_model)

        mk_div(form, 14)
        self.W["w_usb_inst"] = mk_btn(form, self.t("usb_install"),
               self._usb_install, pad=(22,11))
        self.W["w_usb_inst"].config(font=("Segoe UI",11,"bold"))
        self.W["w_usb_inst"].pack(fill="x")

        # Sağ: log (kiçik)
        rc = mk_card(main)
        rc.pack(side="left", fill="both", expand=True)
        mk_lbl(rc, "Log", fg=CL_SUB, bg=CL_CARD, font=FONT_XS).pack(
            anchor="w", padx=12, pady=(10,4))
        tk.Frame(rc, bg=CL_BORDER, height=1).pack(fill="x")
        self.log3 = mk_log(rc, h=6)   # daha kiçik log
        self.log3.pack(fill="both", expand=True, padx=6, pady=6)

    def _check_usb(self):
        """
        XPrinter 7.77 davranışı:
        USB tapıldı → port seç + test çapı göndər
        Tapılmadı  → error messagebox
        """
        log_add(self.log3, "\n  " + self.t("usb_checking"))
        self.W["w_chusb"].config(state="disabled")
        def run():
            port, name = check_usb_printer()
            if port:
                msg = self.t("usb_found").format(port)
                self.after(0, log_add, self.log3, f"  ✓  {name}  ({port})", CL_GREEN)
                ports = get_usb_ports_list()
                if port not in ports: ports.insert(0, port)
                self.after(0, lambda: self.usb_cb.config(values=ports))
                self.after(0, lambda: self.usb_port_var.set(port))
                # Test page — printer adını tapıb göndər
                pname = self.usb_name.get().strip() or "USB-Printer"
                self.after(0, log_add, self.log3, "  → " + self.t("test_sending").format(pname))
                ok, err = print_test_usb(pname)
                if ok:
                    self.after(0, log_add, self.log3, "  ✓  " + self.t("test_sent_ok"), CL_GREEN)
                    full_msg = msg + "\n\n✓ " + self.t("test_sent_ok")
                else:
                    self.after(0, log_add, self.log3,
                               f"  ℹ  Test çapı: {err[:60] if err else 'printer hələ qeydiyyatda deyil'}", CL_AMBER)
                    after_reg = self.t("test_after_reg")
                    full_msg = f"{msg}\n\n({after_reg})"
                self.after(0, lambda: messagebox.showinfo("USB", full_msg))
            else:
                msg = self.t("usb_not_found")
                self.after(0, log_add, self.log3, f"  ✗  {msg}", CL_AMBER)
                self.after(0, lambda: messagebox.showwarning("USB", msg))
            self.after(0, lambda: self.W["w_chusb"].config(state="normal"))
        threading.Thread(target=run, daemon=True).start()

    def _usb_install(self):
        uport = self.usb_port_var.get().strip()
        name  = self.usb_name.get().strip() or "USB-Printer"
        model = self.usb_model.get()
        if not messagebox.askyesno("",
                f"USB Printer:\n\n  Port    {uport}\n  Ad      {name}\n  Model   {model}\n\nDavam?"): return
        log_add(self.log3, f"\n  {uport}  →  {name}  [{model}]")
        ov = WaitOverlay(self.t3, self.t("waiting"))
        def run():
            ok = install_usb(uport, model, name,
                             lambda m: self.after(0, log_add, self.log3, m),
                             t_fn=self.t)
            self.after(0, ov.destroy)
            col = CL_GREEN if ok else CL_RED
            msg = f"  ✓  '{name}'" if ok else "  ✗  Xəta baş verdi"
            self.after(0, log_add, self.log3, f"\n{msg}", col)
            self.after(0, lambda: messagebox.showinfo(self.t("done"),
                       f"'{name}' OK!" if ok else "Xəta baş verdi"))
        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════════
    #  TAB 4 — Qurulmuş Cihazlar (IP + MAC, kopyala)
    # ══════════════════════════════════════════════════════════════
    def _build_t4(self):
        f = self.t4
        top = mk_card(f, padx=16, pady=12)
        top.pack(fill="x", padx=18, pady=(18,8))
        self.W["w_inst"] = mk_lbl(top, self.t("installed"),
                                   fg=CL_WHITE, bg=CL_CARD, font=FONT_H2)
        self.W["w_inst"].pack(side="left")
        self.W["w_ref"] = mk_btn(top, self.t("refresh"),
                                  self._load_list, pad=(14,6))
        self.W["w_ref"].pack(side="right")

        # Treeview: Ad | Port/IP | MAC | Driver
        tf = tk.Frame(f, bg=CL_BG)
        tf.pack(fill="both", expand=True, padx=18, pady=(0,4))
        cols = ("name","port","mac","drv")
        self.W["tree"] = ttk.Treeview(tf, columns=cols, show="headings",
                                       style="CL.Treeview", selectmode="extended")
        tree = self.W["tree"]
        tree.heading("name", text=self.t("col_name"))
        tree.heading("port", text=self.t("col_port"))
        tree.heading("mac",  text=self.t("col_mac"))
        tree.heading("drv",  text=self.t("col_drv"))
        tree.column("name", width=260, minwidth=120)
        tree.column("port", width=160, minwidth=80)
        tree.column("mac",  width=160, minwidth=100)
        tree.column("drv",  width=260, minwidth=100)
        vsb = ttk.Scrollbar(tf, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=tree.xview)
        tree.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        tree.bind("<Double-1>", lambda e: self._do_rename())
        tree.bind("<Button-3>", self._tree_context)  # sağ klik

        # Copy bar
        copy_bar = tk.Frame(f, bg=CL_BG, padx=18)
        copy_bar.pack(fill="x", pady=(2,0))
        self.W["w_copy_ip"] = mk_btn(copy_bar, f"⎘  {self.t('copy_ip')}", self._copy_ip,
               bg=CL_CARD2, fg=CL_TEXT, font=FONT_S, pad=(12,5))
        self.W["w_copy_ip"].pack(side="left", padx=(0,4))
        self.W["w_copy_mac"] = mk_btn(copy_bar, f"⎘  {self.t('copy_mac')}", self._copy_mac,
               bg=CL_CARD2, fg=CL_TEXT, font=FONT_S, pad=(12,5))
        self.W["w_copy_mac"].pack(side="left")

        # Log
        bot = tk.Frame(f, bg=CL_BG, padx=18, pady=4)
        bot.pack(fill="x")
        self.log4 = mk_log(bot, h=4)
        self.log4.pack(fill="x")

        # Action bar
        brow = tk.Frame(bot, bg=CL_BG)
        brow.pack(fill="x", pady=(8,0))
        self.W["w_sala"] = mk_btn(brow, self.t("sel_all_list"),
            self._sel_all, bg=CL_CARD2, fg=CL_TEXT, font=FONT_S, pad=(14,8))
        self.W["w_sala"].pack(side="left", padx=(0,6))
        self.W["w_ren"] = mk_btn(brow, "✏  " + self.t("rename"),
            self._do_rename, bg=CL_GREEN, fg="#0F1A10",
            font=("Segoe UI",10,"bold"), pad=(16,8))
        self.W["w_ren"].pack(side="left", padx=(0,6))
        self.W["w_pt"] = mk_btn(brow, "🖨  " + self.t("print_test"),
            self._do_print_test, bg=CL_BLUE, pad=(16,8))
        self.W["w_pt"].config(font=("Segoe UI",10,"bold"))
        self.W["w_pt"].pack(side="left", padx=(0,6))
        self.W["w_del"] = mk_btn(brow, self.t("delete"),
            self._do_delete, bg=CL_RED, pad=(16,8))
        self.W["w_del"].config(font=("Segoe UI",10,"bold"))
        self.W["w_del"].pack(side="left")

    def _tree_context(self, event):
        """Sağ klik — context menu"""
        tree = self.W["tree"]
        iid = tree.identify_row(event.y)
        if not iid: return
        tree.selection_set(iid)
        menu = tk.Menu(self, tearoff=0, bg=CL_CARD, fg=CL_TEXT,
                       activebackground=CL_BLUE, activeforeground=CL_WHITE,
                       relief="flat", bd=0)
        menu.add_command(label=f"⎘  {self.t('copy_ip')}",  command=self._copy_ip)
        menu.add_command(label=f"⎘  {self.t('copy_mac')}", command=self._copy_mac)
        menu.add_separator()
        menu.add_command(label=self.t("rename"),      command=self._do_rename)
        menu.add_command(label="🖨  "+self.t("print_test"), command=self._do_print_test)
        menu.add_separator()
        menu.add_command(label=self.t("delete"),      command=self._do_delete)
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    def _get_selected_values(self, col_idx):
        tree = self.W["tree"]
        sel = tree.selection()
        return [str(tree.item(s)["values"][col_idx]) for s in sel]

    def _copy_ip(self):
        tree = self.W["tree"]
        sel = tree.selection()
        if not sel: return
        vals = []
        for s in sel:
            v = tree.item(s)["values"]
            # port sütunu: "IP_192_168_1_10" formatında ola bilər, ya da IP birbaşa
            port = str(v[1])
            ip = port[3:].replace("_",".") if port.startswith("IP_") else port
            if ip: vals.append(ip)
        if vals:
            self.clipboard_clear()
            self.clipboard_append("\n".join(vals))
            self.status_var.set(self.t("copied"))

    def _copy_mac(self):
        tree = self.W["tree"]
        sel = tree.selection()
        if not sel: return
        vals = [str(tree.item(s)["values"][2]) for s in sel if str(tree.item(s)["values"][2]) != "—"]
        if vals:
            self.clipboard_clear()
            self.clipboard_append("\n".join(vals))
            self.status_var.set(self.t("copied"))

    def _sel_all(self):
        tree = self.W["tree"]
        tree.selection_set(tree.get_children())

    def _on_tab(self, event):
        if self.nb.index("current") == 3:
            self._load_list()

    def _load_list(self):
        tree = self.W["tree"]
        for r in tree.get_children(): tree.delete(r)
        ov = WaitOverlay(self.t4, self.t("loading"))
        def run():
            rows = get_printers_with_mac()
            self.after(0, ov.destroy)
            self.after(0, self._fill_tree_initial, rows)
        threading.Thread(target=run, daemon=True).start()

    def _fill_tree_initial(self, rows):
        """Əvvəl printerleri göstər, MAC-ları arxa planda yüklə"""
        tree = self.W["tree"]
        self._printer_rows = rows
        for name, port, ip, drv in rows:
            tree.insert("","end", iid=name, values=(name, port, "…", drv))
        self.status_var.set(f"{len(rows)} cihaz")
        # MAC-ları arxa planda yüklə
        def load_macs():
            for name, port, ip, drv in rows:
                if ip:
                    mac = self._mac_cache.get(ip)
                    if not mac:
                        mac = get_mac_for_ip(ip)
                        self._mac_cache[ip] = mac
                else:
                    mac = "—"
                self.after(0, self._update_mac, name, mac)
        threading.Thread(target=load_macs, daemon=True).start()

    def _update_mac(self, name, mac):
        tree = self.W["tree"]
        try:
            vals = list(tree.item(name)["values"])
            if len(vals) >= 3:
                vals[2] = mac
                tree.item(name, values=vals)
        except Exception:
            pass

    def _do_rename(self):
        tree = self.W["tree"]
        sel = tree.selection()
        if not sel: messagebox.showwarning("", self.t("sel_one")); return
        old = str(tree.item(sel[0])["values"][0])
        def on_ok(new_name):
            new_name = new_name.strip()
            if not new_name or new_name == old: return
            log_add(self.log4, f"  ✏  '{old}'  →  '{new_name}'")
            ov = WaitOverlay(self.t4, self.t("waiting"))
            def run():
                ok, err = rename_printer(old, new_name)
                self.after(0, ov.destroy)
                if ok:
                    self.after(0, log_add, self.log4, "  ✓  OK", CL_GREEN)
                    self.after(0, self._load_list)
                else:
                    self.after(0, log_add, self.log4, f"  ✗  {err}", CL_RED)
            threading.Thread(target=run, daemon=True).start()
        RenameDialog(self, old, self.t, on_ok)

    def _do_print_test(self):
        """
        Test çapı:
        - LAN printer (IP var): əvvəl TCP 9100 yoxla, cavab gəlməyibsə dərhal error
        - USB printer: birbaşa WMI
        Timeout gözləmir — fast fail.
        """
        tree = self.W["tree"]
        sel = tree.selection()
        if not sel: messagebox.showwarning("", self.t("sel_one")); return

        items = []
        for s in sel:
            v = tree.item(s)["values"]
            name = str(v[0])
            port = str(v[1])
            ip = port[3:].replace("_",".") if port.startswith("IP_") else ""
            items.append((name, port, ip))

        log_add(self.log4, f"\n  Test çapı: {', '.join(n for n,_,_ in items)}")
        self.W["w_pt"].config(state="disabled")
        ov = WaitOverlay(self.t4, self.t("waiting"))
        results = []

        def run():
            for name, port, ip in items:
                self.after(0, log_add, self.log4, f"  → {name}…")
                if ip:
                    ok, err = print_test_lan(ip, name)
                else:
                    ok, err = print_test_usb(name)

                results.append((name, ok, err))
                key = "test_ok" if ok else "test_fail"
                col = CL_GREEN if ok else CL_RED
                msg = f"  {self.t(key)}: {name}"
                if not ok and err:
                    msg += f"  —  {err[:80]}"
                self.after(0, log_add, self.log4, msg, col)

            self.after(0, ov.destroy)
            self.after(0, self._print_test_done, results)

        threading.Thread(target=run, daemon=True).start()

    def _print_test_done(self, results):
        self.W["w_pt"].config(state="normal")
        ok_count = sum(1 for _,ok,_ in results if ok)
        lines = []
        for name, ok, err in results:
            if ok:
                lines.append(f"✓  {name}")
            else:
                e_short = err[:70] if err else "xəta"
                lines.append(f"✗  {name}  —  {e_short}")
        summary = f"{ok_count}/{len(results)} uğurlu\n\n" + "\n".join(lines)
        if ok_count == len(results):
            messagebox.showinfo(self.t("done"), summary)
        else:
            messagebox.showwarning(self.t("done"), summary)

    def _do_delete(self):
        tree = self.W["tree"]
        sel = tree.selection()
        if not sel: messagebox.showwarning("", self.t("sel_one")); return
        names = [str(tree.item(s)["values"][0]) for s in sel]
        s = "\n".join(f"  • {n}" for n in names)
        if not messagebox.askyesno("", self.t("confirm_del").format(s)): return
        self.W["w_del"].config(state="disabled")
        log_add(self.log4, "\n  " + self.t("deleting_n").format(len(names)))
        ov = WaitOverlay(self.t4, self.t("waiting"))
        def run():
            ok = sum(delete_printer(n,
                     lambda m: self.after(0, log_add, self.log4, m),
                     t_fn=self.t) for n in names)
            self.after(0, ov.destroy)
            self.after(0, self._del_done, ok, len(names))
        threading.Thread(target=run, daemon=True).start()

    def _del_done(self, ok, total):
        self.W["w_del"].config(state="normal")
        msg = self.t("status_del").format(ok)
        self.status_var.set(msg)
        log_add(self.log4, f"  ✓  {msg}", CL_GREEN)
        self._load_list()
        messagebox.showinfo(self.t("done"), msg)

    # ══════════════════════════════════════════════════════════════
    #  TAB 5 — Məlumat (Info)
    # ══════════════════════════════════════════════════════════════
    def _build_t5(self):
        f = self.t5
        outer = tk.Frame(f, bg=CL_BG)
        outer.pack(fill="both", expand=True)
        center = tk.Frame(outer, bg=CL_BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        sq, gap = 26, 6
        total = sq*2+gap
        logo_c = tk.Canvas(center, width=total+4, height=total+4,
                           bg=CL_BG, highlightthickness=0)
        logo_c.pack(pady=(0,14))
        draw_clopos_logo(logo_c, 2, 2, sq=sq, gap=gap, color=CL_WHITE, outline_w=2)

        # App name
        nr = tk.Frame(center, bg=CL_BG)
        nr.pack()
        tk.Label(nr, text="clopos", font=("Segoe UI",22,"bold"),
                 bg=CL_BG, fg=CL_WHITE).pack(side="left")
        tk.Label(nr, text="  ×  ", font=("Segoe UI",18),
                 bg=CL_BG, fg=CL_BORDER).pack(side="left")
        tk.Label(nr, text="xprinter", font=("Segoe UI",22,"bold"),
                 bg=CL_BG, fg=CL_BLUE_L).pack(side="left")
        tk.Label(center, text=f"Auto-Installer  ·  v{VERSION}",
                 font=("Segoe UI",10), bg=CL_BG, fg=CL_DIM).pack(pady=(4,18))

        mk_div(center, 6)

        # Info card
        card = mk_card(center, padx=32, pady=24)
        card.pack(padx=0, pady=8)
        card.config(width=420)

        # Info rows — dynamic (stored for lang update)
        self._info_ver_lbl = tk.Label(card, text=self.t("version_label"),
                                       font=("Segoe UI",11,"bold"), bg=CL_CARD, fg=CL_TEXT)
        self._info_ver_lbl.pack(anchor="w", pady=3)
        self._info_dev_lbl = tk.Label(card, text=self.t("developer"),
                                       font=("Segoe UI",11), bg=CL_CARD, fg=CL_SUB)
        self._info_dev_lbl.pack(anchor="w", pady=3)
        tk.Label(card, text="CloPos IT Team  ·  © 2026",
                  font=("Segoe UI",10), bg=CL_CARD, fg=CL_DIM).pack(anchor="w", pady=3)

        mk_div(card, 12)

        # Website row
        site_row = tk.Frame(card, bg=CL_CARD)
        site_row.pack(anchor="w", pady=4)
        tk.Label(site_row, text="🌐 ", font=("Segoe UI",11),
                 bg=CL_CARD, fg=CL_SUB).pack(side="left")
        site_lbl = tk.Label(site_row, text="clopos.com",
                            font=("Segoe UI",11,"underline"),
                            bg=CL_CARD, fg=CL_BLUE_L, cursor="hand2")
        site_lbl.pack(side="left")
        site_lbl.bind("<Button-1>", lambda e: None)

        mk_div(card, 14)

        # Buttons row
        btn_row = tk.Frame(card, bg=CL_CARD)
        btn_row.pack(fill="x")

        # PDF User Guide button — text from t("user_guide")
        self.W["w_pdf"] = mk_btn(btn_row, self.t("user_guide"),
                          self._open_pdf,
                          bg=CL_CARD2, fg=CL_TEXT,
                          font=("Segoe UI",10,"bold"), pad=(18,10))
        self.W["w_pdf"].pack(side="left", padx=(0,8), fill="x", expand=True)

        # Check update button
        self.W["w_upd"] = mk_btn(btn_row, self.t("check_update"),
                                  self._check_update,
                                  bg=CL_BLUE, pad=(18,10))
        self.W["w_upd"].config(font=("Segoe UI",10,"bold"))
        self.W["w_upd"].pack(side="left", fill="x", expand=True)

    def _open_pdf(self):
        """
        PDF user guide-ı aç.
        Aktiv dilə uyğun faylı axtar, tapılmazsa ingilis versiyasını aç.
        """
        lang = self.lang.get()  # AZ, EN, TR, RU
        base_candidates = [
            os.path.join(sys._MEIPASS, "") if getattr(sys,"frozen",False) else "",
            os.path.dirname(sys.executable),
            os.path.dirname(os.path.abspath(__file__)) if not getattr(sys,"frozen",False) else "",
            os.path.join(os.path.expanduser("~"),"Desktop"),
            r"D:\printer",
        ]
        pdf_names = [
            f"CloPos_XPrinter_UserGuide.pdf",   # single combined 4-lang PDF
        ]
        for base in base_candidates:
            if not base: continue
            for name in pdf_names:
                p = os.path.join(base, name)
                if os.path.exists(p):
                    try:
                        os.startfile(p)
                        return
                    except Exception as e:
                        messagebox.showerror("", str(e))
                        return
        messagebox.showwarning(
            "PDF not found",
            "CloPos_XPrinter_UserGuide.pdf tapılmadı.\n"
            "PDF-i EXE ilə eyni qovluğa yerləşdirin."
        )

    def _check_update(self):
        """
        GitHub-da ən son release-i yoxla.
        Yalnız düyməyə basanda işləyir — proqram açılarkən işləmir.
        """
        self.W["w_upd"].config(state="disabled",
                               text="⏳  " + self.t("update_checking"))
        self.status_var.set(self.t("update_checking"))

        def run():
            has_update, new_tag, url, err = check_for_update()
            self.after(0, self._update_done, has_update, new_tag, url, err)

        threading.Thread(target=run, daemon=True).start()

    def _update_done(self, has_update, new_tag, url, err):
        """Update yoxlaması bitdikdə UI-ı yenilə"""
        self.W["w_upd"].config(state="normal",
                               text=self.t("check_update"))
        self.status_var.set(self.t("status_ready"))

        if err:
            messagebox.showwarning(
                self.t("update_title"),
                self.t("update_error").format(err)
            )
            return

        if has_update:
            # Yeni versiya var — endir sual
            answer = messagebox.askyesno(
                self.t("update_title"),
                self.t("update_found").format(new_tag.lstrip("v")),
            )
            if answer and url:
                import webbrowser
                webbrowser.open(url)
        else:
            # Ən yeni versiya
            messagebox.showinfo(
                self.t("update_title"),
                self.t("update_uptodate").format(VERSION)
            )


if __name__ == "__main__":
    auto_update_and_restart()
    App().mainloop()
