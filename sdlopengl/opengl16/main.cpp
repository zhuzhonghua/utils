#include <SDL2/SDL.h>
#include <SDL_opengl.h>
#include <GL/glu.h>
#include <GL/glx.h>
#include <stdio.h>
#include <string>

#define BOOL		bool
#define FALSE		0
#define TRUE		1

SDL_Window* gWindow = NULL;
SDL_GLContext gContext;

const int SCREEN_WIDTH = 640;
const int SCREEN_HEIGHT = 480;
const int width = 640;
const int height = 480;


bool	keys[512];			// Array Used For The Keyboard Routine
bool	active=TRUE;		// Window Active Flag Set To TRUE By Default
bool	fullscreen=TRUE;	// Fullscreen Flag Set To Fullscreen Mode By Default
bool	light;				// Lighting ON/OFF
bool	lp;					// L Pressed?
bool	fp;					// F Pressed?
bool	gp;					// G Pressed? ( NEW )

GLfloat	xrot;				// X Rotation
GLfloat	yrot;				// Y Rotation
GLfloat xspeed=0.2f;				// X Rotation Speed
GLfloat yspeed=0.2f;				// Y Rotation Speed
GLfloat	z=-5.0f;			// Depth Into The Screen

GLfloat LightAmbient[]=		{ 0.5f, 0.5f, 0.5f, 1.0f };
GLfloat LightDiffuse[]=		{ 1.0f, 1.0f, 1.0f, 1.0f };
GLfloat LightPosition[]=	{ 0.0f, 0.0f, 2.0f, 1.0f };
GLuint	filter;				// Which Filter To Use
GLuint	texture[3];			// Storage For 3 Textures
GLuint	fogMode[]= { GL_EXP, GL_EXP2, GL_LINEAR };	// Storage For Three Types Of Fog
GLuint	fogfilter = 0;								// Which Fog Mode To Use 
GLfloat	fogColor[4] = {0.5f,0.5f,0.5f,1.0f};		// Fog Color


int LoadGLTextures()									// Load Bitmaps And Convert To Textures
{
  SDL_Surface* TextureImage[1];
  if((TextureImage[0] = SDL_LoadBMP("Data/Crate.bmp"))){
    glGenTextures(3, &texture[0]);					// Create Three Textures

      // Create Nearest Filtered Texture
    glBindTexture(GL_TEXTURE_2D, texture[0]);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
    glTexImage2D(GL_TEXTURE_2D, 0, 3, 
                 TextureImage[0]->w, 
                 TextureImage[0]->h, 0, GL_BGR, GL_UNSIGNED_BYTE, 
                 TextureImage[0]->pixels);

    // Create Linear Filtered Texture
    glBindTexture(GL_TEXTURE_2D, texture[1]);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
    glTexImage2D(GL_TEXTURE_2D, 0, 3, 
                 TextureImage[0]->w, 
                 TextureImage[0]->h, 0, GL_BGR, GL_UNSIGNED_BYTE, 
                 TextureImage[0]->pixels);

    // Create MipMapped Texture
    glBindTexture(GL_TEXTURE_2D, texture[2]);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST);
    gluBuild2DMipmaps(GL_TEXTURE_2D, 3, 
                      TextureImage[0]->w, 
                      TextureImage[0]->h, GL_BGR, GL_UNSIGNED_BYTE, 
                      TextureImage[0]->pixels);
  }

  if(TextureImage[0]){
    SDL_FreeSurface(TextureImage[0]);
  }
  
  return 1;										// Return The Status
}


int InitGL()										// All Setup For OpenGL Goes Here
{
  if (!LoadGLTextures()){
    return FALSE;									// If Texture Didn't Load Return FALSE
  }

  glEnable(GL_TEXTURE_2D);							// Enable Texture Mapping
  glShadeModel(GL_SMOOTH);							// Enable Smooth Shading
  glClearColor(0.5f,0.5f,0.5f,1.0f);					// We'll Clear To The Color Of The Fog
  glClearDepth(1.0f);									// Depth Buffer Setup
  glEnable(GL_DEPTH_TEST);							// Enables Depth Testing
  glDepthFunc(GL_LEQUAL);								// The Type Of Depth Testing To Do
  glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);	// Really Nice Perspective Calculations

  glLightfv(GL_LIGHT1, GL_AMBIENT, LightAmbient);		// Setup The Ambient Light
  glLightfv(GL_LIGHT1, GL_DIFFUSE, LightDiffuse);		// Setup The Diffuse Light
  glLightfv(GL_LIGHT1, GL_POSITION,LightPosition);	// Position The Light
  glEnable(GL_LIGHT1);								// Enable Light One

  glFogi(GL_FOG_MODE, fogMode[fogfilter]);			// Fog Mode
  glFogfv(GL_FOG_COLOR, fogColor);					// Set Fog Color
  glFogf(GL_FOG_DENSITY, 0.35f);						// How Dense Will The Fog Be
  glHint(GL_FOG_HINT, GL_DONT_CARE);					// Fog Hint Value
  glFogf(GL_FOG_START, 1.0f);							// Fog Start Depth
  glFogf(GL_FOG_END, 5.0f);							// Fog End Depth
  glEnable(GL_FOG);									// Enables GL_FOG
  return 1;										// Initialization Went OK
}


void ReSizeGLScene()		// Resize And Initialize The GL Window
{
  glViewport(0,0,width,height);						// Reset The Current Viewport

  glMatrixMode(GL_PROJECTION);						// Select The Projection Matrix
  glLoadIdentity();									// Reset The Projection Matrix

  // Calculate The Aspect Ratio Of The Window
  gluPerspective(45.0f,(GLfloat)width/(GLfloat)height,0.1f,100.0f);

  glMatrixMode(GL_MODELVIEW);							// Select The Modelview Matrix
  glLoadIdentity();									// Reset The Modelview Matrix
}

bool Init()
{
	//Initialization flag
  bool success = true;

  //Initialize SDL
  SDL_Init( SDL_INIT_VIDEO );
  
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
      
          //Create context
  gContext = SDL_GL_CreateContext( gWindow );
  SDL_GL_SetSwapInterval( 1 );
  InitGL();
  ReSizeGLScene();

  return 1;
}

int DrawGLScene()									// Here's Where We Do All The Drawing
{
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	// Clear The Screen And The Depth Buffer
	glLoadIdentity();									// Reset The View
	glTranslatef(0.0f,0.0f,z);

	glRotatef(xrot,1.0f,0.0f,0.0f);
	glRotatef(yrot,0.0f,1.0f,0.0f);

	glBindTexture(GL_TEXTURE_2D, texture[filter]);

	glBegin(GL_QUADS);
		// Front Face
		glNormal3f( 0.0f, 0.0f, 1.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex3f(-1.0f, -1.0f,  1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex3f( 1.0f, -1.0f,  1.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex3f( 1.0f,  1.0f,  1.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex3f(-1.0f,  1.0f,  1.0f);
		// Back Face
		glNormal3f( 0.0f, 0.0f,-1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex3f(-1.0f, -1.0f, -1.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex3f(-1.0f,  1.0f, -1.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex3f( 1.0f,  1.0f, -1.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex3f( 1.0f, -1.0f, -1.0f);
		// Top Face
		glNormal3f( 0.0f, 1.0f, 0.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex3f(-1.0f,  1.0f, -1.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex3f(-1.0f,  1.0f,  1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex3f( 1.0f,  1.0f,  1.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex3f( 1.0f,  1.0f, -1.0f);
		// Bottom Face
		glNormal3f( 0.0f,-1.0f, 0.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex3f(-1.0f, -1.0f, -1.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex3f( 1.0f, -1.0f, -1.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex3f( 1.0f, -1.0f,  1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex3f(-1.0f, -1.0f,  1.0f);
		// Right face
		glNormal3f( 1.0f, 0.0f, 0.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex3f( 1.0f, -1.0f, -1.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex3f( 1.0f,  1.0f, -1.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex3f( 1.0f,  1.0f,  1.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex3f( 1.0f, -1.0f,  1.0f);
		// Left Face
		glNormal3f(-1.0f, 0.0f, 0.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex3f(-1.0f, -1.0f, -1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex3f(-1.0f, -1.0f,  1.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex3f(-1.0f,  1.0f,  1.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex3f(-1.0f,  1.0f, -1.0f);
	glEnd();

	xrot+=xspeed;
	yrot+=yspeed;
	return TRUE;										// Keep Going
}

void HandleKeys( unsigned char key, int x, int y )
{
  if(key == 'l'){
    lp=TRUE;
    light=!light;
    if (!light){
      glDisable(GL_LIGHTING);
    }
    else{
      glEnable(GL_LIGHTING);
    }
  }
  else if(key == 'f'){
    fp=TRUE;
    filter+=1;
    if (filter>2)
      filter=0;
  }
  else if(key == 'g'){
    fogfilter+=1;
    if (fogfilter>2)
      fogfilter=0;
    glFogi (GL_FOG_MODE, fogMode[fogfilter]);
  }
}

void Close()
{
	//Destroy window	
	SDL_DestroyWindow( gWindow );
	gWindow = NULL;

	//Quit SDL subsystems
	SDL_Quit();
}

int main()
{
  Init();
  SDL_Event e;
  SDL_StartTextInput();
  bool quit = false;
  while( !quit ){
    while( SDL_PollEvent( &e ) != 0 ){
      if( e.type == SDL_QUIT ){
        quit = true;
      }
      else if( e.type == SDL_TEXTINPUT ){
        int x = 0, y = 0;
        SDL_GetMouseState( &x, &y );
        HandleKeys( e.text.text[ 0 ], x, y );
      }
    }
    DrawGLScene();
    SDL_GL_SwapWindow( gWindow );
    SDL_Delay(20);
  }
  SDL_StopTextInput();
  Close();
      
  return 0;
}
