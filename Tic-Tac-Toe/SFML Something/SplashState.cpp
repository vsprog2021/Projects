#include "SplashState.h"
#include <string>
#include <iostream>
#include "Definitions.h"

SplashState::SplashState(GameDataRef data) : data1(data) {}

void SplashState::Init()
{
	this->data1->assets.LoadTexture("Splash State Background", SPLASH_SCENE_BACKGROUND_FILEPATH);
	background1.setTexture(this->data1->assets.GetTexture("Splash State Background"));

}

void SplashState::HandleInput()
{
	sf::Event event;
	while (this->data1->window.pollEvent(event))
	{
		if (sf::Event::Closed == event.type)
			this->data1->window.close();
	}
}
void SplashState::Update(float time)
{
	if (this->clock1.getElapsedTime().asSeconds() > SPLASH_STATE_SHOW_TIME)
		std::cout << "GO TO MAIN MENU" << std::endl;
}

void SplashState::Draw(float time)
{
	this->data1->window.clear(sf::Color::Red);
	this->data1->window.draw(this->background1); 
	this->data1->window.display();
}
