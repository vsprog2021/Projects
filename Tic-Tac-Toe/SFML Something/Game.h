#pragma once
#include<memory>
#include<SFML\Graphics.hpp>
#include<string>
#include"StateM.h"
#include"Asset.h"
#include"Input.h"

struct Gamedata
{
	StateM machine;
	sf::RenderWindow window;
	Asset assets;
	Input input;
};

typedef std::shared_ptr<Gamedata>  GameDataRef;

class Game
{
	public:
		Game(int width, int height, std::string title);
	
	private:
		const float time = 1.0f / 60.0f;
		sf::Clock clock1;
		GameDataRef data1 = std::make_shared<Gamedata>();

		void Run();
};


