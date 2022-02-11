//----------------------------------------------------------------------------
//Benjamin Carlson, 559th SWEG, Tinker AFB, US Air Force, December, 2021
//This program will read in a configuration file named wp00.txt where 00 can
//be any integer, which contains a line of global values then a set of way
//point locations that define a path. Finally, the last line may contain
//information defining the action to be taken at the end of the path, such as
//creating a loop. The path defined by the input data will be used to create
//a set of 2315 GPS position messages representing an aircraft traveling along
//the waypoints of the input file. It will store the new messages in
//gps_path00.msg where 00 will match the number from the input file.
//Primary code file: path_gen.c  ---   Must have path_gen.h in same directory!
//============================================================================
// Compile with "gcc -o path_gen -Wall path_gen.c -lm"
//----------------------------------------------------------------------------

#include "path_gen.h"

//====================== main ===============================================
//Setup initial environment, implement message processing loop.
int main(int argc, char *argv[])
{
  int x, exit_flag=0, curr_step_time=0;
  uint8_t err=0;
    FILE *gps_path_msg;
    FILE *adsb_path_msg;
    FILE *plain_path_msg;

  if(argc==2 && (argv[1][0]=='H' || argv[1][0]=='h' || argv[1][0]=='?'))
  {                                    //If help requested, print help msg.
    help(argv[0]);
    exit(0);
  }

  if(argc>1)                           //File number for I/O entered?
  {
    //Get number, verify data and convert to 2 digits if needed.
    if(strlen(argv[1])>2)                 
    {
      printf("Error! Invalid file number of: %s entered!\n", argv[1]);
      printf("       Must be between 0 and 99 inclusive.\n");
      return -1;
    }
    else if(strlen(argv[1])==2)        //If file number input has two digits,
    {                                  //use them to update all file names.
      wp_in[2]     =argv[1][0];
      wp_in[3]     =argv[1][1];
      wp_out[2]    =argv[1][0];        //Used to write out the created wp list,
      wp_out[3]    =argv[1][1];        //including the end action waypoints.
      gps_out[8]   =argv[1][0];        //File name for output of 2315 gps
      gps_out[9]   =argv[1][1];        //  type message data.
      adsb_out[9]  =argv[1][0];        //File name for ADS-B messages.
      adsb_out[10] =argv[1][1];
      plain_out[10]=argv[1][0];        //File name for plain, csv text data.
      plain_out[11]=argv[1][1];
    }
    else                               //File number only has a single digit.
    {
      wp_in[3]     =argv[1][0];
      wp_out[3]    =argv[1][0];
      gps_out[9]   =argv[1][0];
      adsb_out[10] =argv[1][0];
      plain_out[11]=argv[1][0];
    }
  }

  if(argc>2)                           //Check for additional arguments.
  {
    gps=0;                             //Start off with gps output disabled.
    if(argc>6)
      argc=6;
    for(x=2; x<argc; x++)              //Process each additional argument.
    {
      if(argv[x][0]=='0')              //Disable screen output.
        screen_out=0;
      else if(argv[x][0]=='g' || argv[x][0]=='G')  //Enable gps output.
        gps=1;
      else if(argv[x][0]=='a' || argv[x][0]=='A')  //Enable ADS-B output.
        adsb=1;
      else if(argv[x][0]=='p' || argv[x][0]=='P')  //Enable plain text output.
        plain=1;
    }
    if(gps==0 && adsb==0 && plain==0)  //If no output was enabled, then
      gps=1;                           //enable gps 2315 message output.
  }

  cir_deg32=180.0/pow(2.0, 31.0);      //For conversion to degrees from words.
  vel_div=0.000000953674;
  deg_rad=M_PI/180.0;                  //Used to convert angles to radians.
  pi2d=M_PI*0.5;                       //Used for angle conversions.
  pi2m=M_PI*2.0;                       //Used for angle conversions.
  time_div=0.00006103515625;           //Used to convert 1553 GPS time.
  wp_base=wp_end=wp_cur=NULL;

  srand(time(NULL));
  Reset_mission_data();                //Reset all mission data structures.

  err=Initial_wp_file();               //Get config and waypoints from file.
  if(err)
    DieWithError("\n\tError reading mission profile from file!\n");

  path_wp_cnt=wp_cnt;                  //Keep track of original path wp count.
  wp_path_end=wp_end;                  //Keep track of original end-of-path.
  WP_set_transform();        //Transform waypoint lat/lon data to 2d plane.
//printf("\nwp_cnt before: %d,  path_flag: %d\n", wp_cnt, path_flag);
  if(path_flag==-1)                    //If loop to path start, then we will
    Copy_insert(wp_end, wp_base);      //copy and add the base wp to the end.
  else if(path_flag<-1)                //If end action path enabled, then
    Create_EA(path_flag);              //create the end action data and wps.
//printf("wp_cnt after: %d,  path_flag: %d\n", wp_cnt, path_flag);
//Print_EA_data();
//Pause("2");

//  For testing only. Verifies proper conversion of wp position data.
/*
double lat1, lon1, lat2, lon2;
wp_cur=wp_base;                      //Start at the second waypoint.
printf("\n----- The following demonstrates the effects of the lat/lon to ");
printf("flat, 2D projection then\n   conversion back to lat/lon, thus ");
printf("revealing any errors caused by these processes! -----");
while(wp_cur!=NULL)
{
Cart_lat_lon(wp_cur->xm, wp_cur->ym, &lat2, &lon2);
printf("\n\tWaypoint #%d data", wp_cur->wpnum);
lat1=(wp_cur->lat_deg)*(wp_cur->lat_dir);
lon1=(wp_cur->lon_deg)*(wp_cur->lon_dir);
printf("\nLoaded lat/lon    :\t %f / %f", lat1, lon1);
printf("\nDetermined lat/lon:\t %f / %f", lat2, lon2);
wp_cur=wp_cur->next;
}
Pause("\n\t\tEnd of Waypoint lat/lon data.\n\n");
*/
Print_WP_list();
Pause("? ");
  Write_wp_lst(wp_cnt);                //Write out complete list of waypoints.
  //Start main loop for message generation and storage.
  if(screen_out)                       //Check for screen output enabled.
  {
    printf("\n==============================================================");
    printf("\n ==========Start of message generation, %d waypoints==========\n",
           wp_cnt);
  }
  //Open each type of path file, if enabled and write initial comment lines.
  if(gps)
  {
    gps_path_msg=fopen(gps_out, "w");
    fprintf(gps_path_msg,
      "#This file contains multiple GPS 2315 position messages\n");
    fprintf(gps_path_msg, "#generated from a list of waypoints.\n");
  }
  if(adsb)
  {
    adsb_path_msg=fopen(adsb_out, "w");
    fprintf(adsb_path_msg, "#This file contains multiple ADS-B messages\n");
    fprintf(adsb_path_msg, "#generated from a list of waypoints.\n");
  }
  if(plain)
  {
    plain_path_msg=fopen(plain_out, "w");
    fprintf(plain_path_msg,"#This file contains multiple location points in ");
    fprintf(plain_path_msg, "ASCII plain text format.\n");
    fprintf(plain_path_msg, "#generated from a list of waypoints.\n");
    fprintf(plain_path_msg, "#8 fields per generated location are as follows:\n");
    fprintf(plain_path_msg, "# 1) Message count (starting with 0)\n");
    fprintf(plain_path_msg, "# 2) Altitude as integer in feet above MSL\n");
    fprintf(plain_path_msg,
            "# 3) Latitude as signed decimal (double), South is negative\n");
    fprintf(plain_path_msg,
            "# 4) Longitude as signed decimal (double), West is negative\n");
    fprintf(plain_path_msg, "# 5) Speed as float in feet per second\n");
    fprintf(plain_path_msg, "# 6) Direction as float in radians\n");
    fprintf(plain_path_msg,
            "# 7) Vertical rate as float in fps with negative as down\n");
    fprintf(plain_path_msg, "# 8) Time in seconds from start of messages\n");
    fprintf(plain_path_msg,
            "#One line per generated location, values are comma seperated\n");
  }

  wp_cur=wp_base;                      //Start at the first waypoint.
  while(exit_flag==0)                  //Set to -1 for normal termination.
  {
    //Returns >0 if end of path encountered, forcing exit.
    exit_flag=Generate_msg(sec_mission_start);
    if(gps)                            //Write out gps 2315 message to gps file
      Write_gps_msg(gps_path_msg, curr_step_time, msg_count);  //if enabled.
    if(adsb)                            //Write out ADS-B message to file
      Write_adsb_msg(adsb_path_msg, sec_mission_start, msg_count); //if enabled
    if(plain)                          //Write out plain text data to file
      Write_plain_msg(plain_path_msg,sec_mission_start,msg_count); //if enabled

    msg_count++;
    curr_step_time=sec_step;           //Set current as global time step size.
    if(var_time>0)                     //If enabled, add random offset of +-
    {
      curr_step_time+=(rand()%(var_time*2+1))-var_time;  //whole seconds.
      if(curr_step_time<=0)            //Must have a positive time interval!
        curr_step_time=1;
    }
    sec_mission_start+=curr_step_time; //Generate one message per time int.
    if(sec_mission_start>max_sec)      //Set exit flag.
      exit_flag=1;
    if(screen_out)                     //Check for screen output enabled.
      printf("\nstatus: %d,  time: %d,  msg#: %d",
              status, sec_mission_start, msg_count);
  }

  if(gps)
    fclose(gps_path_msg);
  if(adsb)
    fclose(adsb_path_msg);
  if(plain)
    fclose(plain_path_msg);

  Delete_lists();                      //Delete any linked lists, such as wp.
  if(screen_out)                       //Check for screen output enabled.
  {
    printf("\n Message generation complete. %d messages written.\n", msg_count);
    if(status==0)
      printf("  Approaching the first waypoint.\n");
    else if(status>=wp_cnt)
      printf("  Past last waypoint!\n");
    else
      printf("  Approaching waypoint # %d\n", status+1);
  }
  return exit_flag;
} //End main

//====================== Support functions ==================================
//----------------- help ----------------------------------------------------
void help(char pname[])                //Display simple instructions.
{
  printf("------------ Explanation of command line arguments -------------\n");
  printf("  Call %s with 0, 1, 2, 3, 4, or 5 arguments where:\n", pname);
  printf("    1: The file number for input and output as such:\n");
  printf("       0 (the default), use wp00.txt and *_path00.txt for I/O\n");
  printf("       where * will be gps, adsb, or plain based on the output\n");
  printf("       format explained below.\n");
  printf("       Any positive integer between 0 and 99 inclusive will\n");
  printf("       be used in place of 0 (wp is short for waypoint)\n");
  printf("    2 - 5 can be any combination of the following:\n");
  printf("       0 will turn off/disable console output.\n");
  printf("       gps will enable output of messages in 2315 gps format to\n");
  printf("           file: gps_path00.txt\n");
  printf("       adsb will output ADS-B messages to adsb_path00.txt\n");
  printf("       plain will output csv text data to plain_path00.txt\n");
  Pause("============= waypoint input: Configuration line ==============");
  printf("  One line of configuration data followed by a list of waypoints\n");
  printf("  then a single end-action must be in file wp00.txt as follows:\n");
  printf("  Lines that start with # are comments and will be ignored.\n");
  printf("  First there must be a single line of numeric values for\n");
  printf("  configuration of the path generation system. If this line is\n");
  printf("  missing, the first line of data will be assumed to be a wp.\n");
  printf("  Any missing values will be interpreted as 0.\n");
  printf("  The 7 fields are as follows:\n");
  printf("    1) max_sec defining time length in seconds or path type to\n");
  printf("       be generated as follows:\n");
  printf("       positive integer-> create path for this number of\n");
  printf("         seconds, stop at last wp.\n");
  printf("       0 -> Stop path creation at end of waypoint list,\n");
  printf("         ignoring the end action, if defined.\n");
  printf("       -1-> Ignore end action, instead loop path from end wp\n");
  printf("         back to starting/first waypoint.\n");
  printf("       -2-> Continue through the defined end action.\n");
  printf("       -3-> Continue through end action and reconnect path to\n");
  printf("         the last waypoint.\n");
  printf("       -4-> Continue as in -3 but follow waypoints back to the\n");
  printf("         starting wp (reverse the path).\n");
  printf("       -5-> Complete the end action then go straight to the\n");
  printf("         starting waypoint.\n");
  printf("       any other negative value will be treated as 0.\n");
  printf("    2) sec_step a positive integer value representing the step\n");
  printf("      size in seconds between generated positions/messages.\n");
  printf("    3) sec_mission_start positive integer representing how much\n");
  printf("      time should elapse between the first waypoint and the\n");
  printf("      start of location/message generation.\n");
  printf("    4) var_time A small positive integer used to randomly space\n");
  printf("      the generation of location/message data. This value will\n");
  printf("      be randomly generated (-/+var_time) before each new\n");
  printf("      location/message and added to sec_step. Negative values\n");
  printf("      will be changed to 1. Set to 0 for no deviation in time\n");
  printf("      between location/message generation.\n");
  printf("  The following values represent perturbations to the actual,\n");
  printf("  generated values and should be small floats, such as 0.05.\n");
  printf("    5) var_alt float representing the random amount the\n");
  printf("      altitude will be adjusted. This value will be *50 then\n");
  printf("      + or - to the actual altitude.\n");
  printf("    6) var_vel float value adjustment for velocity but *100 then\n");
  printf("      + or - adjustment to actual velocity.\n");
  printf("    7) var_dir float adjustment for direction (in radians),\n");
  printf("      divided by 2 then + or - adjustment to actual direction.\n");
  printf("  Either space or comma can be used as a separater.\n");
  printf("  Following is an example:\n");
  printf("0  1  0  0  0.05  0.05  0.05\n");
  Pause("-------------- Explanation of waypoint format -------------");
  printf("  This format for waypoint data is a standard format that we\n");
  printf("  decided to keep for compatibility, even though we do not use\n");
  printf("  some of the fields.\n");
  printf("  A brief explanation of the 9 fields follows:\n");
  printf("    1) waypoint number, starting with 0.\n");
  printf("    2) Turn type, such as Short - not used by path_gen.\n");
  printf("    3-4) Latitude as 2 fields, N/S then decimal degrees.\n");
  printf("    5-6) Longitude as 2 fields, E/W then decimal degrees.\n");
  printf("    7) Altitude in feet.\n");
  printf("    8) Velocity in knots.\n");
  printf("    9) Ascent/descent behavior - true implies immediate ascent\n");
  printf("      or descent. - This field not used by path_gen.\n");
  Pause("-------------- Explanation of End Action fields -------------");
  printf("  After all waypoints have been defined, there may be one line\n");
  printf("  defining an end action (EA). Currently, only two EAs are\n");
  printf("  defined: Loop and Racetrack where Loop will cause the path to\n");
  printf("  loop back to the first wp and Racetrack will cause an oval of\n");
  printf("  8 waypoint to be created at the end of the wp path.\n");
  printf("  The 8 fields are defined as follows:\n");
  printf("    1) EA type, Racetrack or Loop (case sensitive!)\n");
  printf("    2) Direction of EA travel: true=CW, false=CCW (case sensitive)\n");
  printf("    3) Path radius in feet\n");
  printf("    4) Path length in feet\n");
  printf("    5) Bearing to the center of the ea shape in degrees\n");
  printf("    6) Loiter exit criteria, None or ? (don't know other options)\n");
  printf("    7) Time as HH:MM:SS - not used by path_gen\n");
  printf("    8) Altitude change in feet from last path wp\n");
  printf("  The waypoints created by the EA definition will be treated as\n");
  printf("  all others and used to define the location/message data.\n");
  printf("  It may be helpful to try different EA configurations to see\n");
  printf("  what results they produce in the generated location data.\n");
}  //End help

//----------------- Reset_mission_data --------------------------------------
//Clear out and reset all mission data in the global current mission data
//structures, cur_data, and ea. Set all values to 0 or an invalid value.
void Reset_mission_data(void)
{
  int x;

  //Reset all message related data in cur_data.
  for(x=0; x<WORDS; x++)               //Clear out the raw message data array.
    cur_data.msg_data[x]=0;
  cur_data.lat_dir=prev_data.lat_dir=0;
  cur_data.lat_deg=prev_data.lat_deg=-1.0;
  cur_data.lat_rad=prev_data.lat_rad=-1.0;
  cur_data.lon_dir=prev_data.lon_dir=0;
  cur_data.lon_deg=prev_data.lon_deg=-1.0;
  cur_data.lon_rad=prev_data.lon_rad=-1.0;
  cur_data.xm=prev_data.xm=0.0;
  cur_data.ym=prev_data.ym=0.0;
  cur_data.fp_dist=prev_data.fp_dist=-1.0;
  cur_data.alt=prev_data.alt=0.0;
  cur_data.gps_vel=prev_data.gps_vel=0.0;
  cur_data.gps_dir=prev_data.gps_dir=-1.0;  //Valid values= 0.0 to 2*pi.
  cur_data.vEast=prev_data.vEast=0.0;
  cur_data.vNorth=prev_data.vNorth=0.0;
  cur_data.vUp=prev_data.vUp=0.0;
  cur_data.gps_time=prev_data.gps_time=0;
  cur_data.msg_time=prev_data.msg_time=0;
  cur_data.dir=prev_data.dir=-1.0;
  cur_data.dist=prev_data.dist=-1.0;

  //Next reset end action data in ea.
  ea.type=0;                           //End action of 0 is undefined/invalid.
  ea.shape=ea.dir=-1;
  ea.radius=ea.length=0.0;
  ea.bearing=ea.bear_rads=-1.0;
  ea.exit_cr=0;
  ea.hours=ea.mins=ea.secs=0;
  ea.alt=0.0;
  return;
} //End Reset_mission_data

//----------------- Initial_wp_file -----------------------------------------
//Read in configuration data and waypoint list from file. Return 0 on success.
int Initial_wp_file(void)
{
  int i;                               //Index into text line from file.
  char line[1000];                     //Array for line of file data.
  WPptr wp_ptr=NULL;
  FILE *wp_file=fopen(wp_in, "r");

  wp_cnt=0;
  if(!wp_file)
  {
    printf("\n\tERROR! Unable to open file: %s\n", wp_in);
    return 1;
  }

  //First read in line with global configuration data, skipping comment lines.
  //This line must exist even if all values are defaults.
  while(fgets(line, 998, wp_file))
  {
    if(line[0]=='#')                   //Skip comment lines.
      continue;
    break;
  }
  //If line ends in a non-digit, it is likely a wp line, so skip parameter
  if(!(strlen(line)>3 && (int)line[strlen(line)-2]>57))  //processing.
  {
    //Now line should contain configuration data, so parse it here.
    i=0;                               //index into line for number extraction.
    max_sec=(int)AtoF(line, &i);       //These 4 should be ints but just in
    sec_step=(int)AtoF(line, &i);      //case, we'll read them as floats and
    sec_mission_start=(int)AtoF(line, &i);  //convert.
    var_time=(int)AtoF(line, &i);
    var_alt=AtoF(line, &i);
    var_vel=AtoF(line, &i);
    var_dir=AtoF(line, &i);
    fgets(line, 998, wp_file);         //Get first waypoint line.
  }

  if(max_sec<=0)                       //Check for path termination requests.
  {
    if(max_sec>=-5)
      path_flag=max_sec;
    max_sec=INT_MAX;                   //Set to complete path -> max value.
  }

  if(sec_step<=0)                      //Sanity check: if invalid, set to
    sec_step=1;                        //message step size of 1 second.

  if(sec_mission_start<0)              //Start time sanity check.
    sec_mission_start=0;

  if(var_time<0)
    var_time=0;

  if(var_alt<0.0 || var_alt>0.5)       //Keep variableness within reason.
    var_alt=0.0;
  if(var_vel<0.0 || var_vel>0.5)       //Keep variableness within reason.
    var_vel=0.0;
  if(var_dir<0.0 || var_dir>0.5)       //Keep variableness within reason.
    var_dir=0.0;
//printf("%d, %d, %d, %d, %f, %f, %f\n",max_sec,sec_step,sec_mission_start,
//       var_time, var_alt, var_vel, var_dir);
//Pause2(0);

  do
  {
    i=0;                               //Reset the line index.
    if(line[0]>='0' && line[0]<='9')   //If the first character of the line is
    {                                  //a digit, then this is a waypoint.
      wp_ptr=((WPptr)malloc(sizeof(WP)));
      wp_ptr->wpnum=AtoI(line, &i);    //Get waypoint ID number.
      if(line[++i]=='S')               //Get turn type, Short or Long (0/1).
      {
        wp_ptr->turn=0;
        i++;                           //"Short" is 1 char longer than "Long"!
      }
      else
        wp_ptr->turn=1;
      i+=5;                            //Skip to S/N for lat direction.
      if(line[i]=='N')                 //Get latitude direction, North=1,
        wp_ptr->lat_dir=1;             //South=-1.
      else
        wp_ptr->lat_dir=-1;
      //No need to skip i over non-numeric chars, AtoF and AtoI will do this!
      wp_ptr->lat_deg=AtoF(line, &i);  //Get latitude degrees.
      //Convert direction and angular degrees to radians.
      wp_ptr->lat_rad=(wp_ptr->lat_deg)*(wp_ptr->lat_dir)*deg_rad;
      if(line[++i]=='E')               //Get longitude direction, East=1,
        wp_ptr->lon_dir=1;             //West=-1.
      else
        wp_ptr->lon_dir=-1;
      wp_ptr->lon_deg=AtoF(line, &i);  //Get longitude degrees.
      //Convert direction and angular degrees to radians.
      wp_ptr->lon_rad=(wp_ptr->lon_deg)*(wp_ptr->lon_dir)*deg_rad;
      wp_ptr->xm=wp_ptr->ym=0.0;       //Set grid coordinates to origin.
      wp_ptr->wp_dir=wp_ptr->wp_dist=-1.0;  //Set to invalid values.
      wp_ptr->alt=AtoF(line, &i);      //Get altitude in feet.
      wp_ptr->vel=AtoI(line, &i);      //Get velocity in knots.
      wp_ptr->vel_fps=(wp_ptr->vel)*knots_fps; //Put into feet per second.
      if(line[++i]=='t')               //Get altitude adjustment type.
        wp_ptr->alt_adjust=0;          //true=0, ascend/decend immediately.
      else
        wp_ptr->alt_adjust=1;          //false=0, gradual ascent/decent.
      wp_cnt++;                        //Inc the global count of waypoints.
    }
    else if(line[0]=='#')              //Skip comment lines.
      continue;
    else                               //If not a waypoint, then it must be
    {                                  //an end-of-route loiter command.
      if(line[i]=='R' && line[i+1]=='a') //Get loiter path shape.
      //We may add additional loiter shapes, but racetrack is it for now!
      {
        ea.type=1;                     //1=loiter action.
        ea.shape=0;                    //Racetrack=0
        i+=10;                         //Skip over "Racetrack,"
      }
      else if(line[i]=='L' && line[i+1]=='o') //Loop on waypoints.
      {
        ea.type=2;                     //2=loop over path waypoints.
        i+=5;
      }
      else                             //No other end actions defined yet!
        continue;

      if(line[i]=='t')                 //Get direction, true=CW, false=CCW.
        ea.dir=0;
      else
        ea.dir=1;
      ea.radius=AtoF(line, &i);        //Get path radius in feet.
      ea.radiusm=ea.radius*feet_mtrs;  //Convert to meters.
      ea.length=AtoF(line, &i);        //Get path length in feet.
      ea.lengthm=ea.length*feet_mtrs;
      ea.bearing=AtoF(line, &i);       //Get path bearing in degrees.
      ea.bear_rads=ea.bearing*deg_rad;
      ea.bear_rads=pi2d-ea.bear_rads;  //Convert to 0=East and ccw, from
      if(ea.bear_rads<0.0)             //0=North and cw, regardless of what
        ea.bear_rads+=pi2m;            //type of ea is being performed.

      if(line[++i]=='N')               //Get loiter exit criteria, None=0.
        ea.exit_cr=0;
      else                             //Don't know what else possible yet.
        ea.exit_cr=1;
      ea.hours=AtoI(line, &i);         //Get hours (no effect if exit_cr=0).
      ea.mins=AtoI(line, &i);          //Get minutes.
      ea.secs=AtoI(line, &i);          //Get seconds.
      ea.alt=AtoF(line, &i);           //Get change in altitude, in feet.
    }
    if(wp_ptr==NULL)                   //This is an end action.
      continue;
    else if(wp_base==NULL)             //This is the first waypoint.
    {
      wp_base=wp_end=wp_cur=wp_ptr;
      wp_ptr->prev=wp_ptr->next=NULL;
    }
    else                               //This is not the first waypoint.
    {
      wp_end->next=wp_ptr;
      wp_ptr->prev=wp_end;
      wp_ptr->next=NULL;
      wp_end=wp_ptr;
    }
    wp_ptr=NULL;
  } while(fgets(line, 998, wp_file));

  ea.alt+=wp_end->alt;                 //Update ea alt based on last path wp.
  wp_end->wp_dist=1.0;                 //Give distance a dummy value.

  fclose(wp_file);
  return 0;
} //End Initial_wp_file

//----------------- Copy_insert ---------------------------------------------
//Make a copy of wp_to and insert it into the path after wp_from. If wp_to is
//the base of the current path, then instead, copy wp_from and make it the
//new base of the path. The waypoint number from the new wp will simply be
//an increment from the waypoint count.
void Copy_insert(WPptr wp_from, WPptr wp_to)
{
  if(wp_from==wp_to)                   //Do not allow duplicate wp!
  {
    if(screen_out)
      Pause("Error in Copy_insert: Duplicate waypoint passed!");
    return;
  }
  else if(wp_from==NULL || wp_to==NULL)  //Check for null pointer!
  {
    if(screen_out)
      Pause("Error in Copy_insert: Null pointer passed!");
    return;
  }

  WPptr wpt=((WPptr)malloc(sizeof(WP)));  //Temp pointer for creation of wps.
  //Check if wp_to is the base for the current path. If so, and the from wp
  //is not the end of the current path, then insert the from wp as the new
  //path base.
  if(wp_to==wp_base && wp_from!=wp_end)
  {
    Copy_waypoint(wp_from, wpt);
    wpt->prev=NULL;
    wpt->next=wp_base;
    wp_base->prev=wpt;
    wp_cnt+=1;
    Cart_polar((wp_base->xm)-(wpt->xm), (wp_end->ym)-(wpt->ym),
                &(wpt->wp_dir), &(wpt->wp_dist));
    wp_base=wpt;
    return;
  }

  Copy_waypoint(wp_to, wpt);
  wpt->prev=wp_from;
  wp_cnt+=1;
  Cart_polar((wpt->xm)-(wp_from->xm), (wpt->ym)-(wp_from->ym),
              &(wp_from->wp_dir), &(wp_from->wp_dist));

  if(wp_from->next!=NULL)              //If not adding to the path end, insert.
  {
    wpt->next=wp_from->next;
    wpt->next->prev=wpt;
    wp_from->next=wpt;
    Cart_polar((wpt->next->xm)-(wpt->xm), (wpt->next->ym)-(wpt->ym),
                &(wpt->wp_dir), &(wpt->wp_dist));
  }
  else                                 //Adding to the end of the wp list.
  {
    wpt->next=NULL;
    wp_from->next=wpt;
    wp_end=wpt;
  }
  return;
} //End Copy_insert

//----------------- Copy_waypoint -------------------------------------------
//Copy the contents of first wp to second wp. If second is NULL, create new.
void Copy_waypoint(WPptr wp_from, WPptr wp_to)
{
  wp_to->prev=wp_from->prev;
  wp_to->next=wp_from->next;
  wp_to->wpnum=wp_from->wpnum;
  wp_to->turn=wp_from->turn;
  wp_to->lat_dir=wp_from->lat_dir;
  wp_to->lat_deg=wp_from->lat_deg;
  wp_to->lat_rad=wp_from->lat_rad;
  wp_to->lon_dir=wp_from->lon_dir;
  wp_to->lon_deg=wp_from->lon_deg;
  wp_to->lon_rad=wp_from->lon_rad;
  //xm, ym, wp_dir, wp_dist are all in the 2d plane (wp_= dir/dist to next wp).
  wp_to->xm=wp_from->xm;
  wp_to->ym=wp_from->ym;
  wp_to->wp_dir=wp_from->wp_dir;
  wp_to->wp_dist=wp_from->wp_dist;
  wp_to->alt=wp_from->alt;
  wp_to->vel=wp_from->vel;
  wp_to->vel_fps=wp_from->vel_fps;
  wp_to->alt_adjust=wp_from->alt_adjust;

  return;
} //End Copy_waypoint

//----------------- Create_EA -----------------------------------------------
//Create the end action data and list of waypoints defining its path.
//If path_falg==-2, then create ea waypoints and extend path through them.
//If path_flag==-3, then connect last ea waypoint back to the last path wp.
//If path_flag==-4, Connect to last path wp then follow wps back to first wp.
//If path_flag==-5, Connect last ea wp to first path wp.
//If path_flag=0/-1, do not create the end action path, simply return.
void Create_EA(int path_flag)
{
  double d, pi6d=M_PI/6.0, pi3d=M_PI/3.0;

  if(path_flag>=-1)                    //Indicates end action should not be
    return;                            //created.
  if(ea.type==1)                       //Check for loiter end action.
  {
    if(ea.shape==0)                    //Shape is a racetrack.
    {
      path_wp_cnt=wp_cnt;              //Keep track of original path wp count.

      d=ea.bear_rads+pi2d;             //Determine direction to the first wp.
      //For racetrack, we will make 8 intermediate waypoints, 4 at each curve.
      Create_EA_WP(d, ea.lengthm*0.5); //Create first ea wp and
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi6d;                         //Determine angle to wp2.
      Create_EA_WP(d, ea.radiusm);     //Create second ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi3d;                         //Determine angle to wp3.
      Create_EA_WP(d, ea.radiusm);     //Create third ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi3d;                         //Determine angle to wp4.
      Create_EA_WP(d, ea.radiusm);     //Create fourth ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi6d;                         //Determine angle to wp5.
      Create_EA_WP(d, ea.lengthm);     //Create fifth ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi6d;                         //Determine angle to wp6.
      Create_EA_WP(d, ea.radiusm);     //Create sixth ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi3d;                         //Determine angle to wp7.
      Create_EA_WP(d, ea.radiusm);     //Create seventh ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.

      d-=pi3d;                         //Determine angle to wp8.
      Create_EA_WP(d, ea.radiusm);     //Create eigth ea wp.
      wp_cnt+=1;                       //Keep track of number of wpts.
    }
    //No other end action loiter shapes defined yet!

    //Now we need to check for CCW travel and reverse direction for CCW.
    if(ea.dir==1)                      //dir of 1 indicates CCW travel.
    {                                  //Point last path wp to new ea wp.
      Cart_polar(wp_end->xm-wp_path_end->xm, wp_end->ym-wp_path_end->ym,
                 &(wp_path_end->wp_dir), &(wp_path_end->wp_dist));
      Reverse_path(wp_path_end->next, wp_end);
      wp_cur=wp_path_end->next;
      wp_path_end->next=wp_end;        //Point to new first ea wp.
      wp_end=wp_cur;
    }
    wp_end->next=NULL;
    if(path_flag==-3 || path_flag==-4) //Connect last ea wp to last path wp.
      Copy_insert(wp_end, wp_path_end);

    if(path_flag==-4)                  //Travel back through path wps to base.
    {
      wp_cur=wp_path_end;              //Start with the path end node.
      while(wp_cur->prev!=NULL)
      {
        Copy_insert(wp_end, wp_cur->prev);
        wp_cur=wp_cur->prev;
      }
    }
    else if(path_flag==-5)             //Indicates path should continue
      Copy_insert(wp_end, wp_base);
  }
  return;
} //end Create_EA

//----------------- Create_EA_WP --------------------------------------------
//Create a single end-action wp from the current ea_end wp.
void Create_EA_WP(double dir, double dist)
{
  if(dir<0.0)                          //Check for wrap-around.
    dir+=pi2m;
  else if(dir>=pi2m)
    dir-=pi2m;

  wp_cur=((WPptr)malloc(sizeof(WP)));  //Create the wp structure.
  wp_end->wp_dir=dir;                  //Set direction and distance from last
  wp_end->wp_dist=dist;                //wp to the new wp.
  wp_end->next=wp_cur;                 //Link last wp to new one.

  //Determine x/y coordinates from polar coordinates.
  Polar_cart(dir, dist, &(wp_cur->xm), &(wp_cur->ym));
  (wp_cur->xm)+=wp_end->xm;            //Add in offset from last waypoint.
  (wp_cur->ym)+=wp_end->ym;
  wp_cur->alt=ea.alt;                  //Set altitude from end action data.
  wp_cur->vel=wp_end->vel;             //Set velocity in knots from last wp.
  wp_cur->vel_fps=wp_end->vel_fps;     //Set velocity in feet per second.
  wp_cur->prev=wp_end;                 //Link new wp to previous one.
  wp_cur->next=NULL;
  wp_cur->wp_dir=wp_end->wp_dir;       //Temp value, same direction as last.
  wp_cur->wp_dist=0.0;
  wp_cur->wpnum=wp_cnt;                //Assign integer value based on wp cnt.
  wp_cur->turn=wp_end->turn;
  //Now, convert the xm and ym to actual lat/lon values.
  Cart_lat_lon(wp_cur->xm, wp_cur->ym, &(wp_cur->lat_deg), &(wp_cur->lon_deg));
  wp_cur->lat_rad=wp_cur->lat_deg*deg_rad; //Get latitude in radians.
  wp_cur->lon_rad=wp_cur->lon_deg*deg_rad; //Get longitude in radians.
  if(wp_cur->lat_deg>=0.0)             //If North, set dir to +1.
    wp_cur->lat_dir=1;
  else                                 //Otherwise, set dir to -1 and make
  {                                    //degrees positive.
    wp_cur->lat_dir=-1;
    wp_cur->lat_deg*=(-1);
  }
  if(wp_cur->lon_deg>=0.0)             //If East, set dir to +1.
    cur_data.lon_dir=1;
  else                                 //Otherwise, set dir to -1 and make
  {                                    //degrees positive.
    wp_cur->lon_dir=-1;
    wp_cur->lon_deg*=(-1);
  }

  wp_end=wp_cur;                       //Set as end wp for end-action list.
  return;
} //End Create_EA_WP

//----------------- Reverse_path --------------------------------------------
//Reverse the path of waypoints from base to end.
//Works with open or circular/closed paths.
void Reverse_path(WPptr base, WPptr end)
{
  double dir, dist;
  WPptr wpt=NULL, cur=NULL;            //Temp pointers for swapping of wps.
  //First some simple safety checks.
  if(base==NULL || base->next==NULL || end==NULL || end->prev==NULL)
  {
    if(screen_out)
      Pause("Error in Reverse_path: NULL pointer passed!");
    return;
  }

  cur=end;                             //Start with the end node.
  dir=cur->wp_dir;                     //Save its direction and distance
  dist=cur->wp_dist;                   //in case of a circular list.
  while(cur!=base)                     //Once for each waypoint.
  {
    wpt=cur->prev;                     //Switch prev and next pointers.
    cur->prev=cur->next;
    cur->next=wpt;
    cur->wp_dir=wpt->wp_dir+M_PI;      //Get direction back to old prev,
    if((cur->wp_dir)>=pi2m)            //new next wp.
      (cur->wp_dir)-=pi2m;
    cur->wp_dist=wpt->wp_dist;         //Get new distance to next wp.
    cur=wpt;
    if(wpt==NULL)                      //Check for disconnected path.
    {
      if(screen_out)
        Pause("Error in Reverse_path: base does not connect to end!");
      return;
    }
  }

  wpt=cur->prev;                       //Switch prev and next pointers.
  cur->prev=cur->next;
  cur->next=wpt;
  if((end->prev)==base)                //If circular list, flip dir 180 degs.
  {
    dir+=M_PI;
    if(dir>=pi2m)                      //Check for wrap-around.
      dir-=pi2m;
    cur->wp_dir=dir;                   //Set dir to saved/flipped dir.
    cur->wp_dist=dist;                 //Use saved distance.
  }
  else if((base->next)!=NULL)          //Check for nodes before base and
  {                                    //point back to the first of them.
    base->wp_dir=(base->next->wp_dir)+M_PI; //Get and flip direction.
    if((base->wp_dir)>=pi2m)                //Check for wrap-around.
      (base->wp_dir)-=pi2m;
    base->wp_dist=base->next->wp_dist;
  }

  return;
} //End Reverse_path

//----------------- Generate_msg --------------------------------------------
//Generate a 1553 GPS 2315 message and put in current_data.
//m_t is the time in seconds since the start of mission for this message.
//Returns in ret_val a value of 1 to indicate generation of the last message,
//otherwise, returns 0.
int Generate_msg(uint32_t m_t)
{
  int ret_val=0;
  uint32_t msg_t;
  double tmp1=0.0, tmp2=0.0, fmsg_t, alt_dif=0.0;
  double wp_dir, wp_dist;              //Direction and distance to next wp.
  double xo, yo;                       //Source location for current dir/dist.

  //Copy current values to previous.
  prev_data.lat_dir=cur_data.lat_dir;
  prev_data.lat_deg=cur_data.lat_deg;
  prev_data.lat_rad=cur_data.lat_rad;
  prev_data.lon_dir=cur_data.lon_dir;
  prev_data.lon_deg=cur_data.lon_deg;
  prev_data.lon_rad=cur_data.lon_rad;
  prev_data.xm=cur_data.xm;
  prev_data.ym=cur_data.ym;
  prev_data.fp_dist=cur_data.fp_dist;
  prev_data.alt=cur_data.alt;
  prev_data.gps_vel=cur_data.gps_vel;
  prev_data.gps_dir=cur_data.gps_dir;
  prev_data.vEast=cur_data.vEast;
  prev_data.vNorth=cur_data.vNorth;
  prev_data.vUp=cur_data.vUp;
  prev_data.gps_time=cur_data.gps_time;
  prev_data.msg_time=cur_data.msg_time;
  prev_data.dir=cur_data.dir;
  prev_data.dist=cur_data.dist;

  msg_t=m_t-prev_data.msg_time;        //Determine time between last message
  fmsg_t=(double)msg_t;                //and this message as int and float.

  //Now, create new data for next message.
  cur_data.msg_time=m_t;
  wp_dir=wp_base->wp_dir;              //Get direction to the next wp.
  wp_dist=(wp_base->wp_dist)/feet_mtrs; //Get distance to the second wp in ft
  alt_dif=(wp_base->next->alt)-(wp_base->alt); //Change in alt.
  if(msg_t==0)                         //If this is the first message and, the
  {                                    //start of mission, use first wp data.
    cur_data.lat_dir=wp_base->lat_dir;
    cur_data.lat_deg=wp_base->lat_deg;
    cur_data.lat_rad=wp_base->lat_rad;
    cur_data.lon_dir=wp_base->lon_dir;
    cur_data.lon_deg=wp_base->lon_deg;
    cur_data.lon_rad=wp_base->lon_rad;
    cur_data.xm=wp_base->xm;
    cur_data.ym=wp_base->ym;
    cur_data.fp_dist=0.0;
    cur_data.alt=wp_base->alt;
    cur_data.gps_vel=wp_base->vel_fps;
    cur_data.gps_dir=wp_base->wp_dir;
    prev_data.alt=wp_base->alt;        //Set for default start altitude.
  }
  else if(msg_count==0)                //First message but not start of
  {                                    //mission.
    xo=wp_base->xm;                    //Get origin for this direction.
    yo=wp_base->ym;
    //Average velocity between first and second wp used for distance
    //traveled for this point generation in feet.
    tmp1=((wp_base->vel_fps+wp_base->next->vel_fps)*0.5)*fmsg_t;
  }
  else                                 //Not start of mission and not first
  {                                    //message.
    xo=prev_data.xm;                   //Get origin for direction of movement.
    yo=prev_data.ym;
    //Get direction and distance to the next wp from the last position.
    Cart_polar((wp_cur->xm)-xo, (wp_cur->ym)-yo, &wp_dir, &wp_dist);
    wp_dist/=feet_mtrs;                //Convert distance to feet.
    tmp1=(prev_data.gps_vel)*fmsg_t;   //Deteremine feet traveled.
    alt_dif=wp_cur->alt-prev_data.alt;
  }

  if(msg_t>0)                          //These instructions are common to all
  {                                    //situations where msg_t>0.
    //Check for overshoot of next waypoint, but stop on the last.
    while(tmp1>wp_dist && wp_cur->next!=NULL)
    {
      tmp2=((tmp1-wp_dist)/tmp1)*fmsg_t; //Determine seconds past wp.
      fmsg_t=tmp2;                     //Update travel time remaining.
      wp_dir=wp_cur->wp_dir;           //Get direction to the next wp.
      wp_dist=(wp_cur->wp_dist)/feet_mtrs; //Get distance to next wp in feet.
      xo=wp_cur->xm;                   //Get origin for this direction
      yo=wp_cur->ym;                   //and distance of travel.
      alt_dif=(wp_cur->next->alt)-(wp_cur->alt);  //Update change in altitude.
      wp_cur=wp_cur->next;
      status++;
      tmp1=(wp_cur->vel_fps)*tmp2;     //Determine feet traveled.
    }
    cur_data.gps_vel=wp_cur->vel_fps;  //Store velocity in feet/sec.
    cur_data.gps_dir=wp_dir;           //Store current direction in radians.
    tmp2=tmp1*feet_mtrs;               //Convert feet traveled to meters.
    Polar_cart(cur_data.gps_dir, tmp2, &cur_data.xm, &cur_data.ym);
    cur_data.xm+=xo;                   //Set adjusted x coordinate in meters.
    cur_data.ym+=yo;                   //Set adjusted y coordinate in meters.

    if(tmp1>=wp_dist && wp_cur->next==NULL)  //If the end of the line has
    {                                  //been reached then,
      ret_val=1;                       //set exit flag, and
      status++;                        //Increment status to wp_cnt.
    }
    Cart_lat_lon(cur_data.xm, cur_data.ym,
                 &(cur_data.lat_deg), &(cur_data.lon_deg));
    cur_data.lat_rad=cur_data.lat_deg*deg_rad; //Get latitude in radians.
    cur_data.lon_rad=cur_data.lon_deg*deg_rad; //Get longitude in radians.
    if(cur_data.lat_deg>=0.0)          //If North, set dir to +1.
      cur_data.lat_dir=1;
    else                               //Otherwise, set dir to -1 and make
    {                                  //degrees positive.
      cur_data.lat_dir=-1;
      cur_data.lat_deg*=(-1);
    }
    if(cur_data.lon_deg>=0.0)          //If East, set dir to +1.
      cur_data.lon_dir=1;
    else                               //Otherwise, set dir to -1 and make
    {                                  //degrees positive.
      cur_data.lon_dir=-1;
      cur_data.lon_deg*=(-1);
    }
    if(wp_cur!=NULL)
    {
      //Formula for the distance from a given point to a line in 2D Euc Space,
      //where our newly generated point= (X0, Y0), and line is defined by
      //two waypoints as such: wp_cur= (X2, Y2), wp_cur->prev= (X1, Y1):
 //dist= |(X2-X1)(Y1-Y0)-(X1-X0)(Y2-Y1)| / sqrt((X2-X1)(X2-X1)+(Y2-Y1)(Y2-Y1))
      xo=wp_cur->xm-wp_cur->prev->xm;  //X2-X1
      yo=wp_cur->ym-wp_cur->prev->ym;  //Y2-Y1
      cur_data.fp_dist=fabs(xo*(wp_cur->prev->ym-cur_data.ym)-
                   (wp_cur->prev->xm-cur_data.xm)*yo) / sqrt(xo*xo+yo*yo);
    }
    else
      cur_data.fp_dist=0.0;
  }

  //Velocity components, alt and message time will be same in all situations.
  tmp2=tmp1*alt_dif/wp_dist;            //Calculate change in altitude.
  tmp1=(rand()%100)*var_alt-var_alt*50.0;
  cur_data.alt=prev_data.alt+tmp2+tmp1; //Adjust last points alt for current p.
  //Add small random component to direction and velocity (+ or -).
  cur_data.gps_vel+=((rand()%100)*var_vel*2.0-100.0*var_vel);
  cur_data.gps_dir+=((rand()%100)*var_dir/100.0-var_dir*0.5);
  Polar_cart(cur_data.gps_dir, cur_data.gps_vel,
             &cur_data.vEast, &cur_data.vNorth);
  if(fmsg_t>0.0)
    cur_data.vUp=(tmp1+tmp2)/fmsg_t;     //Determine vertical velocity in fps.
  else                                   //Avoid divide by zero.
    cur_data.vUp=0.0;
  if(fabs(cur_data.vUp)<0.001)           //Ignore insignificant values.
    cur_data.vUp=0.0;
  cur_data.gps_time=m_t;

  return ret_val;
} //End Generate_msg

//----------------- Polar_cart ----------------------------------------------
//Convert polar coordinates to cartesian with angle in radians, 0 to 2pi ccw,
//and distance in meters.
void Polar_cart(double dir, double dist, double *xp, double *yp)
{
  *xp=dist*cos(dir);
  *yp=dist*sin(dir);
  return;
} //End Polar_cart

//----------------- Write_gps_msg -------------------------------------------
//Write current message data in current_data to the open gps message file.
void Write_gps_msg(FILE *msgf, int pause_time, int msg_cnt)
{
  uint32_t tmp32;                      //Placeholder variable for conversions.
  double tmp_dbl;
  uint16_t lat1=0, lat2=0;             //Holds two latitude words.
  uint16_t lon1=0, lon2=0;             //Holds two longitude words.
  uint16_t alt1=0;                     //Holds altitude above MSL.
  uint16_t vE1=0, vE2=0;               //Holds E/W velocity words.
  uint16_t vN1=0, vN2=0;               //North/South velocity words.
  uint16_t vU1=0, vU2=0;               //Up/Down velocity words.
  uint16_t time1=0, time2=0;           //Two time data words.
  char ns='N', ew='E';                 //Holds lat/lon N/S, E/W.
  char vew='E', vns='N', vud='U';      //Holds velocity component directions.

  //Convert latitude to 2 16 bit words with word 1 bit 8 as sign bit, 0=N.
  tmp32=(uint32_t)(0.5+cur_data.lat_deg/cir_deg32); //Convert to GPS msg units.
  lat2=tmp32 & 0x0000FFFF;                //Get least significant word.
  lat1=tmp32>>16;                         //Get most significant word.
  if(cur_data.lat_dir!=1)                 //Get direction as char for comment
  {                                       //and set sign bit if South.
    ns='S';
    lat1=lat1 | 0x8000;
  }

  //Convert longitude to 2 16 bit words with word 1 bit 8 as sign bit, 0=E.
  tmp32=(uint32_t)(0.5+cur_data.lon_deg/cir_deg32);
  lon2=tmp32 & 0x0000FFFF;
  lon1=tmp32>>16;
  if(cur_data.lon_dir!=1)
  {
    ew='W';
    lon1=lon1 | 0x8000;
  }

  //Convert Altitude to a single 16 bit two's compliment word.
  tmp_dbl=(cur_data.alt)*0.25+0.5;
  if(tmp_dbl<0.0)                      //If negative, convert to two's comp.
  {
    alt1=(uint16_t)(-tmp_dbl);
    alt1=(~alt1)+1;
  }
  else                                 //Positive values convert directly.
    alt1=(uint16_t)tmp_dbl;

  //Convert East/West velocity into 2 16 bit words from a single 32
  //bit two's compliment word.
  tmp_dbl=(cur_data.vEast)/vel_div+0.5;  //Convert to GPS msg units.
  if(tmp_dbl<0.0)                      //If direction is west, then
  {                                    //make 32 bit two's compliment
    tmp32=(uint32_t)(-tmp_dbl);        //number and save direction for
    tmp32=(~tmp32)+1;                  //comment line.
    vew='W';
  }
  else                                 //Otherwise, positive value so
    tmp32=(uint32_t)tmp_dbl;           //copy directly.
  vE2=tmp32 & 0x0000FFFF;              //Get least significant word.
  vE1=(tmp32>>16) & 0x0000FFFF;        //Get most significant word.

  //Convert N/S velocity into 2 16 bit words, with word 1, bit 8 - sign.
  tmp_dbl=(cur_data.vNorth)/vel_div+0.5;  //Convert to GPS msg units.
  if(tmp_dbl<0.0)                      //If direction is south, then
  {                                    //make 32 bit two's compliment
    tmp32=(uint32_t)(-tmp_dbl);        //number and save direction for
    tmp32=(~tmp32)+1;                  //comment line.
    vns='S';
  }
  else                                 //Otherwise, positive value so
    tmp32=(uint32_t)tmp_dbl;           //copy directly.
  vN2=tmp32 & 0x0000FFFF;              //Get least significant word.
  vN1=(tmp32>>16) & 0x0000FFFF;        //Get most significant word.

  //Convert Up/Down velocity into 2 16 bit words, with word 1, bit 8 - sign.
  tmp_dbl=(cur_data.vUp)/vel_div+0.5;  //Convert to GPS msg units.
  if(tmp_dbl<0.0)                      //If direction is down, then
  {                                    //make 32 bit two's compliment
    tmp32=(uint32_t)(-tmp_dbl);        //number and save direction for
    tmp32=(~tmp32)+1;                  //comment line.
    vud='D';
  }
  else                                 //Otherwise, positive value so
    tmp32=(uint32_t)tmp_dbl;           //copy directly.
  vU2=tmp32 & 0x0000FFFF;              //Get least significant word.
  vU1=(tmp32>>16) & 0x0000FFFF;        //Get most significant word.

  //Convert current message time to two 16 bit data words.
  tmp32=(uint32_t)(0.5+cur_data.gps_time/time_div); //Convert to GPS msg units.
  time2=tmp32 & 0x0000FFFF;            //Get least significant word.
  time1=(tmp32>>16) & 0x0000FFFF;      //Get most significant word.

  //First write out pause time before next message, in milliseconds.
  if(msg_cnt>0)
    fprintf(msgf,"#%d\n", pause_time*1000);

  //Next, add comment lines.
  fprintf(msgf, "#lat=%04X %04X = %c %lf\n", lat1, lat2, ns, cur_data.lat_deg);
  fprintf(msgf, "#lon=%04X %04X = %c %lf\n", lon1, lon2, ew, cur_data.lon_deg);
  fprintf(msgf, "#alt=%04X      = %d feet above sea level\n", alt1,
          (int)cur_data.alt);
  fprintf(msgf, "#  Total velocity in fps = %lf\n", cur_data.gps_vel);
  fprintf(msgf, "#vE= %04X %04X = %c %.2f\n", vE1, vE2, vew, cur_data.vEast);
  fprintf(msgf, "#vN= %04X %04X = %c %.2f\n", vN1, vN2, vns, cur_data.vNorth);
  fprintf(msgf, "#vU= %04X %04X = %c %.2f\n", vU1, vU2, vud, cur_data.vUp);
  fprintf(msgf, "#  %d\n", msg_cnt);
  //Then add 28 16 bit words of GPS data.
  fprintf(msgf, "0xC102,0xF86D,0xF86D,0x88C0,0x%04X,0x%04X,0x%04X\n",
          lat1, lat2, lon1);
  fprintf(msgf, "0x%04X,0x%04X,0x0000,0x%04X,0x%04X,0x%04X,0x%04X\n",
          lon2, alt1, vE1, vE2, vN1, vN2);
  fprintf(msgf, "0x%04X,0x%04X,0xC001,0x0000,0x0000,0xB000,0x%04X\n",
          vU1, vU2, time1);
  fprintf(msgf, "0x%04X,0x0000,0x0000,0x0000,0x0000,0x0000,0x4000\n", time2);

  return;
} //End Write_gps_msg

//----------------- Write_adsb_msg ------------------------------------------
//Write current message data in current_data to the open ADS-B message file.
void Write_adsb_msg(FILE *msgf, int pause_time, int msg_cnt)
{
  ;
} //End Write_adsb_msg

//----------------- Write_plain_msg -----------------------------------------
//Write current message data in current_data to open plain text message file.
void Write_plain_msg(FILE *msgf, int msg_time, int msg_cnt)
{
  CD cd=cur_data;
  //Data is written out as follows:
  //Message number as an integer, altitude as integer in feet above MSL,
  //Latitude/Longitude as signed decimals (doubles), S/W negative
  //Speed as float in feet per second, Direction as float in radians
  //Vertical rate as float with negative as down
  fprintf(msgf, "%6d, %d, %lf, %lf, %f, %f, %.02f, %d\n", msg_cnt, (int)cd.alt,
      cd.lat_dir*cd.lat_deg, cd.lon_dir*cd.lon_deg, (float)cd.gps_vel,
      (float)cd.gps_dir, (float)cd.vUp, msg_time);
} //End Write_plain_msg

//----------------- Write_wp_lst --------------------------------------------
//Write out the current list of waypoints, including end action wps.
void Write_wp_lst(int tot_wps)
{
  int x;
  WPptr wpt=NULL;
  FILE *wp_file=NULL;
  if(wp_cnt<1 || wp_base==NULL)        //Error check, do we have any waypoints!
  {
    printf("Error in Write_wp_lst: No waypoints in the list!\n");
    return;
  }

  wp_file=fopen(wp_out, "w");
  if(tot_wps<1 || tot_wps>wp_cnt)      //If invalid value, set to default.
    tot_wps=wp_cnt;                    //wp_cnt is the global var for # of wps.

  fprintf(wp_file, "#List of waypoints for current path generation.\n");
  fprintf(wp_file, "#This list includes all end action and duplicated wps.\n");
  fprintf(wp_file, "#Format for # waypoint data is as follows:\n");
  fprintf(wp_file, "# 1)Waypoint number, starting at 0 for the root/first wp.\n");
  fprintf(wp_file, "# 2)Altitude as integer in feet above MSL\n");
  fprintf(wp_file, "# 3)Latitude as signed decimal (double), South is neg\n");
  fprintf(wp_file, "# 4)Longitude as signed decimal (double), West is neg\n");
  fprintf(wp_file, "# 5)Speed to next wp as float in feet per second\n");
  fprintf(wp_file, "# 6)Direction to next wp as float in radians\n");
  fprintf(wp_file, "# 7)Distance to next wp as float in meters\n\n");
  fprintf(wp_file, "# %d\n", tot_wps);

  wpt=wp_base;
  for(x=0; x<tot_wps; x++)             //Write out each waypoint's data.
  {
    fprintf(wp_file, "%3d, %d, %lf, %lf, %lf, %lf, %lf\n", x, (int)wpt->alt,
            (wpt->lat_dir)*(wpt->lat_deg), (wpt->lon_dir)*(wpt->lon_deg),
            wpt->vel_fps, wpt->wp_dir, wpt->wp_dist);
    wpt=wpt->next;
    if(wpt==NULL)                      //Safety check, should never occur!
    {
      printf("Error in Write_wp_lst: WP # %d is NULL!\n", x);
      fclose(wp_file);
      return;
    }
  }

  fclose(wp_file);
  return;
} //End Write_wp_lst

//----------------- WP_set_transform ----------------------------------------
//Transform waypoint data from lat/lon 3d points to a 2d Euclidean plane
//(x, y) with meter distances. Perform at start of mission only.
void WP_set_transform(void)
{
  int x;
  WPptr wpt=NULL;                      //Used for wp to wp direction/distance.

  wp_cur=wp_base;                      //Start with first wp.
  phi1=wp_cur->lat_rad;
  lam1=wp_cur->lon_rad;
  //This loop will determine the mid-point for the lat/lon coordinates of
  //the waypoints to be used as the origin in the 2D plane projection.
  for(x=1; x<wp_cnt; x++)
  {
    wp_cur=wp_cur->next;               //Move to next waypoint.
    if(wp_cur==NULL)                   //If we reached the end of the rule
    {                                  //set but there should be more WPs,
      printf("\nERROR! to few waypoints!");  //Debug only, remove later!
      wp_cnt=x;                        //change the waypoint count and break.
      break;
    }
    phi1+=wp_cur->lat_rad;
    lam1+=wp_cur->lon_rad;
  }
  phi1/=(double)(wp_cnt);              //Determine average values to be used
  lam1/=(double)(wp_cnt);              //as the origin (0,0) for the area.
  cosphi1=cos(phi1);
  sinphi1=sin(phi1);

  //This loop will determine the x/y coordinates in the 2d plane for each wp
  //which will be used for line/distance comparisons with new position data.
  wp_cur=wp_base;                      //Start with the first wp.
  for(x=0; x<wp_cnt; x++)
  {
    Point_transform(wp_cur->lat_rad, wp_cur->lon_rad,
                    &(wp_cur->xm), &(wp_cur->ym));
    wp_cur=wp_cur->next;               //Move to next wp.
  }

  //Now determine the direction in radians and distance in meters between wps.
  wp_cur=wp_base;
  for(x=1; x<wp_cnt; x++)
  {
    wpt=wp_cur->next;                  //Get "to" waypoint.
    Cart_polar((wpt->xm)-(wp_cur->xm), (wpt->ym)-(wp_cur->ym),
                &(wp_cur->wp_dir), &(wp_cur->wp_dist));
    wp_cur=wpt;
  }
  //Now set the end waypoint to point in the same direction as previous wp.
  wp_end->wp_dir=wp_end->prev->wp_dir;
  wp_end->wp_dist=0.0;                 //No other waypoint in the chain!

  return;
} //End WP_set_transform

//----------------- Point_transform -----------------------------------------
//Transform individual point data from lat/lon 3d point to a 2d Euclidean
//plane (x, y) with meter distances. The grid origin must already have
//been computed by WP_set_transform.
void Point_transform(double phi2, double lam2, double *xm, double *ym)
{
  double s1, s2, d1, d, az, cosphi2;
  //Calculate the distance between the central point and current point.
  cosphi2=cos(phi2);
  s1=sin((phi2-phi1)*0.5);
  s2=sin((lam2-lam1)*0.5);
  s1=s1*s1;
  s2=s2*s2;
  d1=s1+cosphi1*cosphi2*s2;
  az=2.0*atan2(sqrt(d1), sqrt(1.0-d1));
  d=R*az;                              //Distance from origin.
  //Calculate the azimuth from the central point to current point.
  d1=lam2-lam1;
  s1=sin(d1)*cosphi2;
  s2=cosphi1*sin(phi2)-sinphi1*cosphi2*cos(d1);
  az=pi2d-atan2(s1, s2);
  if(az<0.0)
    az+=pi2m;
  //Determine the 2d Euclidean coordinates based on the polar coordinates.
  *xm=d*cos(az);
  *ym=d*sin(az);

  return;
} //End Point_transform

//----------------- Cart_lat_lon --------------------------------------------
//Convert a point from x/y meters to lat/lon decimal degrees.
void Cart_lat_lon(double xm, double ym, double *lat2, double *lon2)
{
  double dir, dist;
  Cart_polar(xm, ym, &dir, &dist);     //Get polar coordinates.
  dist/=R;                             //Convert distance to angular distance.
  //Need to convert direction from East=0 CCW, to North=0, CW for trig funcs.
  dir=5.0*M_PI/2.0-dir;
  if(dir>=pi2m)
    dir-=pi2m;
  //Determine new lat/lon in radians.
  *lat2=asin(sinphi1*cos(dist)+cosphi1*sin(dist)*cos(dir));
  *lon2=lam1+atan2(sin(dir)*sin(dist)*cosphi1, cos(dist)-sinphi1*sin(*lat2));
  //Convert new lat/lon from radians to +-decimal degrees.
  *lat2=(*lat2)*180.0/M_PI;
  *lon2=(*lon2)*180.0/M_PI;

  return;
} //End Cart_lat_lon

//----------------- Cart_polar ----------------------------------------------
//Convert cartesian coordinates to polar with angle in radians, 0 to 2pi ccw,
//and distance in meters.
void Cart_polar(double xp, double yp, double *dir, double *dist)
{
  *dist=sqrt(xp*xp+yp*yp);
  *dir=atan2(yp, xp);
  if(*dir<0.0)
    *dir=*dir+pi2m;
  return;
} //End Cart_polar

//----------------- Delete_lists --------------------------------------------
//Delete current mission profile lists.
//At this point, we only have the wp list, but others will be added.
void Delete_lists(void)
{
  wp_cur=wp_base;
  while(wp_cur->next!=NULL)            //Delete waypoints individually.
  {
    wp_base=wp_cur;
    wp_cur=wp_cur->next;
    free(wp_base);
  }
  free(wp_cur);
  wp_base=wp_end=wp_path_end=wp_cur=NULL;
  return;
} //End Delete_lists

//----------------- AtoI ----------------------------------------------------
//A simple, custom string to integer converter.
int AtoI(char line[], int *ii)         //Return integer at ii in line[] and
{                                      //advance ii (skip leading spaces).
  int val=0, sign=1, i;
  if(ii==NULL)
    i=0;
  else
    i=*ii;

  //Scan until digit is found. Stop when end of line or end of string reached.
  while((line[i]<'0' || line[i]>'9') && line[i]!='\0' && line[i]!='\n')
  {
    //Check for sign, but only use it if a number follows (skip spurious +-).
    if(line[i]=='-' && line[i+1]>='0' && line[i+1]<='9')
      sign=-1;
    i++;
  }

  if(i>0 && line[i-1]=='.')            //Check for float, return 0 if float.
    return 0;

  while(line[i]>='0' && line[i]<='9')  //Convert to integer.
    val=val*10+(int)(line[i++])-48;
  if(ii!=NULL)
    *ii=i;

  return (val*sign);
} //End AtoI

//----------------- AtoF ----------------------------------------------------
//A simple string to float converter. Works with scientific notation.
double AtoF(char line[], int *ii)      //Return double float at ii in line[]
{                                      //and advance ii.
  int y, z, i;                         //(skip leading blanks)
  double val=0.0, a=.1, sign=1.0;
  if(ii==NULL)
    i=0;
  else
    i=*ii;

  //Scan until digit is found. Stop when end of line or end of string reached.
  while((line[i]<'0' || line[i]>'9') && line[i]!='\0' && line[i]!='\n')
  {
    //Check for sign, but only use it if a number follows (skip spurious +-).
    if(line[i]=='-' && line[i+1]>='0' && line[i+1]<='9')
      sign=-1.0;
    i++;
  }

  while(line[i]>='0' && line[i]<='9')  //Convert left of decimal.
    val=val*10.0+(double)((int)(line[i++])-48);
  if(line[i]=='.')                     //If there is a decimal then
  {
    i++;
    while(line[i]>='0' && line[i]<='9')  //convert right of decimal.
    {
      val=val+a*(double)((int)(line[i++])-48);
      a*=.1;
    }
  }
  if(line[i]=='e' || line[i]=='E')     //If scientific notation then
  {
    y=0;
    if(line[++i]=='-')
      a=.1;
    else
      a=10.0;
    if(line[i]<'0' || line[i]>9)       //If character after e is + or -
      i++;                             //then skip ahead one.
    while(line[i]>='0' && line[i]<='9')
      y=y*10+(int)(line[i++])-48;
    for(z=0; z<y; z++)
      val=val*a;
  }
  if(ii!=NULL)
    *ii=i;
  return (val*sign);
} //End AtoF

//----------------- DieWithError --------------------------------------------
//A simple function to combine an error message with exit().
void DieWithError(char *errorMessage)
{
  printf("%s", errorMessage);
  exit(1);
} //End DieWithError

//====================== Diagnostic functions ===============================
//----------------- Pause ---------------------------------------------------
void Pause(char *msg)                  //Pass the message to be displayed.
{
  if(msg!=NULL)                        //Print message if there is one.
    printf("\nPause: %s", msg);
  getchar();
  return;
} //End Pause

//----------------- Pause2 --------------------------------------------------
void Pause2(int v)                     //Pass the integer to be displayed.
{
  printf("\nPause: %d", v);
  getchar();
  return;
} //End Pause2

//----------------- Print_EA_data -------------------------------------------
void Print_EA_data(void)
{
  printf("\n================ Start of End Action data =================\n");
  printf(" type: %d,  shape: %d\n", ea.type, ea.shape);
  if(ea.dir==0)
    printf(" Direction: ClockWise\n");
  else
    printf(" Direction: CounterClockWise\n");
  printf(" Radius in feet: %f,  Meters: %f\n", ea.radius, ea.radiusm);
  printf(" Length in feet: %f,  Meters: %f\n", ea.length, ea.lengthm);
  printf(" Bearing in degrees: %f,  Radians: %f\n", ea.bearing, ea.bear_rads);
  printf(" Exit criteria: %d\n", ea.exit_cr);
  printf(" Time hh:mm:ss: %2d:%2d:%2d\n", ea.hours, ea.mins, ea.secs);
  printf(" Change in altitude from last path waypoint in feet: %.02f\n",ea.alt);
  printf("-----------------------------------------------------------\n");
} //End Print_EA_data

//----------------- Print_current_data --------------------------------------
//Diagnostic only, remove after development!
void Print_current_data(void)
{
  printf("\n======== Start of Active Current Location Data ========");
  printf("\n-------- Current data -------- status= %d", status);
  printf("\nLatitude: %d  %lf", cur_data.lat_dir, cur_data.lat_deg);
  printf("\n   in radians: %lf", cur_data.lat_rad);
  printf("\nLongitude : %d  %lf", cur_data.lon_dir, cur_data.lon_deg);
  printf("\n   in radians: %lf", cur_data.lon_rad);
  printf("\n2D Euclidean coordinates: %lf , %lf", cur_data.xm, cur_data.ym);
  printf("\nDistance to closest flight path segment: %lf", cur_data.fp_dist);
  printf("\nDirection (radians) and distance (meters) from last to current:");
  printf(" %f,  %f", cur_data.dir, cur_data.dist);
  printf("\nAltitude (feet): %lf", cur_data.alt);
  printf("\nGPS vel in fps : %f", cur_data.gps_vel);
  printf("\nGPS dir in ccw radians, 0=East: %lf", cur_data.gps_dir);
  printf("\nGPS velocity components (East/West, North/South, Up/Down)\n");
  printf("\t%lf \t%lf \t%lf", cur_data.vEast, cur_data.vNorth, cur_data.vUp);
  printf("\nGPS Time in seconds past midnight: %u", cur_data.gps_time);
  printf("\nDirection/distance from last to current: %f / %f",
         cur_data.dir, cur_data.dist);
  printf("\n-------- Previous data --------");
  printf("\nLatitude: %d  %lf", prev_data.lat_dir, prev_data.lat_deg);
  printf("\n   in radians: %lf", prev_data.lat_rad);
  printf("\nLongitude : %d  %lf", prev_data.lon_dir, prev_data.lon_deg);
  printf("\n   in radians: %lf", prev_data.lon_rad);
  printf("\n2D Euclidean coordinates: %lf , %lf",
         prev_data.xm, prev_data.ym);
  printf("\nDistance to closest flight path segment: %lf", prev_data.fp_dist);
  printf("\nAltitude (feet): %lf", prev_data.alt);
  printf("\nGPS velocity (fps) : %f", prev_data.gps_vel);
  printf("\nGPS dir in ccw radians, 0=East: %lf", prev_data.gps_dir);
  printf("\nGPS velocity components (East/West, North/South, Up/Down)\n");
  printf("\t%lf \t%lf \t%lf", prev_data.vEast, prev_data.vNorth,
         prev_data.vUp);
  printf("\nGPS Time in seconds past midnight: %u", prev_data.gps_time);
  printf("\nDirection/distance from last to current: %f / %f",
         prev_data.dir, prev_data.dist);
  printf("\n\n");
  return;
} //End Print_current_data

//----------------- Print_WP_list -------------------------------------------
//Print waypoint set from start location data to end of wp list.
//Diagnostic only, remove after development!
void Print_WP_list(void)
{
  WPptr wpt=wp_base;
  printf("---------- List of %d waypoints (%d from wp file) -----------\n",
         wp_cnt, path_wp_cnt);
  while(wpt!=NULL)                     //Loop through all waypoints.
  {
    Print_WP(wpt);
    wpt=wpt->next;
  }

  return;
} //End Print_WP_list

//----------------- Print_WP ------------------------------------------------
//Print the contents of a single waypoint.
//Diagnostic only, remove after development!
void Print_WP(WPptr wp)
{
  if(wp==NULL)
    printf("\nNo waypoint data!\n");
  else
  {
    printf("\nData for waypoint # %d", wp->wpnum);
    printf("\n  Turn type   :\t%u", wp->turn);
    printf("\n  Lat dir 1=N:\t%d, degrees %lf, radians %lf",
           wp->lat_dir, wp->lat_deg, wp->lat_rad);
    printf("\n  Lon dir 1=E:\t%d, degrees %lf, radians %lf",
           wp->lon_dir, wp->lon_deg, wp->lon_rad);
    printf("\n  2D Euc coords: %lf, %lf", wp->xm, wp->ym);
    printf("\n  Direction/distance to next wp: %f,  %f",
           wp->wp_dir, wp->wp_dist);
    printf("\n  Altitude (feet) :\t%lf", wp->alt);
    printf("\n  Velocity (knots/fps):\t%f / %f", wp->vel, wp->vel_fps);
    printf("\n  Alt adj type:\t%u\n", wp->alt_adjust);
  }
  return;
} //End Print_WP
//---------------------------------------------------------------------------

