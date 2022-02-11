#----------------------------------------------------------------------------
#Benjamin Carlson, Project 70, 559 SEWS, US Air Force, January, 2022
#pg_tools is a set of python tools for reading in, analyzing, displaying, and
#otherwise studying AC path data, waypoint lists, and ADS-B data.
#The tools are meant to be run interactively within a python command window,
#and will look for any data files in the current working directory unless
#otherwise specified.
#
#------------------- Data input and Time functions --------------------------
#Process_path(clear_flag=False, set_num=0)        -Read and plot wp, path set.
#Read_path_files(set_num, path, wp_gen, wp_org)   -Read in path set, 3 files.
#data= convert_path(path, msid="ABC333")          -Convert raw path to data.
#wpo_lst= convert_wp_org(wp_org, msid="ABC111")   -Convert string wp data lsts
#wpg_lst= convert_wp_gen(wp_gen, msid="ABC222")   -to 13 element data set.
#adsb_read_set(dname, out_data, order_type=3)     -Puts data into out_data list
#num= adsb_read_file(fname, out_data, order_type=0) -num lines processed
#group_tracks(raw_data)                           -Organize entries into tracks
#track= extract_raw_track(raw_data, maxs=MAX_SEC) -Extract/return first track.
#data= read_csv(fname="./tmp_data.csv", l=0)      -Read single csv data file
#save_csv(data, fname="./tmp_data.csv")           -Save a single list to file
#remove_non_MSG(raw_data)                         -Remove non MSG entries
#i= add_date_order(raw_data, entry, order=1)      -i is the insert point
#d[3], t[3]= get_date_time(msg)                   -date and time as lists
#comp= compare_dtg(d1, t1, d2, t2)                -1 to 12, 7 if equal
#ds, ts, de, te, tot_secs= get_track_time(raw_data, ms_id, start_i=0, end_i=0)
#seconds= time_diff_messages(msg1, msg2)          -Time difference between msgs
#seconds= time_diff(d1, t1, d2, t2)               -diff in seconds from 1 to 2
#dtg= fmt_dtg(e, d="|")                           -Returns dtg as formatted str
#------------------- Parsing, Listing, and Output functions -----------------
#display_raw(raw_data, start_i=0, end_i=0, disp_tr=True, pause=0)
#display_location(data, start_i=0, end_i=0, pause=0)
#display_data(data, start_i=0, end_i=0, pause=0)  -Display 13 extracted fields.
#display_track_stats(data, len1=0, len2=0)        -Display brief info for each.
#display_anomaly_list(anoms)                      -Display list outliers/anoms.
#data_copy= copy_data(data, start_i=0, end_i=0)   -Return deep copy of entries.
#plot_set(data, clear_flag=True, start_i=0, end_i=0, co=0, dots=0)
#plot_path_set(wps, pd, n, clear_flag=True)       -Plot wps set and path.
#plot_track(track_data, color=0, dots=0)          -Plot a single track.
#track_count= count_tracks(data, start_i=0, end_i=0) -Must be sorted by track!
#track_start, track_end= get_track_indices(data, ms_id, start_i=0, end_i=0)
#field_msgs= extract_field(data, field, start_i=0, end_i=0)
#type_msgs= extract_type(raw_data, t, start_i=0, end_i=0)
#loc_data= extract_location(data, start_i=0, end_i=0) -mode-s ID/alt/lat/lon
#data= extract_data(raw_data, start_i=0, end_i=0)     -Extract useful data
#set_msgs= extract_set(data, vals, field, op="==", start_i=0, end_i=0)
#track_msgs= extract_track(data, vals, field, op="==", start_i=0, end_i=0)
#entry, index= find_entry1(data, val,  field, op, start_i, end_i):
#entry, index= find_entry2(data, vals, field, op, start_i, end_i):
#consolidate_speed(data)                          -Remove dup speed/az/v-rates.
#consolidate_alt(data)                            -Remove duplicate alt lines.
#i= nearest_time(data, index, field)              -Return nearest index in t.
#------------------------ Data analysis functions ---------------------------
#min_val, max_val= find_range(d, f)
#mean, n= calc_mean(data, field)
#sd, var, mean, n= calc_sd_var(data, field, mean=None)
#   Uses identify_track_outliers to actually remove them from data as data2.
#data2= remove_track_outliers(data, sd_mult=3.0, f=[2, 3])
#   Detect outliers in individual tracks by analyzing fields within each.
#ol_list= identify_track_outliers(data, sd_mult=3.0, f=[2,3], stats_out=0)
#  Uses identify_outliers to actually remove them from data as data2, data is
#data2= remove_outliers(data, f, sd_mult=3.0, stats_out=1)  - not modified
#outliers, indices= identify_outliers(data, f, sd_mult, stats_out=1):
#data2= remove_entries(data, indices)
#loc_data= standardize_location(data, fl=0, xmin=X_MIN,  xmax=X_MAX,
#                                           ymin=-Y_MIN, ymax=Y_MAX)
#   Distance and bearing between two lat/lon points (bearing from p1 to p2.
#dist_meters, bearing_degrees= dist_bearing(p1, p2, lat_i=2, lon_i=3)
#   Uses analyze_pos to identify and remove anomalies from data as data2.
#data2=remove_track_anomalies(data, tolerance=0.5, t=0)
#   Analyze location (speed and direction) and/or altitude for anomalies.
#loc_list, alt_list= analyze_pos(data, tolerance=0.5, t=2)
#anomaly_list= analyze_loc(data, tolerance=0.5) -Analyze single tr for loc anom
#anomaly_list= analyze_alt(data, tolerance=0.5) -Analyze single tr for alt anom
#------------------------ Misc support functions ----------------------------
#color_count= set_next_color()
#key##= k(i)                           -Returns func() for field i processing.
#----------------------------------------------------------------------------

from sys import argv
from utils import *
from random import random
import math
import turtle
import datetime
import numbers

#Global turtle setings
turtle.colormode(255)
cc=[240, 20, 20]                       #Current color set as [red, green, blue]
color_mode=0                           #Current mode for changing colors
color_step=45                          #Current step size for color adjustment.
color_count=0
color_max=220                          #Minimum and maximum color brightness.
color_min=0
dot_size=4

#Global constants
R=6371000.0                            #Earth's average radius
KNOTS_TO_MSEC=0.514444                 #Conversion for knots to meters/second.
MAX_SEC=1800                           #Max # of seconds for track separation.

#The following values are used to standardize lat/lon values for plotting.
#X_MIN=-950
#X_MAX=950
#Y_MIN=-450
#Y_MAX=450
#Settings for Widnows
X_MIN=-780
X_MAX=780
Y_MIN=-420
Y_MAX=420
#These are used to hold the lat/lon min and max values from a previous data
#set for standardization of future sets (g stands for global).
glat_min=glat_max=0.0
glon_min=glon_max=0.0

#Global variable used for various interprocess communications.
tmp_var=[]

#-------------------- Read_path_files ---------------------------------------
#Read in an entire set, generated waypoint set, original wp set, and generated
#path data, convert the data to numeric form, extract and standardize location
#data and plot the entire set. If clear_flag is False (default) the previous
#plot will remain and the previous plot limits will be used to standardize the
#new data, if possible. If not, then the limits of the new data will be used.
#Enter 0 to 99 for the set number with 0 default.
#Very little error checking is performed.
#---------------------------------- ------------------------------------------
def Process_path(clear_flag=False, set_num=0):
  if type(clear_flag)!=bool: clear_flag=False
  #If no data has been used for standardization, set clear_flag to True!
  if glat_min==glat_max==glon_min==glon_max==0.0:
    clear_flag=True
  pd=[]
  wpg=[]
  wpo=[]
  Read_path_files(pd, wpg, wpo, set_num)
  if pd:
    pd=convert_path(pd)                #Convert text fields to numeric data.
  if wpg:
    wpg=convert_wp_gen(wpg)            #Ditto for generated waypoints.
  #We must know how many of the wps in the wpg list are original, not gen.
  #Get number of entries in wpo list and subtract one for the config line.
  wpo_num=len(wpo)-1
  if wpo_num>0 and len(wpo[wpo_num])!=9: #Check and see if an end action line
    wpo_num-=1                           #exists and remove it from the count.

  #Now, plot the data if there is any to plot!
  if len(wpg)>0 or len(pd)>0:
    plot_path_set(wpg, pd, wpo_num, clear_flag)
  else:
    print("Error in Process_path: No data found for set: "+str(set_num)+"!")
  #We may eventually add functionality to return the data sets here.
#End Process_path

#-------------------- Read_path_files ---------------------------------------
#Read in the path generated by path_gen from file plain_path??.msg where ??
#is the two digit set number defined by set_num with 00 as the default. The
#generated waypoint list will be read from wp??_lst.txt into wp_gen, and the
#original waypoint list from wp??.txt into wp_org, including the initial
#path configuration parameters line and the end action line.
#set_num must be an enteger from 0 to 99, path, wp_gen, and wp_org must be
#lists, and will normally be empty. If they are not empty, the data read in
#will be added. Also, if any of the three files are not found, an error
#message will be displayed but the other files will still be read in and
#their data returned.
#If set_num is invalid, then the default value of 00 will be used.
#NOTE: If any of the three input lists contains data that is not in the same
#      format as the type would imply, the list will be emptied and the new
#      data read in from the appropriate file will replace it!
#---------------------------------- ------------------------------------------
def Read_path_files(path, wp_gen, wp_org, set_num=0):
  if type(set_num)==int and set_num>=0 and set_num<=99:
    if set_num<10:
      sn="0"+str(set_num)
    else:
      sn=str(set_num)
  else: sn="00"

  path_fn="plain_path"+sn+".msg"
  if not os.path.isfile(path_fn):
    print("Error! Path file: "+path_fn+" does not exist.")
  else:
    print("Reading the path from           : "+path_fn)
    #If path is not a list or the first entry does not have 8 elements, reset.
    if type(path)!=list or len(path)>0 and len(path[0])!=8:
      path.clear()
    num=len(path)
    pd=read_csv(path_fn)
    path.extend(pd)
    print("    "+str(len(pd))+" path entries added to "+str(num)+" entries.")

  wpg_fn="wp"+sn+"_lst.txt"
  if not os.path.isfile(wpg_fn):
    print("Error! Generated path file: "+wpg_fn+" does not exist.")
  else:
    print("Reading generated waypoints from: "+wpg_fn)
    #If wp_gen is not a list or the first entry does not have 7 elements, reset
    if type(wp_gen)!=list or len(wp_gen)>0 and len(wp_gen[0])!=7:
      wp_gen.clear()
    num=len(wp_gen)
    wpgd=read_csv(wpg_fn)
    wp_gen.extend(wpgd)
    print("    "+str(len(wpgd))+" wpg entries added to "+str(num)+" entries.")

  wpo_fn="wp"+sn+".txt"
  if not os.path.isfile(wpo_fn):
    print("Error! Original path file: "+wpo_fn+" does not exist.")
  else:
    print("Reading original waypoints from : "+wpo_fn)
    #If wp_org is not a list then reset. Since the original defined wp list
    if type(wp_org)!=list:             #contains a leading config line and
      wp_org.clear()                   #trailing end action line, the entries
    num=len(wp_org)                    #may not be consistent lengths.
    wpod=read_csv(wpo_fn, True)        #Keep all data lines, even if uneven.
    wp_org.extend(wpod)
    print("    "+str(len(wpod))+" wpo entries added to "+str(num)+" entries.")
    if len(wpod)>0 and len(wpod[0])!=9:
      print("      Including one line of path configuration parameters.")
    if len(wpod)>2 and len(wpod[-1])!=9:
      print("      Including one line containing end action parameters.")

#End Read_path_set

#-------------------- convert_path ------------------------------------------
#Convert a path as read in from plain_plath??.msg into the standard 13 element
#data set compatible with this library. path must be list entries with 8
#string elements per row/entry as created by the path generation tool.
#Returns new data list with 13 element entries without modifying the original
#data. Uses dummy Mode-S ID of ABC333 for each entry unless a value is passed
#in for this purpose. The string passed in for mode-s ID must be exactly 6
#characters, or the default value will be used.
#Returns -1 if an error was encountered.
#----------------------------------------------------------------------------
def convert_path(path, msid="ABC333"):
  data=[]
  if type(msid)!=str or len(msid)!=6:
    msid="ABC333"
  if type(path)!=list or len(path)<1 or len(path[0])!=8:
    print("Error in convert_path: Invalid data sent for path.")
    return -1

  for i in path:
    entry=[]
    entry.append(msid)                 #Put a dummy mode-s id for compatibility
    entry.append(int(i[1]))            #Get the altitude as an integer.
    entry.append(float(i[2]))          #Get the latitude as a float.
    entry.append(float(i[3]))          #Get the longitude as a float.
    entry.append(float(i[4]))          #Get the speed as a float.
    entry.append(float(i[5]))          #Get direction of travel in radians.
    entry.append(float(i[6]))          #Get the vertical rate
    entry.extend([0,0,0,0,0,0])        #6 dummy values for date/time group.
    data.append(entry)

  return data
#End convert_path

#-------------------- convert_wp_org ----------------------------------------
#Convert a list of waypoint elements as string entries into the 13 element
#standard data format. Works only with the original wp format from a wp list
#file as read in by the path generation tool to be used for path creation.
#Returns new data list with 13 element entries without modifying the original
#data. Uses dummy Mode-S ID of ABC111 for each entry unless a value is passed
#in for this purpose. The string passed in for mode-s ID must be exactly 6
#characters, or the default value will be used.
#Returns -1 if an error was encountered.
#----------------------------------------------------------------------------
def convert_wp_org(wp_org, msid="ABC111"):
  wpo_lst=[]
  if type(msid)!=str or len(msid)!=6:
    msid="ABC111"
  if type(wp_org)!=list or len(wp_org)<1 or len(wp_org[0])!=9:
    print("Error in convert_wp_org: Invalid data sent for wp_org.")
    return -1

  for i in wp_org:                     #Convert each line and plug into wpo_lst
    entry=[]
    entry.append(msid)
####### Need to convert and plug in actual data here!!!

    entry.extend([0,0,0,0,0,0])        #6 dummy values for date/time group.
    wpo_lst.append(entry)

  return wpo_lst
#End convert_wp_org

#-------------------- convert_wp_gen ----------------------------------------
#Convert a list of waypoint elements as string entries into the 13 element
#standard data format. Works only with the generated wp format produced by
#the path generation tool and written out to file. Use convert_wp_org to
#convert data from an original waypoint file.
#Returns new data list with 13 element entries without modifying the original
#data. Uses dummy Mode-S ID of ABC222 for each entry unless a value is passed
#in for this purpose. The string passed in for mode-s id must be exactly 6
#characters, or the default value will be used.
#Returns -1 if an error was encountered.
#----------------------------------------------------------------------------
def convert_wp_gen(wp_gen, msid="ABC222"):
  wpg_lst=[]
  if type(msid)!=str or len(msid)!=6:
    msid="ABC222"
  if type(wp_gen)!=list or len(wp_gen)<1 or len(wp_gen[0])!=7:
    print("Error in convert_wp_gen: Invalid data sent for wp_gen")
    return -1

  for i in wp_gen:
    entry=[]
    entry.append(msid)                 #Put a dummy mode-s id for compatibility
    entry.append(int(i[1]))            #Get the altitude as an integer.
    entry.append(float(i[2]))          #Get the latitude as a float.
    entry.append(float(i[3]))          #Get the longitude as a float.
    entry.append(float(i[4]))          #Get the speed to next wp in fps.
    entry.append(float(i[5]))          #Get direction to next wp in radians
    #This next field is normally the vertical rate but for waypoints, it is
    entry.append(float(i[6]))          #the distance to next wp in meters
    entry.extend([0,0,0,0,0,0])        #6 dummy values for date/time group.
    wpg_lst.append(entry)

  return wpg_lst
#End convert_wp_gen

#-------------------- adsb_read_set -----------------------------------------
#Read in all data files from the directory: dname
#Arguments are as follows:
#  dname= Directory name as a string ("./" for current dir).
#  out_data= list to contain data, can be empty.
#  order_type= How entries should be sorted as follows:
#    0: No sorting, just read in serially from files and add to list.
#    1: Sort on date/time of message oldest to newest.
#    2: Sort as 1 but in reverse (newest to oldest).
#    3: Sort on individual tracks but keep in date/time order.
#Returns data as a list or -1 if error encountered.
#----------------------------------------------------------------------------
def adsb_read_set(dname, out_data, order_type=3):
  if dname[len(dname)-1]!='/':
    dname=dname+'/'
  fns=os.listdir(dname+'.')
  flist=[fns[i] for i in range(len(fns)) if ".csv" in fns[i]]
  flist.sort()

  total_entries=len(out_data)
  for fn in flist:
    fn=dname+fn
    print("Current size: "+str(total_entries)+" - Processing file: "+fn)
    if order_type==3:                  #If 3, simply read entries in date order
      ret_val=adsb_read_file(fn, out_data, 1)
    else:                              #otherwise, use the order type passed.
      ret_val=adsb_read_file(fn, out_data, order_type)
    if type(ret_val)==None:
      print("Error in read_set: Error processing file: "+fn)
      return -1
    total_entries+=ret_val
  #Remark this line out if you wish to keep non-MSG messages.
  remove_non_MSG(out_data)
  if order_type==3:                    #User selected to sort on tracks.
    group_tracks(out_data)
    if len(out_data)!=total_entries:   #Check for inconsistency in processing
      print("Error in read_set: Inconsistency in track grouping!")
      print("Entry count missmatch: "+str(total_entries)+" : "+
            str(len(out_data)))

  print("\tAll Done reading. Files: "+str(len(flist))+",  total entries: "+
        str(total_entries))
  return
#End adsb_read_set

#-------------------- adsb_read_file ----------------------------------------
#Read in the data from an ADS-B bs file from dump1090.
#order_type defines the ordering scheme for the entries as such:
#    0: No sorting, just read in serially from file and add.
#    1: Sort on date/time of message - oldest to newest.
#    2: Sort as 1 but in reverse (newest to oldest).
#Returns data as a list or None if error encountered.
#----------------------------------------------------------------------------
def adsb_read_file(fname, out_data, order_type=0):
  if not os.path.isfile(fname):
    print("Error in adsb_read_file: File: "+fname+" does not exist.")
    return None

  if order_type>=3 or order_type<0:
    order_type=1

  infile=open(fname, "r")
  lines=infile.read().split("\n")
  infile.close()

  tmp_data=[]
  for i in lines:
    if len(i)<9:
      continue
    e=i.split(',')

    if len(e)<8:
      continue
    elif len(e[0])<2:
      continue
    tmp_data.append(e)

  if len(out_data)==0:
    out_data.append(tmp_data[0])
    start=1
  else:
    start=0

  for line in tmp_data[start:]:
    if order_type==0:
      out_data.append(line)
    else:
      add_date_order(out_data, line, order_type)

  return len(tmp_data)
#End adsb_read_file

#-------------------- group_tracks ------------------------------------------
#Group the raw entries by contiguous tracks and keep in date/time order.
#Entries must be in date/time order! Modifies data passed in.
#----------------------------------------------------------------------------
def group_tracks(rd):
  if len(rd)<2:                        #Not enough to sort!
    print("Error in group_tracks: Too few entries to sort!")
    return
  elif len(rd[0])!=22:                 #Data in wrong format!
    print("Error in read_csv: Data not in raw format.")
    return

  print("\t----- Extracting tracks for grouping of entries using "+
        "group_tracks - this may take a while! -----")
  track_count=0
  tracks=[]                            #List to copy entries too.
  while len(rd)>0:                     #While we still have data.
    track=extract_raw_track(rd)
    if len(track)>0:                   #If a track was extracted,
      track_count+=1
      if type(track[0])!=list:         #If track only has one entry,
        tracks.append(track)           #append it, otherwise,
      else:
        tracks.extend(track[:])        #Add it's entries to tracks.
      if track_count%10==0:
        print("\tTracks extracted so far: "+str(track_count))
    elif len(rd)>0:                    #An error occured.
      print("Error in group_tracks: Track not found error!")
      break                            #Exit processing

  rd.extend(tracks[:])
  print("\tAll done grouping tracks.  Total tracks: "+
        str(count_tracks(rd)))
  return
#End group_tracks

#-------------------- extract_raw_track -------------------------------------
#Extract and return a single contiguous track from rd. The first track will
#be extracted and returned. The rd must be in date/time order.
#The entries for the track extracted will be removed from rd.
#----------------------------------------------------------------------------
def extract_raw_track(rd, maxs=MAX_SEC):
  if len(rd)==1:
    return rd.pop(0)
  elif len(rd)<1:
    return []
  track=[]
  msid=rd[0][4]
  cur_i=0
  track.append(rd.pop(0))
  while True:
    time_d=time_diff_messages(track[len(track)-1], rd[cur_i])
    if time_d>maxs:                    #All done, so return.
      return track[:]
    if rd[cur_i][4]==msid:
      track.append(rd.pop(cur_i))
    else:
      cur_i+=1
    if cur_i>=len(rd):                 #At end of list, so return.
      return track[:]
  #We should never get here, but just in case!
  return track[:]
#End extract_raw_track

#-------------------- read_csv ----------------------------------------------
#Read in a single csv data file into a 2D list. Return the list.
#If no file name passed in, default name ./tmp_data.csv
#fl will cause uneven lines to be included if True. If False, the default,
#then when a line is read with a different number of elements than the
#previous, reading/line conversion will stop.
#----------------------------------------------------------------------------
def read_csv(fname="./tmp_data.csv", fl=False):
  #Perform validation and checks here eventually.
  infile=open(fname)
  d=[]
  tmp_d=infile.read().split("\n")
  infile.close()
  num=-1
  #Remove any empty lines at the end.
  num_lines=len(tmp_d)
  while len(tmp_d[num_lines-1])<1:
    tmp_d=tmp_d[0:-1]
    num_lines=len(tmp_d)
  tot=0
  for line in tmp_d:
    if len(line)<1:
      continue
    if line[0]=='#':
      continue
    line=line.split(',')
    if num<1:
      num=len(line)
    #If lines have different number of elements and uneven lines are not
    elif num!=len(line) and fl==False:        #allowed, based on fl, then
      print("Error in read_csv: Inconsistent number of entries!")  #quite!
      print("  Line "+str(tot)+" has "+str(len(line))+" entries.")
      break
    #Append the line converted to a list as a new entry.
    d.append(line)

  return d
#End read_csv

#-------------------- save_csv ----------------------------------------------
#Save a single 2D data set in list format to a file.
#If no file name passed in, default name ./tmp_data.csv
#----------------------------------------------------------------------------
def save_csv(data, fname="./tmp_data.csv"):
  outfile=open(fname, "w")
  outfile.write("#CSV output file for Project70 team, 559 SWES, US Air Force\n")
  #Allow user to enter comment lines.
  line=" "
  print("Enter comments one line at a time.")
  print("  Press return with no text to end comment entry.")
  while len(line)!=0:
    line=input("? ")
    if len(line)>0:
      outfile.write('#'+line+"\n")

  #Loop for additional comment lines here eventually!
  for i in data:
    outfile.write(str(i)[1:-1]+"\n")

  outfile.close()
#End save_csv

#-------------------- remove_non_MSG ----------------------------------------
#Remove all non-MSG types (STA, ID, AIR, SEL, and CLK). Aircraft location
#data will only be contained in messages of type MSG and these are the
#predominant type. This function will remove the other types from the list
#passed in and will only operate on an entire list of raw data.
#----------------------------------------------------------------------------
def remove_non_MSG(rd):
  count=0
  for x in range(len(rd)-1, -1, -1):
    if rd[x][0]!="MSG":
      count+=1
      rd.pop(x)

  print(str(count)+" entries removed by remove_non_MSG.")
#End remove_non_MSG

#-------------------- add_date_order ----------------------------------------
#Add an element into the data list either in forward or reverse date order. 
#If order=1, the default, add in forward date order (newer entries appear
#later in the list than older entries).
#Returns insert point index or None if error encountered.
#----------------------------------------------------------------------------
def add_date_order(raw_data, entry, order=1):
  d2, t2=get_date_time(entry)
  if order==1:
    start=len(raw_data)-1
    end=  -1
    step= -1
  elif order==2:
    start=0
    end=  len(raw_data)
    step= 1
  else:
    print("Error in add_date_order: Invalid order type of "+str(order)+" !")
    return None

  for x in range(start, end, step):
    d1, t1=get_date_time(raw_data[x])
    dtg_result=compare_dtg(d1, t1, d2, t2)
    #If entry newer than or equal to current entry, insert after.
    if order==1 and dtg_result<=7:
      i=x+1                            #Keep track of insert point.
      raw_data.insert(i, entry)        #Insert after current entry.
      break                            #Exit loop.
    #Otherwise, check if reverse ordering selected and check.
    elif order==2 and dtg_result<=7:
      i=x
      raw_data.insert(i, entry)
      break

  if order==1 and dtg_result>7:        #If true, we got to beginning of list.
    i=0
    raw_data.insert(i, entry)          #Insert as first element
  elif order==2 and dtg_result>7:      #Else, we got to the end of the list!
    i=len(raw_data)
    raw_data.insert(i, entry)          #Insert as last element.

  return i                             #Return index of insertion.
#End add_date_order

#-------------------- get_date_time -----------------------------------------
#Return the date and time as two numeric lists. Works with raw data or
#data extracted with extract_data. Returns None on error.
#----------------------------------------------------------------------------
def get_date_time(msg):
  if len(msg)==22:
    d=[int(i) for i in msg[6].split("/")]
    t=[i for i in msg[7].split(":")]
    t[0]=int(t[0])
    t[1]=int(t[1])
    t[2]=float(t[2])
  elif len(msg)==13:
    d=msg[7:10]
    t=msg[10:]
  else:
    print("Error in get_date_time: Invalid entry of length "+
          str(len(msg))+" sent!")
    return None
  return d, t
#End get_date_time

#-------------------- compare_dtg -------------------------------------------
#Compare two date time groups. Return result as follows:
#1 older than 2 by year  = 1
#1 older than 2 by month =  2            First is
#1 older than 2 by day   =   3           older
#1 older than 2 by hour  =    4          than
#1 older than 2 by minute=     5         second
#1 older than 2 by second=      6
#Exactly equal           =       7       EQUAL
#2 older than 1 by second=      8
#2 older than 1 by minute=     9         Second is
#2 older than 1 by hour  =   10          older
#2 older than 1 by day   =  11           than
#2 older than 1 by month = 12            first
#2 older than 1 by year  =13
#----------------------------------------------------------------------------
def compare_dtg(d1, t1, d2, t2):
  if d1[0]<d2[0]:
    return 1
  elif d2[0]<d1[0]:
    return 13
  elif d1[1]<d2[1]:
    return 2
  elif d2[1]<d1[1]:
    return 12
  elif d1[2]<d2[2]:
    return 3
  elif d2[2]<d1[2]:
    return 11
  elif t1[0]<t2[0]:
    return 4
  elif t2[0]<t1[0]:
    return 10
  elif t1[1]<t2[1]:
    return 5
  elif t2[1]<t1[1]:
    return 9
  elif t1[2]<t2[2]:
    return 6
  elif t2[2]<t1[2]:
    return 8

  return 7                             #If we get here, they are equal!
#End compare_dtg

#-------------------- get_track_time ----------------------------------------
#Uses raw data or track data as extracted from extract_data, and must be
#ordered by ms-id and date/time. Returns the start date, start time,
#end date, end time, and total track seconds.
#start_i and end_i can be passed but default to 0 and end-of-data.
#Returns -1 if error encountered!
#----------------------------------------------------------------------------
def get_track_time(data, ms_id, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in get_track_time: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1

  if len(data[0])!=22 and len(data[0])!=13:
    print("Error in get_track_time: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1

  t_start, t_end=get_track_indices(data, ms_id, start_i, end_i)
  if t_start<0 or t_end<0:             #Error encountered!
    print("Error in get_track_time: ms_id of "+str(ms_id)+" not found using")
    print("  indices of: "+str(start_i)+" - "+str(end_i))
    return -1

  ds, ts=get_date_time(data[t_start])
  de, te=get_date_time(data[t_end])
  tot_secs=time_diff(ds, ts, de, te)

  return ds, ts, de, te, tot_secs
#End get_track_time

#-------------------- time_diff_messages ------------------------------------
#Calculate the difference in seconds between message 1 and 2.
#Returns -1 if error encountered.
#----------------------------------------------------------------------------
def time_diff_messages(msg1, msg2):
  lm1=len(msg1); lm2=len(msg2)
  if not (lm1==22 or lm1==13) or not (lm2==22 or lm2==13):
    print("Error in time_diff_messages: Data must have 22 or 13 fields.")
    return -1

  d1, t1=get_date_time(msg1)
  d2, t2=get_date_time(msg2)
  
  return time_diff(d1, t1, d2, t2)
#End time_diff_messages

#-------------------- time_diff ---------------------------------------------
#Return the difference between DTG 1 and 2 in seconds. If 2 is earlier in
#time than 1, return count will be negative.
#Return positive seconds difference if d2 later than d1, 0 if equal, or -1.
#----------------------------------------------------------------------------
def time_diff(d1, t1, d2, t2):
  diff=compare_dtg(d1, t1, d2, t2)     #If the difference is within seconds
  if diff==6:                          #only, then calculate directly.
    return t2[2]-t1[2]                 #This will give differences < 1 sec!

  dt1=datetime.datetime(d1[0],d1[1],d1[2],t1[0],t1[1],int(t1[2]),0)
  dt2=datetime.datetime(d2[0],d2[1],d2[2],t2[0],t2[1],int(t2[2]),0)
  diff=dt2-dt1
  if diff.days<0:
    seconds=-1
  elif diff.days>0:                    #Include seconds for multiple days.
    seconds=diff.seconds+round(diff.microseconds/1000000)
    seconds+=diff.days*24*3600
  else:
    seconds=diff.seconds+round(diff.microseconds/1000000)
  return seconds
#End time_diff

#-------------------- fmt_dtg -----------------------------------------------
#Format the date time group as a string for display. e must contain 13 fields
#with the dtg data in 7 to 12 as produced by extract_data.
#d is the separator to use between the date and the time.
#----------------------------------------------------------------------------
def fmt_dtg(e, d=" | "):
  if type(e)!=list and len(e)!=13:
    return ""

  dtg=fmt(e[7],4)+"/"+fmt(e[8],2)+"/"+fmt(e[9],2)+d
  dtg+=fmt(e[10],2)+":"+fmt(e[11],2)+":"+fmt(e[12],2,5)

  return dtg
#End fmt_dtg

#----------------------------------------------------------------------------
#------------------- Parsing, Listing, and Output functions -----------------
#-------------------- display_raw -------------------------------------------
#Display raw data and pause between tracks.
#start_i and end_i can be passed but default to 0 and end-of-data.
#If disp_tr=True (default), pause at end of each track's data.
#If pause>0 then pause after each "pause" number of lines.
#----------------------------------------------------------------------------
def display_raw(raw_data, start_i=0, end_i=0, disp_tr=True, pause=0):
  #Check for a single raw data entry/line passed in.
  if len(raw_data)==22 and len(raw_data[0])==3:
    print(str(raw_data))
    return

  if end_i<=start_i:
    end_i=len(raw_data)
  if start_i<0 or start_i>=end_i:
    print("Error in display_raw: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return

  msid_index=0
  if len(raw_data[0])==22:
    msid_index=4

  ms_id=raw_data[start_i][msid_index]  #Get first mode-s ID
  num=0
  q="-"
  for i in raw_data[start_i:end_i]:
    if i[msid_index]!=ms_id and disp_tr: #If different mode-s ID, display.
      q=input(ms_id+":  entries: "+str(num)+" ")
      print("-"*80)
      ms_id=i[msid_index]
      num=0
    elif pause>0 and num>0 and (num%pause)==0:
      input("=====-----  Press ENTER to continue, q to exit  -----===== ")
    if q=="q" or q=="Q":               #If user typed q, then exit.
      break
    print(str(i))
    num+=1

  return
#End display_raw

#-------------------- display_location --------------------------------------
#Display the Mode S ID and location data. Input must either be a subset of
#bs data with only 4 fields (Mode-S ID, Alt, Lat, Lon), or all 22 fields.
#start_i and end_i can be passed but default to 0 and end-of-data.
#If pause>0 then pause after each "pause" number of lines.
#----------------------------------------------------------------------------
def display_location(data, start_i=0, end_i=0, pause=0):
  #Check for a single location data entry/line passed in.
  if len(data)==4 and len(data[0])==6:
    print(str(data))
    return

  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in display_location: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return
  if len(data[0])==4 or len(data[0])==13:
    msid_index=0; alt=1; lat=2; lon=3
  elif len(data[0])==22:
    msid_index=4; alt=11; lat=14; lon=15
  else:
    print("Error in display_location: Data not in correct format!")
    return

  ms_id=data[start_i][msid_index]      #Get first mode-s ID
  num=0
  q="-"
  print(" Mode-S ID |  Alt-feet  | Latitude \t| Longitude")
  print("-"*60)
  for i in data[start_i:end_i]:
    if i[msid_index]!=ms_id:           #If different mode-s ID, display.
      q=input(ms_id+"  "+str(num)+" ")
      print("-"*60)
      print(" Mode-S ID |  Alt-feet  | Latitude \t| Longitude")
      print("-"*60)
      ms_id=i[msid_index]
      num=0
    elif pause>0 and num>0 and (num%pause)==0:
      q=input("=====-----  Press ENTER to continue, q to exit  -----===== ")

    if q=="q" or q=="Q":               #If user typed q, then exit.
      break
    if len(i)==4 or i[1]=="2" or i[1]=="3":
      print("  "+i[msid_index]+"   |   "+str(i[alt])+"\t| "+str(i[lat])+"\t| "+
            str(i[lon]))
      num+=1

  return
#End display_location

#-------------------- display_data ------------------------------------------
#Display the useful data as extracted by the extract_data function.
#Mode-s ID, altitude, latitude, longitude, speed, direction, vertical rate,
#year, month, day, hour, minute, second (13 fields).
#start_i and end_i can be passed but default to 0 and end-of-data.
#If pause>0 then pause after each "pause" number of lines.
#----------------------------------------------------------------------------
def display_data(data, start_i=0, end_i=0, pause=0):
  #Check for a single data entry/line passed in.
  if len(data)==13 and len(data[0])==6:
    print(str(data))
    return

  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in display_data: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return
  if len(data[0])!=13:
    print("Error in display_data: Data not in correct format!")
    return

  ms_id=data[start_i][0]               #Get first mode-s ID
  num=0
  print("-"*103)
  print(" index || M-S ID |Alt-feet|   Latitude  |  Longitude  |"+
        " Speed|  Az | v-rate|year/month/day|hour:min:sec")
  print("-"*103)
  index=start_i
  q="-"
  for i in data[start_i:end_i]:
    if i[0]!=ms_id:                    #If different mode-s ID, display.
      q=input(ms_id+"  "+str(num)+" "+" ("+str(index-num)+", "+
              str(index-1)+") ")
      print("-"*103)
      print(" index || M-S ID |Alt-feet|   Latitude  |  Longitude  |"+
            " Speed|  Az | v-rate|year/month/day|hour:min:sec")
      print("-"*103)
      ms_id=i[0]
      num=0
    elif pause>0 and num>0 and (num%pause)==0:
      q=input("=====-----  Press ENTER to continue, q to exit  -----===== ")

    if q=="q" or q=="Q":               #If user typed q, then exit.
      break
    print(fmt(index, 6)+" || "+i[0]+" | "+fmt(i[1],6)+" | "+fmt(i[2],11,6)+
          " | "+fmt(i[3],11,6)+" |"+fmt(i[4],6)+"| "+fmt(i[5],3)+" | "+
          fmt(i[6],5)+" |   "+fmt_dtg(i))
    num+=1
    index+=1

  print(ms_id+"  "+str(num)+" "+" ("+str(index-num)+", "+str(index-1)+") ")
  print("\tTotal tracks: "+str(count_tracks(data[start_i:end_i])))
  return
#End display_data

#-------------------- display_track_stats -----------------------------------
#Display one line of data for each track consisting of:
#  track index, Mode-S ID, start / end dtg, start / end index, length
#len1 and len2 can be used to select listing only tracks that have a certain
#number of entries and defalt to 0/0 which will list all tracks. Thus, if you
#desire to see only tracks with more than 10 entries, pass 10, 0.
#If pause>0 then pause after each "pause" number of lines (default is 30).
#----------------------------------------------------------------------------
def display_track_stats(data, pause=30, len1=0, len2=0):
  num_tracks=count_tracks(data)
  print("\n"+"-"*100)
  print(" Index | Mode-S ID|         start DTG        |          end DTG"+
        "         |   start /  end    | length")
  print("-"*100)

  num=0
  q="-"
  start=end=-1
  for x in range(num_tracks):
    tmp_end=end
    #Get next track indices, start searching at "end" of last track.
    start, end=get_track_indices(data, 0, end+1)
    if start<0 or end<0:               #Error encountered!
      print("Error in display_track_stats: ms_id index "+str(x)+
            " not found using")
      print("  indices of: "+str(tmp_end+1)+" - "+str(len(data)))
      retun
    msid=data[start][0]
    l=end-start+1
    print(fmt(x, 6)+" |  "+msid+"  | "+fmt_dtg(data[start], " , ")+" | "+
          fmt_dtg(data[end], " , ")+" | "+fmt(start, 7)+" / "+fmt(end,7)+
          " | "+fmt(l, 4))

    num+=1
    if pause>0 and (num%pause)==0:
      q=input("=====-----  Press Enter to continue, q to exit  -----===== ")
      if q=="q" or q=="Q":
        break
      print("-"*100)
      print(" Index | Mode-S ID|         start DTG        |          end DTG"+
            "         |   start /  end    | length")
      print("-"*100)

  print("\tTotal tracks: "+str(num_tracks)+",  total entries: "+str(len(data)))
#End display_track_stats

#-------------------- display_anomaly_list ----------------------------------
#Display list of outliers or anomalies as created from other functions.
#Each element must consist of a mode-s ID, track index, start/end indexes, and
#a list of track indices representing outliers or anomalies.
#If pause>0 then pause after each "pause" number of lines (default is 0).
#----------------------------------------------------------------------------
def display_anomaly_list(anoms, pause=0):
  print("-"*80)
  print(" index | Mode-S ID | track index |   start / end:"+
        "    List of anomalies")
  print("-"*80)
  num=0
  q="-"
  for i in anoms:
    print(fmt(num, 6)+" |  "+i[0]+"   | "+fmt(i[1], 11)+" | "+fmt(i[2],7)+
          " / "+fmt(i[3],7)+":")
    print(str(i[4:])[1:-1])
    num+=1
    if pause>0 and (num%pause)==0:
      q=input("=====-----  Press ENTER to continue, q to exit  -----===== ")
      if q=="q" or q=="Q":             #If user typed q, then exit.
        break
      print("-"*80)
      print(" index | Mode-S ID | track index |   start / end:"+
            "    List of anomalies")
      print("-"*80)

#End display_anomaly_list

#-------------------- copy_data ---------------------------------------------
#Return a deep copy of data from start_i to end_i. Return -1 on error.
#----------------------------------------------------------------------------
def copy_data(data, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in copy_data: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1

  data_copy=[]
  for i in data[start_i: end_i]:
    data_copy.append(i[:])

  return data_copy
#End copy_data

#-------------------- plot_set ----------------------------------------------
#Plot the location data (lat/lon) of all tracks in a set. If the location
#data has not been extracted (raw data was passed, or extracted subset),
#extract a local copy.
#Function assumes data has not been standardized and will make a local copy
#to standardize for display only. Data passed will not be modified!
#clear_flag==True, clear the turtle window before starting.
#start_i and end_i can be passed but default to 0 and end-of-data.
#co of 0 uses single dark gray color, 1 (default) uses randomly genereated
#colors, or an actual color [0-255 for Red, Green, Blue] can be passed.
#dots=1 (default=0) will plot a dot at each location point (takes much longer).
#----------------------------------------------------------------------------
def plot_set(data, clear_flag=True, start_i=0, end_i=0, co=1, dots=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in plot_set: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return
  if type(co)==list:
    if len(co)!=3:
      print("Error in plot_set: Wrong number of colors: must be 3!")
      return
    elif type(co[0])!=int or type(co[1])!=int or type(co[2])!=int:
      print("Error in plot_set: Integers not sent for color values!")
      return
    elif co[0]<0 or co[0]>255 or co[1]<0 or co[1]>255 or co[2]<0 or co[2]>255:
      print("Error in plot_set: Invalid value sent for color values!")
      print("\tco must be list with three values from 0 to 255.")
      return
  elif type(co)!=int:
    print("Error in plot_set: co must be an integer or list with 3 ints!")
    return
  if type(dots)!=int:
    print("Error in plot_set: dots must be an integer!")
    return
  if len(data[0])==22 or len(data[0])==13:   #Extract the location data only.
    loc_data=extract_location(data, start_i, end_i)
    if clear_flag:
      loc_data=standardize_location(loc_data)
    else:
      loc_data=standardize_location(loc_data, 1)
  elif len(data[0])==4:                #Select subset of location data.
    loc_data=data[start_i: end_i]
  else:                                #Data in the wrong format.
    print("Error in plot_set: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return
  if loc_data==-1:                     #standardize_location returned an error!
    print("Error in plot_set: Data standardization failed!")
    return

  #Clear the turtle window and initialize variables.
  if clear_flag:
    turtle.clear()
#  turtle.speed(19)                      #Set for Linux
  turtle.speed(0)                      #Set for Windows
  start=end=-1

  #Loop once for each track in set.
  num_tracks=count_tracks(loc_data)
  print("---------- Ploting "+str(num_tracks)+" tracks ----------")
  for x in range(num_tracks):
    tmp_end=end
    #Get next track indices, start searching at "end" of last track.
    start, end=get_track_indices(loc_data, 0, end+1)
    if start<0 or end<0:                    #Error encountered!
      print("Error in plot_set: ms_id index "+str(x)+" not found using")
      print("  indices of: "+str(tmp_end+1)+" - "+str(len(loc_data)))
      return
    print("x= "+str(x)+" id= "+loc_data[start][0]+" start= "+str(start)+
          ", end= "+str(end))
    if co==0:                          #Gray scale - all the same.
      plot_track(loc_data[start:end+1], [10,40,60], dots)
    elif type(co)==int:                #Color, different for each track.
      plot_track(loc_data[start:end+1], 1, dots)
    else:                              #Use color passed in.
      plot_track(loc_data[start:end+1], co, dots)

  return
#End plot_set

#-------------------- plot_path_set -----------------------------------------
#Plot a set of waypoints and a path created from them. wps is a list of both
#the original waypoints and any generated by the end-action definition.
#pd is the path data, while n is the number of waypoints at the start of the
#wps list that are original, with the remaining being the end action wps.
#the original wps will be ploted in green, the end action in red, and the
#path will be randomly generated. path may contain more than one path, but if
#more than one, they must be separate and have unique Mode-S IDs. The data
#can either be 13 elements or 4, as from extract_location.
#The screen will normally be cleard before a new plot but if this is not
#desired, set the clear_flag to False (True is the default).
#Returns a negative integer if error encountered.
#----------------------------------------------------------------------------
def plot_path_set(wps=[], pd=[], n=0, clear_flag=True):
  global dot_size
  err=0
  if type(wps)!=list or len(wps)<1 or (len(wps[0])!=4 and len(wps[0])!=13):
    print("Error in plot_path_set: Invalid waypoint data passed!")
    err+=1
    n=0
  if type(pd)!=list or len(pd)<1 or (len(pd[0])!=4 and len(pd[0])!=13):
    print("Error in plot_path_set: Invalid path data passed!")
    err+=2
  if type(n)!=int or n<0 or n>len(wps):
    print("Error in plot_path_set: Invalid wp original count of: "+
          str(n)+" passed! Using 0.")
    n=0
  if type(clear_flag)!=bool:           #If invalid type sent, set to default.
    clear_flag=True

  if err==3:                           #No data to plot, so return.
    print("No valid data for plotting was received.")
    return -1
  loc_data=[]
  #Reduce the wps data to location data only and make a local copy.
  if len(wps)>0:
    if len(wps[0])==13:                #Extract the location data if needed.
      loc_data=extract_location(wps)
    else:
      loc_data=data_copy(wps)
    print("length of wps location data:  "+str(len(loc_data)))

  #Reduce the path data to location data only and make a local copy.
  if len(pd)>1:
    if len(pd[0])==13:                 #Extract the location data if needed.
      loc_data2=extract_location(pd)
    else:
      loc_data2=data_copy(pd)
    loc_data.extend(loc_data2)
    print("length of path location data: "+str(len(loc_data2)))

  print("length of combined data:      "+str(len(loc_data)))
  if clear_flag:
    loc_data=standardize_location(loc_data)
  else:
    loc_data=standardize_location(loc_data, 1)

#  display_location(loc_data,0,0,30)
#  plot_set(loc_data,True,0,0,1,1)
  if clear_flag:
    turtle.clear()
  if err!=1:
    tmp_dot_size=dot_size
    dot_size=10
    if n>0:
      plot_track(loc_data[0:n+1], [10,220,10],1)
    if n<len(wps):
      plot_track(loc_data[n:len(wps)], [240,10,10],1)
    dot_size=tmp_dot_size
  if err!=2:
    num_tracks=count_tracks(loc_data[len(wps):-1])
    if num_tracks>1 or clear_flag==False:
      plot_set(loc_data[len(wps):-1], False)
    else:
      plot_track(loc_data[len(wps):-1], [50,50,255])
#End plot_path_set

#-------------------- plot_track --------------------------------------------
#Plot an individual track. Use next color combo unless overriden by arg.
#Thus track_data should be a splice that only contains data for a single track!
#Also, track_data must contain the 4 field subset of location info as the first
#for fields (modes ID, alt, lat, lon). Override the default color scheme by
#passing a 3 int list from 0 to 255.
#Also, a dot will be drawn at each point if dots is non-zero.
#----------------------------------------------------------------------------
def plot_track(track_data, color=1, dots=0):
  if len(track_data[0])!=4 and len(track_data[0])!=13:
    print("Error in plot_track: Invalid data format passed with "+
          str(len(track_data[0]))+" fields!")
    return

  if type(color)==int:
    set_next_color()
    color=cc                           #Use global color setting in cc.
  #Initialize the turtle window/system
  turtle.hideturtle()
  turtle.penup()
  turtle.color(color)
  start=0
  while not isdata(track_data[0][2]):
    start+=1
  turtle.goto(track_data[start][3], track_data[start][2])
  turtle.pendown()
  turtle.dot(dot_size, color)          #Draw dot at start of track.
  for x in range(start, len(track_data)-1):
    #Draws a dot at each plot point.
    if dots!=0:
      turtle.dot(dot_size, color)
    if isdata(track_data[x+1][2]):     #Check for the existence of data.
      turtle.goto(track_data[x+1][3], track_data[x+1][2])
  turtle.dot(dot_size, color)          #Draw dot at end of track.

  return
#End plot_track

#-------------------- count_tracks ------------------------------------------
#Count number of different tracks based on mode-s ID. Data must be sorted, but
#can be either raw or extracted set. Returns count or -1 on error.
#start_i and end_i can be passed but default to 0 and end-of-data.
#----------------------------------------------------------------------------
def count_tracks(data, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in count_tracks: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1
  if len(data[0])==4 or len(data[0])==13:
    msid_index=0
  elif len(data[0])==22:
    msid_index=4
  else:
    print("Error in count_tracks: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1

  track_count=0
  ms_id=""
  for i in data[start_i:end_i]:
    if i[msid_index]!=ms_id:
      track_count+=1
      ms_id=i[msid_index]

  return track_count
#End count_tracks

#-------------------- get_track_indices -------------------------------------
#Find and return the start and end indices of the given mode-s id.
#ms_id can be either a string containing the actual id or an integer index,
#starting with 0. Thus, the 6th mode-s id in the data would be 5.
#If mode-s id is an integer, the counting of tracks will start at start_i,
#not at the beginning of the list!!
#Works with any of the data sub-sets created by this library.
#start_i and end_i can be passed but default to 0 and end-of-data.
#Returns -1 for indices if ms_id not found, or an error was detected.
#----------------------------------------------------------------------------
def get_track_indices(data, ms_id, start_i=0, end_i=0):
  track_start=track_end=-1
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in get_track_indices: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1, -1
  l=len(data[0])
  if l==22:           msid_index=4
  elif l==13 or l==4: msid_index=0
  else:
    print("Error in get_track_indices: Data not in correct format!")
    print("\tNumber of fields: "+str(l))
    return -1, -1

  if type(ms_id)==int:                 #Search for start based on integer
    count=0                            #index passed.
    msid=data[start_i][msid_index]
    for x in range(start_i, end_i):
      if data[x][msid_index]!=msid:
        count+=1
        msid=data[x][msid_index]
      if count==ms_id:
        track_start=x
        break
  else:                                #Search for start based on string id.
    ms_id=ms_id.upper()                #Convert to upper case.
    for x in range(start_i, end_i):
      if data[x][msid_index]==ms_id:
        track_start=x
        break
  if track_start<0:                    #If a match was not found:
    return -1, -1                      #return -1 for both indices.

  ms_id=data[track_start][msid_index]
  #Now find the ending index.
  for x in range(track_start+1, end_i):
    if data[x][msid_index]!=ms_id:
      track_end=x-1
      break
  if track_end==-1:
    track_end=end_i-1

  return track_start, track_end
#End get_track_indices

#-------------------- extract_field -----------------------------------------
#Extract and return a copy of all messages from data that contain data in
#the given field. Return -1 if error encountered.
#start_i and end_i can be passed but default to 0 and end-of-data.
#----------------------------------------------------------------------------
def extract_field(data, field, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in extract_field: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1
  if field<0 or field>=len(data[0]):
    print("Error in extract_field: Invalid field index of: "+str(t)+
          "! Must be 0 to "+str(len(data[0])))
    return -1

  field_msgs=[]
  for i in data[start_i:end_i]:
    if isdata(i[field]):               #If there is data in the field, then
      field_msgs.append(i[:])          #add this entry.

  print("Total entries containing data in field "+str(field)+" : "+
        str(len(field_msgs)))
  return field_msgs
#End extract_field

#-------------------- extract_type ------------------------------------------
#Given a specific message sub-type, return a copy of all entries of that
#sub-type from raw_data. There are six message types but we are only interested
#in the MSG type which are generated by the aircraft and has 8 sub-types.
#start_i and end_i can be passed but default to 0 and end-of-data.
#Return -1 if error encountered.
#----------------------------------------------------------------------------
def extract_type(raw_data, t, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(raw_data)
  if start_i<0 or start_i>=end_i:
    print("Error in extract_type: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1
  if len(raw_data[0])!=22:
    print("Error in extract_type: Data not in correct format!")
    print("  Number of fields: "+str(len(raw_data[0])))
    return -1
  if t<1 or t>8:                       #Check for invalid ADSB raw message type
    print("Error in extract_type: Invalid message type of: "+str(t))
    return -1

  type_msgs=[]
  t=str(t)
  type_count=0
  track_count=0
  ms_id=""
  for i in raw_data[start_i:end_i]:
    if i[1]==t:
      if i[4]!=ms_id:
        track_count+=1
        ms_id=i[4]
      type_msgs.append(i[:])
      type_count+=1

  print("Total entries containing MSG type: "+t+" is "+str(type_count)+
        ",  total tracks: "+str(track_count))
  return type_msgs
#End extract_type

#-------------------- extract_location --------------------------------------
#Extract only MSG types 2 and 3 and only their mode-s id, alt, lat, and lon.
#Converts the location values from strings to numeric types, but does not
#standardize or modify the values. Only works on raw data (22 fields) or on
#a complete extracted data set of 13 fields.
#start_i and end_i can be passed but default to 0 and end-of-data.
#Returns a list containing the extracted set of location data.
#Returns -1 if error encountered.
#----------------------------------------------------------------------------
def extract_location(data, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in extract_location: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1

  loc_data=[]
  track_count=0
  ms_id=""
  if len(data[0])==13:                 #Work with a subset from extract_data.
    for i in data[start_i:end_i]:
      if i[2]!=None:                   #Only include entries containing
        if i[0]!=ms_id:                #location data.
          track_count+=1               #Keep track of number of unique tracks.
          ms_id=i[0]
        #Copy ms id and location data directly.
        loc_data.append(i[0:4])
  elif len(data[0])==22:               #Complete set of raw data.
    for i in data[start_i:end_i]:
      if i[1]=="2" or i[1]=="3":       #Only include message types with
        if i[4]!=ms_id:                #location data.
          track_count+=1               #Keep track of number of unique tracks.
          ms_id=i[4]
        #Copy ms id and location data as numbers, not strings.
        loc_data.append([i[4], int(i[11]), float(i[14]), float(i[15])])
  else:                                #Incorrect sub-set of data passed.
    print("Error in extract_location: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1

  print("Total entries containing location data: "+str(len(loc_data))+
        ",  total tracks: "+str(track_count))
  return loc_data
#End extract_location

#-------------------- extract_data ------------------------------------------
#Extract all useful data and return a copy as list entries containing:
#Mode-s ID, altitude, latitude, longitude, speed, direction, vertical rate,
#year, month, day, hour, minute, second (13 fields). The generated date/time
#will be extracted from the message that contained lat/lon. Return -1 on error.
#start_i and end_i can be passed but default to 0 and end-of-data.
#----------------------------------------------------------------------------
def extract_data(raw_data, start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(raw_data)
  if start_i<0 or start_i>=end_i:
    print("Error in extract_data: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1
  if len(raw_data[0])!=22:
    print("Error in extract_data: Data not in correct format!")
    print("  Number of fields: "+str(len(raw_data[0])))
    return -1

  print("--------- Extracting entries with useful data ----------")
  data=[]
  for i in raw_data[start_i:end_i]:
    entry=[None]*13
    if i[1]=="2" or i[1]=="3":         #Process position message.
      if len(i[11])>0:                 #Get altitude
        entry[1]=int(i[11])
      if len(i[14])>0:                 #Get latitude
        entry[2]=float(i[14])
      if len(i[15])>0:                 #Get longitude
        entry[3]=float(i[15])
      if i[1]==2:                      #Surface position message.
        if len(i[12])>0:               #Get speed
          entry[4]=int(i[12])
        if len(i[15])>0:               #Get direction
          entry[5]=int(i[15])
    elif i[1]=="4":                    #Process airborne velocity message.
      if len(i[12])>0:                 #Get speed
        entry[4]=int(i[12])
      if len(i[13])>0:                 #Get direction
        entry[5]=int(i[13])
      if len(i[16])>0:                 #Get vertical rate
        entry[6]=int(i[16])
    elif (i[1]=="5" or i[1]=="7") and len(i[11])>0:  #Altitude only.
      entry[1]=int(i[11])
    #If any of the data fields has data, then:
    if not (entry[1:6]==[None, None, None, None, None]):
      entry[0]=i[4]                    #get the mode-s id.
      entry[7:10], entry[10:13]=get_date_time(i)
      data.append(entry)

  print("Total entries in original data: "+str(end_i-start_i))
  print("Total entries containing useful data: "+str(len(data))+
        ",  total tracks: "+str(count_tracks(data)))

  return data
#End extract_data

#-------------------- extract_set -------------------------------------------
#Find and return a copy of all entries where the given field value is equal to
#val. vals can be a single value to compare against or a list with two.
#field is an integer index for the field to compare against for a match.
#start_i and end_i can be passed but default to 0 and end-of-data.
#Return -1 if error encountered.
#op can be as follows:
#   These 4 must be used with a two element list for vals
#   oi/oe/ii/ie are used with the following three functions:
#         extract_set, extract_track, find_entry2
# oi  Search outside of range passed as vals but include the two end points.
# oe  Search outside of range and exclude the two end points.
# ii  Search inside range defined by vals[0] - vals[1] and include them.
# ie  Search inside range but exclude the two end points.
#   These 5 must be used with a single value in vals instead of a list of 2.
# <   All entries less than vals.
# <=  All less than or equal to.
# ==  Exact matches with vals only.
# >   All entries greater than vals.
# >=  All entries greater than or equal to.
#----------------------------------------------------------------------------
def extract_set(data, vals, field, op="==", start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in extract_set: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1
  if field<0 or field>=len(data[0]):   #Check for invalid field index.
    print("Error in extract_set: Invalid field index of: "+str(field))
    return -1

  set_msgs=[]
  #User passed a set of two values?
  if type(vals)==list:
    if len(vals)!=2:                   #Invalid number of arguments.
      print("Error in extract_set: Invalid number of values for" +
            "comparison! Must be 2 but "+len(vals)+" sent!")
      return -1
    elif vals[0]==None or vals[1]==None:  #No data for comparison.
      print("Error in extract_set: None type sent for comparison!")
      return -1
    elif type(vals[0])!=type(vals[1]):
      print("Error in extract_set: Unequal data types passed!")
      return -1
    extract_func=find_entry2
  else:
    extract_func=find_entry1

  while start_i<end_i:
    entry, start_i=extract_func(data, vals, field, op, start_i, end_i)
    if type(entry)==list and len(entry)>0:
      #Do not need to make copy of entry since extract_func does this, thus
      set_msgs.append(entry)           #entry[:] not needed here!!
    start_i+=1                         #Skip the index of last returned entry.

  return set_msgs
#End extract_set

#-------------------- extract_track -----------------------------------------
#Find and return copy of the complete track for which a matching entry exists.
#Returns a copy of the first track with a matching entry, or -1 on error.
#If no match is found, returns an empty list.
#start_i and end_i can be passed but default to 0 and end-of-data.
#----------------------------------------------------------------------------
def extract_track(data, vals, field, op="==", start_i=0, end_i=0):
  if end_i<=start_i:
    end_i=len(data)
  if start_i<0 or start_i>=end_i:
    print("Error in extract_track: Index error! start= "+str(start_i)+
          ",  end= "+str(end_i))
    return -1
  if field<0 or field>=len(data[0]):   #Check for invalid field index.
    print("Error in extract_track: Invalid field index of: "+str(field))
    return -1

  #User passed a set of two values?
  if type(vals)==list:
    if len(vals)!=2:                   #Invalid number of arguments.
      print("Error in extract_track: Invalid number of values for" +
            "comparison! Must be 2 but "+len(vals)+" sent!")
      return -1
    elif vals[0]==None or vals[1]==None:  #No data for comparison.
      print("Error in extract_track: None type sent for comparison!")
      return -1
    elif type(vals[0])!=type(vals[1]):
      print("Error in extract_track: unequal data types passed!")
      return -1
    extract_func=find_entry2
  else:
    extract_func=find_entry1

  track_msgs=[]
  temp, temp_i=extract_func(data, vals, field, op, start_i, end_i)
  if temp_i<end_i:                     #If we found a match, then
    #determine the field that holds the ms-id:
    if len(temp)==22:                  #Raw data.
      ms_id=temp[4]
    else:                              #Reduced data set.
      ms_id=temp[0]

    track_start, track_end=get_track_indices(data, ms_id, start_i, end_i)
    #Loop retrieving next track with matching ID until we get the correct one.
    #It is very unlikely there will be multiple, but just-in-case!!
    while temp_i>track_end:
      track_start, track_end=get_track_indices(data, ms_id, track_end+1, end_i)
    #Now, copy all entries for this track.
    for i in data[track_start:track_end+1]:
      track_msgs.append(i[:])

  return track_msgs
#End extract_track

#-------------------- find_entry1 -------------------------------------------
#Find and return a COPY of the first entry in data that matches, comparing
#to a single value. Returns the matching entry and its index. If no match
#is found or an error occured, returns an empty list and end_i.
#start_i and end_i can be passed but default to 0 and end-of-data.
#NOTE:  Performs very little input validation!
#----------------------------------------------------------------------------
def find_entry1(data, val, field, op, start_i, end_i):
  if type(val)==list or type(op)!=str: #An invalid type was passed!
    print("Error in find_entry1: List passed for val or op not a string!")
  elif op=="<":                        #Search for values less than val.
    for x in range(start_i, end_i):
      if data[x][field]<val:
        return data[x][:], x
  elif op=="<=" or op=="=<":           #Search for less than or equal to.
    for x in range(start_i, end_i):
      if data[x][field]<=val:
        return data[x][:], x
  elif op=="==":                       #Search for equality.
    for x in range(start_i, end_i):
      if data[x][field]==val:
        return data[x][:], x
  elif op==">":                        #Search for values greater than val.
    for x in range(start_i, end_i):
      if data[x][field]>val:
        return data[x][:], x
  elif op==">=" or op=="=>":           #Search for greater than or equal to.
    for x in range(start_i, end_i):
      if data[x][field]>=val:
        return data[x][:], x
  else:                                #Invalid operator passed.
    print("Error in find_entry1: An invalid operator of: "+op+" was passed!")

  return [], end_i                     #Nothing found, or an error occured!
#End find_entry1

#-------------------- find_entry2 -------------------------------------------
#Find and return a COPY of the first entry in data that matches from within
#a range defined by two values in vals[]. Returns the matching entry and its
#index. If no match found or an error occured, returns an empty list and end_i.
#start_i and end_i can be passed but default to 0 and end-of-data.
#NOTE:  Performs very little input validation!
#----------------------------------------------------------------------------
def find_entry2(data, vals, field, op, start_i, end_i):
  if type(val)!=list or type(op)!=str: #An invalid type was passed!
    print("Error in find_entry2: vals not a list or op not a string!")
  elif op=="oi":                       #Search outside range, inclusive.
    for x in range(start_i, end_i):
      if data[x][field]<=vals[0] or data[x][field]>=vals[1]:
        return data[x][:], x
  elif op=="oe":                       #Search outside range, exclusive.
    for x in range(start_i, end_i):
      if data[x][field]<vals[0] or data[x][field]>vals[1]:
        return data[x][:], x
  elif op=="ii":                       #Search inside range, inclusive.
    for x in range(start_i, end_i):
      if data[x][field]>=vals[0] and data[x][field]<=vals[1]:
        return data[x][:], x
  elif op=="ie":                       #Search inside range, exclusive.
    for x in range(start_i, end_i):
      if data[x][field]>vals[0] and data[x][field]<vals[1]:
        return data[x][:], x
  else:                                #Invalid operator passed.
    print("Error in find_entry2: An invalid operator of: "+op+" was passed!")

  return [], end_i                     #Nothing found, or an error occured!
#End find_entry2

#-------------------- consolidate_speed -------------------------------------
#Remove duplicate lines that contain speed/azimuth/v-rate. Also copies nearest
#speed/azimuth/v-rate values into lines missing these. Modifies data in place.
#Only works with data extracted using extract_data (13 fields).
#Returns -1 if error encountered.
#----------------------------------------------------------------------------
def consolidate_speed(data):
  if len(data[0])!=13:                 #Invalid data format.
    print("Error in consolidate_speed: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1

  start=end=-1
  #Loop once for each track in set.
  num_tracks=count_tracks(data)
  print("\tTotal tracks: "+str(num_tracks))
  pre_num=len(data)
  for x in range(num_tracks):
    tmp_end=end
    #Get next track indices, start searching at "end" of last track.
    start, end=get_track_indices(data, 0, end+1)
    if start<0 or end<0:                    #Error encountered!
      print("Error in consolidate_speed: ms_id index "+str(x)+" not found")
      print("  using indices of: "+str(tmp_end+1)+" - "+str(len(data)))
      return -1
    #This loop will fill in all entries for this track with missing speed.
    from_list=[]
    to_list=[]
    for x in range(start, end+1):
      if not isdata(data[x][4]):       #If no speed data present in this entry
        i=nearest_time(data, x, 4)     #find nearest entry with a value.
        if i>=0:                       #If an entry was found, copy its data.
          from_list.append(i)
          to_list.append(x)
        else:                          #If no entry found, we are done with
          break                        #this loop.
    for x in range(len(to_list)):      #Now, copy the data.
      data[to_list[x]][4]=data[from_list[x]][4]
      data[to_list[x]][5]=data[from_list[x]][5]
      data[to_list[x]][6]=data[from_list[x]][6]

    #This loop will remove any entries that only contain speed/az/vr and for
    #which a neighbor entry contains the same value.
    msid=data[start][0]
    while start<len(data)-1:
      if data[start+1][0]!=msid:       #If next entry from different track,
        break                          #we are done, so exit loop.
      if data[start][4]!=data[start+1][4] or \
         data[start][5]!=data[start+1][5] or \
         data[start][6]!=data[start+1][6]:
        start+=1
      elif not isdata(data[start][2]):
        data.pop(start)
      elif not isdata(data[start+1][2]):
        data.pop(start+1)
      else:
        start+=1
    end=start

  post_num=len(data)
  print("\tInitial entries: "+str(pre_num)+" \tFinal entries: "+str(post_num))
  print("\tTotal entries removed: "+str(pre_num-post_num))
#End consolidate_speed

#-------------------- consolidate_alt ---------------------------------------
#Remove duplicate lines that just contain altitude. Also copies nearest
#altitude value into speed/azimuth and lat/lon lines. Modifies data in place.
#Only works with data extracted using extract_data (13 fields).
#Returns -1 if error encountered.
#----------------------------------------------------------------------------
def consolidate_alt(data):
  if len(data[0])!=13:                 #Invalid data format.
    print("Error in consolidate_alt: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1

  start=end=-1
  #Loop once for each track in set.
  num_tracks=count_tracks(data)
  print("\tTotal tracks: "+str(num_tracks))
  pre_num=len(data)
  for x in range(num_tracks):
    tmp_end=end
    #Get next track indices, start searching at "end" of last track.
    start, end=get_track_indices(data, 0, end+1)
    if start<0 or end<0:                    #Error encountered!
      print("Error in consolidate_alt: ms_id index "+str(x)+" not found using")
      print("  indices of: "+str(tmp_end+1)+" - "+str(len(data)))
      return -1
    #This loop will fill in all entries for this track with missing altitude.
    from_list=[]
    to_list=[]
    for x in range(start, end+1):
      if not isdata(data[x][1]):       #If no alt data present in this entry,
        i=nearest_time(data, x, 1)     #Find nearest entry with a value.
        if i>=0:                       #If an entry was found, copy its alt.
          from_list.append(i)
          to_list.append(x)
        else:                          #If no entry found, we are done with
          break                        #this loop.
    for x in range(len(to_list)):      #Now, copy the data.
      data[to_list[x]][1]=data[from_list[x]][1]

    #This loop will remove any entries that only contain altitude and for which
    #a neighbor entry contains the same value.
    msid=data[start][0]
    while start<len(data)-1:
      if data[start+1][0]!=msid:       #If next entry from different track,
        break                          #we are done, so exit loop.
      if data[start][1]!=data[start+1][1]: #If altitudes differ, keep both
        start+=1                           #and continue to the next.
      elif not (isdata(data[start][2]) or isdata(data[start][4])):
        data.pop(start)
      elif not (isdata(data[start+1][2]) or isdata(data[start+1][4])):
        data.pop(start+1)
      else:
        start+=1
    end=start

  post_num=len(data)
  print("\tInitial entries: "+str(pre_num)+" \tFinal entries: "+str(post_num))
  print("\tTotal entries removed: "+str(pre_num-post_num))
#End consolidate_alt

#-------------------- nearest_time ------------------------------------------
#Return the index for the entry nearest in time to the passed entry that 
#contains data in the desired field and has the same Mode-s ID.
#Only works with data extracted using extract_data (13 fields).
#Returns -1 if error encountered or no index identified.
#----------------------------------------------------------------------------
def nearest_time(data, index, field):
  if len(data[0])!=13:                 #Invalid data format.
    print("Error in nearest_time: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1
  if index<0 or index>=len(data):
    print("Error in nearest_time: Invalid index of "+str(index))
    return -1
  if field<0 or field>12:
    print("Error in nearest_time: Invalid field of "+str(field))
    return -1

  msid=data[index][0]                  #Get the track id.
  t1=t2=1000000                        #Set to unrealistically large values.
  i1=index-1                           #Initial index for older time entry.
  while i1>=0:                         #While index is still valid:
    if data[i1][0]!=msid:              #When we have left this tracks entries,
      break                            #then quit searching.
    if isdata(data[i1][field]):        #If part of this track and data in field
      t1=time_diff_messages(data[i1], data[index])  #then get time difference,
      break                                         #and quit searching.
    i1-=1                              #If we get here, no entry found yet.

  i2=index+1                           #Initial index for newer time entry.
  while i2<len(data):                  #While index is still valid:
    if data[i2][0]!=msid:              #Same as above!
      break
    if isdata(data[i2][field]):
      t2=time_diff_messages(data[index], data[i2])
      break
    i2+=1

  if t1==1000000 and t2==1000000:      #If no match found, return -1.
    return -1
  elif t1<=t2:                         #If we found an entry prior in time,
    return i1                          #return its index.
  else:                                #If we found an entry later in time,
    return i2                          #return its index.
#End nearest_time

#----------------------------------------------------------------------------
#------------------------ Data analysis functions ---------------------------
#-------------------- find_range --------------------------------------------
#Find and return the minimum and maximum values for a field.
#Return None on error.
#----------------------------------------------------------------------------
def find_range(d, f):
  if f<0 or f>len(d[0]):
    print("Error if find_range: Invalid field index of "+str(f)+" passed!")
    return None

  min_val=max_val=d[0][f]
  for i in d[1:]:
    if i[f]<min_val:   min_val=i[f]
    elif i[f]>max_val: max_val=i[f]

  return min_val, max_val
#End find_range

#-------------------- calc_mean ---------------------------------------------
#Given data and a field index, determine the mathematical mean.
#Return the mean and the total values used (n), or None on error.
#----------------------------------------------------------------------------
def calc_mean(data, field):
  if field<0 or field>=len(data[0]):   #Invalid field index passed.
    print("Error in calc_mean: Invalid field index of "+str(field))
    return None

  field_sum=0.0
  n=0
  for i in data:
    if isinstance(i[field], numbers.Number):   #Only include if entry
      field_sum+=i[field]                      # contains data!
      n+=1

  if n>0:
    return field_sum/n, n
  else:
    return 0, 0
#End calc_mean

#-------------------- calc_sd_var -------------------------------------------
#Determine statistics for a field within data. If no mean is passed,
#then first determine the mean. Return the standard deviation, variance,
#mean, and total values used (n), or None on error.
#----------------------------------------------------------------------------
def calc_sd_var(data, field, mean=None):
  if field<0 or field>=len(data[0]):   #Bad field index passed!
    print("Error in calc_sd_var: Invalid field index of "+str(field))
    return None

  sd=var=0.0
  if mean==None:                       #If no value for mean was passed, then
    mean, n=calc_mean(data, field)     #deteremine the mean.
  n=0
  for i in data:
    if isinstance(i[field], numbers.Number):   #Only include if entry
      var+=(i[field]-mean)**2                  # contains data!
      n+=1
  if n>0:
    var=var/n
    sd=var**0.5

  return sd, var, mean, n
#End calc_variance

#-------------------- remove_track_outliers ---------------------------------
#Identify all outlier entries within each track analyzed individually by track
#and field data where f is a list of field indices to use for this purpose.
#Creates and returns a new data list that has these identified entries removed,
#thus, the data passed in will not be modified.
#If a single integer is passed for f, only that field will be used. If 0 is
#passed, all 12 data fields will be used (1 to 13 with 0=mode S ID).
#A new data set will be created and returned with the outliers removed based on
#the standard deviation multiplier passed in (sd_mult).
#NOTE:  Only works with 13 element entries.
#----------------------------------------------------------------------------
def remove_track_outliers(data, sd_mult=3.0, f=[2, 3]):
  pre_num=len(data)
  ol_list=identify_track_outliers(data, sd_mult, f)
  if ol_list==-1:                      #Check for an error returned.
    print("Error in remove_track_outliers: General error occured.")
    return -1

  data2=remove_entries(data, ol_list)
  print("\tTotal tracks containing outliers: "+str(len(ol_list)))
  display_anomaly_list(ol_list)
  post_num=len(data2)
  print("\tInitial entries: "+str(pre_num)+" \tFinal entries: "+str(post_num))
  print("\tTotal entries removed: "+str(pre_num-post_num)+" from "+
        str(len(ol_list))+" tracks.")

  return data2
#End remove_track_outliers

#-------------------- identify_track_outliers -------------------------------
#Identify the outliers based on individual field analysis for each track
#individually. In other words, the standard deviation will be calculated for
#each individual track and field and, based on the sd_mult, individual entries
#will be identified for removal. f will identify the field (1 to 12) for
#analysis, or if 0 is passed, all 12 fields will be analyzed. Also, f can be a
#list containing specific field indices such as: f= [2, 3] (the default) which
#will analyze based on the latitude and longitude fields.
#A list will be returned with one entry per track containing outliers as such:
#  Mode-s ID, track index, track start/end indices, list of bad entries.
#Set stats_out to 1 to display each track/field combination's statistics.
#NOTE:  Only works with 13 element entries.
#----------------------------------------------------------------------------
def identify_track_outliers(data, sd_mult=3.0, f=[2,3], stats_out=0):
  if len(data[0])!=13:                 #Invalid data format.
    print("Error in identify_track_outliers: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1
  if type(f)==int and (f<0 or f>12):
    print("Error in identify_track_outliers: Selected field invalid!")
    print("  Field value passed: "+str(f))
    return -1
  if f==0:                             #If user wants all fields analyzed,
    f=[1,2,3,4,5,6,7,8,9,10,11,12]     #create list of field indices.

  ol_list=[]
  start=end=-1
  #Loop once for each track in set.
  num_tracks=count_tracks(data)
  print("\tTotal tracks: "+str(num_tracks))
  for tr in range(num_tracks):
    tmp_end=end
    #Get next track indices, start searching at "end" of last track.
    start, end=get_track_indices(data, 0, end+1)
    if start<0 or end<0:                    #Error encountered!
      print("Error in identify_track_outliers: ms_id index "+str(tr)+" not ")
      print("  found using indices of: "+str(tmp_end+1)+" - "+str(len(data)))
      return
    i_list=[]
    if type(f)==list:                  #Process all fields in the list.
      for x in f:
        e, i=identify_outliers(data[start: end+1], x, sd_mult, stats_out)
        if len(i)>0:                  #If we got anomalous entries, then
          for y in i:
            i_list.append(y)          #Add all indices to track list.
    else:
      e, i_list=identify_outliers(data[start: end+1], f, sd_mult, stats_out)

    if len(i_list)>0:                  #If we got anomalous entries, then
      i_list=[x+start for x in i_list] #add track offset to each index, and
      ol_list.append([data[start][0], tr, start, end]+i_list) #add entry.

  return ol_list
#End identify_track_outliers

#-------------------- remove_outliers ---------------------------------------
#Identify all outlier entries for all tracks based on a given field, where
#f is an integer representing a field index containing numeric data.
#Creates and returns a new data list that has these identified entries removed,
#thus, the data passed in will not be modified. sd_mult is the standard
#deviation multiplier that will be used to identify entries for removal.
#The stats_out flag will enable display of various statistics data. The default
#is 1 to enable this output, set to 0 to disable.
#----------------------------------------------------------------------------
def remove_outliers(data, f, sd_mult=3.0, stats_out=1):
  ol, il=identify_outliers(data, f, sd_mult, stats_out)
  if il==-1:                           #Check for a returned error
    print("Error in remove_outliers: General error occured.")
    return -1
  data2=remove_entries(data, i1)
  
  tracks=count_tracks(ol)
  print("\tTotal tracks containing outliers: "+str(tracks))
  print("\tInitial entries: "+str(len(data))+" \tFinal entries: "+
        str(len(data2)))
  print("\tTotal entries removed: "+str(len(il))+", using field: "+str(f))

  return data2
#End remove_outliers

#-------------------- identify_outliers -------------------------------------
#Identify outliers based on a given field and the sd multiplier passed in.
#Return the list of entries containing outliers and a list of their indices.
#Set stats_out (last argument) to 0 to supress statistics display (default=1).
#Return -1 if error encountered.
#----------------------------------------------------------------------------
def identify_outliers(data, f, sd_mult, stats_out=1):
  if f<0 or f>=len(data[0]):   #Invalid field index passed.
    print("Error in identify_outliers: Invalid field value of "+str(f))
    return -1

  if stats_out:
    print("---------- Identifying outliers within field: "+str(f)+
          " with sd multiple: "+str(sd_mult)+" ----------")
  sd, var, mean, n=calc_sd_var(data, f)
  outliers=[]
  indices=[]
  lower=mean-sd_mult*sd
  upper=mean+sd_mult*sd
  if stats_out:
    print("\tTotal values (n)   ="+str(n))
    print("\tMathematic Mean    ="+str(mean))
    print("\tVariance           ="+str(var))
    print("\tStandard Deviation ="+str(sd))
    print("\tLower bound        ="+str(lower))
    print("\tUpper bound        ="+str(upper))

  for x in range(len(data)):
    val=data[x][f]
    #Only look at entries that have valid data! Remove those outside limits.
    if isinstance(val, numbers.Number) and (val<=lower or val>=upper):
      outliers.append(data[x][:])
      indices.append(x)

  if stats_out:
    print(str(len(indices))+" entries extracted from "+
          str(count_tracks(outliers))+" tracks.")
    print("Total entries analyzed: "+str(len(data))+" containing "+
          str(count_tracks(data))+" total tracks.")

  return outliers, indices
#End identify_outliers

#-------------------- remove_entries ----------------------------------------
#Return a copy of the data set with the entries identified in the indices list
#removed. Will work with a 1-dimensional list containing index values, or a 2-d
#list containing a list entry for each track as produced by the functions:
#  analyze_pos
#  identify_track_outliers
#with the following field values:
#  Mode-s ID, track index, track start/end index, list of entries to be removed
#Thus, the list (index values) of entries to be removed start at 4.
#----------------------------------------------------------------------------
def remove_entries(data, indices):
  data2=[]
  if type(indices[0])==list:
    ix=[]
    for i in indices:
      for x in i[4:]:
        ix.append(x)
  else:
    ix=indices

  for x in range(len(data)):
    if x not in ix:
      data2.append(data[x][:])

  return data2
#End remove_entries

#-------------------- standardize_location ----------------------------------
#Standardize location data (lat/lon). If location data has not been extracted
#(raw data was passed), then a copy of the location data only (ms-id, alt, lat,
#lon) will be extracted, standardized, and returned. Otherwise, the data passed
#in will be copied then standardized.
#fl is a flag that signals use of the globally saved min and max values, if
#they exist and are valid, from a previous standardization. Thus, if this flag
#is 1, the previously saved values will be used. If 0 (the default) the values
#will be extracted from the current data.
#The data passed in will NOT be modified!
#xmin(lon), xmax(lon), ymin(lat), ymax(lat) can be passed for standardizing.
#However, the defaults for these are: -950, 950, -450, 450 (for turtle plots)
#Returns -1 if error encountered.
#Returns -2 if the data cannot be standardized.
#----------------------------------------------------------------------------
def standardize_location(data, fl=0, xmin=X_MIN, xmax=X_MAX,
                         ymin=Y_MIN, ymax=Y_MAX):
  global glat_min, glat_max, glon_min, glon_max
  #Check for error conditions:
  l=len(data[0])
  if l!=4 and l!=13 and l!=22:
    print("Error in standardize_location: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1
  elif l==22 or l==13:                 #Reduce/extract data if needed.
    loc_data=extract_location(data)
  else:                                #Data already extracted so make a local
    loc_data=copy_data(data)           #copy for modification and return.

  lat_min, lat_max=find_range(loc_data, 2)  #y coordinate extremes
  lon_min, lon_max=find_range(loc_data, 3)  #x coordinate extremes
  if fl!=0:                            #Attempt to use previous values.
    #Ensure current global values describe a valid range and that the current
    #dataset ranges overlap the current global ranges.
    if glat_min<glat_max and glon_min<glon_max and \
       lat_min<glat_max and lon_min<glon_max and \
       lat_max>glat_min and lon_max>glon_min:
      lat_min=glat_min
      lat_max=glat_max
      lon_min=glon_min
      lon_max=glon_max
      print("Using data ranges from previous standardization.")
    #Otherwise, either previous data ranges are invalid or there is no overlap.
    else:
      print("Previous data ranges invalid or do not overlap current data!")
      print("  Calculating new data ranges for standardization.")
  else:
      print("Calculating new data ranges for standardization.")
  #Now, save current data ranges to global variables.
  glat_min=lat_min
  glat_max=lat_max
  glon_min=lon_min
  glon_max=lon_max

  lon=lon_max-lon_min
  lat=lat_max-lat_min
  if lat==0.0 or lon==0.0:             #Cannot standardize if a range is zero!
    return -2

  l_aspect=lat/lon
  x=xmax-xmin
  y=ymax-ymin
  yx_aspect=y/x
  delta_aspect=l_aspect-yx_aspect
  delta=.01
  sf=l_aspect*(1.0/yx_aspect)
  if delta_aspect>delta:               #sf should be > 1.0 so
    x=x/sf                             #make horizontal mapping range smaller.
  elif delta_aspect<(-delta):          #sf should be < 1.0 so
    y=y*sf                             #make vertical mapping range smaller.
  xmult=x/lon
  ymult=y/lat
  for i in loc_data:
    i[2]=int((i[2]-lat_min)*ymult+ymin+0.5)
    i[3]=int((i[3]-lon_min)*xmult+xmin+0.5)

  return loc_data
#End standardize_location

#-------------------- dist_bearing ------------------------------------------
#Distance and bearing between two lat/lon points, in meters (uses Haversine
#method) and degrees with 0=N and 90=E from p1 to p2.
#If default values of lat_i and lon_i will be used (2 and 3), then p1 and p2
#must be lists with 4 or 13 fields where lat is in field/index 2 and lon in 3.
#Otherwise, p1 and p2 can be in any format as long as lat_i and lon_i index
#the correct fields within p1 and p2! Returns None on error!
#----------------------------------------------------------------------------
def dist_bearing(p1, p2, lat_i=2, lon_i=3):
  if type(p1)!=list or type(p2)!=list or len(p1)!=len(p2):
    print("Error in dist_bearing: p1 or p2 not lists or are unequal length!")
    return None
  elif lat_i<0 or lon_i<0 or lat_i>=len(p1) or lon_i>=len(p1):
    print("Error in dist_bearing: Latitude or Longitude index incorrect!")
    print("\tCurrent values are: "+str(lat_i)+",  "+str(lon_i))
    return None
  elif not (isinstance(p1[lat_i], numbers.Number) and
            isinstance(p1[lon_i], numbers.Number) and
            isinstance(p2[lat_i], numbers.Number) and
            isinstance(p2[lon_i], numbers.Number)):
    print("Error in dist_bearing: Non-numeric latitude or longitude in p1/p2.")
    return None
     
  phi1=math.radians(p1[lat_i])
  phi2=math.radians(p2[lat_i])
  delta_phi=math.radians(p2[lat_i]-p1[lat_i])
  delta_lambda=math.radians(p2[lon_i]-p1[lon_i])
  cos_phi1=math.cos(phi1)
  cos_phi2=math.cos(phi2)

  a=math.sin(delta_phi/2.0)
  b=math.sin(delta_lambda/2.0)
  a=a*a+cos_phi1*cos_phi2*b*b
  c=2.0*math.atan2(math.sqrt(a), math.sqrt(1.0-a))
  dist_meters=R*c                      #R is the average radius of the Earth.

  b1=math.sin(delta_lambda)*cos_phi2
  b2=cos_phi1*math.sin(phi2)-math.sin(phi1)*cos_phi2*math.cos(delta_lambda)
  bearing_degrees=math.atan2(b1, b2)
  bearing_degrees=math.degrees(bearing_degrees)
  
  return dist_meters, bearing_degrees
#End dist_bearing

#-------------------- remove_track_anomalies --------------------------------
#Identify all anomalous entries within each track analyzed individually by
#track and position/speed/altitude. tolerance will be used to determine if a
#calculated speed (based on two lat/lon sets and time difference between them)
#is realistic compared to the speed reported by the transponder. 50% is the
#default and means all calcualted speeds must be within 50% of the reported
#speed from the nearest message (in time) containing a speed value.
#A new data set will be created and returned with the anomalies removed based
#on the tolerance passed in.
#NOTE:  Only works with 13 element entries.
#----------------------------------------------------------------------------
def remove_track_anomalies(data, tolerance=0.5, t=0):
  pre_num=len(data)
  anom_list=analyze_pos(data, tolerance, t)
  if anom_list==-1:                    #Check for an error returned.
    print("Error in remove_track_anomalies: General error occured.")
    return -1

  data2=remove_entries(data, anom_list)
  display_anomaly_list(anom_list)
  post_num=len(data2)
  print("\tInitial entries: "+str(pre_num)+" \tFinal entries: "+str(post_num))
  print("\tTotal entries removed: "+str(pre_num-post_num)+" from "+
        str(len(anom_list))+" tracks.")

  return data2
  #End remove_track_anomalies

#-------------------- analyze_pos -------------------------------------------
#Analyze the position data (lat/lon/alt) for all tracks and return a list of
#tracks with anomalous data points. tolerance deteremines how far off from the
#ADSB reported speed/direction/vertical rate that an entry can be (50%) without
#being listed as an anomaly.
#NOTE:     Currently only speed is analyzed.
#The returned list will contain one entry per track as such:
#  Mode-s ID, track index, track start/end indices, list of bad entries.
#If location and altitude will both be analyzed, two separate lists will be
#returned, the first containing location anomalies, the second altitude.
#The type of analysis performed is based on the value of t as follows:
#  0= Location (lat/lon, default) only, 1= Altitude, 2= both.
#Before applying this function to data, outliers should be removed using:
#  remove_track_outliers
#and altitude/speed data should be combined/consolidated using:
#  consolidate_alt
#  consolidate_speed
#in this order!
#NOTE:  Only works with 13 element entries.
#----------------------------------------------------------------------------
def analyze_pos(data, tolerance=0.5, t=0):
  if len(data[0])!=13:                 #Invalid data format.
    print("Error in analyze_pos: Data not in correct format!")
    print("  Number of fields: "+str(len(data[0])))
    return -1

  if t>0:
    print("Currently, only the ability to analyze location (lat/lon) exists.")
    t=0

  loc_list=[]
  alt_list=[]
  start=end=-1
  anomaly_count=0
  #Loop once for each track in set.
  num_tracks=count_tracks(data)
  print("\tTotal tracks: "+str(num_tracks))
  for tr in range(num_tracks):
    tmp_end=end
    #Get next track indices, start searching at "end" of last track.
    start, end=get_track_indices(data, 0, end+1)
    if start<0 or end<0:                    #Error encountered!
      print("Error in analyze_pos: ms_id index "+str(tr)+" not found")
      print("  using indices of: "+str(tmp_end+1)+" - "+str(len(data)))
      return -1
    if t==0 or t==2:                   #Analyze track for location anomalies.
      tmp_locs=analyze_loc(data[start: end+1], tolerance)
      lcnt=len(tmp_locs)
      if lcnt>0:                       #If we got anomalous entries, then add
        tmp_locs=[x+start for x in tmp_locs] #track offset to each index, and
        loc_list.append([data[start][0], tr, start, end]+tmp_locs) #add entry.
        anomaly_count+=lcnt
    if t==1 or t==2:                   #Analyze track for altitude anomalies.
      tmp_alt=analyze_alt(data[start: end+1], tolerance)
      atmp=len(tmp_alt)
      if atmp>0:                       #If we got anomalous entries, then add
        tmp_alt=[x+start for x in tmp_alt] #track offset to each index, and
        alt_list.append([data[start][0], tr, start, end]+tmp_alt) #add entry.
        anomaly_count+=atmp

  print("--- Total anomalous entries found:" +str(anomaly_count))
  print("--- Of "+str(num_tracks)+" total tracks analyzed, "+
        str(len(loc_list)+len(alt_list))+" contained anomalies.")

  #All done so determine what to return.
  if t==0:
    return loc_list
  elif t==1:
    return alt_list
  return loc_list, alt_list
#End analyze_pos

#-------------------- analyze_loc -------------------------------------------
#Analyze the location (lat/lon) data for a single track and return a list of
#entries containing anomalous data points. This function assumes that
#all entries belong to a single track and does not verify this!
#tolerance deteremines how far off a calculated value can be from the given
#value before a point is listed as an anomaly.
#The analysis performed uses the lat/lon of two consecutive points to determine
#distance and bearing between them and uses the time difference to determine
#speed. It then compares this calculated data with the direction and speed
#reported in the entries to determine validity.
#NOTE:  Only works with 13 element entries.
#----------------------------------------------------------------------------
def analyze_loc(data, tolerance=0.5):
  lat=2; speed=4
  anomaly_list=[]
  dlen=len(data)
  i1=0
  while i1<dlen and not isdata(data[i1][lat]):   #Find first lat/lon entry
    i1+=1                                        #point for comparison.
  if i1>=dlen:                         #If no "first point" found, then
    return []                          #return an empty list.
  i2=i1+1

  while True:                #Loop until end of lat/lon entries encountered.
    while i2<dlen and not isdata(data[i2][lat]):   #Find second lat/lon entry.
      i2+=1
    if i2>=dlen:                       #If no second entry found, exit loop.
      break
    #Get the distance in meters and the bearing in degrees between two points.
    dist, bearing=dist_bearing(data[i1], data[i2])
    sec=time_diff_messages(data[i1], data[i2])   #Get time in seconds.
    if sec<=0.0:                       #If no measurable time difference,
      sec=1.0                          #set to minimum of 1 second.
    calc_speed=dist/sec
    i3=nearest_time(data, i1, speed)   #Get index to closest speed entry.
    #Speeds as given are in knots; we must convert to meters/second.
    if i3!=-1:                         #If we got an entry,
      given_speed1=(data[i3][speed])*KNOTS_TO_MSEC #Get first speed for comp.
    else:                              #No speeds available, so exit loop.
      break

    i4=nearest_time(data, i2, speed)   #Get index to closest speed entry, may
    given_speed2=(data[i4][speed])*KNOTS_TO_MSEC #be the same as i3.
    diff1=math.fabs(calc_speed-given_speed1)
    diff2=math.fabs(calc_speed-given_speed2)
    #If the calculated speed is out-of-tolerance with both given speeds, then
    if diff1>given_speed1*tolerance and diff2>given_speed2*tolerance:
      anomaly_list.append(i2)          #add index for this entry to list.
    else:                              #Otherwise, advance index for next point
      i1=i2
    i2+=1

  return anomaly_list
#End analyze_loc

#-------------------- analyze_alt -------------------------------------------
#Analyze the altitude data for a single track and return a list of entries
#containing anomalous data points. This function assumes that all entries
#belong to a single track and does not verify this!
#tolerance deteremines how far off a calculated value can be from the given
#value before a point is listed as an anomaly.
#The analysis performed uses the altitude of multiple consecutive points to
#determine vertical displacement then uses the time difference to determine
#vertical speed. It then compares this calculated data with the reported
#vertical speed in the entries to determine validity.
#NOTE:  Only works with 13 element entries.
#----------------------------------------------------------------------------
def analyze_alt(data):
  print("analyze_alt under construction!!!")
  return
  alt=1; vrate=6                       #Indices of interest within an entry.
  anomaly_list=[]
#  for x in range(1, len(data)-1):
    
#End analyze_alt

#----------------------------------------------------------------------------
#------------------------ Misc support functions ----------------------------
#-------------------- set_next_color ----------------------------------------
#Set the next color in the sequence.
#----------------------------------------------------------------------------
def set_next_color():
  global color_mode, cc, color_step, color_count
  tmp_cm=color_mode
  if color_mode<3:                     #0-2 Lower one, raise another
    if cc[color_mode]>color_step:
      cc[color_mode]-=color_step
      cc[(color_mode+1)%3]+=color_step
    else:
      color_mode+=1
  elif color_mode<6:                   #3-5 Lower two, raise one
    if cc[color_mode%3]>color_step:
      cc[color_mode%3]-=color_step
      cc[(color_mode+1)%3]-=color_step
      cc[(color_mode+2)%3]+=color_step
    else:
      color_mode+=1
  elif color_mode<9:                   #6-8 Lower two
    if cc[color_mode%3]>color_step:
      cc[color_mode%3]-=color_step
      cc[(color_mode+1)%3]-=color_step
    else:
      color_mode+=1
  elif color_mode<12:                  #9-11 Lower one
    if cc[color_mode%3]>color_step:
      cc[color_mode%3]-=color_step
    else:
      color_mode+=1
  else:                                #Color mode 12= gray levels.
    if cc[0]>color_step:
      cc[0]-=color_step
      cc[1]-=color_step
      cc[2]-=color_step
    else:
      color_mode+=1

  #If the color mode changed, set up for new mode.
  if color_mode!=tmp_cm:
    if color_mode>2 and color_mode<6:
      cc[color_mode%3]=color_max
      cc[(color_mode+1)%3]=color_max-3
      cc[(color_mode+2)%3]=color_min+1
      color_step=45
    elif color_mode>5 and color_mode<9:
      cc[color_mode%3]=color_max-5
      cc[(color_mode+1)%3]=color_max-6
      cc[(color_mode+2)%3]=color_min+10
      color_step=40
    elif color_mode>8 and color_mode<12:
      cc[color_mode%3]=color_max-7
      cc[(color_mode+1)%3]=color_min+2
      cc[(color_mode+2)%3]=color_min+3
      color_step=45
    elif color_mode==12:
      cc[0]=color_max-10
      cc[1]=color_max-10
      cc[2]=color_max-10
      color_step=33
    elif color_mode>12:
      cc[color_mode%3]=color_max-19
      cc[(color_mode+1)%3]=color_min+9
      cc[(color_mode+2)%3]=color_min+11
      color_mode=0
      color_step=45
      color_count=0

  color_count+=1
  if cc[0]>color_max:                  #Ensure no color goes over the
    cc[0]=color_max                    #maximum intensity set.
  if cc[1]>color_max:
    cc[1]=color_max
  if cc[2]>color_max:
    cc[2]=color_max

  if cc[0]<color_min:                  #Ensure no color goes under the
    cc[0]=color_min                    #minimum intensity set.
  if cc[1]<color_min:
    cc[1]=color_min
  if cc[2]<color_min:
    cc[2]=color_min

  return color_count
#End set_next_color

#----------------------------------------------------------------------------
#Key return functions for functions needing a key field.
#One for each field in the ADSB data (22)
def key0(val):
  return val[0]
def key1(val):
  return val[1]
def key2(val):
  return val[2]
def key3(val):
  return val[3]
def key4(val):
  return val[4]
def key5(val):
  return val[5]
def key6(val):
  return val[6]
def key7(val):
  return val[7]
def key8(val):
  return val[8]
def key9(val):
  return val[9]
def key10(val):
  return val[10]
def key11(val):
  return val[11]
def key12(val):
  return val[12]
def key13(val):
  return val[13]
def key14(val):
  return val[14]
def key15(val):
  return val[15]
def key16(val):
  return val[16]
def key17(val):
  return val[17]
def key18(val):
  return val[18]
def key19(val):
  return val[19]
def key20(val):
  return val[20]
def key21(val):
  return val[21]

#Returns the key processing function for field i.
def k(i):
  if i==0:
    return key0
  if i==1:
    return key1
  if i==2:
    return key2
  if i==3:
    return key3
  if i==4:
    return key4
  if i==5:
    return key5
  if i==6:
    return key6
  if i==7:
    return key7
  if i==8:
    return key8
  if i==9:
    return key9
  if i==10:
    return key10
  if i==11:
    return key11
  if i==12:
    return key12
  if i==13:
    return key13
  if i==14:
    return key14
  if i==15:
    return key15
  if i==16:
    return key16
  if i==17:
    return key17
  if i==18:
    return key18
  if i==19:
    return key19
  if i==20:
    return key20
  if i==21:
    return key21

#----------------------------------------------------------------------------

