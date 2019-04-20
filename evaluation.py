import math
import numpy as np


def readFile(file):
  array = []
  with open(file) as f:
    for line in f:  # read rest of lines
      video_id, time = [int(x) for x in line.split()]
      # print(video_id, time)
      array.append([video_id, time])
  return array
  
ground_truth = readFile("ground_truth_cut.txt")
my_result = readFile("my_result.txt")

topTeamResult = [
    [0.8649, 0.8649, 3.6152],
    [0.7853, 0.8108, 10.2369],
    [0.4951, 0.6286, 48.3406],
    [0.2638, 0.4762, 97.5505],
    [0.064, 0.2363, 157.2298],
    [0.0069, 0.7567, 212.3274],
    [0, 0.7692, 214.2712]
]



# print(ground_truth)
# print(my_result)

def countTruePositive():
  count = 0
  for res in my_result:
    for gt in ground_truth:
      if (res[0] == gt[0] and abs(res[1] - gt[1]) <= 300):
        count += 1
  return count


def countFalsePositive():
  count = 0
  for res in my_result:
    yes = False
    for gt in ground_truth:
      if (res[0] == gt[0] and abs(res[1] - gt[1]) <= 300):
        yes = True
    if not(yes):
      count += 1
  return count


def countFalseNegative():
  count = 0
  for gt in ground_truth:
    yes = False
    for res in my_result:
      if (res[0] == gt[0] and abs(res[1] - gt[1]) <= 300):
        yes = True
    if not(yes):
      count += 1
  return count

def calcPrecision():
  tp = countTruePositive()
  fp = countFalsePositive()
  # print(tp, fp)
  return float(float(tp) / float(tp + fp))

def calcRecall():
  tp = countTruePositive()
  fn = countFalseNegative()
  # print(tp, fn)
  return float(float(tp) / float(tp + fn))

def F1():
  recall = calcRecall()
  precision = calcPrecision()
  # print(recall, precision)
  f1 = (2 * recall * precision) / (recall + precision)
  print("F1: ", f1)
  return f1


def RSME():
  count = 0
  sum = 0
  for res in my_result:
    for gt in ground_truth:
      if (res[0] == gt[0] and abs(res[1] - gt[1]) <= 300):
        sum += (abs(res[1] - gt[1]) ** 2)
        count += 1
  # print(count, sum)
  return math.sqrt(sum / count)

def NRSME():
  ourRSME = RSME()
  print(ourRSME)
  maxVal = minVal = topTeamResult[0][2]
  for val in topTeamResult:
    maxVal = max(maxVal, val[2])
    minVal = min(minVal, val[2])
  # print(minVal, maxVal)
  return (ourRSME - minVal) / (maxVal - minVal)


def calcS2():
  ourF1 = F1()
  ourNRSME = NRSME()
  return ourF1 * (1 - ourNRSME)

print("S2: ", calcS2())