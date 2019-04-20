import os

accept_second = 30
frame_per_second = 1
miss_rate = 4*frame_per_second
confident_rate = 0.7
similar_rate = 70
list_car_label = [2,3,4,6,7,8] # coco label
path_bg = '/content/drive/My Drive/AIC_2019_Train_Cut/cut_video_bg_frames'
# path_bg = '.'
# format <file-number>/result/<frame-number>.txt
# format txt x1,y1, x2,y2, confidence, label 
path_result = '/content/drive/My Drive/AIC_2019_Train_Cut/anomaly'
# path_result = '.'
ans = []

#calculate intersection of 2 rectangle
def intersectArea(a, b):
    dx = min(a[0]+a[2], b[0]+b[2]) - max(a[0], b[0])
    dy = min(a[1]+a[3], b[1]+b[3]) - max(a[1], b[1])
    if (dx>=0) and (dy>=0):
        return dx*dy
    return 0

#calculate similarity (%)
def similar(a, b):
    average = ((a[2]*a[3]) + (b[2]*b[3])) / 2
    # minArea = min(a[2]*a[3], b[2]*b[3])
    intersect = intersectArea(a, b)
    return (float(intersect) / float(average)) * 100

#update list of car after 1 frame [x,y,w,h,t,tlast, confidence] (0->5) 6 label
def update(cars, oneFrame, time):
    for i in oneFrame:
        check = False
        co = 0
        #check if it exist before (%)
        for j in cars:
            if similar(i, j) > similar_rate:
                check = True
                j[6] = i[4]
                j[5] = time
                # open region of car
                j[2] = max(i[2]+i[0], j[2]+j[0]) - min(i[0], j[0])
                j[3] = max(i[3]+i[1], j[3]+j[1]) - min(i[1], j[1])
                j[0] = min(i[0], j[0])
                j[1] = min(i[1], j[1])
                
            co += 1
        #add car if it not exist before
        if check == False:
            newCar = [i[0], i[1], i[2], i[3], time, time, i[4]]
            cars.append(newCar)
    #remove car don't exist anymore
    newList = []
    for i in cars:
        if time <= i[5] + miss_rate:
            newList.append(i)
            # first time -> update ans
        elif time - i[4] > accept_second*frame_per_second:
            ans.append(i)
    return newList

def compress():
    newList = []
    for x in ans:
        if len(newList) == 0:
            newList.append(x)
        else:
            check = 0
            for y in newList:
                # < miss_rate => 1 anomaly 
                if y[4]-x[5] < miss_rate:
                    check = 1
                    y[5]=max(x[5], y[5])
                    break
            if check==0:
                newList.append(x)

    return newList

def readCar(pathFileTxt):
    f = open(pathFileTxt, "r")
    currentCars=[]
    for line in f:
        temp = [float(x) for x in line.split()]
        # convert to x,y,w,h
        temp[2] = temp[2] - temp[0]
        temp[3] = temp[3] - temp[1]
        if (temp[5] in list_car_label) and (temp[2]*temp[3] < 100*200) and (temp[4] > confident_rate):
            currentCars.append(temp)
    return currentCars

resultFinalPath = "result_final.txt"
MainResult = open(os.path.join(path_result, resultFinalPath), "a")
MainResult.write('accept_second %d\n' %accept_second) 
MainResult.write('miss_rate %d\n' %miss_rate)
MainResult.write('confidence %f\n' %confident_rate)
MainResult.write('similar_rate %d\n' %similar_rate)
MainResult.write('################################\n')
#for each video
for i in range(1,100):
    path_oneVideo = os.path.join(path_bg, str(i))
    path_oneVideo = os.path.join(path_oneVideo, 'result')
    #if folder background exist
    if not os.path.exists(path_oneVideo):
        continue
    print("work with " + str(i))
    resultPath = "result" + str(i) + ".txt"
    result = open(os.path.join(path_result, resultPath), "w")
    cars = []
    ans = []
    txts = os.listdir(path_oneVideo)
    txts.sort()

    #in each frame
    co = 0
    longest = 0
    for j in txts:
        if j.endswith('.txt'):
            oneFrame = readCar(os.path.join(path_oneVideo, j))
            cars = update(cars, oneFrame, co)
            if co%(frame_per_second*10)==0:
                print(cars)
                # print for test 
                result.write("\n")
                result.write(str(co) + ": ")
                for xx in cars:
                    result.write("(" + str(xx[0]) + "," + str(xx[1]) + "," + str(xx[2]) + "," + str(xx[3]) + "," + str(xx[4]) + ") ")
                    result.write("\n")
            co += 1

    # for cars stay to end of video    
    for x in cars:
        if co - x[4] > accept_second * frame_per_second:
            ans.append(x)
    ans = compress()

    #print result
    for (x,y,w,h,t,tlast,label) in ans:
        second = int (t / frame_per_second)
        resultString = str(i) + " " + str(second)
        MainResult.write(resultString + "\n")
        print(resultString)

    result.close()

MainResult.write('################################\n')
MainResult.close()