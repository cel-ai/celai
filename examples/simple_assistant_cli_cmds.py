from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.request_context import RequestContext
from cel.connectors.telegram.telegram_connector import TelegramConnector


def register_client_commands(ast: BaseAssistant):

    @ast.client_command("ping")
    async def handle_reset(session, ctx: RequestContext, command: str, args: list[str]):
        log.critical(f"Got reset command")
        await ctx.connector.send_text_message(ctx.lead, "Pong!")
      
      
    @ast.client_command("demo")
    async def handle_demo(session, ctx: RequestContext, command: str, args: list[str]):
        log.critical(f"Got demo command")
        
        demo = args[0] if len(args) > 0 else None
        if demo == "link":
            links = [
                {"text": "Go to Google", "url": "https://www.google.com"},
                {"text": "Go to Facebook", "url": "https://www.facebook.com"}
            ]
            if ctx.connector.name() == "telegram":
                assert isinstance(ctx.connector, TelegramConnector), "Connector must be an instance of TelegramConnector"
                await ctx.connector.send_link_message(ctx.lead, text="Please follow this link", links=links)
            return RequestContext.cancel_response()
        
        
        if demo == "select":
            conn = ctx.connector
            num = int(args[1] if len(args) > 1 else 3)
            options = [f"Option {i}" for i in range(1, num+1)]
            if conn.name() == "telegram":
                assert isinstance(conn, TelegramConnector), "Connector must be an instance of TelegramConnector"
                await conn.send_select_message(ctx.lead, "Select an option", options=options)

            return RequestContext.response_text("", disable_ai_response=True)
        
        # help command
        await ctx.connector.send_text_message(ctx.lead, "Available demos: link, select")
        return RequestContext.cancel_response()