from crewai import Agent


def create_researcher(llm) -> Agent:
    return Agent(
        role="资深研究员",
        goal="寻找关于给定主题的准确事实，并总结关键趋势",
        backstory="你是一名经验丰富的技术研究员，擅长把复杂信息提炼成清晰要点。",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_writer(llm) -> Agent:
    return Agent(
        role="内容作家",
        goal="根据研究结果写出清晰、生动、适合普通读者阅读的短文",
        backstory="你是一名优秀的科技内容作者，擅长把研究材料转化为有吸引力的文章。",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_reviewer(llm) -> Agent:
    return Agent(
        role="专业审稿人",
        goal="检查文章的事实准确性、表达清晰度和结构完整性",
        backstory="你是一名严谨的编辑，擅长发现文章中的逻辑问题、表达问题和事实风险。",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

