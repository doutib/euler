import itertools as it
import numpy as np
import time
import progressbar

def minus(a,b):
    return [[-a,-b], [-a,b], [a,-b], [a,b]]

def angle(x):
    return int((np.angle(x[0]+x[1]*1j, deg=True)+360) % 360)

def norm(x):
    return np.sqrt(x[0]*x[0]+x[1]*x[1])

def norm2(x):
    return int(x[0]*x[0]+x[1]*x[1])

def is_between(vector,min,max):
	return (min[0]*vector[1]>min[1]*vector[0]) and (max[0]*vector[1]<max[1]*vector[0])

def possible_segments_fun(n):
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

def path_count(segment, n, min_angle, max_angle, possible_segments):
	res = 0
	while len(possible_segments)>0:		
		next_segment = possible_segments.pop(0)
		if is_between(next_segment, min_angle, max_angle):									## Get legitimate segment
			new_segment = [segment[0]+next_segment[0], segment[1]+next_segment[1]]          ## Get new first segment			
			new_n = n - norm(segment) - norm(next_segment) + norm(new_segment)
			if new_segment[0]>=0:	
				if round(new_n*new_n) >= 4*norm2(new_segment):								## Can polygon be done?
					if ((norm(new_segment) % 1) == 0):										## Is legitimate finish?			
						res += 1  															## Found one new polygon				
					new_max_angle = [-new_segment[0],-new_segment[1]]																				
					next_possible_segments = next_possible_segments_fun(					## Get legitimate segments of new segment
						next_segment, new_max_angle, possible_segments)				
					if next_possible_segments:												## If there is any legitima, repeat
						res = res + path_count(new_segment, new_n,				
							next_segment, new_max_angle, next_possible_segments)	
			possible_segments = next_possible_segments_fun(									## Update legitimate segment list
				min_angle, max_angle, possible_segments)
	return res

def next_possible_segments_fun(min_angle, max_angle, possible_segments):
	i=0
	while i<len(possible_segments):
		if is_between(possible_segments[i], min_angle, max_angle):
			break
		i += 1
	return possible_segments[i:]

def segments_rolls(possible_segments):
    possible_segments_rolls = {}
    for i in range(len(possible_segments)):
        key = possible_segments[i]
        if key[0]>0:
        	possible_segments_rolls[tuple(key)] = (np.roll(possible_segments,-i,axis=0)).tolist()
    return possible_segments_rolls

def P(n):
	res = 0
	rolls = segments_rolls(possible_segments_fun(n))
	keys = rolls.keys()
	n_iter = len(keys)
	for i, segment_coords in enumerate(keys):
		segment = [segment_coords[0], segment_coords[1]]
		res = res + path_count(segment, n, segment, [-segment_coords[0], -segment_coords[1]], rolls[segment_coords])
		print i*1000/n_iter, res
	return res

print P(30)








