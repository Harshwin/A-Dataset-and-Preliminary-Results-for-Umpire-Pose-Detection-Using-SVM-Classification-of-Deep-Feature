
"""
Video Summarization using VGG19
Paper: Ravi, Aravind, Harshwin Venugopal, Sruthy Paul, and Hamid R. Tizhoosh. 
"A Dataset and Preliminary Results for Umpire Pose Detection Using SVM Classification of Deep Features." 
arXiv preprint arXiv:1809.06217 (2018).

"""
import os
import cv2
from keras import applications
from keras.applications.vgg19 import preprocess_input
from keras.preprocessing import image
import numpy as np  
import pickle
from keras.models import Model
import time
start_time = time.time()

base_model = applications.vgg19.VGG19(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
model = Model(input=base_model.input, output=base_model.get_layer('fc1').output)

#Project Model- loading the saved VGG models
loaded_model1 = pickle.load(open('FER_vgg19fc1_model1net_ck_transfer_only_svm.sav', 'rb'))
loaded_model2 = pickle.load(open('FER_vgg19fc1_model2net_ck_transfer_only_svm.sav', 'rb'))

vidcap = cv2.VideoCapture('testVideoAll1.mp4')# Path to the video to be summarized

count = 0
bufferCount = 0

globalWideVideo =[]
globalOutVideo =[]
globalSixVideo =[]
globalNoBallVideo =[]
globalNoActionVideo =[]
buffer=[]

th=5
buff_th=250
globalWideCounter = 0
globalOutCounter = 0
globalSixCounter = 0
globalNoBallCounter = 0
globalNoActionCounter = 0


while (True):
    success,img = vidcap.read()
    
    if success:
        bufferCount = bufferCount + 1
        buffer.append(img)
        height, width, layers = img.shape
        size = (width,height)
        count=count+1
        print ("success")
        img1 = cv2.resize(img,(224,224))
        x = image.img_to_array(img1)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        #Feature Extraction Step
        features = model.predict(x) #Inception V3 Model
        #Classification Step
        predicted_values = loaded_model1.predict(features.reshape(1,-1)) 
        if predicted_values==2:
            predicted_values_2 = loaded_model2.predict(features.reshape(1,-1))
            choices = {'1':'noball', '2':'out', '3':'six', '4':'wide', '5':'noaction'}
            result = choices.get(np.str(int(predicted_values_2)), 'default')
            if result == 'noball':
                globalNoBallCounter = globalNoBallCounter + 1
                print('noball:')
            if result == 'out':
                globalOutCounter = globalOutCounter + 1
                print('out:')
            if result == 'six':
                globalSixCounter = globalSixCounter + 1
                print('six:')
            if result == 'wide':
                globalWideCounter = globalWideCounter + 1
                print('wide:')
            if result == 'noaction':
                globalNoActionCounter = globalNoActionCounter + 1
                print('noaction:')
            
    else:
        break
    ## Frame accumulation for buffer
    if bufferCount == buff_th:
        actionCount = {'noball': globalNoBallCounter, 'out': globalOutCounter, 'six': globalSixCounter, 'wide': globalWideCounter}

        winner = max(actionCount, key=actionCount.get)
        if winner == 'noball' and globalNoBallCounter >th:
            globalNoBallVideo.append(buffer)
        if winner == 'out'and globalOutCounter >th:
            globalOutVideo.append(buffer) 
        if winner == 'six'and globalSixCounter >th:
            globalSixVideo.append(buffer)
        if winner == 'wide' and globalWideCounter >th:
            globalWideVideo.append(buffer)
       
        bufferCount = 0
        globalWideCounter = 0
        globalOutCounter = 0
        globalSixCounter = 0
        globalNoBallCounter = 0
        globalNoActionCounter = 0
        buffer = []
    
actionCount = {'noball': globalNoBallCounter, 'out': globalOutCounter, 'six': globalSixCounter, 'wide': globalWideCounter}
winner = max(actionCount, key=actionCount.get)
if winner == 'noball' and globalNoBallCounter >th:
    globalNoBallVideo.append(buffer)
if winner == 'out'and globalOutCounter >th:
    globalOutVideo.append(buffer) 
if winner == 'six'and globalSixCounter >th:
    globalSixVideo.append(buffer)
if winner == 'wide' and globalWideCounter >th:
    globalWideVideo.append(buffer)

        
cv2.destroyAllWindows()

print ('Summarizing Video...')


if globalNoBallVideo!=[]:
    noBallVideo = cv2.VideoWriter('no_ball.avi',cv2.VideoWriter_fourcc(*'DIVX'), 25, size)
    for i in range(len(globalNoBallVideo)):
        for j in range(len(globalNoBallVideo[i])):
            # writing to a image array
            noBallVideo.write(globalNoBallVideo[i][j])
    noBallVideo.release()


if globalOutVideo!=[]:
    outVideo = cv2.VideoWriter('out.avi',cv2.VideoWriter_fourcc(*'DIVX'), 25, size)
    for i in range(len(globalOutVideo)):
        for j in range(len(globalOutVideo[i])):
            # writing to a image array
            outVideo.write(globalOutVideo[i][j])
    outVideo.release()    
    


if globalWideVideo!=[]:
    wideVideo = cv2.VideoWriter('wide.avi',cv2.VideoWriter_fourcc(*'DIVX'), 25, size)
    for i in range(len(globalWideVideo)):
        for j in range(len(globalWideVideo[i])):
            # writing to a image array
            wideVideo.write(globalWideVideo[i][j])
    wideVideo.release()
    

if globalSixVideo!=[]:
    sixVideo = cv2.VideoWriter('sixes.avi',cv2.VideoWriter_fourcc(*'DIVX'), 25, size)
    for i in range(len(globalSixVideo)):
        for j in range(len(globalSixVideo[i])):
            # writing to a image array
            sixVideo.write(globalSixVideo[i][j])
    sixVideo.release()
print("--- %s seconds ---" % (time.time() - start_time))
    

