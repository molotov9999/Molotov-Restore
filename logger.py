import requests 

def send(url, title, discription, content):
    data = {
        "username" : "인증로그",
        "content" : content,
        "avatar_url" : "https://cdn.discordapp.com/avatars/905029153533878322/1d1bcc25c20c25bbdae79ab0bb2726d2.webp?size=80"
    }
    data["embeds"] = [{"description" : discription, "title" : title}]
    result = requests.post(url, json = data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

