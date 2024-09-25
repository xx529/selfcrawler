import time

from langchain_core.messages import HumanMessage

from selfcrawler.schema import Content, MessageToMarkdown


def save_html(msg, prefix):
    _msg = msg if isinstance(msg, list) else [msg]
    MessageToMarkdown(messages=_msg).to_html(
        f'/Users/lzx/Documents/GitHub/selfcrawler/reqdoc/prompt/{int(time.time())}_{prefix}.html')


def browser_prompt(
        task_desc: str,
        suggestion: str = '',
        have_done: str = '',
        to_do: str = '',
        html_content: str = '',
        screenshot: str = '',
        error_analysis: str = '',
) -> HumanMessage:
    prompt = f"""
# 这是你的总体任务：
{task_desc}

# 遵守以下规则：
1. 如果以下 html 没有内容，则需要先打开网页，如果已经有内容则直接进行下一步。
2. 创建 CSS 选择器时，确保它们是唯一且具体的，以便即使存在多个相同类型的元素（例如多个h1元素），也能仅选择一个元素。
3. 尽量选择带有 ID 的选择器来选择行元素，因为ID是唯一的。
4. 尽量使用 `:nth-child(n)` 来定位具体的第几个可能的相同元素
5. 避免单独使用通用标签如'h1'。相反，结合其他属性或结构关系来形成唯一的选择器。
6. CSS 选择器必须符合 playwright 的 page.locator 方法的要求。
7. 如果页面有相关问题的答案，请直接回答问题，不要进行其他操作。

# 以下是建议
{suggestion}

# 以下是完成情况的分析
* 已经完成：{have_done}
* 还需要完成：{to_do}

# 以下是可能执行错误的分析
{error_analysis}

# 以下是当前页面的HTML代码
```html
{html_content}
```
"""

    msg = HumanMessage(content=[
        Content.from_text(prompt),
        Content.from_text('# 以下是当前浏览器页面的截图'),
        Content.from_base64(screenshot)
    ])
    return msg


def critic_prompt(
        task_desc: str,
        last_screenshot: str,
        current_screenshot: str,
        action_error: str
) -> HumanMessage:
    msg = HumanMessage(content=[
        Content.from_text(
            "你需要根据以下任务描述和目标，针对执行前和已经执行后的情况进行评价，"
            "判断执行后的情况是否已经满足任务要求，并给出相关的理由。\n"),
        Content.from_text(f"任务内容：{task_desc}\n"),
        Content.from_text(f"执行前的页面截图：\n"),
        Content.from_base64(last_screenshot),
        Content.from_text(f"执行相关操作后的页面截图：\n"),
        Content.from_base64(current_screenshot),
        Content.from_text(f"执行过程中出现的错误：{action_error}\n")
    ])

    return msg
