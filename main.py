from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from selfcrawler.schema import ImageContent, ImageUrl, TextContent, Pos

load_dotenv()


model = ChatOpenAI(model="gpt-4o").with_structured_output(Pos)

message = HumanMessage(
    content=[
        TextContent(text="需要点击达人列表按钮，给出点击的坐标位置").model_dump(),
        ImageContent(image_url=ImageUrl(
            url="https://agent-circle-pub-test-1257687450.cos.ap-beijing.myqcloud.com/3f4279ba-35b6-4e6e-a00e-437ddf1621e1.png")).model_dump()
    ]
)
print(message)


result = model.invoke([message])
print(result)
