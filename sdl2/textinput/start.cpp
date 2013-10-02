#include <SDL2/SDL.h>

#include <stdio.h>

//The event structure
SDL_Event event;
char text[1024];
SDL_Surface *screen = NULL;
const int SCREEN_WIDTH = 640;
const int SCREEN_HEIGHT = 480;
const int SCREEN_BPP = 32;

#include <string>

std::string composition;
int cursor;
int selection_len = 0;

int main(int argc, char* argv[])
{
    SDL_Window* window;
    SDL_Renderer* renderer;

    // Initialize SDL.
	if(SDL_Init(SDL_INIT_EVERYTHING) < 0) {
		printf("%s\n", SDL_GetError());
        return 1;
    }

    // Create the window where we will draw.
    window = SDL_CreateWindow("SDL_RenderClear",
                    SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                    512, 512,
                    SDL_WINDOW_SHOWN);

    // We must call SDL_CreateRenderer in order for draw calls to affect this window.
    renderer = SDL_CreateRenderer(window, -1, 0);

    // Select the color for drawing. It is set to red here.
    SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);

    // Clear the entire screen to our selected color.
    SDL_RenderClear(renderer);

    // Up until now everything was drawn behind the scenes.
    // This will show the new, red contents of the window.
    SDL_RenderPresent(renderer);

	//SDL_StartTextInput();

	bool quit = false;	
    while (!quit)
    {
        if (SDL_PollEvent(&event))
        {
			//printf("%d\n", event.type);
            switch (event.type)
            {
               // case SDL_TEXTINPUT:
               //     /* Add new text onto the end of our text */
               //     strcat(text, event.text.text);
               //     break;
               // case SDL_TEXTEDITING:
               //     /*
               //     Update the composition text.
               //     Update the cursor position.
               //     Update the selection length (if any).
               //     */
               //     composition = event.edit.text;
               //     cursor = event.edit.start;
               //     selection_len = event.edit.length;
               //     break;
				case SDL_QUIT:
					quit = true;
					break;
			//case SDL_KEYDOWN:
			//	{
			//		SDLKey keyPressed = event.key.keysym.sym;
      		//
			//		switch (keyPressed)
			//			{
			//			case SDLK_ESCAPE:
			//				quit = true;
			//				break;
			//			}
			//		break;
			//	}
            }
        }
    }
	printf("quit!");
    // Give us time to see the window.

    // Always be sure to clean up
    SDL_Quit();
    return 0;
}
