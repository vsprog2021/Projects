#include "StateM.h"

void StateM::AddState( StateRef new_state, bool isReplacing)
{
	this->isAdding1 = true;
	this->isReplacing1 = isReplacing;
	this->new_state1 = std::move(new_state);
}

void StateM::RemoveState()
{
	this->isRemoving1 = true;
}

void StateM::Change()
{
	if (isRemoving1 == true && !this->states1.empty())
	{
		this->states1.pop();
		if (!this->states1.empty())
			this->states1.top()->Resume();
		this->isRemoving1 = false;
	}
	if (this->isAdding1)
	{
		if (!this->states1.empty())
		{
			if (this->isReplacing1)
			{
				this->states1.pop();
			}
			else
				this->states1.top()->Pause();
		}
		this->states1.push(std::move(this->new_state1));
		this->states1.top()->Init();
		this->isAdding1 = false;
	}
}

StateRef& StateM::GetState()
{
	return this->states1.top();
}
