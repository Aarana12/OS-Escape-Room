# OS-Escape-Room

## MVP: Room 1 - Scheduling

The first playable room is a scheduling puzzle where the player assigns tasks and chooses a CPU scheduling algorithm.

### Room 1 Objective

Assign tasks to the scheduler, switch algorithms, and compare the average waiting/turnaround times shown on screen.

Press `Enter` in Room 1 to submit your selected algorithm. If it has the best average waiting time for the current task set, Room 2 unlocks.

## MVP: Room 2 - Deadlock

Room 2 is a deadlock-prevention puzzle. The player avoids deadlock by choosing an order of process allocation steps.

### Room 2 Objective

Create a 6-step process order that allows all processes to complete without deadlock:

- `P1` needs `R1 -> R2`
- `P2` needs `R2 -> R3`
- `P3` needs `R3 -> R1`

Press `Enter` in Room 2 to simulate your chosen order.

### Controls

- `Enter` on homepage: start game
- `Esc`: exit current screen
- `A`: assign/add a new task
- `R`: reset tasks to default
- `1`: choose FCFS
- `2`: choose SJF (non-preemptive)
- `3`: choose Round Robin (`q=2`)
- `Enter` in Room 1: submit current algorithm
- `1` / `2` / `3` in Room 2: add `P1` / `P2` / `P3` step to allocation order
- `Backspace` in Room 2: remove last step
- `Enter` in Room 2: simulate allocation order
- `R` in Room 2: reset Room 2 puzzle

### Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python main.py
```