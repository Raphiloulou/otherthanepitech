# test game py 🎮

yo, welcome. this is a little top-down shooter i made with Python and Pygame, built with an AI coding assistant (Claude Code).

you move, you dodge, you shoot. 15 rooms, 3 different worlds, a boss every 5 rooms. simple, but it gets kinda brutal ngl.

## how to run it

takes like 2 minutes, promise.

**1. get Python**

grab it from [python.org](https://www.python.org/downloads/) if you don't have it already.

**2. get the game**

hit the green **Code** button up top, then **Download ZIP**, and unzip it wherever. or if you're fancy:

```bash
git clone https://github.com/Raphiloulou/otherthanepitech.git
```

**3. open a terminal in the game folder**

in VS Code: **File > Open Folder**, pick the game folder, then **Terminal > New Terminal**.

**4. install pygame-ce** (one time only)

on Windows:

```bash
py -m pip install pygame-ce
```

on Mac or Linux:

```bash
python3 -m pip install pygame-ce
```

**5. play**

on Windows:

```bash
py jeu.py
```

on Mac or Linux:

```bash
python3 jeu.py
```

a window pops up and you're in. click on it if your keys aren't doing anything.

## controls

| key | what it does |
|---|---|
| Arrows or Z Q S D | move |
| Mouse | aim |
| Stand still | auto-shoot at your cursor |
| Left click or Space | shoot while moving |
| R | restart after a game over or a win |
| Esc | quit (rage quit included) |

heads up: Z Q S D is for AZERTY keyboards. on QWERTY, just use the arrows.

## how it works

- clear every enemy and the door opens
- walk through it and pick 1 of 3 powers
- trees, graves and rocks block bullets, so use them
- standing still means free shots, but you're also a free target. good luck

## it's not working??

- **`No module named 'pygame'`**: you skipped step 4, or VS Code is using another Python. press `Ctrl+Shift+P`, pick **Python: Select Interpreter**, and choose the one you installed pygame-ce on.
- **`can't open file`**: your terminal isn't in the game folder. `cd` into it and try again.
- **`py` or `python3` isn't recognized**: Python isn't installed right. reinstall it and tick **Add Python to PATH** on Windows.

have fun, and if you beat it, respect fr.
