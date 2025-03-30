import litellm
import os

litellm.drop_params = True
if os.environ.get("ENABLE_OTEL", "false").lower() == "true":
    litellm.callbacks = ["otel"]

QUESTIONING_MODEL = os.environ["QUESTIONING_MODEL"]
SPEC_MODEL: str = os.environ["SPEC_MODEL"]

QUESTIONING_END_TOKEN = "<NO_MORE_QUESTIONS>"
SYSTEM_PROMPT = f"""
You are a helpful assistant that the user can use to develop a detailed
specification for an idea.

Ask the user one question at a time to develop a thorough, step-by-step spec for
this idea. Each question should build on the previous answers, and the end goal
is to have a detailed specification that can be handed off to a developer.

Let's do this iteratively and dig into every relevant detail. Clarify everything
from features to technologies to architecture.

Remember, only one question at a time.

After I have answered all the questions you need, respond with
"{QUESTIONING_END_TOKEN}".
"""

IDEA_PROMPT = """
Here's the idea:

{idea}
"""

SPEC_PROMPT = """
Now that we've wrapped up the brainstorming process, can you compile our
findings into a comprehensive, developer-ready specification? Include all
relevant requirements, architecture choices, data handling details, error
handling strategies, and a testing plan so a developer can immediately begin
implementation.
"""

idea = input("Idea: ")
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": IDEA_PROMPT.format(idea=idea)},
]

response = litellm.completion(
    model=QUESTIONING_MODEL,
    messages=messages,
)
new_message = response.choices[0].message
messages.append({"role": "assistant", "content": new_message.content})

while True:
    if new_message.reasoning_content:
        print(f"Reasoning: {new_message.reasoning_content}")

    print(f"Question: {new_message.content}")
    answer = input("Answer: ")
    messages.append({"role": "user", "content": answer})
    response = litellm.completion(
        model=QUESTIONING_MODEL,
        messages=messages,
    )
    new_message = response.choices[0].message
    messages.append({"role": "assistant", "content": new_message.content})

    if new_message.content.upper().find("<NO_MORE_QUESTIONS>") != -1:
        break

messages.append({"role": "user", "content": SPEC_PROMPT})

response = litellm.completion(
    model=SPEC_MODEL,
    messages=messages,
)

new_message = response.choices[0].message
messages.append({"role": "assistant", "content": new_message.content})

print("Specification:")
print(new_message.content)
