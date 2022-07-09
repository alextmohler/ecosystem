import math
import random

def Dot_Product(v1, v2, rel=True):
    """finds the dot product of the two vectors that are in [x, y, z] form. 'rel' refers to relative. 
    If 'rel' = True than the vectors given are relative to the origin
        If not, than they are in the form [x1, y1, z1, x2, y2, z2] and we must substract xyz2 from xyz1
    """
    if rel == True:
        return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    else:
        vv1 = [v1[3]-v1[0], v1[4]-v1[1], v1[5]-v1[2]]
        vv2 = [v2[3]-v2[0], v2[4]-v2[1], v2[5]-v2[2]]
        return vv1[0] * vv2[0] + vv1[1] * vv2[1] + vv1[2] * vv2[2]

def find_distance(pos1, pos2=[0,0,0]):
    """finds the distance between the two points. If pos2 is left out, it is assumed that it is the origin"""
    return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2)

def find_flat_distance(pos1, pos2):
    """finds the distance between the points as if they were on a single plane. (ie ignores the z coordinate"""
    return math.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)

def find_angle_vector(angle1, angle2, distance=1):
    """finds the vector in the direction indicates by the angles with length 'distance'. The default length is one (ie a unit vector)
    angle1 is the horizontal angle (ie on the xy plane)
    angle2 is the vertical angle
    """
    hor_rad = angle1 #horizontal_angle_radians
    vert_rad = angle2 #vertical_angle_radians
    x = math.cos(vert_rad) * math.cos(hor_rad)
    y = math.cos(vert_rad) * math.sin(hor_rad)
    z = math.sin(vert_rad)
    vector = [x*distance, y*distance, z*distance]
    return vector

def find_angles(pos1, pos2):
    """finds the angles required to reach a certain point, and returns them in form [horizontal_degrees, vertical_degrees]"""
    #making the position relative to the origin for ease of use
    rel_pos = [pos2[0] - pos1[0], pos2[1] - pos1[1], pos2[2] - pos1[2]]

    #organizing the 'edge' cases
    if rel_pos[0] == 0: #if x = 0
        #we need all these measures in radians, because we convert from radians in our return statement
        if rel_pos[1] > 0: #if y is greater than 0
            hor_deg = math.pi/2
        elif rel_pos[1] < 0: #if y is less than 0
            hor_deg = 0-math.pi/2
        else:
            hor_deg = 0 #if x and y are zero, than the horizontal degree does not really matter at all, so we just make it equal to zero
    elif rel_pos[0] < 0: #if x is less than 0
        if rel_pos[1] == 0: #if y = 0
            hor_deg = math.pi #180 degrees
        elif rel_pos[1] > 0: #if y > 0
            hor_deg = math.pi + math.atan(rel_pos[1]/rel_pos[0])
        else:
            hor_deg = math.atan(rel_pos[1]/rel_pos[0]) - math.pi
    else:
        hor_deg = math.atan(rel_pos[1]/rel_pos[0])

    #this is the flat distance between the points, we need this because the the adjacent leg of the triangle we are taking the
    #vertical degrees is the horizontal line to the point
    dist = find_flat_distance(pos1, pos2)

    #some simple trig
    if dist == 0:
        if rel_pos[2] > 0:
            vert_deg = math.pi/2
        elif rel_pos[2] < 0:
            vert_deg = 0 - math.pi/2
    else:
        vert_deg = math.atan(rel_pos[2]/dist)

    #here we convert from radians so it will be degrees
    return [rad_deg(hor_deg), rad_deg(vert_deg)]

def find_midpoint(pos1, pos2):
    return [round((pos1[0]+pos2[0])/2), round((pos1[1]+pos2[1])/2), round((pos1[2]+pos2[2])/2)]

def find_vector(pos1, pos2):
    """finds the vector between the two points"""
    x = pos2[0] - pos1[0]
    y = pos2[1] - pos1[1]
    z = pos2[2] - pos1[2]
    return [x, y, z]

def vector_k(vector, k=1):
    """takes a vector and multiplies it by k"""
    return [vector[0]*k, vector[1]*k, vector[2]*k]

def add_vector(vect1, vect2):
    """returns the vect1 + vect2 in a three element list [x, y, z]"""
    return [vect1[0] + vect2[0], vect1[1] + vect2[1], vect1[2] + vect2[2]]

def deg_rad(ang):
    """converts degrees to radians"""
    return ang * math.pi/180

def rad_deg(ang):
    """converts radians to degrees"""
    return ang * 180/math.pi


def find_mate_ratio(self, pot_mate):
    """finds the ratio of the mate, given the coordinates and type in [x, y, z, type]"""
    pm = pot_mate #the potential mate is the the third thing in the coordinates list
    
    #the mate's traits
    speed = pm.speed
    attractiveness = pm.attractiveness
    vision_arc = pm.vision_arc
    vision_length = pm.vision_length

    #we are multiplying everthing together and then subtracting the distance. This makes it so that the closer male will be slightly higher value
    ratio = speed * attractiveness * vision_arc * vision_length - find_distance(self.pos, pm.pos)
    return ratio

def surrounding_points(self):
    """finds all the surrounding points [-1:1, -1:1, -1:1], and returns them in a list"""
    point_list = []
    for x in range(self.pos[0]-1, self.pos[0]+2):
        for y in range(self.pos[1]-1, self.pos[1]+2):
            for z in range(self.pos[2]-1, self.pos[2]+2):
                if vector_k(self.pos) != [x, y, z]: #ie the random point that is chosen is not the current position
                    point_list.append([x, y, z]) #adding it to the point list
    return point_list

def surrounding_flat_points(self):
    """finds all the surrounding points on a flat plane [-1:1, 0, -1:1], and returns them all in a list"""
    point_list = []
    for x in range(self.pos[0]-1, self.pos[0]+2):
        for y in range(self.pos[1]-1, self.pos[1]+2):
            if vector_k(self.pos) != [x, y, self.pos[2]]:
                point_list.append([x, y, self.pos[2]])
    return point_list

def compare_lists(list1, list2):
    """returns list1 if list1 is greater, returns list2 if list2 is greater. returns "equal" if they are equal"""
    if list1[0] > list2[0]:
        return "list1"
    elif list1[0] < list2[0]:
        return "list2"
    elif list1[0] == list2[0]:
        if list1[1] > list2[1]:
            return "list1"
        elif list1[1] < list2[1]:
            return "list2"
        elif list1[1] == list2[1]:
            if list1[2] > list2[2]:
                return "list1"
            elif list1[2] < list2[2]:
                return "list2"
            elif list1[2] == list2[2]:
                return "equal"

def cross_product(vector1, vector2):
    """takes two vectors and returns a vector normal to that plane"""
    v1_mag = find_distance(vector1)
    v2_mag = find_distance(vector2)
    i_c = vector1[1] * vector2[2] - vector1[2] * vector2[1]
    j_c = vector1[0] * vector2[2] - vector1[2] * vector2[0]
    k_c = vector1[0] * vector2[1] - vector1[1] * vector2[0]
    return [round(i_c), 0-round(j_c), round(k_c)]

class Test():
    def __init__(self):
        self.pos = [5, 5, 5]

def main():
    list1 = input("list1: ").split(",")
    list2 = input("list2: ").split(",")
    print(compare_lists(list1, list2))
    

if __name__ == "__main__":
    main()

