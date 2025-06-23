import pygame as pg
from .utils import draw_text


class Hud:

    def __init__(self, resource_manager, width, height):

        self.resource_manager = resource_manager
        self.width = width
        self.height = height

        self.hud_colour = (0, 0, 0, 240)

        # Scroll-Offset
        self.scroll_offset = 0
        self.scroll_speed = 200  # speed of scrolling

        # resources hud
        self.resouces_surface = pg.Surface((width * 0.53, height * 0.035), pg.SRCALPHA)
        self.resources_rect = self.resouces_surface.get_rect(topleft=(0, 0))
        self.draw_rounded_rect(self.resouces_surface, self.hud_colour, self.resouces_surface.get_rect(), border_radius=20)

        # building hud
        self.build_surface = pg.Surface((width * 0.09, height * 0.9), pg.SRCALPHA)
        self.build_rect = self.build_surface.get_rect(topleft=(self.width * 0.89, self.height * 0.05))
        self.draw_rounded_rect(self.build_surface, self.hud_colour, self.build_surface.get_rect(), border_radius=70)

        # demolish button
        button_size = (int(self.width * 0.04), int(self.height * 0.07))
        self.demolish_surface = pg.Surface(button_size, pg.SRCALPHA)
        self.demolish_rect = self.demolish_surface.get_rect(topleft=(self.width * 0.02, self.height * 0.88))
        self.demolish_color = (0, 0, 0, 240)  # color of demolish thing
        self.draw_rounded_rect(self.demolish_surface, self.demolish_color, self.demolish_surface.get_rect(), border_radius=20)

        # deforest button
        deforest_button_size = (int(self.width * 0.04), int(self.height * 0.07))
        self.deforest_surface = pg.Surface(deforest_button_size, pg.SRCALPHA)
        self.deforest_rect = self.deforest_surface.get_rect(topleft=(self.width * 0.08, self.height * 0.88))
        self.deforest_color = (0, 0, 0, 240)  # color of deforest button

        self.draw_rounded_rect(self.deforest_surface, self.deforest_color, self.deforest_surface.get_rect(), border_radius=20)

        # select hud
        self.select_surface = pg.Surface((width * 0.3, height * 0.2), pg.SRCALPHA)
        self.select_rect = self.select_surface.get_rect(topleft=(self.width * 0.35, self.height * 0.79))
        self.draw_rounded_rect(self.select_surface, self.hud_colour, self.select_surface.get_rect(), border_radius=15)

        self.images = self.load_images()
        self.tiles = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None

    def draw_rounded_rect(self, surface, color, rect, border_radius=10):
        pg.draw.rect(surface, color, rect, border_radius=border_radius)

    def create_build_hud(self):
        render_pos_x = self.width * 0.91 + 10
        object_height = self.build_surface.get_height() // 10

        tiles = []

        # only buildings
        allowed_buildings = ["category_housing", "House", "Big_House", "Villa", "category_services", "Tavern", "Chapel", "Clock", "category_industry", "Treehouse", "Stonemasonry", "Crops", "Fisherman", "Fruitshop", "category_infrastructure", "Marbelpath"]
        for image_name in allowed_buildings:
            image = self.images.get(image_name)
            if image is None:
                continue
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, h=object_height)
            rect = image_scale.get_rect(topleft=(render_pos_x, 0))
            tiles.append({
                "name": image_name,
                "icon": image_scale,
                "image": image,
                "rect": rect,
                "affordable": True
            })

        return tiles

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_action = pg.mouse.get_pressed()

        # scroll with mousewheel
        for event in pg.event.get(pg.MOUSEWHEEL):
            self.scroll_offset -= event.y * self.scroll_speed
            self.scroll_offset = max(0, self.scroll_offset)

        # rightklick undoes
        if mouse_action[2]:
            self.selected_tile = None

        # update position of tiles (scrolling)
        for i, tile in enumerate(self.tiles):
            icon = tile["icon"]
            y = self.height * 0.05 + 40 + i * (icon.get_height() + 10) - self.scroll_offset
            tile_rect = icon.get_rect(topleft=(self.width * 0.91 + 10, y))
            tile["rect"] = tile_rect

            tile["affordable"] = self.resource_manager.is_affordable(tile["name"])

            if tile_rect.collidepoint(mouse_pos) and tile["affordable"]:
                if mouse_action[0]:
                    self.selected_tile = tile

        # click on demolish button
        if self.demolish_rect.collidepoint(mouse_pos):
            if mouse_action[0]:
                # Auswahl auf "demolish" setzen (klein geschrieben)
                self.selected_tile = {"name": "demolish"}

        # click on deforest button
        if self.deforest_rect.collidepoint(mouse_pos):
            if mouse_action[0]:
                self.selected_tile = {"name": "deforest"}

    def draw(self, screen):
        # recource hud
        screen.blit(self.resouces_surface, (self.width * 0.02, self.height * 0.03))

        # build hud (scroll area)
        self.build_surface.fill((0, 0, 0, 0))  # clear
        self.draw_rounded_rect(self.build_surface, self.hud_colour, self.build_surface.get_rect(), border_radius=70)

        for tile in self.tiles:
            icon = tile["icon"].copy()
            if not tile["affordable"]:
                icon.set_alpha(100)
            rel_rect = tile["rect"].copy()
            rel_rect.x -= self.build_rect.x
            rel_rect.y -= self.build_rect.y
            if 0 <= rel_rect.y <= self.build_surface.get_height() - icon.get_height():
                self.build_surface.blit(icon, rel_rect.topleft)

        screen.blit(self.build_surface, self.build_rect.topleft)


        # draw demolish button
        screen.blit(self.demolish_surface, self.demolish_rect.topleft)

        # draw icon of demolish button
        icon = self.images["Demolish"]
        icon_scale = self.scale_image(icon, w=self.demolish_rect.width * 0.5)
        icon_pos = (
            self.demolish_rect.x + (self.demolish_rect.width - icon_scale.get_width()) // 2,
            self.demolish_rect.y + (self.demolish_rect.height - icon_scale.get_height()) // 2
        )
        screen.blit(icon_scale, icon_pos)


        # mask of selected tile (demolish button)
        if self.selected_tile is not None and self.selected_tile["name"] == "demolish":
            pg.draw.rect(screen, (255, 0, 0), self.demolish_rect, 3, border_radius=20)


        # draw deforst button
        screen.blit(self.deforest_surface, self.deforest_rect.topleft)

        deforest_icon = self.images["Deforest"]
        deforest_scale = self.scale_image(deforest_icon, w=self.deforest_rect.width * 0.7)
        deforest_pos = (
            self.deforest_rect.x + (self.deforest_rect.width - deforest_scale.get_width()) // 2,
            self.deforest_rect.y + (self.deforest_rect.height - deforest_scale.get_height()) // 2
        )
        screen.blit(deforest_scale, deforest_pos)

        # mask selected tile (deforest button)
        if self.selected_tile is not None and self.selected_tile["name"] == "deforest":
            pg.draw.rect(screen, (0, 255, 0), self.deforest_rect, 3, border_radius=20)


        # select hud
        if self.examined_tile is not None:
            w, h = self.select_rect.width, self.select_rect.height
            screen.blit(self.select_surface, self.select_rect.topleft)
            img = self.examined_tile.image.copy()
            img_scale = self.scale_image(img, h=h * 0.6)
            screen.blit(img_scale, (self.select_rect.left + 10, self.select_rect.top + 40))
            draw_text(screen, self.examined_tile.name, 40, (255, 255, 255), self.select_rect.topleft)


        # show recources
        pos_x = self.width * 0.03
        pos_y = self.height * 0.026
        text_size = int(self.height * 0.03)
        for resource, val in self.resource_manager.resources.items():
            draw_text(screen, f"{resource}: {val}", text_size, (255, 255, 255), (pos_x, pos_y))
            pos_x += self.width * 0.1


        # villigers
        pop_txt = f"Villiger: {int(self.resource_manager.get_effective_population())}"
        draw_text(screen, pop_txt, text_size, (255, 255, 255), (pos_x, pos_y))
        pos_x += self.width * 0.1


        # happiness
        happy_txt = f"Happiness: {int(self.resource_manager.happiness)}%"
        draw_text(screen, happy_txt, text_size, (255, 255, 255), (pos_x, pos_y))



    def load_images(self):
        House = pg.image.load("assets/graphics/buttons0001.png").convert_alpha()
        Big_House = pg.image.load("assets/graphics/buttons0010.png").convert_alpha()
        Villa = pg.image.load("assets/graphics/buttons0002.png").convert_alpha()
        Tavern = pg.image.load("assets/graphics/buttons0003.png").convert_alpha()
        Chapel = pg.image.load("assets/graphics/buttons0005.png").convert_alpha()
        Clock = pg.image.load("assets/graphics/buttons0006.png").convert_alpha()
        Treehouse = pg.image.load("assets/graphics/buttons0011.png").convert_alpha()
        Stonemasonry = pg.image.load("assets/graphics/buttons0012.png").convert_alpha()
        Crops = pg.image.load("assets/graphics/buttons0013.png").convert_alpha()
        Fisherman = pg.image.load("assets/graphics/buttons0015.png").convert_alpha()
        Fruitshop = pg.image.load("assets/graphics/buttons0016.png").convert_alpha()
        Marbelpath = pg.image.load("assets/graphics/buttons0021.png").convert_alpha()

        demolish_icon = pg.image.load("assets/graphics/demolish.png").convert_alpha()
        deforest_icon = pg.image.load("assets/graphics/deforest.png").convert_alpha()

        category_housing = pg.image.load("assets/graphics/category01.png").convert_alpha()
        category_services = pg.image.load("assets/graphics/category02.png").convert_alpha()
        category_industry = pg.image.load("assets/graphics/category03.png").convert_alpha()
        category_infrastructure = pg.image.load("assets/graphics/category04.png").convert_alpha()

        images = {
            "House": House,
            "Big_House": Big_House,
            "Villa": Villa,
            "Tavern": Tavern,
            "Chapel": Chapel,
            "Clock": Clock,
            "Treehouse": Treehouse,
            "Stonemasonry": Stonemasonry,
            "Crops" : Crops,
            "Fisherman" : Fisherman,
            "Fruitshop" : Fruitshop,
            "Marbelpath" : Marbelpath,

            "Demolish": demolish_icon,
            "Deforest": deforest_icon,

            "category_housing": category_housing,
            "category_services": category_services,
            "category_industry": category_industry,
            "category_infrastructure": category_infrastructure,

        }

        return images

    def scale_image(self, image, w=None, h=None):
        if w is None and h is None:
            return image
        elif w is None:
            scale = h / image.get_height()
            w = scale * image.get_width()
        elif h is None:
            scale = w / image.get_width()
            h = scale * image.get_height()
        return pg.transform.scale(image, (int(w), int(h)))