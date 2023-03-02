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
git clone --recursive https://github.com/vinavfx/stock_manager.git "~/.nuke/stock_manager"

# Windows
git clone --recursive https://github.com/vinavfx/stock_manager.git "C:\Users\<username>\.nuke\stock_manager"

# Or manually copy the entire git downloaded folder and its submodules to the nuke user folder
```

2 - Copy this line to <b>init.py</b>
```python
import stock_manager
```

3 - Copy this line to <b>menu.py</b>
```python
stock_manager.setup()
```

4 - Dependencies ( <b>FFMPEG</b> )
- Linux
```sh
# Any redhat distribution clone, for others look for ffmpeg installation method
sudo dnf -y install ffmpeg
```
- Windows

Download [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip)
manually and copy loose <b>ffmpeg.exe</b> and <b>ffprobe.exe</b> to the 'stock_manager' folder
"C:\Users\username\\.nuke\stock_manager"

# Tips

- If any action that you index does not have a label it is because it is not 
in the list, you can add the type labels - element in [indexing.py](./src/indexing.py)
and re-index and that's it

# Screenshots

- <b>INDEXING</b>

<p align="center"> <img src='screenshots/indexing.jpg' width=70%> </p>

- <b>STATUS BAR</b>

<p align="center"> <img src='screenshots/status_bar.jpg' width=70%> </p>

- <b>DISPLAY OPCIONS</b>

<p align="center"> <img src='screenshots/display.jpg' width=70%> </p>

- <b>FILTER BAR</b>

<p align="center"> <img src='screenshots/filter.jpg' width=70%> </p>

- <b>GRID</b> mode

<p align="center"> <img src='screenshots/grid.jpg' width=70%> </p>

- <b>LIST</b> mode

<p align="center"> <img src='screenshots/list.jpg' width=70%> </p>

