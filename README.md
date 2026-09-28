# PDF Protection Remover

[English](#english) · [Español](#español)

---

## English

Windows tool that removes the password from every PDF in a folder, using one or more passwords **you already know**. It does not crack or guess passwords.

### What it does

- Processes every PDF in the script's folder (subfolders are not included).
- Accepts several passwords: tries the first one on all files, the second one only on those that failed, and so on.
- Before overwriting each PDF, saves a copy of the encrypted original in the `Originals` folder (created if missing; earlier copies are never overwritten).
- Keeps a log (`unprotect_log.csv`) to avoid repeating work: the next run only handles new files or files that failed.
- Uses a **fingerprint** (SHA-256 of the content) to recognise files already handled even if renamed or copied, and reprocesses a file if it was replaced by another one with the same name.
- Detects PDFs with no protection and PDFs with print/copy restrictions only (these are unlocked without a password).
- Shows progress, e.g. `(50%) Analyzing: invoice.pdf · 3/6`, and a final summary: files unprotected out of files attempted, plus a list of failures.
- **Passwords are never stored**: not on disk, not in the log, nowhere. You must enter them again every time you run the program.
- **Works offline.** Everything happens on your computer; no document or password ever leaves it. Internet is only needed once, to install pikepdf.

### Installation

1. Install Python 3 from [python.org](https://www.python.org/downloads/). During setup tick **"Add Python to PATH"**.
2. Open a console (`cmd`) and run:
   ```
   pip install pikepdf
   ```
   or, from the repository folder, `pip install -r requirements.txt`.

   If you skip this step, the program detects it on startup and offers to install pikepdf for you.

### Usage

1. Copy `pdf_protection_remover.pyw` into the folder containing the PDFs.
2. Double-click it.
3. Enter a password. Click **Add another password** to enter more, or **OK and run** to start. Since they are not stored, you will have to type them every time.
4. When finished, check the summary and, if needed, the log.

### Log

File `unprotect_log.csv`, `;`-separated so it opens directly in Excel. Columns: `file`, `status`, `password_no` (order of the password that worked), `date`, `fingerprint`, `detail`.

| Status | Meaning | Retried on next run? |
|---|---|---|
| `UNLOCKED` | Successfully unlocked | No |
| `NOT_PROTECTED` | The file had no password | No |
| `WRONG_PASSWORD` | Could not be opened with any password | Yes |
| `FILE_ERROR` | Damaged file or open in another program | Yes |

If the log is open in Excel when the script runs, it cannot be saved: close it and run again.

### Language

Texts, the log name, the originals folder and the status codes are shown in Spanish if the computer's regional settings are Spanish, and in English otherwise.

### Responsible use

Use it only with documents you own or are authorised to handle. The tool does not bypass protection: it needs the correct password.

### License

MIT. See [LICENSE](LICENSE).

---

## Español

Herramienta para Windows que elimina la contraseña de todos los PDF de una carpeta, usando una o varias contraseñas que **tú ya conoces**. No rompe ni adivina contraseñas.

### Qué hace

- Procesa todos los PDF de la carpeta donde está el script (no entra en subcarpetas).
- Acepta varias contraseñas: prueba la primera en todos los archivos, la segunda solo en los que fallaron, y así sucesivamente.
- Antes de sobrescribir cada PDF, guarda una copia del original cifrado en la carpeta `Originales` (la crea si no existe; nunca pisa una copia anterior).
- Lleva un registro (`log_desproteccion.csv`) para no repetir trabajo: en la siguiente ejecución solo trata los archivos nuevos o los que fallaron.
- Reconoce por su **huella** (SHA-256 del contenido) los archivos ya tratados aunque se hayan renombrado o copiado, y vuelve a tratar un archivo si se ha sustituido por otro con el mismo nombre.
- Detecta los PDF sin protección y los que solo tienen restricciones de impresión o copia (estos se desprotegen sin contraseña).
- Muestra el avance, por ejemplo `(50%) Analizando: factura.pdf · 3/6`, y al final un resumen: archivos desprotegidos sobre intentados y lista de fallos.
- **Las contraseñas nunca se guardan**: ni en disco, ni en el log, ni en ningún otro sitio. Hay que escribirlas de nuevo cada vez que se ejecuta el programa.
- **Funciona sin conexión a Internet.** Todo el proceso ocurre en tu equipo; ningún documento ni contraseña sale de él. Solo hace falta Internet una vez, para instalar pikepdf.

### Instalación

1. Instala Python 3 desde [python.org](https://www.python.org/downloads/). Durante la instalación marca **"Add Python to PATH"**.
2. Abre una consola (`cmd`) y ejecuta:
   ```
   pip install pikepdf
   ```
   o, desde la carpeta del repositorio, `pip install -r requirements.txt`.

   Si te saltas este paso, el programa lo detecta al abrirse y ofrece instalar pikepdf por ti.

### Uso

1. Copia `pdf_protection_remover.pyw` en la carpeta que contiene los PDF.
2. Ábrelo con doble clic.
3. Escribe una contraseña. Pulsa **Añadir otra contraseña** para introducir más, o **Aceptar y ejecutar** para empezar. Como no se guardan, tendrás que escribirlas cada vez.
4. Al terminar, revisa el resumen y, si hace falta, el log.

### Registro (log)

Archivo `log_desproteccion.csv`, separado por `;` para abrirse directamente en Excel. Columnas: `archivo`, `estado`, `contraseña_nº` (orden de la contraseña que funcionó), `fecha`, `huella`, `detalle`.

| Estado | Significado | ¿Se reintenta en la siguiente ejecución? |
|---|---|---|
| `DESPROTEGIDO` | Desprotegido con éxito | No |
| `SIN_PROTECCION` | El archivo no tenía contraseña | No |
| `ERROR_CONTRASEÑA` | No se abrió con ninguna contraseña | Sí |
| `ERROR_ARCHIVO` | Archivo dañado o abierto en otro programa | Sí |

Si el log está abierto en Excel al ejecutar el script, no se podrá guardar: ciérralo y vuelve a ejecutar.

### Idioma

Los textos, el nombre del log, la carpeta de originales y los estados se muestran en español si la configuración regional del equipo es española, y en inglés en cualquier otro caso.

### Uso responsable

Utilízala solo con documentos de tu propiedad o sobre los que tengas autorización. La herramienta no elude la protección: necesita la contraseña correcta.

### Licencia

MIT. Consulta [LICENSE](LICENSE).
