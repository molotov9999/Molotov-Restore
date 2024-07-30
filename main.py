import discord
import asyncio
import requests
import sqlite3
import datetime
import uuid
import config
import requests
import embed

intents = discord.Intents.all()
client = discord.Client(intents=intents)
end_msg = "\n\n> Molotov Restore"

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def embed(embedtype, embedtitle, description):
    if (embedtype == "error"):
        return discord.Embed(color=0xff0000, title=embedtitle, description=description)
    if (embedtype == "success"):
        return discord.Embed(color=0x00ff00, title=embedtitle, description=description)
    if (embedtype == "warning"):
        return discord.Embed(color=0xffff00, title=embedtitle, description=description)

def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간 " + str(round(minutes)) + "분"
    else:
        return False

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime_STR = (ServerTime + datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + datetime.timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

async def exchange_code(code, redirect_url):
    data = {
      'client_id': config.client_id,
      'client_secret': config.client_secret,
      'grant_type': 'authorization_code',
      'code': code,
      'redirect_uri': redirect_url
    }
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    while True:
        r = requests.post('%s/oauth2/token' % config.api_endpoint, data=data, headers=headers)
        if (r.status_code != 429):
            break
        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)
    return False if "error" in r.json() else r.json()

async def refresh_token(refresh_token):
    data = {
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    while True:
        r = requests.post('%s/oauth2/token' % config.api_endpoint, data=data, headers=headers)
        if (r.status_code != 429):
            break

        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)

    print(r.json())
    return False if "error" in r.json() else r.json()

async def add_user(access_token, guild_id, user_id):
    while True:
        jsonData = {"access_token" : access_token}
        header = {"Authorization" : "Bot " + config.token}
        r = requests.put(f"{config.api_endpoint}/guilds/{guild_id}/members/{user_id}", json=jsonData, headers=header)
        if (r.status_code != 429):
            break

        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)

    if (r.status_code == 201 or r.status_code == 204):
        return True
    else:
        print(r.json())
        return False

async def get_user_profile(token):
    header = {"Authorization" : token}
    res = requests.get("https://discordapp.com/api/v8/users/@me", headers=header)
    print(res.json())
    if (res.status_code != 200):
        return False
    else:
        return res.json()

def start_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    return con, cur

async def is_guild(id):
    con,cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    res = cur.fetchone()
    con.close()
    if (res == None):
        return False
    else:
        return True

def eb(embedtype, embedtitle, description):
    if (embedtype == "error"):
        return discord.Embed(color=0xff0000, title=":no_entry: " + embedtitle, description=description)
    if (embedtype == "success"):
        return discord.Embed(color=0x00ff00, title=":white_check_mark: " + embedtitle, description=description)
    if (embedtype == "warning"):
        return discord.Embed(color=0xffff00, title=":warning: " + embedtitle, description=description)
    if (embedtype == "loading"):
        return discord.Embed(color=0x808080, title=":gear: " + embedtitle, description=description)
    if (embedtype == "primary"):
        return discord.Embed(color=0x82ffc9, title=embedtitle, description=description)

async def is_guild_valid(id):
    if not (str(id).isdigit()):
        return False
    if not (await is_guild(id)):
        return False
    con,cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    guild_info = cur.fetchone()
    expire_date = guild_info[3]
    con.close()
    if (is_expired(expire_date)):
        return False
    return True

owner=[]

@client.event
async def on_ready():
    print(f"Login: {client.user}\nInvite Link: https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot")
    while True:
        await client.change_presence(activity=discord.Game(name=str(len(client.guilds)) + "개의 서버이용"))
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Activity(name=str(len(client.guilds)) + "개의 서버이용",type=discord.ActivityType.watching))
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Streaming(name=str(len(client.guilds)) + "개의 서버이용", url="https://www.twitch.tv/lck_korea"))
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=str(len(client.guilds)) + "개의 서버이용"))
        await asyncio.sleep(5)

@client.event
async def on_message(message):
    if (message.content.startswith("!명령어")):
        await message.reply(embed=discord.Embed(title="[ Molotov Restore ]",description=f"!인증 [channel] : 인증을 하실채널을 지정해주세요.\n!복구 [str] : 자신에게 지급된 복구키로 복구를 시작합니다.\n!정보 :라이센스 정보를 확인합니다.\n!로그웹훅 (웹훅) : 인증로그를 보낼곳을 지정합니다.\n!웹훅보기 : 인증로그가 지정되어있는 웹훅을 보여줍니다.\n!역할 @멘션 : 인증시 부여할 역할을 지정합니다.{end_msg}"))

    if message.author.id in owner:
        if (message.content.startswith("!서버삭제 ")):
            amount = message.content.split(" ")[1:]
            try:
                con,cur = start_db()
                cur.execute(f"DELETE FROM guilds WHERE id == ?;",(amount))
                con.commit()
                con.close()
                await message.reply(embed=discord.Embed(title="서버 삭제 완료",description=str(amount)+" 서버 삭제 완료"))
            except Exception as e:
                print(e)
                await message.reply(embed=discord.Embed(title="서버 삭제 실패",description=f"서버 삭제에 실패했습니다\n{amount}"))
                return

        if (message.content.startswith("!생성 ")):
            amount = message.content.split(" ")[1]
            long = message.content.split(" ")[2]
            if (amount.isdigit() and int(amount) >= 1 and int(amount) <= 10):
                con,cur = start_db()
                generated_key = []
                for n in range(int(amount)):
                    key = str(uuid.uuid4())
                    generated_key.append(key)
                    cur.execute("INSERT INTO licenses VALUES(?, ?);", (key, int(long)))
                    con.commit()
                con.close()
                generated_key = "\n".join(generated_key)
                await message.channel.send(generated_key,embed=embed("success", f"{long} 일 라이센스 {amount} 개 생성 성공", generated_key))
            else:
                await message.channel.send(embed=embed("error", "오류", "최대 10개까지 생성 가능합니다."))

    try:
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (message.content == ("!웹훅보기")):
                if not (await is_guild_valid(message.guild.id)):
                    await message.channel.send(embed=embed("error", "오류", "유효한 라이센스가 존재하지 않습니다."))
                    return
                con,cur = start_db()
                cur.execute("SELECT * FROM guilds WHERE id == ?;", (message.guild.id,))
                guild_info = cur.fetchone()
                con.close()
                if guild_info[4] == "no":
                    await message.channel.send(embed=embed("error", "오류", "웹훅이 없습니다."))
                    return
                await message.reply(f"{guild_info[4]}")

            if (message.content == ("!정보")):
                if not (await is_guild_valid(message.guild.id)):
                    await message.channel.send(embed=embed("error", "오류", "유효한 라이센스가 존재하지 않습니다."))
                    return
                con,cur = start_db()
                cur.execute("SELECT * FROM guilds WHERE id == ?;", (message.guild.id,))
                guild_info = cur.fetchone()
                con.close()
                await message.channel.send(embed=embed("success" , "라이센스 정보", f"{get_expiretime(guild_info[3])} 남음\n{guild_info[3]} 까지 이용이 가능합니다"))
    except:
        pass

    if (message.guild != None or message.author.id in owner or message.author.guild_permissions.administrator):
        if (message.content.startswith("!등록 ")):
            license_number = message.content.split(" ")[1]
            con,cur = start_db()
            cur.execute("SELECT * FROM licenses WHERE key == ?;", (license_number,))
            key_info = cur.fetchone()
            if (key_info == None):
                con.close()
                await message.channel.send(embed=embed("error", "오류", "존재하지 않거나 이미 사용된 라이센스입니다."))
                return
            cur.execute("DELETE FROM licenses WHERE key == ?;", (license_number,))
            con.commit()
            con.close()
            key_length = key_info[1]

            if (await is_guild(message.guild.id)):
                con,cur = start_db()
                cur.execute("SELECT * FROM guilds WHERE id == ?;", (message.guild.id,))
                guild_info = cur.fetchone()
                expire_date = guild_info[3]
                if (is_expired(expire_date)):
                    new_expiredate = make_expiretime(key_length)
                else:
                    new_expiredate = add_time(expire_date, key_length)

                cur.execute("UPDATE guilds SET expiredate = ? WHERE id == ?;", (new_expiredate, message.guild.id))
                con.commit()
                con.close()
                await message.channel.send(embed=embed("success", "성공", f"{key_length}일 라이센스가 성공적으로 등록되었습니다."))

            else:
                con,cur = start_db()
                new_expiredate = make_expiretime(key_length)
                recover_key = str(uuid.uuid4())[:8].upper()
                cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?);", (message.guild.id, 0, recover_key, new_expiredate,"no"))
                con.commit()
                con.close()
                await message.channel.send(f"{message.author.mention} 님 디엠을 확인해주세요")
                await message.author.send(embed=embed("success", "[ Molotov Restore ]", f"복구 키 : `{recover_key}`\n해당 키를 꼭 기억하거나 저장해 주세요."))
    
    if message.author.guild_permissions.administrator or message.author.id in owner:
        if (message.content == "!인증"):
            if not (await is_guild_valid(message.guild.id)):
                return
            await message.channel.send(embed=discord.Embed(color=0x5865F2, title="Dev Restoration", description=f"Please authorize your account [here](https://discord.com/api/oauth2/authorize?client_id={config.client_id}&redirect_uri={config.base_url}%2Fcallback&response_type=code&scope=identify%20guilds.join&state={message.guild.id}) to see other channels.\n다른 채널을 보려면 [여기](https://discord.com/api/oauth2/authorize?client_id={config.client_id}&redirect_uri={config.base_url}%2Fcallback&response_type=code&scope=identify%20guilds.join&state={message.guild.id}) 를 눌러 계정을 인증해주세요."))

        if message.content.startswith("!로그웹훅 "):
            if not (await is_guild_valid(message.guild.id)):
                return
            webhook = message.content.split(" ")[1]
        
            con, cur = start_db()
            cur.execute("UPDATE guilds SET verify_webhook == ? WHERE id = ?;", (str(webhook), message.guild.id))
            con.commit()
            con.close()
            await message.reply(embed=embed("success", "인증로그 웹훅저장 성공", f"인증을 완료한후 {webhook} 으로 인증로그가 전송됩니다"))

        if (message.content.startswith("!역할 <@&") and message.content[-1] == ">"):
            if (await is_guild_valid(message.guild.id)):
                mentioned_role_id = message.content.split(" ")[1].split("<@&")[1].split(">")[0]
                if not (mentioned_role_id.isdigit()):
                    await message.channel.send(embed=embed("error", "오류", "존재하지 않는 역할입니다."))
                    return
                mentioned_role_id = int(mentioned_role_id)
                role_info = message.guild.get_role(mentioned_role_id)
                if (role_info == None):
                    await message.channel.send(embed=embed("error", "오류", "존재하지 않는 역할입니다."))
                    return

                con,cur = start_db()
                cur.execute("UPDATE guilds SET role_id = ? WHERE id == ?;", (mentioned_role_id, message.guild.id))
                con.commit()
                con.close()
                await message.channel.send(embed=embed("success", "역할 설정 성공", "인증을 완료한 유저에게 해당 역할이 지급됩니다."))

    if message.author.id in owner:
        if (message.content.startswith("!복구 ")):
            recover_key = message.content.split(" ")[1]
            if (await is_guild_valid(message.guild.id)):
                await message.channel.send(embed=embed("error", "오류", "복구봇 라이센스 등록 전에 복구를 진행하셔야 합니다."))
            else:
                con,cur = start_db()
                cur.execute("SELECT * FROM guilds WHERE token == ?;", (recover_key,))
                token_result = cur.fetchone()
                con.close()
                if (token_result == None):
                    await message.channel.send(embed=embed("error", "오류", "존재하지 않는 복구 키입니다. 관리자에게 문의해주세요,"))
                    return
                if not (await is_guild_valid(token_result[0])):
                    await message.channel.send(embed=embed("error", "오류", "만료된 복구 키입니다. 관리자에게 문의해주세요."))
                    return
                try:
                    server_info = await client.fetch_guild(token_result[0])
                except:
                    server_info = None
                    pass
                if not (await message.guild.fetch_member(client.user.id)).guild_permissions.administrator:
                    await message.channel.send(embed=embed("error", "오류", "복구를 위해서는 봇이 관리자 권한을 가지고 있어야 합니다."))
                    return

                con,cur = start_db()
                cur.execute("SELECT * FROM users WHERE guild_id == ?;", (token_result[0],))
                users = cur.fetchall()
                con.close()

                users = list(set(users))

                await message.channel.send(embed=embed("success", "성공", "유저 복구 중입니다. 최대 2시간이 소요될 수 있습니다."))

                for user in users:
                    try:
                        refresh_token1 = user[1]
                        user_id = user[0]
                        new_token = await refresh_token(refresh_token1)
                        if (new_token != False):
                            new_refresh = new_token["refresh_token"]
                            new_token = new_token["access_token"]
                            await add_user(new_token, message.guild.id, user_id)
                            print(new_token)
                            con,cur = start_db()
                            cur.execute("UPDATE users SET token = ? WHERE token == ?;", (new_refresh, refresh_token1))
                            con.commit()
                            con.close()
                    except:
                        pass

                con,cur = start_db()
                cur.execute("UPDATE users SET guild_id = ? WHERE guild_id == ?;", (message.guild.id, token_result[0]))
                con.commit()
                cur.execute("UPDATE guilds SET id = ? WHERE id == ?;", (message.guild.id ,token_result[0]))
                con.commit()
                con.close()

                await message.channel.send(embed=embed("success", "성공", "유저 복구가 완료되었습니다. 기존 라이센스와 복구 키는 모두 이동됩니다."))

    if message.content.startswith("!채널복구"):
        if message.author.guild_permissions.administrator:
            con = sqlite3.connect("./database.db")
            cur = con.cursor()
            try:
                for ch in message.guild.channels:
                    name = ch.name
                    cur.execute("insert into channels values(?, ?);", (message.guild.id, name))
                    con.commit()
            except:
                print("error")
                pass
            await message.channel.send("채널복구 완료") 

client.run(config.token)
