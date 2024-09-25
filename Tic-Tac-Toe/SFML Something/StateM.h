#pragma once
#include "State.h"
#include <memory>
#include <stack>

typedef std::unique_ptr<State> StateRef;

class StateM
{
public:
	StateM() {};
	~StateM() {};

	void AddState(StateRef new_state, bool isReplacing = true);
	void RemoveState();
	void Change();

	StateRef& GetState();

private:
	std::stack<StateRef> states1;
	StateRef new_state1;
	bool isRemoving1;
	bool isAdding1;
	bool isReplacing1;
};
