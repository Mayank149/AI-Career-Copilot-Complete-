from graphs.career_graph import career_agent


config = {
    "configurable": {
        "thread_id": "test_user_1"
    }
}


# First message
result = career_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "I want to become an AI Engineer. What skills am I missing?"
            }
        ]
    },
    config=config
)

print("Assistant:", result["messages"][-1].content)


# Follow-up message
result = career_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Which of those should I learn first?"
            }
        ]
    },
    config=config
)

print("\nAssistant:", result["messages"][-1].content)