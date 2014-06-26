/*This source code copyrighted by Lazy Foo' Productions (2004-2013)
and may not be redistributed without written permission.*/

//Using SDL, SDL OpenGL, standard IO, and, strings
#include <SDL2/SDL.h>
#include <SDL_opengl.h>
#include <GL/glu.h>
#include <GL/glx.h>
#include <stdio.h>
#include <string>

//Screen dimension constants
const int SCREEN_WIDTH = 640;
const int SCREEN_HEIGHT = 480;
const int width = 640;
const int height = 480;

const int lenx=45;
const int leny=45;
float points[lenx][leny][3];

int wiggle_count = 0;

bool blend;

bool twinkle;
const int num=50;

struct star
{
  int r, g, b;
  float dist;
  float angle;
};

star stars[num];

float zoom = -15.0f;
float tilt = 90.0f;
float spin;

GLuint loop;
GLuint texture[3];

float xrot;
float yrot;
float zrot;

GLfloat xpos, zpos;

GLfloat walkbias, walkbiasangle;

GLfloat lookupdown;
GLfloat sceneroty;

float rtri;
float rquad;

GLfloat LightAmbient[] = {0.5f, 0.5f, 0.5f, 1.0f};

GLfloat LightDiffuse[] = {1.0f, 1.0f, 1.0f, 1.0f};

GLfloat LightPosition[] = {0.0f, 0.0f, 2.0f, 1.0f};

GLuint filter=0;
const float piover180 = 0.0174532925f;

struct VERTEX
{
  float x,y,z;
  float u,v;
};

struct TRIANGLE
{
  VERTEX vertex[3];
};

struct SECTOR
{
  int numTriangles;
  TRIANGLE* triangle;
};

SECTOR sector1;     /* Our sector */

//Starts up SDL, creates window, and initializes OpenGL
bool init();
void Quit();

//Initializes matrices and clear color
bool initGL();
bool resizeWindow();

//Input handler
void handleKeys( unsigned char key, int x, int y );

//Per frame update
void update();

//Renders quad to the screen
void render();

//Frees media and shuts down SDL
void close();

int loadGLTextures();

void readstr( FILE *f, char *string );

//The window we'll be rendering to
SDL_Window* gWindow = NULL;

//OpenGL context
SDL_GLContext gContext;

//Render flag
bool gRenderQuad = true;
float depth = -5.0f;

/* Read In A String */
void readstr( FILE *f, char *string )
{
    /* Start A Loop */
    do
        {
	    /* Read One Line */
	    fgets( string, 255, f );
        } while ( ( string[0] == '/' ) || ( string[0] == '\n' ) );

    return;
}

/* Setup Our World */
void SetupWorld( const char* worldFile )
{
    FILE *filein;        /* File To Work With */

    int numTriangles;    /* Number of Triangles */
    char oneLine[255];   /* One line from conf file */

    float x, y, z, u, v; /* 3d and texture coordinates */

    int triLoop;         /* Triangle loop variable */
    int verLoop;         /* Vertex loop variable */

    /* Open Our File */
    filein = fopen( worldFile, "rt" );

    /* Grab a line from 'filein' */
    readstr( filein, oneLine );

    /* Read in number of triangle */
    sscanf( oneLine, "NUMPOLLIES %d\n", &numTriangles );

    /* allocate space for our triangles */
    sector1.triangle     = (TRIANGLE*)malloc( numTriangles * sizeof( TRIANGLE ) );
    if ( sector1.triangle == NULL )
	  {
	    fprintf( stderr, "Could not allocate memory for triangles.\n" );
	    Quit();
	  }
    sector1.numTriangles = numTriangles;

    /* Get coords for each triangle */
    for ( triLoop = 0; triLoop < numTriangles; triLoop++ )
	  {
	    for ( verLoop = 0; verLoop < 3; verLoop++ )
		  {
		    readstr( filein, oneLine );
		    sscanf( oneLine, "%f %f %f %f %f\n", &x, &y, &z, &u, &v );
		    sector1.triangle[triLoop].vertex[verLoop].x = x;
		    sector1.triangle[triLoop].vertex[verLoop].y = y;
		    sector1.triangle[triLoop].vertex[verLoop].z = z;
		    sector1.triangle[triLoop].vertex[verLoop].u = u;
		    sector1.triangle[triLoop].vertex[verLoop].v = v;
		  }
	  }

    /* Close Our File */
    fclose( filein );

    return;
}

bool init()
{
	//Initialization flag
	bool success = true;

	//Initialize SDL
	if( SDL_Init( SDL_INIT_VIDEO ) < 0 )
	{
		printf( "SDL could not initialize! SDL Error: %s\n", SDL_GetError() );
		success = false;
	}
	else
	{
		//Use OpenGL 2.1
		SDL_GL_SetAttribute( SDL_GL_CONTEXT_MAJOR_VERSION, 2 );
		SDL_GL_SetAttribute( SDL_GL_CONTEXT_MINOR_VERSION, 1 );

		//Create window
		gWindow = SDL_CreateWindow( "SDL Tutorial",
                                SDL_WINDOWPOS_UNDEFINED,
                                SDL_WINDOWPOS_UNDEFINED,
                                SCREEN_WIDTH,
                                SCREEN_HEIGHT,
                                SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN );
		if( gWindow == NULL )
		{
			printf( "Window could not be created! SDL Error: %s\n", SDL_GetError() );
			success = false;
		}
		else
		{
			//Create context
			gContext = SDL_GL_CreateContext( gWindow );
			if( gContext == NULL )
			{
				printf( "OpenGL context could not be created! SDL Error: %s\n", SDL_GetError() );
				success = false;
			}
			else
			{
				//Use Vsync
				if( SDL_GL_SetSwapInterval( 1 ) < 0 )
				{
					printf( "Warning: Unable to set VSync! SDL Error: %s\n", SDL_GetError() );
				}

				//Initialize OpenGL
				if( !initGL() )
				{
					printf( "Unable to initialize OpenGL!\n" );
					success = false;
				}
        //SetupWorld( "data/world.txt" );
        if( !resizeWindow() ){
          printf( "Unable to resizeWindow!\n" );
					success = false;
        }
			}
		}
	}

	return success;
}

bool resizeWindow()
{
  bool success = true;
	GLenum error = GL_NO_ERROR;
  
  glViewport(0, 0, width, height);
	//Initialize Projection Matrix
	glMatrixMode( GL_PROJECTION );
	glLoadIdentity();

  gluPerspective(45.0f,(GLfloat)width/(GLfloat)height,0.1f,100.0f);
  
	//Initialize Modelview Matrix
	glMatrixMode( GL_MODELVIEW );
	glLoadIdentity();

	//Check for error
	error = glGetError();
	if( error != GL_NO_ERROR )
	{
		printf( "Error initializing OpenGL! %s\n", gluErrorString( error ) );
		success = false;
	}
	
  return success;
}
bool initGL()
{
	bool success = true;
	GLenum error = GL_NO_ERROR;

  if(!loadGLTextures()){
    return false;
  }

  glEnable(GL_TEXTURE_2D);
  glShadeModel(GL_SMOOTH);
  glClearColor(0.0f, 0.0f, 0.0f, 0.5f);
  glClearDepth(1.0f);
  //glEnable(GL_DEPTH_TEST);
  //glDepthFunc(GL_LEQUAL);

  glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
	//Check for error
	error = glGetError();
	if( error != GL_NO_ERROR )
	{
		printf( "Error initializing OpenGL! %s\n", gluErrorString( error ) );
		success = false;
	}

  //glLightfv(GL_LIGHT1, GL_AMBIENT, LightAmbient);
  //glLightfv(GL_LIGHT1, GL_DIFFUSE, LightDiffuse);
  //glLightfv(GL_LIGHT1, GL_POSITION, LightPosition);
  //glEnable(GL_LIGHT1);
  //
  //glColor4f(1.0f, 1.0f, 1.0f, 0.5f);
  glBlendFunc(GL_SRC_ALPHA,GL_ONE);
  glEnable(GL_BLEND);

  for(int i = 0; i < num; i++){
    stars[i].dist = (float(i)/num)*5.0f;
    stars[i].r = rand()%256;
    stars[i].g = rand()%256;
    stars[i].b = rand()%256;
  }

  glPolygonMode(GL_BACK, GL_FILL);
  glPolygonMode(GL_FRONT, GL_LINE);

  for(int x=0; x < lenx; x++){
    for(int y=0; y < leny; y++){
      points[x][y][0] = float((x/(lenx/9.0f))-4.5f);
      points[x][y][1] = float((y/(leny/9.0f))-4.5f);
      points[x][y][2] = float(sin((((x/(lenx/9.0f))*40.0f)/360.0f)*3.14*2.0f));
    }
  }

	return success;
}

void handleKeys( unsigned char key, int x, int y )
{
  //printf("%d\n", key);
	//Toggle quad
	if( key == 'q' )
	{
		gRenderQuad = !gRenderQuad;
	}
  else if(key == 'l'){
    yrot -= 1.5f;
  }
  else if(key == 'j'){
    yrot += 1.5f;
  }
  else if(key == 'i'){
    xpos -= (float)sin(yrot*piover180)*0.05f;
    zpos -= (float)cos(yrot*piover180)*0.05f;
    if(walkbiasangle >= 359.0f){
      walkbiasangle=0.0f;
    }
    else{
      walkbiasangle+=10;
    }
    walkbias = (float)sin(walkbiasangle*piover180)/20.0f;
  }
  else if(key == 'k'){
    xpos += (float)sin(yrot*piover180)*0.05f;
    zpos += (float)cos(yrot*piover180)*0.05f;
    if(walkbiasangle <= 1.0f){
      walkbiasangle=359.0f;
    }
    else{
      walkbiasangle-=10;
    }
    walkbias = (float)sin(walkbiasangle*piover180)/20.0f;
  }
  else if(key == 't'){
    twinkle = !twinkle;
  }
  else if(key == 'b'){
    blend = !blend;
    if(blend){
      glEnable(GL_BLEND);
      glDisable(GL_DEPTH_TEST);
    }
    else{
      glDisable(GL_BLEND);
      glEnable(GL_DEPTH_TEST);
    }
  }
  else if(key == '+')
  {
    zoom += 1.0f;
  }
  else if(key == '-'){
    zoom -= 1.0f;
  }
  else if(key == ']'){
    rtri += 10.0f;
  }
  else if(key == '['){
    rtri -= 10.0f;
  }
  else if(key == '1'){
    filter = 0;
  }
  else if(key == '2'){
    filter = 1;
  }
  else if(key == '3'){
    filter = 2;
  }
}

void update()
{
	//No per frame update needed
}

void render()
{
  GLfloat xtrans = -xpos;
  GLfloat ztrans = -zpos;
  GLfloat ytrans = -walkbias-0.25f;
  GLfloat sceneroty = 360.0f - yrot;
  
	//Clear color buffer
	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
  glLoadIdentity();

  glTranslatef(0.0f, 0.0f, -12.0f);
  
  glRotatef(xrot, 1.0f, 0.0f, 0.0f);
  glRotatef(yrot, 0.0f, 1.0f, 0.0f);
  glRotatef(zrot, 0.0f, 0.0f, 1.0f);
  
  glBindTexture(GL_TEXTURE_2D, texture[filter]);
  
  glBegin(GL_QUADS);
  for(int x = 0; x<lenx-1;x++){
    for(int y = 0; y < leny-1; ++y){
      float fx = float(x)/(lenx-1);
      float fy = 1.0-float(y)/(leny-1);
      float fxb = float(x+1)/(lenx-1);
      float fyb = 1.0-float(y+1)/(leny-1);
  
      glTexCoord2f(fx, fy);
      glVertex3f(points[x][y][0], points[x][y][1], points[x][y][2]);
  
      glTexCoord2f(fx, fyb);
      glVertex3f(points[x][y+1][0], points[x][y+1][1], points[x][y+1][2]);
  
      glTexCoord2f(fxb, fyb);
      glVertex3f(points[x+1][y+1][0], points[x+1][y+1][1], points[x+1][y+1][2]);
      
      glTexCoord2f(fxb, fy);
      glVertex3f(points[x+1][y][0], points[x+1][y][1], points[x+1][y][2]);
    }
  }
  glEnd();

  //glBegin(GL_QUADS);
  //    glTexCoord2f(0, 1);
  //    //glTexCoord2f(1, 1);
  //    glVertex3f(points[0][0][0], points[0][0][1], 0);
  //
  //    glTexCoord2f(0, 0);
  //    //glTexCoord2f(1, 0);
  //    glVertex3f(points[0][44][0], points[0][44][1], 0);
  //
  //    glTexCoord2f(1, 0);
  //    //glTexCoord2f(0, 0);
  //    glVertex3f(points[44][44][0], points[44][44][1], 0);
  //    
  //    glTexCoord2f(1, 1);
  //    //glTexCoord2f(0, 1);
  //    glVertex3f(points[44][0][0], points[44][0][1], 0);
  //glEnd();
  //if(wiggle_count == 2){
  //  for(int y=0; y< 45; y++){
  //    float hold = points[0][y][2];
  //    for(int x=0; x<44; x++){
  //      points[x][y][2] = points[x+1][y][2];
  //    }
  //    points[44][y][2]=hold;
  //  }
  //  wiggle_count=0;
  //}
  //wiggle_count++;
  //xrot+=0.3f;
  //yrot+=0.2f;
  //zrot+=0.4f;
  
}

void Quit()
{
	//Destroy window	
	SDL_DestroyWindow( gWindow );
	gWindow = NULL;

  if(sector1.triangle){
    free(sector1.triangle);
  }
  
	//Quit SDL subsystems
	SDL_Quit();
}

int loadGLTextures()
{
  int status = 0;
  SDL_Surface* TextureImage[1];
  if((TextureImage[0] = SDL_LoadBMP("data/tim.bmp")))
  {
    status = 1;
    glGenTextures(1, &texture[0]);

    glBindTexture(GL_TEXTURE_2D, texture[0]);
    glTexImage2D(GL_TEXTURE_2D, 0, 3, TextureImage[0]->w,
                 TextureImage[0]->h, 0, GL_BGR,
                 GL_UNSIGNED_BYTE, TextureImage[0]->pixels);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindTexture(GL_TEXTURE_2D, texture[1]);
    glTexImage2D(GL_TEXTURE_2D, 0, 3, TextureImage[0]->w,
                 TextureImage[0]->h, 0, GL_BGR,
                 GL_UNSIGNED_BYTE, TextureImage[0]->pixels);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    
    glBindTexture(GL_TEXTURE_2D, texture[2]);
    gluBuild2DMipmaps(GL_TEXTURE_2D, 3, TextureImage[0]->w,
                 TextureImage[0]->h, GL_BGR,
                 GL_UNSIGNED_BYTE, TextureImage[0]->pixels);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
  }
  if(TextureImage[0]){
    SDL_FreeSurface(TextureImage[0]);
  }
  return status;
}

int main( int argc, char* args[] )
{
	//Start up SDL and create window
	if( !init() )
	{
		printf( "Failed to initialize!\n" );
	}
	else
	{
		//Main loop flag
		bool quit = false;

		//Event handler
		SDL_Event e;
		
		//Enable text input
		SDL_StartTextInput();

		//While application is running
		while( !quit )
		{
			//Handle events on queue
			while( SDL_PollEvent( &e ) != 0 )
			{
				//User requests quit
				if( e.type == SDL_QUIT )
				{
					quit = true;
				}
				//Handle keypress with current mouse position
				else if( e.type == SDL_TEXTINPUT )
				{
					int x = 0, y = 0;
					SDL_GetMouseState( &x, &y );
					handleKeys( e.text.text[ 0 ], x, y );
				}
			}

			//Render quad
			render();
			
			//Update screen
			SDL_GL_SwapWindow( gWindow );
      SDL_Delay(20);
		}
		
		//Disable text input
		SDL_StopTextInput();
	}

	//Free resources and close SDL
	Quit();

	return 0;
}
