from mcdreforged.api.all import *
import json

class Position:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

def build_tellraw(target: str, args: list) -> str:
    """
    Concatenate a tellraw command.
    Args:
        target (str): The player or selector to send the tellraw to.
        args (list): A list of dict objects representing tellraw JSON components.
    Returns:
        str: The tellraw command string.
    """
    return f'tellraw {target} {json.dumps(args, ensure_ascii=False)}'

PLUGIN_METADATA = {
    'id': 'ez_tp',
    'version': '1.0.0',
    'name': '简单TP'
}

def on_load(server: PluginServerInterface, old):

    server.register_command(
        Literal('@etp')
            .runs(etp_root)
            .then(
                Literal('player')
                    .then(
                        Literal('list')
                            .runs(etp_player_list) 
                    )
                    .then(
                        Literal('go')
                            .then(
                                Text('target')
                                    .runs(
                                        lambda src, 
                                        ctx: etp_player_tp_command(
                                            src, ctx.get('target')
                                        )
                                    )
                            )
                    )
            )
            .then(
                Literal('location')
                    .then(
                        Literal('list')
                            .runs(
                                lambda src,
                                ctx: etp_location_list(src, 0)
                            )
                            .then(
                                Integer('page')
                                    .runs(
                                        lambda src, 
                                        ctx: etp_location_list(
                                            src, ctx.get('page')
                                        )
                                    )
                            )
                    )
                    .then(
                        Literal('force-set')
                            .then(
                                Text('name')
                                    .runs(
                                        lambda src, 
                                        ctx: etp_location_set_command(
                                            src, ctx.get('name'), True
                                        )
                                    )
                            )
                    )
                    .then(
                        Literal('set')
                            .then(
                                Text('name')
                                    .runs(
                                        lambda src, 
                                        ctx: etp_location_set_command(
                                            src, ctx.get('name')
                                        )
                                    )
                            )
                    )
                    .then(
                        Literal('go')
                            .then(
                                Text('target')
                                    .runs(
                                        lambda src,
                                        ctx: etp_location_tp_command(
                                            src, ctx.get('target')
                                        )
                                    )
                            )
                    )
            )
    )

@new_thread("etp_root")
def etp_root(src: CommandSource):
    if src.is_player:
        playerSrc: PlayerCommandSource = src
        
        playerSrc.reply('')
        playerSrc.reply('== 简单TP菜单 ==')
        playerSrc.get_server().execute(
            build_tellraw(
                playerSrc.player,
                [
                    {
                        "text": "传送到",
                        "underlined": True,
                        "clickEvent": {
                            "action": "suggest_command",
                            "value": "@etp player list"
                        }
                    },
                    {
                        "text": "玩家",
                        "color": "green",
                        "underlined": True,
                        "clickEvent": {
                            "action": "suggest_command",
                            "value": "@etp player list"
                        }
                    }
                ]
            )
        )
        playerSrc.get_server().execute(
            build_tellraw(
                playerSrc.player,
                [
                    {
                        "text": "传送到",
                        "underlined": True,
                        "clickEvent": {
                            "action": "suggest_command",
                            "value": "@etp location list"
                        }
                    },
                        {
                        "text": "地点",
                        "color": "yellow",
                        "underlined": True,
                        "clickEvent": {
                            "action": "suggest_command",
                            "value": "@etp location list"
                        }
                    }
                ]
            )
        )
        playerSrc.get_server().execute(
            build_tellraw(
                playerSrc.player,
                [
                    {
                        "text": "记录此地",
                        "color": "aqua",
                        "underlined": True,
                        "clickEvent": {
                            "action": "suggest_command",
                            "value": "@etp location set <名称>"
                        }
                    }
                ]
            )
        )
        playerSrc.reply('=' * 14)
        playerSrc.reply('')

@new_thread("etp_player_list")
def etp_player_list(src: CommandSource):
    if src.is_player:
        import minecraft_data_api as api

        playerSrc: PlayerCommandSource = src
        # 3个元组类型
        _amount, _limit, players = api.get_server_player_list()
        # get <name> array from the string
        
        if not players:
            return src.reply(RText('当前没有在线玩家。', color='red'))
        
        # 输出标题，居中显示
        playerSrc.reply('')
        playerSrc.reply('===== 传送到玩家 =====')
        for player in players:
            if player == playerSrc.player: continue
            # 居中玩家名，两侧空格补齐
            playerSrc.get_server().execute(
                build_tellraw(
                    playerSrc.player,
                    [
                        {
                            "text": player,
                            "color": "green",
                            "underlined": True,
                            "clickEvent": {
                                "action": "suggest_command",
                                "value": f"@etp player go {player}"
                            }
                        }
                    ]
                )
            )
        # 计算输出区域的长度
        playerSrc.reply('=' * 20)
        playerSrc.reply('')
            

@new_thread("etp_player_tp_command")
def etp_player_tp_command(src: CommandSource, target: str):
    server = src.get_server()
    if src.is_player:
        import minecraft_data_api as api
        srcPlayer: PlayerCommandSource = src
        _amount, _limit, players = api.get_server_player_list()
        if target not in players:
            src.reply('玩家 {} 不在线。'.format(target))
            return
        # 传送命令
        server.execute('tp {} {}'.format(srcPlayer.player, target))
        src.reply('已将你传送到玩家 {}'.format(target))
        
@new_thread("etp_location_list")
def etp_location_list(src: CommandSource, page: int = 0):
    server = src.get_server()
    src.reply('==== 地点列表 ====')
    import os
    import json
    locations_file = os.path.join(os.getcwd(), 'plugins', 'etp_locations.json')
    if not os.path.exists(locations_file):
        src.reply('没有已保存的地点。')
        return
    with open(locations_file, 'r', encoding='utf-8') as f:
        locations = json.load(f)    
    if not locations:
        src.reply('没有已保存的地点。')
        return
    # 每页显示8个地点
    items_per_page = 8
    total_items = len(locations)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    if page < 0 or page >= total_pages:
        src.reply(f'页码无效。请输入 0 到 {total_pages - 1} 之间的数字。')
        return
    start_index = page * items_per_page
    end_index = min(start_index + items_per_page, total_items)
    location_items = list(locations.items())[start_index:end_index]
    if not location_items:
        src.reply(f'没有更多地点。当前页码: {page + 1}/{total_pages}')
        return
    for name, _position in location_items:
        src.get_server().execute(
            build_tellraw(
                src.player,
                [
                    {
                        "text": f"{name}",
                        "color": "yellow",
                        "underlined": True,
                        "clickEvent": {
                            "action": "suggest_command",
                            "value": f"@etp location go {name}"
                        }
                    }
                ]
            )
        )
    server.execute(
        build_tellraw(
            src.player,
            [
                {"text": "==="},
                {
                    "text": " ← ",
                    "color": "gray" if page == 0 else "green",
                    "clickEvent": {
                        "action": "suggest_command",
                        "value": f"@etp location list {max(0, page - 1)}" if page > 0 else ""
                    }
                },
                {"text": str(page + 1), "color": "white"},
                {"text": f"/{total_pages} ", "color": "gray"},
                {
                    "text": " → ",
                    "color": "gray" if page >= total_pages - 1 else "green",
                    "clickEvent": {
                        "action": "suggest_command",
                        "value": f"@etp location list {min(total_pages - 1, page + 1)}" if page < total_pages - 1 else ""
                    }
                },
                {"text": "==="}
            ]
        )
    )

@new_thread("etp_location_set_command")
def etp_location_set_command(src: CommandSource, name: str, force: bool = False):
    server = src.get_server()
    if src.is_player:
        import minecraft_data_api as api
        srcPlayer: PlayerCommandSource = src
        # 获取玩家位置
        pos =  api.get_player_info(srcPlayer.player, 'Pos')
        if pos is None:
            raise ValueError('无法获取玩家位置。')
        position = Position(pos[0], pos[1], pos[2])
        
        import os
        import json
        locations_file = os.path.join(os.getcwd(), 'plugins', 'etp_locations.json')

        # 读取已存在的坐标数据
        if os.path.exists(locations_file):
            with open(locations_file, 'r', encoding='utf-8') as f:
                locations = json.load(f)
        else:
            locations = {}

        if name in locations and not force:
            # 已存在同名地点，提示用户覆盖
            existing = locations[name]
            srcPlayer.reply('')
            server.execute(
                build_tellraw(
                    srcPlayer.player,
                    [
                        {"text": f"已存在此地点 ({round(existing['x'], 2)}, {round(existing['y'], 2)}, {round(existing['z'], 2)})，点击", "color": "white"},
                        {
                            "text": "这里",
                            "color": "green",
                            "underlined": True,
                            "clickEvent": {
                                "action": "suggest_command",
                                "value": f"@etp location force-set {name}"
                            }
                        },
                        {"text": "确认覆盖", "color": "white"}
                    ]
                )
            )
            srcPlayer.reply('')
            
        else:
            # 保存新坐标
            locations[name] = {'x': position.x, 'y': position.y, 'z': position.z}

            with open(locations_file, 'w', encoding='utf-8') as f:
                json.dump(locations, f, ensure_ascii=False, indent=2)

            srcPlayer.reply('')
            server.execute(
                build_tellraw(
                    srcPlayer.player, 
                    [
                        {"text": "已保存当前位置为: ", "color": "white"},
                        {"text": name, "color": "green"},
                        {"text": f" ({round(position.x, 2)}, {round(position.y, 2)}, {round(position.z, 2)})", "color": "white"}
                    ]
                )
            )
            srcPlayer.reply('')

@new_thread("etp_location_tp_command")
def etp_location_tp_command(src: CommandSource, target: str):
    server = src.get_server()
    if src.is_player:
        import os
        import json
        locations_file = os.path.join(os.getcwd(), 'plugins', 'etp_locations.json')
        
        if not os.path.exists(locations_file):
            src.reply('没有已保存的地点。')
            return
        
        with open(locations_file, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        if target not in locations:
            src.reply('没有名为 {} 的地点。'.format(target))
            return
        
        coords = locations[target]
        # 传送命令
        server.execute('tp {} {} {} {}'.format(src.player, coords['x'], coords['y'], coords['z']))
        # 回复玩家
        server.execute(
            build_tellraw(
                src.player,
                [
                    {"text": "已将你传送到地点: ", "color": "white"},
                    {"text": target, "color": "green"},
                ]
            )
        )
