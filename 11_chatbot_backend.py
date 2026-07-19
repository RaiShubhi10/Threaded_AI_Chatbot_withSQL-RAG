from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI()

def chat_node(state: ChatState):
    #take user query from state
    messages = state['messages']
    #send to llm
    response = llm.invoke(messages)
    #response store state
    return {'messages': [response]}

checkpointer = MemorySaver()
graph = StateGraph('chat_node',chat_node)

#add nodes
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot = graph.compile(checkpointer=checkpointer)

for message_chunk, metadata in chatbot.stream(
    {'messages':[HumanMessage(content='What is the recipe to make pasta')]},
    config = {'configurable':{'thread_id':'thread-1'}},
    stream_mode='messages'
):
    if message_chunk.content:
        print(message_chunk.content, end=" ",flush=True)
