# OS-Escape-Room

## MVP: Room 1 - Scheduling

The first playable room is a scheduling puzzle where the player assigns tasks and chooses a CPU scheduling algorithm.

### Room 1 Objective

Assign tasks to the scheduler, switch algorithms, and compare the average waiting/turnaround times shown on screen.

Press `Enter` in Room 1 to submit your selected algorithm. If it has the best average waiting time for the current task set, Room 2 unlocks.

### Controls

- `Enter` on homepage: start game
- `Esc`: exit current screen
- `A`: assign/add a new task
- `R`: reset tasks to default
- `1`: choose FCFS
- `2`: choose SJF (non-preemptive)
- `3`: choose Round Robin (`q=2`)
- `Enter` in Room 1: submit current algorithm
- `R` in Room 2: replay Room 1

### Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python main.py
```