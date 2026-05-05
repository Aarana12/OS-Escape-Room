import pygame
import random
from final_room import FinalRoom


ROOM1_CONFIG = {
    "room": "scheduling_1",
    "tasks": [
        {"name": "T1", "arrival": 0, "burst": 5},
        {"name": "T2", "arrival": 1, "burst": 3},
        {"name": "T3", "arrival": 2, "burst": 2},
    ],
    "algorithms": ["FCFS", "SJF", "RR"],
    "quantum": 2,
    "max_submit_attempts": 3,
    "max_task_edits": 3,
    "goal": "choose_best_algorithm",
}

ROOM2_CONFIG = {
    "room": "deadlock_1",
    "processes": ["P1", "P2", "P3"],
    "resources": ["R1", "R2", "R3"],
    "needs": {
        "P1": ["R1", "R2"],
        "P2": ["R2", "R3"],
        "P3": ["R3", "R1"],
    },
    "max_steps": 6,
    "goal": "complete_without_deadlock",
}


# Matrix Theme Constants

MATRIX_GREEN = (0, 255, 90)
MATRIX_LIGHT_GREEN = (170, 255, 190)
MATRIX_DIM_GREEN = (55, 170, 85)
MATRIX_BG = (0, 5, 2)
MATRIX_PANEL = (3, 18, 8)
MATRIX_DARK_PANEL = (2, 10, 5)
MATRIX_RED = (255, 70, 70)
MATRIX_YELLOW = (255, 230, 90)
MATRIX_CYAN = (90, 255, 210)
MATRIX_WHITE = (230, 255, 235)
MATRIX_GRAY = (120, 150, 125)


class MatrixRain:
    def __init__(self, font, width=800, height=600):
        self.font = font
        self.width = width
        self.height = height
        self.characters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&<>/[]{}"
        self.columns = []

        column_width = 16
        for x in range(0, width, column_width):
            self.columns.append({
                "x": x,
                "y": random.randint(-height, 0),
                "speed": random.randint(2, 7),
                "length": random.randint(8, 22),
            })

    def update_and_draw(self, screen):
        screen.fill(MATRIX_BG)

        for column in self.columns:
            x = column["x"]
            y = column["y"]

            for i in range(column["length"]):
                char = random.choice(self.characters)
                alpha_strength = max(40, 255 - i * 14)

                if i == 0:
                    color = (220, 255, 225)
                else:
                    color = (0, max(80, alpha_strength), 55)

                char_surface = self.font.render(char, True, color)
                screen.blit(char_surface, (x, y - i * 18))

            column["y"] += column["speed"]

            if column["y"] - column["length"] * 18 > self.height:
                column["y"] = random.randint(-260, -20)
                column["speed"] = random.randint(2, 7)
                column["length"] = random.randint(8, 22)

        # Dark overlay so the UI stays readable
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        screen.blit(overlay, (0, 0))


def draw_matrix_panel(screen, rect, border_color=MATRIX_GREEN, fill_color=MATRIX_PANEL, border_width=2):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(
        panel,
        (*fill_color, 220),
        pygame.Rect(0, 0, rect.width, rect.height),
        border_radius=8,
    )
    screen.blit(panel, rect.topleft)

    glow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(
        glow,
        (*border_color, 55),
        pygame.Rect(6, 6, rect.width, rect.height),
        3,
        border_radius=10,
    )
    screen.blit(glow, (rect.x - 6, rect.y - 6))

    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)


def draw_matrix_label(screen, font, text, pos, color=MATRIX_GREEN):
    x, y = pos
    glow = font.render(text, True, color)
    glow.set_alpha(85)

    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        screen.blit(glow, (x + ox, y + oy))

    main = font.render(text, True, color)
    screen.blit(main, (x, y))


def draw_wrapped_text(screen, font, text, x, y, max_width, color, line_height=20, max_lines=5):
    words = text.split()
    lines = []
    cur_line = ""

    for word in words:
        test = (cur_line + " " + word).strip()
        if font.size(test)[0] <= max_width:
            cur_line = test
        else:
            if cur_line:
                lines.append(cur_line)
            cur_line = word

    if cur_line:
        lines.append(cur_line)

    for i, line in enumerate(lines[:max_lines]):
        screen.blit(font.render(line, True, color), (x, y + i * line_height))


# Room 1: CPU Scheduling Logic

def _fcfs(tasks):
    ordered = sorted(tasks, key=lambda task: task["arrival"])
    timeline = []
    current_time = 0

    for task in ordered:
        if current_time < task["arrival"]:
            current_time = task["arrival"]

        start_time = current_time
        finish_time = start_time + task["burst"]
        wait_time = start_time - task["arrival"]
        turnaround_time = finish_time - task["arrival"]

        timeline.append({
            "name": task["name"],
            "start": start_time,
            "finish": finish_time,
            "wait": wait_time,
            "turnaround": turnaround_time,
        })

        current_time = finish_time

    return timeline


def _sjf_non_preemptive(tasks):
    pending = [dict(task) for task in tasks]
    timeline = []
    current_time = 0

    while pending:
        available = [task for task in pending if task["arrival"] <= current_time]

        if not available:
            current_time = min(task["arrival"] for task in pending)
            available = [task for task in pending if task["arrival"] <= current_time]

        chosen = min(available, key=lambda task: (task["burst"], task["arrival"], task["name"]))

        start_time = current_time
        finish_time = start_time + chosen["burst"]
        wait_time = start_time - chosen["arrival"]
        turnaround_time = finish_time - chosen["arrival"]

        timeline.append({
            "name": chosen["name"],
            "start": start_time,
            "finish": finish_time,
            "wait": wait_time,
            "turnaround": turnaround_time,
        })

        current_time = finish_time
        pending.remove(chosen)

    return timeline


def _round_robin(tasks, quantum=2):
    ready = []
    pending = sorted([dict(task) for task in tasks], key=lambda task: task["arrival"])
    remaining = {task["name"]: task["burst"] for task in tasks}
    completion_time = {}
    slices = []

    current_time = 0
    index = 0

    while index < len(pending) or ready:
        while index < len(pending) and pending[index]["arrival"] <= current_time:
            ready.append(pending[index]["name"])
            index += 1

        if not ready:
            current_time = pending[index]["arrival"]
            continue

        current_name = ready.pop(0)
        run_time = min(quantum, remaining[current_name])
        start_time = current_time
        finish_time = current_time + run_time

        slices.append(f"{current_name}[{start_time}-{finish_time}]")

        current_time = finish_time
        remaining[current_name] -= run_time

        while index < len(pending) and pending[index]["arrival"] <= current_time:
            ready.append(pending[index]["name"])
            index += 1

        if remaining[current_name] > 0:
            ready.append(current_name)
        else:
            completion_time[current_name] = current_time

    timeline = []

    for task in tasks:
        finish_time = completion_time[task["name"]]
        turnaround_time = finish_time - task["arrival"]
        wait_time = turnaround_time - task["burst"]

        timeline.append({
            "name": task["name"],
            "start": None,
            "finish": finish_time,
            "wait": wait_time,
            "turnaround": turnaround_time,
        })

    timeline.sort(key=lambda item: item["finish"])
    return timeline, slices


def _build_result(tasks, algorithm_name):
    if algorithm_name == "FCFS":
        timeline = _fcfs(tasks)
        slices = []
    elif algorithm_name == "SJF":
        timeline = _sjf_non_preemptive(tasks)
        slices = []
    else:
        timeline, slices = _round_robin(tasks, quantum=2)

    avg_wait = sum(item["wait"] for item in timeline) / len(timeline)
    avg_turnaround = sum(item["turnaround"] for item in timeline) / len(timeline)

    return {
        "timeline": timeline,
        "avg_wait": avg_wait,
        "avg_turnaround": avg_turnaround,
        "slices": slices,
        "algorithm": algorithm_name,
    }


def _best_algorithms_for_tasks(tasks):
    algorithm_names = ["FCFS", "SJF", "RR"]
    wait_by_algorithm = {}

    for algorithm_name in algorithm_names:
        wait_by_algorithm[algorithm_name] = _build_result(tasks, algorithm_name)["avg_wait"]

    best_wait = min(wait_by_algorithm.values())
    epsilon = 1e-9

    return [
        algorithm_name
        for algorithm_name, avg_wait in wait_by_algorithm.items()
        if abs(avg_wait - best_wait) < epsilon
    ]


def _build_scheduler_timeline(tasks, algorithm_name, quantum=2):
    """Return a list of tick-by-tick snapshots for replay/visualisation."""
    if algorithm_name == "FCFS":
        base = _fcfs(tasks)
        slices_raw = [(row["name"], row["start"], row["finish"]) for row in base]
    elif algorithm_name == "SJF":
        base = _sjf_non_preemptive(tasks)
        slices_raw = [(row["name"], row["start"], row["finish"]) for row in base]
    else:
        base, slice_strs = _round_robin(tasks, quantum)
        slices_raw = []

        for s in slice_strs:
            name, rest = s.split("[")
            t0, t1 = rest.rstrip("]").split("-")
            slices_raw.append((name, int(t0), int(t1)))

    arrival = {t["name"]: t["arrival"] for t in tasks}
    burst = {t["name"]: t["burst"] for t in tasks}
    all_names = [t["name"] for t in tasks]

    snapshots = []
    tick = 0

    for running_name, t_start, t_end in slices_raw:
        for t in range(t_start, t_end):
            states = {}

            for name in all_names:
                if name == running_name:
                    states[name] = "running"
                else:
                    # Fixed UI bug: calculate how much CPU time this task had before tick t.
                    executed_time = sum(
                        max(0, min(t, st_end) - st_s)
                        for sn, st_s, st_end in slices_raw
                        if sn == name
                    )

                    if executed_time >= burst[name]:
                        states[name] = "terminated"
                    elif arrival[name] <= t:
                        states[name] = "ready"
                    else:
                        states[name] = "not-arrived"

            snapshots.append({
                "tick": t,
                "running": running_name,
                "states": states,
                "slice_label": f"{running_name} [{t_start}-{t_end}]",
            })

        tick = t_end

    final_states = {name: "terminated" for name in all_names}

    snapshots.append({
        "tick": tick,
        "running": None,
        "states": final_states,
        "slice_label": "done",
    })

    result = _build_result(tasks, algorithm_name)
    wait_map = {row["name"]: row["wait"] for row in result["timeline"]}
    turnaround_map = {row["name"]: row["turnaround"] for row in result["timeline"]}

    return {
        "snapshots": snapshots,
        "slices_raw": slices_raw,
        "avg_wait": result["avg_wait"],
        "avg_turnaround": result["avg_turnaround"],
        "wait_map": wait_map,
        "turnaround_map": turnaround_map,
        "algorithm": algorithm_name,
    }


def _educational_feedback_room1(tasks, selected_algorithm):
    best = _best_algorithms_for_tasks(tasks)
    results = {alg: _build_result(tasks, alg) for alg in ["FCFS", "SJF", "RR"]}
    lines = []

    if selected_algorithm in best:
        lines.append(f"{selected_algorithm} VERIFIED — lowest avg wait time.")
        lines.append("ACCESS KEY GENERATED: scheduling puzzle solved.")
    else:
        best_str = " or ".join(best)
        sel_wait = results[selected_algorithm]["avg_wait"]
        best_wait = results[best[0]]["avg_wait"]

        lines.append(f"{selected_algorithm} avg wait = {sel_wait:.1f} | {best_str} avg wait = {best_wait:.1f}")

        if selected_algorithm == "FCFS":
            lines.append("FCFS can create convoy effect: long tasks block shorter ones.")
        elif selected_algorithm == "RR":
            lines.append("Round Robin improves fairness, but average wait is higher here.")

        if "SJF" in best:
            lines.append("SJF minimizes average wait time for this task set.")

    return lines


#Room 2: Deadlock Simulation Logic

def _simulate_deadlock_resolution(order, config):
    needs = config["needs"]
    process_ids = config["processes"]
    resource_ids = config["resources"]

    resources = {r: None for r in resource_ids}
    progress = {p: 0 for p in process_ids}
    held = {p: set() for p in process_ids}
    timeline = []

    def _get_state(pid):
        if progress[pid] >= len(needs[pid]):
            return "terminated"

        wanted = needs[pid][progress[pid]]
        owner = resources[wanted]

        if owner is not None and owner != pid:
            return "blocked"

        return "ready"

    for step, process_id in enumerate(order, start=1):
        max_steps_needed = len(needs[process_id])

        if progress[process_id] >= max_steps_needed:
            event = f"{process_id} already finished."
            action = "already_finished"
        else:
            wanted_resource = needs[process_id][progress[process_id]]
            owner = resources[wanted_resource]

            if owner is None:
                resources[wanted_resource] = process_id
                held[process_id].add(wanted_resource)
                progress[process_id] += 1

                if progress[process_id] == max_steps_needed:
                    for r in list(held[process_id]):
                        resources[r] = None

                    held[process_id].clear()
                    event = f"{process_id} acquires {wanted_resource}, completes, and releases all resources."
                    action = "completed"
                else:
                    event = f"{process_id} acquires {wanted_resource}."
                    action = "acquired"
            else:
                event = f"{process_id} blocked — {wanted_resource} held by {owner}."
                action = "blocked"

        states = {pid: _get_state(pid) for pid in process_ids}

        if action in ("acquired", "completed"):
            states[process_id] = "running"

        snapshot = {
            "step": step,
            "process_id": process_id,
            "action": action,
            "event": event,
            "states": dict(states),
            "held": {p: set(s) for p, s in held.items()},
            "resources": dict(resources),
            "progress": dict(progress),
            "deadlock": False,
            "chain": [],
        }

        unfinished = [pid for pid in process_ids if progress[pid] < len(needs[pid])]

        if unfinished:
            blocked_pids = [
                pid for pid in unfinished
                if resources[needs[pid][progress[pid]]] is not None
                and resources[needs[pid][progress[pid]]] != pid
            ]

            if len(blocked_pids) == len(unfinished):
                chain = [
                    f"{pid} waits for {needs[pid][progress[pid]]} held by "
                    f"{resources[needs[pid][progress[pid]]]}"
                    for pid in unfinished
                ]

                snapshot["deadlock"] = True
                snapshot["chain"] = chain
                snapshot["event"] += " -> DEADLOCK DETECTED"
                timeline.append(snapshot)

                return {"success": False, "timeline": timeline, "chain": chain}

        timeline.append(snapshot)

    if all(progress[p] >= len(needs[p]) for p in process_ids):
        return {"success": True, "timeline": timeline, "chain": []}

    return {"success": False, "timeline": timeline, "chain": ["Sequence ended before all processes completed."]}


#Main Game Loop

def run_game():
    screen = pygame.display.get_surface()

    if screen is None:
        screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("consolas", 38, bold=True)
    body_font = pygame.font.SysFont("consolas", 26, bold=True)
    small_font = pygame.font.SysFont("consolas", 20)
    tiny_font = pygame.font.SysFont("consolas", 17)
    matrix_font = pygame.font.SysFont("consolas", 18, bold=True)

    final_title_font = pygame.font.SysFont("consolas", 50, bold=True)
    final_subtitle_font = pygame.font.SysFont("consolas", 38, bold=True)
    final_small_font = pygame.font.SysFont("consolas", 17, bold=True)

    matrix_rain = MatrixRain(matrix_font)

    final_room = FinalRoom(
        final_title_font,
        final_subtitle_font,
        final_small_font,
        matrix_font,
    )

    room1_config = ROOM1_CONFIG
    tasks = [dict(t) for t in room1_config["tasks"]]
    default_tasks = [dict(t) for t in room1_config["tasks"]]

    selected_algorithm = "FCFS"
    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
    room1_replay_index = len(room1_sim["snapshots"]) - 1
    room1_feedback = []

    message = "SYSTEM LOCKED: Select optimal CPU scheduling protocol to continue."
    room_state = "room1"

    wrong_submit_attempts = 0
    submit_attempts = 0
    max_submit_attempts = room1_config["max_submit_attempts"]

    task_edits_used = 0
    max_task_edits = room1_config["max_task_edits"]

    room2_config = ROOM2_CONFIG
    room2_sequence = []
    room2_max_steps = room2_config["max_steps"]
    room2_status = "unsolved"
    room2_timeline = []
    room2_replay_index = -1
    room2_chain = []

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mouse.set_visible(True)
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    return

                if room_state == "finale":
                    continue

                # Room 2 Controls
                if room_state == "room2":
                    if event.key == pygame.K_r:
                        room2_sequence = []
                        room2_status = "unsolved"
                        room2_timeline = []
                        room2_replay_index = -1
                        room2_chain = []
                        message = "ROOM 2 RESET: Build a safe allocation sequence."

                    elif room2_status != "unsolved":
                        if event.key == pygame.K_LEFT:
                            room2_replay_index = max(0, room2_replay_index - 1)
                            message = f"REPLAY STEP {room2_replay_index + 1} / {len(room2_timeline)}."
                        elif event.key == pygame.K_RIGHT:
                            room2_replay_index = min(len(room2_timeline) - 1, room2_replay_index + 1)
                            message = f"REPLAY STEP {room2_replay_index + 1} / {len(room2_timeline)}."
                        elif event.key == pygame.K_SPACE:
                            room2_replay_index = len(room2_timeline) - 1
                            message = "REPLAY JUMPED TO FINAL STATE."

                    else:
                        if event.key == pygame.K_BACKSPACE:
                            if room2_sequence:
                                room2_sequence.pop()
                                message = "LAST PROCESS REMOVED FROM SEQUENCE."

                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            if len(room2_sequence) < room2_max_steps:
                                key_to_process = {
                                    pygame.K_1: "P1",
                                    pygame.K_2: "P2",
                                    pygame.K_3: "P3",
                                }

                                process = key_to_process[event.key]
                                room2_sequence.append(process)
                                message = f"PROCESS {process} ADDED. STEPS: {len(room2_sequence)}/{room2_max_steps}."
                            else:
                                message = "SEQUENCE FULL: Press ENTER to simulate or BACKSPACE to edit."

                        elif event.key == pygame.K_RETURN:
                            if len(room2_sequence) < room2_max_steps:
                                message = f"ADD {room2_max_steps - len(room2_sequence)} MORE STEP(S) BEFORE SIMULATION."
                            else:
                                simulation = _simulate_deadlock_resolution(room2_sequence, room2_config)

                                room2_timeline = simulation["timeline"]
                                room2_chain = simulation.get("chain", [])
                                room2_replay_index = len(room2_timeline) - 1

                                if simulation["success"]:
                                    room2_status = "solved"
                                    message = "ACCESS GRANTED: Safe sequence verified. Deadlock prevented."
                                    room_state = "finale"
                                    final_room.reset()
                                else:
                                    room2_status = "failed"
                                    message = "DEADLOCK DETECTED: Press R to reset and try a safer order."

                    continue

                # Room 1 Failed Controls
                if room_state == "room1_failed":
                    if event.key == pygame.K_r:
                        tasks = [dict(task) for task in default_tasks]
                        selected_algorithm = "FCFS"
                        room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                        room1_replay_index = len(room1_sim["snapshots"]) - 1
                        room1_feedback = []
                        room_state = "room1"
                        wrong_submit_attempts = 0
                        submit_attempts = 0
                        task_edits_used = 0
                        message = "ROOM 1 RESET: Try a new scheduling protocol."

                    continue

                # Room 1 Controls
                if event.key == pygame.K_LEFT:
                    room1_replay_index = max(0, room1_replay_index - 1)
                    message = f"TIMELINE TICK {room1_sim['snapshots'][room1_replay_index]['tick']}."

                elif event.key == pygame.K_RIGHT:
                    room1_replay_index = min(len(room1_sim["snapshots"]) - 1, room1_replay_index + 1)
                    message = f"TIMELINE TICK {room1_sim['snapshots'][room1_replay_index]['tick']}."

                elif event.key == pygame.K_SPACE:
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    message = "TIMELINE JUMPED TO FINAL TICK."

                elif event.key == pygame.K_RETURN:
                    submit_attempts += 1
                    best_algorithms = _best_algorithms_for_tasks(tasks)
                    room1_feedback = _educational_feedback_room1(tasks, selected_algorithm)

                    if selected_algorithm in best_algorithms:
                        room_state = "room2"
                        wrong_submit_attempts = 0
                        room2_sequence = []
                        room2_status = "unsolved"
                        room2_timeline = []
                        room2_replay_index = -1
                        room2_chain = []
                        message = "ACCESS GRANTED: Room 2 firewall unlocked."
                    else:
                        wrong_submit_attempts += 1

                        if submit_attempts >= max_submit_attempts:
                            room_state = "room1_failed"
                            message = "ACCESS DENIED: Terminal locked. Press R to reset."
                        else:
                            message = f"ACCESS DENIED: {max_submit_attempts - submit_attempts} attempt(s) left."

                elif event.key == pygame.K_1:
                    selected_algorithm = "FCFS"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    message = "PROTOCOL SELECTED: FCFS."

                elif event.key == pygame.K_2:
                    selected_algorithm = "SJF"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    message = "PROTOCOL SELECTED: SJF."

                elif event.key == pygame.K_3:
                    selected_algorithm = "RR"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    message = "PROTOCOL SELECTED: ROUND ROBIN q=2."

                elif event.key == pygame.K_a:
                    if task_edits_used >= max_task_edits:
                        message = "TASK EDIT LIMIT REACHED: Submit or press R to reset."
                    else:
                        next_id = len(tasks) + 1
                        burst = 2 + (next_id % 4)
                        arrival = max(0, next_id - 2)

                        tasks.append({"name": f"T{next_id}", "arrival": arrival, "burst": burst})
                        task_edits_used += 1

                        room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                        room1_replay_index = len(room1_sim["snapshots"]) - 1
                        room1_feedback = []

                        message = f"TASK T{next_id} INJECTED. EDITS LEFT: {max_task_edits - task_edits_used}."

                elif event.key == pygame.K_r:
                    tasks = [dict(task) for task in default_tasks]
                    selected_algorithm = "FCFS"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    wrong_submit_attempts = 0
                    submit_attempts = 0
                    task_edits_used = 0
                    message = "ROOM 1 RESET: Default tasks restored."

        # IMPORTANT: this must be OUTSIDE the event loop.
        if room_state == "finale":
            final_room.update_and_draw(screen, pygame.mouse.get_pos())
            pygame.display.flip()
            clock.tick(60)
            continue

        pygame.mouse.set_visible(True)

        # Matrix background for all gameplay screens
        matrix_rain.update_and_draw(screen)

        # Room 2 Renderer
        if room_state == "room2":
            if room2_replay_index >= 0 and room2_timeline:
                snap = room2_timeline[room2_replay_index]
                disp_states = snap["states"]
                disp_held = snap["held"]
                disp_resources = snap["resources"]
                current_event = snap["event"]
                current_step_num = snap["step"]
            else:
                disp_states = {p: "ready" for p in room2_config["processes"]}
                disp_held = {p: set() for p in room2_config["processes"]}
                disp_resources = {r: None for r in room2_config["resources"]}
                current_event = "No simulation yet."
                current_step_num = 0

            draw_matrix_label(screen, title_font, "ROOM 2: DEADLOCK PREVENTION", (20, 8), MATRIX_GREEN)

            draw_matrix_panel(screen, pygame.Rect(20, 48, 760, 74))
            mission_lines = [
                "MISSION: Prevent deadlock by choosing a safe resource allocation order.",
                "P1 needs R1->R2 | P2 needs R2->R3 | P3 needs R3->R1",
                "Build 6 steps with [1]=P1 [2]=P2 [3]=P3, then ENTER to simulate.",
            ]

            for i, line in enumerate(mission_lines):
                screen.blit(tiny_font.render(line, True, MATRIX_LIGHT_GREEN), (28, 56 + i * 22))

            draw_matrix_panel(screen, pygame.Rect(20, 126, 760, 46))
            seq_text = " -> ".join(room2_sequence) if room2_sequence else "(empty)"

            screen.blit(tiny_font.render("ORDER:", True, MATRIX_DIM_GREEN), (28, 133))
            screen.blit(
                tiny_font.render(f"{seq_text}   [{len(room2_sequence)}/{room2_max_steps}]", True, MATRIX_WHITE),
                (90, 133),
            )

            if room2_status == "unsolved":
                ctrl = "[1][2][3] add  [BACKSPACE] undo  [ENTER] simulate  [R] reset  [ESC] exit"
            else:
                ctrl = "[LEFT]/[RIGHT] replay  [SPACE] final state  [R] reset  [ESC] exit"

            screen.blit(tiny_font.render(ctrl, True, MATRIX_GRAY), (28, 155))

            state_colors = {
                "ready": ((3, 22, 12), MATRIX_CYAN),
                "running": ((0, 70, 25), MATRIX_GREEN),
                "blocked": ((70, 5, 5), MATRIX_RED),
                "terminated": ((10, 10, 10), MATRIX_GRAY),
            }

            for i, pid in enumerate(room2_config["processes"]):
                bx, by = 20, 178 + i * 56
                state = disp_states.get(pid, "ready")
                bg, fg = state_colors[state]

                draw_matrix_panel(screen, pygame.Rect(bx, by, 228, 50), fg, bg, 1)

                held_list = ", ".join(sorted(disp_held.get(pid, set()))) or "none"

                screen.blit(tiny_font.render(f"{pid} [{state.upper()}]", True, fg), (bx + 8, by + 8))
                screen.blit(tiny_font.render(f"holds: {held_list}", True, MATRIX_GRAY), (bx + 8, by + 28))

            for i, rid in enumerate(room2_config["resources"]):
                bx, by = 258, 178 + i * 56
                owner = disp_resources.get(rid)

                if owner:
                    bg, fg = (45, 32, 0), MATRIX_YELLOW
                    owner_text = f"owner: {owner}"
                else:
                    bg, fg = (2, 18, 8), MATRIX_GREEN
                    owner_text = "free"

                draw_matrix_panel(screen, pygame.Rect(bx, by, 180, 50), fg, bg, 1)

                screen.blit(tiny_font.render(rid, True, fg), (bx + 8, by + 8))
                screen.blit(tiny_font.render(owner_text, True, MATRIX_GRAY), (bx + 8, by + 28))

            draw_matrix_panel(screen, pygame.Rect(448, 178, 332, 166), MATRIX_CYAN, MATRIX_DARK_PANEL)

            screen.blit(tiny_font.render("CURRENT STEP", True, MATRIX_CYAN), (458, 186))

            if room2_replay_index >= 0:
                screen.blit(
                    tiny_font.render(f"Step {current_step_num} / {len(room2_timeline)}", True, MATRIX_YELLOW),
                    (458, 208),
                )

                event_color = MATRIX_RED if "DEADLOCK" in current_event else MATRIX_WHITE
                draw_wrapped_text(screen, tiny_font, current_event, 458, 230, 310, event_color, 20, 4)

                screen.blit(
                    tiny_font.render(f"<- {room2_replay_index} / {len(room2_timeline) - 1} ->", True, MATRIX_GRAY),
                    (458, 324),
                )
            else:
                screen.blit(tiny_font.render("Build order and press ENTER.", True, MATRIX_GRAY), (458, 208))

            draw_matrix_panel(screen, pygame.Rect(20, 352, 760, 134), MATRIX_GREEN, MATRIX_DARK_PANEL)
            draw_matrix_label(screen, body_font, "EVENT LOG", (30, 360), MATRIX_GREEN)

            if room2_timeline and room2_replay_index >= 0:
                visible = room2_timeline[:room2_replay_index + 1]

                for j, s in enumerate(visible[-5:]):
                    is_cur = (j == len(visible[-5:]) - 1)
                    color = MATRIX_YELLOW if is_cur else MATRIX_DIM_GREEN
                    prefix = "> " if is_cur else "  "

                    screen.blit(
                        tiny_font.render(f"{prefix}{s['step']}. {s['event']}", True, color),
                        (30, 386 + j * 20),
                    )
            else:
                screen.blit(tiny_font.render("No events yet.", True, MATRIX_GRAY), (30, 386))

            if room2_status == "failed" and room2_chain:
                screen.blit(tiny_font.render("DEADLOCK: circular wait detected —", True, MATRIX_RED), (20, 492))
                chain_text = " | ".join(room2_chain)
                screen.blit(tiny_font.render(chain_text[:98], True, MATRIX_YELLOW), (20, 511))

            status_color = MATRIX_GREEN if room2_status == "solved" else MATRIX_RED if room2_status == "failed" else MATRIX_GRAY

            screen.blit(tiny_font.render(f"STATUS: {room2_status.upper()}", True, status_color), (20, 534))
            screen.blit(tiny_font.render(message, True, MATRIX_WHITE), (20, 556))

            pygame.display.flip()
            clock.tick(60)
            continue

        # Room 1 Failed Renderer
        if room_state == "room1_failed":
            draw_matrix_panel(screen, pygame.Rect(130, 140, 540, 300), MATRIX_RED, MATRIX_DARK_PANEL)

            draw_matrix_label(screen, title_font, "ROOM 1 LOCKED", (250, 190), MATRIX_RED)

            screen.blit(body_font.render("0 TRIES LEFT.", True, MATRIX_WHITE), (260, 250))
            screen.blit(tiny_font.render("Press [R] to reset Room 1 and try again.", True, MATRIX_LIGHT_GREEN), (215, 305))
            screen.blit(tiny_font.render("Press [ESC] to exit.", True, MATRIX_GRAY), (305, 340))
            screen.blit(tiny_font.render(message, True, MATRIX_WHITE), (30, 555))

            pygame.display.flip()
            clock.tick(60)
            continue

        # Room 1 Renderer
        draw_matrix_label(screen, title_font, "ROOM 1: CPU SCHEDULING", (20, 8), MATRIX_GREEN)

        draw_matrix_panel(screen, pygame.Rect(20, 48, 760, 46), MATRIX_GREEN, MATRIX_DARK_PANEL)

        screen.blit(
            tiny_font.render("MISSION: Identify the most efficient scheduling algorithm for these tasks.", True, MATRIX_LIGHT_GREEN),
            (28, 55),
        )

        screen.blit(
            tiny_font.render(
                f"Attempts left: {max_submit_attempts - submit_attempts} | "
                f"Task edits left: {max_task_edits - task_edits_used} | "
                "[1]=FCFS [2]=SJF [3]=RR [A]=add [ENTER]=submit [LEFT/RIGHT]=step [R]=reset",
                True,
                MATRIX_GRAY,
            ),
            (28, 74),
        )

        alg_labels = [("FCFS", "1"), ("SJF", "2"), ("RR", "3")]

        for i, (alg, key) in enumerate(alg_labels):
            bx = 20 + i * 140
            selected = selected_algorithm == alg

            bg = (0, 55, 20) if selected else MATRIX_DARK_PANEL
            border = MATRIX_GREEN if selected else MATRIX_DIM_GREEN
            label_color = MATRIX_LIGHT_GREEN if selected else MATRIX_GRAY

            draw_matrix_panel(screen, pygame.Rect(bx, 100, 130, 30), border, bg, 2)

            screen.blit(tiny_font.render(f"[{key}] {alg}", True, label_color), (bx + 10, 108))

        snap = room1_sim["snapshots"][room1_replay_index]

        task_state_colors = {
            "not-arrived": ((8, 8, 8), (90, 100, 90)),
            "ready": ((3, 22, 12), MATRIX_CYAN),
            "running": ((0, 70, 25), MATRIX_GREEN),
            "terminated": ((10, 10, 10), MATRIX_GRAY),
        }

        for i, task in enumerate(tasks):
            bx, by = 20, 140 + i * 52
            state = snap["states"].get(task["name"], "not-arrived")
            bg, fg = task_state_colors[state]

            draw_matrix_panel(screen, pygame.Rect(bx, by, 230, 46), fg, bg, 1)

            screen.blit(tiny_font.render(f"{task['name']} [{state.upper()}]", True, fg), (bx + 8, by + 6))
            screen.blit(
                tiny_font.render(f"arrival={task['arrival']} burst={task['burst']}", True, MATRIX_GRAY),
                (bx + 8, by + 26),
            )

        table_height = 46 * len(tasks) + 4
        draw_matrix_panel(screen, pygame.Rect(260, 140, 240, table_height), MATRIX_GREEN, MATRIX_DARK_PANEL)

        screen.blit(tiny_font.render("WAIT   TURNAROUND", True, MATRIX_DIM_GREEN), (268, 145))

        for i, task in enumerate(tasks):
            by = 140 + 4 + i * 46 + 20
            w = room1_sim["wait_map"].get(task["name"], 0)
            t = room1_sim["turnaround_map"].get(task["name"], 0)

            screen.blit(tiny_font.render(f"{task['name']}: {w:>3}       {t:>3}", True, MATRIX_WHITE), (268, by))

        draw_matrix_panel(screen, pygame.Rect(510, 140, 270, table_height), MATRIX_CYAN, MATRIX_DARK_PANEL)

        tick_label = f"TICK {snap['tick']} [{room1_replay_index + 1}/{len(room1_sim['snapshots'])}]"
        screen.blit(tiny_font.render(tick_label, True, MATRIX_YELLOW), (518, 148))

        running_name = snap["running"]

        if running_name:
            screen.blit(tiny_font.render(f"CPU: {running_name} RUNNING", True, MATRIX_GREEN), (518, 170))
        else:
            screen.blit(tiny_font.render("CPU: IDLE", True, MATRIX_GRAY), (518, 170))

        screen.blit(tiny_font.render(snap["slice_label"], True, MATRIX_CYAN), (518, 192))

        screen.blit(
            tiny_font.render(
                f"Avg wait: {room1_sim['avg_wait']:.2f}  Avg turn: {room1_sim['avg_turnaround']:.2f}",
                True,
                MATRIX_LIGHT_GREEN,
            ),
            (518, 214),
        )

        screen.blit(tiny_font.render("<- LEFT / RIGHT ->", True, MATRIX_GRAY), (518, 236))

        tl_x, tl_y, tl_h = 20, 312, 30

        bar_colors = {}
        palette = [
            (0, 255, 90),
            (90, 255, 210),
            (255, 230, 90),
            (255, 70, 70),
            (170, 100, 255),
        ]

        for ci, task in enumerate(tasks):
            bar_colors[task["name"]] = palette[ci % len(palette)]

        all_slices = room1_sim["slices_raw"]
        max_tick = all_slices[-1][2] if all_slices else 1
        px_per_tick = min(700 / max(max_tick, 1), 28)

        draw_matrix_panel(screen, pygame.Rect(tl_x, tl_y, 760, tl_h + 18), MATRIX_GREEN, MATRIX_DARK_PANEL, 1)

        current_tick = snap["tick"]

        for sname, t0, t1 in all_slices:
            rx = int(tl_x + t0 * px_per_tick)
            rw = max(int((t1 - t0) * px_per_tick) - 1, 1)
            color = bar_colors.get(sname, MATRIX_GRAY)

            if t1 <= current_tick:
                draw_color = color
            else:
                draw_color = tuple(max(c - 120, 10) for c in color)

            pygame.draw.rect(screen, draw_color, pygame.Rect(rx, tl_y + 2, rw, tl_h - 4), border_radius=3)

            if rw > 20:
                screen.blit(tiny_font.render(sname, True, (0, 0, 0)), (rx + 2, tl_y + 7))

        for t in range(0, max_tick + 1, max(1, max_tick // 10)):
            mx = int(tl_x + t * px_per_tick)
            pygame.draw.line(screen, MATRIX_DIM_GREEN, (mx, tl_y + tl_h - 2), (mx, tl_y + tl_h + 14))
            screen.blit(tiny_font.render(str(t), True, MATRIX_GRAY), (mx, tl_y + tl_h + 2))

        ph_x = int(tl_x + current_tick * px_per_tick)
        pygame.draw.line(screen, MATRIX_YELLOW, (ph_x, tl_y), (ph_x, tl_y + tl_h + 18), 2)

        fb_y = 370
        draw_matrix_panel(screen, pygame.Rect(20, fb_y, 760, 80), MATRIX_GREEN, MATRIX_DARK_PANEL)

        screen.blit(tiny_font.render("ANALYSIS", True, MATRIX_GREEN), (28, fb_y + 5))

        if room1_feedback:
            for j, fb_line in enumerate(room1_feedback[:3]):
                screen.blit(tiny_font.render(fb_line, True, MATRIX_LIGHT_GREEN), (28, fb_y + 24 + j * 20))
        else:
            screen.blit(
                tiny_font.render("Press [ENTER] to submit your algorithm choice and see analysis.", True, MATRIX_GRAY),
                (28, fb_y + 24),
            )

        screen.blit(tiny_font.render(message, True, MATRIX_WHITE), (20, 458))

        pygame.display.flip()
        clock.tick(60)