"""
This module contains functions to interact with the AI model API.
"""

import os
import sys

from mistralai import (AssistantMessage, Mistral, SystemMessage, ToolMessage,
                       UserMessage)

from format import print_gradient


def ask_llm(usr_prompt: str) -> str:
    """
    Request AI to generate a commit message.
    """
    sys_prompt_path = '/home/maty/Tools/ai-git-push/conf/sys_prompt.md'
    if not os.path.isfile(sys_prompt_path):
        sys_prompt_path = '/Users/maty/Tools/ai-git-push/conf/sys_prompt.md'
        if not os.path.isfile(sys_prompt_path):
            print_gradient("❌ Error: 'sys_prompt.md' file not found.",
                           "red_magenta")
            sys.exit(1)
    with open(sys_prompt_path, 'r', encoding='utf-8') as f:
        sys_prompt = f.read()
    api_key = os.getenv('MISTRAL_API_KEY')
    client = Mistral(api_key)
    print_gradient("💭 AI generating commit message...", "cyan_blue")
    conversation: list[AssistantMessage | SystemMessage | ToolMessage |
                       UserMessage] = [
        SystemMessage(content=sys_prompt),
        UserMessage(content=usr_prompt)
    ]
    response = client.chat.complete(
        model=os.getenv('MISTRAL_MODEL'),
        messages=conversation,
    )
    if not response or not response.choices:
        print_gradient("❌ Error: AI failed to generate commit message",
                       "red_magenta")
        sys.exit(1)
    response_msg = response.choices[0].message.content
    if isinstance(response_msg, str):
        return response_msg
    else:
        print_gradient(
            "❌ Error: AI response is not a valid string", "red_magenta")
        sys.exit(1)
