#pragma once

class State
{
	public:
		virtual void Init() = 0;
		virtual void HandleInput() = 0;
		virtual void Update(float) = 0;
		virtual void Draw(float time) = 0;
		virtual void Pause() {};
		virtual void Resume() {};
};