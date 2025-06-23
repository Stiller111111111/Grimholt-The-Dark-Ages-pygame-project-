import pygame as pg
import random
import noise
from .settings import TILE_SIZE
from .buildings import Treehouse, Stonemasonry, House, Big_House, Villa, Tavern, Chapel, Clock, Crops, Marbelpath, Fisherman, Fruitshop


class World:

    def __init__(self, resource_manager, entities, hud, grid_length_x, grid_length_y, width, height):
        self.resource_manager = resource_manager
        self.entities = entities
        self.hud = hud

        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height

        self.perlin_scale = grid_length_x / 2

        # area for flor tiles (double width for isometric offset)
        self.grass_tiles = pg.Surface(
            (grid_length_x * TILE_SIZE * 2, grid_length_y * TILE_SIZE + 2 * TILE_SIZE)
        ).convert_alpha()

        # load all images
        self.tiles = self.load_images()

        # create world infrastructure (2D-Array with tile info)
        self.world = self.create_world()

        # parralel array for buildings
        self.buildings = [[None for _ in range(self.grid_length_y)] for _ in range(self.grid_length_x)]

        # temporary view off selected tile when placing
        self.temp_tile = None

        # position of examined tile (examining objects)
        self.examine_tile = None

        # state of mouseclick, only reacts once per click
        self.left_mouse_was_pressed = False
        self.right_mouse_was_pressed = False

        self.generate_sand_around_water()


    def update(self, camera):
        mouse_pos = pg.mouse.get_pos()
        mouse_buttons = pg.mouse.get_pressed()

        left_pressed = mouse_buttons[0]
        right_pressed = mouse_buttons[2]

        # right click for undoing selection
        if right_pressed and not self.right_mouse_was_pressed:
            self.examine_tile = None
            self.hud.examined_tile = None

        self.temp_tile = None

        # checks if demolish mode is acctive
        demolish_mode = (
            self.hud.selected_tile is not None and
            isinstance(self.hud.selected_tile, dict) and
            self.hud.selected_tile.get("name", "").lower() == "demolish"
        )
        deforest_mode = (
            self.hud.selected_tile is not None and
            isinstance(self.hud.selected_tile, dict) and
            self.hud.selected_tile.get("name", "").lower() == "deforest"
        )

        grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)

        building_name = None
        if self.hud.selected_tile is not None and isinstance(self.hud.selected_tile, dict):
            building_name = self.hud.selected_tile.get("name")

        # checks if you can place tile (not in gui), save tile name
        can_place = self.can_place_tile(grid_pos, building_name)

        if self.hud.selected_tile is not None and not demolish_mode and not deforest_mode:
            if isinstance(self.hud.selected_tile, dict) and "image" in self.hud.selected_tile:
                img = self.hud.selected_tile["image"].copy()
                img.set_alpha(100)  # transparency

                render_pos = self.world[grid_pos[0]][grid_pos[1]]["render_pos"]
                iso_poly = self.world[grid_pos[0]][grid_pos[1]]["iso_poly"]
                collision = self.world[grid_pos[0]][grid_pos[1]]["collision"]

                # checks if your allowed to place stuff (no collisin and other stuff)
                valid_position = not collision and can_place

                self.temp_tile = {
                    "image": img,
                    "render_pos": render_pos,
                    "iso_poly": iso_poly,
                    "collision": collision,
                    "valid_position": valid_position
                }

                # build if left ,ousebutton an valid positioning
                if left_pressed and not self.left_mouse_was_pressed and valid_position:
                    name = self.hud.selected_tile["name"]

                    # create building object
                    ent = None
                    if name == "House":
                        ent = House(render_pos, self.resource_manager)
                    elif name == "Big_House":
                        ent = Big_House(render_pos, self.resource_manager)
                    elif name == "Villa":
                        ent = Villa(render_pos, self.resource_manager)
                    elif name == "Tavern":
                        ent = Tavern(render_pos, self.resource_manager)
                    elif name == "Chapel":
                        ent = Chapel(render_pos, self.resource_manager)
                    elif name == "Clock":
                        ent = Clock(render_pos, self.resource_manager)
                    elif name == "Treehouse":
                        ent = Treehouse(render_pos, self.resource_manager)
                    elif name == "Stonemasonry":
                        ent = Stonemasonry(render_pos, self.resource_manager)
                    elif name == "Crops":
                        ent = Crops(render_pos, self.resource_manager)
                    elif name == "Marbelpath":
                        ent = Marbelpath(render_pos, self.resource_manager)
                    elif name == "Fisherman":
                        ent = Fisherman(render_pos, self.resource_manager)
                    elif name == "Fruitshop":
                        ent = Fruitshop(render_pos, self.resource_manager)


                    if ent is not None:
                        self.entities.append(ent)
                        self.buildings[grid_pos[0]][grid_pos[1]] = ent
                        self.world[grid_pos[0]][grid_pos[1]]["collision"] = True

                    self.hud.selected_tile = None
            else:
                self.temp_tile = None


        elif deforest_mode and can_place:
            # remove tree if tere and left mousebutton
            tile_data = self.world[grid_pos[0]][grid_pos[1]]
            if left_pressed and not self.left_mouse_was_pressed and tile_data["tile"] == "tree":
                # remove tree
                tile_data["tile"] = ""
                tile_data["collision"] = False

                # add 5 wood
                self.resource_manager.add("Wood", 5)


        elif demolish_mode and can_place:
            # buildings remove
            building = self.buildings[grid_pos[0]][grid_pos[1]]
            if left_pressed and not self.left_mouse_was_pressed and building is not None:
                if building.name.lower() in [
                    "house", "big_house", "villa", "tavern", "chapel", "clock", "treehouse", "stonemasonry", "crops", "marbelpath", "fisherman", "fruitshop"
                ]:
                    # get recources back (50%) + villiger reduction
                    self.resource_manager.refund_resources_and_population(building.name)

                    # remove building out of world
                    self.entities.remove(building)
                    self.buildings[grid_pos[0]][grid_pos[1]] = None
                    self.world[grid_pos[0]][grid_pos[1]]["collision"] = False

        else:
            # no mode active: leftclocl = building info
            if can_place:
                building = self.buildings[grid_pos[0]][grid_pos[1]]
                if left_pressed and not self.left_mouse_was_pressed and building is not None:
                    self.examine_tile = grid_pos
                    self.hud.examined_tile = building

        # save status of mouse for next loop
        self.left_mouse_was_pressed = left_pressed
        self.right_mouse_was_pressed = right_pressed


    def draw(self, screen, camera):
        # draw floor
        screen.blit(self.grass_tiles, (camera.scroll.x, camera.scroll.y))

        # draw all tiles
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                tile_data = self.world[x][y]
                render_pos = tile_data["render_pos"]
                tile = tile_data["tile"]

                # draw tiles (rock, tree, etc.)
                if tile != "":
                    screen.blit(
                        self.tiles[tile],
                        (
                            render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                            render_pos[1] - (self.tiles[tile].get_height() - TILE_SIZE) + camera.scroll.y
                        )
                    )

                # draw sand
                if tile != "":
                    screen.blit(
                        self.tiles[tile],
                        (
                            render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                            render_pos[1] - (self.tiles[tile].get_height() - TILE_SIZE) + camera.scroll.y
                        )
                    )

                # draw buildings
                building = self.buildings[x][y]
                if building is not None:
                    screen.blit(
                        building.image,
                        (
                            render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                            render_pos[1] - (building.image.get_height() - TILE_SIZE) + camera.scroll.y
                        )
                    )

                    # mark examined building
                    if self.examine_tile == (x, y):
                        mask = pg.mask.from_surface(building.image).outline()
                        mask = [
                            (mx + render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                             my + render_pos[1] - (building.image.get_height() - TILE_SIZE) + camera.scroll.y)
                            for mx, my in mask
                        ]
                        pg.draw.polygon(screen, (255, 255, 255), mask, 3)

        # darw preview tile  (transpernecy when building)
        if self.temp_tile is not None:
            iso_poly = self.temp_tile["iso_poly"]
            iso_poly = [(x + self.grass_tiles.get_width() / 2 + camera.scroll.x, y + camera.scroll.y) for x, y in iso_poly]

            # red marking if kollision or not able to place
            color = (255, 255, 255) if self.temp_tile.get("valid_position", False) else (255, 0, 0)
            pg.draw.polygon(screen, color, iso_poly, 3)

            render_pos = self.temp_tile["render_pos"]
            screen.blit(
                self.temp_tile["image"],
                (
                    render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                    render_pos[1] - (self.temp_tile["image"].get_height() - TILE_SIZE) + camera.scroll.y
                )
            )


    def create_world(self):
        world = []

        for grid_x in range(self.grid_length_x):
            col = []
            for grid_y in range(self.grid_length_y):
                tile = self.grid_to_world(grid_x, grid_y)
                col.append(tile)

                # traw floor (block)
                render_pos = tile["render_pos"]
                self.grass_tiles.blit(self.tiles["block"], (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))
            world.append(col)

        return world


    def grid_to_world(self, grid_x, grid_y):
        # posiion of rect in cordinates (kartesischen)
        rect = [
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE),
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE)
        ]

        # make it isometric cordinates
        iso_poly = [self.cart_to_iso(x, y) for x, y in rect]

        minx = min(x for x, y in iso_poly)
        miny = min(y for x, y in iso_poly)

        # perlin noise value for nature
        perlin = 100 * noise.pnoise2(grid_x / self.perlin_scale, grid_y / self.perlin_scale)

        r = random.randint(1, 1000)

        # locate water
        if perlin <= -10:
            tile = "water"
        elif perlin >= 30:
            tile = "tree"
        else:
            if r == 1:
                tile = "tree"
            elif r == 2:
                tile = "rock"
            else:
                tile = ""

        collision = tile != ""

        return {
            "grid": [grid_x, grid_y],
            "cart_rect": rect,
            "iso_poly": iso_poly,
            "render_pos": [minx, miny],
            "tile": tile,
            "collision": collision
        }
    
    def generate_sand_around_water(self):
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                tile_data = self.world[x][y]
                if tile_data["tile"] == "water":
                    # check tiles around it
                    for nx in range(max(0, x-1), min(self.grid_length_x, x+2)):
                        for ny in range(max(0, y-1), min(self.grid_length_y, y+2)):
                            if (nx, ny) != (x, y):
                                neighbor_tile = self.world[nx][ny]
                                # make tile sand if near water wenn not blocked by water or other stuff
                                if neighbor_tile["tile"] == "":
                                    neighbor_tile["tile"] = "sand"
                                    neighbor_tile["collision"] = False  # can build on sand


    def cart_to_iso(self, x, y):
        iso_x = x - y
        iso_y = (x + y) / 2
        return iso_x, iso_y
    

    
    def has_adjacent_rock(self, grid_pos):
        x, y = grid_pos
        neighbors = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1)
        ]
        for nx, ny in neighbors:
            if 0 <= nx < self.grid_length_x and 0 <= ny < self.grid_length_y:
                if self.world[nx][ny]["tile"] == "rock":
                    return True
        return False
    
    def has_adjacent_tree(self, grid_pos):
        x, y = grid_pos
        neighbors = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1)
        ]
        for nx, ny in neighbors:
            if 0 <= nx < self.grid_length_x and 0 <= ny < self.grid_length_y:
                if self.world[nx][ny]["tile"] == "tree":
                    return True
        return False
    
    def has_adjacent_water(self, grid_pos):
        x, y = grid_pos
        neighbors = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1)
        ]
        for nx, ny in neighbors:
            if 0 <= nx < self.grid_length_x and 0 <= ny < self.grid_length_y:
                if self.world[nx][ny]["tile"] == "water":
                    return True
        return False
    
    def has_marbelpath_in_radius(self, grid_pos, radius=4):
        x, y = grid_pos
        for nx in range(x - radius, x + radius + 1):
            for ny in range(y - radius, y + radius + 1):
                if 0 <= nx < self.grid_length_x and 0 <= ny < self.grid_length_y:
                    building = self.buildings[nx][ny]
                    if building is not None and building.name.lower() == "marbelpath":
                        return True
        return False



    def mouse_to_grid(self, x, y, scroll):
        # calculate mouse -> cordinates (offset and remove cmaera)
        world_x = x - scroll.x - self.grass_tiles.get_width() / 2
        world_y = y - scroll.y

        # recalculate to map cordinates (kartesische) (by cart_to_iso)
        cart_y = (2 * world_y - world_x) / 2
        cart_x = cart_y + world_x

        grid_x = int(cart_x // TILE_SIZE)
        grid_y = int(cart_y // TILE_SIZE)

        return grid_x, grid_y


    def load_images(self):
        block = pg.image.load("assets/graphics/block.png").convert_alpha()
        House = pg.image.load("assets/graphics/building01.png").convert_alpha()
        Big_House = pg.image.load("assets/graphics/building10.png").convert_alpha()
        Villa = pg.image.load("assets/graphics/building02.png").convert_alpha()
        Tavern = pg.image.load("assets/graphics/building03.png").convert_alpha()
        Chapel = pg.image.load("assets/graphics/building05.png").convert_alpha()
        Clock = pg.image.load("assets/graphics/building06.png").convert_alpha()
        Treehouse = pg.image.load("assets/graphics/building11.png").convert_alpha()
        Stonemasonry = pg.image.load("assets/graphics/building12.png").convert_alpha()
        Crops = pg.image.load("assets/graphics/building13.png").convert_alpha()
        Fisherman = pg.image.load("assets/graphics/building15.png").convert_alpha()
        Fruitshop = pg.image.load("assets/graphics/building16.png").convert_alpha()
        Marbelpath = pg.image.load("assets/graphics/building21.png").convert_alpha()

        tree = pg.image.load("assets/graphics/tree.png").convert_alpha()
        rock = pg.image.load("assets/graphics/rock.png").convert_alpha()
        water = pg.image.load("assets/graphics/water.png").convert_alpha()
        sand = pg.image.load("assets/graphics/sand.png").convert_alpha()

        return {
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

            "tree": tree,
            "rock": rock,
            "block": block,
            "water": water,
            "sand": sand,
        }


    def can_place_tile(self, grid_pos, building_name=None):
        # check if mouse over gui
        mouse_on_panel = False
        mouse_pos = pg.mouse.get_pos()
        for rect in [self.hud.resources_rect, self.hud.build_rect, self.hud.select_rect]:
            if rect.collidepoint(mouse_pos):
                mouse_on_panel = True
                break

        # check if in map
        world_bounds = (0 <= grid_pos[0] < self.grid_length_x) and (0 <= grid_pos[1] < self.grid_length_y)
        if not world_bounds or mouse_on_panel:
            return False

        # check for stonemaconary near rock
        if building_name == "Stonemasonry":
            if not self.has_adjacent_rock(grid_pos):
                return False
            
        # check for treehouse near tree
        if building_name == "Treehouse":
            if not self.has_adjacent_tree(grid_pos):
                return False
            
        # check for treehouse near tree
        if building_name == "Fisherman":
            if not self.has_adjacent_water(grid_pos):
                return False
    
        # check if near marbelpath
        if building_name in ["House", "Big_House", "Villa", "Tavern", "Chapel", "Clock", "Fruitshop", "Crops", "Stonemasonry", "Treehouse", "Fisherman"]:
            if not self.has_marbelpath_in_radius(grid_pos, radius=4):
                return False

        return True