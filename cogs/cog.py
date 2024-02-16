from discord.ext import commands
import discord, os, glob, asyncio, json, io

from google.cloud import translate_v2 as translate
from google.cloud import texttospeech

    
from cogs.func.apex import Apex
from cogs.func.music import AudioStatus
from cogs.func.ydl2 import Music
from cogs.func.sens import Sens

class MyCog(commands.Cog):
    def __init__(self, bot):
        #super().__init__()
        self.bot = bot
        self.Audio_queue = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("準備完了！")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("そのコマンドは存在しません")
            
            
    @commands.command()
    async def hello(self, ctx):
            await ctx.send("hello!")  

    @commands.command(name="tts", help='テキスト読み上げを行うためのテキストチャンネルを作成します')
    async def tts(self, ctx):
        channel_text = "読み上げチャンネル"
        tts_channel = discord.utils.get(self.bot.get_all_channels(), name=channel_text, type=discord.ChannelType.text)   #テキストチャンネルを表す
        if tts_channel is None:
            category = discord.utils.get(ctx.guild.categories, name="テキストチャンネル")
            await ctx.guild.create_text_channel(name="読み上げチャンネル", category=category)
            await ctx.send("読み上げチャンネルを作成しました")
            await ctx.send("読み上げチャンネルで入力してください")
            
        else:
            await ctx.send("読み上げチャンネルが既に存在します")
            await ctx.send("読み上げチャンネルで入力してください")

    @commands.command(name="trans", help='テキストを翻訳します')
    async def trans(self, ctx):
        # 入力待ちメッセージを送信する
        await ctx.send('翻訳する文章を入力してください')

        # 1つ目の入力値を受け取る
        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg1 = await self.bot.wait_for('message', check=check1)
        text = msg1.content
        try:
            # Google Cloud Translation APIを使用して翻訳を実行する
            translate_client = translate.Client()
            result = translate_client.translate(text, target_language='en')

            # 翻訳結果を返信する
            await ctx.send(f'翻訳結果: {result["translatedText"]}')
        except Exception as e:
            print(e)
            await ctx.send(f'エラー')

    @commands.command(name="clear", help='コマンドが入力されたテキストチャンネルのテキストを全て削除します')
    async def clear(self, ctx):
        channel = ctx.message.channel
        await channel.purge()

    @commands.command(name="member", help='サーバーに参加しているメンバーを表示します')
    async def member(self, ctx):
        members = ctx.channel.members
        member_list = "\n".join([member.name for member in members])
        await ctx.send(member_list)

    @commands.command(name="role", help='サーバーに参加しているメンバーのロールを表示します')
    async def role(self, ctx):
        roles = ctx.guild.roles
        role_list = [role.name for role in roles]
        await ctx.send(f"Roles in this server: {', '.join(role_list)}")


    @commands.command(name="music", help='音楽を再生します。事前にボイスチャンネルに入る必要があります')
    async def music(self, ctx):
        if ctx.guild.voice_client is None:
            await ctx.send("ボイスチャンネルに接続していません。")
            return

        # 入力待ちメッセージを送信する
        await ctx.send('URLを入力してください')

        # URLを受け取る
        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check1)
        url = msg.content
        
        title = None  # 初期化
        if Music(url).download_music() == "error":
            await ctx.send("URLが存在しません")
            return
        
        title = Music(url).download_music()

        print("music:", title)
        
        await self.Audio_queue.add_audio(title, f'./downloads/{title}.wav')          #music = ./downloads/アスノヨゾラ哨戒班.webm
        await ctx.send(f"{title}を再生リストに追加しました")


    @commands.command(name="play", help='音楽を再生します')
    async def play(self, ctx):
        if ctx.guild.voice_client is None:
            await ctx.send("ボイスチャンネルに接続していません。")
            return
        
        # 再生中の場合は再生しない
        if ctx.guild.voice_client.is_playing():
            await ctx.send("再生中です。")
            return
        ctx.guild.voice_client.resume()

    @commands.command(name="queue", help='プレイリストを表示します')
    async def queue(self, ctx):
        if ctx.guild.voice_client is None:
            await ctx.send("ボイスチャンネルに接続していません。")
            return
        
        queue_list = self.Audio_queue.get_list()
        if len(queue_list) == 0:
            await ctx.send("再生リストがありません。")
            return
        songs = ""
        await ctx.send("------next-------")
        for i, (title, _) in enumerate(queue_list):
            songs += f"{i+1}. {title}\n"
        await ctx.send(songs)

    @commands.command("reset", help='プレイリストをリセットします')
    async def reset(self, ctx):
        queue_list = self.Audio_queue.get_list()
        if len(queue_list) == 0:
            await ctx.send("再生リストがありません。")
            return
        try:   
            """再生キューのリセット"""
            self.Audio_queue.reset()
            await ctx.send("キューをリセットしました")
        except:
            await ctx.send("キューをリセットできませんでした")
            
    @commands.command(name="next", help='次の曲を再生します')
    async def next(self, ctx):
        queue_list = self.Audio_queue.get_list()
        if not self.Audio_queue.is_playing():
            await ctx.send('曲が再生されていません')
            return       
        if len(queue_list) == 0:
            await ctx.send("再生リストがありません。")
            return
        
        if self.Audio_queue.is_playing():
            await self.Audio_queue.play_next_audio()
            await ctx.send('次の曲を再生します')
        else:
            await ctx.send('曲が再生されていません')
   
    @commands.command(name="stop", help='再生中の曲を停止します')
    async def stop(self, ctx):
        if ctx.guild.voice_client is None:
            await ctx.send("ボイスチャンネルに接続していません。")
            return
        # 再生中ではない場合は実行しない
        if not ctx.guild.voice_client.is_playing():
            await ctx.send("音楽を再生していません。")
            return
        ctx.guild.voice_client.pause()
        await ctx.send("音楽を停止します")
        
    @commands.command(name="join", help='ボットをボイスチャンネルに参加させます')
    async def join(self, ctx):
        #global Audio_queue       #AudioStatusクラスのインスタンス
        if ctx.author.voice is None:
            await ctx.send("あなたはボイスチャンネルに接続していません。")
            return

        # ボットが既にボイスチャンネルに接続している場合は切断する
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.disconnect()

        # ボイスチャンネルに接続する
        voice_channel = ctx.author.voice.channel.id                     #送信者の入っているボイスチャンネルのID
        vc = await self.bot.get_channel(voice_channel).connect()             #ボイスチャンネルに入る
        self.Audio_queue = AudioStatus(vc)
        
        await self.Audio_queue.reset()  #キューのリセット
        
        folder_path = './downloads/'
        files = glob.glob(folder_path + '*')  # ディレクトリ内の全てのファイルを取得
        for file in files:
            os.remove(file)  # ファイルを削除
            
        folder_path = './text_speech/'
        files = glob.glob(folder_path + '*')  # ディレクトリ内の全てのファイルを取得
        for file in files:
            os.remove(file)  # ファイルを削除    
            
        
        await ctx.send("接続しました。")

    @commands.command(name="leave", help='ボットをボイスチャンネルから退出させます')
    async def leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.send("ボイスチャンネルに接続していません。")
            return
        #キューのリセット vc切断
        await self.Audio_queue.leave()
        self.vc = None
        
        #  ディレクトリ内の全てのファイルを削除
        folder_path = './downloads/'
        files = glob.glob(folder_path + '*')
        for file in files:
            os.remove(file)  
    
        await ctx.send("切断しました。")        

    @commands.command(name="sens", help='ゲームの振り向きを計算します')
    async def sens(self, ctx):
        games = ['apex', 'valorant', 'fortnite']
        options = '\n'.join([f'{index + 1}. {game}' for index, game in enumerate(games)])
        prompt = f'ゲームタイトルを入力してください:\n{options}'
        await ctx.send(prompt)

        # 1つ目の入力値を受け取る
        input1 = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

        try:
            choice_index = int(input1.content) - 1
            if choice_index < 0 or choice_index >= len(games):
                raise ValueError
        except ValueError:
            await ctx.send(f'ゲームタイトルが見つかりませんでした')
            return

        selected_game = games[choice_index]

        # 2つ目の入力値を受け取る
        await ctx.send("dpiを入力してください")
        input2 = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

        # 3つ目の入力値を受け取る
        await ctx.send("ゲーム内感度を入力してください")
        input3 = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

        user_sens = Sens(selected_game, input2.content, input3.content)
        hurimuki = user_sens.hurimuki()
        if hurimuki == "error":
            await ctx.send(f'数値を半角で入力してください')
        else:
            await ctx.send(f'振り向き：{hurimuki}cm')

    @commands.Cog.listener()
    async def on_voice_state_update(self, ctx, member, before, after):
        channel_text = "入退室通知"
        message_channel = discord.utils.get(self.bot.get_all_channels(), name=channel_text, type=discord.ChannelType.text)   #テキストチャンネルを表す
        if message_channel is None:
            category = discord.utils.get(ctx.guild.categories, name="テキストチャンネル")
            await ctx.guild.create_text_channel(name=channel_text, category=category)
            await ctx.send("入退室通知チャンネを作成しました")


        # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
        if before.channel != after.channel:
            
            # 通知メッセージを書き込むテキストチャンネル（チャンネル名を指定）
            botRoom = discord.utils.get(self.bot.get_all_channels(), name=channel_text, type=discord.ChannelType.text)   #テキストチャンネルを表す
            
            if botRoom is not None:
                # 入退室を監視する対象のボイスチャンネル（チャンネルIDを指定)
                channelvoice_name = "ゲーム"
                channel_voice = discord.utils.get(self.bot.get_all_channels(), name=channelvoice_name, type=discord.ChannelType.voice)   #ボイスチャンネルを表す
                
                # 退室通知
                if before.channel is not None and before.channel.name in channel_voice.name:
                    after_members = len(after.channel.members) if after.channel and after.channel.members else 0
                    await botRoom.send(f"**{before.channel.name}**から、__{member.name}__が退出しました！\n現在の参加人数：{after_members}人")
                # 入室通知
                if after.channel is not None and after.channel.name in channel_voice.name:
                    after_members = len(after.channel.members) if after.channel and after.channel.members else 0
                    await botRoom.send(f"**{after.channel.name}**に、__{member.name}__が参加しました！\n現在の参加人数：{after_members}人")



    @commands.group(name="apex")
    async def _apex(self, ctx):
        # サブコマンドが実行された時は何もしない
        if ctx.invoked_subcommand:
            return

    @_apex.command(name="stats", help='Apexの戦績を表示します')
    @commands.has_permissions(administrator=True)
    async def _apex_stats(self, ctx):
        platforms = ['origin', 'xbl', 'psn']
        options = '\n'.join([f'{index + 1}. {platform}' for index, platform in enumerate(platforms)])
        prompt = f'platformを入力してください:\n{options}'
        await ctx.send(prompt)
        
        # 1つ目の入力値を受け取る
        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            choice = await self.bot.wait_for('message', check=check1, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send('Time is up!')
            return
        
        try:
            choice_index = int(choice.content) - 1
            if choice_index < 0 or choice_index >= len(platforms):
                raise ValueError
        except ValueError:
            await ctx.send(f'プラットフォームが見つからなかった')
            return
        selected_platform = platforms[choice_index]


        await ctx.send('ゲームIDを入力してください')
        # 2つ目の入力値を受け取る
        def check2(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg2 = await self.bot.wait_for('message', check=check2)
        game_ID = msg2.content
        
        try:
            user = Apex(selected_platform, game_ID)
            response = user.GetProfile()
            data = json.loads(response)

            res_stats = Apex.DispStats(data)
            for key, value in res_stats.items():
                await ctx.send(f"{key} : {value}")
        except:
            await ctx.send(f'ユーザーが見つからなかった')   

    @_apex.command(name="rank", help='Apexのランクを表示します')
    @commands.has_permissions(administrator=True)
    async def _apex_rank(self, ctx):
        # 入力待ちメッセージを送信する
        #await ctx.send('')
        platforms = ['origin', 'xbl', 'psn']
        options = '\n'.join([f'{index + 1}. {platform}' for index, platform in enumerate(platforms)])
        prompt = f'platformを入力してください:\n{options}'
        await ctx.send(prompt)
        # 1つ目の入力値を受け取る
        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            choice = await self.bot.wait_for('message', check=check1, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send('Time is up!')
            return
        try:
            choice_index = int(choice.content) - 1
            if choice_index < 0 or choice_index >= len(platforms):
                raise ValueError
        except ValueError:
            await ctx.send(f'プラットフォームが見つからなかった')
            return
        selected_platform = platforms[choice_index]

        await ctx.send('ゲームIDを入力してください')
        # 2つ目の入力値を受け取る
        def check2(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg2 = await self.bot.wait_for('message', check=check2)
        game_ID = msg2.content
        try:
            user = Apex(selected_platform, game_ID)
            response = user.GetProfile()
            data = json.loads(response)
            
            res_rank = Apex.Disprank(data)
            for key, value in res_rank.items():
                await ctx.send(f"{key} : {value}")
        except:
            await ctx.send(f'ユーザーが見つからなかった')
            


async def setup(bot):
    await bot.add_cog(MyCog(bot))