import base64
from pathlib import Path
from typing import List, Literal
import markdown

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


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

    def to_html(self, path: str) -> str:
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

            md.append(string)

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
