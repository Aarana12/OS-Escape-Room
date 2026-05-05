import pygame
import random
import textwrap

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Dana/Team OS Escape Room: 9-room state-based game.
# Controls: mouse click to explore, type answers in puzzle mode, ENTER submit, ESC quit.

ROOMS = [
    {
        "title": "Room 1: CPU Scheduling Lab",
        "topic": "CPU Scheduling",
        "theme": "A dusty scheduler office with blinking ready queues and a tired CPU throne.",
        "concept": "CPU scheduling decides which ready process gets the CPU next.",
        "palette": ((12, 9, 24), (58, 35, 95), (255, 210, 85)),
        "question": "Which non-preemptive scheduling algorithm chooses the process with the smallest CPU burst next?",
        "answers": ["sjf", "shortest job first"],
        "hint1": "The clock is grumpy. It hates long jobs blocking tiny jobs. Look where the shortest task would hide.",
        "hint2": "Correct! Hint #2: the next clue is near the READY QUEUE. Short jobs love cutting politely in line.",
        "hint3": "Riddle: I schedule who goes IN, then kick them OUT when their burst is done. I/O? More like I/Owe you a key. Check the CPU throne.",
        "objects": {
            "hint1": (80, 390, 130, 80, "Wall Clock"),
            "puzzle": (520, 190, 170, 100, "Burst Chart"),
            "hint3": (305, 330, 190, 85, "Ready Queue"),
            "key": (335, 175, 125, 95, "CPU Throne"),
            "decoy": (90, 150, 140, 100, "Old Printer"),
        },
    },
    {
        "title": "Room 2: OS Services Desk",
        "topic": "Services",
        "theme": "A service counter where the OS clerk stamps I/O, files, execution, and errors.",
        "concept": "Operating systems provide services like program execution, I/O operations, file-system manipulation, communication, and error detection.",
        "palette": ((4, 20, 26), (13, 70, 84), (0, 255, 180)),
        "question": "What OS service lets a running program read/write a file or device?",
        "answers": ["i/o", "io", "i/o operations", "io operations", "input output", "input/output"],
        "hint1": "The clerk says: requests go in, results go out. Check the ticket machine first.",
        "hint2": "Correct! Hint #2: find the device that literally takes input and output. It is feeling keyboard-smashy.",
        "hint3": "Riddle: I go IN and OUT all day, but I'm not your weird uncle at Longhorn. The key is where the keys already live.",
        "objects": {
            "hint1": (90, 170, 150, 90, "Ticket Machine"),
            "puzzle": (505, 160, 190, 100, "Service Forms"),
            "hint3": (270, 390, 190, 80, "I/O Terminal"),
            "key": (515, 390, 155, 80, "Keyboard"),
            "decoy": (90, 395, 120, 75, "Trash Bin"),
        },
    },
    {
        "title": "Room 3: OS Structures Tower",
        "topic": "Structures",
        "theme": "A tower of kernel layers, modules, and tiny microkernel message tubes.",
        "concept": "OS structure can be simple, layered, microkernel-based, or modular.",
        "palette": ((20, 14, 18), (86, 52, 52), (255, 115, 115)),
        "question": "Which OS structure moves as much as possible from the kernel into user space and uses message passing?",
        "answers": ["microkernel", "micro kernel"],
        "hint1": "The tower is stacked in layers, but the smallest kernel is hiding in a tiny mailbox.",
        "hint2": "Correct! Hint #2: message passing is the gossip pipeline of this room. Follow the message tubes.",
        "hint3": "Riddle: I keep the kernel tiny, because drama belongs in user space. Your key passed a note through the mailbox.",
        "objects": {
            "hint1": (95, 345, 145, 105, "Layer Stack"),
            "puzzle": (525, 130, 150, 130, "Kernel Diagram"),
            "hint3": (310, 260, 175, 95, "Message Tubes"),
            "key": (530, 385, 140, 80, "Mailbox"),
            "decoy": (90, 135, 120, 75, "DOS Box"),
        },
    },
    {
        "title": "Room 4: Process Morgue",
        "topic": "Processes",
        "theme": "Processes are born, run, wait, and terminate under flickering green lamps.",
        "concept": "A process is a program in execution; it moves through states such as new, ready, running, waiting, and terminated.",
        "palette": ((8, 16, 10), (31, 82, 42), (125, 255, 130)),
        "question": "What do we call a program while it is actively executing?",
        "answers": ["process", "a process"],
        "hint1": "The birth certificate says NEW, but the toe tag says TERMINATED. Start at the process table.",
        "hint2": "Correct! Hint #2: the next clue is at the WAITING bench. Something is blocked and being dramatic.",
        "hint3": "Riddle: I was new, then ready, then running; now I'm waiting for attention like a group project reply. Check the exit status drawer.",
        "objects": {
            "hint1": (90, 150, 175, 95, "Process Table"),
            "puzzle": (505, 165, 185, 100, "State Machine"),
            "hint3": (300, 395, 185, 80, "Waiting Bench"),
            "key": (525, 390, 150, 80, "Exit Status"),
            "decoy": (95, 395, 145, 75, "Zombie File"),
        },
    },
    {
        "title": "Room 5: Thread Weaving Room",
        "topic": "Threads",
        "theme": "A neon loom spins multiple threads through one shared process blanket.",
        "concept": "Threads are lightweight execution units that can share a process's code, data, and resources.",
        "palette": ((18, 8, 28), (70, 27, 105), (220, 130, 255)),
        "question": "Threads in the same process share the same address space: true or false?",
        "answers": ["true", "t", "yes", "y"],
        "hint1": "Many threads, one messy closet. The clue is tangled in the loom.",
        "hint2": "Correct! Hint #2: sharing is caring until everyone writes at once. Check shared memory.",
        "hint3": "Riddle: We run separate paths but raid the same fridge. The key is caught in the yarn spool.",
        "objects": {
            "hint1": (95, 330, 170, 100, "Thread Loom"),
            "puzzle": (520, 155, 170, 105, "Thread Cards"),
            "hint3": (300, 180, 185, 90, "Shared Memory"),
            "key": (525, 385, 145, 85, "Yarn Spool"),
            "decoy": (85, 140, 135, 75, "Single Sock"),
        },
    },
    {
        "title": "Room 6: Synchronization Vault",
        "topic": "Synchronization",
        "theme": "A vault where race conditions sprint, mutexes guard doors, and semaphores count snacks.",
        "concept": "Synchronization prevents race conditions by controlling access to critical sections using tools like mutex locks and semaphores.",
        "palette": ((24, 12, 4), (92, 55, 16), (255, 170, 60)),
        "question": "What is the section of code where shared data is accessed and must be protected?",
        "answers": ["critical section", "critical-section", "critical"],
        "hint1": "Two gremlins changed counter at the same time. The first clue is near the racing scoreboard.",
        "hint2": "Correct! Hint #2: only one at a time may pass. Go bother the mutex guard.",
        "hint3": "Riddle: I lock the door before chaos gets in. If you release me nicely, I'll release the key. Check the vault lock.",
        "objects": {
            "hint1": (95, 145, 175, 95, "Race Board"),
            "puzzle": (515, 155, 175, 105, "Counter Code"),
            "hint3": (300, 390, 185, 80, "Mutex Guard"),
            "key": (535, 385, 135, 85, "Vault Lock"),
            "decoy": (95, 390, 140, 80, "Snack Semaphore"),
        },
    },
    {
        "title": "Room 7: Deadlock Dining Room",
        "topic": "Deadlocks",
        "theme": "Processes sit at a cursed dinner table, each holding one fork and waiting forever.",
        "concept": "Deadlock can occur when mutual exclusion, hold and wait, no preemption, and circular wait all hold at the same time.",
        "palette": ((22, 4, 8), (80, 18, 28), (255, 90, 120)),
        "question": "Which deadlock condition means each process is waiting in a closed loop for another process's resource?",
        "answers": ["circular wait", "circular-wait"],
        "hint1": "Everyone at dinner is holding something and side-eyeing someone else. Check the circular table.",
        "hint2": "Correct! Hint #2: break the loop. The next clue is where the resource graph bends back on itself.",
        "hint3": "Riddle: I can't leave because you can't leave because they can't leave. Very group chat. The key is under the last fork.",
        "objects": {
            "hint1": (105, 350, 170, 100, "Circular Table"),
            "puzzle": (510, 145, 185, 105, "Deadlock Rules"),
            "hint3": (300, 165, 190, 95, "Resource Graph"),
            "key": (535, 390, 130, 80, "Last Fork"),
            "decoy": (95, 140, 130, 75, "Cold Soup"),
        },
    },
    {
        "title": "Room 8: Main Memory Maze",
        "topic": "Main Memory",
        "theme": "A maze of frames, holes, base registers, limits, and suspiciously tiny fragments.",
        "concept": "Main memory management uses techniques such as contiguous allocation, paging, segmentation, relocation, and protection.",
        "palette": ((5, 11, 24), (25, 55, 105), (105, 190, 255)),
        "question": "In paging, physical memory is divided into fixed-size blocks called what?",
        "answers": ["frames", "frame"],
        "hint1": "The memory hole is too small to be useful and is now emotionally fragmented. Look near the tiny holes.",
        "hint2": "Correct! Hint #2: pages need frames. Go to the page table before it gets invalid.",
        "hint3": "Riddle: I split your program into pages and scatter them like laundry. The key is sitting in a free frame.",
        "objects": {
            "hint1": (90, 160, 165, 95, "Tiny Holes"),
            "puzzle": (515, 155, 175, 105, "Paging Quiz"),
            "hint3": (300, 390, 185, 80, "Page Table"),
            "key": (535, 390, 145, 80, "Free Frame"),
            "decoy": (95, 390, 140, 75, "Limit Register"),
        },
    },
    {
        "title": "Room 9: Virtual Memory Exit",
        "topic": "Virtual Memory",
        "theme": "The final chamber glitches: half the room is in memory, half is on disk, all of it is judging you.",
        "concept": "Virtual memory separates logical memory from physical memory and uses demand paging, page faults, and replacement algorithms.",
        "palette": ((10, 4, 18), (45, 18, 78), (0, 230, 255)),
        "question": "What event happens when a needed page is not currently in main memory?",
        "answers": ["page fault", "pagefault", "fault"],
        "hint1": "The room is bigger than the building. Start at the impossible mirror.",
        "hint2": "Correct! Hint #2: the missing page is not gone, just not loaded. Check the swap portal.",
        "hint3": "Riddle: I am not here, but I can still run. My page is fashionably late from disk. The final key is in the fault trap.",
        "objects": {
            "hint1": (90, 150, 170, 95, "Impossible Mirror"),
            "puzzle": (515, 150, 175, 105, "Demand Pager"),
            "hint3": (295, 390, 190, 80, "Swap Portal"),
            "key": (540, 388, 135, 82, "Fault Trap"),
            "decoy": (95, 395, 135, 75, "Belady Ghost"),
        },
    },
]


def normalize(text):
    return text.strip().lower().replace("_", " ")


def wrap_lines(text, font, width):
    # Character-based wrapping works well enough with pygame default fonts.
    chars = max(25, width // 9)
    lines = []
    for part in str(text).split("\n"):
        lines.extend(textwrap.wrap(part, chars) or [""])
    return lines


def draw_text(screen, font, text, x, y, color=(235, 240, 255), width=720, line_gap=4):
    yy = y
    for line in wrap_lines(text, font, width):
        screen.blit(font.render(line, True, color), (x, yy))
        yy += font.get_height() + line_gap
    return yy


def draw_button(screen, rect, label, font, fill, border, text_color=(255, 255, 255)):
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, border, rect, 2, border_radius=10)
    label_img = font.render(label, True, text_color)
    label_rect = label_img.get_rect(center=rect.center)
    screen.blit(label_img, label_rect)


def draw_escape_background(screen, room, tick):
    base, wall, accent = room["palette"]
    screen.fill(base)

    # Back wall and floor perspective.
    pygame.draw.rect(screen, wall, pygame.Rect(55, 70, 690, 330), border_radius=8)
    pygame.draw.polygon(screen, tuple(max(c - 22, 0) for c in wall), [(55, 400), (745, 400), (800, 600), (0, 600)])

    # CRT scanlines and flicker.
    flicker = 18 if (tick // 18) % 2 == 0 else 0
    for y in range(0, SCREEN_HEIGHT, 8):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (SCREEN_WIDTH, y), 1)
    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(4):
        pygame.draw.rect(glow, (*accent, 18 + flicker), pygame.Rect(65 - i * 3, 80 - i * 3, 670 + i * 6, 310 + i * 6), 2, border_radius=10)
    screen.blit(glow, (0, 0))

    # Ceiling lamp.
    pygame.draw.line(screen, accent, (400, 0), (400, 85), 3)
    pygame.draw.circle(screen, accent, (400, 95), 25)
    pygame.draw.circle(screen, (255, 255, 220), (400, 95), 10)

    # Door.
    pygame.draw.rect(screen, (18, 12, 20), pygame.Rect(355, 200, 90, 200), border_radius=6)
    pygame.draw.rect(screen, accent, pygame.Rect(355, 200, 90, 200), 2, border_radius=6)
    pygame.draw.circle(screen, accent, (430, 300), 5)


class EscapeRoomGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("consolas", 30, bold=True)
        self.body_font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.room_index = 0
        self.mode = "room"  # room, question, hallway, freedom
        self.answer_text = ""
        self.message = "Click objects to search the room. Find Hint #1 first."
        self.tick = 0
        self.room_progress = [self.new_progress() for _ in ROOMS]
        self.transition_timer = 0

    @staticmethod
    def new_progress():
        return {
            "hint1": False,
            "question_open": False,
            "question_solved": False,
            "hint3": False,
            "key": False,
            "escaped": False,
            "searched_decoys": set(),
        }

    @property
    def room(self):
        return ROOMS[self.room_index]

    @property
    def progress(self):
        return self.room_progress[self.room_index]

    def object_at(self, pos):
        for obj_id, data in self.room["objects"].items():
            x, y, w, h, label = data
            if pygame.Rect(x, y, w, h).collidepoint(pos):
                return obj_id
        return None

    def handle_room_click(self, pos):
        # Door exit area.
        door_rect = pygame.Rect(355, 200, 90, 200)
        if door_rect.collidepoint(pos):
            if self.progress["key"]:
                self.progress["escaped"] = True
                if self.room_index == len(ROOMS) - 1:
                    self.mode = "freedom"
                    self.message = "SYSTEM ESCAPED. You beat the OS."
                else:
                    self.mode = "hallway"
                    self.transition_timer = 0
                    self.message = "Door unlocked. Enter the hallway."
            else:
                self.message = "The door is locked. You need the key first."
            return

        obj = self.object_at(pos)
        if obj is None:
            self.message = random.choice([
                "You tap the wall. The wall says nothing. Rude.",
                "Dusty pixels. No clue here.",
                "The OS whispers: segmentation fault... just kidding.",
            ])
            return

        if obj == "hint1":
            self.progress["hint1"] = True
            self.message = "Hint #1 found: " + self.room["hint1"]
        elif obj == "puzzle":
            if not self.progress["hint1"]:
                self.message = "This puzzle panel is asleep. Find Hint #1 first."
            elif self.progress["question_solved"]:
                self.message = "Already solved: " + self.room["hint2"]
            else:
                self.mode = "question"
                self.answer_text = ""
                self.message = "Answer the OS question to unlock Hint #2."
        elif obj == "hint3":
            if not self.progress["question_solved"]:
                self.message = "Hint #2 is locked. Solve the OS question first."
            else:
                self.progress["hint3"] = True
                self.message = "Hint #3 found: " + self.room["hint3"]
        elif obj == "key":
            if not self.progress["hint3"]:
                self.message = "You sense a key here... but the riddle has not revealed it yet."
            else:
                self.progress["key"] = True
                self.message = "KEY FOUND! Click the door to escape this room."
        else:
            label = self.room["objects"][obj][4]
            self.progress["searched_decoys"].add(label)
            self.message = f"You searched the {label}. It contains crumbs, dust, and zero kernel privileges."

    def handle_question_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.mode = "room"
            self.message = "Question closed."
        elif event.key == pygame.K_RETURN:
            ans = normalize(self.answer_text)
            valid = [normalize(a) for a in self.room["answers"]]
            if ans in valid:
                self.progress["question_solved"] = True
                self.mode = "room"
                self.message = self.room["hint2"]
            else:
                self.message = "Nope. The OS beeped judgmentally. Try again."
        elif event.key == pygame.K_BACKSPACE:
            self.answer_text = self.answer_text[:-1]
        else:
            if event.unicode and len(self.answer_text) < 45:
                self.answer_text += event.unicode

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.mode != "question":
                return False
            if self.mode == "question":
                self.handle_question_key(event)
            elif self.mode == "hallway":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.room_index += 1
                    self.mode = "room"
                    self.message = "New room loaded. Click around until you find Hint #1."
            elif self.mode == "freedom":
                if event.key == pygame.K_r:
                    self.room_index = 0
                    self.mode = "room"
                    self.room_progress = [self.new_progress() for _ in ROOMS]
                    self.message = "Reset complete. Back to Room 1."
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mode == "room":
                self.handle_room_click(event.pos)
            elif self.mode == "hallway":
                # Click next door.
                if pygame.Rect(300, 235, 200, 135).collidepoint(event.pos):
                    self.room_index += 1
                    self.mode = "room"
                    self.message = "New room loaded. Click around until you find Hint #1."
        return True

    def draw_room_objects(self):
        for obj_id, data in self.room["objects"].items():
            x, y, w, h, label = data
            rect = pygame.Rect(x, y, w, h)
            accent = self.room["palette"][2]
            fill = (18, 18, 28)
            border = (95, 95, 110)

            if obj_id == "hint1" and not self.progress["hint1"]:
                border = accent
            elif obj_id == "puzzle" and self.progress["hint1"] and not self.progress["question_solved"]:
                border = (255, 235, 120)
            elif obj_id == "hint3" and self.progress["question_solved"] and not self.progress["hint3"]:
                border = accent
            elif obj_id == "key" and self.progress["hint3"] and not self.progress["key"]:
                border = (255, 240, 80)
                fill = (45, 35, 8)
            elif obj_id == "key" and self.progress["key"]:
                border = (110, 255, 110)

            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)

            # Little icon-ish shapes.
            cx, cy = rect.center
            if obj_id == "key":
                pygame.draw.circle(self.screen, border, (cx - 18, cy), 10, 2)
                pygame.draw.line(self.screen, border, (cx - 8, cy), (cx + 32, cy), 3)
                pygame.draw.line(self.screen, border, (cx + 20, cy), (cx + 20, cy + 10), 2)
            elif obj_id == "puzzle":
                pygame.draw.rect(self.screen, border, pygame.Rect(cx - 25, cy - 18, 50, 36), 2)
                pygame.draw.line(self.screen, border, (cx - 18, cy - 4), (cx + 18, cy - 4), 2)
                pygame.draw.line(self.screen, border, (cx - 18, cy + 8), (cx + 12, cy + 8), 2)
            else:
                pygame.draw.circle(self.screen, border, (cx, cy - 8), 12, 2)
                pygame.draw.line(self.screen, border, (cx, cy + 4), (cx, cy + 20), 2)

            label_img = self.small_font.render(label, True, (230, 230, 240))
            self.screen.blit(label_img, (x + 8, y + h - 24))

    def draw_hud(self):
        pygame.draw.rect(self.screen, (5, 5, 12), pygame.Rect(0, 0, SCREEN_WIDTH, 70))
        self.screen.blit(self.title_font.render(self.room["title"], True, (255, 255, 255)), (20, 12))
        progress_text = (
            f"Hint1: {'Y' if self.progress['hint1'] else 'N'}  |  "
            f"Question: {'Y' if self.progress['question_solved'] else 'N'}  |  "
            f"Riddle: {'Y' if self.progress['hint3'] else 'N'}  |  "
            f"Key: {'Y' if self.progress['key'] else 'N'}"
        )
        self.screen.blit(self.small_font.render(progress_text, True, self.room["palette"][2]), (22, 46))
        self.screen.blit(self.small_font.render(f"Room {self.room_index + 1}/9", True, (190, 190, 210)), (700, 46))

    def draw_info_panel(self):
        panel = pygame.Rect(20, 475, 760, 105)
        pygame.draw.rect(self.screen, (5, 5, 12), panel, border_radius=12)
        pygame.draw.rect(self.screen, self.room["palette"][2], panel, 2, border_radius=12)
        draw_text(self.screen, self.small_font, "OS Concept: " + self.room["concept"], 34, 488, (190, 220, 255), 730)
        draw_text(self.screen, self.small_font, "Log: " + self.message, 34, 528, (245, 245, 245), 730)

    def draw_room(self):
        draw_escape_background(self.screen, self.room, self.tick)
        self.draw_hud()
        draw_text(self.screen, self.small_font, self.room["theme"], 75, 92, (220, 220, 230), 650)
        self.draw_room_objects()

        # Door label changes after key.
        door_text = "EXIT" if self.progress["key"] else "LOCKED"
        door_color = (120, 255, 120) if self.progress["key"] else (255, 90, 90)
        self.screen.blit(self.small_font.render(door_text, True, door_color), (374, 410))
        self.draw_info_panel()

    def draw_question(self):
        self.draw_room()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))
        box = pygame.Rect(90, 140, 620, 310)
        pygame.draw.rect(self.screen, (10, 12, 24), box, border_radius=16)
        pygame.draw.rect(self.screen, self.room["palette"][2], box, 3, border_radius=16)
        self.screen.blit(self.title_font.render("OS QUESTION LOCK", True, (255, 255, 255)), (120, 165))
        draw_text(self.screen, self.body_font, self.room["question"], 120, 220, (235, 240, 255), 560)
        input_rect = pygame.Rect(120, 320, 560, 45)
        pygame.draw.rect(self.screen, (0, 0, 0), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2, border_radius=8)
        self.screen.blit(self.body_font.render(self.answer_text + "_", True, self.room["palette"][2]), (132, 332))
        self.screen.blit(self.small_font.render("ENTER = submit   ESC = close", True, (190, 190, 205)), (120, 388))
        self.screen.blit(self.small_font.render(self.message, True, (255, 220, 150)), (120, 415))

    def draw_hallway(self):
        self.screen.fill((3, 3, 10))
        for i in range(16):
            shade = 20 + i * 7
            pygame.draw.rect(self.screen, (shade // 3, shade // 3, shade), pygame.Rect(40 + i * 20, 40 + i * 14, 720 - i * 40, 520 - i * 28), 1)
        self.screen.blit(self.big_font.render("HALLWAY", True, (255, 255, 255)), (275, 90))
        done = self.room["topic"]
        next_room = ROOMS[self.room_index + 1]["topic"]
        draw_text(self.screen, self.body_font, f"You escaped {done}. The OS hallway hums like a cursed server rack.", 120, 170, (230, 230, 240), 560)
        door = pygame.Rect(300, 235, 200, 135)
        draw_button(self.screen, door, f"Enter {next_room}", self.body_font, (18, 18, 35), ROOMS[self.room_index + 1]["palette"][2])
        self.screen.blit(self.small_font.render("Click the door or press ENTER/SPACE.", True, (190, 190, 205)), (250, 405))

    def draw_freedom(self):
        self.screen.fill((1, 7, 10))
        for _ in range(80):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, random.choice([(0, 255, 180), (0, 220, 255), (255, 255, 255)]), (x, y), 1)
        self.screen.blit(self.big_font.render("FREEDOM.EXE", True, (0, 255, 180)), (235, 120))
        draw_text(self.screen, self.body_font, "You escaped the Operating System. The kernel releases your process, closes the file, clears memory, and pretends this was normal behavior.", 120, 205, (240, 240, 255), 560)
        draw_text(self.screen, self.body_font, "Final status: EXIT CODE 0 — YAY", 250, 330, (255, 240, 120), 400)
        self.screen.blit(self.small_font.render("Press R to restart or ESC to quit.", True, (200, 200, 210)), (275, 430))

    def draw(self):
        if self.mode == "room":
            self.draw_room()
        elif self.mode == "question":
            self.draw_question()
        elif self.mode == "hallway":
            self.draw_hallway()
        elif self.mode == "freedom":
            self.draw_freedom()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.tick += 1
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break
            self.draw()
            self.clock.tick(60)


def run_game():
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("OS Escape Room: Escape the Operating System")
    EscapeRoomGame(screen).run()
