import pygame
import sqlite3
import random
import sys

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Arial", 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Собери очки и победи!")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 50)
        self.speed = 5
        self.score = 0

    def move(self, keys):
        if keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_UP]: self.rect.y -= self.speed
        if keys[pygame.K_DOWN]: self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

class ScoreDB:
    def __init__(self):
        self.conn = sqlite3.connect("player.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
            name TEXT, score INTEGER
        )''')
        self.conn.commit()

    def add_score(self, name, score):
        self.cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
        self.conn.commit()

    def get_top_scores(self, limit=5):
        self.cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


def create_collectibles(count):
    return [pygame.Rect(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), 20, 20) for _ in range(count)]

def create_traps(count):
    return [pygame.Rect(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), 30, 30) for _ in range(count)]


def get_username():
    input_text = ""
    active = True
    while active:
        screen.fill(BLACK)
        text = font.render("Введите ваше имя и нажмите Enter:", True, WHITE)
        screen.blit(text, (100, 200))
        user_input = font.render(input_text, True, GREEN)
        screen.blit(user_input, (100, 250))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode


def show_game_over(name, score, db):
    db.add_score(name, score)
    top_scores = db.get_top_scores()
    screen.fill(BLACK)
    game_over = font.render(f"Игра окончена! Ваш результат: {score}", True, WHITE)
    screen.blit(game_over, (100, 100))

    top_text = font.render("ТОП 5 игроков:", True, WHITE)
    screen.blit(top_text, (100, 150))
    for i, (n, s) in enumerate(top_scores):
        score_line = font.render(f"{i+1}. {n} — {s}", True, GREEN if n == name else WHITE)
        screen.blit(score_line, (100, 180 + i * 30))

    prompt = font.render("Нажмите клавишу 'Esc' для выхода", True, RED)
    screen.blit(prompt, (100, 400))
    pygame.display.flip()
    wait_for_esc()

def wait_for_esc():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False

def main():
    db = ScoreDB()
    name = get_username()
    player = Player()
    collectibles = create_collectibles(10)
    traps = create_traps(5)
    running = True

    while running:
        clock.tick(FPS)
        screen.fill((30, 30, 30))

        keys = pygame.key.get_pressed()
        player.move(keys)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for c in collectibles[:]:
            if player.rect.colliderect(c):
                player.score += 1
                collectibles.remove(c)

        for t in traps:
            if player.rect.colliderect(t):
                show_game_over(name, player.score, db)
                running = False

        if not collectibles:
            show_game_over(name, player.score + 5, db)
            running = False

        player.draw()
        for c in collectibles:
            pygame.draw.rect(screen, WHITE, c)
        for t in traps:
            pygame.draw.rect(screen, RED, t)

        score_text = font.render(f"{name}, очки: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    db.close()
    pygame.quit()

if __name__ == "__main__":
    main()
