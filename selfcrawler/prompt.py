import time

from langchain_core.messages import HumanMessage

from selfcrawler.schema import Content, MessageToMarkdown


def save_prompt_completion(msg, prefix):
    _msg = msg if isinstance(msg, list) else [msg]
    MessageToMarkdown(messages=_msg).to_markdown(
        f'/Users/lzx/Documents/GitHub/selfcrawler/reqdoc/prompt/{int(time.time())}_{prefix}.md'
    )


def browser_prompt(
        task_desc: str,
        suggestion: str = '',
        done: str = '',
        todo: str = '',
        html_content: str = '',
        screenshot: str = '',
        code_error_analysis: str = '',
) -> HumanMessage:
    prompt = f"""
**这是你的总体任务**

{task_desc}


**遵守以下规则**
1. 如果以下 html 没有内容，则需要先打开网页，如果已经有内容则直接进行下一步。
2. 创建 CSS 选择器时，确保它们是唯一且具体的，以便即使存在多个相同类型的元素（例如多个h1元素），也能仅选择一个元素。
3. 避免单独使用像'h1'这样的通用标签。相反，结合其他属性或结构关系来形成唯一的选择器。
4. 尽量选择带有 ID 的选择器来选择行元素，因为ID是唯一的。
5. 尽量使用 `:nth-child(n)` 来定位具体的第几个可能的相同元素
6. CSS 选择器必须符合 playwright 的 page.locator 方法的要求。
7. 进行点击操作时候会触发页面的加载，所以点击元素后需要等待若干时间。


**以下是建议**

{suggestion}


**以下是完成情况的分析**
* 已经完成：{done}
* 还需要完成：{todo}

**以下是可能执行错误的分析**

{code_error_analysis}


**以下是当前页面的HTML代码**
```html
{html_content}
```
"""

    msg = HumanMessage(content=[
        Content.from_text(prompt),
        Content.from_text('**以下是当前浏览器页面的截图**'),
        Content.from_base64(screenshot) if screenshot else Content.from_text('无截图')
    ])
    return msg


def critic_prompt(
        task_desc: str,
        last_screenshot: str,
        current_screenshot: str,
        action_response: str,
        code_error: str
) -> HumanMessage:
    msg = HumanMessage(content=[
        Content.from_text(
            "你需要根据以下任务描述和目标，针对执行前和已经执行后的情况进行评价，"
            "判断执行后的情况是否已经满足任务要求，并给出相关的理由。\n\n"),
        Content.from_text(f"**任务内容**\n\n{task_desc}\n\n"),
        Content.from_text(f"**执行前的页面截图**\n\n"),
        Content.from_base64(last_screenshot) if last_screenshot else Content.from_text('无截图\n\n'),
        Content.from_text(f"**执行相关操作后的页面截图**\n\n"),
        Content.from_text(action_response + '\n\n'),
        Content.from_base64(current_screenshot) if current_screenshot else Content.from_text('无截图\n\n'),
        Content.from_text(f"**执行过程中出现的错误**{code_error}\n\n")
    ])

    return msg
