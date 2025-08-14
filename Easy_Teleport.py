from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'ez_tp',
    'version': '0.0.1',
    'name': '简单TP'
}

def on_load(server: PluginServerInterface, old):

    server.register_command(
        Literal('!!etp')
        .runs(etp_root)
        .then(
            Literal('players')
            .runs(etp_player_list) 
        )
        .then(
            Literal('player')
            .then(
                Text('target')
                .runs(
                    lambda src, ctx: etp_player_tp_command(
                        src, ctx.get('target')
                    )
                )
            )
        )
        .then(
            Literal('locations')
            .runs(lambda src: src.reply('功能尚未实现，请稍后再试。'))  # Placeholder for location command
        )
    )

@new_thread("etp_root")
def etp_root(src: CommandSource):
    if src.is_player:
        playerSrc: PlayerCommandSource = src
        
        playerSrc.reply('')
        playerSrc.reply('==简单TP菜单==')
        playerSrc.get_server().execute(
            'tellraw {} [{{"text":"传送到","underlined":true,"clickEvent":{{"action":"suggest_command","value":"!!etp players"}}}},{{"text":"玩家 ","color":"green","underlined":true,"clickEvent":{{"action":"suggest_command","value":"!!etp players"}}}}]'.format(playerSrc.player)
        )
        playerSrc.get_server().execute(
            'tellraw {} [{{"text":"传送到","underlined":true,"clickEvent":{{"action":"suggest_command","value":"!!etp locations"}}}},{{"text":"地点 ","color":"yellow","underlined":true,"clickEvent":{{"action":"suggest_command","value":"!!etp locations"}}}}]'.format(playerSrc.player)
        )
        playerSrc.reply('============')
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
            'tellraw {} [{{"text":"{}","color":"green","underlined":true,"clickEvent":{{"action":"suggest_command","value":"!!etp player {}"}}}}]'.format(
                playerSrc.player, player, player)
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