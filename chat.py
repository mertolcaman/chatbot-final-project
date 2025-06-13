from agent.test_agent import test_agent
from agent.product_agent import product_agent
import uuid


session_id = str(uuid.uuid4()) #for dynamic session id
# mode = input("Choose mode (chat/debug): ").strip().lower()  #optional: mode to choose 

mode= "chat"


# while True:
    


#     if mode not in ["chat", "debug"]:
#         print("Invalid mode selected. Defaulting to debug.")
#         mode = "debug"

#     user_query = input("Ask something: ")
#     if user_query in ["exit", "quit"]:
#         break

#     if mode == "chat":
        
#         print(f"Session ID: {session_id}")



#         response = product_agent.invoke(
#             {"input": user_query},
#             config={"configurable": {"session_id": session_id}}
#         )
#     else:
#         response = test_agent.run(user_query)

#     print("💬", response)