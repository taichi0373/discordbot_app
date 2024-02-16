import discord
from glob import glob
import os, asyncio

class AudioQueue(asyncio.Queue):
    def __init__(self):         #再生キューの上限
        super().__init__(100)

    def __getitem__(self, idx): #キュー内の要素をidx番目で取り出し
        return self._queue[idx]

    def to_list(self):          #キューをリスト化
        return list(self._queue)

    def reset(self):            #キューのリセット
        self._queue.clear()
        

class AudioStatus:
    def __init__(self, vc):
        self.vc = vc                                #自分が今入っているvc
        self.queue = AudioQueue()                   #再生キュー
        self.playing = asyncio.Event()
        asyncio.create_task(self.playing_task())
    
    def get_list(self):
        return self.queue.to_list()
    
    #曲の追加
    async def add_audio(self, title, path):
        await self.queue.put([title, path])
        
    async def remove_audio(self, queue_idx):
        if queue_idx < len(self.queue):
            del self.queue._queue[queue_idx]
            return True
        return False
        
    #曲の再生（再生にはffmpegが必要）    
    async def playing_task(self):
        while True:
            self.playing.clear()
            try:
                title, path = await asyncio.wait_for(self.queue.get(), timeout=180)      #timeout: taskが無ければ3分後に切断  
            except asyncio.TimeoutError:
                asyncio.create_task(self.leave())
            volume = 0.6
            try:
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path), volume=volume)
                print(f'{path}を再生します')
                self.vc.play(source, after = self.play_next)
                await self.playing.wait()  #再生可能になるまで待つ
            except:
                asyncio.create_task(self.leave())
                return print("error")
 
 
    # 次の曲を再生するためのメソッド
    async def play_next_audio(self):
        if not self.vc:
            return
        self.vc.stop()  # 現在再生中の曲を停止
        #task = await self.playing_task((self.queue.get()))  # キューから次の曲を取得して再生
        task = await self.playing_task(await self.queue.get())
        asyncio.create_task(task)
        
        
    #playing_taskの中で呼び出される
    #再生が終わると次の曲を再生する
    def play_next(self, err=None):
        self.bgminfo = None
        self.playing.set()
        return
            
    #vcの切断 and キューのリセット
    async def leave(self):
        self.queue.reset()  
        if self.vc:
            await self.vc.disconnect()  
            self.vc = None
        return
    
    #キューのリセットのみ
    async def reset(self):
        self.queue.reset()  
    
    
    #曲が再生中ならtrue
    def is_playing(self):
        return self.vc.is_playing()
    def playing_info(self):
        if (self.bgminfo is None):
            return 'This bot is not playing an Audio File'

