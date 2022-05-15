import asyncio
import os
from datetime import datetime
from math import e
from telnetlib import EC

import discord
import gspread
import pandas as pd
import youtube_dl
from discord.channel import VoiceChannel
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials

from configuracion import *

id_hoja = '1qHJJHi1qPgsGGsmDo35xm68bR9aIiXnntKIDfi3DkA0'
# credencial de acceso app = AIzaSyA9GX-ar3lc3Tu4583XyNbTa3awbSx8PBQ
# datos del bot proporcionados por discord
TOKEN = get_token()
GUILD = get_guild()
# client = discord.Client()
sirsergio = 368302438953910273


bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print('Bot activado como  {0.user}'.format(bot))


def SheetAPI():
    # conexion a la hoja de google sheet

    cred = gspread.service_account(filename='miscredenciales.json')

    # abrir hoja de google sheet

    gsheet = cred.open_by_key(id_hoja)
    # obtenemos la hoja de google sheet
    sheet = gsheet.worksheet('MAYO_2022')

    return sheet

    
"""    # valores de la hoja de google sheet

    data=sheet.get_all_records()
    df=pd.DataFrame(data)

    # obtenemos los valores de la columna de google sheet para mostrarlos en el terminal
    print(df)"""
# idea : Hacer que al cambiar el mes se actualice la hoja de google sheet o cree una nueva hoja


@bot.command()
async def rules(ctx):
    await ctx.send('Aquí van las normas para ostigar a la gente a seguirlas, además de recordatorios UwU (poner Embed)')


@bot.command()
async def _help(ctx):
    await ctx.send('Por ejemplo (respentando las comillas):$work He trabajado "8" horas para "hacer mis tareas" crea una insercíon en tu hoja de cálculo'
                   + '\n' + '$rules para ver las normas para nada democráticas de este servidor')


@bot.command()
async def work(ctx, *args):
    # Coger los 3 argumentos entrecomillador
    total_time = float(args[2])
    description = args[5]
    fecha = str(datetime.today().strftime('%d/%m/%Y'))

    print(fecha)
    print(total_time)
    print(description)
    if ctx.message.author.id == sirsergio:
        print('entro')
        if isinstance(total_time, float) and description is not None:
            sheet = SheetAPI()
            print('entra')

            if total_time > 4:
                extra_time = total_time - 4
                precio_dia = (4*8) + (extra_time*9.5)
            else:
                precio_dia = total_time*8
                extra_time = 0
            new_row = [fecha, total_time, extra_time, description, precio_dia]
            data = sheet.get_all_records()
            new_row_index = data.__len__() + 1
            print(new_row_index)
            try:
                sheet.insert_row(new_row, index=new_row_index)

                await ctx.send('Se ha registrado el tiempo')
                await ctx.send('Recuerda infomar a Andrés:')
                await ctx.send(' A ' + fecha + ' ' + str(total_time) + 'horas, ' + str(description))
                print('se inserto')
            except Exception as e:
                print('Error al insertar la fila', e)
                await ctx.send('No se ha podido registrar el tiempo : ', e)
        else:
            await ctx.send('No se ha podido registrar el tiempo')
            await ctx.send('Por favor, compruebe que los datos introducidos son correctos')
            #  await ctx.send('Por ejemplo: $test "Nombre del proyecto" "Nombre del usuario" "Tiempo total" "Tiempo extra" "Descripción"')
            await ctx.send('Por ejemplo (respentando las comillas):$work He trabajado "8" horas para "lokitest foro"')

    else:
        await ctx.send('No tienes permisos para usar este comando')


@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Por favor, introduzca los datos necesarios o de forma correcta')
        await ctx.send('Por ejemplo (respentando las comillas):$work He trabajado "8" horas para "hacer mis tareas"')


# Parte del bot de musica
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
ffmpeg_options = {'options': "-vn"}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

voice_clients = {}
@bot.command()
async def play(ctx, url: str):
    """  await ctx.send('Helloow')
        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=ctx.author.voice.channel.name)
        if voiceChannel is None:
            await ctx.send('No estás en un canal de voz')
            return
        else:
            try:           
                await voiceChannel.connect()
            except Exception as e:
                print("PASS NOT ENTER ", e.args)
                pass"""
    
    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except:
        print("error")

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        song = data['url']
        player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player)

    except Exception as err:
            print(err)
    """   try:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)     


            if voice.is_playing()==False:    
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                if oldfilename is not None:
                    try:
                        if oldfilename.exist():
                            os.remove(oldfilename)
                    except:
                        pass

                oldfilename = filename
            
                voice.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename), after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send('**Now playing:** {}'.format(filename)) 
            


    except Exception as e:
        await ctx.send(e.args)
        pass"""
    
    

@play.error
async def errorPlay(ctx):
   await ctx.send('No se ha podido reproducir la canción')

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send('No estoy conectado')
@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send('Pausado')
    else:
        await ctx.send('No estoy reproduciendo nada')

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send('Reproduciendo')
    else:
        await ctx.send('No estoy pausado')
@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send('Detenido')
    else:
        await ctx.send('No estoy reproduciendo nada')


@bot.command()
async def volume(ctx, volume: int):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.source.volume = volume / 100
        await ctx.send('Volumen: {}%'.format(volume))
    else:
        await ctx.send('No estoy reproduciendo nada')
        
bot.run(TOKEN)
