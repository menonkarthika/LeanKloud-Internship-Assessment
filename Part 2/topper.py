# -*- coding: utf-8 -*-
"""
Created on Sat May 22 18:38:12 2021

@author: Karthika
"""

import pandas as pd

df = pd.read_csv("C:\\Users\\Hp\\Desktop\\LeanKloud\\Student_marks_list.csv")

subjects=["Maths","Biology","English","Physics","Chemistry","Hindi"]
toppers=[]
for sub in subjects:
    column = df[sub]
    max_value = column.max()
    arr=df.loc[df[sub] == max_value]
    arr=arr["Name"].values
    toppers.append(arr)
    


df['Sum'] = df.Maths + df.Biology + df.English + df.Physics + df.Chemistry + df.Hindi

sorted = df.sort_values(['Sum'], ascending=False).groupby('Sum').head(3)

list = sorted['Name'].tolist()

i=0
top3=[]



for i in range(3):
    top3.append(list[i])
    


i=0
for i in range(6):
    if(toppers[i].size==1):
        print("\nTopper in", subjects[i],"is", ''.join(toppers[i]))
    else:
        j=0
        print("\nToppers in", subjects[i],"are ", end="")
        while(j<toppers[i].size):
            if(j==toppers[i].size-1):
                print(toppers[i][j])
            else:
                print(toppers[i][j],"and ",end="")
            j+=1
            
   
      
print("\n")

j=0
print("\nBest students in the class are ", end="")
while(j<3):
    if(j==2):
        print(top3[j])
    else:
        print(top3[j],",",end="")
    j+=1
    


print("\nTo find topper in each subject, loop through every row for that column. Assume there are n rows (students) for 6 subjects")
print("\nHence complexity to find topper in each subject is O(row*col) i.e, O(n*6) => O(n)")
print("\n-------------------------------------------------------------------------------------------------------------------------")
print("\n\nTo find best students the sum of their scores is first tabulated and the complexity for this is again O(n*6) => O(n)")
print("\nThe total scores are then sorted in descending order and the complexity for this is O(nlogn) ")
print("\nFinally the top 3 students are obtained from the sorted array and the complexity for this is O(3)  ")
print("\nHence the complexity for obtaining top 3 students is O(n)+O(nlogn)+O(3) => O(nlogn)")






    