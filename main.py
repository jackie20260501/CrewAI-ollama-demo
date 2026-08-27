from src.crew import build_content_crew
from src.llm_config import get_local_llm, get_model_name
from src.monitoring import ResourceMonitor, instrument_llm
from src.validation import validate_final_output


def main() -> None:
    monitor = ResourceMonitor()

    print("启动 CrewAI + Ollama 本地 LLM Demo")
    print(f"模型: {get_model_name()}")
    print("流程: 研究员 -> 作家 -> 审稿人")
    print(f"初始资源: {monitor.snapshot()}")
    print("=" * 60)

    llm, llm_stats = instrument_llm(
        get_local_llm(),
        monitor,
        labels=["资深研究员", "内容作家", "专业审稿人"],
    )
    crew = build_content_crew(llm)
    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("最终结果")
    print("=" * 60)
    print(result)
    print("\n" + "=" * 60)
    print(validate_final_output(result))
    print("=" * 60)
    print(llm_stats.format_summary())
    print("=" * 60)
    print(f"结束资源: {monitor.snapshot()}")


if __name__ == "__main__":
    main()
