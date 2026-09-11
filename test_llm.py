from models.llm import LLMClient


def main():

    llm = LLMClient()

    result = llm.generate(
        system_prompt="你是一个测试助手。",
        user_prompt="请只回答：测试成功"
    )

    print("\n模型返回：")
    print(result)


if __name__ == "__main__":
    main()