from typing import Literal

from pydantic import BaseModel, Field


class ImageUrl(BaseModel):
    url: str = Field(..., description="图片链接")


class ImageContent(BaseModel):
    type: Literal["image_url"] = Field('image_url', description="消息类型")
    image_url: ImageUrl = Field(..., description="图片链接")


class TextContent(BaseModel):
    type: Literal["text"] = Field('text', description="消息类型")
    text: str = Field('', description="文本消息内容")


class Pos(BaseModel):
    x: int = Field(..., description="x坐标")
    y: int = Field(..., description="y坐标")
