#include <stdio.h>
#include <stdlib.h>
#include <GL/gl.h>
#include <GL/glu.h>
#include <SDL2/SDL.h>

#include <iostream>  
  
using namespace std;  
 
const int SCREEN_WIDTH = 640;
const int SCREEN_HEIGHT = 480;

bool done = false;
char text[1024]={0};
SDL_Window *win = NULL;

SDL_GLContext mainGLContext;

int resizeWindow(int width, int height)
{
	/* Setup our viewport. */
	glViewport( 0, 0, ( GLint )width, ( GLint )height );

	glMatrixMode(GL_PROJECTION);						// 选择投影矩阵
	glLoadIdentity();							// 重置投影矩阵

	// 设置视口的大小
	gluPerspective(45.0f,(GLfloat)width/(GLfloat)height,0.1f,100.0f);

	glMatrixMode(GL_MODELVIEW);						// 选择模型观察矩阵
	glLoadIdentity();	

	return true;
}

int initGL()
{
	///* Enable smooth shading */
	//glShadeModel( GL_SMOOTH );

	///* Set the background black */
	glClearColor( 0.0f, 0.0f, 0.0f, 0.0f );

	///* Depth buffer setup */
	//glClearDepth( 1.0f );

	///* Enables Depth Testing */
	//glEnable( GL_DEPTH_TEST );

	///* The Type Of Depth Test To Do */
	//glDepthFunc( GL_LEQUAL );

	///* Really Nice Perspective Calculations */
	//glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST );

	return true;
}

int DrawGLScene()								// 从这里开始进行所有的绘制
{
	//glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);			// 清除屏幕和深度缓存
	//glLoadIdentity();							// 重置当前的模型观察矩阵
	return 1;								//  一切 OK
}


/* function to handle key press events */
void handleKeyPress( SDL_Keysym *keysym )
{
    switch ( keysym->sym )
	{
	case SDLK_ESCAPE:
	    break;
	case SDLK_F1:
	    break;
	default:
	    break;
	}

    return;
}

int handleEvents()
{
	while(!done)
	{
		SDL_Event event;

		char* composition=0;
		int cursor = 0;
		int selection_len = 0;

		if (SDL_PollEvent(&event))
		{
			switch (event.type)
			{
			case SDL_TEXTINPUT:
				strcat(text, event.text.text);
				break;
			case SDL_TEXTEDITING:
				composition = event.edit.text;
				cursor = event.edit.start;
				selection_len = event.edit.length;
				break;
			case SDL_KEYDOWN:
				/* handle key presses */
				handleKeyPress( &event.key.keysym );
				break;
			case SDL_QUIT:
				/* handle quit requests */
				done = true; 
				break;
			default:
				break;
			}

		}
		else
		{
			break;
		}
	}
	return 1;
}
int loop()
{
	SDL_StartTextInput();
	while(!done)
	{
		//handleEvents();
		DrawGLScene();
		//SDL_GL_SwapWindow(win);

		SDL_Delay(20);
	}

	return 1;
}
/* Our program's entry point */  
int main(int argc, char *argv[])  
{
    if (SDL_Init(SDL_INIT_EVERYTHING) == -1){
        std::cout << SDL_GetError() << std::endl;
        return 1;
    }

	/* Sets up OpenGL double buffering */
	//SDL_GL_SetAttribute( SDL_GL_DOUBLEBUFFER, 1 );

    win = SDL_CreateWindow("Hello World!", 
                            SDL_WINDOWPOS_UNDEFINED, 
                            SDL_WINDOWPOS_UNDEFINED, 
                            SCREEN_WIDTH, 
                            SCREEN_HEIGHT, 
                            SDL_WINDOW_SHOWN|SDL_WINDOW_OPENGL);
    if (win == NULL){
        std::cout << SDL_GetError() << std::endl;
        return 1;
    }
 
	initGL();
	resizeWindow(SCREEN_WIDTH, SCREEN_HEIGHT);

	loop();

    SDL_DestroyWindow(win);

    SDL_Quit();
    return 0;  
}  
