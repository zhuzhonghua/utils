#include <iostream>
#include <SDL2/SDL.h>

int main(int argc, char **argv){
    if (SDL_Init(SDL_INIT_EVERYTHING) != 0){
        std::cout << "SDL Error: " << SDL_GetError() << std::endl;
        return 1;
    }
	SDL_Window* pWindow = SDL_CreateWindow("Hello World", 100, 100, 640, 480, SDL_WINDOW_SHOWN);
	if (!pWindow){
		std::cout << "SDL Error: " << SDL_GetError() << std::endl;
        return 1;
	}

	SDL_Renderer* pRender = SDL_CreateRenderer(pWindow, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
	if (!pRender){
		std::cout << "SDL Error: " << SDL_GetError() << std::endl;
        return 1;
	}

	SDL_Surface* bmp = SDL_LoadBMP("hello.bmp");
	if (!bmp){
		std::cout << "SDL Error: " << SDL_GetError() << std::endl;
        return 1;
	}

	SDL_Texture* pTex = SDL_CreateTextureFromSurface(pRender, bmp);
	SDL_FreeSurface(bmp);

	SDL_RenderClear(pRender);
	SDL_RenderCopy(pRender, pTex, NULL, NULL);
	SDL_RenderPresent(pRender);

	SDL_Delay(2000);

	SDL_DestroyTexture(pTex);
	SDL_DestroyRenderer(pRender);
	SDL_DestroyWindow(pWindow);
	
    SDL_Quit();

    return 0;
}
