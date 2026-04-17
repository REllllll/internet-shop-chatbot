# Internet Shop Chatbot

# Graduation Thesis: The Interim Report

## Zhipeng Wang

## Student ID: 50087526

## Program: BMIS

```
u10zw22@abdn.ac.uk
```
```
Aberdeen-SCNU Joint Institute of Data Science and AI,
University of Aberdeen, Aberdeen AB24 3UE, UK
```
# Introduction

With the rapid development of e-commerce and the widespread adoption of mobile inter-
net, the sheer volume of product information has made ”information overload” a major
bottleneck hindering users’ efficient decision-making. To address this issue, personal-
ized recommendation systems based on collaborative filtering and deep learning have
been widely applied to mainstream e-commerce platforms such as Taobao and Amazon,
becoming the core engine for improving click-through rate (CTR) and conversion rate
(CVR).[1]
In recent years, with breakthroughs in Natural Language Processing (NLP) technol-
ogy, particularly Large Language Models (LLMs), recommendation systems are undergo-
ing a paradigm shift from ”static display” to ”dynamic interaction.” Major e-commerce
platforms have launched conversational AI-powered shopping guides, attempting to accu-
rately capture user intent and provide suggestions through multi-turn natural language
dialogues.[2]
While prior research has explored AI-based recommendation systems and conversa-
tional agents, several gaps remain:

- Traditional recommendation algorithms, such as collaborative filtering, typically
    rely on offline model building using static historical data snapshots. However, as
    Chandramouli et al. pointed out, this offline mechanism has significant limitations
    when dealing with update-intensive scenarios because it cannot capture the rapid
    release of new products or dynamic changes in user preferences in real time. Song
    et al. (2016) also support this view, arguing that assuming user preferences are
    static is particularly unrealistic in shopping scenarios where interests are constantly
    changing. They demonstrate that models built based on static snapshots experience
    significant performance degradation as content relevance changes. In domains with
    extremely high real-time requirements, such as e-commerce, systems must be able
    to discard outdated data and immediately integrate new events to keep recommen-
    dation results ”fresh”.[3][4]


- As Mo et al. (2025) described in their review of conversational search, users’ initial
    information needs are often vague. Traditional search engines, as a “single search”
    paradigm, often fail to maintain the interactive context, resulting in limited un-
    derstanding of complex needs.Sun and Zhang (2018) also pointed out that existing
    e-commerce search systems mostly adopt a single-round ad-hoc search model, lack-
    ing a dynamic clarification mechanism similar to that of human shopping guides to
    help users refine their needs.[5][6]
- Zhang and Chen (2020) pointed out that although deep learning and latent factor
    models have significantly improved the accuracy of recommender systems, their in-
    herent ”black-box” nature often leads to a lack of transparency, making it difficult
    for users to intuitively understand why specific items are recommended. To alle-
    viate this problem, introducing explanation mechanisms is particularly important.
    Research shows that providing the logical reasons behind recommendations can
    effectively respond to users’ need for justification in decision-making, thereby signif-
    icantly improving the system’s transparency, trustworthiness, and persuasiveness.[7]
- While Large Language Models (LLMs) exhibit remarkable reasoning capabilities,
    their reliance on static training data renders them virtually isolated when faced
    with dynamic real-world scenarios. To overcome this limitation and enable interac-
    tion between LLMs and real-world data, current engineering practices often rely on
    customized API integration. However, Singh et al. point out that this fragmented
    integration approach leads to high system complexity, poor scalability, and a lack
    of unified security standards. Similarly, Hou et al. pointed out that traditional tool
    integration methods are usually based on manual API docking or platform-specific
    plugins, leading to fragmented development and poor system scalability. Through
    a systematic analysis of the Model Context Protocol (MCP), they emphasized the
    importance of establishing a unified communication standard for breaking down
    barriers between models and external data (such as databases and web services),
    and pointed out that existing research still has gaps in the security and lifecycle
    management of standardized protocols.[8][9]
- Traditional e-commerce systems often present users with unstructured product lists,
    a ”single-shot retrieval” model that struggles with complex decision-making. Ac-
    cording to McGinty and Smyth (2002), the user’s decision-making process is essen-
    tially a ”navigation by proposing” process. Compared to forcing users to process nu-
    merous parameters or manually filter lists, comparison-based interaction—allowing
    users to choose between specific options (A and B)—significantly reduces cognitive
    costs. This research demonstrates that by utilizing preference-based feedback, sys-
    tems can more accurately capture users’ implicit needs, thus outperforming simple
    ”similar product recommendation” strategies.[10]

These insights motivate the need for a fully integrated, explainable, multi-turn con-
versational recommender.


# Goals

Goal 1: Design and Implementation of a Conversational Recommendation
System
The primary goal of this project is to design and implement a fully functional conver-
sational recommendation system that integrates large language model (LLM) reasoning
with real-time product data retrieval and workflow automation. Through multi-turn di-
alogue, the system incrementally elicits user preferences by asking concise and targeted
questions, and subsequently retrieves relevant items from a live product database to gen-
erate informed recommendations.
Goal 2: Privacy-Preserving User Data Handling
A key objective of the system is to ensure strong user data privacy protection through-
out the recommendation process. The system adopts strict data minimization prin-
ciples, avoids storing unnecessary personal information, and incorporates architectural
safeguards to prevent unauthorized access. User preference data is processed only to
the extent required for recommendation generation, ensuring compliance with privacy-
by-design principles.
Goal 3: Explainable and Personalized Recommendations
Under the premise of privacy protection, the system aims to deliver personalized
and explainable product recommendations. Each recommendation is accompanied by
clear, evidence-based explanations that justify why specific products match user prefer-
ences. This includes trade-off analysis, feature-level reasoning, and horizontal compar-
isons among similar products, thereby improving user trust, transparency, and decision
confidence.

# 1 Methodology

An agile and iterative software development methodology will be followed for this project,
in order to develop the conversational recommendation system and its underlying retrieval
and workflow components. The main activities to be undertaken are outlined below:

- Learning relevant technologies such as the Model Context Protocol (MCP), n8n
    workflow automation, and integrating LLM tools through structured prompting
    and schema-constrained outputs.
- Exploring product data sources and understanding the structure, access methods,
    and constraints of external APIs or databases.
- Creating the requirements specification document, defining both functional and non-
    functional requirements including transparency and privacy protection.
- Designing the overall system architecture, including the conversational layer, re-
    trieval pipeline, ranking module, and workflow interactions.
- Implementing prototypes for individual components (preference elicitation, MCP
    retrieval, recommendation logic) to validate early design assumptions.


- Integrating system components and developing full functionality to meet the require-
    ments specification, including comparison generation and recommendation expla-
    nation.
- Evaluating the system through testing and debugging of workflows, retrieval accu-
    racy, and structured LLM outputs.
- Refining prompts, schemas, and pipeline logic through iterative experimentation
    and error analysis.
- Writing documentation including the interim report, final project report, system
    description, and maintenance notes.
- Implementing additional features or enhancements such as improved transparency
    explanations or UI refinements, where time permits.

# Resources Required

The successful completion of this project requires a combination of hardware and software
resources to support system development, experimentation, and evaluation. The key
resources and their purposes are outlined below:

- Hardware: A personal computer with a stable internet connection is required
    for software development, testing, and experimentation. The system will be used
    to implement and run the conversational recommendation pipeline, execute local
    prototypes, and access cloud-based APIs for large language models and real-time
    product data.
- Programming Environment: Python is used as the primary backend devel-
    opment language for implementing preference elicitation logic, product retrieval
    through the Model Context Protocol (MCP), and recommendation workflows. It
    also supports rapid prototyping and integration with external APIs.
- Workflow Automation Platform: n8n is employed to orchestrate the recom-
    mendation pipeline, including product data retrieval, error handling, logging, and
    workflow reproducibility. It enables modular design and facilitates the integration
    of multiple system components.
- Frontend and Prototyping Tools: ReactJS is used to develop a lightweight
    user interface for the conversational system, enabling user interaction and visual
    presentation of recommendations and product comparisons. Figma is utilised to
    design and iterate on interface prototypes before implementation, ensuring clarity
    and usability of the user experience.
- Development and Version Control Tools: Standard development tools, in-
    cluding code editors and version control systems such as Git, are required to man-
    age source code, track changes, and support iterative development throughout the
    project.


# 2 Risk Assessment

Several risks may affect the progress or quality of the project. The main risks, along with
mitigation strategies and estimated severity levels, are outlined below:

- Unstable or inconsistent LLM outputs The large language model may generate
    responses that do not follow the required structure or schema. Mitigation: enforce
    strict JSON schemas, implement automated output validation and repair routines,
    and apply prompt engineering techniques. Level: Medium
- Unavailability or inconsistency of product data sources External APIs or
    databases accessed via MCP may occasionally fail or return incomplete results.
    Mitigation: implement fallback sources, introduce caching mechanisms, and add
    error-handling workflows in n8n. Level: Medium
- Workflow execution failures in n8n Workflow nodes may fail due to config-
    uration errors, network issues, or unexpected data formats. Mitigation: modular
    workflow design, logging and retry strategies, early integration testing, and node-
    level validation. Level: Low
- Delays due to technical complexity or integration challenges Connecting
    LLMs, MCP tools, and workflow automation may require more time than antic-
    ipated. Mitigation: follow an incremental integration approach, maintain weekly
    milestones, and prioritise core functionality before enhancements. Level: Medium
- Privacy or security risks when handling user preference data Even minimal
    user inputs (preferences, constraints, queries) may present confidentiality concerns.
    Mitigation: apply privacy-by-design principles, minimise data retention, avoid stor-
    ing unnecessary personal information, and ensure secure communication channels.
    Level: Medium
- Hardware or software failure resulting in data loss Local development en-
    vironments may experience system crashes or corrupted project files. Mitigation:
    perform regular backups, use version control (Git), and store project assets in re-
    dundant secure locations. Level: Low


# Timetable

```
2025 2026
```
```
December January February March April
```
```
W1W2 W3 W4 W5 W6 W7 W8 W9W10W11W12W13W14W15W16W17W18W
```
Requirements Specification
System Architecture
& Workflow Design
Preference Elicitation Module

```
MCP Retrieval Prototype
Recommendation En-
gine Development
Comparison Module &
Explanation Refinement
System Integration
Debugging & Pri-
vacy Validation
Testing & Evaluation Phase
Final Report Prepa-
ration & Submission
```
```
Final Submission
```
```
Figure 1: Project timetable and major development activities (Updated).
```
# References

```
[1] Qi Zhao, Yi Zhang, Daniel Friedman, and Fangfang Tan. E-commerce recommen-
dation with personalized promotion. In Proceedings of the 9th ACM Conference on
Recommender Systems, pages 219–226, 2015.
```
```
[2] Zihuai Zhao, Wenqi Fan, Jiatong Li, Yunqing Liu, Xiaowei Mei, Yiqi Wang, Zhen
Wen, Fei Wang, Xiangyu Zhao, Jiliang Tang, et al. Recommender systems in the
era of large language models (llms). IEEE Transactions on Knowledge and Data
Engineering, 36(11):6889–6907, 2024.
```
```
[3] Badrish Chandramouli, Justin J Levandoski, Ahmed Eldawy, and Mohamed F Mok-
bel. Streamrec: a real-time recommender system. In Proceedings of the 2011 ACM
SIGMOD International Conference on Management of data, pages 1243–1246, 2011.
```
```
[4] Yang Song, Ali Mamdouh Elkahky, and Xiaodong He. Multi-rate deep learning for
temporal recommendation. In Proceedings of the 39th International ACM SIGIR
```

```
conference on Research and Development in Information Retrieval, pages 909–912,
2016.
```
```
[5] Fengran Mo, Kelong Mao, Ziliang Zhao, Hongjin Qian, Haonan Chen, Yiruo Cheng,
Xiaoxi Li, Yutao Zhu, Zhicheng Dou, and Jian-Yun Nie. A survey of conversational
search. ACM Transactions on Information Systems, 43(6):1–50, 2025.
```
```
[6] Yueming Sun and Yi Zhang. Conversational recommender system. In The 41st in-
ternational acm sigir conference on research & development in information retrieval,
pages 235–244, 2018.
```
```
[7] Yongfeng Zhang, Xu Chen, et al. Explainable recommendation: A survey and new
perspectives. Foundations and Trends® in Information Retrieval, 14(1):1–101, 2020.
```
```
[8] Aditi Singh, Abul Ehtesham, Saket Kumar, and Tala Talaei Khoei. A survey of
the model context protocol (mcp): Standardizing context to enhance large language
models (llms). 2025.
```
```
[9] Xinyi Hou, Yanjie Zhao, Shenao Wang, and Haoyu Wang. Model context protocol
(mcp): Landscape, security threats, and future research directions. arXiv preprint
arXiv:2503.23278, 2025.
```
[10] Lorraine Mc Ginty and Barry Smyth. Comparison-based recommendation. In Euro-
pean conference on case-based reasoning, pages 575–589. Springer, 2002.


