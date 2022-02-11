#General purpose utility functions.
#File name: utils.py

import os
import math

#------ List of functions: --------------------------------------------------
#cls()                                 Windows clear the terminal screen.
#clear()                               Linux clear the terminal screen.
#    For following three, num is the number, x is the following index in s.
#num, x= get_float(s, i=0)             Convert and return float at i.
#num, x= get_int(s, i=0)               Convert and return int at i.
#num, x= find_int(s, i=0)              Starting at i, find and return int.
#dd    = dms_to_dd(dms)                Convert angle in deg/min/sec to decimal.
#entries= line_parser(line, num_fields) Parse line into fields, include commas
#    Convert to a formatted string (num may be a string or a number).
#ret_str= fmt(num, tot=0, right=0, just=0, none_space=1, leading_z=0)
#m, i+3= convert_month(s, i)           Convert 3 char month to int, "jan"=1.
#year, month, day, hour= get_date(s)   Convert string to year, month, day, h.
#    Convert line, a string, to a list of fields.
#ret_line= get_fields(line, lst, widths=0, digs=0, nans=0)
#s[i1:i2], i3= divide_field(s, i)      Return string split on space at i.
#data_copy= copy_data(data)            Return deep copy of a list.
#count= count_vals(s)                  Count number of valid numeric values.
#True/False= nan_check(s, i)           Check for valid nan at position i.
#True/False= isdata(d, no_data=None)   Returns True if d contains data.
#info(a, type1="", pause=30)           Display information about the object: a.
#lst_info(lst, pause=30)               Display info about the fields of lst.

#------------------ cls -----------------------------------------------------
#Call the Windows clear screen function to clear the python command terminal.
def cls():
  os.system('cls')
#End cls

#------------------ clear ---------------------------------------------------
#Call the Linux clear screen function to clear the python command terminal.
def clear():
  os.system('clear')
#End clear

#------------------ get_float -----------------------------------------------
#Find, convert and return the first float found starting at position i,
#skipping leading spaces. Also return the index just after the last digit
#position. Works with Scientific Notation if e/E present before exponent.
#If nan or NaN discovered, then math.nan will be returned. 
#If conversion failed, value will be None. If end of string, index will be -1.
def get_float(s, i=0):
  decimal_flag=0                       #Keep track of whether dec pt was found.
  digit_flag=0                         #Keep track of whether digit was found.
  sn_flag=0                            #Set scientific notation flag.
  e_index=0                            #Index where e/E was found for SN.

  if type(s)!=str:                     #Check for invalid input.
    return None, -1

  len_s=len(s)
  if len_s<1 or i>=len_s:              #Check for empty string or invalid i.
    return None, -1

  while i<len_s and s[i]=='\n':        #Skip leading new-lines.
    i+=1
  while i<len_s and (s[i]==' ' or s[i]=='\t'):   #Skip leading spaces/tabs.
    i+=1
  if i>=len_s:                         #Check for end of string.
    return None, -1

  s=s.lower()                          #Convert to lower case for nan and exp.
  if s[i]=='n':                        #If 3 or more characters, check for nan.
    if nan_check(s, i):                #If a valid nan is present,
      return math.nan, i+3             #return math.nan.

  for x in range(i, len_s):            #Loop through each character in string.
    if (s[x]=='+' or s[x]=='-'):       #If a sign char was found, then
      if x==i:                         #if it was the first char, continue with
        continue                       #remainder of the string, otherwise
      elif sn_flag and s[x-1]=='e':
        continue
      else:                            #exit from processing characters.
        break
    elif s[x]=='.':                    #If decimal point was found, then
      if decimal_flag==1:              #if one was already found, exit loop,
        x-=1                           #Otherwise, remove second decimal point
        break                          #and exit loop.
      decimal_flag=1                   #set the decimal flag.
    elif s[x].isdigit():               #If digit was found, set digit flag so
      digit_flag=1                     #that we know later a digit was present.
    #Check for scientific notation.
    elif (s[x]=='e') and digit_flag and not sn_flag:
      sn_flag=1
      e_index=x
    else:                              #Otherwise, an invalid character was
      break                            #found so we should exit the loop.
  
  if not digit_flag:                   #If no digit was found,
    return None, x                     #then return None!

  while x>i and (s[x]=='e' or s[x]=='+' or s[x]=='-'):
    x=x-1                              #Remove trailing sn characters.

  if s[x].isdigit():                   #If the last character was a digit,
    x+=1                               #then include it in the conversion.
  elif x==i:                           #Otherwise, if we found no valid
    return None, x                     #characters, then return None.

  num=float(s[i:x])                    #Convert section of string to a float.
  if x<len_s and s[x]=='\n':           #If last char is a newline, inc index.
    x+=1
  return num, x
#End get_float

#------------------ get_int -------------------------------------------------
#Find, convert and return the first integer found starting at position i,
#skipping leading spaces. Also return the index just after the last digit
#position. If nan or NaN discovered, then math.nan will be returned.
#If conversion failed, value will be None. If end of string, index will be -1.
def get_int(s, i=0):
  if type(s)==list and len(s)>i:
    s=s[i]
  if type(s)!=str:                     #Check for invalid input.
    return None, i
 
  len_s=len(s)
  if len_s<1 or i>=len_s:              #Check for empty string or invalid i.
    return None, -1

  while i<len_s and s[i]=='\n':        #Skip leading new-lines.
    i+=1
  while i<len_s and (s[i]==' ' or s[i]=='\t'):   #Skip leading spaces/tabs.
    i+=1
  if i>=len_s:                         #Return if end of string encountered.
    return None, -1

  if len_s-i>2:                        #If 3 or more characters, check for nan
    s=s.lower()                        #Convert to lower case.
    if s[i]=='n' and s[i+1]=='a' and s[i+2]=='n':  #If nan, return nan.
      return math.nan, i+3

  for x in range(i, len_s):
    if (s[x]=='+' or s[x]=='-'):
      if x==i:
        continue
      else:
        break
    elif not s[x].isdigit():
      break
  
  if s[x].isdigit():
    x+=1
  elif x==i or s[x-1]=='+' or s[x-1]=='-':
    return None, i

  num=int(s[i:x])                      #Convert section of string to an int.
  if x<len_s and s[x]=='\n':           #If last char is a newline, inc index.
    x+=1
  return num, x
#End get_int

#------------------ find_int ------------------------------------------------
#Similar to get_int except skips all non digit characters until a digit
#is found, at which point, convert all the contiguous digits to a single
#integer. Return this integer and the ending index. Return None on failure.
def find_int(s, i=0):
  len_s=len(s)
  if len_s==0 or i>=len_s:             #Return if no string, or end of string.
    return None, -1
  while i<len_s and not s[i].isdigit():#Skip leading non-digit characters.
    i+=1

  if i>=len_s:                         #Return if no digits found.
    return None, -1
  elif i>0 and s[i-1]=='-':            #If previous character was a negative
    i-=1                               #sign, then keep it.

  x=i+1
  while x<len_s and s[x].isdigit():    #Find the last digit.
    x+=1

  num=int(s[i:x])                      #Convert section of string to an int.
  if x<len_s and s[x]=='\n':           #If last char is a newline, inc index.
    x+=1
  return num, x

#End find_int

#------------------ dms_to_dd -----------------------------------------------
#Convert angle in degree / minute / second to decimal degrees. Works with
#Geo coordinates with N/S or E/W appended returning negative value for S/W.
def dms_to_dd(dms):
  d, i=find_int(dms)
  m, i=find_int(dms, i)
  s, i=find_int(dms, i)
  dd=float(d)+float(m)/60.0+float(s)/3600.0
  while i<len(dms) and dms[i]==" ":    #Skip white space.
    i+=1
  dms=dms.lower()
  #If last character is an S/s or W/w, convert value to negative.
  if i<len(dms) and (dms[i]=="s" or dms[i]=="w"):
    dd=-dd
  return dd
#End dms_to_dd

#------------------ line_parser ---------------------------------------------
#My custom parser that deals correctly with commas embedded within a field.
#It will keep the comma as part of the field but remove the quotes. Returns a
#list with the fields as strings. If num_fields number of fields not found,
#returns an integer representing the number of fields found. If a field
#contains a comma, the field must start and end with a quote.
#Returns -1 on error.
def line_parser(line, num_fields):
  entries=[]
  if type(line)!=str or len(line)<(num_fields-1):
    return -1

  start=0
  q_flag=False
  l=len(line)
  for x in range(l):
    #Check for end of field, start of next, or end-of-line.
    if (line[x]=="," and q_flag==False) or x==l-1:
      if x==l-1:                       #If at the end of the string, increment
        x+=1                           #x to handle last character properly.
      #Check for mismatched parenthesis; if so, return an error immediately.
      if (line[start]=='"' and line[x-1]!='"') or  \
         (line[start]!='"' and line[x-1]=='"'):
        return -1
      elif line[start]=='"' and line[x-1]=='"':  #Otherwise, check for matched
        entries.append(line[start+1:x-1])        #parens to remove,
      else:                                      #otherwise,
        entries.append(line[start:x])            #add as is.
      start=x+1
    elif line[x]=='"':
      q_flag=not q_flag

  if len(entries)!=num_fields:
    return len(entries)
  return entries
#End line_parser

#------------------ fmt -----------------------------------------------------
#My custom formatter since I am tired of dealing with Python's!
#Pass number or string, total width of returned string, number of digits to
#the right of the decimal place (0 default), 0/1/2 for justification
#(default=0 or right) 1=Left and 2=Center, none_space enables
#replacing the word "None" with spaces (default=1 for replacing),
#leading_z=1 for leading zeros instead of leading spaces
#(default=0 for leading spaces). leading_z is ignored if just is 1 or 2.
#If total width of 0 is indicated (tot==0), then the value will be converted
#directly with no additional formatting; exception for None value which will
#still be converted to space if none_flag>0.
#Returns formatted string.
def fmt(num, tot=0, right=0, just=0, none_space=1, leading_z=0):
  if tot==0:                           #tot of 0 indicates return as simple
    if num==None and none_space:       #string. However, None value should
      return ""                        #be converted based on none_space.
    else:
      return str(num)
  if tot<right:                        #Sanity check.
    tot=right

  if type(num)==int:                   #Process an integer.
    ret_str=str(num)
    if right>0:
      ret_str+="."+right*"0"
  elif type(num)==float:               #Process a float.
    if math.isnan(num):                #Process a NaN value!
      ret_str=str(num)
    elif right<1:
      ret_str=str(round(num))
    else:
      #Determine digits on left of decimal place including negative sign.
      if abs(num)<1.0:
        left=0
      else:
        left=int(math.log(abs(num), 10))+1
      if num<0.0:                      #If negative value, include on left one
        left+=1                        #space for the sign.
      r=tot-left-1                     #Determine how much room on right.
      if r<right:                      #If the available digits on right is
        right=r                        #less than number requested, adjust!
      digits=pow(10.0, right)
      ret_str=str(round(num*digits)/digits)
      i=0
      while ret_str[i]!='.':
        i+=1
      l=right-(len(ret_str)-i-1)
      ret_str+=l*"0"
  elif type(num)==str:                 #Process a string!
    ret_str=num
  elif num==None:                      #Process the None type.
    ret_str=str(None) if none_space==0 else "      "
  else:                                #Otherwise, return spaces only.
    return tot*" "

  l=len(ret_str)
  if l>tot:                            #Here we need to truncate.
    ret_str=ret_str[0:tot]
    if ret_str[-1]=='.':               #Remove trailing decimal points.
      ret_str=ret_str[0:-1]
    l=len(ret_str)

  if l<tot:                            #Here we need to pad with spaces.
    if just==0:                        #Right justify.
      if leading_z==0:
        ret_str=(tot-l)*" " + ret_str
      else:
        ret_str=(tot-l)*"0" + ret_str
    elif just==1:                      #Left justify (no option or trailing 0).
      ret_str+=(tot-l)*" "
    else:                              #Center, ignore leading option.
      tmp=tot-l
      rside=tmp//2
      lside=tmp-rside
      ret_str=lside*" "+ret_str+rside*" "
  #Now, if string is too long, attempt to truncate decimal places.
  l=len(ret_str)
  if "." in ret_str and l>tot and right>0 and num>1.0 and type(num)==float:
    i1=ret_str.rfind(".")
    if i1>=(tot-1):
      ret_str=ret_str[0:i1]
    else:
      ret_str=ret_str[0:tot]
  return ret_str
#End fmt

#------------------ convert_month --------------------------------------------
#Convert the letter designated month at position i to an int (1 to 12)
#Converts the letters to lower before processing.
#Returns 1 to 12 for the month and the index of the next character after.
def convert_month(s, i):
  s=s.lower()                          #Ensure lower case.
  if s[i:i+3]=="jan":
    m=1
  elif s[i:i+3]=="feb":
    m=2
  elif s[i:i+3]=="mar":
    m=3
  elif s[i:i+3]=="apr":
    m=4
  elif s[i:i+3]=="may":
    m=5
  elif s[i:i+3]=="jun":
    m=6
  elif s[i:i+3]=="jul":
    m=7
  elif s[i:i+3]=="aug":
    m=8
  elif s[i:i+3]=="sep":
    m=9
  elif s[i:i+3]=="oct":
    m=10
  elif s[i:i+3]=="nov":
    m=11
  elif s[i:i+3]=="dec":
    m=12
  else:
    m=1
  return m, i+3
#End convert_month

#------------------ get_date ------------------------------------------------
#From a string containing year, month, day, hour, convert and return them.
#If month is in name form, convert to integer. Return 1 for missing values.
#If invalid value is found, attempts to correct such as converting a negative
#value to the smallest for that field.
def get_date(s):
  len_s=len(s)
  i=0
  if len_s<4:                          #If string too short, return all
    return 1964, 1, 1, 0               #default values.

  s=s.lower()                          #Convert month to lower case chars.
  year, i=get_int(s, i)                #Get the year.
  if year<1964:
    year=1964
  elif year>2018:
    year=2018
  if s[i]==',':                        #Skip commas.
    i+=1

  month, i=get_int(s, i)               #Get the month.
  if s[i]>='a' and s[i]<='z':          #If month is in letter form,
    month, i=convert_month(s, i)       #convert to ordinal
  if month<1:
    month=1
  elif month>12:
    month=12
  if s[i]==',':                        #Skip commas.
    i+=1

  day, i=get_int(s, i)
  if day<1:
    day=1
  elif day>31:
    day=31
  if s[i]==',':                        #Skip commas.
    i+=1

  hour, i=get_int(s, i)
  if hour<0:
    hour=0
  elif hour>23:
    hour=23
  
  return year, month, day, hour
#End get_date

#------------------ get_fields ----------------------------------------------
#Get a list of fields from line and return as a string. lst is a list of
#integer values representing the field indices to retrieve. Thus, if there are
#10 fields in line and lst=[1, 4, 10], extract these fields only, convert to
#a string and return. widths, digs, and nans can be lists with additional
#formatting options for each extracted fields where widths contains the width
#value of each converted field, digs contains number of digits to be kepts, and
#nans indicates the maximum allowed value for each specific field where, if
#the converted value is larger than its associated value in nans, it will be
#converted to math.nan. In Python, nan is considered a float type, whereas
#None is nothing (it is its own type).
#Indices in lst use 1 based indexing, NOT 0!
def get_fields(line, lst, widths=0, digs=0, nans=0):
  if type(widths)!=int:                #If additional formatting arguments
    fmt_flag=True                      #passed in, set flag to True.
  else:
    fmt_flag=False

  len_l=len(lst)
  len_s=len(line)
  ret_line=""
  if len_l<1 or len_s<1:
    return ret_line

  i=count=0
  lst_index=0
  while i<len_s and i>=0:
    count+=1
    val, i=get_float(line, i)
    if val!=None and val==int(val):
      val=int(val)
    if count==lst[lst_index]:
      if fmt_flag:
        if val>=nans[lst_index]:
          val=math.nan
        ret_line+=fmt(val, widths[lst_index], digs[lst_index], 1)
      else:
        if count>1:
          ret_line+=("\t")
        ret_line+=str(val)
      lst_index+=1

  return ret_line
#End get_fields

#------------------ divide_field --------------------------------------------
#Split up a line of text without breaking up a word (split on a space). s is
#the string to divide, i is the width of the desired returned string.
#Returns the first i characters from s up to a space and the index for the
#next non-space character so that s can be continued from the returned index.
#Also trims white-space from the beginning of the returned string.
#Returns an empty string and 0 on error.
def divide_field(s, i):
  if type(s)!=str or type(i)!=int or i<1 or len(s)==0:
    return "", 0
  len_s=len(s)
  sl=s.lstrip()                        #Strip whitespace from left side only.
  if len(sl)==0:                       #String only contains white-space!
    return "", len_s

  i1=len_s-len(sl)                     #Get index to first non-white-space char
  i3=min(i+i1, len_s)                  #Index to return for next character.
  if i3==len_s:                        #All done, return stripped string.
    return s.strip(), len_s

  i2=i3                                #i2 is ending point for returned string.
  if s[i3].isspace():                  #Search left for end of white-space.
    while i2>i1 and s[i2].isspace():   #Scan back to end of text.
      i2-=1
    i2+=1                              #Inc to last white-space encountered.
    while i3<len_s and s[i3].isspace(): #Scan to start of next text.
      i3+=1                            #i3 will be index to start of next text.
  else:                                #Scan left to white-space.
    while i3>i1 and not s[i3].isspace():
      i3-=1
    if i3==i1:                         #If no white-space found, then
      i3=i2                            #we will have to break a word!
    else:                              #Otherwise, find beginning of text.
      i2=i3-1                          #Now find end of text.
      while i2>i1 and s[i2].isspace():
        i2-=1
      i2+=1                            #Inc to last white-space encountered.
      i3+=1                            #Inc to first non-white space.

  return s[i1:i2], i3
#End divide_field

#------------------ copy_data -----------------------------------------------
#Return a deep copy of data in list form.
def copy_data(data):
  data_copy=[]
  for i in data:
    try:
      data_copy.append(i[:])           #Treat as a list object, on failure
    except:                            #treat as a non-list object.
      data_copy.append(i)

  return data_copy
#End copy_data

#------------------ count_vals -----------------------------------------------
#Find all valid numeric values (including NaN, which Python considers a float)
#in the string s, and return the count.
#Skip all leading non-numeric characters, but if non-numeric character is
#encountered after the first number, then quit counting.
def count_vals(s):
  i=count=0
  len_s=len(s)
  if len_s==0:                         #Return if no string.
    return count

  s=s.lower()                          #Convert for nan and exp checks.
  while i<len_s and not s[i].isdigit():  #Skip leading non-digit chars.
    if s[i]=='n' and i+2<len_s:        #There may be a nan present.
      if nan_check(s, i):              #If there is a valid nan, break
        break                          #the loop.
    i+=1

  while i<len_s:                       #Process remainder of string.
    val, i=get_float(s, i)
    if type(val)==float:               #If a float was encountered, increment
      count+=1                         #the count and continue.
    else:                              #Otherwise, set index to exit.
      i=len_s

  return count
#End count_vals

#------------------ nan_check ------------------------------------------------
#Determine if the point in the string at i contains a valid nan. There
#must be either a white space or string termination at the beginning and end.
#Only checks for lower case nan!
def nan_check(s, i):
  len_s=len(s)
  if len_s-i<3:                        #Return false if too few characters
    return False

  nan_flag=0
  if s[i]=='n' and s[i+1]=='a' and s[i+2]=='n':
    #We have "nan", now check for beginning of string, or leading w space.
    if (i>0 and (s[i-1]==' ' or s[i-1]=='\t' or s[i-1]=='\n')) or i==0:
      nan_flag+=1
    #We have "nan", now check for end of string, or trailing white space.
    if (i+3<len_s and (s[i+3]==' ' or s[i+3]=='\t' or s[i+3]=='\n')) \
        or i+3==len_s:
      nan_flag+=1
    #Did we have a space or beginning/end at each end of the "nan"?
    if nan_flag==2:
      return True                      #If so, this is a float/nan, so exit.

  return False
#End nan_check

#------------------ isdata ---------------------------------------------------
#Return True if d contains any kind of usable data. Return False for empty
#strings but True for any numeric type. If d is a list, check each
#entry in the list and, if any contains data, return True.
#If no_data contains a value, then this value will be used in the comparison
#for a lack of data. Thus, if d is equal to no_data, then there is no data and
#False will be returned.
def isdata(d, no_data=None):
  if type(d)==None:                    #None implies no data!
    return False
  elif type(d)==int or type(d)==float: #Ints and floats must contain data, even
    return not d==no_data              #if it is just 0 so compare to default.
  elif type(d)==str:
    if len(d)==0:
      return False                     #An empty string contains no data.
    return not d==no_data              #Otherwise, compare to no_data value.
  elif type(d)==list:
    for i in d:                        #If any element of the list contains
      if isdata(i, no_data):           #data, then return True,
        return True                    #else
    return False                       #return False
  #Additional data types here as needed them.

  return False                         #If uncertain, return False!
#End isdata

#------------------ info -----------------------------------------------------
#Display information about the object passed. Also list the avaliable methods.
#If type1 contains a type, then display only that type.
#If the type is invalid, then display everything.
#type1 can also be "method" or "function" for only displaying these.
#Pause after each "pause" number of lines, default=30.
def info(a, type1="", pause=30):
  w=30                                 #Width for object name display.
  built_in="<class 'builtin_function_or_method'>"
  print("-"*27+" info "+"-"*27)
  t=type(a)
  print(" Type "+" "*15+": "+str(t).split("'")[1])
  try:
    print(" Length : "+str(len(a)))
  except:
    None

  try:
    type2=eval(type1)
  except:
    if type(type1)!=str:
      type2=None
    elif type1.lower()=="function":
      type2=type(isdata)
    elif type1.lower()=="method":
      type2="<class 'method'>"
    else:
      type2=None

  if type2:
    print("-"*12+" Displaying only: "+str(type2)+"-"*12)
  else:
    print("-"*60)
  n=0
  if type(type2)!=str:  st2=str(type2)
  else:                 st2=type2
  q=""
  for i in dir(a):
    if len(i)>1 and i[0]!='_':
      st1=str(type(eval("a."+i)))
      if type2==None or st1==st2 or ((st2=="<class 'method'>" or \
               st2=="<class 'function'>") and st1==built_in):
        n+=1
        print(fmt(i, w, 0, 1)+" : "+str(type(eval("a."+i))))
        if pause>0 and n%pause==0:
          q=input("     Press ENTER to continue or q to quit: ")
        if q.lower()=='q':
          break
  print()
  if type(a)==list:
    lst_info(a, pause)
  return
#End info

#------------------ lst_info -------------------------------------------------
#Display information about the fields of the list passed.
#Pause after each "pause" number of lines, default=30.
def lst_info(lst, pause=30):
  print("-"*17+" lst_info "+"-"*17)
  if type(lst)!=list:
    print("  lst_info error! passed item is not a list type.")
    return
  print("   The list contains "+str(len(lst))+" elements as follows:")
  n=0
  print("index :          type         :  length")
  print("-"*44)
  q=""
  for i in lst:
    if type(i)==str or type(i)==list:
      print(fmt(n, 5)+" :"+fmt(str(type(i)), 20)+"   : "+fmt(len(i),4))
    else:
      print(fmt(n, 5)+" :"+fmt(str(type(i)), 20))
    n+=1
    if pause>0 and n%pause==0:
      q=input("     Press ENTER to continue or q to quit: ")
    if q.lower()=='q':
      break
  print()
  return
#End lst_info
#-----------------------------------------------------------------------------

