import pygame


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


def run_game():
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 46)
    body_font = pygame.font.SysFont(None, 30)
    small_font = pygame.font.SysFont(None, 24)

    tasks = [
        {"name": "T1", "arrival": 0, "burst": 5},
        {"name": "T2", "arrival": 1, "burst": 3},
        {"name": "T3", "arrival": 2, "burst": 2},
    ]
    default_tasks = [
        {"name": "T1", "arrival": 0, "burst": 5},
        {"name": "T2", "arrival": 1, "burst": 3},
        {"name": "T3", "arrival": 2, "burst": 2},
    ]
    selected_algorithm = "FCFS"
    result = _build_result(tasks, selected_algorithm)
    message = "Room 1: Solve the scheduler puzzle to unlock Room 2."
    room_state = "room1"
    wrong_submit_attempts = 0
    submit_attempts = 0
    max_submit_attempts = 3
    task_edits_used = 0
    max_task_edits = 3

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
                        tasks = [dict(task) for task in default_tasks]
                        selected_algorithm = "FCFS"
                        result = _build_result(tasks, selected_algorithm)
                        room_state = "room1"
                        wrong_submit_attempts = 0
                        submit_attempts = 0
                        task_edits_used = 0
                        message = "Room 1 restarted. Solve the puzzle to unlock Room 2."
                    continue

                if room_state == "room1_failed":
                    if event.key == pygame.K_r:
                        tasks = [dict(task) for task in default_tasks]
                        selected_algorithm = "FCFS"
                        result = _build_result(tasks, selected_algorithm)
                        room_state = "room1"
                        wrong_submit_attempts = 0
                        submit_attempts = 0
                        task_edits_used = 0
                        message = "Room 1 reset. Try a new strategy."
                    continue

                if event.key == pygame.K_RETURN:
                    submit_attempts += 1
                    best_algorithms = _best_algorithms_for_tasks(tasks)
                    if selected_algorithm in best_algorithms:
                        room_state = "room2"
                        wrong_submit_attempts = 0
                        message = "Access granted. Room 2 unlocked!"
                    else:
                        wrong_submit_attempts += 1
                        if submit_attempts >= max_submit_attempts:
                            room_state = "room1_failed"
                            message = "All attempts used. Terminal locked. Press R to reset Room 1."
                        elif wrong_submit_attempts == 1:
                            message = "Incorrect. Try once more with a different algorithm."
                        else:
                            message = "Hint: Compare the scheduler results and choose the most efficient option."
                    continue

                if event.key == pygame.K_1:
                    selected_algorithm = "FCFS"
                    result = _build_result(tasks, selected_algorithm)
                    message = "Algorithm set to FCFS."
                elif event.key == pygame.K_2:
                    selected_algorithm = "SJF"
                    result = _build_result(tasks, selected_algorithm)
                    message = "Algorithm set to SJF."
                elif event.key == pygame.K_3:
                    selected_algorithm = "RR"
                    result = _build_result(tasks, selected_algorithm)
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
                        result = _build_result(tasks, selected_algorithm)
                        message = f"Assigned task T{next_id}. Task edits left: {max_task_edits - task_edits_used}."
                elif event.key == pygame.K_r:
                    tasks = [dict(task) for task in default_tasks]
                    result = _build_result(tasks, selected_algorithm)
                    wrong_submit_attempts = 0
                    submit_attempts = 0
                    task_edits_used = 0
                    room_state = "room1"
                    message = "Tasks reset to default room setup."

        screen.fill((0, 0, 0))

        if room_state == "room2":
            pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(150, 150, 500, 260), 2)
            title = title_font.render("Room 2 Unlocked!", True, (255, 255, 255))
            subtitle = body_font.render("You beat Room 1!", True, (235, 235, 235))
            line1 = small_font.render("Room 2 MVP placeholder.", True, (200, 200, 200))
            line2 = small_font.render("Press [Enter] to continue,[R] to replay Room 1, or [ESC] to exit.", True, (200, 200, 200))

            screen.blit(title, (250, 180))
            screen.blit(subtitle, (250, 230))
            screen.blit(line1, (180, 300))
            screen.blit(line2, (180, 335))

            message_surface = small_font.render(message, True, (220, 220, 220))
            screen.blit(message_surface, (30, 555))

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

        title = title_font.render("Room 1: Scheduling", True, (255, 255, 255))
        screen.blit(title, (30, 20))

        mission_panel = pygame.Rect(20, 70, 760, 80)
        pygame.draw.rect(screen, (220, 220, 220), mission_panel, 2)
        mission_lines = [
            "Mission: Choose the best algorithm for these tasks.",
            f"Submissions left: {max_submit_attempts - submit_attempts} | Task edits left: {max_task_edits - task_edits_used}",
        ]
        for index, line in enumerate(mission_lines):
            line_surface = small_font.render(line, True, (210, 210, 210))
            screen.blit(line_surface, (30, 82 + index * 28))

        algorithm_panel = pygame.Rect(20, 160, 760, 40)
        pygame.draw.rect(screen, (220, 220, 220), algorithm_panel, 2)
        algorithm_order = ["FCFS", "SJF", "RR"]
        for index, algorithm_name in enumerate(algorithm_order):
            button_x = 180 + index * 150
            button_rect = pygame.Rect(button_x, 166, 120, 28)
            if selected_algorithm == algorithm_name:
                pygame.draw.rect(screen, (255, 255, 255), button_rect, 0)
                button_text = small_font.render(algorithm_name, True, (0, 0, 0))
            else:
                pygame.draw.rect(screen, (220, 220, 220), button_rect, 1)
                button_text = small_font.render(algorithm_name, True, (220, 220, 220))
            screen.blit(button_text, (button_rect.x + 35, button_rect.y + 4))

        instructions = [
            "Controls: [1][2][3] choose algorithm | [A] add task | [ENTER] submit | [R] reset | [ESC] exit",
            f"Current selection: {selected_algorithm}",
        ]

        for index, line in enumerate(instructions):
            line_surface = small_font.render(line, True, (200, 200, 200))
            screen.blit(line_surface, (30, 205 + index * 24))

        tasks_panel = pygame.Rect(20, 255, 360, 280)
        pygame.draw.rect(screen, (220, 220, 220), tasks_panel, 2)
        tasks_title = body_font.render("Assigned Tasks", True, (255, 255, 255))
        screen.blit(tasks_title, (30, 265))

        for index, task in enumerate(tasks):
            task_line = f"{task['name']}: arrival={task['arrival']}, burst={task['burst']}"
            task_surface = small_font.render(task_line, True, (220, 220, 220))
            screen.blit(task_surface, (35, 300 + index * 24))

        result_panel = pygame.Rect(400, 255, 380, 280)
        pygame.draw.rect(screen, (220, 220, 220), result_panel, 2)
        result_title = body_font.render("Scheduler Result", True, (255, 255, 255))
        screen.blit(result_title, (410, 265))

        for index, row in enumerate(result["timeline"][:8]):
            row_line = (
                f"{row['name']}: finish={row['finish']} | wait={row['wait']} | turn={row['turnaround']}"
            )
            row_surface = small_font.render(row_line, True, (220, 220, 220))
            screen.blit(row_surface, (410, 300 + index * 24))

        avg_line = f"Avg turnaround: {result['avg_turnaround']:.2f}"
        avg_surface = small_font.render(avg_line, True, (220, 220, 220))
        screen.blit(avg_surface, (410, 492))

        if result["slices"]:
            slices_text = "RR timeline: " + " -> ".join(result["slices"][:4])
            if len(result["slices"]) > 4:
                slices_text += " ..."
            slices_surface = small_font.render(slices_text, True, (220, 220, 220))
            screen.blit(slices_surface, (30, 540))

        message_surface = small_font.render(message, True, (220, 220, 220))
        screen.blit(message_surface, (30, 565))

        pygame.display.flip()
        clock.tick(60)

