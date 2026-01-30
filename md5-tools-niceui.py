import hashlib
import requests
from time import sleep
from nicegui import ui, app
import asyncio
import aiohttp
import inspect

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

    ui.add_head_html("<link href='https://cdn.jsdelivr.net/npm/@mdi/font@6.x/css/materialdesignicons.min.css' rel='stylesheet'>")
    ui.add_css('''
    .q-uploader__files .q-img__image, .q-uploader__file .q-img__image { max-height: 100px; object-fit: contain; }
    ''')
    with ui.card().classes('absolute top-2 left-4 p-1 shadow-lg bg-gradient-to-r from-indigo-600 to-indigo-500 text-white rounded-lg flex items-center gap-3 md:w-auto w-85 sm:justify-center'):
        with ui.column():
            ui.label('MD5 Tools').classes('text-base font-semibold')
            ui.label('MD5 utilities — hash, compare & files').classes('text-xs opacity-80')
        with ui.row().classes('items-center gap-2'):
            ui.link('', 'https://github.com/BedMan95/md5-tools', new_tab=True).props('icon=mdi-github')
            
# Four cards grid
    with ui.row().classes('w-full max-w-4xl mx-auto gap-6 grid grid-cols-1 md:grid-cols-2 pt-20 md:pt-0'):
        # Card: Hash Text
        with ui.card().classes('p-3 text-sm min-h-[350px] flex flex-col justify-between'):
            ui.label('Hash Text').classes('text-base font-semibold')

            hash_text_input = ui.textarea(
                placeholder='Type or paste your text here...'
            ).classes('font-mono text-sm w-full')\
             .props('autogrow outlined clearable')

            ui.label('MD5 Hash result:').classes('text-sm font-medium mb-2')

            with ui.row().classes('items-start gap-4'):
                hash_text_result = ui.label('')\
                    .classes('font-mono text-sm break-all bg-slate-50 dark:bg-slate-900 rounded w-full')\
                    .props('id=hash_text_result')

            async def do_hash_text():
                txt = hash_text_input.value.strip()
                if not txt:
                    hash_text_result.text = 'Please enter some text!'
                    hash_text_result.classes(replace='text-red-600')
                    return
                hash_text_result.text = md5_hash(txt)
                hash_text_result.classes(replace='text-green-600')
                ui.notify('MD5 generated', color='positive')

            with ui.row().classes('mt-4 justify-end gap-3'):
                ui.button('Generate', on_click=do_hash_text, icon='mdi-shield-key')\
                    .classes('bg-indigo-600 text-white px-3 py-2 text-sm h-9 rounded')
                ui.button('Copy', on_click=lambda: [
                    ui.run_javascript("navigator.clipboard.writeText(document.getElementById('hash_text_result').innerText)"),
                    ui.notify('Hash copied to clipboard ✅')
                ]).classes('bg-indigo-500 text-white px-3 py-2 text-sm h-9 rounded')
                ui.button('Clear', on_click=lambda: [
                    hash_text_input.set_value(''),
                    hash_text_result.set_text(''),
                    hash_text_result.classes(replace='text-gray-500 bg-slate-50 dark:bg-slate-900')
                ]).classes('bg-gray-400 text-white px-3 py-2 text-sm h-9 rounded')

        # Card: Crack MD5 (existing)
        with ui.card().classes('p-3 text-sm min-h-[350px] flex flex-col justify-between'):
            ui.label('Crack MD5').classes('text-base font-semibold mb-2')

            crack_hash_input = ui.input(
                placeholder='e.g. d41d8cd98f00b204e9800998ecf8427e'
            ).classes('font-mono text-sm w-full')\
             .props('outlined clearable maxlength=32')

            ui.label('Cracking result:').classes('text-sm font-medium mb-2')

            crack_result = ui.markdown('')\
                .classes('font-mono text-sm whitespace-pre-wrap bg-slate-50 dark:bg-slate-900 rounded').props('id=crack_result')

            crack_spinner = ui.spinner()
            crack_spinner.visible = False

            async def do_crack():
                h = crack_hash_input.value.strip().lower()
                if len(h) != 32 or not all(c in '0123456789abcdef' for c in h):
                    crack_result.content = '**Invalid MD5 format!**\nMust be exactly 32 hexadecimal characters.'
                    crack_result.classes(replace='text-red-600')
                    ui.notify('Invalid MD5 format', color='negative')
                    return

                crack_spinner.visible = True
                crack_result.content = 'Searching... (this may take a few seconds)'
                crack_result.classes(replace='text-blue-600')

                plain = await cheap_md5_lookup(h, crack_result)

                crack_spinner.visible = False

                if plain:
                    crack_result.content = f'**FOUND!**\n\n**Plaintext:** {plain}\n\n**MD5:** {h}'
                    crack_result.classes(replace='text-green-700 font-bold')
                    ui.notify('Plaintext found ✅', color='positive')
                else:
                    crack_result.content = (
                        '**Not found** in available public lookup services.\n\n'
                        'Note (2026):\n'
                        '• Most free online MD5 databases are dead or blocked\n'
                        '• Try Hashcat + good wordlists / rules / masks\n'
                        '• Use rainbow tables for common passwords'
                    )
                    crack_result.classes(replace='text-orange-700')
                    ui.notify('Nothing found — try local cracking', color='warning')

            with ui.row().classes('mt-4 justify-end gap-3'):
                ui.button('Search', on_click=do_crack, icon='mdi-magnify')\
                    .classes('bg-green-600 text-white px-3 py-2 text-sm h-9 rounded')
                ui.button('Copy', on_click=lambda: [
                    ui.run_javascript("navigator.clipboard.writeText(document.getElementById('crack_result').innerText)"),
                    ui.notify('Result copied to clipboard ✅')
                ]).classes('bg-indigo-500 text-white px-3 py-2 text-sm h-9 rounded')

        # Card: Hash Compare
        with ui.card().classes('p-3 text-sm min-h-[350px] flex flex-col justify-between'):
            ui.label('Hash Compare').classes('text-base font-semibold mb-2')

            left_input = ui.textarea(placeholder='Left hash...').classes('w-full font-mono min-h-[70px] text-sm')\
                .props('autogrow outlined clearable')
            right_input = ui.textarea(placeholder='Right hash...').classes('w-full font-mono min-h-[70px] mt-3 text-sm')\
                .props('autogrow outlined clearable')

            compare_result = ui.label('').classes('text-green-600 font-bold')

            def do_compare():
                # Compare the raw hash strings provided by the user (no MD5 computation)
                l = left_input.value.strip().lower()
                r = right_input.value.strip().lower()
                lh = l if l else '—'
                rh = r if r else '—'
                left_input.text = lh
                right_input.text = rh
                if lh != '—' and rh != '—' and lh == rh:
                    compare_result.text = 'MATCH ✅'
                    compare_result.classes(replace='text-green-600 font-bold')
                else:
                    compare_result.text = 'No match'
                    compare_result.classes(replace='text-orange-600')

            def clear_compare():
                left_input.set_value('')
                right_input.set_value('')
                compare_result.set_text('')

            with ui.row().classes('mt-3 justify-end gap-3'):
                ui.button('Compare', on_click=do_compare, icon='mdi-equal')\
                    .classes('bg-indigo-600 text-white px-3 py-2 text-sm h-9 rounded')
                ui.button('Clear', on_click=clear_compare).classes('bg-gray-400 text-white px-3 py-2 text-sm h-9 rounded')

        # Card: File to MD5
        with ui.card().classes('p-3 text-sm min-h-[350px] flex flex-col justify-between'):
            ui.label('File to MD5').classes('text-base font-semibold mb-2')

            file_result = ui.label('No file uploaded').classes('mt-3 font-mono text-sm p-2 bg-slate-50 dark:bg-slate-900 rounded').props('id=file_result')

            async def handle_upload(event):
                """Handle both single and multi upload events from NiceGUI.
                Accepts UploadEventArguments (event.file) or MultiUploadEventArguments (event.files).
                This version awaits any awaitable read/content values and normalizes to bytes.
                """
                try:
                    uploads = []
                    # event may have .files (list) or .file (single)
                    if hasattr(event, 'files') and event.files:
                        uploads = event.files
                    elif hasattr(event, 'file') and event.file:
                        uploads = [event.file]

                    if not uploads:
                        file_result.text = 'No file uploaded'
                        file_result.classes(replace='text-red-600')
                        return

                    parts = []
                    for f in uploads:
                        name = getattr(f, 'name', None) or getattr(f, 'filename', None) or 'file'
                        data = None

                        # prefer .content if present
                        if hasattr(f, 'content'):
                            data = f.content
                            if inspect.isawaitable(data):
                                data = await data

                        # try .read() if available (may be awaitable)
                        elif hasattr(f, 'read'):
                            maybe = f.read()
                            if inspect.isawaitable(maybe):
                                data = await maybe
                            else:
                                data = maybe

                        # fall back to .data
                        elif hasattr(f, 'data'):
                            data = f.data
                            if inspect.isawaitable(data):
                                data = await data

                        # dict-style payloads
                        elif isinstance(f, dict):
                            data = f.get('content') or f.get('data')
                            if inspect.isawaitable(data):
                                data = await data
                            if not name:
                                name = f.get('name', 'file')

                        if data is None:
                            file_result.text = f'Error reading file: no data for {name}'
                            file_result.classes(replace='text-red-600')
                            return

                        # if data is a str, encode to bytes
                        if isinstance(data, str):
                            data = data.encode('utf-8')

                        # if data is file-like, try to read it
                        if hasattr(data, 'read'):
                            maybe = data.read()
                            if inspect.isawaitable(maybe):
                                data = await maybe
                            else:
                                data = maybe

                        # ensure bytes-like
                        if not isinstance(data, (bytes, bytearray, memoryview)):
                            try:
                                data = bytes(data)
                            except Exception:
                                file_result.text = f'Error reading file: unsupported data type {type(data)} for {name}'
                                file_result.classes(replace='text-red-600')
                                return

                        digest = hashlib.md5(data).hexdigest()
                        parts.append(f'{name}: {digest}')

                    file_result.text = '\n'.join(parts)
                    file_result.classes(replace='text-green-600')
                    ui.notify('File hash computed', color='positive')
                except Exception as e:
                    file_result.text = f'Error reading file: {e}'
                    file_result.classes(replace='text-red-600')

            file_upload = ui.upload(label='Upload file', multiple=False, on_upload=handle_upload).classes('w-full h-[120px] overflow-auto')

            with ui.row().classes('mt-4 justify-end gap-3'):
                ui.button('Copy', on_click=lambda: [
                    ui.run_javascript("navigator.clipboard.writeText(document.getElementById('file_result').innerText)"),
                    ui.notify('Result copied to clipboard ✅')
                ]).classes('bg-indigo-500 text-white px-3 py-2 text-sm h-9 rounded')
                ui.button('Clear', on_click=lambda: [
                    file_result.set_text('No file uploaded'),
                ]).classes('bg-gray-400 text-white px-3 py-2 text-sm h-9 rounded')
                

ui.run(
    title='MD5 Tools',
    reload=True,
    port=7777
)