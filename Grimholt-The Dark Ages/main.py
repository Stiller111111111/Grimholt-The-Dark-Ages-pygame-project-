import pygame as pg
from game.game import Game

def draw_text(surface, text, size, color, x, y):
    font = pg.font.Font("assets/graphics/font.ttf", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def main():
    pg.init()
    pg.mixer.init()

    music = True
    if music:
        pg.mixer.music.load("assets/sounds/music.mp3")
        pg.mixer.music.play(-1)  # -1 = loop of music
        pg.mixer.music.set_volume(0.2)  # volume of music

    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    clock = pg.time.Clock()
    width, height = screen.get_size()
    game = Game(screen, clock)

    background_img = pg.image.load("assets/graphics/Background.png").convert()
    background_img = pg.transform.scale(background_img, (width, height))

    options_img = pg.image.load("assets/graphics/Options.png").convert()
    options_img = pg.transform.scale(options_img, (width, height))

    game_over_img = pg.image.load("assets/graphics/Game_over.png").convert()
    game_over_img = pg.transform.scale(game_over_img, (width, height))

    running = True
    state = "menu"  # state for menu

    menu_items = ["Play", "Settings", "Quit"]
    options_items = ["Music", "Controls", "Back"]
    controls_items = ["Back"]
    game_over_items = ["Ok"]
    selected = 0

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:
                if state == "menu":
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(menu_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(menu_items)
                    elif event.key == pg.K_RETURN:
                        if menu_items[selected] == "Play":
                            state = "game"
                        elif menu_items[selected] == "Settings":
                            state = "options"
                        elif menu_items[selected] == "Quit":
                            running = False
                    # Settings goes here

                elif state == "options":
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(options_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(options_items)
                    elif event.key == pg.K_RETURN:
                        if options_items[selected] == "Music":
                            music = not music  # Toggle on off
                            if music:
                                pg.mixer.music.unpause()
                            else:
                                pg.mixer.music.pause()
                        elif options_items[selected] == "Controls":
                            state = "controls"
                        elif options_items[selected] == "Back":
                            state = "menu"
                    if event.key == pg.K_ESCAPE:
                        state = "menu"

                elif state == "controls":
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(controls_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(controls_items)
                    elif event.key == pg.K_RETURN:
                        if controls_items[selected] == "Back":
                            state = "options"
                    if event.key == pg.K_ESCAPE:
                        state = "options"
                
                elif state == "game_over":
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(game_over_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(game_over_items)
                    elif event.key == pg.K_RETURN:
                        if game_over_items[selected] == "Ok":
                            running = False

                elif state == "game":
                    if event.key == pg.K_ESCAPE:
                        state = "menu"
                    else:
                        # event to game
                        if hasattr(game, "handle_event"):
                            game.handle_event(event)

            else:
                # other events
                if state == "game" and hasattr(game, "handle_event"):
                    game.handle_event(event)

        screen.blit(background_img, (0, 0))

        if state == "menu":
            draw_text(screen, "Grimholt", width // 20, (255, 255, 255), width // 5, height * 0.06)
            draw_text(screen, "The Dark Ages", width // 20, (255, 255, 255), width // 5, height * 0.15)
            for i, item in enumerate(menu_items):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                draw_text(screen, item, width // 40, color, width // 22, height * (0.34 + i * 0.06))

        elif state == "options":
            screen.blit(options_img, (0, 0))
            draw_text(screen, "Settings", width // 30, (255, 255, 255), width // 5.2, height * 0.11)
            for i, item in enumerate(options_items):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                draw_text(screen, item, width // 40, color, width // 5.2, height * (0.34 + i * 0.06))

        elif state == "controls":
            screen.blit(options_img, (0, 0))
            draw_text(screen, "Controls", width // 30, (255, 255, 255), width // 5.2, height * 0.11)
            for i, item in enumerate(controls_items):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                draw_text(screen, item, width // 40, color, width // 5.2, height * (0.34 + i * 0.06))

        elif game.state == "game_over":
            screen.blit(game_over_img, (0, 0))
            draw_text(screen, "Game Over", width // 30, (255, 255, 255), width // 5.2, height * 0.2)
            draw_text(screen, "Nobody wanted to life", width // 40, (255, 255, 255), width // 5, height * 0.3)
            draw_text(screen, "in such a Empire", width // 40, (255, 255, 255), width // 5, height * 0.4)
            for i, item in enumerate(game_over_items):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                draw_text(screen, item, width // 40, color, width // 5.2, height * (0.5 + i * 0.06))


        elif state == "game":
            game.update()
            game.draw()

        pg.display.flip()
        clock.tick(175)

    pg.quit()

if __name__ == "__main__":
    main()