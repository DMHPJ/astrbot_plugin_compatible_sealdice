import asyncio

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


IGNORED_PREFIXES = ("!", ".", "。", "/")
LOG_ON_COMMAND = ".log on"
LOG_OFF_COMMAND = ".log off"
STORAGE_KEY = "disabled_groups"


def _message_text(event: AstrMessageEvent) -> str:
    """返回唤醒前缀被 AstrBot 移除前的原始纯文本。"""
    return event.message_obj.message_str.lstrip()


def _group_key(event: AstrMessageEvent) -> str | None:
    group_id = event.get_group_id()
    if not group_id:
        return None
    return f"{event.get_platform_name()}:{group_id}"


class SeaDiceMessageFilter(filter.CustomFilter):
    """只唤醒需要由本插件拦截的消息，避免误唤醒普通群消息。"""

    disabled_groups: set[str] = set()

    def filter(self, event: AstrMessageEvent, _cfg) -> bool:
        message = _message_text(event)
        if message.startswith(IGNORED_PREFIXES):
            return True

        group_key = _group_key(event)
        return group_key is not None and group_key in self.disabled_groups


@register(
    "astrbot_plugin_compatible_sealdice",
    "DMHPJ",
    "避免 AstrBot 与 SealDice 同时响应",
    "1.0.0",
)
class CompatibleSeaDicePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._state_lock = asyncio.Lock()

    async def initialize(self):
        disabled_groups = await self.get_kv_data(STORAGE_KEY, [])
        SeaDiceMessageFilter.disabled_groups = set(disabled_groups)

    async def _set_group_disabled(self, group_key: str, disabled: bool) -> None:
        async with self._state_lock:
            if disabled:
                SeaDiceMessageFilter.disabled_groups.add(group_key)
            else:
                SeaDiceMessageFilter.disabled_groups.discard(group_key)

            await self.put_kv_data(
                STORAGE_KEY,
                sorted(SeaDiceMessageFilter.disabled_groups),
            )

    @filter.custom_filter(SeaDiceMessageFilter, priority=1000)
    async def intercept_sealdice_messages(self, event: AstrMessageEvent):
        """拦截 SealDice 指令，并在记录期间静默当前群的 AstrBot。"""
        event.stop_event()

        group_key = _group_key(event)
        if group_key is None:
            return

        command = _message_text(event).strip().casefold()
        if command == LOG_ON_COMMAND:
            await self._set_group_disabled(group_key, True)
            logger.info(f"SealDice 记录已开启，AstrBot 在群 {group_key} 中进入静默。")
        elif command == LOG_OFF_COMMAND:
            await self._set_group_disabled(group_key, False)
            logger.info(f"SealDice 记录已关闭，AstrBot 在群 {group_key} 中恢复响应。")
