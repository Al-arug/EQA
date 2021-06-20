from glob import glob 
import numpy as np
import pandas as pd 

import json

class ExtractCloseObjects:
    
    def __init__(self):
         
       # self.path=(path)
        #self.house_id = house_id
       # self.room_id = room_id
        
        #super().__init__()
      #  self.path = path
        #self.ParseHouses()
        #self.path = path
        
        house_file= '/home/gusarual@GU.GU.SE/QuestionGeneration/Houses_parsed.json'
        with open(house_file, "r") as house: 
            self.houses = json.loads(house.read())
            
           
        #self.getNearbyPairs()  
        
    def getNearbyPairs(self,house_id,room_id,
                   hthreshold=0.1,
                   vthreshold=0.1):#0.005):
    
        self.availableEnts = self.houses[house_id][room_id]  
     
        assert len(self.availableEnts) != 0

        self.nearbyPairs = []#{'on': [], 'next_to': []}
        
        AllObjInRoom = []
        for i in (list(self.availableEnts.keys())[:-1]):
            AllObjInRoom.append(self.availableEnts[i]["name"])
            for j in (list(self.availableEnts.keys())[1:]):
             #   print(self.availableEnts[i]["name"])
                
                if i!= j:
                        # next to
                    dist = self.getClosestDistance(
                            self.availableEnts[i],
                            self.availableEnts[j],
                            axes=[0,1,2])
                    if dist < 0.32 : 
                        self.nearbyPairs.append(([self.availableEnts[i]["name"],i], [self.availableEnts[j]["name"],j], dist))
                   # print(self.nearbyPairs)       #            
                 #   if dist < hthreshold and (self.isContained(
                  #              self.availableEnts[i],
                   #             self.availableEnts[j],
                    #            axis=0) & self.isContained(
                     #               self.availableEnts[i],
                      #              self.availableEnts[j],
                      #              axis=2)) == False:
                           # if availableEnts[i].type == 'room' and availableEnts[j].type == 'room':
                              #  nearbyPairs['next_to'].append(
                              #      (availableEnts[i], availableEnts[j], dist))
                      #  if self.isContained(      # y axis 
                       #         self.availableEnts[i],
                        #        self.availableEnts[j],
                         #       axis=1) == True:
                          #      self.nearbyPairs['next_to'].append(
                           #             ([self.availableEnts[i]["name"],i], [self.availableEnts[j]["name"],j], dist))
      #  print(self.availableEnts[i]["name"],i)
                        # on / below
                        #if availableEnts[i].type == 'object' and availableEnts[j].type == 'object':
                 #   dist = self.getClosestDistance(
                  #              self.availableEnts[i],
                   #             self.availableEnts[j],
                 #               axes=[1])
                 #   if dist < vthreshold and (self.isContained(
                  #                  self.availableEnts[i],
                   #                 self.availableEnts[j],
                    #                axis=0) & self.isContained(
                     #                   self.availableEnts[i],
                      #                  self.availableEnts[j],
                       #                 axis=2)) == True and self.isContained(
                       #                     self.availableEnts[i],
                        #                    self.availableEnts[j],
                         #                   axis=1) == False:

                                # higher first
                     #   if self.isHigher(
                      #                  self.availableEnts[i],
                       #                 self.availableEnts[j],
                        #                axis=1):
                         #           self.nearbyPairs['on'].append(
                          #              ([self.availableEnts[i]["name"],i], [self.availableEnts[j]["name"],j], dist))
                      #  elif self.isHigher(
                       #                 self.availableEnts[i],
                        #                self.availableEnts[j],
                         #               axis=1):
                          #          self.nearbyObjectPairs['on'].append(
                           #             ([self.availableEnts[i]["name"],i], [self.availableEnts[j]["name"],j], dist))

        return self.nearbyPairs, AllObjInRoom #pass    #return nearbyPairs
    
    def getClosestDistance(self,obj1, obj2, axes=[0, 1], order=2):
        assert 'bbox' in obj1 and 'bbox' in obj2

        bbox = [
                {
                    'min': np.array(obj1['bbox']['min'])[axes],
                    'max': np.array(obj1['bbox']['max'])[axes]
                },
                {
                    'min': np.array(obj2['bbox']['min'])[axes],
                    'max': np.array(obj2['bbox']['max'])[axes]
                },
            ]

        cornerInds = [[
                int(i) for i in list('{0:0{width}b}'.format(j, width=len(axes)))
            ] for j in range(2**len(axes))]
        corners = [[
                np.array(
                    [bbox[obj][['min', 'max'][i[j]]][j] for j in range(len(axes))])
                for i in cornerInds
            ] for obj in range(2)]

        dist = 1e5
        for i in range(len(corners[0])):
            for j in range(len(corners[1])):
                d = np.linalg.norm(corners[0][i] - corners[1][j], ord=order)
                if d < dist:
                    dist = d

        return dist


        """
        Checks if coordinates along given axis of one object is contained in another
        obj1, obj2 should have 'bbox' attributes
        """

    def isContained(self,obj1, obj2, axis=0):
        if obj1['bbox']['min'][axis] < obj2['bbox']['min'][axis] and obj1['bbox']['max'][axis] > obj2['bbox']['max'][axis]:
            return True
        elif obj2['bbox']['min'][axis] < obj1['bbox']['min'][axis] and obj2['bbox']['max'][axis] > obj1['bbox']['max'][axis]:
            return True
        else:
            return False

        """
        Checks if obj1 is higher than obj2 along given axis
        """

    def isHigher(self,obj1, obj2, axis=0):
        if obj1['bbox']['max'][axis] > obj2['bbox']['max'][axis]:
            return True
        else:
            return False

    
    
      
    
class HouseParser(): #ExtractCloseObjects
    
    def __init__(self,path):
        
       # super().__init__(path)
        
        self.path = path
        
       # self.getNearbyPairs()
        self.ParseHouses()
        
    def ExtractObjectInfo(self,objects,cat_map, radiis):
    
   # radiis={item:[] for idx,item in cat_map.items()}
        house={}
        for obj in objects:    
            obj_id = "obj_" + obj[1]  
            room_id = "room_" + obj[2] 
            centroid = np.array([float(i) for i in obj[4:7]])
            obj_radi = np.array([float(i) for i in obj[-11:-8]])
            cat_name = cat_map[str(obj[3])] 
            max1 = centroid + obj_radi
            mini= centroid - obj_radi 
            if room_id in house:
                house[room_id][obj_id]={"name":cat_name,"bbox":{"max":list(max1),"min":list(mini)}}
                radiis[cat_name].append(np.prod(obj_radi*2))

            elif room_id not in house:
                house[room_id]= {obj_id:{"name":cat_name,"bbox":{"max":list(max1),"min":list(mini)}}}
                radiis[cat_name].append(np.prod(obj_radi*2))

        return  house , radiis       
        
        
   # @classmethod
    def ParseHouses(self):
    
        House_files = glob('/home/gusarual@GU.GU.SE/Habitat-Project/habitat-lab/data/scene_datasets/mp3d/*/*.house') 
    
    
        PathToMData = self.path #"./Matterport-master/metadata/category_mapping.tsv"#path
        MetaData = pd.read_csv(PathToMData,sep='\t')
        categories= MetaData["category"].to_list()

        cat_map = {str(i):categories[i] for i in range(len(categories))}
        self.Obj_volumes = {cat:[] for cat in categories}
        cat_map["-1"]="unknown"
    
        self.Parsed_houses= {}
    
        for house in House_files:
            AllData = pd.read_csv(house, sep='\t')
            house_id = house.split("/")[-2]
        
            objects=[line[1].tolist()[0].split() for line in AllData.iterrows() if line[1].tolist()[0][0]== "O"] 
        
            objectsInfo,volumes = self.ExtractObjectInfo(objects,cat_map,self.Obj_volumes)   
            self.Parsed_houses[house_id]= objectsInfo
            self.Obj_volumes= volumes
            
        with open("Houses_parsed1.json", "w") as outfile: 
            json.dump(self.Parsed_houses, outfile)
            
        with open("Obj_volumes1.json", "w") as file: 
            json.dump(self.Obj_volumes, file)
            
    
        
        pass
    
    
#HouseParser("./Matterport-master/metadata/category_mapping.tsv")
    
    
    