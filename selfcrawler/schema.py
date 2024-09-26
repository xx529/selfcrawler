import base64
from pathlib import Path
from typing import List, Literal

import markdown
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from selfcrawler.utils import Browser


class Navigate(BaseModel):
    """
    根据当前对话信息，判断下一步需要执行的操作
    """
    question: str = Field('', description="需要询问用户问题来获取当前缺失的信息")
    action: str = Field('', description="需要执行的网页操作的描述")
    is_task_finish: bool = Field(False, description="是否完成已经完成任务")


class ActionFeedBack(BaseModel):
    """
    根据当前任务已经执行完成的情况给出评价，给出是否已经完成任务，已经完成和还需要的操作，以及相关的理由
    """
    analysis: str = Field(description="分析当前的任务情况")
    is_action_finish: bool = Field(description="是否完成任务")
    done: str = Field(description="已经完成的内容")
    todo: str = Field(description="任务未完成情况下，给出具体还需要操作的内容，例如点击某个按钮，输入某个内容")
    suggestion: str = Field(description="任务未完成情况下，给出的下一步操作，或者改进的建议")
    code_error_analysis: str = Field('', description="如果出现代码错误，针对错误代码进行分析")


class GraphState(TypedDict):
    messages: list
    browser: Browser

    # action_response: dict
    # question: str
    # question_response: dict

    # navigator
    action: str
    task_finish: bool

    # browser
    last_screenshot: str
    code_error: list
    action_response: str

    # critic
    suggestion: str
    done: str
    todo: str
    code_error_analysis: str
    is_action_finish: bool


class ImageUrl(BaseModel):
    url: str = Field(..., description="图片链接")

    @classmethod
    def from_local_img(cls, img_path: str) -> 'ImageUrl':
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            return cls(url=f"data:image/png;base64,{base64_image}")

    @classmethod
    def from_base64(cls, base64_img: str) -> 'ImageUrl':
        return cls(url=f"data:image/png;base64,{base64_img}")

    @classmethod
    def from_url(cls, url: str) -> 'ImageUrl':
        return cls(url=url)


class ImageContent(BaseModel):
    type: Literal["image_url"] = Field('image_url', description="消息类型")
    image_url: ImageUrl = Field(..., description="图片链接")


class TextContent(BaseModel):
    type: Literal["text"] = Field('text', description="消息类型")
    text: str = Field('', description="文本消息内容")


class Content:

    @staticmethod
    def from_text(text: str) -> dict:
        return TextContent(text=text).model_dump()

    @staticmethod
    def from_image(image_path: str) -> dict:
        return ImageContent(image_url=ImageUrl.from_local_img(img_path=image_path)).model_dump()

    @staticmethod
    def from_base64(base64_img: str) -> dict:
        return ImageContent(image_url=ImageUrl.from_base64(base64_img=base64_img)).model_dump()


class ActionResponse(BaseModel):
    content: str = Field(..., description="操作内容")
    base64_img: str | None = Field(None, description="图片 base64 编码")
    reply: str = Field('', description="回复内容")


class MessageToMarkdown(BaseModel):
    messages: List[BaseMessage] = Field(..., description="消息列表")

    def to_markdown(self, path: str):
        md = []
        for message in self.messages:
            string = f'## {message.type.upper()}\n'

            if isinstance(message.content, str):
                string += message.content

            elif isinstance(message.content, list):
                for i in message.content:
                    if i['type'] == 'text':
                        string += i['text']
                    elif i['type'] == 'image_url':
                        string += f'\n\n![img]({i["image_url"]["url"]})\n\n'

            string += '\n---\n'

            md.append(string)
        ...
        m = '\n'.join(md)

        if (p := Path(path)).exists():
            p.unlink()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(m)

    def to_html(self, path: str):
        md = []
        for message in self.messages:
            string = f'## {message.type.upper()}\n'

            if isinstance(message.content, str):
                string += message.content

            elif isinstance(message.content, list):
                for i in message.content:
                    if i['type'] == 'text':
                        string += i['text']
                    elif i['type'] == 'image_url':
                        string += f'\n\n![img]({i["image_url"]["url"]})\n\n'

            string += '\n---\n'

            md.append(string)
        ...
        m = '\n'.join(md)
        html_with_meta = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
        <meta charset="UTF-8">
        <title>Markdown 转 HTML</title>
        </head>
        <body>
        {markdown.markdown(m)}
        </body>
        </html>
        """

        if (p := Path(path)).exists():
            p.unlink()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_with_meta)
