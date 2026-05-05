# Operating System Escape Room

A 9-room Pygame escape-room game where the player is trapped inside an operating system and must escape by solving OS-themed puzzles.

## Current Playable Rooms

1. CPU Scheduling
2. OS Services
3. OS Structures
4. Processes
5. Threads
6. Synchronization
7. Deadlocks
8. Main Memory
9. Virtual Memory

## Game Flow

Each room follows the same escape-room loop:

1. Search clickable objects.
2. Find Hint #1.
3. Use Hint #1 to find the OS question panel.
4. Answer the OS question to unlock Hint #2.
5. Use Hint #2 to find Hint #3.
6. Hint #3 gives a silly OS riddle that reveals the key location.
7. Find the key.
8. Click the door to escape into the hallway.
9. Enter the next room.

The final room sends the player to `FREEDOM.EXE`.

## Controls

- Mouse click: search objects / interact with doors
- Type answer: while OS question lock is open
- Enter: submit question answer
- Escape: close question or quit game
- Hallway: click next door or press Enter/Space
- Final screen: R to restart, Escape to quit

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python main.py
```

## Design Notes

This version uses a reusable room engine in `game.py`. Each room is defined in the `ROOMS` list with:

- title
- topic
- theme
- OS concept
- question and acceptable answers
- three hint texts
- clickable object rectangles

To edit a room, change its entry in `ROOMS`.


## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python main.py
```