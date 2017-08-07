import itertools as it
import numpy as np
import time
import itertools
import copy

def minus(a,b):
    return [[-a,-b], [-a,b], [a,-b], [a,b]]

def angle(x):
    return int((np.angle(x[0]+x[1]*1j, deg=True)+360) % 360)

def norm(x):
    return np.sqrt(x[0]*x[0]+x[1]*x[1])

def fun(n):
    '''
    Find a,b st: 
     - a2+b2=c2
     - 2c<=n
    '''
    c_max = int(n/2)
    res = []
    angles = []
    for a,b in it.combinations_with_replacement(range(1,c_max),2):
        if np.sqrt(np.power(a,2)+np.power(b,2)) % 1 ==0:
            for x in minus(a,b):
                res.append(x)
                angles.append(angle(x))
            for x in minus(b,a):
                res.append(x)
                angles.append(angle(x))
    for k in range(1,c_max):
        res.append([0,-k])
        angles.append(angle([0,-k]))
        res.append([0,k])
        angles.append(angle([0,k]))
        res.append([-k,0])
        angles.append(angle([-k,0]))
        res.append([k,0])
        angles.append(angle([k,0]))
    angles_inds = np.array(angles).argsort()
    return [res[i] for i in angles_inds]

class Polygon:
    def __init__(self, n, start, segment_history, possible_segments, is_done,
                current_perimeter, current_pos, end):
        self.n = n
        self.start = start
        self.segment_history = segment_history
        self.is_done = is_done
        self.possible_segments = possible_segments
        self.current_perimeter = current_perimeter
        self.current_pos = current_pos
        self.end = end
    def get_n(self):
        return self.n
    def get_start(self):
        return self.start
    def get_segment_history(self):
        return self.segment_history
    def get_is_done(self):
        return self.is_done
    def get_possible_segments(self):
        return self.possible_segments
    def get_current_perimeter(self):
        return self.current_perimeter
    def get_current_pos(self):
        return self.current_pos
    def get_end(self):
        return self.end

def is_valid_increment(p, increment, angles_dict):  
    # Initiate
    is_not_aborted = False
    is_done = False
    angle_increment = angles_dict[tuple(increment)]
    angle_end = angles_dict[tuple(p.get_end())] 
    ## Length
    if (angle_increment>angle_end):
        # Forward
        if (angle_increment-angle_end)<180:
            new_current_perimeter = p.get_current_perimeter() + norm(increment)
            current_pos = p.get_current_pos()
            new_current_pos = current_pos + increment
            # Perimeter
            if ((new_current_perimeter+norm(new_current_pos))<=p.get_n()):
                # Too much
                if angle(-np.array(current_pos))>=angle_increment:
                    # Final
                    is_not_aborted = True
                    if all(new_current_pos == np.zeros(2)):
                         is_done = True
    return is_not_aborted, is_done

# Rolls segments
def segments_rolls(possible_segments):
    possible_segments_rolls = {}
    for i in range(len(possible_segments)):
        key = possible_segments[i]
        possible_segments_rolls[tuple(key)] = list(np.roll(possible_segments,-i,axis=0))
    return possible_segments_rolls

# Initiate polygon based on first segment, and update possible_segments_rolls
def initiate_one_polygon(start, possible_segments_rolls, n):
    possible_segments = possible_segments_rolls[tuple(start)]
    possible_segments.pop(0)
    segment_history = [np.array(start)]
    is_done = False
    # New
    current_perimeter = norm(start)
    current_pos = np.array(start)
    end = np.array(start)
    return Polygon(n, start, segment_history, possible_segments, is_done,
                  current_perimeter, current_pos, end)

# Initiate polygons
def initiate_all_polygons(n):
    possible_segments = fun(n)
    possible_segments_rolls = segments_rolls(possible_segments)
    res = []
    for start in possible_segments:
        res.append(initiate_one_polygon(start, possible_segments_rolls, n))
    return res

# Update a undone polygon into new polygons (potentially done)
def update_one_polygon(p):
    new_polygons = []
    segments = p.get_possible_segments()
    to_visit = p.get_possible_segments()
    for segment in segments:
        is_not_aborted,is_done = is_valid_increment(p, segment)
        to_visit.pop(0)
        if is_not_aborted:
            # Define new polygon
            segment_history = p.getsegment_history()
            segment_history.append(segment)
            new_p = Polygon(p.get_n(), 
                            p.get_start(), 
                            segment_history, 
                            to_visit, 
                            is_done,
                            p.get_current_perimeter()+norm(segment), 
                            p.get_current_pos()+segment,
                            segment)
            # Add polygon to the new list
            new_polygons.append(new_p)
    return new_polygons

# Main
def P(n, verbose = 0):
    # Initiate
    stack = initiate_all_polygons(n)
    count = 0
    t0 = time.time()
    if verbose:
        verbose_count = 0
    # Create angle dictionary for optim
    angles_dict = {}
    for x in fun(n):
        angles_dict[tuple(x)] = angle(x)
    # Updates
    while len(stack)>0:
        if (verbose and ((time.time()-t0) >= verbose*verbose_count)):
            print '\n********************'
            print 'Undone:', len(stack), 'Done:', count
            print '--------------------'
            print 'Found in', time.time()-t0, 'seconds.'
            verbose_count += 1
        # Polygon updates
        p = stack.pop()
        # Stack updates to undone list
        segments = p.get_possible_segments()
        to_visit = copy.copy(segments)
        for segment in segments:
            is_not_aborted,is_done = is_valid_increment(p, segment, angles_dict)
            to_visit.pop(0)
            if is_not_aborted:
                # Define new polygon
                new_p = Polygon(p.get_n(), 
                                p.get_start(), 
                                p.get_segment_history(), 
                                to_visit, 
                                is_done,
                                p.get_current_perimeter()+norm(segment), 
                                p.get_current_pos()+segment,
                                segment)
                new_p.segment_history.append(segment)
                if new_p.is_done:
                    count += 1
                else:
                    # Stack polygon to the new list
                    stack.append(copy.deepcopy(new_p))
    print '\n@@@@@@@@@@@@@@@@@@@@@@@@@'
    print '@      RESULT =', count, '     @'
    print '@@@@@@@@@@@@@@@@@@@@@@@@@'
    print 'Found in', time.time()-t0, 'seconds.'
    return count


print (P(4), P(5), P(6), P(7), P(8), P(9), P(10), P(11), P(12))






