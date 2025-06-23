import pygame as pg

class Building:
    def __init__(self, pos, resource_manager, image_path, name):
        image = pg.image.load(image_path)
        self.image = image
        self.name = name
        self.rect = self.image.get_rect(topleft=pos)
        self.resource_manager = resource_manager
        self.resource_manager.apply_cost_to_resource(self.name)
        self.resource_cooldown = pg.time.get_ticks()

    # def update(self):
    #     # Default: macht nichts, kann überschrieben werden
    #     pass


class House(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building01.png", "House")


class Big_House(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building10.png", "Big_House")


class Marbelpath(Building):
    def __init__(self, pos, recource_manager):
        super().__init__(pos, recource_manager, "assets/graphics/building21.png", "Marbelpath")


class Villa(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building02.png", "Villa")


class Tavern(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building03.png", "Tavern")


class Chapel(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building05.png", "Chapel")


class Clock(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building06.png", "Clock")


class Treehouse(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building11.png", "Treehouse")

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2000:
            self.resource_manager.resources["Wood"] += 3
            self.resource_cooldown = now

class Stonemasonry(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building12.png", "Stonemasonry")

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2000:
            self.resource_manager.resources["Stone"] += 1
            self.resource_cooldown = now

class Crops(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building13.png", "Crops")

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2000:
            self.resource_manager.resources["Food"] += 1
            self.resource_cooldown = now

class Fisherman(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building15.png", "Fisherman")

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2000:
            self.resource_manager.resources["Food"] += 10
            self.resource_cooldown = now

class Fruitshop(Building):
    def __init__(self, pos, resource_manager):
        super().__init__(pos, resource_manager, "assets/graphics/building16.png", "Fruitshop")

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2000:
            self.resource_manager.resources["Food"] += 4
            self.resource_cooldown = now