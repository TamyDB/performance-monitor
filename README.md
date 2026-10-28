# Performance Monitor

**Performance Monitor** is an educational Python desktop application for Windows that explores how software can present a legitimate-looking interface while performing an unexpected action—a form of deception associated with Trojan horses.

The application presents a PC diagnostic menu, displays simulated progress, and then interrupts the sequence with a fictional security alert and multiple windows playing Bad Apple. The alert reveals that the sequence is a prank.

## Download and run

**Download [PcDiagnostic.exe from the latest GitHub release](https://github.com/TamyDB/performance-monitor/releases/latest) and open it on Windows.**

No Python installation, dependency setup, or separate video download is required to run the packaged application.

To stop the application:

- Press **Esc** while any application window has focus.
- Close any application window.
- Wait for the automatic shutdown, **45 seconds after the alert**.

## Project purpose

This project uses a local simulation to explore deceptive interfaces and social engineering concepts associated with Trojans. It also provides practice with desktop development, object-oriented programming, event handling, background tasks, resource encryption, and Windows executable packaging.

The diagnostic interface is simulated: it does not measure system performance or check hardware health. The application does not implement remote access, credential collection, data exfiltration, persistence, or propagation. Encryption applies to the bundled video resource, not to the user's files.

## Features

- Component selection: CPU, RAM, graphics card, and storage.
- Video preparation in a background thread and simulated diagnostic progress.
- Fictional compromise alert with a prank reveal.
- Video windows appearing every **150 ms** at random screen positions.
- A maximum of **12 simultaneous video windows**, after which existing windows reappear at new positions.
- Looping playback with audio enabled in only one window.
- Exit through Esc, closing any window, or the 45-second timeout.

Simultaneous video playback consumes CPU, memory, and GPU resources. The window limit bounds the number of players; performance still depends on the computer. Run the simulation on your own devices or with the participants' permission.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python | Application logic and object-oriented structure |
| PySide6 / Qt | Desktop interface, events, and audio/video playback |
| cryptography | AES-256-GCM authenticated encryption of the video resource |
| PyInstaller | Packaging the application into a Windows executable |
| GitHub Actions | Windows builds and release publishing |

## Development

The following steps are for contributors who want to run the source or build their own executable. Release users can use the download above.

### Run from source

On Windows, install 64-bit Python and place `bad-apple.mp4` in the project root. An MP4 encoded with H.264 video and AAC audio is recommended for compatibility.

From PowerShell in the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Development mode reads the local MP4 directly. Dependencies are declared in `requirements.txt`.

### Build a Windows executable

Run the build on Windows:

```powershell
.\.venv\Scripts\python.exe build.py
```

To use a different video path:

```powershell
.\.venv\Scripts\python.exe build.py --video 'C:\Videos\bad-apple.mp4'
```

The output is `dist\PcDiagnostic.exe`. The executable bundles the Python interpreter, required libraries, and encrypted video. Single-file packaging extracts runtime libraries to a temporary directory when launched; it does not mean that everything runs exclusively in memory.

### GitHub Actions releases

The workflow in `.github/workflows/release.yml` builds on Windows x64 using Python 3.12. Trigger it manually from the **Actions** tab or by pushing a tag matching `v*`.

Because `*.mp4` files are ignored by Git, provide a direct HTTPS video URL through either:

- The `video_url` input when starting the workflow manually.
- The repository variable `BAD_APPLE_VIDEO_URL`, under **Settings → Secrets and variables → Actions → Variables**.

The workflow downloads and encrypts the video during the build, checks Python syntax, runs the encryption tests, and publishes a release containing `PcDiagnostic.exe` and `SHA256SUMS.txt`. It also retains these files as a workflow artifact for 14 days. Manual runs generate a release tag from the workflow run ID and attempt number.

## Video encryption and limitations

Each build generates a random 256-bit AES key and nonce. The video is encrypted using AES-GCM and bundled into the executable alongside the key. This avoids distributing a separate MP4, but **does not prevent extraction through reverse engineering**, because the application needs the key to play the video.

In the packaged application, the entire video is decrypted before playback into `%TEMP%\PcDiagnostic-<identifier>\playback.mp4`. The decrypted file can be accessed there while the application runs. The application attempts to remove it during normal shutdown; forced termination or open file handles can leave temporary files behind.

The current implementation reads the entire video into memory during encryption and decryption. A publicly hosted source URL also remains publicly accessible. Resource encryption is not a mechanism for evading security tools or guaranteeing that users cannot extract the video.

## Project structure

- `app.py`: interface, video preparation, playback, and shutdown.
- `media.py`: authenticated encryption and video resource format.
- `build.py`: resource preparation and executable packaging.
- `build.ps1`: optional PowerShell build shortcut.
- `tests/test_media.py`: encryption integrity and decryption tests.
- `.github/workflows/release.yml`: Windows build and release publishing.

## Testing

Run the encryption tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests cover recovery of the original content and rejection of tampered data, incorrect keys, and invalid resource formats. They do not validate the interface or media playback.

Python syntax and encryption tests have been checked in the Linux development environment. The visual behavior and packaged executable still require validation on Windows, including Esc handling, window closing, the 45-second timeout, and temporary-file cleanup.
