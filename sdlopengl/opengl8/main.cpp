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
GLuint texture[1];

float xrot;
float yrot;
float zrot;

float rtri;
float rquad;

GLfloat LightAmbient[] = {0.5f, 0.5f, 0.5f, 1.0f};

GLfloat LightDiffuse[] = {1.0f, 1.0f, 1.0f, 1.0f};

GLfloat LightPosition[] = {0.0f, 0.0f, 2.0f, 1.0f};

GLuint filter=0;

//Starts up SDL, creates window, and initializes OpenGL
bool init();


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

//The window we'll be rendering to
SDL_Window* gWindow = NULL;

//OpenGL context
SDL_GLContext gContext;

//Render flag
bool gRenderQuad = true;
float depth = -5.0f;

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
  
	return success;
}

void handleKeys( unsigned char key, int x, int y )
{
	//Toggle quad
	if( key == 'q' )
	{
		gRenderQuad = !gRenderQuad;
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
	//Clear color buffer
	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
  glBindTexture(GL_TEXTURE_2D, texture[0]);

  for(int loop=0; loop<num; loop++){
    glLoadIdentity();
    glTranslatef(0.0f, 0.0f, zoom);
    glRotatef(tilt, 1.0f, 0.0f, 0.0f);
    
    glRotatef(stars[loop].angle, 0.0f, 1.0f, 0.0f);
    glTranslatef(stars[loop].dist, 0.0f, 0.0f);

    glRotatef(-stars[loop].angle, 0.0f, 1.0f, 0.0f);
    glRotatef(-tilt, 1.0f, 0.0f, 0.0f);

    if(twinkle){
      glColor4ub(stars[num-loop-1].r, stars[num-loop-1].g,stars[num-loop-1].b,255);
      glBegin(GL_QUADS);
        glTexCoord2f( 0.0f, 1.0f ); glVertex3f( -1.0f, -1.0f, 0.0f );
        glTexCoord2f( 1.0f, 1.0f ); glVertex3f(  1.0f, -1.0f, 0.0f );
        glTexCoord2f( 1.0f, 0.0f ); glVertex3f(  1.0f,  1.0f, 0.0f );
        glTexCoord2f( 0.0f, 0.0f ); glVertex3f( -1.0f,  1.0f, 0.0f );       
      glEnd();
    }
    glRotatef(spin, 0.0f, 0.0f, 1.0f);
    glColor4ub(stars[loop].r,stars[loop].g,stars[loop].b,255);
    glBegin(GL_QUADS);
      glTexCoord2f( 0.0f, 1.0f ); glVertex3f( -1.0f, -1.0f, 0.0f );
      glTexCoord2f( 1.0f, 1.0f ); glVertex3f(  1.0f, -1.0f, 0.0f );
      glTexCoord2f( 1.0f, 0.0f ); glVertex3f(  1.0f,  1.0f, 0.0f );
      glTexCoord2f( 0.0f, 0.0f ); glVertex3f( -1.0f,  1.0f, 0.0f );       
    glEnd();

    spin+=0.01f;
    stars[loop].angle+=float(loop)/num;
    stars[loop].dist-=0.01f;

    if(stars[loop].dist <0.0f){
      stars[loop].dist+=5.0f;
      stars[loop].r = rand()%256;
      stars[loop].g = rand()%256;
      stars[loop].b = rand()%256;
    }
  }
}

void close()
{
	//Destroy window	
	SDL_DestroyWindow( gWindow );
	gWindow = NULL;

	//Quit SDL subsystems
	SDL_Quit();
}

int loadGLTextures()
{
  int status = 0;
  SDL_Surface* TextureImage[1];
  if((TextureImage[0] = SDL_LoadBMP("data/star.bmp")))
  {
    status = 1;
    glGenTextures(1, &texture[0]);
    
    glBindTexture(GL_TEXTURE_2D, texture[0]);
    glTexImage2D(GL_TEXTURE_2D, 0, 3, TextureImage[0]->w,
                 TextureImage[0]->h, 0, GL_BGR,
                 GL_UNSIGNED_BYTE, TextureImage[0]->pixels);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
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
	close();

	return 0;
}
