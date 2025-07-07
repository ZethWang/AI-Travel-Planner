#!/usr/bin/env python
import os
import json
import sys
import logging
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

load_dotenv()

logging.basicConfig(
  level=logging.DEBUG,
  format='DEBUG: %(asctime)s - %(message)s',
  stream=sys.stderr
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Google Calendar MCP", dependencies=["python-dotenv", "google-api-python-client", "google-auth", "google-auth-oauthlib"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REFRESH_TOKEN:
  logger.error("错误：需要 GOOGLE_CLIENT_ID、GOOGLE_CLIENT_SECRET 和 GOOGLE_REFRESH_TOKEN 环境变量")
  sys.exit(1)

@mcp.tool()
async def create_event(
  summary: str, 
  start_time: str, 
  end_time: str, 
  description: str = None, 
  location: str = None, 
  attendees: list = None, 
  reminders: dict = None
) -> str:
  """创建具有指定详细信息的日历事件
  
  参数:
      summary: 事件标题
      start_time: 开始时间（ISO 格式）
      end_time: 结束时间（ISO 格式）
      description: 事件描述
      location: 事件位置
      attendees: 参与者邮箱列表
      reminders: 事件提醒设置
  
  返回:
      包含事件创建确认和链接的字符串
  """
  logger.debug(f'正在创建日历事件，参数: {locals()}')
  
  try:
    logger.debug('创建 OAuth2 客户端')
    # Google OAuth2 
    creds = Credentials(
      None, 
      refresh_token=GOOGLE_REFRESH_TOKEN,
      token_uri="https://oauth2.googleapis.com/token",
      client_id=GOOGLE_CLIENT_ID,
      client_secret=GOOGLE_CLIENT_SECRET
    )
    logger.debug('OAuth2 客户端已创建')
    
    logger.debug('创建日历服务')
    calendar_service = build('calendar', 'v3', credentials=creds)
    logger.debug('日历服务已创建')
    
    event = {
      'summary': summary,
      'start': {
        'dateTime': start_time,
        'timeZone': 'Asia/Shanghai'
      },
      'end': {
        'dateTime': end_time,
        'timeZone': 'Asia/Shanghai'
      }
    }
    
    if description:
      event['description'] = description
    
    if location:
      event['location'] = location
      logger.debug(f'位置已添加: {location}')
    
    if attendees:
      event['attendees'] = [{'email': email} for email in attendees]
      logger.debug(f'参与者已添加: {event["attendees"]}')
    
    if reminders:
      event['reminders'] = reminders
      logger.debug(f'自定义提醒已设置: {json.dumps(reminders)}')
    else:
      event['reminders'] = {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 10}
        ]
      }
      logger.debug(f'默认提醒已设置: {json.dumps(event["reminders"])}')
    
    logger.debug('尝试插入事件')
    response = calendar_service.events().insert(calendarId='primary', body=event).execute()
    logger.debug(f'事件插入响应: {json.dumps(response)}')
    
    return f"事件已创建: {response.get('htmlLink', '链接不可用')}"
    
  except Exception as error:
    logger.debug(f'发生错误:')
    logger.debug(f'错误类型: {type(error).__name__}')
    logger.debug(f'错误消息: {str(error)}')
    import traceback
    logger.debug(f'错误追踪: {traceback.format_exc()}')
    raise Exception(f"创建事件失败: {str(error)}")

def main():
  """运行 MCP 日历服务器。"""
  try:
    mcp.run()
  except KeyboardInterrupt:
    logger.info("服务器被用户停止")
  except Exception as e:
    logger.error(f"运行服务器时发生致命错误: {e}")
    sys.exit(1)

if __name__ == "__main__":
  main()