#pragma once
#include <map>
#include <SFML\Graphics.hpp>

class Asset
{
public:
	Asset() {};
	~Asset() {};
	void LoadTexture(std::string name, std::string filename);
	sf::Texture& GetTexture(std::string name);

	void LoadFont(std::string name, std::string filename);
	sf::Font& GetFont(std::string name);

private:
	std::map<std::string, sf::Texture> texture1;
	std::map<std::string, sf::Font> font1;
};