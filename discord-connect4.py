import discord
from discord.ext import commands, tasks
import asyncio
import random


TOKEN = 'Your token here'

client = commands.Bot(command_prefix='§')
client.remove_command('help')



#----------------------- Var -----------------------------#

invite_url = 'https://discord.com/api/oauth2/authorize?client_id=747832023271604236&permissions=76864&scope=bot'

numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']

game_list = {}



#---------------------- Function ------------------------#

def format_grid(grid):
	global numbers

	res = []

	for i in numbers:
		res.append(i)

	res.append('\n')

	for Yaxe in range(len(grid)):

		for Xaxe in range(len(grid[Yaxe])):

			if grid[Yaxe][Xaxe]==0:
				res.append('⬛')
			if grid[Yaxe][Xaxe]==1:
				res.append('🔴')
			if grid[Yaxe][Xaxe]==2:
				res.append('🟡')


		res.append('\n')



	return ''.join(res)


def process_game(game_list, n):

	grid = game_list['grid']
	turn = game_list['turn']

	if grid[5][n]==0:
		grid[5][n]=turn

	elif grid[4][n]==0:
		grid[4][n]=turn

	elif grid[3][n]==0:
		grid[3][n]=turn

	elif grid[2][n]==0:
		grid[2][n]=turn

	elif grid[1][n]==0:
		grid[1][n]=turn

	else:
		grid[0][n]=turn

	return grid



def check_win(game_list):

	grid = game_list['grid']
	turn = game_list['turn']

	for Yaxe in range(3):
		for Xaxe in range(4):

			#From up left to down right check
			if grid[Yaxe][Xaxe]==turn and grid[Yaxe+1][Xaxe+1]==turn and grid[Yaxe+2][Xaxe+2]==turn and grid[Yaxe+3][Xaxe+3]==turn:
				game_list['winner'] = turn

			#From down left to up right
			if grid[Yaxe+3][Xaxe]==turn and grid[Yaxe+2][Xaxe+1]==turn and grid[Yaxe+1][Xaxe+2]==turn and grid[Yaxe][Xaxe+3]==turn:
				game_list['winner'] = turn


	for Yaxe in range(3):
		for Xaxe in range(len(grid)):
			if grid[Yaxe][Xaxe]==turn and grid[Yaxe+1][Xaxe]==turn and grid[Yaxe+2][Xaxe]==turn and grid[Yaxe+3][Xaxe]==turn:
				game_list['winner'] = turn


	for Yaxe in range(len(grid)):
		for Xaxe in range(4):
			if grid[Yaxe][Xaxe]==turn and grid[Yaxe][Xaxe+1]==turn and grid[Yaxe][Xaxe+2]==turn and grid[Yaxe][Xaxe+3]==turn:
				game_list['winner'] = turn


	return game_list




#--------------- Commands and Events ---------------------#


# //// Events \\\\

@client.event
async def on_ready():
	background_task.start()
	await client.change_presence(activity=discord.Game(name='§help'))
	print('Ready to connect 4')


# Background tasks
@tasks.loop(seconds=10.0)
async def background_task():
	global game_list

	to_pop = []

	for current_game in game_list:
		game_list[current_game]['timeout'] -= 10

		if game_list[current_game]['timeout'] <= 0:

			embed = discord.Embed(title='Connect 4', description=str('Game ended by time out\n\n' + format_grid(game_list[current_game]['grid'])), color=game_list[current_game]['color'])
			embed.set_footer(text = 'Game ended')
			channel = client.get_channel(game_list[current_game]['channel_id'])
			msg = await channel.fetch_message(current_game)
			await msg.edit(embed=embed)

			to_pop.append(current_game)

	for i in to_pop:
		game_list.pop(i)




@client.event
async def on_raw_reaction_add(payload):
	global game_list
	global numbers


	#current game shortcut
	current_game = payload.message_id


	#Do nothing if not meant to
	if (payload.message_id in game_list)==False:
		return
	if payload.user_id == client.user.id:
		return
	if payload.user_id != game_list[current_game][game_list[current_game]['turn']]:
		return



	if str(payload.emoji)=='❌' and payload.user_id == game_list[current_game][game_list[current_game]['turn']]:
		embed = discord.Embed(title='Connect 4', description=str('Game ended by <@'+str(game_list[current_game][game_list[current_game]['turn']])+'>\n\n' + format_grid(game_list[current_game]['grid'])), color=game_list[current_game]['color'])
		embed.set_footer(text = 'Game ended')
		channel = client.get_channel(payload.channel_id)
		msg = await channel.fetch_message(current_game)
		await msg.edit(embed=embed)
		game_list.pop(payload.message_id)

	else:
		#Put circle
		for i in range(len(numbers)):
			if str(payload.emoji)==numbers[i] and payload.user_id == game_list[current_game][game_list[current_game]['turn']]:
				if game_list[current_game]['grid'][0][i] != 0 and str(payload.emoji)==numbers[i]:
					return
				game_list[current_game]['grid'] = process_game(game_list[current_game], i)
				game_list[current_game] = check_win(game_list[current_game])
				if game_list[current_game]['turn']==1:
					game_list[current_game]['turn']=2
				else:
					game_list[current_game]['turn']=1


		#Make message
		embed = discord.Embed(title='Connect 4', description=str('Its <@'+str(game_list[current_game][game_list[current_game]['turn']])+'> turn :\n\n' + format_grid(game_list[current_game]['grid'])), color=game_list[current_game]['color'])
		channel = client.get_channel(payload.channel_id)
		msg = await channel.fetch_message(current_game)
		await msg.edit(embed=embed)

		game_list[current_game]['timeout'] = 60

		member = await client.fetch_user(payload.user_id)
		await msg.remove_reaction(payload.emoji, member)


		#Check win
		if game_list[current_game]['winner']!=0:

			if game_list[current_game]['turn']==1:
				game_list[current_game]['turn']=2
			else:
					game_list[current_game]['turn']=1

			embed = discord.Embed(title='Connect 4', description=str('🎉 <@'+str(game_list[current_game][game_list[current_game]['turn']])+'> won 🎉\n\n' + format_grid(game_list[current_game]['grid'])), color=game_list[current_game]['color'])
			embed.set_footer(text = 'Game ended')
			msg = await channel.fetch_message(current_game)
			await msg.edit(embed=embed)
			game_list.pop(payload.message_id)
			return





# //// Commands \\\\

@client.command()
async def help(ctx):

	_play = '**§play @player1 @player2**  -  start a game of connect 4\n'
	_about = '**§about**  -  about the bot\n'
	_invite = '**§invite**  -  get a link to invite the bot to your server\n'
	_help = '**§help**  -  show this message'

	embed = discord.Embed(title='Connect 4 | help', description=str(_play + _invite + _about + _help), color=0x03fce3)
	await ctx.send(embed=embed)




@client.command()
async def play(ctx, user_1 : discord.Member, user_2 : discord.Member):
	global game_list
	global numbers

	default_grid = [[0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0]]

	color = random.randint(0, 0xFFFFFF)

	embed = discord.Embed(title='Connect 4', description=str('Its <@'+str(user_1.id)+'> turn :\n\n' + format_grid(default_grid)), color=color)
	msg = await ctx.send(embed=embed)

	for i in numbers:
		await msg.add_reaction(i)
	await msg.add_reaction('❌')

	game_list[msg.id] = {'grid':default_grid, 1:user_1.id, 2:user_2.id, 'color':color, 'turn':1, 'winner':0, 'timeout':60, 'channel_id':ctx.channel.id}



@client.command()
async def invite(ctx):
	global invite_url
	embed = discord.Embed(title='Connect 4 | invite', description=str('Here is the link to invite the Connect 4 bot to your discord server :\n' + invite_url), color=0x03fce3)
	await ctx.send(embed=embed)


@client.command()
async def about(ctx):
	embed = discord.Embed(title='Connect 4 | about', description='An easy way to play Connect 4 without even leaving discord !\n\nJust do **§play @player1 @player2** to start a game and use the reactions to play.\n⚠️ The game ends if no one plays after 60 seconds ⚠️', color=0x03fce3)
	member = str(await client.fetch_user(395950370846801922))
	embed.set_footer(text = str('Made by ' + str(member)))
	embed.set_thumbnail(url=client.user.avatar_url)
	#embed.set_footer(text = str('Currently in ' + str(len(client.guilds)) + ' servers'))
	await ctx.send(embed=embed)


@client.command()
async def debug_info(ctx):
	global game_list

	if ctx.author.id == 395950370846801922:

		member = str(await client.fetch_user(395950370846801922))
		server_count =  str(len(client.guilds))
		game_count = str(len(game_list))

		embed = discord.Embed(title = 'Connect 4 info', description=str('Server count :' + server_count + '\nGame running :' + game_count), color=0x03fce3)
		embed.set_thumbnail(url=client.user.avatar_url)
		await ctx.send(embed=embed)


client.run(TOKEN)
