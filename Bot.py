import asyncio
import discord
import myToken
import random
from discord.ext import commands
from discord.ext.commands import bot
bot = commands.Bot(command_prefix=myToken.prefix, description=myToken.description)


ourServer = None
inProgress = False
readyUsers = []
firstCaptain = None
secondCaptain = None
teamOne = []
teamTwo = []
currentPickingCaptain = ""
pickNum = 1
team1VoiceChannel = None
team2VoiceChannel = None
serverName = myToken.guildID


async def readyUp(ctx):
    # we received a message
    # modifying these globals
    global inProgress
    global readyUsers
    global firstCaptain
    global secondCaptain
    global teamOne
    global teamTwo
    global pickNum

    # extract the author and message from context.
    author = ctx.author
    message = ctx.message

    # make sure they're using the bot setup channel
    if (message.channel.id != myToken.setupChannelId):
        # if they aren't using an appropriate channel, return
        return

        # ready command
    if (inProgress == False and len(readyUsers) < 10):
        # check if they are already ready
        if (author in readyUsers):
            embed = discord.Embed(
                description=author.mention + "You're already ready, chill.", color=0x03f0fc)
            await ctx.send(embed=embed)
            return
        # actually readying up
        else:
            # add them to the ready list and send a message
            readyUsers.append(author)
            if (len(readyUsers) == 8 or len(readyUsers) == 9):
                embed = discord.Embed(description="<@&" + str(myToken.csRoleID) + ">" + " we only need " + str(
                    10 - len(readyUsers)) + " more players. `!ready` to join", color=0x03f0fc)
                await ctx.send(embed=embed)
            elif (len(readyUsers) == 10):
                # we have 10 ready users, now need captains
                embed = discord.Embed(
                    description="**WE BALLIN'. Now randomly selecting captains.**", color=0x03f0fc)
                await ctx.send(embed=embed)
                inProgress = True
                firstCaptain = readyUsers[random.randrange(len(readyUsers))]
                readyUsers.remove(firstCaptain)
                secondCaptain = readyUsers[random.randrange(len(readyUsers))]
                readyUsers.remove(secondCaptain)
                embed = discord.Embed(description="**Captains**\nTeam: " +
                                                  firstCaptain.mention + "\nTeam: " + secondCaptain.mention,
                                      color=0x03f0fc)
                await ctx.send(embed=embed)
                embed = discord.Embed(
                    description=firstCaptain.mention + " it is now your pick, pick with `" + myToken.prefix +
                                "pick @user`. Please choose from " + " \n ".join(str(x.mention) for x in readyUsers),
                    color=0x03f0fc)
                await ctx.send(embed=embed)
            elif (len(readyUsers) != 0):
                embed = discord.Embed(description=author.mention + " **is now ready, we need **" + str(
                    10 - len(readyUsers)) + " **more**", color=0x03f0fc)
                await ctx.send(embed=embed)
            return


async def notready(ctx):
    global readyUsers
    # make sure they're using the bot setup channel
    if (ctx.message.channel.id != myToken.setupChannelId):
        # if they aren't using an appropriate channel, return
        return
    author = ctx.author
    try:
        readyUsers.remove(author)
        # unready message
        embed = discord.Embed(description=author.mention + " You are no longer ready. We now need " +
                                          str(10 - len(readyUsers)) + " more", color=0x3f0fc)
        await ctx.send(embed=embed)
    except ValueError:
        embed = discord.Embed(description=author.mention +
                                          " You are not in the ready list to begin with!", color=0x3f0fc)
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    global ourServer
    global team1VoiceChannel
    global team2VoiceChannel

    team1VoiceChannel = bot.get_channel(myToken.team1ChannelId)
    team2VoiceChannel = bot.get_channel(myToken.team2ChannelId)
    print('------')
    print('Logged in as {} with id {}'.format(bot.user.name, bot.user.id))
    print('VC1 Name is {}\nVC2 Name is {}'.format(
        team1VoiceChannel, team2VoiceChannel))
    print('------')
    # loop over all the servers the bots apart


@bot.command()
async def ready(ctx):
    await readyUp(ctx)
    return


@bot.command()
async def gaben(ctx):
    await readyUp(ctx)
    return


@bot.command()
async def pick(ctx, *, arg):
    global inProgress
    global readyUsers
    global firstCaptain
    global secondCaptain
    global teamOne
    global teamTwo
    global pickNum

    # make sure they're using the bot setup channel
    if (ctx.message.channel.id != myToken.setupChannelId):
        # if they aren't using an appropriate channel, return
        return
    if (inProgress == True and pickNum < 9):
        author = ctx.author
        message = ctx.message
        # make sure a captain is picking, and its his turn
        if (author == firstCaptain and (pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8)):
            # get the user they picked
            if (len(message.mentions) != 1):
                embed = discord.Embed(
                    description="Please pick a user by @ing them. " + myToken.prefix + "pick @user", color=0x03f0fc)
                await ctx.send(embed=embed)
                return

            pickedUser = message.mentions[0]
            # make sure hes a real user
            if (pickedUser not in (name for name in readyUsers)):
                embed = discord.Embed(description=str(
                    pickedUser) + " `is not in the 10man, please pick again.`", color=0x03f0fc)
                await ctx.send(embed=embed)
                return

            # add him to team one
            teamOne.append(pickedUser)

            # move him to voice channel for team 1
            await pickedUser.move_to(team1VoiceChannel)

            # remove him from ready users
            readyUsers.remove(pickedUser)

            # increment pick number
            pickNum += 1
            print(pickNum)
            # check if we're done picking
            if (pickNum == 9):
                embed = discord.Embed(description='''The teams are now made and bot setup is finished.\n
                Team 1: ''' + ", ".join(str(x.name) for x in teamOne) + '''

                Team 2: ''' + ", ".join(str(x.name) for x in teamTwo) + '''
                **Good luck and have fun!**''', color=0x3f0fc)
                await ctx.send(embed=embed)
                await firstCaptain.move_to(team1VoiceChannel)
                await secondCaptain.move_to(team2VoiceChannel)
                inProgress = False
                readyUsers = []
                teamOne = []
                teamTwo = []
                firstCaptain = None
                secondCaptain = None
                pickNum = 1
                return
            # check if we need to pick again or its other captains turn
            if (pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7):
                embed = discord.Embed(description=secondCaptain.mention + " it is now your pick, pick with " +
                                                  myToken.prefix + "pick @user. Please choose from " + " \n ".join(
                    str(x.mention) for x in readyUsers))
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=firstCaptain.mention + " it is now your pick, pick with " +
                                                  myToken.prefix + "pick @user. Please choose from " + " \n ".join(
                    str(x.mention) for x in readyUsers))
                await ctx.send(embed=embed)
            return

        elif (author == secondCaptain and (pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7)):
            # get the user they picked
            if (len(message.mentions) != 1):
                embed = discord.Embed(
                    description="Please pick a user by @ing them. " + myToken.prefix + "pick @user", color=0x03f0fc)
                await ctx.send(embed=embed)
                return

            pickedUser = message.mentions[0]
            teamTwo.append(pickedUser)

            # move him to voice channel for team 2
            await pickedUser.move_to(team2VoiceChannel)

            # remove him from ready users
            readyUsers.remove(pickedUser)

            pickNum += 1
            if (pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8):
                embed = discord.Embed(description=firstCaptain.mention + " it is now your pick, pick with " +
                                                  myToken.prefix + "pick @user. Please choose from " + " \n ".join(
                    str(x.mention) for x in readyUsers))
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=secondCaptain.mention + " it is now your pick, pick with " +
                                                  myToken.prefix + "pick @user. Please choose from " + " \n ".join(
                    str(x.mention) for x in readyUsers))
                await ctx.send(embed=embed)
            return
        else:
            embed = discord.Embed(
                description="You're not a captain, sorry, but please let the captains select!", color=0x03f0fc)
            await ctx.send(embed=embed)
    return


@bot.command()
async def unready(ctx):
    await notready(ctx)
    return


@bot.command()
async def ungaben(ctx):
    await notready(ctx)
    return


@bot.command()
async def done(ctx):
    global inProgress
    global readyUsers
    global firstCaptain
    global secondCaptain
    global teamOne
    global teamTwo
    global pickNum
    # make sure they're using the bot setup channel
    if (ctx.message.channel.id != myToken.setupChannelId):
        # if they aren't using an appropriate channel, return
        return
    inProgress = False
    readyUsers = []
    teamOne = []
    teamTwo = []
    firstCaptain = None
    secondCaptain = None
    pickNum = 1
    embed = discord.Embed(
        description="**Current 10man finished, need** 10 **readied players**", color=0xff0000)
    await ctx.send(embed=embed)
    return


@bot.command()
async def whosready(ctx):
    global readyUsers
    # make sure they're using the bot setup channel
    if (ctx.message.channel.id != myToken.setupChannelId):
        # if they aren't using an appropriate channel, return
        return
    if (len(readyUsers) == 0):
        embed = discord.Embed(
            description="There is currently no players in queue!", color=0xff0000)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description="__**Readied Users:**__ \n" +
                                          " \n ".join(sorted(str(x.name) for x in readyUsers)), color=0xebe534)
        await ctx.send(embed=embed)
    return


bot.run(myToken.token)


