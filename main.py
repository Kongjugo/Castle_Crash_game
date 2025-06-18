import pygame
import os
import random
import math

# 게임 스크린 크기 
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# RGB 값 색상 지정
Black = (0, 0, 0)
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)
Pink = (255, 192, 203)
Gray = (150, 150, 150)

# FPS 설정
FPS = 60

# 초기화 
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Window Name 설정
pygame.display.set_caption("Castle Crash")

# Window 크기 정의
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Screen Update
clock = pygame.time.Clock()

# Assets Folder Path 설정
current_path = os.path.dirname(__file__)
asset_path = os.path.join(current_path, 'assets')

# Font 설정 (assets 폴더에 폰트 파일 필요)
header = pygame.font.Font(os.path.join(asset_path, 'ChosunKg.TTF'), 60)
subheader = pygame.font.Font(os.path.join(asset_path, 'ChosunSg.TTF'), 20)

bold = pygame.font.Font(os.path.join(asset_path, 'ChosunKg.TTF'), 30)
regular = pygame.font.Font(os.path.join(asset_path, 'ChosunSg.TTF'), 20)

# 배경화면 (assets 폴더에 background.png 필요)
background = pygame.image.load(os.path.join(asset_path, 'background.png'))

# 이미지 불러오기 (assets 폴더에 player.png, enemy.png 필요)
player_image = pygame.image.load(os.path.join(asset_path, 'player.png'))
enemy_image = pygame.image.load(os.path.join(asset_path, 'enemy.png'))

# 음원 불러오기
bgm_menu = pygame.mixer.Sound(os.path.join(asset_path, 'bgm_menu.mp3'))
bgm_play = pygame.mixer.Sound(os.path.join(asset_path, 'bgm_play.mp3'))
shoot_sound = pygame.mixer.Sound(os.path.join(asset_path, 'shoot.mp3'))
break_sound = pygame.mixer.Sound(os.path.join(asset_path, 'break.mp3'))

# 전역 변수 설정
enemy_health = 100
player_health = 100

player_damage = 10
enemy_damage = 10

background_top_y = SCREEN_HEIGHT - background.get_height()

player_x = SCREEN_WIDTH // 2 - player_image.get_width() // 2 - 290
enemy_x = SCREEN_WIDTH // 2 - enemy_image.get_width() // 2 + 230 

player_y = SCREEN_HEIGHT // 2 - player_image.get_height() + 215
enemy_y = SCREEN_HEIGHT // 2 - enemy_image.get_height() + 240 

# 발사 관련 변수
player_angle = 55
player_power = 65
enemy_angle = 0
enemy_power = 0

projectile = None  # 현재 발사체
trajectory_points = []

round_timer = 0
round_number = 1
player_fired = False
enemy_fired = False
player_can_shoot = True

# 게임 상태: 0: 메뉴, 1: 게임 플레이, 2: 게임 종료, 3: 일시정지, 4: 설명
game_state = 0

# 설명화면에서 돌아갈 이전 상태 저장용 변수
prev_game_state = 0
instruction_page = 0  # 0: 조작 방법, 1: 랭크 설명

# 누적 시간 변수
total_play_time = 0  # 단위: 프레임

def play_bgm():
    global bgm_menu, bgm_play, game_state
    if game_state == 0:
        bgm_menu.set_volume(0.4)
        if not pygame.mixer.get_busy():
            bgm_menu.play(-1)
    elif game_state == 1:
        bgm_menu.stop()
        bgm_play.set_volume(0.3)
        if not pygame.mixer.get_busy():
            bgm_play.play(-1)
    else:
        bgm_menu.stop()
        bgm_play.stop()

# 초기화 함수
def init_game():
    global player_health, enemy_health, player_angle, player_power
    global round_number, round_timer, player_fired, enemy_fired, projectile, trajectory_points, player_can_shoot, player_x
    global total_play_time, forfeit_flag
    player_health = 100
    enemy_health = 100
    player_angle = 45
    player_power = 50
    round_number = 1
    round_timer = 0
    player_fired = False
    enemy_fired = False
    projectile = None
    trajectory_points.clear()
    player_can_shoot = True
    player_x = SCREEN_WIDTH // 2 - player_image.get_width() // 2 - 290
    total_play_time = 0
    forfeit_flag = False

# 메뉴 화면 
def draw_menu(blink):
    play_bgm()
    screen.fill(White)
    title = header.render("Castle Crash", True, Black)
    subtitle = subheader.render("made by seogo", True, Black)

    if blink:
        start_text = regular.render("Press Space to Start", True, Black)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 - 15))
    pygame.display.flip()

# 게임 화면
def draw_play():    
    play_bgm()
    screen.fill(White)
    screen.blit(background, [SCREEN_WIDTH // 2 - background.get_width() // 2, SCREEN_HEIGHT - background.get_height()])

    # UI
    round_text = bold.render(f"Round {round_number}", True, Red)
    timer_text = regular.render(f"Time: {round_timer // FPS}", True, Black)

    player_health_text = regular.render(f"Player Health: {player_health}", True, Black)
    enemy_health_text = regular.render(f"Enemy Health: {enemy_health}", True, Black)

    screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, 10))
    screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 50))
    screen.blit(player_health_text, (10, 10))
    screen.blit(enemy_health_text, (SCREEN_WIDTH - enemy_health_text.get_width() - 10, 10))

    screen.blit(player_image, (player_x, player_y))
    screen.blit(enemy_image, (enemy_x, enemy_y))

    # 각도/세기 표시
    angle_text = regular.render(f"Angle: {player_angle}", True, Black)
    power_text = regular.render(f"Power: {player_power}", True, Black)
    screen.blit(angle_text, (10, 40))
    screen.blit(power_text, (10, 65))

    # 포물선 궤적 그리기 (플레이어가 발사 준비 중일 때만)
    if not player_fired and not enemy_fired:
        for point in calculate_trajectory(player_x + player_image.get_width(), player_y + player_image.get_height() // 2 - 30, player_angle, player_power):
            pygame.draw.circle(screen, (180,180,180), point, 1)

    # 발사체 그리기
    if projectile:
        pygame.draw.circle(screen, Blue, (int(projectile['x']), int(projectile['y'])), 6)

    # 파티클 업데이트 및 그리기
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0 or p.radius <= 0:
            particles.remove(p)

    # Q키 안내 메시지 (라운드 3의 배수마다)
    if game_state == 1 and round_number % 3 == 0:
        q_msg = regular.render("Q를 누르면 현재 라운드와 시간에서 포기할 수 있습니다.", True, (80, 80, 255))
        screen.blit(q_msg, (SCREEN_WIDTH // 2 - q_msg.get_width() // 2, SCREEN_HEIGHT - 60))

    pygame.display.flip()

# 궤적 계산 함수 (속도 30% 증가)
def calculate_trajectory(x, y, angle, power):
    # 속도 40% 증가 (30% + 10%)
    rad_angle = math.radians(angle)
    v = power * 1.4
    vx = v * math.cos(rad_angle)
    vy = -v * math.sin(rad_angle)
    g = 9.8
    points = []
    t = 0
    dt = 0.05
    while True:
        px = x + vx * t
        py = y + vy * t + 0.5 * g * (t ** 2)
        # 화면을 벗어나지 않도록 제한
        if py > SCREEN_HEIGHT:
            py = SCREEN_HEIGHT
        if px < 0:
            px = 0
        if px > SCREEN_WIDTH:
            px = SCREEN_WIDTH
        points.append((int(px), int(py)))
        if py >= SCREEN_HEIGHT:
            break
        t += dt
        if len(points) > 400:
            break
    return points

def draw_instruction():
    screen.fill(White)
    # 타이틀 상단에 배치
    if instruction_page == 0:
        title = header.render("조작 방법", True, Black)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
        lines = [
            "방향키 ↑↓ : 각도 조절",
            "방향키 ←→ : 파워 조절",
            "Space : 발사/시작/재시작",
            "S : 일시정지/재개",
            "I : 조작방법 보기/끄기",
            "D : 다음 페이지",
            "X : 게임 종료",
            "R : 메뉴로",
            "Q : 포기하기"
        ]
        y = 160
        for line in lines:
            txt = regular.render(line, True, Black)
            screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
            y += 40
        info = regular.render("D: 다음 / I: 닫기", True, Gray)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, y + 20))
    elif instruction_page == 1:
        title = header.render("랭크 설명", True, Black)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
        rank_lines = [
            "플래티넘 : 2분 안에 클리어",
            "골드     : 3분 안에 클리어",
            "실버     : 4분 안에 클리어",
            "브론즈   : 4분 이상 클리어",
            "아이언   : 중도 포기"
        ]
        y = 180
        for line in rank_lines:
            txt = regular.render(line, True, Black)
            screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
            y += 45
        info = regular.render("A: 이전 / I: 닫기", True, Gray)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, y + 20))
    pygame.display.flip()

# 이벤트 함수
def handle_event():
    global game_state, player_angle, player_power, projectile, trajectory_points
    global player_fired, player_can_shoot, prev_game_state, instruction_page, winner, forfeit_flag

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        if event.type == pygame.KEYDOWN:
            # 메뉴 화면에서 X로 종료
            if game_state == 0 and event.key == pygame.K_x:
                return True
            # 일시정지 상태에서만 X, R 동작
            if game_state == 3:
                if event.key == pygame.K_x:
                    return True  # X를 누르면 게임 종료
                if event.key == pygame.K_r:
                    game_state = 0  # R을 누르면 메뉴로 돌아감
                    return False
                if event.key == pygame.K_s:
                    game_state = 1  # S를 누르면 일시정지 해제
                return False
            # 설명화면에서 페이지 이동 및 닫기
            if game_state == 4:
                if event.key == pygame.K_i:
                    game_state = prev_game_state
                    return False
                if event.key == pygame.K_d:
                    instruction_page = min(1, instruction_page + 1)
                    return False
                if event.key == pygame.K_a:
                    instruction_page = max(0, instruction_page - 1)
                    return False
                # 다른 키는 무시
                return False
            if event.key == pygame.K_i:
                prev_game_state = game_state
                game_state = 4  # I를 누르면 설명화면
                instruction_page = 0
            elif event.key == pygame.K_s:
                if game_state == 1:
                    game_state = 3  # S를 누르면 일시정지
            elif event.key == pygame.K_q:
                if game_state == 1:
                    # 플레이 중 Q를 누르면 포기 처리
                    game_state = 2
                    winner = "포기"
                    forfeit_flag = True
            elif event.key == pygame.K_SPACE:
                if game_state == 0:
                    init_game()
                    game_state = 1
                elif game_state == 1 and not player_fired and not enemy_fired and player_can_shoot:
                    fire_player()
            elif event.key == pygame.K_UP:
                if game_state == 1 and not player_fired and not enemy_fired:
                    player_angle = min(player_angle + 1, 90)
            elif event.key == pygame.K_DOWN:
                if game_state == 1 and not player_fired and not enemy_fired:
                    player_angle = max(player_angle - 1, 0)
            elif event.key == pygame.K_RIGHT:
                if game_state == 1 and not player_fired and not enemy_fired:
                    player_power = min(player_power + 1, 100)
            elif event.key == pygame.K_LEFT:
                if game_state == 1 and not player_fired and not enemy_fired:
                    player_power = max(player_power - 1, 10)
            # 결과 화면에서 스페이스 누르면 메뉴로
            if game_state == 2:
                if event.key == pygame.K_SPACE:
                    game_state = 0
                return False

    return False

# 플레이어 발사 (한 번만 발사 가능)
def fire_player():
    global projectile, trajectory_points, player_fired, player_can_shoot, player_damage, player_power
    player_fired = True
    player_can_shoot = False
    shoot_sound.play(maxtime=3000)
    # 발사 위치를 약간 위로 올림
    start_x = player_x + player_image.get_width()
    start_y = player_y + player_image.get_height() // 2 - 20  # 20픽셀 위로
    trajectory_points.clear()
    trajectory_points.extend(calculate_trajectory(start_x, start_y, player_angle, player_power))
    rad = math.radians(player_angle)
    projectile = {
        'x': start_x,
        'y': start_y,
        'vx': player_power * 1.5 * 1.4 * math.cos(rad),  # 속도 40% 증가
        'vy': -player_power * 1.5 * 1.4 * math.sin(rad), # 속도 40% 증가
        'time': 0
    }
    n = random.randint(2, 4)
    player_damage = int(player_power * 2 * (0.4 ** n))

# 적 발사 (40% 확률로 명중, 60%는 근처 빗나감)
def enemy_fire():
    global projectile, trajectory_points, enemy_fired, player_fired, enemy_damage

    enemy_fired = True
    player_fired = False

    angle_deg = 130
    min_power = 40
    max_power = 60

    hit_chance = random.random()
    if hit_chance < 0.4:
        target_x = player_x + player_image.get_width() // 2
        target_y = player_y + player_image.get_height() // 2
        start_x = enemy_x
        start_y = enemy_y + enemy_image.get_height() // 2 - 20  # 20픽셀 위로
        dx = target_x - start_x
        dy = start_y - target_y
        g = 9.8

        rad = math.radians(angle_deg)
        try:
            best_power = min_power
            min_dist = float('inf')
            for power in range(min_power, max_power + 1):
                vx = power * 1.3 * math.cos(rad)
                vy = -power * 1.3 * math.sin(rad)
                if vx == 0:
                    continue
                t = dx / vx
                if t < 0:
                    continue
                y_at_t = start_y + vy * t + 0.5 * g * (t ** 2)
                dist = abs(y_at_t - target_y)
                if dist < min_dist:
                    min_dist = dist
                    best_power = power
            power_rand = best_power + random.uniform(-1.5, 1.5)
            power_rand = max(min_power, min(max_power, power_rand))
        except Exception:
            power_rand = random.randint(min_power, max_power)
    else:
        power_rand = random.randint(min_power, max_power)
        miss = random.uniform(6, 12)
        if random.choice([True, False]):
            power_rand += miss
        else:
            power_rand -= miss
        power_rand = max(min_power, min(max_power, power_rand))

    start_x = enemy_x
    start_y = enemy_y + enemy_image.get_height() // 2 - 20  # 20픽셀 위로

    trajectory_points.clear()
    trajectory_points.extend(calculate_trajectory(start_x, start_y, angle_deg, power_rand))

    rad = math.radians(angle_deg)
    shoot_sound.play(maxtime=3000)
    projectile = {
        'x': trajectory_points[0][0],
        'y': trajectory_points[0][1],
        'vx': power_rand * 1.5 * 1.4 * math.cos(rad),   # 속도 40% 증가
        'vy': -power_rand * 1.5 * 1.4 * math.sin(rad),  # 속도 40% 증가
        'time': 0
    }
    n = random.randint(2, 4)
    enemy_damage = int(power_rand * 4 * (0.4 ** n))

# 파티클 클래스
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 5)
        self.color = random.choice([(255, 80, 80), (255, 200, 80), (255, 255, 255)])
        self.life = random.randint(15, 30)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius = max(1, self.radius - 0.1)
        self.life -= 1

    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

particles = []

# 발사체 위치 업데이트
def update_projectile():
    global projectile, player_health, enemy_health, enemy_fired, player_fired, particles

    if projectile:
        # 궤도 따라가기: trajectory_points를 따라 이동
        if 'trajectory_idx' not in projectile:
            projectile['trajectory_idx'] = 0
        projectile['trajectory_idx'] += 1
        if projectile['trajectory_idx'] < len(trajectory_points):
            projectile['x'], projectile['y'] = trajectory_points[projectile['trajectory_idx']]
        else:
            end_turn()
            return

        proj_x = int(projectile['x'])
        proj_y = int(projectile['y'])

        player_rect = pygame.Rect(player_x, player_y, player_image.get_width(), player_image.get_height())
        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_image.get_width(), enemy_image.get_height())
        proj_rect = pygame.Rect(proj_x - 3, proj_y - 3, 6, 6)

        if enemy_fired:
            if player_rect.colliderect(proj_rect):
                break_sound.play()
                player_health -= enemy_damage
                for _ in range(20):
                    particles.append(Particle(proj_x, proj_y))
                end_turn()
        elif player_fired:
            if enemy_rect.colliderect(proj_rect):
                break_sound.play()
                enemy_health -= player_damage
                for _ in range(20):
                    particles.append(Particle(proj_x, proj_y))
                end_turn()

# 턴 종료 처리
def end_turn():
    global projectile, player_fired, enemy_fired, round_number, round_timer, player_can_shoot, player_x

    projectile = None
    trajectory_points.clear()

    if player_fired and not enemy_fired:
        player_fired = False
        enemy_fire()
    elif enemy_fired:
        reset_round()

# 라운드 리셋
def reset_round():
    global round_number, round_timer, enemy_fired, player_fired, player_can_shoot, player_x
    global player_health, enemy_health, player_angle, player_power

    round_number += 1
    if round_number > 20:
        round_number = 20

    # 라운드가 지날 때마다 플레이어의 각도와 파워를 랜덤하게 변경
    player_angle = random.randint(20, 70)
    player_power = random.randint(30, 70)

    round_timer = 0
    enemy_fired = False
    player_fired = False
    player_can_shoot = True
    player_x -= 5

# 게임 오버 화면
def draw_game_over(winner):
    screen.fill(White)
    # 랭크가 가장 눈에 띄게
    total_seconds = total_play_time // FPS
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    # 랭크 판정
    if forfeit_flag:
        rank = "아이언"
        rank_color = (120, 120, 120)
    elif total_seconds <= 120:
        rank = "플래티넘"
        rank_color = (0, 180, 255)
    elif total_seconds <= 180:
        rank = "골드"
        rank_color = (255, 215, 0)
    elif total_seconds <= 240:
        rank = "실버"
        rank_color = (180, 180, 180)
    else:
        rank = "브론즈"
        rank_color = (205, 127, 50)

    rank_text = header.render(f"{rank}", True, rank_color)
    time_text = regular.render(f"Total Time : {minutes}분 {seconds}초", True, Black)
    round_text = regular.render(f"Round : {round_number}", True, Black)
    restart_text = regular.render("스페이스 : 메뉴로", True, Gray)

    y = SCREEN_HEIGHT // 2 - 120
    screen.blit(rank_text, (SCREEN_WIDTH // 2 - rank_text.get_width() // 2, y))
    y += rank_text.get_height() + 10
    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, y))
    y += time_text.get_height() + 10
    screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, y))
    y += round_text.get_height() + 40
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y))

    pygame.display.flip()

# 메인 루프
def main():
    global round_timer, game_state, player_health, enemy_health, round_number, total_play_time, winner, forfeit_flag

    blink = True
    blink_timer = 0

    running = True
    winner = ""
    forfeit_flag = False
    while running:
        clock.tick(FPS)
        running = not handle_event()

        if game_state == 0:
            blink_timer += 1
            if blink_timer % 30 == 0:
                blink = not blink
            draw_menu(blink)

        elif game_state == 1:
            round_timer += 1
            total_play_time += 1  # 누적 시간 증가
            update_projectile()
            draw_play()
            # 승리 조건 체크
            if enemy_health <= 0:
                game_state = 2
                winner = "Player"
                forfeit_flag = False
            elif player_health <= 0:
                game_state = 2
                winner = "Enemy"
                forfeit_flag = False
            elif round_number >= 20:
                if player_health > enemy_health:
                    game_state = 2
                    winner = "Player"
                elif player_health < enemy_health:
                    game_state = 2
                    winner = "Enemy"
                else:
                    game_state = 2
                    winner = "Draw"
                forfeit_flag = False

        elif game_state == 2:
            draw_game_over(winner)

        elif game_state == 3:
            # 일시정지 화면
            pause_text = header.render("일시정지", True, Red)
            info_text = regular.render("S를 다시 누르면 재개", True, Black)
            total_seconds = total_play_time // FPS
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_text = regular.render(f"Total Time : {minutes}분 {seconds}초", True, Black)
            round_text = regular.render(f"Round : {round_number}", True, Black)

            screen.fill(White)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
            screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
            pygame.display.flip()

        elif game_state == 4:
            draw_instruction()

    pygame.quit()

if __name__ == "__main__":
    main()
