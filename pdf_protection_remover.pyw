# Desprotege los PDF de la carpeta donde está este script.
# Removes password protection from the PDFs in this script's folder.
# Requisitos / Requirements: Python 3 + "pip install pikepdf".
import csv
import hashlib
import locale
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    import pikepdf
except ImportError:
    # Sin consola (.pyw) el fallo sería invisible: se ofrece instalarlo en main().
    # Without a console (.pyw) the failure would be invisible: main() offers to install it.
    pikepdf = None

TEXTOS = {
    "es": {
        "log": "log_desproteccion.csv",
        "originales": "Originales",
        # cabeceras del log / log headers
        "columnas": {"archivo": "archivo", "estado": "estado", "n": "contraseña_nº",
                     "fecha": "fecha", "huella": "huella", "detalle": "detalle"},
        # códigos de estado del log / log status codes
        "estados": {"ok": "DESPROTEGIDO", "sin": "SIN_PROTECCION",
                    "err_pw": "ERROR_CONTRASEÑA", "err_arch": "ERROR_ARCHIVO"},
        # nombre legible de los errores en la ventana final / readable error names
        "err_pw": "contraseña incorrecta",
        "err_arch": "error de archivo",
        "titulo": "Desproteger PDF",
        "contraseña_n": "Contraseña nº {n}   (añadidas: {k})",
        "btn_añadir": "Añadir otra contraseña",
        "btn_ejecutar": "Aceptar y ejecutar",
        "btn_cancelar": "Cancelar",
        "falta_una": "Escribe una contraseña.",
        "falta_alguna": "Escribe al menos una contraseña.",
        "en_proceso": "Tarea en proceso…",
        "analizando": "Analizando: {archivo}",
        "descifrando": "Descifrando: Contraseña {n} de {total} · {archivo}",
        "log_abierto": "No se pudo escribir el log. ¿Está abierto en Excel?\n"
                       "Ciérralo y vuelve a ejecutar.",
        "nada_pendiente": "No hay PDF pendientes en esta carpeta.",
        "resumen": "{exitos} de {intentados} archivos protegidos desprotegidos con éxito.",
        "sin_prot": "{n} archivo(s) no tenían protección.",
        "reconocidos": "{n} archivo(s) renombrados o copiados ya estaban hechos.",
        "no_desprotegidos": "No desprotegidos:",
        "y_mas": "… y {n} más (ver {log})",
        "det_restricciones": "solo tenía restricciones",
        "det_mismo": "mismo contenido que {archivo}",
        "det_fallo": "falló con las {n} contraseñas",
        "falta_pikepdf": "Falta un componente necesario para leer PDF (pikepdf).\n\n"
                         "¿Quieres instalarlo ahora?\n"
                         "Tarda menos de un minuto y necesita conexión a Internet.",
        "instalando": "Instalando pikepdf…",
        "instalado": "pikepdf se ha instalado correctamente.\n\n"
                     "Vuelve a abrir el programa para empezar.",
        "fallo_instalacion": "No se pudo instalar pikepdf.\n\n"
                             "Puedes intentarlo a mano en una consola (cmd):\n{cmd}\n\n"
                             "Detalle:\n{detalle}",
    },
    "en": {
        "log": "unprotect_log.csv",
        "originales": "Originals",
        "columnas": {"archivo": "file", "estado": "status", "n": "password_no",
                     "fecha": "date", "huella": "fingerprint", "detalle": "detail"},
        "estados": {"ok": "UNLOCKED", "sin": "NOT_PROTECTED",
                    "err_pw": "WRONG_PASSWORD", "err_arch": "FILE_ERROR"},
        "err_pw": "wrong password",
        "err_arch": "file error",
        "titulo": "Unprotect PDF",
        "contraseña_n": "Password #{n}   (added: {k})",
        "btn_añadir": "Add another password",
        "btn_ejecutar": "OK and run",
        "btn_cancelar": "Cancel",
        "falta_una": "Enter a password.",
        "falta_alguna": "Enter at least one password.",
        "en_proceso": "Task in progress…",
        "analizando": "Analyzing: {archivo}",
        "descifrando": "Decrypting: Password {n} of {total} · {archivo}",
        "log_abierto": "Could not write the log. Is it open in Excel?\n"
                       "Close it and run again.",
        "nada_pendiente": "No pending PDFs in this folder.",
        "resumen": "{exitos} of {intentados} protected files successfully unprotected.",
        "sin_prot": "{n} file(s) were not protected.",
        "reconocidos": "{n} renamed or copied file(s) were already done.",
        "no_desprotegidos": "Not unprotected:",
        "y_mas": "… and {n} more (see {log})",
        "det_restricciones": "only had restrictions",
        "det_mismo": "same content as {archivo}",
        "det_fallo": "failed with all {n} passwords",
        "falta_pikepdf": "A component needed to read PDFs is missing (pikepdf).\n\n"
                         "Do you want to install it now?\n"
                         "It takes less than a minute and needs an Internet connection.",
        "instalando": "Installing pikepdf…",
        "instalado": "pikepdf was installed successfully.\n\n"
                     "Open the program again to start.",
        "fallo_instalacion": "pikepdf could not be installed.\n\n"
                             "You can try it manually in a console (cmd):\n{cmd}\n\n"
                             "Details:\n{detalle}",
    },
}


def detectar_idioma():
    """Español si el locale del equipo es español; inglés en cualquier otro caso.
    Spanish if the system locale is Spanish; English otherwise."""
    try:  # Windows: configuración regional del usuario / user regional settings
        import ctypes
        lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
        return "es" if lcid & 0x3FF == 0x0A else "en"
    except Exception:  # otros sistemas / other systems
        loc = (locale.getlocale()[0] or "").lower()
        return "es" if loc.startswith(("es", "spanish")) else "en"


T = TEXTOS[detectar_idioma()]
E = T["estados"]
CARPETA = Path(__file__).resolve().parent
LOG = CARPETA / T["log"]
ORIGINALES = CARPETA / T["originales"]
TERMINADOS = {E["ok"], E["sin"]}  # no se reprocesan / never reprocessed


def leer_log():
    if not LOG.exists():
        return {}
    a_interno = {v: k for k, v in T["columnas"].items()}
    with open(LOG, newline="", encoding="utf-8-sig") as f:
        filas = [{a_interno.get(k, k): v for k, v in fila.items()}
                 for fila in csv.DictReader(f, delimiter=";")]
    return {fila["archivo"]: fila for fila in filas}


def guardar_log(registros):
    # ";" y utf-8-sig para que Excel en español lo abra bien.
    # ";" and utf-8-sig so Spanish-locale Excel opens it correctly.
    col = T["columnas"]
    with open(LOG, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(col.values()), delimiter=";")
        w.writeheader()
        for r in sorted(registros.values(), key=lambda r: r["archivo"].lower()):
            w.writerow({col[k]: r.get(k, "") for k in col})


def huella(ruta):
    """SHA-256 del contenido: identifica el archivo aunque cambie de nombre.
    SHA-256 of the content: identifies the file even if renamed."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def registrar(registros, pdf, estado, n="", detalle=""):
    registros[pdf.name] = {"archivo": pdf.name, "estado": estado, "n": n,
                           "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           "huella": huella(pdf), "detalle": detalle}


def respaldar(pdf):
    """Copia el original a la carpeta de originales sin pisar copias anteriores.
    Copies the original to the originals folder without overwriting earlier copies."""
    ORIGINALES.mkdir(exist_ok=True)
    destino = ORIGINALES / pdf.name
    if destino.exists():
        destino = ORIGINALES / f"{pdf.stem}_{datetime.now():%Y%m%d_%H%M%S}{pdf.suffix}"
    shutil.copy2(pdf, destino)
    return destino


def desproteger(pdf, contraseña):
    """Abre con la contraseña, respalda el original y lo sobrescribe sin cifrado.
    Opens with the password, backs up the original and overwrites it unencrypted."""
    tmp = pdf.with_name(pdf.name + ".tmp")
    try:
        with pikepdf.open(pdf, password=contraseña) as doc:
            doc.save(tmp)  # pikepdf guarda sin cifrado por defecto / saves unencrypted by default
        copia = respaldar(pdf)
        try:
            os.replace(tmp, pdf)
        except OSError:
            # El original sigue intacto: su copia solo sería un duplicado al reintentar.
            # The original is untouched: its backup would only be a duplicate on retry.
            copia.unlink()
            raise
    finally:
        if tmp.exists():
            tmp.unlink()


def procesar(contraseñas, avisar):
    """avisar(texto, i, total) informa del avance / reports progress."""
    if LOG.exists():
        # Fallar antes de tocar ningún PDF: con el log bloqueado (abierto en Excel) se
        # perdería el registro de lo desprotegido en esta ejecución.
        # Fail before touching any PDF: with the log locked (open in Excel) the record
        # of what this run unlocked would be lost.
        open(LOG, "a").close()
    registros = leer_log()
    terminados_por_huella = {r["huella"]: r["archivo"] for r in registros.values()
                             if r.get("huella") and r["estado"] in TERMINADOS}
    candidatos = sorted(p for p in CARPETA.iterdir()
                        if p.is_file() and p.suffix.lower() == ".pdf")

    exitos, sin_proteccion, reconocidos = 0, 0, 0
    tratados, pendientes = [], []

    # 1) Análisis: omitir lo ya hecho (nombre + huella) y clasificar el resto
    # 1) Analysis: skip what is already done (name + fingerprint), classify the rest
    for i, p in enumerate(candidatos, 1):
        avisar(T["analizando"].format(archivo=p.name), i, len(candidatos))
        h = huella(p)
        previo = registros.get(p.name)
        if previo and previo["estado"] in TERMINADOS:
            if not previo.get("huella"):      # log antiguo sin huella / old log, no fingerprint
                previo["huella"] = h
                continue
            if previo["huella"] == h:         # mismo archivo, ya hecho / same file, done
                continue
            # mismo nombre, contenido distinto: se reprocesa / same name, new content: redo
        elif h in terminados_por_huella:      # renombrado o copia / renamed or copied
            estado_previo = registros[terminados_por_huella[h]]["estado"]
            registrar(registros, p, estado_previo,
                      detalle=T["det_mismo"].format(archivo=terminados_por_huella[h]))
            reconocidos += 1
            continue

        tratados.append(p)
        try:
            with pikepdf.open(p) as doc:
                cifrado = doc.is_encrypted
        except pikepdf.PasswordError:
            pendientes.append(p)
            continue
        except Exception as e:
            registrar(registros, p, E["err_arch"], detalle=str(e))
            continue
        if not cifrado:
            registrar(registros, p, E["sin"])
            sin_proteccion += 1
            continue
        try:  # solo restricciones de impresión/copia / print/copy restrictions only
            desproteger(p, "")
            registrar(registros, p, E["ok"], detalle=T["det_restricciones"])
            exitos += 1
        except Exception as e:
            registrar(registros, p, E["err_arch"], detalle=str(e))

    intentados = len(tratados) - sin_proteccion

    # 2) Cada contraseña en todos los pendientes; la siguiente solo en los fallidos
    # 2) Each password on all pending files; the next one only on those that failed
    for n, pw in enumerate(contraseñas, 1):
        siguientes = []
        for i, p in enumerate(pendientes, 1):
            avisar(T["descifrando"].format(n=n, total=len(contraseñas), archivo=p.name),
                   i, len(pendientes))
            try:
                desproteger(p, pw)
                registrar(registros, p, E["ok"], n)
                exitos += 1
            except pikepdf.PasswordError:
                siguientes.append(p)
            except Exception as e:  # p. ej. abierto en otro programa / e.g. open elsewhere
                registrar(registros, p, E["err_arch"], n, str(e))
        pendientes = siguientes

    for p in pendientes:
        registrar(registros, p, E["err_pw"], detalle=T["det_fallo"].format(n=len(contraseñas)))

    guardar_log(registros)
    legible = {E["err_pw"]: T["err_pw"], E["err_arch"]: T["err_arch"]}
    nombres = {p.name for p in tratados}
    fallos = [f"{r['archivo']} ({legible.get(r['estado'], r['estado'])})"
              for r in registros.values()
              if r["archivo"] in nombres and r["estado"] not in TERMINADOS]
    return exitos, intentados, sin_proteccion, reconocidos, fallos


def pedir_contraseñas(raiz):
    """Devuelve la lista de contraseñas, o None si se cancela.
    Returns the list of passwords, or None if cancelled."""
    import tkinter as tk

    contraseñas, ejecutar = [], [False]
    dlg = tk.Toplevel(raiz)
    dlg.title(T["titulo"])
    dlg.resizable(False, False)
    dlg.attributes("-topmost", True)
    etiqueta = tk.Label(dlg, padx=20, pady=10)
    etiqueta.pack()
    campo = tk.Entry(dlg, show="*", width=40)
    campo.pack(padx=20)
    aviso = tk.Label(dlg, fg="red")
    aviso.pack()

    def refrescar():
        etiqueta.config(text=T["contraseña_n"].format(n=len(contraseñas) + 1,
                                                      k=len(contraseñas)))
        campo.delete(0, tk.END)
        campo.focus_set()

    def añadir():
        if not campo.get():
            aviso.config(text=T["falta_una"])
            return
        contraseñas.append(campo.get())
        aviso.config(text="")
        refrescar()

    def aceptar():
        if campo.get():
            contraseñas.append(campo.get())
        if not contraseñas:
            aviso.config(text=T["falta_alguna"])
            return
        ejecutar[0] = True
        dlg.destroy()

    botones = tk.Frame(dlg, pady=10)
    botones.pack()
    tk.Button(botones, text=T["btn_añadir"], command=añadir).pack(side="left", padx=5)
    tk.Button(botones, text=T["btn_ejecutar"], command=aceptar).pack(side="left", padx=5)
    tk.Button(botones, text=T["btn_cancelar"], command=dlg.destroy).pack(side="left", padx=5)

    refrescar()
    raiz.wait_window(dlg)
    return contraseñas if ejecutar[0] else None


def instalar_pikepdf(raiz):
    """Ofrece instalar pikepdf con pip.
    Offers to install pikepdf with pip."""
    from tkinter import messagebox
    import tkinter as tk

    if not messagebox.askyesno(T["titulo"], T["falta_pikepdf"]):
        return
    # pythonw.exe no tiene salida; pip se lanza con python.exe, en la misma carpeta.
    # pythonw.exe has no output; pip runs with python.exe, from the same folder.
    python = Path(sys.executable).with_name("python.exe")
    en_venv = sys.prefix != sys.base_prefix  # --user no está permitido en un venv / not allowed in a venv
    cmd = [str(python), "-m", "pip", "install", "--disable-pip-version-check", "pikepdf"]
    if not en_venv:
        cmd.append("--user")  # sin administrador aunque Python esté en Program Files / no admin needed

    ventana = tk.Toplevel(raiz)
    ventana.title(T["titulo"])
    ventana.attributes("-topmost", True)
    ventana.protocol("WM_DELETE_WINDOW", lambda: None)
    tk.Label(ventana, text=T["instalando"], font=("Segoe UI", 11, "bold"),
             padx=40, pady=20).pack()
    ventana.update()

    # pip corre en un hilo para que la ventana siga respondiendo (si no, Windows la marca "No responde").
    # pip runs in a thread so the window keeps responding (otherwise Windows marks it "Not responding").
    resultado = {}
    hilo = threading.Thread(target=lambda: resultado.update(r=subprocess.run(
        cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)))
    hilo.start()
    while hilo.is_alive():
        ventana.update()
        time.sleep(0.05)
    ventana.destroy()

    r = resultado["r"]
    if r.returncode != 0:
        detalle = "\n".join((r.stderr or r.stdout).strip().splitlines()[-6:])
        messagebox.showerror(T["titulo"], T["fallo_instalacion"].format(
            cmd=subprocess.list2cmdline(cmd), detalle=detalle))
        return
    # Se pide reabrir en lugar de relanzar solo: un proceso nuevo ve el paquete sin trucos con sys.path.
    # Asks to reopen instead of relaunching itself: a new process sees the package without sys.path tricks.
    messagebox.showinfo(T["titulo"], T["instalado"])


def texto_avance(texto, i, total):
    """Ejemplo / example: "(50%) Analizando: factura.pdf · 3/6"."""
    return f"({i / total:.0%}) {texto} · {i}/{total}"


def main():
    import tkinter as tk
    from tkinter import messagebox

    raiz = tk.Tk()
    raiz.withdraw()

    if pikepdf is None:
        instalar_pikepdf(raiz)
        return

    contraseñas = pedir_contraseñas(raiz)
    if contraseñas is None:
        return

    ventana = tk.Toplevel(raiz)
    ventana.title(T["titulo"])
    ventana.attributes("-topmost", True)
    ventana.protocol("WM_DELETE_WINDOW", lambda: None)
    tk.Label(ventana, text=T["en_proceso"], font=("Segoe UI", 11, "bold"),
             padx=30, pady=10).pack()
    avance = tk.Label(ventana, text="", width=70, anchor="w", padx=30, pady=10)
    avance.pack()
    ventana.update()

    def avisar(texto, i, total):
        avance.config(text=texto_avance(texto, i, total))
        ventana.update()

    try:
        exitos, intentados, sin_prot, reconocidos, fallos = procesar(contraseñas, avisar)
    except PermissionError:
        ventana.destroy()
        messagebox.showerror(T["titulo"], T["log_abierto"])
        return
    ventana.destroy()

    if intentados == 0 and sin_prot == 0 and reconocidos == 0:
        messagebox.showinfo(T["titulo"], T["nada_pendiente"])
        return
    msg = T["resumen"].format(exitos=exitos, intentados=intentados)
    if sin_prot:
        msg += "\n" + T["sin_prot"].format(n=sin_prot)
    if reconocidos:
        msg += "\n" + T["reconocidos"].format(n=reconocidos)
    if fallos:
        msg += f"\n\n{T['no_desprotegidos']}\n" + "\n".join(fallos[:15])
        if len(fallos) > 15:
            msg += "\n" + T["y_mas"].format(n=len(fallos) - 15, log=T["log"])
        messagebox.showwarning(T["titulo"], msg)
    else:
        messagebox.showinfo(T["titulo"], msg)


if __name__ == "__main__":
    main()
