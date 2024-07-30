import discord

end_msg = "\n> Supporter : `MUTE`, `MSH` Dev : `Triglav`, `MLYO` ㅣ [Support Server](https://fomon.xyz/Dev) ㅣ [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=905029153533878322&permissions=8&scope=bot)"

help_embed = discord.Embed(title=".", description="더욱 열심히 하는 .가 되겠습니다. 명령어는 하단을 참고해주세요.", color=0x62c1cc)
help_embed.add_field(name="!인증", value="인증을 하실채널을 지정합니다.", inline=False)
help_embed.add_field(name="!복구 복구키", value="자신에게 지급된 복구키로 복구를 시작합니다.", inline=False)
help_embed.add_field(name="!정보", value="라이센스 정보를 확인합니다.", inline=False)
help_embed.add_field(name="!로그웹훅 (웹훅)", value="인증로그를 보낼곳을 지정합니다.", inline=False)
help_embed.add_field(name="!웹훅보기", value="인증로그가 지정되어있는 웹훅을 보여줍니다.", inline=False)
help_embed.add_field(name="!역할 @멘션", value="인증시 부여할 역할을 지정합니다.", inline=False)