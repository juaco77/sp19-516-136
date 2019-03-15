import random
import sys
import os

print('Hello world')

# Comment
'''
Milti line comment
'''

name = "Joaquin"
print (name)

# 5 Main Types in Python Strings, Lists, Tuples, Dictionaries
# String

quote = "\"This is a test quote using escape charaters\""
multi_line_quote = ''' like with
comments, use three quotes'''

print (quote, multi_line_quote)
# reg exp to print new lines 5 times
print('\n' * 5)

print ("%s %s %s" % ('I like the quote', quote, multi_line_quote))

# List
grocery_list = ['Tomatoes',
                'Juice',
                'Milk',
                'Bananas']
print ('Firt Item', grocery_list[0])
grocery_list[2] = 'Soap'
print ('Firt Item', grocery_list[2])
print (grocery_list)
print(grocery_list[1:3])
#List Inside of List
other_events = ['Gardening','Housekeeping','Pool Maintenance']

toDoList = [other_events, grocery_list]
print('Full todo list: ',toDoList)
print('Part of todo list: ',((toDoList[0][0])))

grocery_list.append('Potatoes')
print(toDoList)

grocery_list.insert(1,'Pickle')
print('Added Pickle',toDoList)
grocery_list.remove('Pickle')
print('Removed Pickle',toDoList)
grocery_list.sort()
print('Sorted',toDoList)
grocery_list.reverse()
print('Reverse',toDoList)
del grocery_list[4]
print('Deleted 5th item',toDoList)

todoList2 = other_events + grocery_list
print('len',len(todoList2))
print('max',max(todoList2))
print('min',min(todoList2))

#Tuples cannot be changed

piTuple = (3,1,4,1,5,9)
newTuple = list(piTuple) #convert tuple to List
newList = tuple(newTuple) #convert list to Tuple

print(len(newList))
print(min(newList))
print(max(newList))


superVillains = {'Fiddler': 'Isaac Bowin',
                 'Captain Cold' : 'Leonard Snow',
                 'Weather Man' : 'Marky Mark',
                 'Mirror Guy' : 'Idon Know',
                 'Pied Piper' : 'John Gluten'}

print('superVillains',superVillains)
del(superVillains['Captain Cold'])
print('deleted one',superVillains)
superVillains['Fiddler'] = 'Johhny Walker'
print('changed Fiddler',superVillains)
print('len',len(superVillains))
print('get one',superVillains.get("Mirror Guy"))
print('keys',superVillains.keys())
print('values',superVillains.values())


# 7 Main Operators + - * / % ** (exponential multiplication) // floor division

print ("5+2=", 5+2)
print ("5-2=", 5-2)
print ("5*2=", 5*2)
print ("5/2=", 5/2)
print ("5%2=", 5%2)
print ("5**2=", 5**2)
print ("5//2=", 5//2)


'''
Order of operation matters
Multiplication happens first in the next example.
It is important to use ()
Example:
'''

print("1 + 2 - 3 * 2 =",1 + 2 - 3 * 2)
print("(1 + 2 - 3) * 2 =",(1 + 2 - 3) * 2)


#Conditions
'''
if
else
elif
==
!=
>
>=
<=
'''

age = 21

if age > 16 :
    print('You are old enough to drive')
else:
    print('You are not')

if age>=21 :
    print('Greater or equal than 21')
elif age >= 16:
    print('Something else')
else:
    print('Whatever')

if ((age >= 1) and (age <= 18)):
    print ('You get a birthday')
elif ((age ==21) or (age >= 65)):
    print ('something')
elif not(age == 30):
    print ('You dont')
else:
    print('else')

# Loops

for x in range(0,10):
    print(x, ' ', end="")

print('\n')

for y in grocery_list:
    print(y)

for x in [2,4,6,8,10]:
    print(x)

numList = [[1,2,3],[10,20,30],[100,200,300]]

for x in range(0,3):
    for y in range(0,3):
        print(numList[x][y])


randomNumber = random.randrange(0,100)

while(randomNumber!=15):
    print(randomNumber)
    randomNumber = random.randrange(0,100)




























