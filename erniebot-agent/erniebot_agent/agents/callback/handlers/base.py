# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import List, Union

from erniebot_agent.agents import Agent
from erniebot_agent.agents.agent_step import AgentStep
from erniebot_agent.agents.llms import LLM
from erniebot_agent.messages import Message
from erniebot_agent.tools import Tool


class CallbackHandler(AgentCallbackHandlerMixin, LLMCallbackHandlerMixin,
                      ToolCallbackHandlerMixin):
    """"""

    async def on_agent_start(self, agent: Agent, prompt: str) -> None:
        """"""

    async def on_llm_start(self,
                           agent: Agent,
                           llm: LLM,
                           messages: List[Message]) -> None:
        """"""

    async def on_llm_end(self, agent: Agent, llm: LLM,
                         response: Message) -> None:
        """"""

    async def on_llm_error(self,
                           agent: Agent,
                           llm: LLM,
                           error: Union[Exception, KeyboardInterrupt]) -> None:
        """"""

    async def on_tool_start(self, agent: Agent, tool: Tool,
                            input_args: str) -> None:
        """"""

    async def on_tool_end(self, agent: Agent, tool: Tool,
                          response: str) -> None:
        """"""

    async def on_tool_error(self,
                            agent: Agent,
                            tool: Tool,
                            error: Union[Exception, KeyboardInterrupt]) -> None:
        """"""

    async def on_agent_end(self, agent: Agent, response: str) -> None:
        """"""
