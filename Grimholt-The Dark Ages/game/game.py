import pygame as pg
import sys
from .world import World
from .settings import TILE_SIZE
from .utils import draw_text
from .camera import Camera
from .hud import Hud
from .resource_manager import ResourceManager


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()

        self.state = "playing"

        # entities
        self.entities = []

        # resource manager
        self.resource_manager = ResourceManager()

        # hud
        self.hud = Hud(self.resource_manager, self.width, self.height)

        # world
        self.world = World(self.resource_manager, self.entities, self.hud, 100, 100, self.width, self.height)

        # camera
        self.camera = Camera(self.width, self.height)

        self.food_timer = 0
        self.food_consumption_interval = 10000  # Millisekunden (1 Sekunde)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(60)
            self.events()
            self.update()
            self.draw()

    def events(self):
        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEWHEEL:
                # Handling wie gehabt
                scroll_speed = self.hud.scroll_speed
                tile_height = self.hud.tiles[0]["icon"].get_height() + 10
                total_height = len(self.hud.tiles) * tile_height
                visible_height = self.hud.build_surface.get_height()
                max_scroll = max(0, total_height - visible_height)
                new_scroll = self.hud.scroll_offset - event.y * scroll_speed
                self.hud.scroll_offset = max(0, min(new_scroll, max_scroll))

        # Übergib alle Events an HUD (z. B. für Mausklicks etc.)
        self.hud.handle_events(events)

    def update(self):
        self.camera.update()

        dt = self.clock.get_time() / 1000  # Zeit seit letztem Frame in Sekunden
        self.food_timer += dt

        mouse_pos = pg.mouse.get_pos()
        mouse_action = pg.mouse.get_pressed()

        if self.hud.selected_tile is not None and self.hud.selected_tile["name"] == "Demolish":
            if mouse_action[0]:
                for entity in self.entities:
                    if entity.rect.collidepoint(mouse_pos):
                        self.entities.remove(entity)
                        break
        else:
            for e in self.entities:
                if hasattr(e, "update"):
                    e.update()

        # Update ResourceManager (kein automatischer Happiness-Verlust hier!)
        self.resource_manager.update()

        # Food-Verbrauch & Happiness-Anpassung alle 1 Sekunde (food_consumption_interval in Sekunden)
        if self.food_timer >= self.food_consumption_interval / 1000:  # Dividiere durch 1000, da Interval in ms
            self.food_timer = 0

            food_needed_per_villager = 1  # Beispiel
            effective_pop = self.resource_manager.get_effective_population()

            if effective_pop == 0:
                self.state = "game_over"

            total_food_needed = effective_pop * food_needed_per_villager

            current_food = self.resource_manager.resources.get("Food", 0)

            if current_food >= total_food_needed:
                self.resource_manager.resources["Food"] -= total_food_needed

                # Optional: leichte Erholung der Happiness, max 100
                self.resource_manager.happiness = min(100, self.resource_manager.happiness + 1)

            else:
                # Zu wenig Food: Hungerwirkung bis zu 30% Happiness-Verlust (pro Sekunde)
                self.resource_manager.resources["Food"] = 0

                missing_food = total_food_needed - current_food
                hunger_ratio = min(missing_food / total_food_needed, 1)  # 0..1

                happiness_loss = hunger_ratio * 10
                self.resource_manager.happiness -= happiness_loss
                if self.resource_manager.happiness < 0:
                    self.resource_manager.happiness = 0

        self.hud.update()
        self.world.update(self.camera)


    def draw(self):
        self.screen.fill((0, 0, 0))
        self.world.draw(self.screen, self.camera)
        self.hud.draw(self.screen)

        draw_text(
            self.screen,
            'fps={}'.format(round(self.clock.get_fps())),
            25,
            (255, 255, 255),
            (10, 10)
        )

        pg.display.flip()

