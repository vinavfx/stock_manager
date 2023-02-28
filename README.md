# Stock Manager
Stock manager for <b>Nuke</b> that indexes the stocks in a lighter version of jpg
to be able to visualize it and be able to quickly choose the correct stock
for the shot that requires it. and just it will support Nuke with Python 3,
not to dirty the code,

# Feautres
- <b>Quick</b> display of any video or texture in stock
- <b>Automatic labeling</b> using the name of the file or its folder
- <b>Fast search</b>, since the indexing remains in memory
- Various forms of <b>display and loading</b>

# Installation
1 - Copy to nuke folder
```sh
# Linux:
git clone --recursive https://github.com/fcocc77/stock_manager.git "~/.nuke/stock_manager"

# Windows
git clone --recursive https://github.com/fcocc77/stock_manager.git "C:\Users\<username>\.nuke\stock_manager"

# Or manually copy the entire git downloaded folder and its submodules to the nuke user folder
```

2 - Copy this line to <b>menu.py</b>
```python
import stock_manager
```

3 - Dependencies ( <b>FFMPEG</b> )
- Linux
```sh
# Any redhat distribution clone, for others look for ffmpeg installation method
sudo dnf -y install ffmpeg
```
- Windows

Download ffmpeg manually and copy it to loose stock manager folder as
<a href="https://ffmpeg.org/download.html#build-windows" target="_blank">ffmpeg.exe</a>
"C:\Users\username\\.nuke\stock_manager"


# Screenshots

- <b>INDEXING</b>

![Alt text](screenshots/indexing.jpg?raw=true)

- <b>STATUS BAR</b>

![Alt text](screenshots/status_bar.jpg?raw=true)

- <b>DISPLAY OPCIONS</b>

![Alt text](screenshots/display.jpg?raw=true)

- <b>FILTER BAR</b>

![Alt text](screenshots/filter.jpg?raw=true)

- <b>VIEWER</b>

![Alt text](screenshots/viewer.jpg?raw=true)

