import json
from typing import List

from erniebot_agent.agents.functional_agent import FunctionalAgent
from erniebot_agent.agents.schema import AgentAction, AgentFile, AgentResponse
from erniebot_agent.messages import AIMessage, FunctionMessage, HumanMessage, Message
from erniebot_agent.prompt.prompt_template import PromptTemplate
from erniebot_agent.retrieval.baizhong_search import BaizhongSearch
from erniebot_agent.utils.logging import logger


def check_retrieval_intent(retrieval_results: str, query: str) -> str:
    # Be careful, slighly changes on prompt will influence final results at a large scale
    template = """{{retrieval_results}}，请判断上面的关键信息和"{{query}}"是否相关? \
        要求：按照下面的格式输出，如果相关，则回复：{"msg":true}，如果不相关，则回复：{"msg":false}。回复："""
    template_engine = PromptTemplate(template, input_variables=["retrieval_results", "query"])
    prompt = template_engine.format(retrieval_results=retrieval_results, query=query)
    return prompt


class FunctionalAgentWithRetrieval(FunctionalAgent):
    def __init__(self, knowledge_base: BaizhongSearch, top_k: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = knowledge_base
        self.top_k = top_k

    async def _async_run(self, prompt: str) -> AgentResponse:
        results = await self._maybe_retrieval(prompt)
        if results["msg"] is True:
            # RAG
            step_input = HumanMessage(
                content="背景：" + results["retrieval_results"] + "请根据上面的背景信息回答下面的问题：" + prompt
            )
            chat_history: List[Message] = []
            actions_taken: List[AgentAction] = []
            files_involved: List[AgentFile] = []

            chat_history.append(HumanMessage(content=prompt))

            fake_chat_history = chat_history.copy()
            fake_chat_history.append(step_input)
            llm_resp = await self._async_run_llm(
                messages=chat_history,
                functions=None,
                system=self.system_message.content if self.system_message is not None else None,
            )
            output_message = llm_resp.message
            chat_history.append(
                AIMessage(
                    content="",
                    function_call={
                        "name": "knowledge_retrieval_tool",
                        "thoughts": "这是一个检索的需求，我需要在knowledge_retrieval_tool知识库中检索出与输入的query相关的段落，并返回给用户。",
                        "arguments": '{"query": "%s"}' % prompt,
                    },
                )
            )

            # Knowledge Retrieval Tool
            action = AgentAction(
                tool_name="knowledge_retrieval_tool", tool_args='{"query": "OpenAI管理层变更会带来哪些影响？"}'
            )
            actions_taken.append(action)
            # return response
            next_step_input = FunctionMessage(name=action.tool_name, content=output_message.content)
            num_steps_taken = 0
            while num_steps_taken < self.max_steps:
                curr_step_output = await self._async_step(
                    next_step_input, chat_history, actions_taken, files_involved
                )
                if curr_step_output is None:
                    response = self._create_finished_response(chat_history, actions_taken, files_involved)
                    self.memory.add_message(chat_history[0])
                    self.memory.add_message(chat_history[-1])
                    return response
                num_steps_taken += 1
            response = self._create_stopped_response(chat_history, actions_taken, files_involved)
            return response
        else:
            # Functional Agent
            logger.info(f"Use functional agent to handle the query: {prompt}")
            return await super()._async_run(prompt)

    async def _maybe_retrieval(
        self,
        step_input,
    ):
        documents = self.knowledge_base.search(step_input, top_k=self.top_k, filters=None)
        retrieval_results = "\n".join(
            [f"第{index}个段落：{item['content_se']}" for index, item in enumerate(documents)]
        )
        messages = [HumanMessage(content=check_retrieval_intent(retrieval_results, step_input))]
        response = await self._async_run_llm(messages)
        message = response.message
        results = self._parse_results(message.content)
        return {"msg": results["msg"], "retrieval_results": retrieval_results}

    def _parse_results(self, results):
        left_index = results.find("{")
        right_index = results.rfind("}")
        if left_index == -1 or right_index == -1:
            return results
        try:
            return json.loads(results[left_index : right_index + 1])
        except Exception:
            return results
