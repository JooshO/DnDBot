# bot.py
import os
import random
import re
import requests
import json

from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


# Prints when user logs in
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(name='spell', 
             help='Fetches spells. Usage: !spell {spell-name}. Replace any spaces in the spell name with a \'-\'')
async def get_spell(ctx, spell_name: str):
    retrieved = requests.get('https://www.dnd5eapi.co/api/spells/{0}/'.format(spell_name))
    spell_data = json.loads(retrieved.json())
    response = spell_data['name']
    response += '\nLevel: {0} | School: {1}\n'.format(spell_data['level'], spell_data['school']['name'])
    response += f'Casting Time: {spell_data["casting_time"]} | ' \
                f'Range {spell_data["range"]} | Duration {spell_data["duration"]}\n'
    t_str = str(spell_data["components"])
    t_str = re.sub(r'[^A-Z ,]', '', t_str)
    response += f'Components: {t_str} | Materials: {spell_data["material"]}\n'
    response += '------------------------------------------------------------------------------------------------------'
    response += str(spell_data['desc'])[2:-2] + '\n'
    response += f'At higher levels: {str(spell_data["higher_level"])[2:-2]}'

    print(retrieved.json())
    await ctx.send(response)
    

# Dice rolling command
@bot.command(name='roll', help='Rolls dice in the format {num}d{side count}')
async def roll_dice(ctx, command: str):
    # RegEx out anything not 0-9 or d
    command = re.sub(r'[^d0-9]', '', command)

    # Splits out every part
    dice_list = command.split('+')

    # Create a list and index for storing all rolled values
    out_list = [0] * len(dice_list)
    index = 0

    # For every roll in the list
    for dice_command in dice_list:
        # If there isn't a d, we are just adding so store the number
        if dice_command.find('d') == -1:
            out_list[index] = int(dice_command.strip())

        else:
            # Split into number of dice and number of sides
            temp = dice_command.split('d')

            # Create a list of roles for this die
            dice = [
                random.choice(range(1, int(temp[1]) + 1))
                for _ in range(int(temp[0]))
            ]

            # Sum that list
            out_list[index] = sum(dice)

        # Increment the index
        index += 1

    # Sum everything
    response = "Rolling {0}: {1}".format(command, str(sum(out_list)))

    await ctx.send(response)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


bot.run(TOKEN)
