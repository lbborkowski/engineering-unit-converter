# Engineering unit converter tool
# Created by Luke Borkowski on 06/12/16
# Input: given value(s); given units; desired units
# Output: value(s) in desired units
# Purpose: This tool allows the user to convert between any consistent units. 
#          The goal is for the tool to be lightweight and easy to use. This is 
#          accomplished by allowing the user to type the given and desired units 
#          rather than choosing from a list of units as most unit conversion tools require.
#          Also, the tool allows the user to convert an array of values of the same 
#          given units to an array in the desired units. 
# Method: The general steps performed in this tool include:
#           1. Reduced the given and desired units into their base (fundamental) units
#           2. Compare the given and desired base units to ensure consistency
#           3. Find the conversion factors between each base unit pair
#           4. Compute the overall conversion factor
#           5. Apply the overall conversion factor to the given value
#           6. Output the value in the desired unit system
  
from fractions import Fraction
import math
import csv
from Tkinter import *

#################################################################################
# functions #####################################################################
#################################################################################

def focus_next_window(event):
    event.widget.tk_focusNext().focus()
    return("break")

#################################################################################      
################################################################################# 

def focus_prev_window(event):
    event.widget.tk_focusPrev().focus()
    return("break")

#################################################################################      
#################################################################################

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

#################################################################################      
#################################################################################    

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
  
#################################################################################      
#################################################################################     

def readUnits():
  with open('Units.csv', 'r') as f:
    reader=csv.reader(f)
    unitList=list(reader)

  nUnits=len(unitList)

  cUnits=[]
  bUnits=[]
  bUnitsEx=[]
  c2bConvFac=[]
  for i in range(nUnits):
    cUnits.append(unitList[i][0])
    c2bConvFac.append(float(Fraction(unitList[i][2])))
    bUnitSep=sorted(list(find_all(unitList[i][1], '/'))+list(find_all(unitList[i][1], '*')))
    start=0
    temp=[]
    temp2=[1.0]
    temp3=[]
    if not bUnitSep:
      cLoc=unitList[i][1].find('^')
      if cLoc==-1:
        temp=[unitList[i][1]]
        temp3.append(1.0)
      else:
        temp=[unitList[i][1][:cLoc]]
        temp3.append(float(unitList[i][1][cLoc+1:]))
    else:
      for k in bUnitSep:
        if unitList[i][1][k]=='/':
          temp2.append(-1.0)
        elif unitList[i][1][k]=='*':
          temp2.append(1.0)
        cLoc=unitList[i][1][start:k].find('^')
        if cLoc==-1:
          temp.append(unitList[i][1][start:k])
          temp3.append(1.0)
        else:
          temp.append(unitList[i][1][start:start+cLoc])
          temp3.append(float(unitList[i][1][start+cLoc+1:k]))
      
        if k==bUnitSep[-1]:
          cLoc=unitList[i][1][k+1:].find('^')
          if cLoc==-1:
            temp.append(unitList[i][1][k+1:])
            temp3.append(1.0)
          else:
            temp.append(unitList[i][1][k+1:k+1+cLoc])
            temp3.append(float(unitList[i][1][k+2+cLoc:]))
      
        start=k+1

    for q in range(len(temp2)):
      temp2[q]=temp2[q]*temp3[q]
  
    bUnits.append(temp)
    bUnitsEx.append(temp2)
  
  return (cUnits,bUnits,bUnitsEx,c2bConvFac)

#################################################################################      
#################################################################################
  
def CompVals(event=None):

  text2.delete('1.0','end')
  text3.delete('1.0','end')

  givVals=text1.get('1.0','end')

  nVals=int(text1.index('end-1c').split('.')[0]) # line count

  givValsList=[]
  for i in range(nVals):
    if is_number(text1.get(str(i+1)+'.0',str(i+1)+'.end')):
      givValsList.append(float(text1.get(str(i+1)+'.0',str(i+1)+'.end')))
    else:
      text3.insert('end','***ERROR*** Entered value not a number' + '\n')
      return
  
  givUnit=entry1.get()
  desUnit=entry2.get()

  convFact=UnitConv(givValsList,givUnit,desUnit)

  desValsList=[]
  if (type(convFact)==float or type(convFact)==int):
    desValsList=[convFact*i for i in givValsList]
    for i in desValsList:
      text2.insert('end',str(format(i,'.8e'))+'\n')
    text3.insert('end','Unit conversion successful' + '\n')
  elif type(convFact)==str:
    text3.insert('end',convFact + '\n')
  elif type(convFact)==list:
    desValsList=convFact[:]
    for i in desValsList:
      text2.insert('end',str(format(i,'.8e'))+'\n')
    text3.insert('end','Unit conversion successful' + '\n')
  else:
    print 'SOMETHING IS WRONG'
    
#################################################################################      
#################################################################################

def UnitConv(givValsList,givUnit,desUnit):
  
  ## break given and desired unit expressions into components of array ##
  
  # find all instances of '/' and '*' in given and desired units
  givUnitSep=sorted(list(find_all(givUnit, '/'))+list(find_all(givUnit, '*')))
  desUnitSep=sorted(list(find_all(desUnit, '/'))+list(find_all(desUnit, '*')))
  
  # remove all the instances of '/' and '*' that are in exponent
  for i in givUnitSep:
    if is_number(givUnit[i+1]):
      givUnitSep.remove(i)
  for i in desUnitSep:
    if is_number(desUnit[i+1]):
      desUnitSep.remove(i)

  # create array containing all units in given units
  start=0
  temp1=[]
  temp2=[1.0]
  temp3=[]
  givUnitAr=[]
  givUnitEx=[]
  if not givUnitSep: 
    cLoc=givUnit.find('^')
    if cLoc==-1:
      temp1=[givUnit]
      temp3.append(1.0)
    else:
      temp1=[givUnit[:cLoc]]
      bparloc=givUnit.find('(')
      eparloc=givUnit.find(')')
      if bparloc==-1:
        temp3.append(float(givUnit[cLoc+1:]))
      else:
        if givUnit[cLoc+1]=='-':
          temp3.append(-1.0*float(Fraction(givUnit[bparloc+1:eparloc])))
        else:
          temp3.append(float(Fraction(givUnit[bparloc+1:eparloc])))  
  else:
    for i in givUnitSep:
      if givUnit[i]=='/':
        temp2.append(-1.0)
      elif givUnit[i]=='*':
        temp2.append(1.0)
      cLoc=givUnit[start:i].find('^')
      if cLoc==-1:
        temp1.append(givUnit[start:i])
        temp3.append(1.0)
      else:
        temp1.append(givUnit[start:start+cLoc])
        bparloc=givUnit[start+cLoc+1:i].find('(')
        eparloc=givUnit[start+cLoc+1:i].find(')')
        if bparloc==-1:
          temp3.append(float(givUnit[start+cLoc+1:i]))
        else:
          if givUnit[start+cLoc+1]=='-':
            temp3.append(-1.0*float(Fraction(givUnit[start+cLoc+1+bparloc+1:start+cLoc+1+eparloc])))
          else:
            temp3.append(float(Fraction(givUnit[start+cLoc+1+bparloc+1:start+cLoc+1+eparloc])))     

      if i==givUnitSep[-1]:
        cLoc=givUnit[i+1:].find('^')
        if cLoc==-1:
          temp1.append(givUnit[i+1:])
          temp3.append(1.0)
        else:
          temp1.append(givUnit[i+1:i+1+cLoc])
          bparloc=givUnit[i+1+cLoc+1:].find('(')
          eparloc=givUnit[i+1+cLoc+1:].find(')')
          if bparloc==-1:
            temp3.append(float(givUnit[i+1+cLoc+1:]))
          else:
            if givUnit[i+1+cLoc+1]=='-':
              temp3.append(-1.0*float(Fraction(givUnit[i+1+cLoc+1+bparloc+1:i+1+cLoc+1+eparloc])))
            else:
              temp3.append(float(Fraction(givUnit[i+1+cLoc+1+bparloc+1:i+1+cLoc+1+eparloc])))

      start=i+1

  for q in range(len(temp2)):
    temp2[q]=temp2[q]*temp3[q]
  
  givUnitAr=temp1
  givUnitEx=temp2

  # create array containing all units in desired units
  start=0
  temp1=[]
  temp2=[1.0]
  temp3=[]
  desUnitAr=[]
  desUnitEx=[]
  if not desUnitSep: 
    cLoc=desUnit.find('^')
    if cLoc==-1:
      temp1=[desUnit]
      temp3.append(1.0)
    else:
      temp1=[desUnit[:cLoc]]
      bparloc=desUnit.find('(')
      eparloc=desUnit.find(')')
      if bparloc==-1:
        temp3.append(float(desUnit[cLoc+1:]))
      else:
        if desUnit[cLoc+1]=='-':
          temp3.append(-1.0*float(Fraction(desUnit[bparloc+1:eparloc])))
        else:
          temp3.append(float(Fraction(desUnit[bparloc+1:eparloc])))  
  else:
    for i in desUnitSep:
      if desUnit[i]=='/':
        temp2.append(-1.0)
      elif desUnit[i]=='*':
        temp2.append(1.0)
      cLoc=desUnit[start:i].find('^')
      if cLoc==-1:
        temp1.append(desUnit[start:i])
        temp3.append(1.0)
      else:
        temp1.append(desUnit[start:start+cLoc])
        bparloc=desUnit[start+cLoc+1:i].find('(')
        eparloc=desUnit[start+cLoc+1:i].find(')')
        if bparloc==-1:
          temp3.append(float(desUnit[start+cLoc+1:i]))
        else:
          if desUnit[start+cLoc+1]=='-':
            temp3.append(-1.0*float(Fraction(desUnit[start+cLoc+1+bparloc+1:start+cLoc+1+eparloc])))
          else:
            temp3.append(float(Fraction(desUnit[start+cLoc+1+bparloc+1:start+cLoc+1+eparloc])))     

      if i==desUnitSep[-1]:
        cLoc=desUnit[i+1:].find('^')
        if cLoc==-1:
          temp1.append(desUnit[i+1:])
          temp3.append(1.0)
        else:
          temp1.append(desUnit[i+1:i+1+cLoc])
          bparloc=desUnit[i+1+cLoc+1:].find('(')
          eparloc=desUnit[i+1+cLoc+1:].find(')')
          if bparloc==-1:
            temp3.append(float(desUnit[i+1+cLoc+1:]))
          else:
            if desUnit[i+1+cLoc+1]=='-':
              temp3.append(-1.0*float(Fraction(desUnit[i+1+cLoc+1+bparloc+1:i+1+cLoc+1+eparloc])))
            else:
              temp3.append(float(Fraction(desUnit[i+1+cLoc+1+bparloc+1:i+1+cLoc+1+eparloc])))

      start=i+1

  for q in range(len(temp2)):
    temp2[q]=temp2[q]*temp3[q]
  
  desUnitAr=temp1
  desUnitEx=temp2

  # first check if simple temperature conversion
  if len(givUnitAr)==1 and len(desUnitAr)==1 and (givUnitAr[0]=='F' or givUnitAr[0]=='R' or givUnitAr[0]=='C' or givUnitAr[0]=='K') and (desUnitAr[0]=='F' or desUnitAr[0]=='R' or desUnitAr[0]=='C' or desUnitAr[0]=='K'):
    if (givUnitAr[0]=='F' and desUnitAr[0]=='C'):
      # desVal=(givVal-32.0)*5.0/9.0
      convFac=[(givVal-32.0)*5.0/9.0 for givVal in givValsList]
    elif (givUnitAr[0]=='K' and desUnitAr[0]=='C'):
      # desVal=givVal-273.15
      convFac=[givVal-273.15 for givVal in givValsList]
    elif (givUnitAr[0]=='R' and desUnitAr[0]=='C'):
      # desVal=(givVal-491.67)*5.0/9.0
      convFac=[(givVal-491.67)*5.0/9.0 for givVal in givValsList]
    elif (givUnitAr[0]=='C' and desUnitAr[0]=='K'):
      # desVal=givVal+273.15
      convFac=[givVal+273.15 for givVal in givValsList]
    elif (givUnitAr[0]=='F' and desUnitAr[0]=='K'):
      # desVal=(givVal+459.67)*5.0/9.0
      convFac=[(givVal+459.67)*5.0/9.0 for givVal in givValsList]
    elif (givUnitAr[0]=='R' and desUnitAr[0]=='K'):
      # desVal=givVal*5.0/9.0
      convFac=[givVal*5.0/9.0 for givVal in givValsList]
    elif (givUnitAr[0]=='C' and desUnitAr[0]=='F'):
      # desVal=givVal*9.0/5.0+32.0
      convFac=[givVal*9.0/5.0+32.0 for givVal in givValsList]
    elif (givUnitAr[0]=='R' and desUnitAr[0]=='F'):
      # desVal=givVal-459.67
      convFac=[givVal-459.67 for givVal in givValsList]
    elif (givUnitAr[0]=='K' and desUnitAr[0]=='F'):
      # desVal=givVal*9.0/5.0-459.67
      convFac=[givVal*9.0/5.0-459.67 for givVal in givValsList]
    elif (givUnitAr[0]=='F' and desUnitAr[0]=='R'):
      # desVal=givVal+459.67
      convFac=[givVal+459.67 for givVal in givValsList]
    elif (givUnitAr[0]=='C' and desUnitAr[0]=='R'):
      # desVal=(givVal+273.15)*9.0/5.0
      convFac=[(givVal+273.15)*9.0/5.0 for givVal in givValsList]
    elif (givUnitAr[0]=='K' and desUnitAr[0]=='R'):
      # desVal=givVal*9.0/5.0
      convFac=[givVal*9.0/5.0 for givVal in givValsList]
    return convFac
 
  # read in all available units and their respective base units and conversion factors
  cUnits,bUnits,bUnitsEx,c2bConvFac=readUnits()

  # separate given and desired units into base units
  convAr=[]
  givBsUnitAr=[] # given base unit array
  givBsUnitEx=[] # given base unit exponent array
  for i in range(len(givUnitAr)):
    if givUnitAr[i] in cUnits:
      ind=cUnits.index(givUnitAr[i])
      for n in bUnits[ind]:
        givBsUnitAr.append(n)
      for m in bUnitsEx[ind]:
        givBsUnitEx.append(m*givUnitEx[i])
      convAr.append(math.pow(c2bConvFac[ind],givUnitEx[i]))
    else:
      convFac='***ERROR***: Given unit [' + givUnitAr[i] + '] not recognized'
      return convFac

  desBsUnitAr=[] # desired base unit array
  desBsUnitEx=[] # desired base unit exponent array
  for i in range(len(desUnitAr)):
    if desUnitAr[i] in cUnits:
      ind=cUnits.index(desUnitAr[i])
      for n in bUnits[ind]:
        desBsUnitAr.append(n)
      for m in bUnitsEx[ind]:
        desBsUnitEx.append(m*desUnitEx[i])
      convAr.append(math.pow(1.0/c2bConvFac[ind],desUnitEx[i]))
    else:
      convFac='***ERROR***: Desired unit [' + desUnitAr[i] + '] not recognized'
      return convFac
  
  ##########################################################################################
  # combine like units
  # base units
  #   SI: m (L), kg (M), s (T), K (TH)
  #   US: in (L), slinch (M), s (T), R (TH)
  
  sumM=0
  sumKg=0
  sumS=0
  sumK=0
  sumIn=0
  sumSlinch=0
  sumR=0
  
  k=0
  for i in givBsUnitAr:
    if i=='m':
      sumM=sumM+givBsUnitEx[k]
    elif i=='kg':
      sumKg=sumKg+givBsUnitEx[k]
    elif i=='s':
      sumS=sumS+givBsUnitEx[k]
    elif i=='K':
      sumK=sumK+givBsUnitEx[k]
    elif i=='in':
      sumIn=sumIn+givBsUnitEx[k]
    elif i=='slinch':
      sumSlinch=sumSlinch+givBsUnitEx[k]
    elif i=='R':
      sumR=sumR+givBsUnitEx[k]
    k=k+1
  
  givSumM=sumM
  givSumKg=sumKg
  givSumS=sumS
  givSumK=sumK
  givSumIn=sumIn
  givSumSlinch=sumSlinch
  givSumR=sumR
  
  sumM=0
  sumKg=0
  sumS=0
  sumK=0
  sumIn=0
  sumSlinch=0
  sumR=0
  
  k=0
  for i in desBsUnitAr:
    if i=='m':
      sumM=sumM+desBsUnitEx[k]
    elif i=='kg':
      sumKg=sumKg+desBsUnitEx[k]
    elif i=='s':
      sumS=sumS+desBsUnitEx[k]
    elif i=='K':
      sumK=sumK+desBsUnitEx[k]
    elif i=='in':
      sumIn=sumIn+desBsUnitEx[k]
    elif i=='slinch':
      sumSlinch=sumSlinch+desBsUnitEx[k]
    elif i=='R':
      sumR=sumR+desBsUnitEx[k]
    k=k+1
  
  desSumM=sumM
  desSumKg=sumKg
  desSumS=sumS
  desSumK=sumK
  desSumIn=sumIn
  desSumSlinch=sumSlinch
  desSumR=sumR
    
  if givSumM != 0 and desSumM !=0:
    if givSumM > desSumM:
      givSumM=givSumM-desSumM
      desSumM=0
    else:
      desSumM=desSumM-givSumM
      givSumM=0
  
  if givSumKg != 0 and desSumKg !=0:
    if givSumKg > desSumKg:
      givSumKg=givSumKg-desSumKg
      desSumKg=0
    else:
      desSumKg=desSumKg-givSumKg
      givSumKg=0
  
  if givSumS != 0 and desSumS !=0:
    if givSumS > desSumS:
      givSumS=givSumS-desSumS
      desSumS=0
    else:
      desSumS=desSumS-givSumS
      givSumS=0
  
  if givSumK != 0 and desSumK !=0:
    if givSumK > desSumK:
      givSumK=givSumK-desSumK
      desSumK=0
    else:
      desSumK=desSumK-givSumK
      givSumK=0
  
  if givSumIn != 0 and desSumIn !=0:
    if givSumIn > desSumIn:
      givSumIn=givSumIn-desSumIn
      desSumIn=0
    else:
      desSumIn=desSumIn-givSumIn
      givSumIn=0
  
  if givSumSlinch != 0 and desSumSlinch !=0:
    if givSumSlinch > desSumSlinch:
      givSumSlinch=givSumSlinch-desSumSlinch
      desSumSlinch=0
    else:
      desSumSlinch=desSumSlinch-givSumSlinch
      givSumSlinch=0
  
  if givSumR != 0 and desSumR !=0:
    if givSumR > desSumR:
      givSumR=givSumR-desSumR
      desSumR=0
    else:
      desSumR=desSumR-givSumR
      givSumR=0
  
  givUnitFin=[]
  givUnitFinEx=[]
  if givSumM != 0:
    givUnitFin.append('m')
    givUnitFinEx.append(givSumM)
  if givSumKg != 0:
    givUnitFin.append('kg')
    givUnitFinEx.append(givSumKg)
  if givSumS != 0:
    givUnitFin.append('s')
    givUnitFinEx.append(givSumS)
  if givSumK != 0:
    givUnitFin.append('K')
    givUnitFinEx.append(givSumK)
  if givSumIn != 0:
    givUnitFin.append('in')
    givUnitFinEx.append(givSumIn)
  if givSumSlinch != 0:
    givUnitFin.append('slinch')
    givUnitFinEx.append(givSumSlinch)
  if givSumR != 0:
    givUnitFin.append('R')
    givUnitFinEx.append(givSumR)
  
  desUnitFin=[]
  desUnitFinEx=[]
  if desSumM != 0:
    desUnitFin.append('m')
    desUnitFinEx.append(desSumM)
  if desSumKg != 0:
    desUnitFin.append('kg')
    desUnitFinEx.append(desSumKg)
  if desSumS != 0:
    desUnitFin.append('s')
    desUnitFinEx.append(desSumS)
  if desSumK != 0:
    desUnitFin.append('K')
    desUnitFinEx.append(desSumK)
  if desSumIn != 0:
    desUnitFin.append('in')
    desUnitFinEx.append(desSumIn)
  if desSumSlinch != 0:
    desUnitFin.append('slinch')
    desUnitFinEx.append(desSumSlinch)
  if desSumR != 0:
    desUnitFin.append('R')
    desUnitFinEx.append(desSumR)
  
##########################################################################################
  
  # determine type of each unit
  givUnitFinTy=[]
  for i in givUnitFin:
    if (i=='m' or i=='in'):
      givUnitFinTy.append('L')
    elif (i=='kg' or i=='slinch'):
      givUnitFinTy.append('M')
    elif (i=='s'):
      givUnitFinTy.append('T')
    elif (i=='K' or i=='R'):
      givUnitFinTy.append('TH')
    else:
      print '***ERROR*** something is wrong'
  
  desUnitFinTy=[]
  for i in desUnitFin:
    if (i=='m' or i=='in'):
      desUnitFinTy.append('L')
    elif (i=='kg' or i=='slinch'):
      desUnitFinTy.append('M')
    elif (i=='s'):
      desUnitFinTy.append('T')
    elif (i=='K' or i=='R'):
      desUnitFinTy.append('TH')
    else:
      print '***ERROR*** something is wrong'
  
  together=zip(givUnitFinTy,givUnitFin,givUnitFinEx)
  sorted_together=sorted(together)
  givUnitFinTy=[x[0] for x in sorted_together]
  givUnitFin=[x[1] for x in sorted_together]
  givUnitFinEx=[x[2] for x in sorted_together]
  
  together=zip(desUnitFinTy,desUnitFin,desUnitFinEx)
  sorted_together=sorted(together)
  desUnitFinTy=[x[0] for x in sorted_together]
  desUnitFin=[x[1] for x in sorted_together]
  desUnitFinEx=[x[2] for x in sorted_together]
  
  if givUnitFinTy != desUnitFinTy:
    convFac='***ERROR***: Given and desired units are not consistent'
    return convFac
  
  if givUnitFinEx != desUnitFinEx:
    convFac='***ERROR***: Given and desired units are not consistent'
    return convFac
  
  # convert base units
  k=0
  for i in range(len(givUnitFinTy)):
    if (givUnitFin[i]=='m' and desUnitFin[i]=='in'):
      convAr.append(math.pow(1.0/0.02540000000000000,givUnitFinEx[k]))
    elif (givUnitFin[i]=='in' and desUnitFin[i]=='m'):
      convAr.append(math.pow(0.02540000000000000,givUnitFinEx[k]))
    elif (givUnitFin[i]=='kg' and desUnitFin[i]=='slinch'):
      convAr.append(math.pow(1.0/14.59390/12.0,givUnitFinEx[k]))
    elif (givUnitFin[i]=='slinch' and desUnitFin[i]=='kg'):
      convAr.append(math.pow(14.59390*12.0,givUnitFinEx[k]))
    elif (givUnitFin[i]=='K' and desUnitFin[i]=='R'):
      convAr.append(math.pow(9.0/5.0,givUnitFinEx[k]))
    elif (givUnitFin[i]=='R' and desUnitFin[i]=='K'):
      convAr.append(math.pow(5.0/9.0,givUnitFinEx[k]))
    k=k+1
  
  convFac=1
  for i in convAr:
    convFac=convFac*i
  
  return convFac


#################################################################################
# end functions #################################################################
#################################################################################

#################################################################################
# GUI ###########################################################################
#################################################################################

root=Tk()

root.wm_title("Engineering Unit Converter")

label1=Label(root,text='Given value(s)',font = "Verdana 10 bold")
label2=Label(root,text='Given units',font = "Verdana 10 bold")
label3=Label(root,text='Converted value(s)',font = "Verdana 10 bold")
label4=Label(root,text='Converted units',font = "Verdana 10 bold")
label5=Label(root,text='Messages',font = "Verdana 10 bold")

entry1=Entry(root,bd=4)
entry2=Entry(root,bd=4)

text1=Text(root,height=40,width=20,bd=4)
text1.grid(row=1,column=0,rowspan=40,padx=5,pady=(0,5))
text2=Text(root,height=40,width=20,bd=4)
text2.grid(row=1,column=2,rowspan=40,padx=5,pady=(0,5))
text3=Text(root,height=3,width=60,bd=4)
text3.grid(row=42,column=0,columnspan=3,padx=5,pady=(0,10),sticky=W)

label1.grid(row=0,column=0,padx=5,pady=(5,0))
label2.grid(row=0,column=1,padx=5,pady=(5,0))
label3.grid(row=0,column=2,padx=5,pady=(5,0))
label4.grid(row=2,column=1,padx=5,pady=(5,0))
label5.grid(row=41,column=0,padx=5,sticky=W)

entry1.grid(row=1,column=1,sticky=N,padx=5)
entry2.grid(row=3,column=1,sticky=N,padx=5)

button1=Button(root,text='>> Convert >>',command=CompVals,bd=4,font = "Verdana 10 bold")
button1.grid(row=6,column=1,sticky=N)

text1.bind("<Tab>", focus_next_window)
text2.bind("<Tab>", focus_next_window)
text3.bind("<Tab>", focus_next_window)
button1.bind("<Return>", CompVals)
root.bind("<F5>", CompVals)

text1.bind("<Shift-Tab>", focus_prev_window)
text2.bind("<Shift-Tab>", focus_prev_window)
text3.bind("<Shift-Tab>", focus_prev_window)

new_order=(text1,entry1,entry2,button1,text2,text3)
for widget in new_order:
  widget.lift()

root.mainloop()

#################################################################################
# end GUI #######################################################################
#################################################################################
