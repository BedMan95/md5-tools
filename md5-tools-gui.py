import hashlib
import requests
from time import sleep
from nicegui import ui, app
import asyncio
import aiohttp

def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


async def cheap_md5_lookup(hash_value: str, status: ui.markdown) -> str | None:
    hash_value = hash_value.strip().lower()
    if len(hash_value) != 32 or not all(c in '0123456789abcdef' for c in hash_value):
        return None

    status.content = 'Searching... (may take a few seconds)'
    status.classes(replace='text-blue-600')

    sites = [
        f"http://www.nitrxgen.net/md5db/{hash_value}.txt",
        f"https://md5.gromweb.com/?md5={hash_value}",
        # Add more if you find working ones in 2026
    ]

    for url in sites:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=8,
                                     headers={"User-Agent": "NiceGUI-MD5-Tool/2026"}) as resp:
                    text = await resp.text()
                    if not text or any(x in text.lower() for x in ["not found", "no match", "could not"]):
                        continue

                    if "nitrxgen" in url and len(text.strip()) < 120:
                        return text.strip()

                    if "gromweb" in url and "The MD5 hash" in text:
                        try:
                            start = text.find('The MD5 hash') + 140
                            end = text.find('</p>', start)
                            segment = text[start:end].strip()
                            if '/?string=' in segment:
                                plain = segment.split('/?string=')[-1].split('"')[0]
                                return plain.replace("%20", " ").replace("+", " ")
                            else:
                                return segment.strip('"').strip("'")
                        except:
                            pass

                    import re
                    candidates = re.findall(r'[\w !@#$%^&*()_+\-=\[\]{}|;:,.<>?\'"\\\/]{2,60}', text)
                    for cand in candidates:
                        plain = cand.strip()
                        if 1 <= len(plain) <= 60 and md5_hash(plain) == hash_value:
                            return plain
        except Exception:
            continue
        await asyncio.sleep(1.3)

    return None

@ui.page('/')
async def main_page():

    ui.label('MD5 Tools')\
        .classes('text-3xl font-bold text-center mt-6 mb-2 text-indigo-700')

    with ui.card().classes('w-full max-w-3xl mx-auto shadow-xl mt-4'):
        with ui.tabs().classes('w-full') as tabs:
            hash_tab = ui.tab('Hash Text')
            crack_tab = ui.tab('Crack MD5')

        with ui.tab_panels(tabs, value=hash_tab).classes('w-full'):
            with ui.tab_panel(hash_tab):
                ui.label('Enter text to hash').classes('text-lg font-medium mb-3')
                
                text_input = ui.textarea(
                    placeholder='Type or paste your text here...',
                ).classes('w-full font-mono text-base min-h-[160px] resize-y')\
                 .props('autogrow outlined clearable')
                
                ui.separator().classes('my-6')
                
                ui.label('MD5 Hash result:').classes('text-base font-medium mb-2')
                
                result_label = ui.label('—').classes(
                    'font-mono text-xl break-all min-h-[3rem] p-3 bg-gray-50 dark:bg-gray-800 rounded'
                )

                async def do_hash():
                    txt = text_input.value.strip()
                    if not txt:
                        result_label.text = 'Please enter some text!'
                        result_label.classes(replace='text-red-600')
                        return
                    result = md5_hash(txt)
                    result_label.text = result
                    result_label.classes(replace='text-green-600 font-mono text-xl break-all')
                
                with ui.row().classes('mt-6 justify-center gap-4'):
                    ui.button('Generate MD5', on_click=do_hash)\
                        .classes('bg-indigo-600 text-white px-10 py-3 text-base font-medium')
                    
                    ui.button('Clear', on_click=lambda: [
                        text_input.set_value(''),
                        result_label.set_text('—'),
                        result_label.classes(replace='text-gray-500 bg-gray-50 dark:bg-gray-800')
                    ]).classes('bg-gray-600 text-white px-10 py-3 text-base font-medium')

            with ui.tab_panel(crack_tab):
                ui.label('Enter MD5 hash (32 hex chars)').classes('text-lg font-medium mb-3')
                
                hash_input = ui.input(
                    placeholder='e.g. d41d8cd98f00b204e9800998ecf8427e'
                ).classes('font-mono text-xl w-full')\
                 .props('outlined clearable maxlength=32')
                
                ui.separator().classes('my-6')
                
                ui.label('Cracking result:').classes('text-base font-medium mb-2')
                
                result_container = ui.markdown('Ready to crack...')\
                    .classes(
                        'min-h-[160px] font-mono text-base whitespace-pre-wrap p-3 '
                        'bg-gray-50 dark:bg-gray-800 rounded prose prose-sm max-w-none'
                    )

                async def start_crack():
                    h = hash_input.value.strip().lower()
                    if len(h) != 32 or not all(c in '0123456789abcdef' for c in h):
                        result_container.content = '**Invalid MD5 format!**\nMust be exactly 32 hexadecimal characters.'
                        result_container.classes(replace='text-red-600')
                        return
                        
                    plain = await cheap_md5_lookup(h, result_container)
                    
                    if plain:
                        result_container.content = f'**FOUND!**\n\n**Plaintext:** {plain}\n\n**MD5:** {h}'
                        result_container.classes(replace='text-green-700 font-bold')
                    else:
                        result_container.content = (
                            '**Not found** in available public lookup services.\n\n'
                            'Note (2026):\n'
                            '• Most free online MD5 databases are dead or blocked\n'
                            '• Try Hashcat + good wordlists / rules / masks\n'
                            '• Use rainbow tables for common passwords'
                        )
                        result_container.classes(replace='text-orange-700')
                
                with ui.row().classes('mt-6 justify-center gap-4'):
                    ui.button('Search Plaintext', on_click=start_crack)\
                        .classes('bg-green-600 text-white px-10 py-3 text-base font-medium')
                    
                    ui.button('Clear', on_click=lambda: [
                        hash_input.set_value(''),
                        result_container.set_content('Ready to crack...'),
                        result_container.classes(replace='text-gray-500 bg-gray-50 dark:bg-gray-800')
                    ]).classes('bg-gray-600 text-white px-10 py-3 text-base font-medium')
                

    ui.separator().classes('my-8')

    ui.label('Many online services are unreliable in 2026')\
        .classes('text-center text-gray-500 text-sm mb-4')


ui.run(
    title='MD5 Tools',
    reload=True,
    port=7777
)