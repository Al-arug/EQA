# EQA

concluding remerks from meeting: 

16 apr: Parsed the houses from Habitat-simulators, following this demo: https://aihabitat.org/docs/habitat-api/habitat-sim-demo.html#scene-semantic-annotations. Forked habitat-sim in a different folder to get the latest upgrade. 


19apr: There is 2d and 3d bounding boxes. The EQA code is desinged to generate from a 2d bounding boxes. The semantic annotaitions extracted from Habitat-sim includes 3d information as such: Object id:0_0_0, category:wall, center:[-8.86568    1.2817702 -2.73879  ], dims:[4.5891   2.581481 4.591819]. Attempts at solving this issue by looking through the Mp3d, habitat, and eqa repos. Some issues on habitat-lab repo shows some ways to create Pgnv datasets.  Another way to solve the the issue is by changng the 3d bounding boxes into 2d. further work: Even if this issue is solved, we need to look at way to run the whole EQA task and extract episodes with observations. 

I also check ISQL paper, which provides a dataser of questions about scenes from Gipson. The questions are asked by human annotators. 
Checked MESH data --> graphics

two issues to check tomorrow : https://github.com/facebookresearch/habitat-sim/issues/915 , https://github.com/facebookresearch/habitat-sim/issues/760 


19-27 apr: invistigating the geometric information in the habitat sim semantic parser. the parser can be found in home/simulator/habitat-sim/testing/parse.py. aabb and obb. SOme conlusions drawn is to get the volumes of the objects inside the enviroment and make size-questions, the sizes are determined relative to the mean size of the objects of the same kind. Second point is to investigate how the navigation works with the dataset. some of the points discuessed : 

I think it is something quite different what we thought previously. The coordinates are probably global (relative to some origin) and the BB is an approximation of the object to the global orientation, i.e. the squares that an object would occupy if we outline it on a graph paper (hence the object is not oriented either). So that’s way it is useful for collision detection since two objects should not overlap in any of the squares.

https://stackoverflow.com/questions/22512319/what-is-aabb-collision-detection

AABB stands for "Axis-Aligned Bounding Box.”

It is a fairly computationally- and memory-efficient way of representing a volume, typically used to see if two objects might be touching.

Since it is axis-aligned, it does not necessarily "fit" your real 3D object very well. AABB checks are often used as a coarse first-approximation to see if objects might be colliding. Then, if the AABB check passes, more detailed checks are made.

Example:

Imagine your world is 2D, and you draw it on a sheet of graph paper. You have some objects in the world (a ball, a tree, whatever). To make an AABB for one of the objects, you draw a rectangle around the object, making your lines parallel to the grid lines on the paper.

If you have the AABB for two objects, you can do some pretty simple math to see if those AABBs overlap. If they don't overlap, those two objects couldn't possibly be touching, so it's an easy early-out for your collision algorithm.

This generalizes to 3D (and more-Ds) fairly easily.

You might want to check out gamedev.stackexchange.com, too.

—

Axis Aligned Bounding Box

Basically its the smallest Cuboid that can completely contain the shape, usually defined by a pair of 3d co-ordinates.

It's very fast to check for collisions between two AABB as all you need to do is check the range of the X, Y and Z values for the corners.

—

From Matterport instructions: https://github.com/niessner/Matterport/blob/master/data_organization.md

In Matterport AABB (xlo, ylo, zlo, xhi, yhi, zhi) is only used in level, region, portal, surface but not object.

Objects have (px, py, pz, a0x, a0y, a0z, a1x, a1y, a1z, r0, r1, r2) define the center, axis directions, and radii of an oriented bounding box, height is the distance from the floor, and 0 is a value that can be ignored. Radii is a plural of radii (distance from the centre) rather than radian (angle)?

Axis directions a0 and a1 seem to be two points; the points that orient the x and y axis of the object (we do not need z because we are grounded by gravity)? Here then I assume that all coordinates are global. 

28 april: Many of the semantic annotation correspondes with the same ids to the eqa dataset. the info section of each sample can be extracted from the semantic parser. 

code for generating shortest path for the point navigation dataset: https://github.com/facebookresearch/habitat-lab/blob/master/examples/shortest_path_follower_example.py . Git issues:  https://github.com/facebookresearch/habitat-lab/issues/140. 

The navigation is being trained and will evaluate it. 

