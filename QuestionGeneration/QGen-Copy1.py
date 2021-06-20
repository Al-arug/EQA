import re
from nltk.stem import WordNetLemmatizer
import copy
import statistics
#from HouseParser import HouseParser
from HouseParser import ExtractCloseObjects
import random
import numpy as np

        #question reference issue 
       # is there a storage shelving close to the plant in the kitchen?
    
        # Bad examples 
      #  is there a balcony railing close to the picture in the office?
      #  is there a pew close to the table in the dining room?
          
            #Good examples
       # is there a window close to the picture in the office?
       # is there a sconce close to the cabinet in the office?
       # is there a laundry basket close to the shower in the bathroom?
       # is there a chandelier close to the cabinet in the foyer?
    
            #ambigues
       # is there a cup close to the curtain in the kitchen?
       # is there a bathroom utensil close to the curtain in the kitchen?
       # is there a smoke detector close to the clothes in the closet?
        #Annette Herskovits


class QStringBuilder:
    
    def __init__(self,dataset1,dataset2,qtype):
       
        self.qtype = qtype
        self.TrainDataset = dataset1
        self.ValDataset =   dataset2   
       
        self.wnl = WordNetLemmatizer()
        
        
        

        
        
        
             
        self.w2idx= self.TrainDataset["question_vocab"]["word2idx_dict"]
        self.stoi= self.TrainDataset["question_vocab"]["stoi"] 
        self.itos= self.TrainDataset["question_vocab"]["itos"]
        self.word_list = self.TrainDataset["question_vocab"]["word_list"]
        self.answer_list = []
        self.big = 0
        self.medium = 0 
        self.small = 0 
        self.countMediumAns =0
        
        self.SceneCount = {}
        self.templates = {'size_obj': 'how big <AUX> the <OBJ>?',
                          'size_room': 'how big <AUX> the <OBJ> in the <ROOM>?',
                          'spatial_room': '<AUX> there <ARTICLE> <OBJ1> close to the <OBJ> in the <ROOM>?',
                          'spatial_obj':'<AUX> there <ARTICLE> <OBJ1> close to the <OBJ>?'}
    
 
   
        self.articleMap = {'utensil': 'a', 'utensil holder': 'a'}

       # self.questionSampling(self.dataset,self.qtype)
        
        
        
        if self.qtype== "spatial_room" or self.qtype== "spatial_obj": 
            
            self.undefinedObjects = ['remove','appliance','unknown','wall /otherroom','mirror /otherroom','art/man statue','painting /otherroom','hot water/cold water knob','weight','unknown clutter','object','wall','window frame','door frame','ceiling /otherroom','handrail /otherroom','furniture','window/door',"ceiling","frame"]
        
         #   self.AddedObjects = {"chair":0,"toaster":0,"plant":0,"sofa":0}
        
            self.count_near=0
            self.count_no=0
            
            
            with open("Added_objects.json", "r") as objects: 
                self.AddedObjects = json.loads(objects.read())
            
        self.SplitGeneration(self.TrainDataset,self.ValDataset,qtype) 
     #   self.questionSampling(self.dataset,self.qtype)
                
     #   with open("Added_objects.json", "w") as outfile: 
       #     json.dump(self.AddedObjects, outfile)    
            
            
    def SplitGeneration(self,TrainDataset,ValDataset,qtype):
        
        TrainEpisodes = self.questionSampling(TrainDataset,self.qtype,TrainSplit=True)
        
        if "spatial" in qtype: 
            print(f"There is {self.count_near} positive spatial questions and {self.count_no} negative samples in the training set")
            self.count_near=0
            self.count_no=0
            
        self.countMediumAns =0 
        TrainDataset = self.LoadDataset(TrainEpisodes,TrainSplit=True)
        with gzip.open("train1.json.gz", 'w') as fout:
             fout.write(json.dumps(TrainDataset).encode('utf-8'))
                
  
        
        TestEpisodes = self.questionSampling(ValDataset,self.qtype,TrainSplit=False)
        
        
        if "spatial" in qtype: 
            print(f"There is {self.count_near} positive spatial questions and {self.count_no} negative samples in the test set")
        
        TestDataset = self.LoadDataset(TestEpisodes,TrainSplit=False)
       # for i in TestDataset["episodes"]: 
       #     if i["question"]["question_type"] == "spatial_obj":
       #         print(i)
       #         break 
                
      #  print(TestDataset["question_vocab"]["word2idx_dict"])
      #  print(TestDataset["answer_vocab"]["word2idx_dict"])
      #  print(self.big,self.medium,self.small)  # (2502 5292 1122,spatial room)
        with gzip.open("val1.json.gz", 'w') as fout:
             fout.write(json.dumps(TestDataset).encode('utf-8'))
        
        pass
        
        
    def questionSampling(self,dataset,qtype,TrainSplit=True):

        filterd_data = self.function_if_question_is_object(dataset,qtype)

        random.shuffle(filterd_data)

        # Houses = HouseParser("./Matterport-master/metadata/category_mapping.tsv")
        # allObjVolumes = Houses.Obj_volumes

        with open("Obj_volumes.json","r") as vol:
            allObjVolumes = json.loads(vol.read())
            
        with open("Houses_parsed.json","r") as house:
            houses = json.load(house)

        Pairs = ExtractCloseObjects()
        

        for episode in filterd_data: 

            target_name,target_id,target_volume,room_name,room_id = self.get_objects(episode)
            scene = episode["scene_id"].split("/")[-2]

            room_id1 = "room_"+str(room_id)
            obj_id1 = "obj_"+str(target_id)

            if "size" in qtype:
                if target_name not in allObjVolumes:
                    target_name = houses[scene][room_id1][obj_id1]["name"]
                    #print()
                    print(obj_id1,room_id1,scene)

                answer_text = self.GetSizeAnswer(target_name,target_volume,allObjVolumes,TrainSplit)
                question_text,question_idx = self.question_generation(episode,qtype,target_name,room_name,TrainSplit)

                episode["episode_id"]=str(len(dataset["episodes"])+1)
                episode["question"]['question_text']=question_text
                episode["question"]['question_tokens']=question_idx
                episode["question"]['question_type']=qtype
                episode["question"]['answer_text']=answer_text
                episode["info"]['question_answers_entropy'] = None 

            if "spatial" in qtype:

                scene = episode["scene_id"].split("/")[-2]

                room_id = "room_"+str(room_id)
                obj_id = "obj_"+str(target_id)

                close_objects , AllObjInRoom = GetPairs.getNearbyPairs(scene,room_id)
                  

                answer_text, obj1 = self.GetSpatialAnswer(obj_id,target_name,close_objects,AllObjInRoom,TrainSplit)

                question_text,question_idx = self.question_generation(episode,qtype,target_name,room_name,obj1)

                episode["episode_id"]=str(len(dataset["episodes"])+1)
                episode["question"]['question_text']=question_text
                episode["question"]['question_tokens']=question_idx
                episode["question"]['question_type']=qtype
                episode["question"]['answer_text']=answer_text
                episode["info"]['question_answers_entropy'] = None 
        j = dataset["episodes"] + filterd_data

      #  final = self.LoadDataset(j) 
      #  print(final.keys())
      #  print(self.count_near,self.count_no)
       # print(self.AddedObjects)

        return j     
        
    def function_if_question_is_object(self,data,qtype): 

        if qtype=="size_room" or qtype=="spatial_room":
            Targetype="color_room"
    
        elif qtype=="size_obj" or qtype=="spatial_obj":
            Targetype="color"

        episodes= copy.deepcopy(data["episodes"])
        filtered = [episode for episode in episodes if episode["question"]["question_type"] == Targetype]

        return filtered 

    
    def get_objects(self,episode):
        
        if episode["info"]["bboxes"][0]["target"]==True:
            target_name = episode["info"]["bboxes"][0]["name"]
            target_name = ' '.join(re.split("_|#",target_name))
            target_volume= np.prod(np.array(episode["info"]["bboxes"][0]["box"]["radii"])*2)
            target_id = episode["info"]["bboxes"][0]["box"]["obj_id"]

            room_name = episode["info"]["bboxes"][1]["name"][0]
            room_name = ' '.join(re.split("_|#",room_name))
            room_id = episode["info"]["bboxes"][0]["box"]["room_id"]
            room_volume=  np.prod(np.array(episode["info"]["bboxes"][1]["box"]["radii"])*2)                     


        else: 
            target_name = episode["bboxes"][1]["name"][0]
            target_name = ' '.join(re.split("_|#",name))
            target_volume= np.prod(np.array(episode["info"]["bboxes"][1]["box"]["radii"])*2)

        return target_name,target_id,target_volume,room_name,room_id
    
    
    def question_generation(self,episode,qtype,obj,room,obj1): 
        
        question_text = self.prepareString(self.templates[qtype],obj,room,obj1)
        
      
        self.function_for_word_to_idx(question_text[:-1])            
         #   assert all([True if i in self.w2idx else False for i in question_text[:-1]]) 
            
        question_idx = [self.w2idx[i] for i in question_text[:-1].split() if i != "NoObject"]

        return  question_text, question_idx

    
    def function_for_word_to_idx(self,sentence): 
        if all([True if i in self.w2idx else False for i in sentence.split()]):
            pass 
        else: 
            for i in sentence.split():
                if i != 'NoObject':
                    if i not in self.w2idx:
                        self.w2idx[i]=len(self.w2idx) 
                        self.stoi[i]=len(self.stoi)
                    if i not in self.word_list: 
                        self.word_list.append(i)
                        self.itos.append(i)
        pass 


        
    def GetSizeAnswer(self,obj_name,target_volume,volumes,TrainSplit):
        
        mean = {i:sum(l)/len(l) for i,l in volumes.items() if len(l)!=0}
        stdev =  {i:statistics.stdev(l) for i,l in volumes.items() if len(l)>1}

        if obj_name not in volumes:    
            print("different name", obj_name)
            obj = [i for i in stdev.keys() if obj_name in i ]
            mean_size= mean[obj[0]]
            StandardDev= stdev[obj[0]]
        else: 
            
            mean_size = mean[obj_name]
            StandardDev= stdev[obj_name]
        
        big = mean_size + StandardDev
        small = mean_size - StandardDev
        
        
        answer_text=""
        if target_volume>= big:
            answer_text += "big"
            self.big += 1
        elif target_volume <= small:
            answer_text += "small"
            self.small +=1
            
        elif target_volume < big and target_volume > small:
            
            if TrainSplit == True and self.qtype== "size_obj" and self.countMediumAns == 610:
                answer_text = None
            elif TrainSplit == False and self.qtype== "size_obj" and self.countMediumAns == 60:
                answer_text = None
            elif TrainSplit == True and self.qtype== "size_room" and self.countMediumAns == 2677:
                answer_text = None    
            elif TrainSplit == False and self.qtype== "size_room" and self.countMediumAns == 445:
                answer_text = None 
            else: 
                answer_text+= "medium"
                self.countMediumAns+=1
                #
        
        return answer_text
    
    def GetSpatialAnswer(self,obj_id,obj_name,close_objects,AllObjInRoom,TrainSplit):
        
       
        NearByObject = []
       
      
        for i in close_objects: 
            if obj_id == i[0][1]:
                NearByObject.append(i[1][0])

        
        NearByObject=[i for i in NearByObject if i not in self.undefinedObjects if "/otherroom" not in i if i in self.AddedObjects.keys()]
               
        if len(NearByObject) == 1 and NearByObject[0]== obj_name:
            NearByObject = None
        
        if NearByObject: 
            
            while True:
                CloseObj = random.choice(NearByObject)
                if CloseObj != obj_name:
                    break
            
            answer = "yes"
            self.count_near+=1
            
            return answer , CloseObj
        
        else:
            
            answer = "no"
            while True:
                random_obj = random.choice([i for i in self.AddedObjects.keys()])
                if random_obj != obj_name and random_obj not in AllObjInRoom:
                    break
            
            
            if TrainSplit==True and self.qtype== "spatial_obj" and self.count_no == 300 : 
                answer = None 
                random_obj = "NoObject"
                print(answer)
                
            if TrainSplit==False and self.qtype== "spatial_obj" and self.count_no == 25 : 
                answer = None 
                random_obj = "NoObject"
                
            
            if TrainSplit==True and self.qtype== "spatial_room" and self.count_no == 1600: 
                
                answer = None 
                random_obj = "NoObject"  
            
            
            if TrainSplit==False and self.qtype== "spatial_room" and self.count_no == 300: 
                
                answer = None 
                random_obj = "NoObject"
            
            if answer !=None:
                self.count_no+=1
            print(answer)
            return answer, random_obj   
                
        
    def prepareString(self,qString,obj,room,obj1): 


        obj = ' '.join(re.split("_|#",obj))

        room = ' '.join(re.split("_|#",room.lower()))

        if '<AUX>' in qString and "<OBJ1>" not in qString:
            qString = self.replaceAux(qString, obj)
            
        if '<AUX>' in qString and "<OBJ1>" in qString:
            qString = self.replaceAux(qString, obj1)  
            qString = self.replaceObj(qString, obj1)
            
        if '<ARTICLE>' in qString:
            qString = self.replaceArticle(qString, obj1)
            
        if '<OBJ>' in qString or '<OBJ-plural>' in qString:
            qString = self.replaceObj(qString, obj)
        if '<ROOM>' in qString or '<ROOM-plural>' in qString:
            qString = self.replaceRoom(qString, room)
            
        self.qString = qString  
      #  print(self.qString)
       
        return self.qString            
                
    
    
    
    
    def isPlural(self,word):
        lemma = self.wnl.lemmatize(word, 'n')
       # print(lemma,word)
        plural = True if word is not lemma else False
       
        return plural


    def replaceAux(self,template, obj):
        assert '<AUX>' in template
        if self.isPlural(obj) or obj =="clothes":
            return template.replace('<AUX>', 'are')
        else:
            return template.replace('<AUX>', 'is')

    def replaceArticle(self,template, obj):
        assert '<ARTICLE>' in template
        if self.isPlural(obj) or obj in ["clothes","wine"] :
            return template.replace(' <ARTICLE>', '', 1)
        else:
            if obj in self.articleMap:
                return template.replace('<ARTICLE>', self.articleMap[obj], 1)
            elif obj[0] in ['a', 'e', 'i', 'o', 'u']:
                return template.replace('<ARTICLE>', 'an', 1)
            else:
                return template.replace('<ARTICLE>', 'a', 1)

    def replaceObj(self,template, obj):
        
        if '<OBJ1>' in template:
            return template.replace('<OBJ1>', obj, 1)
        
        if '<OBJ>' in template and '<OBJ1>' not in template:
            return template.replace('<OBJ>', obj, 1)
              
        elif '<OBJ-plural>' in template:
            if isPlural(obj):
                return template.replace('<OBJ-plural>', obj)
        else:
            return template.replace('<OBJ-plural>', obj + 's')
    

    def replaceRoom(self,template, room):
            # assert '<ROOM>' in template
        if '<ROOM>' in template:
            return template.replace('<ROOM>', room)
        elif '<ROOM-plural>' in template:
            return template.replace('<ROOM-plural>', room + 's')
    


       


           


    
    def LoadDataset(self,episodes,TrainSplit):
        assert self.w2idx == self.stoi
        assert self.itos == self.word_list
        
        episodes = [episode for episode in episodes if episode["question"]['answer_text']!= None]
        random.shuffle(episodes)
        
        #self.answer_list = []
        
        for i in range(1,len(episodes)):
            episodes[i]["episode_id"]= i
            if TrainSplit == True:
                self.answer_list.append(episodes[i]["question"]['answer_text'])
        
        answerW2idx = {self.answer_list[i]:i for i in range(len(self.answer_list))}
        
        
        assert all([True if i not in self.w2idx.values() else False for i in answerW2idx.values()])
        
        answerW2idx['<unk>'] = 0 
        dataset = {"episodes":episodes,
                   
                  "question_vocab": {"word_list":self.word_list,
                                     "word2idx_dict":self.w2idx,
                                      "stoi":self.stoi,
                                      "itos":self.itos,
                                      'UNK_INDEX': 1,
                                       'PAD_INDEX':0},
                   
                  "answer_vocab": {"word_list":self.answer_list,
                                   "word2idx_dict":answerW2idx,
                                   "stoi":answerW2idx,
                                   "itos":self.answer_list,
                                   'UNK_INDEX': 1,
                                   'PAD_INDEX':0}}
                          
        return dataset 
            
            
            
import json
import gzip  # home/gusarual@GU.GU.SE/Habitat-Project/habitat-lab/data/datasets/eqa/mp3d/v1/
             # home/gusarual@GU.GU.SE/Habitat-Project/habitat-lab/data/datasets/eqa/mp3d/v1/val/
w = "./train.json.gz" #home/gusarual@GU.GU.SE/Habitat-Project/habitat-lab/data/datasets/eqa/mp3d/v1/train/
r = "./val.json.gz"               
with gzip.open(w, "rb") as f:
    d = json.loads(f.read().decode("ascii"))    

with gzip.open(r, "rb") as f:
    o = json.loads(f.read().decode("ascii")) 
QStringBuilder(d,o,"size_room") 
    
    
    