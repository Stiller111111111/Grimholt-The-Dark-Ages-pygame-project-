import pygame as pg

class ResourceManager:

    def __init__(self):

        # resources
        self.resources = {
            "Wood": 10,
            "Stone": 10,
            "Food" : 50
        }

        # costs
        self.costs = {
            "Treehouse": {"Wood": 7, "Stone": 0},
            "House": {"Wood": 5, "Stone": 0},
            "Big_House": {"Wood": 20, "Stone": 10},
            "Villa": {"Wood": 40, "Stone": 20},
            "Tavern": {"Wood": 7, "Stone": 5},
            "Chapel": {"Wood": 80, "Stone": 50},
            "Clock": {"Wood": 120, "Stone": 100},
            "Stonemasonry": {"Wood": 20, "Stone": 0},
            "Crops": {"Wood": 5, "Stone": 0},
            "Fruitshop" : {"Wood": 20, "Stone": 10},
            "Fisherman": {"Wood": 40, "Stone": 30},
            "Marbelpath": {"Wood": 5, "Stone": 2},
        }

        # population data
        self.population = 10  # population at startz (not effected by happines)
        self.happiness = 60  # happiness at start

        self.population_per_building = {
            "House": 5,
            "Big_House": 15,
        }

    def get_effective_population(self):
        # population effected by happiness
        return int(self.population * (int(self.happiness) / 100))

    def apply_cost_to_resource(self, building):
        for resource, cost in self.costs[building].items():
            self.resources[resource] -= cost

        # add villigers if building has villigers
        if building in self.population_per_building:
            self.population += self.population_per_building[building]

    def add(self, resource, amount):
        if resource in self.resources:
            self.resources[resource] += amount

    def is_affordable(self, building):
        if building not in self.costs:
            return False
        for resource, cost in self.costs[building].items():
            if cost > self.resources.get(resource, 0):
                return False
        return True

    def refund_resources_and_population(self, building, refund_ratio=0.5):
        # give back recources (partually)
        for resource, cost in self.costs.get(building, {}).items():
            refund = int(cost * refund_ratio)
            self.resources[resource] += refund

        # remove villiger if building gives them
        if building in self.population_per_building:
            self.population -= self.population_per_building[building]
            self.population = max(0, self.population)

    def update(self):
        # happiness goes down
        if self.happiness < 0:
            self.happiness = 0
        if self.happiness > 100:
            self.happiness = 100

        # when no food happiness goes down
        if self.resources["Food"] == 0:
            self.happiness -= 0.01 
            if self.happiness < 0:
                self.happiness = 0