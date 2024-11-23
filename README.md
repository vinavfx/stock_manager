# Stock Manager
Stock manager for <b>Nuke</b> that indexes the stocks in a lighter version of jpg
to be able to visualize it and be able to quickly choose the correct stock
for the shot that requires it. 

Showing: <a href=https://vinavfx.com/blog target='_blank'>https://vinavfx.com/blog</a>

# Feautres
- <b>Quick</b> display of any video or texture in stock
- <b>Automatic labeling</b> using the name of the file or its folder
- <b>Fast search</b>, since the indexing remains in memory
- Various forms of <b>display and loading</b>

# Installation
1 - Copy to nuke folder
```sh
# Linux:
cd ~/.nuke
git clone --recursive https://github.com/vinavfx/stock_manager.git

# Windows
# Download git: https://git-scm.com/download/win
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

4 - Dependencies ( <b>FFmpeg, ImageMagick</b> )
- Linux
```sh
# Any redhat distro clone, for others look for installation method
sudo dnf -y install ffmpeg, convert
```

# Indexing
To be able to view your stock in the viewer, you first have to modify 
the variables in env.py and then index the folders.

1 - Modify <b>env.py</b>
```python
INDEXING_DIR = '<path_where_it_will_be_indexed>'

ROOT_STOCKS_DIRS = [
    '<path_your_stocks',
    '<extra_path_your_stocks',
    '<extra_path_your_stocks',
    ...
]
```

2 - To index (Terminal only)
```sh
cd ~/.nuke/stock_manager/scripts
python3 indexing.py
```

# Screenshots

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
