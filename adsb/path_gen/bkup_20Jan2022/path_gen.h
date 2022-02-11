//----------------------------------------------------------------------------
//Benjamin Carlson, US Air Force, December, 2021
//This program will read in a configuration file named wp00.txt where 00 can
//be any integer, which contains a line of global values then a set of way
//point locations that define a path. Finally, the last line may contain
//information defining the action to be taken at the end of the path, such as
//creating a loop. The path defined by the input data will be used to create
//a set of 2315 GPS position messages representing an aircraft traveling along
//the waypoints of the input file. It will store the new messages in path00.msg
//where 00 will match the number from the input file.
//Primary code file: path_gen.c  ---   Must have path_gen.h in same directory!
//============================================================================
//All altitude values are in feet, all distance values are in meters!
//All velocities are in feet per second, unless otherwise noted.
//============================================================================
#include <stdio.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include <time.h>

#define WORDS 28                       //# of words in a 2315 GPS message.

//File IO global file names for easier access (no passing of names needed).
char      wp_in[9]="wp00.txt\0";
char    wp_out[13]="wp00_lst.txt\0";
char   gps_out[15]="gps_path00.msg\0";
char  adsb_out[16]="adsb_path00.msg\0";
char plain_out[17]="plain_path00.msg\0";
int gps=1, adsb=0, plain=0;            //Enables/disables type of file output.
//Set to 1 to enable various messages be displayed during processing, 0 to
int screen_out=1;                      //inhibit all output to the screen.

//Variables used to add a perturbation factor to generated values for messages
float var_alt=0.05;                    //Random offset for altitude.
float var_vel=0.05;                    //Random offset for velocity.
float var_dir=0.05;                    //Random offset for direction.
//Random number of seconds added/subtracted to message time step between
int var_time=0;                        //message generation, 0 as default.

double dmin=0.001;                     //Minimum difference of interest.
//Default tolerance values for position, velocity, and altitude.
//double pt=500.0;                       //Max of 500 meters position tolerance.
//double vt=10.0*1.68781;                //Max of 10 knots vel (change to fps).
//double at=500.0;                       //Max of 500 feet altitude.

//These are used to convert angles from 1553 words to degrees.min/sec.
double cir_deg32, vel_div;             //Used for 1553 field conversions.
double deg_rad;                        //Holds PI/180.0 for deg to radians.
double pi2d, pi2m;                     //Holds PI/2.0 and PI*2.0.
double time_div;        //Used for to convert time to GPS 1553 message time.

double phi1=0.0, lam1=0.0;             //Mid values in rads for waypoint set.
double cosphi1, sinphi1;               //Cosine and sine of lat mid point.
double R=6371000.0;                    //Average Earth radius.
double knots_fps=1.68781;              //Conversion of knots to feet per sec.
double feet_mtrs=0.3048;               //Conversion of feet to meters.

uint8_t wp_cnt=0;                      //Number of waypoints, including ea wps.
uint8_t path_wp_cnt=0;                 //Number of wps in the mission path.
unsigned int msg_count=0;              //Count of messages generated.
uint32_t sec_mission_start=0;          //Seconds since start of mission.
int max_sec=INT_MAX;                   //Max time in seconds for path gen.
int sec_step=1;                        //Step size in seconds between gen msgs.
int path_flag=0;                       //Indicates type of path to generate.

//Mission status, 0=between first and second wps, 1= between wp2 and 3, if
uint8_t status=0;                      //equal to wp_cnt, performing end action

//Mission waypoint rule structure.
struct waypoint
{
  struct waypoint *prev, *next;
  int16_t wpnum;                       //Way point id number from mission prof
  uint8_t turn;                        //Turn type, Short=0.
  int8_t lat_dir;                      //North=1, South=-1
  double lat_deg;                      //0 to 90 degrees, min, sec as decimal.
  double lat_rad;                      //Combines direction with angle in rads
  int8_t lon_dir;                      //East=1, West=-1
  double lon_deg;                      //0 to 180 degrees, min, sec, as dec.
  double lon_rad;                      //Combines direction with angle in rads
  //xm, ym, wp_dir, wp_dist are all in the 2d plane (wp_= dir/dist to next wp).
  double xm, ym;                       //X/Y 2d coordinates in meters.
  double wp_dir;                       //Direction to next wp in radians.
  double wp_dist;                      //Distance to next waypoint in meters.
  double alt;                          //Altitude in feet above MSL.
  double vel;                          //Velocity in knots.
  double vel_fps;                      //Velocity in feet per second.
  uint8_t alt_adjust;                  //abrupt=0/true, gradual=1/false.
};
typedef struct waypoint WP;
typedef WP *WPptr;
WPptr wp_base, wp_end, wp_cur;         //wp_cur points to wp being approached.
WPptr wp_path_end;                     //End of wp path not including ea wps.

//Mission endpoint action, usually a loiter.
struct end_action
{
  uint8_t type;                        //Type, 0 undefined, 1 loiter (default)
  uint8_t shape;                       //Shape of loiter path, racetrack=0.
  uint8_t dir;                         //CW=0/true, CCW=1/false.
  double radius;                       //Radius of loiter shape in feet.
  double radiusm;                      //Radius in meters.
  double length;                       //Length of loiter shape in feet.
  double lengthm;                      //Length of shape in meters.
  double bearing;                      //Bearing in degrees.
  double bear_rads;                    //Bearing in radians.
  uint8_t exit_cr;                     //Exit criteria, None=0.
  uint8_t hours;                       //Number of hours to loiter.
  uint8_t mins;                        //Number of minutes to loiter.
  uint8_t secs;                        //Number of seconds to loiter.
  double alt;                          //Altitude for end action.
};
typedef struct end_action EA;          //Endpoint Action structer.
EA ea;                                 //One end action per mission.

//Active and current operational data, including last received 1553 message.
struct current_data
{
  unsigned int msg_data[WORDS];        //Raw message data in 16 bit words.
  //Current data from last message containing raw data in msg_data.
  int8_t lat_dir;                      //North=1, South=-1
  double lat_deg;                      //0 to 90 degrees, min, sec as decimal.
  double lat_rad;                      //Combines direction with angle in rads
  int8_t lon_dir;                      //East=1, West=-1
  double lon_deg;                      //0 to 180 degrees, min, sec, as dec.
  double lon_rad;                      //Combines direction with angle in rads
  double xm, ym;                       //X/Y 2d coordinates in meters.
  double fp_dist;                      //Distance to closest part of fl path.
  double alt;                          //Altitude in feet above MSL.
  double gps_vel, gps_dir;             //Vel/dir in fps/rads as calc from GPS.
  //These may be useful in determining direction based on GPS data.
  double vEast, vNorth, vUp;           //Individual components of vel in fps.
  uint32_t gps_time;                   //GPS seconds past midnight.
  uint32_t msg_time;                   //Mission time that this msg was gen.

  //Direction and distance from prev_xm/ym to current xm/ym, radians, meters.
  double dir;                          //Direction from last to current.
  double dist;                         //Distance from last to current.
};
typedef struct current_data CD;
CD cur_data, prev_data;                //Global structs for current/prev data.

//Support functions
void help(char []);                    //Display instructions for use.
void Reset_mission_data(void);         //Reset all mission data structures.
int Initial_wp_file(void);             //Load initial config and path data.
void Copy_insert(WPptr, WPptr);        //Copy second wp and insert after first.
void Copy_waypoint(WPptr, WPptr);      //Copy data from waypoint.
void Create_EA(int);                   //Create the end action data and wps.
void Create_EA_WP(double, double);     //Create one end-action waypoint.
void Reverse_path(WPptr, WPptr);       //Reverse a waypoint path.
int Generate_msg(uint32_t);            //Generate a 1553 GPS 2315 message.
void Polar_cart(double, double, double *, double *); //Polar to cartesian.

void Write_gps_msg(FILE *, int, int);  //Write current message to gps file.
void Write_adsb_msg(FILE *, int, int); //Write current message to adsb file.
void Write_plain_msg(FILE *, int, int);//Write current message to plain file.
void Write_wp_lst(int);                //Send # of wps to write out.

void WP_set_transform(void);           //Transform waypoint data to 2d.
//Convert a point from lat/lon radians to x/y meters in 2d Euclidean grid.
void Point_transform(double, double, double *, double *);
//Convert a point from x/y meters to lat/lon decimal degrees.
void Cart_lat_lon(double, double, double *, double *);
void Cart_polar(double, double, double *, double *); //Cartesian to polar.

void Delete_lists(void);               //Delete all linked lists.
int AtoI(char [], int *);              //Convert ASCII to an integer.
double AtoF(char [], int *);           //Convert ASCII to a float/double.
void DieWithError(char *);             //Print error message and exit.
//These 6 functions will be removed after development.
void Pause(char *);                    //Pass the message to be displayed.
void Pause2(int);                      //Pass the integer to be displayed.
void Print_EA_data(void);              //Display all data in the ea structure.
void Print_current_data(void);
void Print_WP_list(void);
void Print_WP(WPptr);
//---------------------------------------------------------------------------

