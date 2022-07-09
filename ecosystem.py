#imports
import math
import random
import sys
import concurrent.futures
from utils import *
import os

Executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)
#sys.setrecursionlimit(30) #for troubleshooting the recursion problems

#the class for the things that Rabbits eat
class Shrub():
    def __init__(self, pos):
        self.pos = pos
        self.size = random.randint(0,3)

    def __str__(self):
        return "Shrub at " + str(self.pos)

"""
#This is the main world class
the map is made up of mini lists: [x, y, z, type], where type is what the thing is.
the world is made up of sixteen by sixteen chunks, thus all world borders must be divisible by sixteen
"""
class World():
    def __init__(self, world_width=256, world_length=256, world_height=64):
        self.map = [] 
        self.world_width = world_width #this is the x
        self.world_length = world_length #this is the y
        self.world_height = world_height #this is the z

        #establing the path to the ./chunks directory
        cwd = os.getcwd()
        pot_chunks = os.listdir(cwd+"/chunks/")

        #for all the chunks that need to be in the world; this is why the all the world borders must be divisible by sixteen
        for x in range(int(world_width/16)):
            for y in range(int(world_length/16)):
                #picking the chunk out of the chunks directory
                while True:
                    chunk_choice = random.choice(pot_chunks)
                    #making sure that the chunk selected is not the README
                    if chunk_choice != "README.txt":
                        break

                #establishing the list of chunks to be used
                chunk_file = open(cwd + "/chunks/" + chunk_choice, "r")
                chunk = chunk_file.read()
                pos_list = chunk.split("\n")
                chunk_file.close()

                #we need to offset the x and y according to how many chunks have already been put in
                x_offset = x*16
                y_offset = y*16

                #for every position in the chunk's position list, except the last because that will be "" because of the way that the file is
                for pos in pos_list[:-1]:
                    #everything in the pos_list is still a string, so we make it not a string
                    po = pos.split(",") #the splitting of the string. This will create a list of mini strings of the coordinates and the type
                    p = [] #this will be the list that we pull the data from to set the type
                    for thing in range(len(po)): #for each entry in p
                        if thing != 3: #if it is not the type (the type is at po[3])
                            p.append(int(po[thing].strip())) #taking away the spaces and then converting to int, then adding to p
                        else:
                            sp = po[thing].strip() #we just are stripping off the spaces
                            #if it something that we have a class for, that will not be initialized later
                            if sp == "Shrub":
                                p.append(Shrub([int(po[0]), int(po[1]), int(po[2])])) #we are adding in a random shrub
                            p.append(sp)
                    #setting the type. p is now a list in form [x, y, z, type], so we grab those elements and put them into the form needed for the set_type function
                    self.set_type([p[0] + x_offset, p[1] + y_offset, p[2]], p[3])

    def search(self, _min, _max, search_object, prior_recurses=0):
        """takes a minimum and maximum and search object and prior_recurses. 
            We then do a binary search of self.map for a specific point and return a list: [successful, midpoint]
                where successful is 0 if successful and 1 if not, and midpoint is the midpoint that we are at
        _min is the minimum, _max is the maximum
        search_object is what we are looking for
        prior_recurses is so we know when we are pointlessly recursing
        """

        #the establishing of the midpoint
        midpoint = int((_min + _max)/2)

        #if the map does not exist yet. If this happens we need to return the midpoint, which is in this, case 0
        #if we do not do this here, then we get a domain error when we try to do math.log2(len(self.map)) because we cannot take the log2 of 0
        if len(self.map) == 0:
            return [1, midpoint] #we need to return the 1 part so that the get_type and set_type functions know that something is wrong
        
        if prior_recurses >= math.log2(len(self.map))+1:
            return [1, midpoint+1] #we need to return the 1 part so that the get_type and set_type functions know that something is wrong

        #adding another recursion
        recurses = prior_recurses + 1
        #making the midlist
        mid_list = self.map[midpoint]
        
        #we compare the lists; compare_lists will return "list1" if the first list is greater, and "list2" if the second list is greater. It will return "equal" if they are equal
        res = compare_lists(mid_list, search_object)
        if res == "list1":
            #this means that the list index for the search_object is below the midpoint
            return self.search(_min, midpoint, search_object, recurses)
        elif res == "list2":
            #this means that the list index for the search_object is above the midpoint
            return self.search(midpoint, _max, search_object, recurses)
        elif res == "equal":
            #this means that they are equal
            return [0, midpoint] #we return the 0 part so that the functions know that they are equal
        
    def get_type(self, coords):
        """requires a list of coords and returns the type of object in that location"""
        pos = self.search(0, len(self.map), coords) #we are using the search function to come up with the number
        if pos[0] == 0: #if the search function successfully finds the point
            c_list = self.map[pos[1]]
            return c_list[3]
        elif pos[0] == 1: #if the point is not found
            return "Location not found."

    def set_type(self, coords, new_type):
        """requires a list of coods, and the new_type. It sets the location indicated by the coords to be the new_type"""
        pos = self.search(0, len(self.map), coords) #we are using the search function to come up with the number

        if pos[0] == 0: #the search function found the position so we just reassign the type and reinsert it
            c_list = self.map.pop(pos[1]) #'coordinate list'. We are also removing it from the self.map list
            c_list[3] = new_type #the third entry is the type, which we are changing
            self.map.insert(pos[1], c_list)
        elif pos[0] == 1: #search function didn't find the position so we reassign it
            c_list = [coords[0], coords[1], coords[2], new_type] #coordinate list
            mp = pos[1]
            for x in range(mp-2, mp+2):
                if len(self.map) > x and x >= 0:
                    pos_list = self.map[x]
                    if pos_list[0] == coords[0] and pos_list[1] == coords[1]:
                        if pos_list[2] < coords[2]:
                            mp = x+1
            self.map.insert(mp, c_list)
 
    def delete_pos(self, coords):
        #using the search function to come up with the number
        pos = self.search(0, len(self.map), coords)
        if pos[0] == 0:
            self.map.pop(pos[1])
        elif pos[0] == 1:
            print("No position found. (World.delete_pos)\nMAP:")
            mp = pos[1]
            for x in range((mp-5), (mp+5)):
                print(x, "::", self.map[x])

#the establishment of the world. This needs to be done here, because it needs to be accessed by all classes and such
world = World(256, 256, 64)
animal_list = []

class Animal():
    def __init__(self, genetics=[1, 1, 1, 1], pos=[0, 0, 0], name="no_name"):
        #initalizing the position. We set it in the world
        self.pos = pos
        world.set_type(self.pos, self)

        #adding it to the list of animals
        animal_list.append(self)

        #self.alive. This is for telling the main() function whether to run this animal's action code or not. If it is true than it will, if not, it won't
        self.alive = True
        self.health = 100 #this may be changed in the individual classes for the animal

        #the way that the animal is pointing. This is in degrees, which often causes some confusion because everything else needs radians
        self.alignment = [0, 0]

        #default traits of the animal
        default_speed = 1
        default_vision_arc = 120
        default_vision_length = 128
        default_attractiveness = 1

        #the gender of the animal
        if random.randint(1,10)%2 == 1:
            self.gender = "male"
        else:
            self.gender = "female"

        #misc
        self.age = 0
        self.name = name
        self.genetics = genetics
        
        #the mate and the chosen_water
        self.mate = None
        self.chosen_water = None
        self.target = None

        #the list of types of the things that the animal should be concerned about and its type
        #these should all be reassigned in the individual animal class __init__
        self.type = Animal
        self.prey_type_list = []
        self.predator_type_list = []

        #the list of things that the animal can see
        self.mate_list = []
        self.prey_list = []
        self.water_list = []
        self.obstacle_list = [] #obstacle list is anything that we don't recognize, which should be only ground
        self.predator_list = []

        #the active status and objective of the animal
        self.active = False
        self.objective = ""
        self.tasks = []

        #the driving forces of the animal
        self.hunger = 0
        self.thirst = 0
        self.arousal = 0

        #the tolerance of the animal
        self.hunger_threshold = 0.3
        self.thirst_threshold = 0.3
        self.arousal_threshold = 0.2
        
        #the critical level at which the animal will focus on that, in absence of something better to do. ie if the animal is looking for a mate at this point, it will stop and do something else
        self.critical_hunger = 0.7
        self.critical_thirst = 0.7

        #how much we add to the hunger/thirst/arousal variables every frame
        self.hunger_add = 0.01
        self.thirst_add = 0.02
        self.arousal_add = 0.01
        
        #the damages for various things, most of these will be reassigned
        self.attack_damage = 0 #this is how much damage an animal will do when attacking another animal
        #how much damage starving or dying of thirst will do
        self.hunger_damage = 20
        self.thirst_damage = 20

        #gene-influnced traits
        self.speed = default_speed * genetics[0]
        self.vision_arc = default_vision_arc * genetics[1]
        self.vision_length = default_vision_length * genetics[2]
        self.attractiveness = default_attractiveness * genetics[3]

    def __str__(self):
        return self.name + "-(of type: " + str(self.type) + ", of gender: " + self.gender + ", at " + str(self.pos) + ", age: " + str(self.age) + ")"

    def Action(self):
        """We look at the things that we have to do and then choose which is the most pressing priority"""
        #checking if we should be taking damage
        if self.hunger > 1:
            self.health -= self.hunger_damage
        if self.thirst > 1:
            self.health -= self.thirst_damage

        #making the animal see
        self.see()

        #printing stats #FIXME diagnostic
        print("\n" + self.__str__() + " be doing action.")
        print("   " + self.name + "'s objective:", self.objective)
        print("   " + self.name + "'s stats:")
        print("     " + self.name + "'s health:", self.health)
        print("     " + self.name + "'s hunger:", self.hunger)
        print("     " + self.name + "'s thirst", self.thirst)
        print("     " + self.name + "'s arousal", self.arousal)

        #checking if we should be dying we do this after the printing of the stats so we can see our health
        self.life_update()
        if self.alive == False:
            return None #we want to break off the function here because we do not want a dead animal to do anything (obviously)

        #making sure we eat or drink if we need to
        if self.hunger > self.critical_hunger:
            self.active = True
            self.objective = "food"
        elif self.thirst > self.critical_thirst:
            self.active = True
            self.objective = "water"

        if self.active == True:
            if len(self.tasks) > 0:
                self.Do_Task(tasks.pop[0])
            elif self.objective == "water": #if we want water
                print("   " + self.name + "'s chosen water:", self.chosen_water) #diagnostic
                if self.chosen_water == None:
                    self.look_around()
                    self.chosen_water = self.choose_water() #choosing the water to go to. We do this every time so that if there is for some strange reason new water, than we can adjust quickly
                elif find_distance(self.pos, self.chosen_water) < 2: #if we are close enough to drink
                    self.thirst = 0 #ie we have drank the water and are now satisfied
                    self.chosen_water = None #so that we rechose the water next time
                    self.active = False
                    self.objective = ""
                else: #ie we have actually chosen water
                    #moving self towards the chosen water
                    self.move_towards(self.chosen_water)

            elif self.objective == "mate":
                if self.mate == None:
                    self.look_around()
                    pot_mate = self.choose_mate()
                    print(self.name, "tried mating with", pot_mate)

                    if pot_mate != None: #the pot_mate would equal None if there are no potential mates in sight
                        pot_mate = pot_mate[3]
                        acceptance = pot_mate.accept_mate_request(self)

                        if acceptance == True:
                            self.mate = pot_mate #setting our mate to be our potential mate
                            self.mate.mate = self #setting the mate's mate to be self
                            print(self.mate.__str__() + " accepted mate request from " + self.name)

                else:
                    #if we are close enough to our mate we reproduce, otherwise we move toward the mate
                    if find_distance(self.pos, self.mate.pos) < 2: #we need the distance to be less than 2 not 1 because the distance 0,0,0 and 1,1,1 is ~1.7
                        self.reproduce() #this will do all the fancy genetics and name stuff

                        #we have just successfully mated, theoretically, so we reset all the atributes of both self, and self.mate
                        self.active = False
                        self.mate.active = False
                        self.objective = ""
                        self.mate.objective = ""
                        self.arousal = 0
                        self.mate.arousal = 0
                    else:
                        self.move_towards(self.mate.pos)

            elif self.objective == "food":
                self.look_around() #we look around for the nearest food
                self.target = self.choose_prey()
                if self.target != None:
                    print(self.name + "'s chosen food:", self.target, "Distance:", find_distance(self.pos, self.target.pos)) #FIXME diagnostic
                    self.hunt() #this will deal with everything to do with eating, as most things are fairly animal specific

        elif self.hunger > self.thirst and self.hunger > self.hunger_threshold: #if we should be hungry
            self.active = True
            self.objective = "food"

        elif self.thirst > self.hunger and self.thirst > self.thirst_threshold: #if we should be thirsty
            self.active = True
            self.objective = "water"

        elif self.arousal > self.hunger and self.arousal > self.thirst and self.arousal > self.arousal_threshold: #if we should be looking for a mate
            self.active = True
            self.objective = "mate"

        else: #here we move the animal somewhere random
            print(self.name, "did a random move.")

            iters = 0
            while iters < 5: #while we have done this less than 5 times
                s = round(self.speed)
                random_p = [random.randint(0-s,s), random.randint(0-s,s), 0]
                prev_p = vector_k(self.pos)
                random_pos = add_vector(self.pos, random_p)
                if world.get_type(random_pos) == "Location not found.":
                    self.move(random_pos)
                    iters = 6 #breaking the loop
                else:
                    iters += 1

        #time goes on, so the stats do as well :) (hunger, thirst, arousal, age)
        self.hunger += self.hunger_add
        self.thirst += self.thirst_add
        self.arousal += self.arousal_add
        self.age += 1 #how old the Animal is (how many frames it has gone through)

    def see(self):
        """the seeing function:
        we create a vector in the center of the sight cone and then check the angle between it and the vector to another given point in the world.
        if the angle is less than or equal to self.vision_arc/2 we add it to the list
        """
        center_vector = find_angle_vector(self.alignment[0], self.alignment[1], self.vision_length)

        #the lists of stuff that the animal can see
        mate_list = []
        prey_list = []
        predator_list = []
        water_list = []
        obstacle_list = []

        """
        the comparing of the angle between the points
        formula for angle: theta = arccos((x dot y)/ |x|*|y|)
        """
        cv_mag = find_distance(center_vector) #center_vector_magnitude. This is needed for computing theta

        #for each point in the world, we compare it, and if it is within the vision_arc, we put it in its respective list
        for point in world.map:
            done = False #done is for telling if the point is taken or not. If it is not assigned to true by the time we get to the end it will be added to the obstacle list
            if find_distance(self.pos, point) <= self.vision_length and vector_k(self.pos) != vector_k(point):
                coords_vector = [point[0] - self.pos[0], point[1] - self.pos[1], point[2] - self.pos[2]]
                dot_product = Dot_Product(center_vector, coords_vector)

                #finding the angle and converting it to radians
                theta = math.acos(dot_product/(find_distance(coords_vector) * cv_mag)) #by the formula for theta
                deg_theta = rad_deg(theta)

                #if the degree measure is within the vision arc
                if deg_theta <= self.vision_arc/2:
                    _type = point[3]
                    if isinstance(_type, self.type) == True: #if it another one of type: 'self'
                        if _type.gender != self.gender: #if it is the opposite gender, than it is a potential mate
                            mate_list.append(point)
                            done = True

                    for prey in self.prey_type_list: #for prey_type in the prey_type_list
                        if isinstance(_type, prey) == True: #if it is a prey
                            prey_list.append(point)
                            done = True

                    for predator in self.predator_type_list:
                        if isinstance(_type, predator) == True: #if its a predator
                            predator_list.append(point)
                            done = True

                    if _type == "water": #if it is water
                        water_list.append(point)
                        done == True

                    if done == False: #if it is not anything else than it is an obstacle
                        obstacle_list.append(point)

        #establishing the lists of things that the animal sees
        self.mate_list = mate_list
        self.prey_list = prey_list
        self.water_list = water_list
        self.obstacle_list = obstacle_list
        self.predator_list = predator_list

    def look_around(self):
        """sees everything within the vision_length. The animation should be the animal looking around, because that is what it is"""
        #initializing the 'return' lists
        mate_list = []
        prey_list = []
        predator_list = []
        water_list = []
        obstacle_list = []
        
        #we compare the distance to the point and self.vision_length. If the distance is less than the vision_length we can see it
        #we do not compare the degrees because the animal is looking around and so it should see everything
        for point in world.map: #for every point in the map, if it is within the vision distance figure out what it is
            done = False #done is for telling if the point is taken or not. If it is not assigned to true by the time we get to the end it will be added to the obstacle list
            if find_distance(self.pos, point) <= self.vision_length and vector_k(self.pos) != vector_k(point): #if it is within the vision_length and not our current position
                _type = point[3] #the type is stored in the point like so [x, y, z, type]
                if isinstance(_type, self.type) == True: #if it another one of type: 'self'
                    if _type.gender != self.gender: #if it is the opposite gender
                        mate_list.append(point)
                        done = True
                for prey in self.prey_type_list: #for prey_type in the prey_type_list
                    if isinstance(_type, prey) == True: #if it is a prey
                        prey_list.append(point)
                        done = True
                for predator in self.predator_type_list:
                    if isinstance(_type, predator) == True: #if its a predator
                        predator_list.append(point)
                        done = True
                if _type == "water": #if it is water
                    water_list.append(point)
                    done == True
                if done == False: #if it is not anything else than it is an obstacle
                    obstacle_list.append(point)

        #making our findings public
        self.mate_list = mate_list
        self.prey_list = prey_list
        self.predator_list = predator_list
        self.water_list = water_list
        self.obstacle_list = obstacle_list

    def Die(self):
        print("\n"+self.__str__()+" has died.")
        world.delete_pos(self.pos)
        self.alive = False

    def attack(self, target):
        self.target.health -= self.attack_damage
        self.target.life_update() #life_update just checks if the target is dead, without having to run the target's Action() function


    def life_update(self):
        if self.health =< 0:
            self.Die()

    def choose_water(self):
        chosen_water = None
        closest_dist = 0
        for water in self.water_list:
            if closest_dist == 0:
                chosen_water = water
                closest_dist = find_distance(self.pos, water)
            else:
                pot_water_dist = find_distance(self.pos, water)
                if pot_water_dist < closest_dist:
                    chosen_water = water
                    closest_dist = pot_water_dist
        return chosen_water

    def choose_prey(self):
        closest_dist = 0
        chosen_prey = None
        for pot_prey_coords in self.prey_list:
            pot_prey = pot_prey_coords[3] #we do this because the entries in self.prey_list are as follows [x, y, z, prey_object]
            prey_dist = find_distance(self.pos, pot_prey.pos)
            if closest_dist == 0:
                chosen_prey = pot_prey
                closest_dist = prey_dist
            else:
                if prey_dist < closest_dist:
                    chosen_prey = pot_prey
                    closest_dist = prey_dist
        return chosen_prey

    def choose_mate(self):
        """chooses a mate, and returns the chosen mate's coordinates
        Choosing a mate:
            males have no distinction
            females find the male with the largest ratio of attractiveness, speed, and vision
        """
        mate_choice = None
        if self.gender == "male":
            if self.mate_list == []: #ie there are no available mates
                return None
            for pot_mate in self.mate_list: #for all the 'potential mates' in the mate list
                if mate_choice == None:
                    mate_choice = pot_mate
                    mate_distance = find_distance(self.pos, pot_mate)
                else:
                    pot_mate_distance = find_distance(self.pos, pot_mate) #potential_mate_distance. the distance to the potential mate
                    if pot_mate_distance < mate_distance: #if the potential mate is closer than the current mate
                        mate_choice = pot_mate
                        mate_distance = pot_mate_distance
        else:
            if self.mate_list == []: #if the mate list is empty
                return None
            for pot_mate in self.mate_list:
               if mate_choice == None:
                   mate_choice = pot_mate
                   mate_ratio = find_mate_ratio(self, pot_mate[3]) #here we strain out the animal from the coords list
               else:
                    pot_mate_ratio = find_mate_ratio(self, pot_mate[3]) #here we again strain out the animal from the coords list
                    if pot_mate_ratio > mate_ratio: #if the potential mate is better than the other one
                        mate_choice = pot_mate
                        mate_ratio = pot_mate_ratio
        return mate_choice

    def accept_mate_request(self, mate):
        """if the mate meets the standards, then return True, otherwise return False"""
        if self.gender == "male":
            if mate.arousal > self.arousal_threshold:
                return True
            else:
                return False
        if self.gender == "female":
            if self.arousal > self.arousal_threshold:
                #finding the ratio of self, and the potential mate to make sure that the female only mates something better than herself
                self_ratio = find_mate_ratio(self, self)

                #we add the distance to this because the function: find_mate_ratio() subtracts it,
                #which means that if the male is equal, than the female will not want it, which is not what we want
                pot_mate_ratio = find_mate_ratio(self, mate) + find_distance(self.pos, mate.pos)

                #comparing the ratio, or the arousal
                if self_ratio <= pot_mate_ratio:
                    return True
                elif self.arousal >= 1:
                    return True
                else:
                    return False
            else:
                return False
    
    def reproduce(self):
        surr_pts = surrounding_flat_points(self) #surrounding points
        child_pos = []
        for pt in surr_pts:
            if world.get_type(pt) == "Location not found.":
                child_pos = vector_k(pt)
        if child_pos == []:
            print("\n\n\nThere is no avalaible child position, surrounding points:", surr_pts, "\n\n\n")
            raise KeyboardInterrupt

        #the genes for the child
        parent1_genes = [] #the genes that 'self' will pass on
        parent2_genes = [] #the genes that 'mate' will pass on

        #establishing the genes for parent1
        for gene in self.genetics:
            if random.randint(1, 3) == 1:
                #we mutate :)
                multiplier = random.randint(-20, 20)
                increment = gene/100
                gene = gene + (multiplier * increment)
                parent1_genes.append(gene)
            else:
                parent1_genes.append(gene)

        #establishing the genes for parent2
        for gene in self.mate.genetics:
            if random.randint(1, 3) == 1:
                #we mutate :)
                multiplier = random.randint(-20, 20)
                increment = gene/100
                gene = gene + (multiplier * increment)
                parent2_genes.append(gene)
            else:
                parent2_genes.append(gene)

        #averaging the parents genes
        passed_genes = [(parent1_genes[0]+parent2_genes[0])/2, (parent1_genes[1]+parent2_genes[1])/2, (parent1_genes[2]+parent2_genes[2])/2, (parent1_genes[3]+parent2_genes[3])/2]

        #taking the first half of the 1 name and the second half of the other and smashing them together
        parent1_name = self.name[0:round(len(self.name)/2)]
        parent2_name = self.mate.name[int(len(self.mate.name)/2):]
        child_name = parent1_name + parent2_name

        #establishing the child :)
        child = self.type(genetics=passed_genes, pos=child_pos, name=child_name) #self.type stores the class, so this will initiate another object with type self.type
        print("\n" + self.__str__() + " and " + self.mate.__str__() + " gave birth to " + child.name) #FIXME diagnostic

    def Do_Task(self, task):
        """a task is a list with format ["method", method_data]
        with "method" being 'move', etc
        and method_data being whatever data is required.
            For 'move' this is the coordinates
        """
        method = task[0]
        if method == "move":
            #if the method is 'move', then the coords will be held in the task[1]
            self.move(task[1])
        else: #if we do not know the method in the function
            print("Unknown method. Function: parabola_bird.Do_Task")

    def move(self, destination):
        #if the location is empty we move the animal
        if world.get_type(destination) == "Location not found.":
            previous_pos = vector_k(self.pos) #previous position, so we can delete it without deleting our 'self'
            self.pos = vector_k(destination) #manipulating the position, preparing to move the 'self'
            world.set_type(self.pos, self) #the actual moving of the 'self'
            world.delete_pos(previous_pos) #the removing of the old 'self' position from the world.map list

            print("Moved", self.name, "to", destination, "(print statement in function: Animal.move())") #FIXME diagnostic
        else:
            print("Print Statement in Animal.move(); There is something in the way. (dest, dest_type):", destination, world.get_type(destination))
            #for testing
            """
            for x in range(self.pos[0]-2, self.pos[0]+3):
                for y in range(self.pos[1]-2, self.pos[1]+3):
                    for z in range(self.pos[2]-1, self.pos[2]+1):
                        ml = world.search(0, len(world.map), [x, y, z])
                        if ml[0] == 0:
                            print([x, y, z], "::", ml[1], world.map[ml[1]], world.get_type([x, y, z])) #FIXME diagnostic
            """

    def move_towards(self, pos):
        """needs a self animal and a position to move towards
        it moves the self animal toward the position
        """
        #we set the animal pointing toward the thing that it is going toward, and then a draw a vector self.speed units toward the entity
        self.alignment = find_angles(self.pos, pos)
        movement_vector = find_angle_vector(deg_rad(self.alignment[0]), deg_rad(self.alignment[1]), self.speed) #we make a vector as long as the animal's speed so that it moves at the proper speed

        #establishing the place that we will be moving by adding our current position to the movement_vector
        new_pos = add_vector(self.pos, movement_vector)
        rounded_pos = [round(new_pos[0]), round(new_pos[1]), round(new_pos[2])]

        #the actual moving of the animal
        self.move(rounded_pos)


"""
Below is the famed parabola animal class. It is a bird that only dives in parabolas.
genetics = [speed, vision arc, vision length, attractiveness]
these determine the characteristics of a animal
"""
class parabola_bird(Animal):
    def __init__(self, genetics=[1, 1, 1, 1], pos=[0,0,0], name = "no_name"):
        Animal.__init__(self, genetics=genetics, pos=pos, name=name)
        self.type = parabola_bird
        self.prey_type_list = [Fox, Rabbit]
        self.dive_speed = 2 * genetics[1] #this makes it roughly double the normal speed
        self.attack_damage = 100

    def hunt(self):
        """we find food and we get it"""
        #TODO Document this function
        if len(self.tasks) == 0 and self.hunger < self.hunger_threshold: #if we have not assigned the dive path yet or we need to dive again
            positions = self.find_path() #finding the parabola dive path
            if positions != None: #if we have found a good path. (ie the find_path() function has not returned None)
                for pos in positions: #adding all the position to self.tasks
                    self.tasks.append(pos)
            else: #the find_path() function will return None if there is no good path
                print(self.__str__() + " is not able to dive at target", self.target.__str__(), "Print statement in parabola_bird.hunt()") #FIXME diagnostic

        elif find_distance(self.pos, self.target.pos) < 2: #if we are close enough to hit the target
            self.attack(self.target) #we hit the target
            if self.target.alive == False: #if the target is dead than we have eaten.
                self.hunger = 0 #while we have eaten, we are not yet finished with the dive, so we only reset the hunger

        elif len(self.tasks) != 0: #if we have tasks. these will be the positions in the dive
            self.Do_Task(self.tasks.pop(0))

        else: #if there are no tasks than we are done hunting, because we have reached the top of our arc
            #therefore we reset all of our stats, except hunger, because we have already reset that when we attacked the prey
            if self.hunger < self.hunger_threshold: #we need this because we may not have killed the prey, and hence reset our hunger. 
                #We are comparing self.hunger to self.hunger_threshold and not zero, because we have done things since eating, (ie: coming up the dive) and our hunger will be greater than zero, but probably less than hunger_threshold
                self.active = False
                self.objective = ""
                self.target = None

    def find_path(self):
        """find the dive path of the bird and return all the positions in a list"""
        prey_dist = find_flat_distance(self.pos, self.target.pos)
        angles = find_angles(self.pos, self.target.pos)
        hor_deg = angles[0]
        #here we get three potential positions for the end of the parabola. These are all relative to the origin. We will add them to self.pos, and see if they are plausible end points
        pos1 = find_angle_vector(deg_rad(hor_deg), 0, prey_dist*2) #this is straight ahead
        pos2 = find_angle_vector(deg_rad(hor_deg+45), 0, prey_dist) #this is "angle to prey" +45 degrees and then prey_dist forward
        pos3 = find_angle_vector(deg_rad(hor_deg-45), 0, prey_dist) #this is "angle to prey" -45 degrees and then prey_dist forward

        pos_list = [add_vector(self.pos, [round(pos1[0]), round(pos1[1]), round(pos1[2])]), add_vector(self.pos, [round(pos2[0]), round(pos2[1]), round(pos2[2])]), add_vector(self.pos, [round(pos3[0]), round(pos3[1]), round(pos3[2])])]
        for pos in pos_list:
            if 0 < pos[0] < world_width and 0 < pos[1] < world_length and 0 < pos[2] < world_height:
                start = self.pos
                midpoint = self.target.pos
                end = pos
        return None

class Rabbit(Animal):
    def __init__(self, genetics=[1, 1, 1, 1], pos=[0,0,0], name="no_name"):
        Animal.__init__(self, genetics=genetics, pos=pos, name=name)
        self.type = Rabbit
        self.prey_type_list = [Shrub] #while the Rabbit does not technically have prey, having their food as a prey type makes the universal Animal() class able to handle it, and we do not need individual functions for the rabbit
        self.predator_type_list = [Fox, parabola_bird]
    
    def hunt(self):
        """the function that handles all the eating for the Rabbit"""
        #the finding of a target is done in Animal.Action() and this function is only run if we have a target. Therefore it is safe to assume that we have a target
        if find_distance(self.pos, self.target.pos) < 2: #if we are close enough to eat
            #we have 'eaten' so we reset all the stats
            self.hunger = 0
            self.active = False
            self.objective = ""
            self.target = None
        else: #if we are not close enough
            self.move_towards(self.target.pos) #we move closer

class Fox(Animal):
    def __init__(self, genetics=[1, 1, 1, 1], pos=[0, 0, 0], name="no_name"):
        Animal.__init__(self, genetics=genetics, pos=pos, name=name)
        #reassigning the things that need to be reassigned from the Animal class
        self.type = Fox
        self.prey_type_list = [Rabbit]
        self.predator_type_list = [parabola_bird]
        self.attack_damage = 50

    def hunt(self):
        """the function that handles all of the eating stuff for the Fox, assuming that a target is selected in Animal.Action()"""
        if find_distance(self.pos, self.target.pos) < 2: #if we are close enough to attack our target
            self.attack(self.target)
            if self.target.alive == False:
                self.hunger = 0
                self.active = False
                self.objective = ""
                self.target = None
        else:
            self.move_towards(self.target.pos)


def main():
    """
    bird_male = parabola_bird(pos=[39, 39, 25], name="NICK")
    bird_female = parabola_bird(pos=[30, 30, 30], name="OLIVIA")
    bird_male.gender = "male"
    bird_male.alignment = [180, 0]
    bird_female.gender = "female"
    """
    fox_male = Fox(pos=[25, 20, 1], name="ETHAN")
    fox_female = Fox(pos=[25, 18, 1], name="ELLIE")
    fox_male.gender = "male"
    fox_female.gender = "female"
    fox_male.alignment = [180, 0]

    rabbit_male = Rabbit(pos=[20, 20, 1], name="DANIEL")
    rabbit_male.alignment = [180, 0]
    rabbit_female = Rabbit(pos=[22, 22, 1], name="AVA")
    rabbit_female.gender = "female"
   
    while True:
        live_animal_list = [] #this is for the population
        for animal in animal_list: #for all the animals in animal list
            if animal.alive == True:
                #input(".")
                live_animal_list.append(animal) #this is for the population
                animal.Action() #calling the Animal's action method. This will make it do things
        print("\nWorld Stats:")
        print("Population:", len(live_animal_list))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye.")
