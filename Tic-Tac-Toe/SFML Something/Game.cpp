#include "Game.h"
#include "SplashState.h"
#include <memory>
#include <SFML\Graphics.hpp>

Game::Game(int width, int height, std::string title)
{
	data1->window.create(sf::VideoMode(width, height), "LOL");
	//data1->window.create(sf::VideoMode(width, height),"LOL");
	data1->machine.AddState(StateRef(new SplashState (this->data1)));

	this->Run();
}

void Game::Run()
{
	float newTime, frameTime, interpolation;
	float curentTime = this->clock1.getElapsedTime().asSeconds();
	float accumulator = 0.0f;
	while (this->data1->window.isOpen())
	{
		this->data1->machine.Change();
		newTime = this->clock1.getElapsedTime().asSeconds();
		frameTime = newTime - curentTime;
		if (frameTime > 0.25f)
			frameTime = 0.25f;
		curentTime = newTime;
		accumulator += frameTime;
		while (accumulator >= time)
		{
			this->data1->machine.GetState()->HandleInput();
			this->data1->machine.GetState()->Update(time);
			accumulator -= time;
		}
		interpolation = accumulator / time;
		this->data1->machine.GetState()->Draw(interpolation);
	}
}