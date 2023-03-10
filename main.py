import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

intent = discord.Intents.all()
bot = commands.Bot(command_prefix='$', help_command=None, intents=intent)
guild = None
chan = None
chat_lounge = None
f = open("vars.txt", "r")
arr = f.readlines()  # 0 is toggle, 1 is channel
f.close()

@bot.event
async def on_ready():
    global guild, chan, chat_lounge
    print('We have logged in as {0.user}'.format(bot))
    guild = bot.guilds[0]
    chan = guild.get_channel(int(arr[1]))
    chat_lounge = guild.get_channel(914110047859118080)

@bot.command(name="desc")
async def desc(ctx):
    if ctx.channel != chat_lounge:
      await ctx.channel.send("Use commands in {} please.".format(chat_lounge.mention))
      return
    await ctx.channel.send("```"\
                            "This bot was inspired by a rule made up for fun among the moderators."\
                           "The rule was made such that if your webcam is not switched on, the others would not"\
                           " be able to hear you. This bot enforces it.\nTo use it, just enter the \"No Camera "\
                           "No Talk\" lobby and the rule will take place. To unmute yourself, switch on your"\
                           " camera. If your camera is switched off, you will be muted again. Do not worry, "\
                           "when you leave the lobby, you will be unmuted until you enter again."\
                           "```")

@bot.command(name="set")
async def set(ctx, channel_id):
    if ctx.channel != chat_lounge:
      await ctx.channel.send("Use commands in {} please.".format(chat_lounge.mention))
      return

    if not ctx.message.author.guild_permissions.administrator:
      await ctx.channel.send("Only administrators can use this command.")
      return

    try:
        global chan, arr
        channel_id = int(channel_id.translate({ord(i): None for i in '<#>'}))
        channel = guild.get_channel(channel_id)
        bit = channel.bitrate
        arr[1] = str(channel_id)
        f = open("vars.txt", "w")
        for x in arr:
          f.write(x)
        f.close()
        chan = channel
        await ctx.channel.send("No Camera No Talk channel set to {}".format(chan.mention))
    except Exception as e:
        print(e)
        await ctx.channel.send("Invalid channel.")
        return

@bot.command(name="toggle")
async def toggle(ctx):
  if ctx.channel != chat_lounge:
    await ctx.channel.send("Use commands in {} please.".format(chat_lounge.mention))
    return

  if not ctx.message.author.guild_permissions.administrator:
    await ctx.channel.send("Only administrators can use this command.")
    return

  global arr
  flag = arr[0]
  if flag == "True\n":
    arr[0] = "False\n"
    await ctx.channel.send("Rule is **disabled**.")
  else:
    arr[0] = "True\n"
    await ctx.channel.send("Rule is **enabled**.")
  f = open("vars.txt", "w")
  for x in arr:
    f.write(x)
  f.close()

@bot.command(name="help")
async def help(ctx):
    await ctx.channel.send(">>> __**Commands available (use in ncnt channel)**__\n"\
                           "**$desc**: Brings up the description of the bot.\n"\
                           "**$status**: Brings up the current status of the rule.\n"\
                           "**$set** ***channel***: Sets the channel for the rule to take place. Use #! to mention a voice channel. (Admins only)\n"\
                           "**$toggle**: Enables or disables the rule. (Admins only)")

@bot.command(name="status")
async def status(ctx):
  if ctx.channel != chat_lounge:
    await ctx.channel.send("Use commands in {} please.".format(chat_lounge.mention))
    return
  status = arr[0]
  if status == "True\n":
    flag = "**enabled**"
  else:
    flag = "**disabled**"
  await ctx.channel.send("The rule is currently {0} and the channel set is {1}".format(flag, chan.mention))

async def set_mute(member):
    await member.edit(mute=True)

async def set_unmute(member):
    await member.edit(mute=False)


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and arr[0] == "True\n":
        if member.bot or (member.voice.mute and not member.voice.self_video and after.channel.id == chan.id)\
                or (not member.voice.mute and member.voice.self_video and after.channel.id == chan.id):
            return
        if after.channel.id == chan.id:  # if joined lobby 1
            if not member.voice.self_video:  # if video not on
                if before.channel != after.channel:
                  await chat_lounge.send("{}, no camera no talk".format(member.mention))
                await set_mute(member)  # server mute
            elif member.voice.self_video:  # if video on
                await set_unmute(member)  # unmute
            else:  # if any other change in state
                return
        elif before.channel.id == chan.id and before.channel.id != after.channel.id:  # not in lobby 1
            await set_unmute(member)


keep_alive()
bot.run(os.environ['TOKEN'])
