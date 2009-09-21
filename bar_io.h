
//
// Bar type
//
typedef struct _Bar
{ int time;
  float x;
  float y;
} Bar;

inline Bar *Bar_Static_Cast( int time, float x, float y);

//
// Bar File IO 
//
BarFile* Bar_File_Open      ( const char* filename, const char *mode);
void     Bar_File_Close     ( BarFile *file );
void     Bar_File_Append_Bar( BarFile *file,  Bar* b );
Bar     *Read_Bars          ( BarFile *file, int *n );