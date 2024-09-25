#include "Asset.h"

void Asset::LoadTexture(std::string name, std::string filename)
{
	sf::Texture tex;
	if (tex.loadFromFile(filename))
	{
		this->texture1[name] = tex;
	}
}

sf::Texture& Asset::GetTexture(std::string name)
{
	return this->texture1.at(name);
}

void Asset::LoadFont(std::string name, std::string filename)
{
	sf::Font font;
	if (font.loadFromFile(filename))
	{
		this->font1[name] = font;
	}
}

sf::Font& Asset::GetFont(std::string name)
{
	return this->font1.at(name);
}
