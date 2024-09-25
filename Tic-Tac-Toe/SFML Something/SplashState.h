#pragma once
#include<SFML\Graphics.hpp>
#include"State.h"
#include"Game.h"

class SplashState: public State
{
private:
	GameDataRef data1;
	sf::Clock clock1;
	sf::Sprite background1;

public:
	SplashState(GameDataRef data);
	void Init();
	void HandleInput() ;
	void Update(float time);
	void Draw(float time);
};

