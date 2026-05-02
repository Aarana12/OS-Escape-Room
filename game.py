import pygame


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
        timeline.append(
            {
                "name": task["name"],
                "start": start_time,
                "finish": finish_time,
                "wait": wait_time,
                "turnaround": turnaround_time,
            }
        )
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

        timeline.append(
            {
                "name": chosen["name"],
                "start": start_time,
                "finish": finish_time,
                "wait": wait_time,
                "turnaround": turnaround_time,
            }
        )

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
        timeline.append(
            {
                "name": task["name"],
                "start": None,
                "finish": finish_time,
                "wait": wait_time,
                "turnaround": turnaround_time,
            }
        )

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

    # Build per-tick snapshots using slice list
    snapshots = []
    tick = 0
    for (running_name, t_start, t_end) in slices_raw:
        for t in range(t_start, t_end):
            states = {}
            for name in all_names:
                if name == running_name:
                    states[name] = "running"
                else:
                    # finished if burst already fully consumed before this tick
                    done = all(
                        (sn == name and st_end <= t)
                        for (sn, st_s, st_end) in slices_raw
                        if sn == name and st_s < t
                    )
                    if done:
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

    # Final tick: all terminated
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
        lines.append(f"{selected_algorithm} is correct — lowest avg wait time.")
    else:
        best_str = " or ".join(best)
        sel_wait = results[selected_algorithm]["avg_wait"]
        best_wait = results[best[0]]["avg_wait"]
        lines.append(f"{selected_algorithm} avg wait = {sel_wait:.1f}  |  {best_str} avg wait = {best_wait:.1f}")
        if selected_algorithm == "FCFS":
            lines.append("FCFS runs tasks in arrival order — longer tasks can block shorter ones (convoy effect).")
        elif selected_algorithm == "RR":
            lines.append("Round Robin splits time fairly but adds overhead — better for fairness than throughput.")
        if "SJF" in best:
            lines.append("SJF picks the shortest remaining burst first, minimising average wait time here.")
    return lines


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
                    f"{pid} waits for {needs[pid][progress[pid]]} held by {resources[needs[pid][progress[pid]]]}"
                    for pid in unfinished
                ]
                snapshot["deadlock"] = True
                snapshot["chain"] = chain
                snapshot["event"] += " -> DEADLOCK!"
                timeline.append(snapshot)
                return {"success": False, "timeline": timeline, "chain": chain}

        timeline.append(snapshot)

    if all(progress[p] >= len(needs[p]) for p in process_ids):
        return {"success": True, "timeline": timeline, "chain": []}

    return {"success": False, "timeline": timeline, "chain": ["Sequence ended before all processes completed."]}


def run_game():
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 46)
    body_font = pygame.font.SysFont(None, 30)
    small_font = pygame.font.SysFont(None, 24)

    room1_config = ROOM1_CONFIG
    tasks = [dict(t) for t in room1_config["tasks"]]
    default_tasks = [dict(t) for t in room1_config["tasks"]]
    selected_algorithm = "FCFS"
    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
    room1_replay_index = len(room1_sim["snapshots"]) - 1
    room1_feedback = []
    message = "Room 1: Pick the best scheduling algorithm to unlock Room 2."
    room_state = "room1"
    wrong_submit_attempts = 0
    submit_attempts = 0
    max_submit_attempts = room1_config["max_submit_attempts"]
    task_edits_used = 0
    max_task_edits = room1_config["max_task_edits"]
    room2_config = ROOM2_CONFIG
    room2_sequence = []
    room2_max_steps = room2_config["max_steps"]
    room2_status = "not-started"
    room2_timeline = []
    room2_replay_index = -1
    room2_chain = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if room_state == "room2":
                    if event.key == pygame.K_r:
                        room2_sequence = []
                        room2_status = "not-started"
                        room2_timeline = []
                        room2_replay_index = -1
                        room2_chain = []
                        message = "Room 2 reset."
                    elif room2_status != "not-started":
                        if event.key == pygame.K_LEFT:
                            room2_replay_index = max(0, room2_replay_index - 1)
                            message = f"Step {room2_replay_index + 1} / {len(room2_timeline)}."
                        elif event.key == pygame.K_RIGHT:
                            room2_replay_index = min(len(room2_timeline) - 1, room2_replay_index + 1)
                            message = f"Step {room2_replay_index + 1} / {len(room2_timeline)}."
                        elif event.key == pygame.K_SPACE:
                            room2_replay_index = len(room2_timeline) - 1
                            message = "Jumped to final step."
                    else:
                        if event.key == pygame.K_BACKSPACE:
                            if room2_sequence:
                                room2_sequence.pop()
                                message = "Removed last step from allocation order."
                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            if len(room2_sequence) < room2_max_steps:
                                key_to_process = {
                                    pygame.K_1: "P1",
                                    pygame.K_2: "P2",
                                    pygame.K_3: "P3",
                                }
                                room2_sequence.append(key_to_process[event.key])
                                message = (
                                    f"Added {key_to_process[event.key]}. "
                                    f"Steps: {len(room2_sequence)}/{room2_max_steps}."
                                )
                            else:
                                message = "Order is full. Press Enter to simulate or Backspace to edit."
                        elif event.key == pygame.K_RETURN:
                            if len(room2_sequence) < room2_max_steps:
                                message = f"Add {room2_max_steps - len(room2_sequence)} more steps before submit."
                            else:
                                simulation = _simulate_deadlock_resolution(room2_sequence, room2_config)
                                room2_timeline = simulation["timeline"]
                                room2_chain = simulation.get("chain", [])
                                room2_replay_index = len(room2_timeline) - 1
                                if simulation["success"]:
                                    room2_status = "solved"
                                    message = "Deadlock prevented! Room 2 cleared!"
                                else:
                                    room2_status = "failed"
                                    message = "Deadlock occurred. Press R to reset and try a safer order."
                    continue

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
                        message = "Room 1 reset. Try a new strategy."
                    continue

                if event.key == pygame.K_LEFT:
                    room1_replay_index = max(0, room1_replay_index - 1)
                    message = f"Tick {room1_sim['snapshots'][room1_replay_index]['tick']}."
                elif event.key == pygame.K_RIGHT:
                    room1_replay_index = min(len(room1_sim["snapshots"]) - 1, room1_replay_index + 1)
                    message = f"Tick {room1_sim['snapshots'][room1_replay_index]['tick']}."
                elif event.key == pygame.K_SPACE:
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    message = "Jumped to final tick."
                elif event.key == pygame.K_RETURN:
                    submit_attempts += 1
                    best_algorithms = _best_algorithms_for_tasks(tasks)
                    room1_feedback = _educational_feedback_room1(tasks, selected_algorithm)
                    if selected_algorithm in best_algorithms:
                        room_state = "room2"
                        wrong_submit_attempts = 0
                        room2_sequence = []
                        room2_status = "not-started"
                        room2_timeline = []
                        room2_replay_index = -1
                        room2_chain = []
                        message = "Access granted. Room 2 unlocked!"
                    else:
                        wrong_submit_attempts += 1
                        if submit_attempts >= max_submit_attempts:
                            room_state = "room1_failed"
                            message = "All attempts used. Terminal locked. Press R to reset."
                        else:
                            message = f"Incorrect. {max_submit_attempts - submit_attempts} attempt(s) left."
                elif event.key == pygame.K_1:
                    selected_algorithm = "FCFS"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    message = "Algorithm set to FCFS."
                elif event.key == pygame.K_2:
                    selected_algorithm = "SJF"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    message = "Algorithm set to SJF."
                elif event.key == pygame.K_3:
                    selected_algorithm = "RR"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    message = "Algorithm set to Round Robin (q=2)."
                elif event.key == pygame.K_a:
                    if task_edits_used >= max_task_edits:
                        message = "No task edits left. Submit or press R to reset."
                    else:
                        next_id = len(tasks) + 1
                        burst = 2 + (next_id % 4)
                        arrival = max(0, next_id - 2)
                        tasks.append({"name": f"T{next_id}", "arrival": arrival, "burst": burst})
                        task_edits_used += 1
                        room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                        room1_replay_index = len(room1_sim["snapshots"]) - 1
                        room1_feedback = []
                        message = f"Added T{next_id}. Edits left: {max_task_edits - task_edits_used}."
                elif event.key == pygame.K_r:
                    tasks = [dict(task) for task in default_tasks]
                    selected_algorithm = "FCFS"
                    room1_sim = _build_scheduler_timeline(tasks, selected_algorithm, room1_config["quantum"])
                    room1_replay_index = len(room1_sim["snapshots"]) - 1
                    room1_feedback = []
                    wrong_submit_attempts = 0
                    submit_attempts = 0
                    task_edits_used = 0
                    message = "Tasks reset to default."

        screen.fill((0, 0, 0))

        if room_state == "room2":
            # --- resolve display snapshot ---
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

            # Title
            screen.blit(title_font.render("Room 2: Deadlock Prevention", True, (255, 255, 255)), (20, 8))

            # Mission panel (3 lines)
            pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(20, 48, 760, 74), 2)
            mission_lines = [
                "Mission: Prevent deadlock by choosing a safe resource allocation order.",
                "P1 needs R1->R2 | P2 needs R2->R3 | P3 needs R3->R1   (press a key twice to finish a process)",
                "Build 6 steps with [1]=P1 [2]=P2 [3]=P3 then ENTER. After simulating use LEFT/RIGHT to replay.",
            ]
            for i, line in enumerate(mission_lines):
                screen.blit(small_font.render(line, True, (210, 210, 210)), (28, 56 + i * 22))

            # Allocation order & controls
            pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(20, 126, 760, 46), 2)
            seq_text = " -> ".join(room2_sequence) if room2_sequence else "(empty)"
            screen.blit(small_font.render("Order:", True, (180, 180, 180)), (28, 133))
            screen.blit(small_font.render(
                f"{seq_text}   [{len(room2_sequence)}/{room2_max_steps}]", True, (220, 220, 220)), (80, 133))
            if room2_status == "not-started":
                ctrl = "[1][2][3] add  [BACKSPACE] undo  [ENTER] simulate  [R] reset  [ESC] exit"
            else:
                ctrl = "[LEFT]/[RIGHT] step replay  [SPACE] jump to end  [R] reset  [ESC] exit"
            screen.blit(small_font.render(ctrl, True, (160, 160, 160)), (28, 155))

            # State color map: bg, fg
            state_colors = {
                "ready":      ((40, 40, 90),   (140, 140, 255)),
                "running":    ((20, 80, 20),   (100, 255, 100)),
                "blocked":    ((100, 20, 20),  (255, 100, 100)),
                "terminated": ((25, 25, 25),   (110, 110, 110)),
            }

            # Thread state boxes (left column x=20, w=228)
            for i, pid in enumerate(room2_config["processes"]):
                bx, by = 20, 178 + i * 56
                state = disp_states.get(pid, "ready")
                bg, fg = state_colors[state]
                pygame.draw.rect(screen, bg, pygame.Rect(bx, by, 228, 50))
                pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(bx, by, 228, 50), 1)
                held_list = ", ".join(sorted(disp_held.get(pid, set()))) or "none"
                screen.blit(small_font.render(f"{pid}  [{state.upper()}]", True, fg), (bx + 8, by + 8))
                screen.blit(small_font.render(f"holds: {held_list}", True, (170, 170, 170)), (bx + 8, by + 28))

            # Resource ownership boxes (middle column x=258, w=180)
            for i, rid in enumerate(room2_config["resources"]):
                bx, by = 258, 178 + i * 56
                owner = disp_resources.get(rid)
                if owner:
                    bg, fg = (55, 40, 10), (255, 200, 80)
                    owner_text = f"owner: {owner}"
                else:
                    bg, fg = (20, 20, 20), (100, 200, 100)
                    owner_text = "free"
                pygame.draw.rect(screen, bg, pygame.Rect(bx, by, 180, 50))
                pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(bx, by, 180, 50), 1)
                screen.blit(small_font.render(rid, True, fg), (bx + 8, by + 8))
                screen.blit(small_font.render(owner_text, True, (170, 170, 170)), (bx + 8, by + 28))

            # Current step panel (right column x=448, w=332)
            pygame.draw.rect(screen, (20, 20, 40), pygame.Rect(448, 178, 332, 166))
            pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(448, 178, 332, 166), 1)
            screen.blit(small_font.render("Current Step", True, (180, 180, 180)), (458, 186))
            if room2_replay_index >= 0:
                screen.blit(small_font.render(
                    f"Step {current_step_num} / {len(room2_timeline)}", True, (220, 220, 180)), (458, 208))
                words = current_event.split()
                lines, cur_line = [], ""
                for word in words:
                    test = (cur_line + " " + word).strip()
                    if small_font.size(test)[0] < 312:
                        cur_line = test
                    else:
                        lines.append(cur_line)
                        cur_line = word
                if cur_line:
                    lines.append(cur_line)
                for j, ln in enumerate(lines[:4]):
                    c = (255, 100, 100) if "DEADLOCK" in ln else (220, 220, 220)
                    screen.blit(small_font.render(ln, True, c), (458, 230 + j * 22))
                screen.blit(small_font.render(
                    f"<- {room2_replay_index} / {len(room2_timeline) - 1} ->",
                    True, (130, 130, 130)), (458, 324))
            else:
                screen.blit(small_font.render("Build order and press ENTER.", True, (140, 140, 140)), (458, 208))

            # Event log panel
            pygame.draw.rect(screen, (12, 12, 28), pygame.Rect(20, 352, 760, 134))
            pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(20, 352, 760, 134), 1)
            screen.blit(body_font.render("Event Log", True, (255, 255, 255)), (30, 360))
            if room2_timeline and room2_replay_index >= 0:
                visible = room2_timeline[:room2_replay_index + 1]
                for j, s in enumerate(visible[-5:]):
                    is_cur = (j == len(visible[-5:]) - 1)
                    color = (255, 255, 100) if is_cur else (170, 170, 170)
                    prefix = "> " if is_cur else "  "
                    screen.blit(small_font.render(f"{prefix}{s['step']}. {s['event']}", True, color), (30, 386 + j * 20))
            else:
                screen.blit(small_font.render("No events yet.", True, (100, 100, 100)), (30, 386))

            # Educational deadlock feedback
            if room2_status == "failed" and room2_chain:
                screen.blit(small_font.render("Deadlock: circular wait —", True, (255, 120, 60)), (20, 492))
                chain_text = " | ".join(room2_chain)
                screen.blit(small_font.render(chain_text[:98], True, (255, 170, 120)), (20, 511))

            # Status & message
            status_color = (100, 255, 100) if room2_status == "solved" else (255, 100, 100) if room2_status == "failed" else (180, 180, 180)
            screen.blit(small_font.render(f"Status: {room2_status}", True, status_color), (20, 534))
            screen.blit(small_font.render(message, True, (200, 200, 200)), (20, 556))

            pygame.display.flip()
            clock.tick(60)
            continue


        if room_state == "room1_failed":
            pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(130, 140, 540, 300), 2)
            title = title_font.render("Room 1 Locked", True, (255, 255, 255))
            line1 = body_font.render("0 tries left.", True, (220, 220, 220))
            line2 = small_font.render("Press [R] to reset Room 1 and try again.", True, (220, 220, 220))
            line3 = small_font.render("Press [ESC] to exit.", True, (220, 220, 220))
            screen.blit(title, (280, 190))
            screen.blit(line1, (240, 250))
            screen.blit(line2, (230, 305))
            screen.blit(line3, (320, 340))

            message_surface = small_font.render(message, True, (220, 220, 220))
            screen.blit(message_surface, (30, 555))

            pygame.display.flip()
            clock.tick(60)
            continue

        # ── Room 1 Renderer ─────────────────────────────────────────────────
        screen.blit(title_font.render("Room 1: CPU Scheduling", True, (255, 255, 255)), (20, 8))

        # Mission / info bar
        pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(20, 48, 760, 46), 2)
        screen.blit(small_font.render(
            "Mission: Identify the most efficient scheduling algorithm for these tasks.",
            True, (210, 210, 210)), (28, 55))
        screen.blit(small_font.render(
            f"Attempts left: {max_submit_attempts - submit_attempts}  |  Task edits left: {max_task_edits - task_edits_used}  |  "
            f"[1]=FCFS  [2]=SJF  [3]=RR  [A]=add task  [ENTER]=submit  [LEFT/RIGHT]=step  [R]=reset  [ESC]=exit",
            True, (160, 160, 160)), (28, 74))

        # Algorithm selector buttons
        alg_labels = [("FCFS", "1"), ("SJF", "2"), ("RR", "3")]
        for i, (alg, key) in enumerate(alg_labels):
            bx = 20 + i * 140
            selected = selected_algorithm == alg
            bg = (60, 100, 60) if selected else (20, 20, 20)
            border = (100, 220, 100) if selected else (100, 100, 100)
            pygame.draw.rect(screen, bg, pygame.Rect(bx, 100, 130, 30))
            pygame.draw.rect(screen, border, pygame.Rect(bx, 100, 130, 30), 2)
            label_color = (180, 255, 180) if selected else (160, 160, 160)
            screen.blit(small_font.render(f"[{key}] {alg}", True, label_color), (bx + 10, 108))

        # ── Task state boxes (left, y=140, w=230) ───────────────────────────
        snap = room1_sim["snapshots"][room1_replay_index]
        task_state_colors = {
            "not-arrived": ((15, 15, 15),   (80, 80, 80)),
            "ready":        ((40, 40, 90),   (140, 140, 255)),
            "running":      ((20, 80, 20),   (100, 255, 100)),
            "terminated":   ((25, 25, 25),   (110, 110, 110)),
        }
        for i, task in enumerate(tasks):
            bx, by = 20, 140 + i * 52
            state = snap["states"].get(task["name"], "not-arrived")
            bg, fg = task_state_colors[state]
            pygame.draw.rect(screen, bg, pygame.Rect(bx, by, 230, 46))
            pygame.draw.rect(screen, (180, 180, 180), pygame.Rect(bx, by, 230, 46), 1)
            screen.blit(small_font.render(f"{task['name']}  [{state.upper()}]", True, fg), (bx + 8, by + 6))
            screen.blit(small_font.render(
                f"arrival={task['arrival']}  burst={task['burst']}", True, (150, 150, 150)), (bx + 8, by + 26))

        # ── Per-task wait/turnaround table (middle, x=260) ──────────────────
        pygame.draw.rect(screen, (15, 15, 30), pygame.Rect(260, 140, 240, 46 * len(tasks) + 4))
        pygame.draw.rect(screen, (180, 180, 180), pygame.Rect(260, 140, 240, 46 * len(tasks) + 4), 1)
        screen.blit(small_font.render("wait  turnaround", True, (130, 130, 130)), (268, 140))
        for i, task in enumerate(tasks):
            by = 140 + 4 + i * 46 + 20
            w = room1_sim["wait_map"].get(task["name"], 0)
            t = room1_sim["turnaround_map"].get(task["name"], 0)
            screen.blit(small_font.render(f"{task['name']}: {w:>3}    {t:>3}", True, (200, 200, 200)), (268, by))

        # ── Current tick step panel (right, x=510) ──────────────────────────
        pygame.draw.rect(screen, (20, 20, 40), pygame.Rect(510, 140, 270, 46 * len(tasks) + 4))
        pygame.draw.rect(screen, (180, 180, 180), pygame.Rect(510, 140, 270, 46 * len(tasks) + 4), 1)
        tick_label = f"Tick {snap['tick']}  [{room1_replay_index + 1}/{len(room1_sim['snapshots'])}]"
        screen.blit(small_font.render(tick_label, True, (200, 200, 180)), (518, 148))
        running_name = snap["running"]
        if running_name:
            screen.blit(small_font.render(f"CPU: {running_name} running", True, (100, 255, 100)), (518, 170))
        else:
            screen.blit(small_font.render("CPU: idle", True, (130, 130, 130)), (518, 170))
        screen.blit(small_font.render(snap["slice_label"], True, (180, 180, 100)), (518, 192))
        screen.blit(small_font.render(
            f"Avg wait: ?  Avg turn: {room1_sim['avg_turnaround']:.2f}",
            True, (180, 220, 180)), (518, 214))
        screen.blit(small_font.render("<- LEFT / RIGHT ->", True, (100, 100, 100)), (518, 236))

        # ── CPU Execution Timeline bar ───────────────────────────────────────
        tl_x, tl_y, tl_h = 20, 312, 30
        bar_colors = {}
        palette = [(100, 180, 255), (100, 255, 160), (255, 200, 80), (255, 120, 120), (200, 120, 255)]
        for ci, task in enumerate(tasks):
            bar_colors[task["name"]] = palette[ci % len(palette)]
        all_slices = room1_sim["slices_raw"]
        max_tick = all_slices[-1][2] if all_slices else 1
        px_per_tick = min(700 / max(max_tick, 1), 28)
        pygame.draw.rect(screen, (15, 15, 15), pygame.Rect(tl_x, tl_y, 760, tl_h + 18))
        pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(tl_x, tl_y, 760, tl_h + 18), 1)
        current_tick = snap["tick"]
        for (sname, t0, t1) in all_slices:
            rx = int(tl_x + t0 * px_per_tick)
            rw = max(int((t1 - t0) * px_per_tick) - 1, 1)
            color = bar_colors.get(sname, (150, 150, 150))
            # dim slices not yet reached
            if t1 <= current_tick:
                draw_color = color
            else:
                draw_color = tuple(max(c - 120, 10) for c in color)
            pygame.draw.rect(screen, draw_color, pygame.Rect(rx, tl_y + 2, rw, tl_h - 4))
            if rw > 20:
                screen.blit(small_font.render(sname, True, (0, 0, 0)), (rx + 2, tl_y + 8))
        # tick markers
        for t in range(0, max_tick + 1, max(1, max_tick // 10)):
            mx = int(tl_x + t * px_per_tick)
            pygame.draw.line(screen, (80, 80, 80), (mx, tl_y + tl_h - 2), (mx, tl_y + tl_h + 14))
            screen.blit(small_font.render(str(t), True, (100, 100, 100)), (mx, tl_y + tl_h + 2))
        # playhead
        ph_x = int(tl_x + current_tick * px_per_tick)
        pygame.draw.line(screen, (255, 255, 0), (ph_x, tl_y), (ph_x, tl_y + tl_h + 18))

        # ── Educational feedback panel ───────────────────────────────────────
        fb_y = 370
        pygame.draw.rect(screen, (15, 10, 25), pygame.Rect(20, fb_y, 760, 80))
        pygame.draw.rect(screen, (100, 80, 140), pygame.Rect(20, fb_y, 760, 80), 1)
        screen.blit(small_font.render("Analysis", True, (160, 130, 200)), (28, fb_y + 5))
        if room1_feedback:
            for j, fb_line in enumerate(room1_feedback[:3]):
                screen.blit(small_font.render(fb_line, True, (210, 190, 255)), (28, fb_y + 24 + j * 20))
        else:
            screen.blit(small_font.render(
                "Press [ENTER] to submit your algorithm choice and see analysis.", True, (100, 100, 120)), (28, fb_y + 24))

        # ── Status / message ─────────────────────────────────────────────────
        screen.blit(small_font.render(message, True, (200, 200, 200)), (20, 458))

        pygame.display.flip()
        clock.tick(60)

