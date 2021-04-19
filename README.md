# EQA

concluding remerks from meeting: 

16 apr: Parsed the houses from Habitat-simulators, following this demo: https://aihabitat.org/docs/habitat-api/habitat-sim-demo.html#scene-semantic-annotations. Forked habitat-sim in a different folder to get the latest upgrade. 


19apr: There is 2d and 3d bounding boxes. The EQA code is desinged to generate from a 2d bounding boxes. The semantic annotaitions extracted from Habitat-sim includes 3d information as such: Object id:0_0_0, category:wall, center:[-8.86568    1.2817702 -2.73879  ], dims:[4.5891   2.581481 4.591819]. Attempts at solving this issue by looking through the Mp3d, habitat, and eqa repos. Some issues on habitat-lab repo shows some ways to create Pgnv datasets.  Another way to solve the the issue is by changng the 3d bounding boxes into 2d. further work: Even if this issue is solved, we need to look at way to run the whole EQA task and extract episodes with observations. 

I also check ISQL paper, which provides a dataser of questions about scenes from Gipson. The questions are asked by human annotators. 
Checked MESH data --> graphics

two issues to check tomorrow : https://github.com/facebookresearch/habitat-sim/issues/915 , https://github.com/facebookresearch/habitat-sim/issues/760 
