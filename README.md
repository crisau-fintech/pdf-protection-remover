# PDF Protection Remover

Windows tool that removes the password from every PDF in a folder, using one or
more passwords **you already know**. It does not crack or guess passwords.

## Requirements

- Windows
- Python 3 from [python.org](https://www.python.org/downloads/) (during setup, tick
  **"Add Python to PATH"**)
- The `pikepdf` library. If it is missing, the program detects it on startup and
  offers to install it for you.

## Install

1. Install Python 3 (see above).
2. Optionally, install pikepdf yourself by opening a console (`cmd`) and running
   `pip install pikepdf` (or `pip install -r requirements.txt` from this folder).
   If you skip this step, the program offers to do it the first time you open it.

## Usage

1. Copy `pdf_protection_remover.pyw` into the folder that contains the PDFs.
2. Double-click it.
3. Enter a password. Click **Add another password** to enter more, or **OK and
   run** to start. Passwords are not stored, so you type them every time.
4. When it finishes, check the summary and, if needed, the log.

## What it does

- Processes every PDF in the script's folder (subfolders are not included).
- Accepts several passwords: tries the first one on all files, the second one only
  on those that failed, and so on.
- Before overwriting each PDF, saves a copy of the encrypted original in the
  `Originals` folder (created if missing; earlier copies are never overwritten).
- Keeps a log (`unprotect_log.csv`) to avoid repeating work: the next run only
  handles new files or files that failed.
- Uses a **fingerprint** (SHA-256 of the content) to recognise files already
  handled even if renamed or copied, and reprocesses a file if it was replaced by
  another one with the same name.
- Detects PDFs with no protection and PDFs with print/copy restrictions only (these
  are unlocked without a password).
- Shows progress, e.g. `(50%) Analyzing: invoice.pdf · 3/6`, and a final summary:
  files unprotected out of files attempted, plus a list of failures.
- **Passwords are never stored**: not on disk, not in the log, nowhere.
- **Works offline.** Everything happens on your computer; no document or password
  ever leaves it. Internet is only needed once, to install pikepdf.

## Log

File `unprotect_log.csv`, `;`-separated so it opens directly in Excel. Columns:
`file`, `status`, `password_no` (order of the password that worked), `date`,
`fingerprint`, `detail`.

| Status | Meaning | Retried on next run? |
|---|---|---|
| `UNLOCKED` | Successfully unlocked | No |
| `NOT_PROTECTED` | The file had no password | No |
| `WRONG_PASSWORD` | Could not be opened with any password | Yes |
| `FILE_ERROR` | Damaged file or open in another program | Yes |

## Language

The program follows Windows' regional settings: in Spanish if they are Spanish,
in English otherwise. In Spanish, the names change as follows:

| English | Spanish |
|---|---|
| `unprotect_log.csv` | `log_desproteccion.csv` |
| `Originals` folder | `Originales` folder |
| `UNLOCKED` | `DESPROTEGIDO` |
| `NOT_PROTECTED` | `SIN_PROTECCION` |
| `WRONG_PASSWORD` | `ERROR_CONTRASEÑA` |
| `FILE_ERROR` | `ERROR_ARCHIVO` |

## Troubleshooting

**The log could not be saved.** It was open in Excel when the program ran. The
program stops before touching any PDF, so nothing is lost: close the log and run
the program again.

**A file shows `WRONG_PASSWORD`.** None of the passwords you entered opens it. Run
the program again with the right one; files already unlocked are skipped.

## Responsible use

Use it only with documents you own or are authorised to handle. The tool does not
bypass protection: it needs the correct password.

## License

MIT. See [LICENSE](LICENSE).
