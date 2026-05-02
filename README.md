# Operating System Escape Room

An interactive classroom game where players solve operating system puzzles to escape each room.

## Demo Format

We plan to present this as a live demo and make it interactive with the class, similar to an in-class game format.

- The class helps solve puzzles in real time.
- The winning team gets a dozen cookies.

## Project Concept

The game is built around OS concepts that players actively use while solving puzzles.

Current playable rooms:

1. Room 1: CPU Scheduling
2. Room 2: Deadlock Prevention

Planned and explored ideas include adding more puzzle rooms and richer UI interactions.

## Tech Stack

Primary stack in this repository:

- Python
- Pygame

Explored and discussed for future use:

- Tkinter for additional GUI puzzle panels
- JavaScript or TypeScript based visual components
- Additional Python game libraries as needed

## General Game Flow

Current implemented flow:

1. Pygame runs the main game loop.
2. Player solves an OS puzzle room.
3. Success unlocks the next room.

Proposed extended flow (future option):

1. Pygame triggers a puzzle interaction.
2. A Tkinter panel opens for that puzzle.
3. Result is returned to Pygame and progress continues.

## Team Roles

- Project Manager: Dana
- Gameplay and Logic Programmer: Areli
- UI and Frontend Developers: Nicolas, Camrynne
- Documentation Lead: Raymond

Notes:

- UI and frontend work is split between visual interface and interface logic.
- Team members may overlap into logic and programming as needed.
- A lead tracks progress and follow-up to keep tasks moving.

## Collaboration and Organization

- Code hosting: GitHub
- Repository: https://github.com/Aarana12/OS-Escape-Room.git
- Team communication: Discord
- Planning cadence: Weekly sprints
- Work tracking: what is planned, in progress, and completed is tracked through sprint check-ins and repository activity

## Rough Presentation Outline

1. Design Process
2. Sprint Timeline and Progress
3. Features
4. Tech Stack
5. Live Demo
6. Takeaways, Mistakes, and Lessons Learned

## Week 1 Progress Update

Completed in Week 1:

- Team discussion on communication tools
- Tech stack decisions (languages, libraries, IDEs)
- GitHub repository setup and team invites
- Sprint planning kickoff
- Homepage implementation for the escape room game

## Current Game Details

### Room 1: Scheduling

Goal: choose the best scheduling algorithm for the task set.

- Switch algorithms and inspect behavior.
- Submit your choice in Room 1.
- A correct choice unlocks Room 2.

### Room 2: Deadlock Prevention

Goal: build a safe allocation order so all processes complete without deadlock.

- P1 needs R1 then R2
- P2 needs R2 then R3
- P3 needs R3 then R1

## Controls

Global and menu:

- Enter on homepage: start game
- Esc: exit current screen

Room 1:

- 1: choose FCFS
- 2: choose SJF (non-preemptive)
- 3: choose Round Robin (q=2)
- A: add a new task
- Enter: submit algorithm
- Left and Right: replay scheduler timeline
- R: reset tasks and attempts

Room 2:

- 1, 2, 3: add P1, P2, P3 to allocation order
- Backspace: remove last step
- Enter: simulate allocation order
- Left and Right: replay simulation
- Space: jump to final replay step
- R: reset Room 2 puzzle

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python main.py
```