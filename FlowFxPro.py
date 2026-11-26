# FlowFx Pro - PC / FiveM FPS Booster (Windows 10/11)  *ต้องรันแบบ Administrator*
import ctypes, os, sys, re, subprocess, threading, time, glob, shutil, collections, wave, tkinter as tk
from tkinter import ttk, messagebox
try: import winreg
except ImportError: winreg = None

if os.name == "nt" and not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(f'"{a}"' for a in sys.argv), None, 1); sys.exit()

_d = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)); os.environ["PATH"] = _d + os.pathsep + os.environ.get("PATH", "")  # หา ffmpeg ในโฟลเดอร์แอป
BG, PN, AC, AC2, FG, DIM = "#0a0a14", "#14142a", "#00e5ff", "#b14cff", "#eaeaf8", "#8a8aa8"
NW = 0x08000000
def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True, creationflags=NW, errors="ignore")
    return (r.stdout or "") + (r.stderr or "")
def ps(c):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", c], capture_output=True, text=True, creationflags=NW, errors="ignore")
    return (r.stdout or "") + (r.stderr or "")
def reg(k, n, v, t="REG_DWORD"): sh(f'reg add "{k}" /v {n} /t {t} /d "{v}" /f')
HKCU, HKLM = r"HKCU", r"HKLM"

# ---------------- Core tweaks ----------------
GUID = re.compile(r"([0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12})", re.I)
def power_plan(L):
    m = GUID.search(sh("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")) or GUID.search(sh("powercfg -duplicatescheme SCHEME_MIN"))
    if not m: return L("สร้าง power plan ไม่สำเร็จ")
    g = m.group(1)
    sh(f'powercfg -changename {g} "Flowsus" "FlowFx Pro Max Performance"')
    for a in ["SUB_PROCESSOR PROCTHROTTLEMIN 100", "SUB_PROCESSOR PROCTHROTTLEMAX 100", "SUB_PROCESSOR CPMINCORES 100", "SUB_PCIEXPRESS ASPM 0",
              "SUB_DISK DISKIDLE 0", "SUB_SLEEP STANDBYIDLE 0", "2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0"]:
        sh(f"powercfg -setacvalueindex {g} {a}")
    sh(f"powercfg -setactive {g}"); L("Power plan 'Flowsus' เปิดใช้งานแล้ว")
def gamemode(L):
    reg(r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", 1); reg(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", 1)
    reg(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", 0); reg(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2)
    reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0); L("Game Mode ON / Game DVR OFF")
def hags(L): reg(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 2); L("HAGS เปิด (รีสตาร์ทเครื่อง 1 ครั้ง)")
def mmcss(L):
    p = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
    reg(p, "NetworkThrottlingIndex", 4294967295); reg(p, "SystemResponsiveness", 0)
    for n, v, t in [("GPU Priority", 8, "REG_DWORD"), ("Priority", 6, "REG_DWORD"), ("Scheduling Category", "High", "REG_SZ"), ("SFIO Priority", "High", "REG_SZ")]:
        reg(p + r"\Tasks\Games", n, v, t)
    reg(r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 38); L("MMCSS + CPU scheduler ปรับเพื่อเกม")
def mouse(L):
    for n, v in [("MouseSpeed", 0), ("MouseThreshold1", 0), ("MouseThreshold2", 0)]: reg(r"HKCU\Control Panel\Mouse", n, v, "REG_SZ")
    L("ปิด Mouse Acceleration")
def visual(L):
    reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2)
    reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", 0)
    reg(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", 0, "REG_SZ"); L("ลด Visual Effects")
def bgapps(L):
    reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", 1)
    for s in ("SysMain", "DiagTrack"): sh(f"sc stop {s}"); sh(f"sc config {s} start= disabled")
    L("ปิด Background apps / SysMain / Telemetry")
def clean(L):
    n = 0
    for d in [os.environ.get("TEMP", ""), r"C:\Windows\Temp", r"C:\Windows\Prefetch"]:
        for f in glob.glob(d + r"\*"):
            try: shutil.rmtree(f) if os.path.isdir(f) else os.remove(f); n += 1
            except Exception: pass
    sh("ipconfig /flushdns"); L(f"ล้างไฟล์ขยะ {n} รายการ + flush DNS")
def killbloat(L):
    for p in ["OneDrive", "Teams", "msedgewebview2", "YourPhone", "SearchApp", "Widgets", "GameBar", "Cortana"]: sh(f"taskkill /f /im {p}.exe")
    L("ปิดโปรเซสเกะกะแล้ว")
def restore(L): ps("Enable-ComputerRestore -Drive 'C:\\'; Checkpoint-Computer -Description 'FlowFxPro' -RestorePointType MODIFY_SETTINGS"); L("สร้าง Restore Point แล้ว")
def revert(L):
    sh("powercfg -setactive SCHEME_BALANCED"); net_apply("normal", "default", "disabled", False, None); qos_clear(); sh("sc config SysMain start= auto"); sh("bcdedit /deletevalue disabledynamictick"); reg(r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", 0); sh("sc config DiagTrack start= auto")
    reg(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched", "NonBestEffortLimit", 20); L("คืนค่า Power/Net/QoS แล้ว (ที่เหลือใช้ Restore Point)")
def timer(L):
    sh("bcdedit /set disabledynamictick yes"); sh("bcdedit /deletevalue useplatformclock")
    reg(r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", 1)
    reg(r"HKCU\Control Panel\Desktop", "MenuShowDelay", 0, "REG_SZ"); reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize", "StartupDelayInMSec", 0)
    L("Timer / Power Throttling / Startup delay ปรับแล้ว")
def nicpower(L): ps("Get-NetAdapter | ? Status -eq 'Up' | % { try { Set-NetAdapterPowerManagement -Name $_.Name -AllowComputerToTurnOffDevice Disabled } catch {} }"); L("ปิดประหยัดไฟการ์ดแลน")
def ramclean(L):
    try:
        k, a = ctypes.windll.kernel32, ctypes.windll.advapi32; h = ctypes.c_void_p(); a.OpenProcessToken(k.GetCurrentProcess(), 0x28, ctypes.byref(h))
        class LUID(ctypes.Structure): _fields_ = [("lo", ctypes.c_uint32), ("hi", ctypes.c_int32)]
        class TP(ctypes.Structure): _fields_ = [("n", ctypes.c_uint32), ("l", LUID), ("a", ctypes.c_uint32)]
        t = TP(1, LUID(), 2); a.LookupPrivilegeValueW(None, "SeProfileSingleProcessPrivilege", ctypes.byref(t.l)); a.AdjustTokenPrivileges(h, False, ctypes.byref(t), 0, None, None)
        ctypes.windll.ntdll.NtSetSystemInformation(80, ctypes.byref(ctypes.c_int(4)), 4); L("ล้าง Standby RAM แล้ว")
    except Exception as e: L(f"RAM clean ล้มเหลว: {e}")
BOOST = [("Power plan 'Flowsus' (Ultimate Performance)", power_plan), ("Game Mode ON + ปิด Game DVR", gamemode), ("Hardware GPU Scheduling", hags),
         ("MMCSS / CPU Priority เกม", mmcss), ("ปิด Mouse Acceleration", mouse), ("Visual Effects โหมดเร็ว", visual),
         ("ปิด Background apps / SysMain / Telemetry", bgapps), ("ล้างไฟล์ขยะ + Flush DNS", clean), ("ปิดโปรเซสเกะกะ", killbloat), ("Timer / ปิด Power Throttling", timer), ("ปิดประหยัดไฟการ์ดแลน", nicpower), ("ล้าง Standby RAM", ramclean)]

# ---------------- Network ----------------
DNS = {"Cloudflare": ("1.1.1.1", "1.0.0.1"), "Google": ("8.8.8.8", "8.8.4.4"), "Quad9": ("9.9.9.9", "149.112.112.112"), "OpenDNS": ("208.67.222.222", "208.67.220.220"), "Auto (DHCP)": None}
NETP = {"1. Default (คืนค่า)": ("normal", "default", "disabled", False, "Auto (DHCP)"), "2. Balanced Gaming": ("normal", "disabled", "disabled", True, "Cloudflare"),
        "3. Low Ping": ("restricted", "disabled", "disabled", True, "Cloudflare"), "4. Ultra Low Latency": ("disabled", "disabled", "disabled", True, "Cloudflare"),
        "5. Stream + Game": ("normal", "default", "disabled", True, "Google")}
def net_apply(auto, ecn, ts, nodelay, dns):
    sh(f"netsh int tcp set global autotuninglevel={auto}"); sh(f"netsh int tcp set global ecncapability={ecn}")
    sh(f"netsh int tcp set global timestamps={ts}"); sh("netsh int tcp set global rss=enabled"); sh("netsh int tcp set global fastopen=enabled")
    base = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as k:
            for i in range(winreg.QueryInfoKey(k)[0]):
                try:
                    with winreg.OpenKey(k, winreg.EnumKey(k, i), 0, winreg.KEY_SET_VALUE) as s:
                        for n in ("TcpAckFrequency", "TCPNoDelay"):
                            if nodelay: winreg.SetValueEx(s, n, 0, winreg.REG_DWORD, 1)
                            else:
                                try: winreg.DeleteValue(s, n)
                                except OSError: pass
                except OSError: pass
    except Exception: pass
    d = DNS.get(dns) if isinstance(dns, str) else dns
    q = "Get-NetAdapter | ? Status -eq 'Up' | "
    ps(q + (f"Set-DnsClientServerAddress -ServerAddresses {d[0]},{d[1]}" if d else "Set-DnsClientServerAddress -ResetServerAddresses")); sh("ipconfig /flushdns")

# ---------------- QoS ----------------
GAMES_EXE = ["FiveM.exe", "FiveM_*GTAProcess.exe", "GTA5.exe", "VALORANT-Win64-Shipping.exe", "cs2.exe", "FortniteClient-Win64-Shipping.exe", "r5apex.exe", "RobloxPlayerBeta.exe"]
QOSP = {"Light (DSCP 34)": (34, False), "Gaming (DSCP 46)": (46, False), "Ultra (DSCP 46 + ปลด Bandwidth limit)": (46, True)}
def qos_clear(): ps("Get-NetQosPolicy | ? Name -like 'FlowFx_*' | Remove-NetQosPolicy -Confirm:$false")
def qos_apply(dscp, unlimit, exes):
    qos_clear()
    for e in exes: ps(f"New-NetQosPolicy -Name 'FlowFx_{e}' -AppPathNameMatch '{e}' -DSCPAction {dscp} -IPProtocolMatch Both")
    reg(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched", "NonBestEffortLimit", 0 if unlimit else 20)

# ---------------- Process Lasso ----------------
LASSO = {"Game Boost": ("High", "BelowNormal", "all", "all"), "Ultra Lasso": ("High", "Idle", "no0", "c0"),
         "Streamer": ("AboveNormal", "BelowNormal", "all", "all"), "Background Killer": ("High", "Idle", "all", "c0")}
BGP = "chrome,msedge,firefox,Discord,Spotify,OneDrive,steamwebhelper,EpicGamesLauncher,Teams,SearchApp,Widgets"
def lasso_apply(p, games, bgs):
    n = os.cpu_count() or 4; full = (1 << n) - 1; gm = full & ~1 if p[2] == "no0" else full; bm = 1 if p[3] == "c0" else full
    s = ""
    for names, pri, m in [(games, p[0], gm), (bgs, p[1], bm)]:
        for x in [i.strip() for i in names.split(",") if i.strip()]:
            s += f"Get-Process -Name '{x}' -EA 0 | % {{ try {{ $_.PriorityClass='{pri}'; $_.ProcessorAffinity={m} }} catch {{}} }};"
    ps(s)

# ---------------- FiveM ----------------
GTA = os.path.expanduser(r"~\Documents\Rockstar Games\GTA V\settings.xml")
FIVEP = {"Max FPS": dict(TextureQuality=0, ShaderQuality=0, ShadowQuality=0, ReflectionQuality=0, ReflectionMSAA=0, SSAO=0, AnisotropicFiltering=0, MSAA=0, GrassQuality=0, ParticleQuality=0, WaterQuality=0, PostFX=0, Tessellation=0, MotionBlurStrength="0.000000", DoF="false"),
         "Balanced": dict(TextureQuality=1, ShaderQuality=1, ShadowQuality=1, ReflectionQuality=1, ReflectionMSAA=0, SSAO=0, AnisotropicFiltering=4, MSAA=0, GrassQuality=1, ParticleQuality=1, WaterQuality=1, PostFX=1, Tessellation=0, MotionBlurStrength="0.000000", DoF="false"),
         "Clean Look": dict(TextureQuality=2, ShaderQuality=1, ShadowQuality=1, ReflectionQuality=1, ReflectionMSAA=0, SSAO=0, AnisotropicFiltering=8, MSAA=0, GrassQuality=1, ParticleQuality=1, WaterQuality=1, PostFX=2, Tessellation=0, MotionBlurStrength="0.000000", DoF="false")}
def fivem_gfx(name, L):
    if not os.path.exists(GTA): return L("ไม่พบ settings.xml (เปิด GTA V/FiveM 1 ครั้งก่อน)")
    shutil.copy(GTA, GTA + ".flowfx.bak"); t = open(GTA, encoding="utf-8").read()
    for k, v in FIVEP[name].items(): t = re.sub(rf'(<{k}\s+value=")[^"]*(")', rf'\g<1>{v}\g<2>', t)
    open(GTA, "w", encoding="utf-8").write(t); L(f"FiveM กราฟิกพรีเซ็ต '{name}' แล้ว (สำรองไว้ .flowfx.bak)")
def fivem_extra(L):
    ld = os.environ.get("LOCALAPPDATA", ""); app = ld + r"\FiveM\FiveM.app"
    for d in ["data\\cache", "data\\server-cache", "data\\server-cache-priv", "data\\nui-storage"]:
        shutil.rmtree(os.path.join(app, d), ignore_errors=True)
    for e in glob.glob(ld + r"\FiveM\FiveM.exe") + glob.glob(app + r"\*.exe"):
        reg(r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences", f'"{e}"', "GpuPreference=2;", "REG_SZ")
        reg(r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers", f'"{e}"', "~ DISABLEDXMAXIMIZEDWINDOWEDMODE", "REG_SZ")
    L("ล้างแคช FiveM + บังคับ GPU แรงสุด + ปิด Fullscreen Optimization")

# ---------------- Recorder (video + audio) ----------------
FF_RES = {"Native": "", "1440p": "scale=-2:1440", "1080p": "scale=-2:1080", "720p": "scale=-2:720", "480p": "scale=-2:480"}
FF_Q = {"Low": 30, "Medium": 26, "High": 21, "Ultra": 17}
def venc(e, q):
    return {"libx264 (CPU)": f"-c:v libx264 -preset ultrafast -crf {q}", "h264_nvenc (NVIDIA)": f"-c:v h264_nvenc -preset p1 -rc vbr -cq {q} -b:v 0",
            "h264_amf (AMD)": f"-c:v h264_amf -quality speed -rc cqp -qp_i {q} -qp_p {q}"}[e]
class Aud:  # system loopback + mic เป็นแทร็กแยกกัน (WASAPI ผ่าน pyaudiowpatch)
    def __init__(s): s.p = None; s.wavs = {}; s.fmt = {}; s.ring = {}; s.cnt = {}; s.st = []; s.done = set(); s.d = ""
    def start(s, mic, keep, long, d):
        import pyaudiowpatch as pa
        s.d, s.keep, s.done = d, keep, set(); s.p = pa.PyAudio(); w = s.p.get_host_api_info_by_type(pa.paWASAPI)
        sp = s.p.get_device_info_by_index(w["defaultOutputDevice"])
        if not sp["isLoopbackDevice"]:
            for l in s.p.get_loopback_device_info_generator():
                if sp["name"] in l["name"]: sp = l; break
        devs = {"sys": sp}
        if mic: devs["mic"] = s.p.get_device_info_by_index(w["defaultInputDevice"])
        s.t0 = time.time(); s.wavs = {}
        for k, dv in devs.items():
            ch, rt = int(dv["maxInputChannels"]), int(dv["defaultSampleRate"]); s.fmt[k] = (ch, rt); s.ring[k] = collections.deque(); s.cnt[k] = 0
            if long:
                f = wave.open(f"{d}\\a_{k}.wav", "wb"); f.setnchannels(ch); f.setsampwidth(2); f.setframerate(rt); s.wavs[k] = f
            def cb(data, fc, ti, stt, k=k): s.feed(k, data); return (None, pa.paContinue)
            s.st.append(s.p.open(format=pa.paInt16, channels=ch, rate=rt, frames_per_buffer=1024, input=True, input_device_index=dv["index"], stream_callback=cb))
    def feed(s, k, data):
        now = time.time(); r = s.ring[k]; r.append((now, data))
        while r and r[0][0] < now - s.keep: r.popleft()
        if k in s.wavs:  # เติมความเงียบให้ sync (loopback ไม่ส่งข้อมูลตอนเงียบ)
            ch, rt = s.fmt[k]; n = len(data) // (2 * ch); gap = int((now - n / rt - s.t0) * rt) - s.cnt[k]
            if gap > rt // 20: s.wavs[k].writeframes(b"\0" * gap * 2 * ch); s.cnt[k] += gap
            s.wavs[k].writeframes(data); s.cnt[k] += n
    def stop(s):
        for x in s.st:
            try: x.stop_stream(); x.close()
            except Exception: pass
        s.st = []; s.done = set(s.wavs)
        for f in s.wavs.values(): f.close()
        s.wavs = {}
        if s.p: s.p.terminate(); s.p = None
    def clip(s, k, secs):
        if k not in s.ring: return None
        ch, rt = s.fmt[k]; bpf = 2 * ch; tot = int(secs * rt); buf = bytearray(tot * bpf); t0 = time.time() - secs
        for ta, dd in list(s.ring[k]):
            n = len(dd) // bpf; off = int((ta - n / rt - t0) * rt)
            if off >= tot: continue
            if off < 0: dd = dd[-off * bpf:]; off = 0
            dd = dd[:(tot - off) * bpf]
            if dd: buf[off * bpf: off * bpf + len(dd)] = dd
        fn = f"{s.d}\\a_{k}_clip.wav"; f = wave.open(fn, "wb"); f.setnchannels(ch); f.setsampwidth(2); f.setframerate(rt); f.writeframes(bytes(buf)); f.close(); return fn
    def file(s, k, dur): return (f"{s.d}\\a_{k}.wav" if k in s.done else None) if dur is None else s.clip(k, dur)
class Rec:
    def __init__(s): s.p = None; s.a = Aud(); s.mode = None; s.d = os.path.expanduser(r"~\Videos\FlowFx"); os.makedirs(s.d + r"\buf", exist_ok=True)
    def start(s, c):
        if shutil.which("ffmpeg") is None: return "ffmpeg"
        s.c, s.mode = c, c["mode"]
        try: s.a.start(c["mic"], c["secs"] + 15, c["mode"] == "Long", s.d)
        except Exception as e: L(f"เสียงใช้ไม่ได้ ({e}) — กด 'ติดตั้งไลบรารีเสียง' แล้วเปิดแอปใหม่")
        vf = f'-vf "{FF_RES[c["res"]]}"' if FF_RES[c["res"]] else ""
        cap = f'-f gdigrab -framerate {c["fps"]} -draw_mouse {int(c["cur"])} -i desktop {vf} {venc(c["enc"], FF_Q[c["q"]])} -pix_fmt yuv420p'
        if c["mode"] == "Replay":
            for f in glob.glob(s.d + r"\buf\*"): os.remove(f)
            out = f'-force_key_frames "expr:gte(t,n_forced*5)" -f segment -segment_time 5 -segment_wrap {max(2, c["secs"] // 5 + 1)} -reset_timestamps 1 "{s.d}\\buf\\s%03d.ts"'
        else: s.vid = s.d + time.strftime(r"\Rec_%Y%m%d_%H%M%S.mkv"); out = f'"{s.vid}"'
        s.p = subprocess.Popen(f"ffmpeg -y {cap} {out}", shell=True, creationflags=NW, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def mux(s, v, out, dur):
        c = s.c; ins = f'-i "{v}"'; mp = "-map 0:v"; fl = ""; n = 0
        for k, g in (("sys", c["vs"]), ("mic", c["vm"])):
            w = s.a.file(k, dur)
            if w: ins += f' -itsoffset {c["off"] / 1000} -i "{w}"'; mp += f" -map {n + 1}:a"; fl += f' -filter:a:{n} volume={g / 100} -metadata:s:a:{n} title={"System" if k == "sys" else "Mic"}'; n += 1
        sh(f'ffmpeg -y {ins} {mp} -c:v copy {"-c:a aac -b:a 192k" if n else ""} {fl} "{out}"'); return out
    def save(s):
        if not s.p or s.mode != "Replay": return None
        fs = sorted(glob.glob(s.d + r"\buf\*.ts"), key=os.path.getmtime)[-(s.c["secs"] // 5 + 1):]
        if not fs: return None
        lst, tmp = s.d + r"\list.txt", s.d + r"\tmp.mp4"; open(lst, "w").write("".join(f"file '{f}'\n" for f in fs)); sh(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{tmp}"')
        try: dur = float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{tmp}"').strip().splitlines()[0])
        except Exception: dur = s.c["secs"]
        return s.mux(tmp, s.d + time.strftime(r"\Clip_%Y%m%d_%H%M%S.mp4"), min(dur, s.c["secs"] + 5))
    def stop(s):
        r = None
        if s.p:
            try: s.p.stdin.write(b"q\n"); s.p.stdin.flush(); s.p.wait(20)
            except Exception: sh(f"taskkill /f /t /pid {s.p.pid}")
            s.p = None; s.a.stop()
            if s.mode == "Long": r = s.mux(s.vid, s.vid.replace(".mkv", ".mp4"), None)
        else: s.a.stop()
        return r

# ---------------- GUI ----------------
root = tk.Tk(); root.title("FlowFx Pro"); root.geometry("1020x700"); root.configure(bg=BG)
hdr = tk.Canvas(root, height=70, bg=BG, highlightthickness=0); hdr.pack(fill="x")
for i in range(1020):
    r1, g1, b1, r2, g2, b2 = 0, 229, 255, 177, 76, 255; t = i / 1020
    hdr.create_line(i, 66, i, 70, fill="#%02x%02x%02x" % (int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t)))
hdr.create_text(24, 33, text="FlowFx", anchor="w", fill=AC, font=("Segoe UI Black", 26)); hdr.create_text(160, 38, text="PRO", anchor="w", fill=AC2, font=("Segoe UI Black", 20))
logbox = tk.Text(root, height=7, bg="#06060e", fg="#7dffb0", bd=0, font=("Consolas", 10)); logbox.pack(side="bottom", fill="x")
def L(m): root.after(0, lambda: (logbox.insert("end", "› " + m + "\n"), logbox.see("end")))
def bgrun(fn, *a):
    def w():
        try: fn(*a)
        except Exception as e: L(f"ERROR: {e}")
    threading.Thread(target=w, daemon=True).start()
def Btn(p, t, c, ac=AC, **k): return tk.Button(p, text=t, command=c, bg=ac, fg="#000" if ac == AC else "#fff", bd=0, activebackground=AC2, cursor="hand2", font=("Segoe UI Semibold", 10), padx=14, pady=7, **k)
def Lbl(p, t, big=False): return tk.Label(p, text=t, bg=PN, fg=AC if big else FG, font=("Segoe UI Semibold", 13 if big else 10), anchor="w")
side = tk.Frame(root, bg=PN, width=190); side.pack(side="left", fill="y"); main = tk.Frame(root, bg=BG); main.pack(side="left", fill="both", expand=True)
pages = {}
def page(n):
    f = tk.Frame(main, bg=PN); pages[n] = f; return f
def show(n):
    for f in pages.values(): f.pack_forget()
    pages[n].pack(fill="both", expand=True, padx=14, pady=14)

# Dashboard
p = page("📊 Dashboard"); Lbl(p, "Live Monitor", 1).pack(fill="x", padx=16, pady=(14, 6))
cvs = tk.Canvas(p, bg=PN, height=170, highlightthickness=0); cvs.pack(fill="x", padx=22); st = {"cpu": 0, "ram": 0, "ping": "-"}
class MS(ctypes.Structure): _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(f"x{i}", ctypes.c_ulonglong) for i in range(7)]
def draw():
    cvs.delete("all")
    for y, (t, v) in enumerate([("CPU", st["cpu"]), ("RAM", st["ram"])]):
        cvs.create_text(0, 25 + y * 50, text=f"{t} {v}%", anchor="w", fill=FG, font=("Segoe UI Semibold", 11)); cvs.create_rectangle(110, 15 + y * 50, 700, 35 + y * 50, fill=BG, outline="")
        cvs.create_rectangle(110, 15 + y * 50, 110 + 590 * v // 100, 35 + y * 50, fill=AC if v < 75 else "#ff4d6d", outline="")
    cvs.create_text(0, 135, text=f"Ping 1.1.1.1 : {st['ping']}", anchor="w", fill="#7dffb0", font=("Segoe UI Semibold", 13))
def mon():
    i = ctypes.c_ulonglong; idle, ker, usr = i(), i(), i(); prev = None; n = 0
    while True:
        try:
            ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(ker), ctypes.byref(usr)); c = (idle.value, ker.value + usr.value)
            if prev and c[1] - prev[1]: st["cpu"] = max(0, int(100 * (1 - (c[0] - prev[0]) / (c[1] - prev[1]))))
            prev = c; m = MS(); m.l = ctypes.sizeof(m); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); st["ram"] = m.load
            if n % 3 == 0: x = re.search(r"[=<](\d+)ms", sh("ping -n 1 -w 1000 1.1.1.1")); st["ping"] = x.group(1) + " ms" if x else "timeout"
            n += 1; root.after(0, draw)
        except Exception: pass
        time.sleep(1)
if os.name == "nt": threading.Thread(target=mon, daemon=True).start()
r = tk.Frame(p, bg=PN); r.pack(anchor="w", padx=22, pady=14)
Btn(r, "🚀 BOOST FPS NOW", lambda: bgrun(boost_all)).pack(side="left"); Btn(r, "🧹 ล้าง RAM", lambda: bgrun(ramclean, L), AC2).pack(side="left", padx=8); Btn(r, "🗑 ล้างขยะ", lambda: bgrun(clean, L), AC2).pack(side="left")

# Boost page
p = page("⚡ Boost"); Lbl(p, "One-Click FPS Boost", 1).pack(fill="x", padx=16, pady=(14, 6)); vars_ = []
for name, fn in BOOST:
    v = tk.BooleanVar(value=True); vars_.append((v, fn)); tk.Checkbutton(p, text=name, variable=v, bg=PN, fg=FG, selectcolor=BG, activebackground=PN, activeforeground=AC, font=("Segoe UI", 11)).pack(anchor="w", padx=22)
def boost_all(): restore(L); [fn(L) for v, fn in vars_ if v.get()]; L("✔ BOOST เสร็จ — รีสตาร์ทเครื่องเพื่อให้ผลเต็มที่")
r = tk.Frame(p, bg=PN); r.pack(fill="x", padx=16, pady=14)
Btn(r, "🚀 BOOST FPS NOW", lambda: bgrun(boost_all)).pack(side="left"); Btn(r, "↩ คืนค่า", lambda: bgrun(revert, L), AC2).pack(side="left", padx=8)

# Network page
p = page("🌐 Network"); Lbl(p, "Network Presets (5 แบบ)", 1).pack(fill="x", padx=16, pady=(14, 6))
for n, v in NETP.items(): Btn(p, n, lambda v=v, n=n: (bgrun(lambda: (net_apply(*v), L(f"Net preset: {n}"))))).pack(anchor="w", padx=22, pady=3)
Lbl(p, "ปรับเอง", 1).pack(fill="x", padx=16, pady=(14, 4)); m = tk.Frame(p, bg=PN); m.pack(anchor="w", padx=22)
cv = [tk.StringVar(value=x) for x in ("normal", "disabled", "disabled", "Cloudflare")]; nd = tk.BooleanVar(value=True)
for i, (t, vals) in enumerate([("AutoTuning", ["normal", "restricted", "highlyrestricted", "disabled"]), ("ECN", ["default", "enabled", "disabled"]), ("Timestamps", ["disabled", "enabled"]), ("DNS", list(DNS))]):
    Lbl(m, t).grid(row=0, column=i * 2, padx=4); ttk.Combobox(m, textvariable=cv[i], values=vals, width=14, state="readonly").grid(row=0, column=i * 2 + 1)
tk.Checkbutton(p, text="Disable Nagle (TcpAckFrequency/TCPNoDelay)", variable=nd, bg=PN, fg=FG, selectcolor=BG, activebackground=PN).pack(anchor="w", padx=22, pady=6)
Btn(p, "Apply Custom", lambda: bgrun(lambda: (net_apply(cv[0].get(), cv[1].get(), cv[2].get(), nd.get(), cv[3].get()), L("Net custom applied")))).pack(anchor="w", padx=22)

# QoS page
p = page("📡 QoS"); Lbl(p, "QoS Presets", 1).pack(fill="x", padx=16, pady=(14, 6)); ex = tk.StringVar(value=",".join(GAMES_EXE))
for n, (d, u) in QOSP.items(): Btn(p, n, lambda d=d, u=u, n=n: bgrun(lambda: (qos_apply(d, u, [x.strip() for x in ex.get().split(",") if x.strip()]), L(f"QoS: {n}")))).pack(anchor="w", padx=22, pady=3)
Lbl(p, "รายชื่อเกม (.exe คั่นด้วย ,)").pack(fill="x", padx=16, pady=(12, 2)); tk.Entry(p, textvariable=ex, bg=BG, fg=FG, insertbackground=AC, bd=0).pack(fill="x", padx=22, ipady=5)
Lbl(p, "DSCP ปรับเอง (0-63)").pack(fill="x", padx=16, pady=(12, 2)); ds = tk.IntVar(value=46); tk.Scale(p, from_=0, to=63, orient="horizontal", variable=ds, bg=PN, fg=FG, troughcolor=BG, highlightthickness=0).pack(fill="x", padx=22)
r = tk.Frame(p, bg=PN); r.pack(anchor="w", padx=22, pady=8)
Btn(r, "Apply DSCP", lambda: bgrun(lambda: (qos_apply(ds.get(), False, [x.strip() for x in ex.get().split(",") if x.strip()]), L("QoS custom applied")))).pack(side="left"); Btn(r, "ลบ QoS ทั้งหมด", lambda: bgrun(qos_clear), AC2).pack(side="left", padx=8)

# Lasso page
p = page("🧠 Lasso"); Lbl(p, "Process Lasso Presets", 1).pack(fill="x", padx=16, pady=(14, 6))
gm_ = tk.StringVar(value="FiveM*,GTA5,VALORANT*,cs2,FortniteClient*,r5apex"); bg_ = tk.StringVar(value=BGP); auto = tk.BooleanVar(value=False); cur = [None]
Lbl(p, "เกม (ใช้ * ได้)").pack(fill="x", padx=16); tk.Entry(p, textvariable=gm_, bg=BG, fg=FG, insertbackground=AC, bd=0).pack(fill="x", padx=22, ipady=5)
Lbl(p, "โปรแกรมพื้นหลังที่จะลดความสำคัญ").pack(fill="x", padx=16, pady=(8, 0)); tk.Entry(p, textvariable=bg_, bg=BG, fg=FG, insertbackground=AC, bd=0).pack(fill="x", padx=22, ipady=5)
def lasso_go(n): cur[0] = LASSO[n]; bgrun(lambda: (lasso_apply(cur[0], gm_.get(), bg_.get()), L(f"Lasso: {n}")))
for n in LASSO: Btn(p, n, lambda n=n: lasso_go(n)).pack(anchor="w", padx=22, pady=3)
tk.Checkbutton(p, text="Auto-enforce ทุก 5 วิ (ล็อกค่าไว้ตลอดตอนเล่น)", variable=auto, bg=PN, fg=FG, selectcolor=BG, activebackground=PN).pack(anchor="w", padx=22, pady=8)
import fnmatch
ag = tk.BooleanVar(value=False); tk.Checkbutton(p, text="Auto Game Mode: ตรวจเจอเกมแล้ว ล้าง RAM + Lasso ให้เอง", variable=ag, bg=PN, fg=AC, selectcolor=BG, activebackground=PN).pack(anchor="w", padx=22); was = [False]
def loop():
    while True:
        time.sleep(5)
        try:
            if ag.get():
                procs = [l.split('","')[0].strip('"').lower() for l in sh("tasklist /fo csv /nh").splitlines() if l]
                pats = [x.strip().lower() + ("" if "*" in x else "*") for x in gm_.get().split(",") if x.strip()]
                run = any(fnmatch.fnmatch(pr, pt) for pr in procs for pt in pats)
                if run and not was[0]: cur[0] = cur[0] or LASSO["Ultra Lasso"]; ramclean(L); L("🎮 ตรวจเจอเกม — Auto Boost")
                was[0] = run
                if run: lasso_apply(cur[0], gm_.get(), bg_.get())
            if auto.get() and cur[0]: lasso_apply(cur[0], gm_.get(), bg_.get())
        except Exception: pass
threading.Thread(target=loop, daemon=True).start()

# FiveM page
p = page("🎮 FiveM"); Lbl(p, "FiveM / GTA V Graphics (FPS สูง)", 1).pack(fill="x", padx=16, pady=(14, 6))
for n in FIVEP: Btn(p, f"กราฟิก: {n}", lambda n=n: bgrun(fivem_gfx, n, L)).pack(anchor="w", padx=22, pady=3)
Btn(p, "ล้างแคช + GPU Priority + ปิด FSO", lambda: bgrun(fivem_extra, L), AC2).pack(anchor="w", padx=22, pady=10)
Lbl(p, "ปิดเกมก่อนกดพรีเซ็ตกราฟิก / ระบบสำรอง settings.xml ให้อัตโนมัติ").pack(fill="x", padx=16)

# Startup page
p = page("🚀 Startup"); Lbl(p, "Startup Manager (ปิดโปรแกรมที่ค้างตอนเปิดเครื่อง)", 1).pack(fill="x", padx=16, pady=(14, 6))
lb = tk.Listbox(p, bg=BG, fg=FG, selectbackground=AC2, bd=0, height=14, font=("Consolas", 10)); lb.pack(fill="both", expand=True, padx=22)
RUN, OFF = r"Software\Microsoft\Windows\CurrentVersion\Run", r"Software\FlowFx\DisabledStartup"
RT = lambda t: winreg.HKEY_CURRENT_USER if t == "HKCU" else winreg.HKEY_LOCAL_MACHINE
def st_list():
    lb.delete(0, "end")
    for t in ("HKCU", "HKLM"):
        try:
            with winreg.OpenKey(RT(t), RUN) as k:
                for i in range(winreg.QueryInfoKey(k)[1]): lb.insert("end", f"{t} | {winreg.EnumValue(k, i)[0]}")
        except OSError: pass
def st_off():
    for s_ in lb.curselection():
        t, n = lb.get(s_).split(" | ", 1)
        with winreg.OpenKey(RT(t), RUN, 0, winreg.KEY_ALL_ACCESS) as k: v = winreg.QueryValueEx(k, n); winreg.DeleteValue(k, n)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, OFF) as o: winreg.SetValueEx(o, f"{t}|{n}", 0, v[1], v[0])
    st_list(); L("ปิด startup ที่เลือกแล้ว (กู้คืนได้)")
def st_back():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, OFF, 0, winreg.KEY_ALL_ACCESS) as o:
            for n, v, ty in [winreg.EnumValue(o, i) for i in range(winreg.QueryInfoKey(o)[1])]:
                t, nm = n.split("|", 1)
                with winreg.OpenKey(RT(t), RUN, 0, winreg.KEY_SET_VALUE) as k: winreg.SetValueEx(k, nm, 0, ty, v)
                winreg.DeleteValue(o, n)
    except OSError: pass
    st_list(); L("กู้คืน startup แล้ว")
r = tk.Frame(p, bg=PN); r.pack(anchor="w", padx=22, pady=10)
Btn(r, "ปิดตัวที่เลือก", st_off).pack(side="left"); Btn(r, "กู้คืนทั้งหมด", st_back, AC2).pack(side="left", padx=8)
if winreg: st_list()

# Recorder page
rec = Rec(); p = page("🎬 Recorder"); Lbl(p, "Recorder: Replay ย้อนหลัง / อัดยาว + เสียง", 1).pack(fill="x", padx=16, pady=(14, 6))
V = dict(mode=tk.StringVar(value="Replay"), secs=tk.IntVar(value=30), fps=tk.IntVar(value=60), res=tk.StringVar(value="Native"), q=tk.StringVar(value="High"), enc=tk.StringVar(value="libx264 (CPU)"),
         cur=tk.BooleanVar(value=True), mic=tk.BooleanVar(value=True), vs=tk.IntVar(value=100), vm=tk.IntVar(value=100), off=tk.IntVar(value=0))
g = tk.Frame(p, bg=PN); g.pack(anchor="w", padx=22)
for i, (t, k, vals) in enumerate([("โหมด (Replay/Long)", "mode", ["Replay", "Long"]), ("ย้อนหลัง (วินาที)", "secs", [15, 30, 60, 120, 300]), ("FPS อัดคลิป", "fps", [24, 30, 60, 90, 120, 144]),
        ("ความละเอียด", "res", list(FF_RES)), ("คุณภาพภาพ", "q", list(FF_Q)), ("Encoder", "enc", ["libx264 (CPU)", "h264_nvenc (NVIDIA)", "h264_amf (AMD)"])]):
    Lbl(g, t).grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=4, pady=3); ttk.Combobox(g, textvariable=V[k], values=vals, width=20, state="readonly").grid(row=i // 2, column=(i % 2) * 2 + 1)
for t, k in [("อัดเมาส์ในคลิป", "cur"), ("อัดไมค์ (แทร็กแยก)", "mic")]: tk.Checkbutton(p, text=t, variable=V[k], bg=PN, fg=FG, selectcolor=BG, activebackground=PN).pack(anchor="w", padx=22)
for t, k, hi in [("ระดับเสียงเกม/ระบบ %", "vs", 200), ("ระดับเสียงไมค์ %", "vm", 200), ("ชดเชย sync เสียง (ms)", "off", 1000)]:
    Lbl(p, t).pack(fill="x", padx=16); tk.Scale(p, from_=0, to=hi, orient="horizontal", variable=V[k], bg=PN, fg=FG, troughcolor=BG, highlightthickness=0).pack(fill="x", padx=22)
def cfg(): return {k: v.get() for k, v in V.items()}
def rstart(c):
    if rec.p: return L("กำลังอัดอยู่แล้ว")
    e = rec.start(c); L("ไม่พบ ffmpeg — กดติดตั้ง ffmpeg ก่อน" if e else f"เริ่มโหมด {c['mode']} | F9 = เซฟคลิปย้อนหลัง, F10 = เริ่ม/หยุดอัดยาว")
def rsave(): o = rec.save(); L(f"เซฟคลิป: {o}" if o else "ต้องเปิดโหมด Replay ก่อน")
def rstop(): o = rec.stop(); L(f"บันทึกแล้ว: {o}" if o else "หยุดแล้ว")
r = tk.Frame(p, bg=PN); r.pack(anchor="w", padx=22, pady=10)
Btn(r, "▶ เริ่ม", lambda: bgrun(rstart, cfg())).pack(side="left"); Btn(r, "💾 เซฟคลิป (F9)", lambda: bgrun(rsave)).pack(side="left", padx=6); Btn(r, "■ หยุด (F10)", lambda: bgrun(rstop), AC2).pack(side="left")
r = tk.Frame(p, bg=PN); r.pack(anchor="w", padx=22)
Btn(r, "ติดตั้ง ffmpeg", lambda: bgrun(lambda: (L("กำลังติดตั้ง ffmpeg…"), sh("winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements"), L("เสร็จ — เปิดแอปใหม่")))).pack(side="left")
Btn(r, "ติดตั้งไลบรารีเสียง", lambda: bgrun(lambda: (L("กำลังติดตั้ง…"), sh(f'"{sys.executable}" -m pip install pyaudiowpatch pycaw comtypes'), L("เสร็จ — เปิดแอปใหม่")))).pack(side="left", padx=6)
Lbl(p, "ไฟล์อยู่ที่ Videos\\FlowFx | มีแทร็กเสียง System และ Mic แยกกันในไฟล์ .mp4").pack(fill="x", padx=16, pady=6)
def hotkey():
    u = ctypes.windll.user32; u.RegisterHotKey(None, 1, 0, 0x78); u.RegisterHotKey(None, 2, 0, 0x79); msg = ctypes.wintypes.MSG()
    while u.GetMessageW(ctypes.byref(msg), None, 0, 0):
        if msg.message == 0x0312:
            if msg.wParam == 1: bgrun(rsave)
            elif rec.p: bgrun(rstop)
            else: root.after(0, lambda: bgrun(rstart, dict(cfg(), mode="Long")))
if os.name == "nt": import ctypes.wintypes; threading.Thread(target=hotkey, daemon=True).start()

# Audio mixer page
p = page("🔊 Audio"); Lbl(p, "Audio Mixer: ปรับเสียงแต่ละแอป", 1).pack(fill="x", padx=16, pady=(14, 6)); mix = tk.Frame(p, bg=PN); mix.pack(fill="both", expand=True, padx=22)
def mix_load():
    for w in mix.winfo_children(): w.destroy()
    try:
        from pycaw.pycaw import AudioUtilities
        ss = [x for x in AudioUtilities.GetAllSessions() if x.Process]
    except Exception as e: return L(f"Mixer ใช้ไม่ได้: {e} (ติดตั้งไลบรารีเสียงในหน้า Recorder)")
    for x in ss:
        v = x.SimpleAudioVolume; row = tk.Frame(mix, bg=PN); row.pack(fill="x", pady=2); Lbl(row, x.Process.name()[:20]).pack(side="left"); mv = tk.BooleanVar(value=bool(v.GetMute()))
        sc = tk.Scale(row, from_=0, to=100, orient="horizontal", length=320, bg=PN, fg=FG, troughcolor=BG, highlightthickness=0, command=lambda val, v=v: v.SetMasterVolume(int(val) / 100, None)); sc.set(int(v.GetMasterVolume() * 100)); sc.pack(side="left", padx=8)
        tk.Checkbutton(row, text="Mute", variable=mv, bg=PN, fg=FG, selectcolor=BG, activebackground=PN, command=lambda v=v, m=mv: v.SetMute(int(m.get()), None)).pack(side="left")
        Btn(row, "Solo", lambda x=x: ([y.SimpleAudioVolume.SetMute(int(y is not x), None) for y in ss], mix_load()), AC2).pack(side="left", padx=6)
r = tk.Frame(p, bg=PN); r.pack(anchor="w", padx=22, pady=8)
Btn(r, "🔄 โหลดแอปที่มีเสียง", mix_load).pack(side="left"); Btn(r, "Unmute ทั้งหมด", lambda: (setattr(mix_load, "x", 0), [None], bgrun(lambda: unmute_all())), AC2).pack(side="left", padx=6)
def unmute_all():
    from pycaw.pycaw import AudioUtilities
    for x in AudioUtilities.GetAllSessions(): x.SimpleAudioVolume.SetMute(0, None)
    root.after(0, mix_load)
Lbl(p, "ระดับเสียงต่อแอปจะถูกอัดรวมในแทร็ก System (Solo = อัดเฉพาะแอปนั้น)").pack(fill="x", padx=16)

for n in pages: tk.Button(side, text=n, command=lambda n=n: show(n), bg=PN, fg=FG, activebackground=AC2, bd=0, anchor="w", font=("Segoe UI Semibold", 12), padx=18, pady=12, cursor="hand2").pack(fill="x")
root.protocol("WM_DELETE_WINDOW", lambda: (rec.stop(), root.destroy())); show("📊 Dashboard"); L("FlowFx Pro พร้อมใช้งาน"); root.mainloop()
